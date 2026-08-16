#!/usr/bin/env python3
"""Recover a reference tree from an immutable original executable.

The destination must not exist.  The script reads the local encryption key
without printing it, invokes the pinned GDRE binary, and stores stdout/stderr
inside the experiment directory.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", type=Path, default=ROOT / "00_original/Mutagenic.exe")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--log-dir", type=Path, required=True)
    args = ap.parse_args()

    exe = args.exe.resolve()
    out = args.out.resolve()
    log_dir = args.log_dir.resolve()
    gdre = (ROOT / "02_tools/gdre/gdre_tools.exe").resolve()
    key_file = ROOT / "manifests/script_key.txt"
    for path in (exe, gdre, key_file):
        if not path.is_file():
            raise SystemExit(f"ERROR: required input missing: {path}")
    if out.exists():
        raise SystemExit(f"ERROR: refusing to overwrite recovery destination: {out}")
    if log_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite log directory: {log_dir}")
    log_dir.mkdir(parents=True, exist_ok=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    key = key_file.read_text(encoding="utf-8").strip()
    if len(key) != 64:
        raise SystemExit("ERROR: local script key is not 64 hex characters")

    stdout_path = log_dir / "gdre_stdout.log"
    stderr_path = log_dir / "gdre_stderr.log"
    command = [str(gdre), "--headless", f"--recover={exe}",
               f"--key={key}", f"--output={out}",
               "--force-bytecode-version=3.5.3.stable"]
    with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout:
        with stderr_path.open("w", encoding="utf-8", errors="replace") as stderr:
            result = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, text=True)
    if result.returncode != 0:
        print(f"GDRE_EXIT={result.returncode}")
        print(f"stdout={stdout_path}")
        print(f"stderr={stderr_path}")
        return result.returncode

    report = out / "gdre_export.log"
    if not report.is_file():
        raise SystemExit(f"ERROR: GDRE succeeded but report is missing: {report}")
    print(f"GDRE_EXIT=0")
    print(f"recovered={out}")
    print(f"stdout={stdout_path}")
    print(f"stderr={stderr_path}")
    print(f"report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
