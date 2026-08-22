#!/usr/bin/env python3
"""B3-P2-X2 S3 persistence gate - offline self-test runner.

Thin wrapper: resolves the repo root from the script location and delegates
to scripts/validate/s3_persistence_selftests.py, which emits a selfcheck
evidence JSON under 10_logs (git-ignored).  Exit code is the selftest
verdict (0 = PASS, 1 = SELFTEST_FAIL).

    python tests/s3_persistence/run_selfchecks.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[1]
    selftests = repo_root / "scripts" / "validate" / "s3_persistence_selftests.py"
    if not selftests.is_file():
        print(f"ERROR: selftests module not found at {selftests}", file=sys.stderr)
        return 1
    proc = subprocess.run([sys.executable, str(selftests)], capture_output=True,
                          text=True, timeout=300)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())