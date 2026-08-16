#!/usr/bin/env python3
"""Compare two extracted runtime trees and save a complete hash manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            size += len(block)
            h.update(block)
    return size, h.hexdigest()


def inventory(root: Path) -> dict[str, dict]:
    out = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        size, sha = digest(path)
        out[rel] = {"size": size, "sha256": sha}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("expected", type=Path)
    ap.add_argument("actual", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, default=None)
    args = ap.parse_args()
    expected = inventory(args.expected.resolve())
    actual = inventory(args.actual.resolve())
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatch = sorted(k for k in set(expected) & set(actual) if expected[k] != actual[k])
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "expected_root": str(args.expected.resolve()),
        "actual_root": str(args.actual.resolve()),
        "expected_count": len(expected),
        "actual_count": len(actual),
        "missing": missing,
        "extra": extra,
        "content_mismatch": mismatch,
        "verdict": "PASS" if not missing and not extra and not mismatch else "FAIL",
        "proves": "path set and SHA-256 content equality between the two trees",
        "not_proven": "runtime behavior or source recovery correctness",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps({
            "recorded_at": report["recorded_at"],
            "root": str(args.expected.resolve()),
            "count": len(expected),
            "files": [{"relpath": k, **v} for k, v in expected.items()],
        }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("expected_count", "actual_count", "missing", "extra", "content_mismatch", "verdict")}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
