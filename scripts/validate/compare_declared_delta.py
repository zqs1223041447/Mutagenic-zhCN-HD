#!/usr/bin/env python3
"""Prove that a generated pack differs from its raw baseline only as declared."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def inv(root: Path) -> dict[str, tuple[int, str]]:
    return {p.relative_to(root).as_posix(): (p.stat().st_size, sha(p)) for p in root.rglob("*") if p.is_file()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--actual", type=Path, required=True)
    ap.add_argument("--declared", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    base = inv(args.base.resolve())
    actual = inv(args.actual.resolve())
    mod = json.loads(args.declared.read_text(encoding="utf-8"))
    declared_logical = {p["path"] for p in mod.get("patches", [])}
    declared_logical.update(p["path"] for p in mod.get("asset_overlays", []))
    expected_physical = set()
    for path in declared_logical:
        p = Path(path)
        if p.suffix == ".gd":
            expected_physical.add(p.with_suffix(".gde").as_posix())
            expected_physical.add(f"{p.as_posix()}.remap")
        else:
            expected_physical.add(p.as_posix())
    changed = {k for k in set(base) | set(actual) if base.get(k) != actual.get(k)}
    unexpected = sorted(changed - expected_physical)
    missing_declared = sorted(expected_physical - changed)
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base": str(args.base.resolve()),
        "actual": str(args.actual.resolve()),
        "declared_logical_paths": sorted(declared_logical),
        "expected_physical_paths": sorted(expected_physical),
        "actual_changed_paths": sorted(changed),
        "unexpected_changed_paths": unexpected,
        "declared_paths_without_delta": missing_declared,
        "verdict": "PASS" if not unexpected and not missing_declared else "FAIL",
        "proves": "generated pack path/content delta equals manifest expansion",
        "not_proven": "runtime behavior or PCK/EXE embedding correctness",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("actual_changed_paths", "unexpected_changed_paths", "declared_paths_without_delta", "verdict")}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
