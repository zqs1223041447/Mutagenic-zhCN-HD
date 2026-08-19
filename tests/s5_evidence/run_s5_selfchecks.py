#!/usr/bin/env python3
"""B2-X2 S5 evidence self-test runner.

Thin wrapper: resolves the repo root from the script location and delegates to
scripts/validate/s5_evidence_selftests.py, which emits a selfcheck evidence
JSON under 10_logs (git-ignored).  Exit code is the driver's selfcheck verdict
(0 = PASS, 1 = SELFTEST_FAIL).

    python tests/s5_evidence/run_s5_selfchecks.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[1]
    selftests = repo_root / "scripts" / "validate" / "s5_evidence_selftests.py"
    if not selftests.is_file():
        print("ERROR: selftests module not found at " + str(selftests), file=sys.stderr)
        return 1
    proc = subprocess.run([sys.executable, str(selftests)], capture_output=True, text=True, timeout=900)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())