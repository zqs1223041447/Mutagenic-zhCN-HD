#!/usr/bin/env python3
"""Capture reproducibility metadata for the local Windows toolchain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str]) -> dict:
    try:
        p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
        return {"command": command, "returncode": p.returncode,
                "stdout": p.stdout, "stderr": p.stderr}
    except Exception as exc:
        return {"command": command, "error": repr(exc)}


def file_hash(path: Path) -> dict:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            size += len(block)
            h.update(block)
    return {"path": str(path.resolve()), "size": size, "sha256": h.hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "10_logs/environment.json")
    args = ap.parse_args()
    py = ROOT / "02_tools/venv/Scripts/python.exe"
    gdre = ROOT / "02_tools/gdre/gdre_tools.exe"
    tools = [p for p in (py, gdre, ROOT / "00_original/Mutagenic.exe") if p.is_file()]
    commands = [
        [str(py), "--version"],
        ["git", "--version"],
        ["uv", "--version"],
        [str(gdre), "--version"],
        [str(gdre), "--help"],
        [str(gdre), "--godot-version"],
        [str(gdre), "--list-bytecode-versions"],
    ]
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cwd": str(ROOT),
        "os": {"platform": platform.platform(), "release": platform.release(),
               "version": platform.version(), "machine": platform.machine()},
        "python": {"executable": sys.executable, "version": sys.version},
        "powershell": os.environ.get("PSVersionTable", "not exposed to child process"),
        "tools": [file_hash(p) for p in tools],
        "commands": [run(command) for command in commands],
        "resolved_commands": {name: shutil.which(name) for name in ("git", "uv", "python")},
    }
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"written={out}")
    for item in report["tools"]:
        print(f"tool={item['path']} sha256={item['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
