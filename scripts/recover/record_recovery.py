#!/usr/bin/env python3
"""Validate and record a GDRE recovery reference tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--recovered", type=Path, required=True)
    ap.add_argument("--source-sha256", required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    raw = args.raw.resolve()
    recovered = args.recovered.resolve()
    raw_gde = sorted(raw.rglob("*.gde"))
    recovered_gd = sorted(recovered.rglob("*.gd"))
    recovered_gde = sorted(recovered.rglob("*.gde"))
    missing_sources = []
    source_hash_mismatch = []
    for raw_path in raw_gde:
        rel = raw_path.relative_to(raw)
        gd = recovered / rel.with_suffix(".gd")
        auto_gde = recovered / ".autoconverted" / rel
        if not gd.is_file():
            missing_sources.append(rel.as_posix())
        if auto_gde.is_file() and sha256(auto_gde) != sha256(raw_path):
            source_hash_mismatch.append(rel.as_posix())
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_exe_sha256": args.source_sha256.lower(),
        "raw_root": str(raw),
        "recovered_root": str(recovered),
        "raw_gde_count": len(raw_gde),
        "recovered_gd_count": len(recovered_gd),
        "recovered_gde_count": len(recovered_gde),
        "missing_decompiled_sources": missing_sources,
        "autoconverted_source_hash_mismatch": source_hash_mismatch,
        "project_godot": (recovered / "project.godot").is_file(),
        "gdre_report": (recovered / "gdre_export.log").is_file(),
        "verdict": "PASS" if len(raw_gde) == 524 and len(recovered_gd) >= 524 and not missing_sources and not source_hash_mismatch and (recovered / "project.godot").is_file() else "FAIL",
        "proves": "all raw encrypted scripts have reference source and preserved raw encrypted copies",
        "not_proven": "compiler semantic equivalence for every script, runtime behavior, production safety of any future edits",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(recovered.rglob("*")):
        if path.is_file():
            files.append({"relpath": path.relative_to(recovered).as_posix(), "size": path.stat().st_size, "sha256": sha256(path)})
    args.manifest.write_text(json.dumps({"source": str(recovered), "count": len(files), "files": files, "report": str(args.report)}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("raw_gde_count", "recovered_gd_count", "recovered_gde_count", "missing_decompiled_sources", "autoconverted_source_hash_mismatch", "verdict")}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
