#!/usr/bin/env python3
"""Record a complete GDRE PCK listing for a final EXE."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GDRE = ROOT / "02_tools/gdre/gdre_tools.exe"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("exe", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    exe = args.exe.resolve()
    result = subprocess.run(
        [str(GDRE), "--headless", f"--list-files={exe}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    paths = [line.strip() for line in result.stdout.splitlines() if line.strip().startswith("res://")]
    suffixes = {
        ".gde": sum(path.endswith(".gde") for path in paths),
        ".gd.remap": sum(path.endswith(".gd.remap") for path in paths),
        "plain .gd": sum(path.endswith(".gd") for path in paths),
        ".tscn": sum(path.endswith(".tscn") for path in paths),
        ".tres": sum(path.endswith(".tres") for path in paths),
    }
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "exe": str(exe),
        "returncode": result.returncode,
        "stdout_sha256": hashlib.sha256(result.stdout.encode("utf-8", "replace")).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr.encode("utf-8", "replace")).hexdigest(),
        "listed_count": len(paths),
        "suffix_counts": suffixes,
        "files": paths,
        "verdict": "PASS" if result.returncode == 0 and len(paths) == 3744 else "FAIL",
        "proves": "GDRE can list the final embedded PCK and the complete path inventory is recorded",
        "not_proven": "runtime behavior, gameplay flow, visual quality, or persistence",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("returncode", "listed_count", "suffix_counts", "verdict")}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
