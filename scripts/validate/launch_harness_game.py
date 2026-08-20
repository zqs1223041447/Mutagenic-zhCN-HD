#!/usr/bin/env python3
"""B2-X0 S2 harness launcher: boot candidate, drive UI to TestLevel, harvest telemetry.

Stages an isolated APPDATA (save seed + driver game_request), launches the
candidate, sends keyboard input to its window (Menu Enter -> CharacterSelect
Enter -> Hideout -> F10 twice for goto_test_level, the action's real keybind
per project.godot), polls for the k5 harness telemetry file under
user://combat_harness/, copies it to the driver-expected path and captures
game logs as runtime evidence.

Usage:
    python scripts/validate/launch_harness_game.py --request <driver request json>
        --candidate <exe> --expected-telemetry <out json> --apdata <dir>
        [--save-dat <seed save>] [--boot-seconds 8] [--timeout-seconds 90]
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
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
VK_F10 = 0x7A
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


def tap(key: int, hold_ms: int = 100, gap_ms: int = 100) -> None:
    user32.keybd_event(key, 0, 0, None)
    time.sleep(hold_ms / 1000.0)
    user32.keybd_event(key, 0, 2, None)
    time.sleep(gap_ms / 1000.0)


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--expected-telemetry", required=True)
    ap.add_argument("--apdata", required=True)
    ap.add_argument("--save-dat", default=None)
    ap.add_argument("--boot-seconds", type=int, default=8)
    ap.add_argument("--timeout-seconds", type=int, default=90)
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
    scenario_id = str(game_request.get("scenario_id", ""))
    seed = str(game_request.get("seed", ""))
    telemetry_path = harness_dir / f"telemetry_{scenario_id}_{seed}.json"

    if args.save_dat:
        save_src = Path(args.save_dat).resolve()
        if save_src.is_file():
            shutil.copy2(save_src, user_dir / "_0_6_0.dat")
        else:
            print(f"WARNING: seed save missing, continuing without: {save_src}")
        save_dst = user_dir / "_0_6_0.dat"
        if save_dst.is_file():
            try:
                save_json = json.loads(save_dst.read_text(encoding="utf-8"))
                save_json.setdefault("settings", {})["enable_fullscreen"] = False
                save_dst.write_text(json.dumps(save_json, ensure_ascii=False) + "\n",
                                    encoding="utf-8")
            except Exception:
                pass

    evidence_dir = Path(args.expected_telemetry).resolve().parent
    evidence_dir.mkdir(parents=True, exist_ok=True)
    shots_dir = evidence_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    steps: dict = {"window_found": False, "save_loaded": False,
                   "enter_menu_sent": False, "enter_character_sent": False,
                   "f10_sent": False, "telemetry_found": False, "foreground": []}
    recorded_at = utc_now()
    os.environ["APPDATA"] = str(apdata_root)
    proc = subprocess.Popen([str(exe)], cwd=str(work_dir))
    try:
        time.sleep(args.boot_seconds)
        hwnd = None
        for _ in range(60):
            hwnd = find_window(proc.pid, "Mutagenic")
            if hwnd is not None:
                break
            time.sleep(0.5)
        if hwnd is None:
            print("ERROR: no visible 'Mutagenic' window for pid", proc.pid)
            return 2
        steps["window_found"] = True
        focus_window(hwnd)
        time.sleep(0.5)
        steps["foreground"].append(foreground_title())

        log_file = user_dir / "logs" / "godot.log"
        ready_deadline = time.monotonic() + 60.0
        ready = False
        while time.monotonic() < ready_deadline:
            if log_file.is_file():
                text = log_file.read_text(errors="replace")
                if "LOADED AND MERGED" in text:
                    ready = True
                    break
            time.sleep(1.0)
        steps["save_loaded"] = ready

        tap(hwnd, VK_ENTER, SC_ENTER)
        steps["enter_menu_sent"] = True
        time.sleep(4.0)
        capture_window(hwnd, shots_dir / "1_menu.png")
        tap(hwnd, VK_ENTER, SC_ENTER)
        steps["enter_character_sent"] = True
        time.sleep(6.0)
        capture_window(hwnd, shots_dir / "2_character_select.png")
        steps["foreground"].append(foreground_title())

        deadline = time.monotonic() + args.timeout_seconds
        tap(hwnd, VK_F10, SC_F10)
        steps["f10_sent"] = True
        time.sleep(2.0)
        capture_window(hwnd, shots_dir / "3_after_f10.png")
        last_enter = time.monotonic()
        while time.monotonic() < deadline:
            if telemetry_path.is_file():
                steps["telemetry_found"] = True
                break
            if time.monotonic() - last_enter >= 12.0:
                tap(hwnd, VK_ENTER, SC_ENTER)
                last_enter = time.monotonic()
            tap(hwnd, VK_F10, SC_F10)
            time.sleep(4.0)
    finally:
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"],
                               capture_output=True)
        time.sleep(0.5)

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
        "evidence_id": "B2-X0-launch-harness-game-v1",
        "recorded_at": recorded_at,
        "ended_at": utc_now(),
        "candidate": str(exe),
        "candidate_sha256": None,
        "request": str(Path(args.request).resolve()),
        "isolated_apdata": str(apdata_root),
        "seed_save": str(Path(args.save_dat).resolve()) if args.save_dat else None,
        "scenario_id": scenario_id,
        "seed": seed,
        "telemetry_expected": str(Path(args.expected_telemetry).resolve()),
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
