#!/usr/bin/env python3
"""B3-X0 S2 harness launcher: boot candidate, drive UI to TestLevel, harvest telemetry.

B3-X0 S2 iteration (tooling-only fixes; candidate binary untouched):
  * VK_F10 corrected from 0x7A (F11) to 0x79 (real F10); goto_test_level is
    bound to physical scancode F10 in project.godot.
  * scenario_id/seed fall back to id/default_seed for driver requests that
    omit the canonical keys.
  * Disk-level observability: staged seed save fingerprint before/after, godot
    log marker timeline, heartbeat.jsonl per poll, phase list, early-exit
    detection, telemetry-found screenshot.

Stages an isolated APPDATA (save seed + driver game_request), launches the
candidate, sends keyboard input to its window (Menu Enter -> CharacterSelect
Enter -> Hideout -> F10 twice for goto_test_level, the action's real keybind
per project.godot), polls for the k5 harness telemetry file under
user://combat_harness/, copies it to the driver-expected path and captures
game logs as runtime evidence.

Usage:
    python scripts/validate/launch_harness_game.py --request <driver request json>
        --candidate <exe> --expected-telemetry <out json> --apdata <dir>
        [--save-dat <seed save>] [--boot-seconds 8] [--timeout-seconds 180]
        [--poll-seconds 1]
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_ENTER = 0x0D
VK_F10 = 0x79  # 0x7A was F11 (MapVirtualKey(0x7A)->scan 0x57); real F10 is 0x79
VK_MENU = 0x12
SC_ENTER = 0x1C
SC_F10 = 0x44
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_window(pid: int, title: str):
    found = []

    def cb(hwnd, _lparam):
        wpid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value != pid:
            return True
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)
        if buf.value.lower() == title.lower():
            found.append(hwnd)
            return False
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return found[0] if found else None


def focus_window(hwnd) -> None:
    """Alt-trick foreground activation: holding Alt lets any process take foreground."""
    user32.keybd_event(VK_MENU, 0, 0, None)
    tid = user32.GetWindowThreadProcessId(hwnd, None)
    user32.AttachThreadInput(kernel32.GetCurrentThreadId(), tid, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.SetActiveWindow(hwnd)
    user32.SetFocus(hwnd)
    user32.AttachThreadInput(kernel32.GetCurrentThreadId(), tid, False)
    user32.keybd_event(VK_MENU, 0, 2, None)


def post_key(hwnd, vk: int, scan: int, down: bool) -> None:
    lparam = scan | (0 if down else (1 << 30)) | (0 if down else (1 << 31))
    user32.PostMessageW(hwnd, WM_KEYDOWN if down else WM_KEYUP, vk, lparam)


def tap(hwnd, vk: int, _scan: int, hold_ms: int = 120) -> None:
    """keybd_event: sets hardware keyboard state so Godot's key-state queries
    match the posted window messages (PostMessage alone leaves state stale)."""
    user32.keybd_event(vk, 0, 0, None)
    time.sleep(hold_ms / 1000.0)
    user32.keybd_event(vk, 0, 2, None)
    time.sleep(120 / 1000.0)


def foreground_title() -> str:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "<none>"
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value or "<untitled>"


def capture_screen(path: Path) -> None:
    """Full virtual-screen capture via a PowerShell System.Drawing one-liner."""
    subprocess.run([
        "powershell", "-NoProfile", "-NonInteractive", "-Command",
        "Add-Type -AssemblyName System.Drawing;"
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen;"
        "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height;"
        "$g=[System.Drawing.Graphics]::FromImage($bmp);"
        "$g.CopyFromScreen($b.X,$b.Y,0,0,$b.Size);"
        "$bmp.Save('" + str(path) + "');$g.Dispose();$bmp.Dispose()",
    ], capture_output=True, timeout=30)


def capture_window(hwnd, path: Path) -> None:
    """Crop of the target window rect, captured from the virtual screen."""
    rect = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    if w <= 0 or h <= 0:
        return
    subprocess.run([
        "powershell", "-NoProfile", "-NonInteractive", "-Command",
        "Add-Type -AssemblyName System.Drawing;"
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$bmp=New-Object System.Drawing.Bitmap " + str(w) + "," + str(h) + ";"
        "$g=[System.Drawing.Graphics]::FromImage($bmp);"
        "$g.CopyFromScreen(" + str(rect.left) + "," + str(rect.top) + ",0,0,"
        + str(w) + "," + str(h) + ");"
        "$bmp.Save('" + str(path) + "');$g.Dispose();$bmp.Dispose()",
    ], capture_output=True, timeout=30)


def snapshot_file(path: Path, label: str) -> dict:
    """Disk-level save-file fingerprint for observability (rewrite detection)."""
    try:
        data = path.read_bytes()
        return {"label": label, "exists": True, "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "mtime": int(os.path.getmtime(path)), "at": utc_now()}
    except OSError:
        return {"label": label, "exists": False, "at": utc_now()}


def make_marker_tracker(log_file: Path):
    """Returns a callable that reads the godot log, records first-seen markers
    and returns the set of currently-seen markers.  Works around the observed
    buffering problem (B2-I1's 348-byte log) by re-reading the file each poll."""
    seen = {}

    def observe():
        try:
            text = log_file.read_text(errors="replace")
        except OSError:
            text = ""
        for name in MARKER_PATTERNS:
            if name not in seen and name in text:
                seen[name] = utc_now()
        return dict(seen), text

    return observe


MARKER_PATTERNS = [
    "GameState getting ready",
    "No save file found",
    "LOADED AND MERGED",
    "GOING TO HIDEOUT",
    "Switching levels...",
    "Destination found: test_level",
    "Resetting World",
    "Already switching...",
    "Failed with no destination scene",
    "COMBAT_HARNESS",
    "ALERT",
    "SCRIPT ERROR",
    "FATAL",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--expected-telemetry", required=True)
    ap.add_argument("--apdata", required=True)
    ap.add_argument("--save-dat", default=None)
    ap.add_argument("--boot-seconds", type=int, default=8)
    ap.add_argument("--timeout-seconds", type=int, default=180)
    ap.add_argument("--poll-seconds", type=float, default=1.0)
    args = ap.parse_args()

    exe = Path(args.candidate).resolve()
    work_dir = exe.parent
    if not exe.is_file():
        raise SystemExit(f"ERROR: candidate exe missing: {exe}")
    if not (work_dir / "steam_api64.dll").is_file():
        raise SystemExit(f"ERROR: adjacent steam_api64.dll missing: {work_dir}")

    apdata_root = Path(args.apdata).resolve()
    user_dir = apdata_root / "Godot/app_userdata/Mutagenic"
    harness_dir = user_dir / "combat_harness"
    harness_dir.mkdir(parents=True, exist_ok=True)

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    game_request = request.get("game_request")
    if not isinstance(game_request, dict):
        raise SystemExit(f"ERROR: driver request has no game_request object: {args.request}")
    (harness_dir / "request.json").write_text(
        json.dumps(game_request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    scenario_id = str(game_request.get("scenario_id") or game_request.get("id", ""))
    seed = str(game_request.get("seed", game_request.get("default_seed", "")))
    if not scenario_id or not seed:
        print("WARNING: request has no scenario_id/seed keys; fell back to id/default_seed")

    telemetry_path = harness_dir / f"telemetry_{scenario_id}_{seed}.json"

    save_path = user_dir / "_0_6_0.dat"
    seed_save_before = None
    if args.save_dat:
        save_src = Path(args.save_dat).resolve()
        if save_src.is_file():
            shutil.copy2(save_src, save_path)
        else:
            print(f"WARNING: seed save missing, continuing without: {save_src}")
        if save_path.is_file():
            try:
                save_json = json.loads(save_path.read_text(encoding="utf-8"))
                save_json.setdefault("settings", {})["enable_fullscreen"] = False
                save_path.write_text(json.dumps(save_json, ensure_ascii=False) + "\n",
                                     encoding="utf-8")
            except Exception as exc:
                print(f"WARNING: could not finalize seed save: {exc}")
            seed_save_before = snapshot_file(save_path, "finalized")

    evidence_dir = Path(args.expected_telemetry).resolve().parent
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shots_dir = evidence_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    heartbeat_path = evidence_dir / "heartbeat.jsonl"

    steps: dict = {"window_found": False, "save_loaded": False,
                   "enter_menu_sent": False, "enter_character_sent": False,
                   "f10_sent": False, "telemetry_found": False,
                   "process_exited_early": False, "foreground": []}
    phases: list = []
    recorded_at = utc_now()
    os.environ["APPDATA"] = str(apdata_root)
    proc = subprocess.Popen([str(exe)], cwd=str(work_dir))

    log_file = user_dir / "logs" / "godot.log"
    observe_log = make_marker_tracker(log_file)
    markers = {}

    def poll_observe(phase: str) -> None:
        nonlocal markers
        markers, _ = observe_log()
        save_state = snapshot_file(save_path, "live") if save_path.exists() else None
        with heartbeat_path.open("a", encoding="utf-8") as hb:
            hb.write(json.dumps({
                "at": utc_now(), "phase": phase,
                "alive": proc.poll() is None,
                "markers": markers,
                "save": save_state,
                "telemetry": telemetry_path.is_file(),
                "foreground": foreground_title(),
            }, ensure_ascii=False) + "\n")

    try:
        time.sleep(args.boot_seconds)
        hwnd = None
        for _ in range(60):
            hwnd = find_window(proc.pid, "Mutagenic")
            if hwnd is not None:
                break
            if proc.poll() is not None:
                break
            time.sleep(0.5)
        if hwnd is None:
            print("ERROR: no visible 'Mutagenic' window for pid", proc.pid)
            return 2
        steps["window_found"] = True
        focus_window(hwnd)
        time.sleep(0.5)
        steps["foreground"].append(foreground_title())
        phases.append({"at": utc_now(), "phase": "window_found"})

        ready_deadline = time.monotonic() + 60.0
        ready = False
        while time.monotonic() < ready_deadline and proc.poll() is None:
            poll_observe("save_readiness")
            if markers.get("LOADED AND MERGED") or markers.get("No save file found"):
                ready = True
                break
            if seed_save_before and seed_save_before.get("sha256"):
                live = snapshot_file(save_path, "live")
                if live.get("sha256") != seed_save_before["sha256"]:
                    ready = True
                    break
            time.sleep(args.poll_seconds)
        steps["save_loaded"] = ready
        phases.append({"at": utc_now(), "phase": "save_readiness", "ready": ready})
        poll_observe("save_readiness_done")

        tap(hwnd, VK_ENTER, SC_ENTER)
        steps["enter_menu_sent"] = True
        time.sleep(3.0)
        capture_window(hwnd, shots_dir / "1_menu.png")
        poll_observe("after_menu_enter")

        tap(hwnd, VK_ENTER, SC_ENTER)
        steps["enter_character_sent"] = True
        time.sleep(5.0)
        capture_window(hwnd, shots_dir / "2_character_select.png")
        steps["foreground"].append(foreground_title())
        poll_observe("after_character_enter")

        deadline = time.monotonic() + args.timeout_seconds
        tap(hwnd, VK_F10, SC_F10)
        steps["f10_sent"] = True
        last_enter = time.monotonic()
        last_f10 = time.monotonic()
        while time.monotonic() < deadline:
            poll_observe("await_telemetry")
            if proc.poll() is not None:
                steps["process_exited_early"] = True
                phases.append({"at": utc_now(), "phase": "process_exited",
                               "exit_code": proc.poll()})
                break
            if telemetry_path.is_file():
                steps["telemetry_found"] = True
                phases.append({"at": utc_now(), "phase": "telemetry_found"})
                capture_window(hwnd, shots_dir / "4_telemetry.png")
                time.sleep(4.0)
                poll_observe("telemetry_grace")
                break
            now = time.monotonic()
            if now - last_enter >= 12.0:
                focus_window(hwnd)
                tap(hwnd, VK_ENTER, SC_ENTER)
                last_enter = now
            if now - last_f10 >= 5.0:
                focus_window(hwnd)
                tap(hwnd, VK_F10, SC_F10)
                last_f10 = now
            time.sleep(args.poll_seconds)
    finally:
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"],
                               capture_output=True)
        time.sleep(0.5)
        markers, _ = observe_log()

    log_dir = user_dir / "logs"
    log_evidence = []
    if log_dir.is_dir():
        for log in sorted(log_dir.glob("godot*.log"), key=lambda p: p.stat().st_mtime):
            if log.stat().st_mtime >= time.time() - 1200:
                text = log.read_text(errors="replace")
                log_evidence.append({
                    "name": log.name,
                    "size": log.stat().st_size,
                    "harness_lines": [ln for ln in text.splitlines() if "COMBAT_HARNESS" in ln],
                    "fatal_lines": [ln for ln in text.splitlines()
                                    if "ALERT" in ln or "SCRIPT ERROR" in ln or "FATAL" in ln],
                })
                shutil.copy2(log, evidence_dir / log.name)

    telemetry = None
    if telemetry_path.is_file():
        shutil.copy2(telemetry_path, Path(args.expected_telemetry).resolve())
        telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))

    status = "PASS" if steps["telemetry_found"] else "FAIL"
    result = {
        "evidence_id": "B3-X0-launch-harness-game-v2",
        "recorded_at": recorded_at,
        "ended_at": utc_now(),
        "candidate": str(exe),
        "candidate_sha256": None,
        "request": str(Path(args.request).resolve()),
        "isolated_apdata": str(apdata_root),
        "seed_save": str(Path(args.save_dat).resolve()) if args.save_dat else None,
        "seed_save_before": seed_save_before,
        "seed_save_after": snapshot_file(save_path, "after") if save_path.exists() else None,
        "scenario_id": scenario_id,
        "seed": seed,
        "telemetry_expected": str(Path(args.expected_telemetry).resolve()),
        "markers": markers,
        "phases": phases,
        "heartbeat": str(heartbeat_path),
        "steps": steps,
        "logs": log_evidence,
        "telemetry": telemetry,
        "status": status,
        "proves": "the candidate booted under an isolated APPDATA and the keyboard sequence (Enter/Enter/F10 for goto_test_level per project.godot) reached the harness, which produced telemetry for the declared scenario/seed",
        "not_proven": "in-game assert satisfaction (host driver evaluates telemetry); visual quality; persistence semantics beyond the seeded save",
    }
    evidence_out = evidence_dir / f"launcher_{scenario_id}_{seed}.json"
    evidence_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(f"launcher evidence: {evidence_out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
