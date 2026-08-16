#!/usr/bin/env python3
"""Verify every declared TEXT_PATCH in an extracted runtime tree.

The check is manifest-driven and matches exact serialized fields. It does not
use arbitrary substring presence, so English node names and paths may remain
unchanged while their display text is localized.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    manifest_path = args.manifest.resolve()
    candidate = args.candidate.resolve()
    if not root.is_dir():
        raise SystemExit(f"ERROR: extracted runtime root does not exist: {root}")
    if not manifest_path.is_file():
        raise SystemExit(f"ERROR: manifest does not exist: {manifest_path}")
    if not candidate.is_file():
        raise SystemExit(f"ERROR: candidate EXE does not exist: {candidate}")

    manifest = read_json(manifest_path)
    patches = manifest.get("patches", [])
    checks: list[dict[str, Any]] = []
    for patch in patches:
        relative = str(patch.get("path", ""))
        path = root / Path(relative)
        old_text = str(patch.get("old_text", ""))
        new_text = str(patch.get("new_text", ""))
        expected = int(patch.get("expected_occurrences", 1))
        check: dict[str, Any] = {
            "unit_id": patch.get("unit_id"),
            "path": relative,
            "expected_occurrences": expected,
        }
        if not path.is_file():
            check["missing_file"] = True
            checks.append(check)
            continue
        content = path.read_text(encoding="utf-8")
        old_count = content.count(old_text)
        new_count = content.count(new_text)
        check.update(
            {
                "old_field_count": old_count,
                "new_field_count": new_count,
                "old_field_absent": old_count == 0,
                "new_field_exact": new_count == expected,
            }
        )
        checks.append(check)

    passed = all(
        check.get("missing_file") is not True
        and check.get("old_field_absent") is True
        and check.get("new_field_exact") is True
        for check in checks
    )
    report = {
        "evidence_id": "manifest-driven-embedded-localization-text",
        "candidate": str(candidate),
        "candidate_sha256": sha256(candidate),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "patch_count": len(patches),
        "checks": checks,
        "status": "PASS" if passed else "FAIL",
        "proves": (
            "every manifest-declared serialized TEXT_PATCH is present exactly at "
            "its expected occurrence count and its old field is absent in the "
            "fully extracted candidate runtime"
        ),
        "not_proven": (
            "visual rendering, dynamic text, interaction, persistence, broad "
            "localization, or release readiness"
        ),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"status": report["status"], "patch_count": len(patches), "candidate_sha256": report["candidate_sha256"]},
            ensure_ascii=False,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
