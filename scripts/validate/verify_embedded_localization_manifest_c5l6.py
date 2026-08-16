#!/usr/bin/env python3
"""Verify every manifest-declared serialized text field is present exactly in the
extracted candidate and the old English field is absent.

Mirrors scripts/validate/verify_embedded_localization_manifest.py semantics:
exact `text = "..."` serialized field check against the extracted scene files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--extract", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    mod = json.loads(args.manifest.read_text(encoding="utf-8"))
    extract = args.extract.resolve()
    hits = []
    misses = []
    old_fields_remaining = []
    for patch in mod.get("patches", []):
        if patch.get("classification") == "ASSET_PATCH":
            continue
        rel = patch["path"]
        target = extract / rel
        if not target.is_file():
            misses.append({"unit_id": patch.get("unit_id"), "path": rel, "reason": "file_missing"})
            continue
        content = target.read_text(encoding="utf-8")
        new = patch["new_text"]
        old = patch["old_text"]
        new_count = content.count(new)
        old_count = content.count(old)
        expected = patch.get("expected_occurrences", 1)
        if new_count == expected:
            hits.append({"unit_id": patch.get("unit_id"), "path": rel, "new_text": new, "count": new_count})
        else:
            misses.append({"unit_id": patch.get("unit_id"), "path": rel, "expected": expected, "actual_new": new_count, "new_text": new})
        if old_count > 0:
            old_fields_remaining.append({"unit_id": patch.get("unit_id"), "path": rel, "old_text": old, "count": old_count})

    report = {
        "manifest": str(args.manifest.resolve()),
        "declared_patches": len(mod.get("patches", [])),
        "new_field_hits": len(hits),
        "new_field_misses": misses,
        "old_fields_remaining": old_fields_remaining,
        "verdict": "PASS" if not misses and not old_fields_remaining else "FAIL",
        "proves": "every manifest-declared serialized text field is present exactly expected times and old fields are absent in the extracted candidate",
        "not_proven": "visual rendering, dynamic text, or interaction",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"hits": len(hits), "misses": len(misses), "old_remaining": len(old_fields_remaining), "verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
