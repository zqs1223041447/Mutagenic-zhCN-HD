#!/usr/bin/env python3
"""B3-P1-X1 S2 save-bisect runner: launch a candidate game in an isolated
APPDATA profile and record the GameState.do_save_game() marker timeline.

The diagnostic candidate (built from mods/b3-p1-s2-diagnostic) writes one
marker file per do_save_game() substep under user://s2_markers/ (m01_enter,
m02_timestamp, m03_checksum, m04_stamp, m05_serialize, m06_dataprep,
m07_pre_open, m08_open_done, m09_store, m10_close, m11_onsave_done).  The
last marker present at the end of the observation window identifies the
substep where the observed debounce-save stall occurs.

No host-specific paths are hardcoded; everything comes from CLI arguments.
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

MARKERS_REL = Path("Godot/app_userdata/Mutagenic/s2_markers")
SAVE_REL = Path("Godot/app_userdata/Mutagenic/_0_6_0.dat")
LOG_REL = Path("Godot/app_userdata/Mutagenic/logs/godot.log")
TELEMETRY_GLOB = "telemetry_*.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cpu_percent(pid: int, span: float = 2.0) -> float:
    kernel32 = ctypes.windll.kernel32
    h = kernel32.OpenProcess(0x400, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return -1.0
    k1 = ctypes.c_ulonglong(); u1 = ctypes.c_ulonglong()
    c1 = ctypes.c_ulonglong(); e1 = ctypes.c_ulonglong()
    kernel32.GetProcessTimes(h, ctypes.byref(c1), ctypes.byref(e1), ctypes.byref(k1), ctypes.byref(u1))
    time.sleep(span)
    k2 = ctypes.c_ulonglong(); u2 = ctypes.c_ulonglong()
    c2 = ctypes.c_ulonglong(); e2 = ctypes.c_ulonglong()
    kernel32.GetProcessTimes(h, ctypes.byref(c2), ctypes.byref(e2), ctypes.byref(k2), ctypes.byref(u2))
    ctypes.windll.kernel32.CloseHandle(h)
    return round(((k2.value + u2.value) - (k1.value + u1.value)) / 1e7 / span * 100.0, 1)


def graceful_close(hwnd: int) -> None:
    ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)


SCAN = {0x0D: 0x1C, 0x23: 0x4F}


def post_key(hwnd: int, vk: int) -> None:
    scan = SCAN.get(vk, 0)
    ctypes.windll.user32.PostMessageW(hwnd, 0x0100, vk, (scan << 16) | 1)
    ctypes.windll.user32.PostMessageW(hwnd, 0x0101, vk, (scan << 16) | 0xC0000001)


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class INPUT(ctypes.Structure):
    class _I(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _fields_ = [("type", ctypes.c_ulong), ("i", _I)]


def send_key_fg(hwnd: int, vk: int) -> bool:
    """Bring the game to foreground and send a real key via SendInput so the
    raw-input path can populate physical_scancode for action matching.
    Returns True if the game window ended up focused (fg check)."""
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.keybd_event(0x12, 0, 0, None)  # ALT down (foreground unlock)
    tid = user32.GetWindowThreadProcessId(hwnd, None)
    user32.AttachThreadInput(kernel32.GetCurrentThreadId(), tid, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.SetActiveWindow(hwnd)
    user32.SetFocus(hwnd)
    user32.AttachThreadInput(kernel32.GetCurrentThreadId(), tid, False)
    user32.keybd_event(0x12, 0, 2, None)  # ALT up
    time.sleep(0.15)
    fg = user32.GetForegroundWindow()
    ok = bool(fg) and (fg == hwnd)
    if not ok:
        return False
    down = INPUT(1, INPUT._I(KEYBDINPUT(vk, 0, 0, 0, None)))
    up = INPUT(1, INPUT._I(KEYBDINPUT(vk, 0, 2, 0, None)))
    arr = (INPUT * 2)(down, up)
    user32.SendInput(2, arr, ctypes.sizeof(INPUT))
    return True


def find_window(pid: int, title: str, timeout: float) -> int | None:
    user32 = ctypes.windll.user32
    found = []

    def cb(hwnd, _lp):
        wpid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value != pid:
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)
        if buf.value == title and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    proto = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        found.clear()
        user32.EnumWindows(proto(cb), 0)
        if found:
            return found[0]
        time.sleep(0.25)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe", type=Path, required=True, help="candidate game EXE")
    ap.add_argument("--appdata", type=Path, required=True, help="isolated APPDATA root (created if missing)")
    ap.add_argument("--out-dir", type=Path, required=True, help="evidence output directory")
    ap.add_argument("--seed-save", type=Path, default=None, help="optional save to stage as _0_6_0.dat")
    ap.add_argument("--request", type=Path, default=None, help="optional combat_harness request.json")
    ap.add_argument("--duration", type=float, default=45.0, help="observation window seconds")
    ap.add_argument("--poll", type=float, default=0.25, help="poll interval seconds")
    ap.add_argument("--cpu-span", type=float, default=2.0, help="CPU sample span seconds")
    ap.add_argument("--control", type=str, required=True, help="control id (a/b/c) recorded in evidence")
    ap.add_argument("--enter-from", type=float, default=None, help="start Enter taps at t seconds (None=off)")
    ap.add_argument("--enter-every", type=float, default=1.5)
    ap.add_argument("--end-from", type=float, default=None, help="start End-key taps at t seconds (None=off)")
    ap.add_argument("--end-every", type=float, default=3.0)
    ap.add_argument("--end-sendinput", action="store_true", help="deliver End via keybd_event (raw-input path) instead of PostMessage")
    args = ap.parse_args()

    appdata = args.appdata.resolve()
    user_dir = appdata / "Godot/app_userdata/Mutagenic"
    user_dir.mkdir(parents=True, exist_ok=True)
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    events: list[dict] = []
    t0 = time.monotonic()

    def note(kind: str, detail: str) -> None:
        events.append({"t_sec": round(time.monotonic() - t0, 2), "kind": kind, "detail": detail})

    save_path = user_dir / SAVE_REL.name
    save_before = None
    if args.seed_save:
        src = args.seed_save.resolve()
        shutil.copy2(src, save_path)
        save_before = sha256_bytes(save_path.read_bytes())
        note("staged", f"seed_save={src.name} sha={save_before[:10]} size={save_path.stat().st_size}")
    if args.request:
        req_dir = user_dir / "combat_harness"
        req_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.request.resolve(), req_dir / "request.json")
        note("staged", f"request={args.request.name}")

    env = dict(os.environ.copy())
    env["APPDATA"] = str(appdata)
    proc = subprocess.Popen([str(args.exe)], cwd=str(args.exe.parent), env=env)
    note("launched", f"pid={proc.pid}")

    hwnd = find_window(proc.pid, "Mutagenic", 25.0)
    note("window", f"hwnd={hwnd}")

    markers_dir = user_dir / "s2_markers"
    last_markers: dict[str, tuple[int, int]] = {}
    last_save_sha = save_before
    last_log_size = 0
    last_cpu = 0.0
    next_cpu = time.monotonic() + 3.0
    telemetry_found = False

    deadline = time.monotonic() + args.duration
    enter_next = time.monotonic() + args.enter_from if args.enter_from is not None else None
    end_next = time.monotonic() + args.end_from if args.end_from is not None else None
    enter_count = 0
    end_count = 0
    while time.monotonic() < deadline:
        now = time.monotonic()
        if hwnd:
            if enter_next is not None and now >= enter_next:
                post_key(hwnd, 0x0D)
                enter_count += 1
                note("key_enter", f"count={enter_count}")
                enter_next = now + args.enter_every
            if end_next is not None and now >= end_next:
                if args.end_sendinput:
                    fg_ok = send_key_fg(hwnd, 0x23)
                    note("key_end", f"count={end_count + 1} via=sendinput fg_ok={fg_ok}")
                else:
                    post_key(hwnd, 0x23)
                    note("key_end", f"count={end_count + 1} via=postmessage")
                end_count += 1
                end_next = now + args.end_every
        if markers_dir.is_dir():
            cur = {}
            for p in markers_dir.iterdir():
                if p.is_file():
                    st = p.stat()
                    cur[p.name] = (st.st_mtime_ns, st.st_size)
            for name, sig in sorted(cur.items()):
                if name not in last_markers:
                    note("marker", name)
                elif last_markers[name] != sig:
                    note("marker_rewrite", f"{name} mtime={sig[0]}")
            last_markers = cur
        if save_path.exists():
            cur_sha = sha256_bytes(save_path.read_bytes())
            if cur_sha != last_save_sha:
                note("save_rewrite", f"sha={cur_sha[:10]} size={save_path.stat().st_size}")
                last_save_sha = cur_sha
        if LOG_REL.exists():
            cur_size = (user_dir / "logs/godot.log").stat().st_size
            if cur_size != last_log_size:
                note("log_growth", f"bytes={cur_size}")
                last_log_size = cur_size
        for tel in (user_dir / "combat_harness").glob(TELEMETRY_GLOB) if (user_dir / "combat_harness").is_dir() else []:
            if not telemetry_found:
                telemetry_found = True
                note("telemetry", tel.name)
        if now >= next_cpu:
            last_cpu = cpu_percent(proc.pid, args.cpu_span)
            note("cpu", f"{last_cpu}%")
            next_cpu = now + 8.0
        if proc.poll() is not None:
            note("process_exited", f"code={proc.returncode}")
            break
        time.sleep(args.poll)

    if hwnd and proc.poll() is None:
        graceful_close(hwnd)
        time.sleep(3.0)
    if proc.poll() is None:
        proc.kill()
        note("killed", "terminated after graceful close timeout")

    final_markers = sorted(p.name for p in markers_dir.iterdir()) if markers_dir.is_dir() else []
    log_excerpt = ""
    log_path = user_dir / "logs/godot.log"
    if log_path.exists():
        lines = log_path.read_text(errors="replace").splitlines()
        log_excerpt = "\n".join(lines[-40:])
    evidence = {
        "task_id": "B3-P1-X1",
        "control": args.control,
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "candidate_exe": str(args.exe),
        "candidate_exe_sha256": sha256_bytes(args.exe.resolve().read_bytes()),
        "appdata": str(appdata),
        "save_before_sha256": save_before,
        "save_after_sha256": last_save_sha,
        "window_found": hwnd is not None,
        "telemetry_found": telemetry_found,
        "final_markers": final_markers,
        "marker_count": len(final_markers),
        "last_marker": final_markers[-1] if final_markers else None,
        "key_enter_count": enter_count,
        "key_end_count": end_count,
        "events": events,
        "log_tail": log_excerpt,
    }
    report = out_dir / f"control_{args.control}_evidence.json"
    report.write_text(json.dumps(evidence, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "control": args.control,
        "window_found": evidence["window_found"],
        "marker_count": evidence["marker_count"],
        "last_marker": evidence["last_marker"],
        "final_markers": evidence["final_markers"],
        "save_before": (save_before or "none")[:10],
        "save_after": (last_save_sha or "none")[:10],
        "telemetry_found": telemetry_found,
        "events": len(events),
        "keys": {"enter": enter_count, "end": end_count},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
