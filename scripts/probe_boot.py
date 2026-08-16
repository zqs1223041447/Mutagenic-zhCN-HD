#!/usr/bin/env python3
"""Runtime boot probe: launch a Godot exe and decide PASS/FAIL from evidence.

Evidence used (no visual judgement):
  1. Whether a modal window (e.g. "ALERT!") belonging to the process exists.
  2. Whether the newest Godot log contains boot progress markers.
  3. Process alive/exit code.

A process staying alive is NOT treated as success, because a blocking error
dialog also keeps the process alive.

Usage:
    python scripts/probe_boot.py <exe_path> [--seconds 12] [--label NAME]
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

LOG_DIR = Path(os.environ["APPDATA"]) / "Godot/app_userdata/Mutagenic/logs"

# Markers that only appear once the project actually booted and ran autoloads.
BOOT_MARKERS = [
    "GameState getting ready",
    "Loaded data for",
    "Physics FPS set to",
]
FATAL_MARKERS = [
    "Couldn't load project data",
    "Error: Couldn't load project",
]

user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def windows_of_pid(pid: int) -> list[str]:
    """Return titles of visible top-level windows owned by pid."""
    titles: list[str] = []

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
        titles.append(buf.value)
        return True

    EnumWindows(EnumWindowsProc(cb), 0)
    return titles


def newest_log(after: float) -> Path | None:
    """Return the best (most detailed) log written since `after`.

    Godot writes two files per run:
      godot.log                  - 6-line summary (overwritten each run)
      godot<ISO-timestamp>.log   - full boot log

    We prefer the timestamped one because it contains the boot markers.
    """
    if not LOG_DIR.exists():
        return None
    # Look for timestamped logs created during this run
    ts_cands = [
        p for p in LOG_DIR.glob("godot20*.log")
        if p.stat().st_mtime >= after - 1
    ]
    if ts_cands:
        return max(ts_cands, key=lambda p: p.stat().st_mtime)
    # Fallback to any log
    cands = [p for p in LOG_DIR.glob("godot*.log") if p.stat().st_mtime >= after - 1]
    if not cands:
        return None
    return max(cands, key=lambda p: p.stat().st_size)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("exe", type=Path)
    ap.add_argument("--seconds", type=int, default=12)
    ap.add_argument("--label", default=None)
    args = ap.parse_args()

    exe = args.exe.resolve()
    label = args.label or exe.name
    if not exe.exists():
        print(f"FAIL {label}: exe not found: {exe}")
        return 2

    started = time.time()
    proc = subprocess.Popen([str(exe)], cwd=str(exe.parent))
    time.sleep(args.seconds)

    alive = proc.poll() is None
    titles = windows_of_pid(proc.pid) if alive else []
    dialog = [t for t in titles if t.strip() and t.strip().lower() != "mutagenic"]

    log = newest_log(started)
    text = log.read_text(errors="replace") if log else ""
    booted = [m for m in BOOT_MARKERS if m in text]
    fatal = [m for m in FATAL_MARKERS if m in text]

    if alive:
        proc.kill()
        proc.wait(timeout=10)

    print(f"=== {label} ===")
    print(f"exe            : {exe}")
    print(f"alive@{args.seconds}s     : {alive} (exit={proc.returncode})")
    print(f"windows        : {titles}")
    print(f"modal dialog   : {dialog if dialog else 'none'}")
    print(f"log            : {log.name if log else 'NONE'} ({len(text.splitlines())} lines)")
    print(f"boot markers   : {booted if booted else 'NONE'}")
    print(f"fatal markers  : {fatal if fatal else 'none'}")

    game_window = any("Mutagenic" in t and "ALERT" not in t for t in titles)
    alert_window = any("ALERT" in t for t in titles)

    # Never fall back to an older log: it is not evidence for this process.
    # A current run without a current log must remain unproven/FAIL.
    current_evidence = bool(log) or bool(titles)
    ok = current_evidence and (bool(booted) or game_window) and not fatal and not alert_window
    print(f"game_window    : {game_window}")
    print(f"alert_window   : {alert_window}")
    print(f"VERDICT        : {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
