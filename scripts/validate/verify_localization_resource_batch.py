#!/usr/bin/env python3
"""Fail-closed validation for a multi-unit DISPLAY_SAFE scene/resource batch.

The validator accepts only manifest-declared text patches. It checks each
file preimage, exact old/new occurrence counts, byte-preserving replacement
outside the declared fields, and structural Godot resource token equality.
It never edits either input tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.drive or ".." in path.parts:
        raise ValueError(f"unsafe manifest path: {value}")
    return path


def structural_tokens(text: str) -> dict[str, list[str]]:
    patterns = {
        "node_declarations": r"^\[node .*$",
        "node_paths": r"NodePath\([^\n]*\)",
        "resource_paths": r"res://[^\"\s]+",
        "ext_resources": r"^\[ext_resource .*$",
        "sub_resources": r"^\[sub_resource .*$",
        "connections": r"^\[connection .*$",
    }
    return {
        name: re.findall(pattern, text, flags=re.MULTILINE)
        for name, pattern in patterns.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--units", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    base_root = args.base.resolve()
    actual_root = args.actual.resolve()
    manifest_path = args.manifest.resolve()
    units_path = args.units.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    units_data = json.loads(units_path.read_text(encoding="utf-8"))
    locked_units = {item["unit_id"]: item for item in units_data.get("entries", [])}
    errors: list[dict[str, object]] = []
    checked: list[dict[str, object]] = []
    patches = manifest.get("patches", [])
    seen_unit_ids: set[str] = set()

    if not patches:
        errors.append({"reason": "manifest_has_no_patches"})

    by_path: dict[str, list[dict[str, object]]] = {}
    for patch in patches:
        if patch.get("classification") != "TEXT_PATCH":
            errors.append({"reason": "non_text_patch_in_resource_batch", "patch": patch})
            continue
        try:
            rel = safe_relative(str(patch["path"]))
        except (KeyError, ValueError) as exc:
            errors.append({"reason": "invalid_patch_path", "detail": str(exc)})
            continue
        unit_id = patch.get("unit_id")
        unit = locked_units.get(unit_id)
        if not unit:
            errors.append({"reason": "unit_not_in_locked_extraction", "unit_id": unit_id})
        else:
            if unit_id in seen_unit_ids:
                errors.append({"reason": "duplicate_unit_id", "unit_id": unit_id})
            seen_unit_ids.add(unit_id)
            if unit.get("classification") != "DISPLAY_SAFE":
                errors.append({"reason": "unit_is_not_DISPLAY_SAFE", "unit_id": unit_id, "classification": unit.get("classification")})
            if unit.get("source") != rel.as_posix():
                errors.append({"reason": "unit_source_path_mismatch", "unit_id": unit_id, "unit_source": unit.get("source"), "patch_path": rel.as_posix()})
            if unit.get("text") != patch.get("source_text"):
                errors.append({"reason": "unit_source_text_mismatch", "unit_id": unit_id})
            if str(patch.get("preimage_sha256", "")).upper() != str(unit.get("source_file_sha256", "")).upper():
                errors.append({"reason": "unit_preimage_hash_mismatch", "unit_id": unit_id})
        by_path.setdefault(rel.as_posix(), []).append(patch)

    for rel_text, file_patches in sorted(by_path.items()):
        rel = Path(rel_text)
        base_path = base_root / rel
        actual_path = actual_root / rel
        if not base_path.is_file() or not actual_path.is_file():
            errors.append({"path": rel_text, "reason": "base_or_actual_file_missing"})
            continue
        base_bytes = base_path.read_bytes()
        actual_bytes = actual_path.read_bytes()
        base_sha = sha256(base_bytes)
        actual_sha = sha256(actual_bytes)
        file_errors: list[str] = []
        for patch in file_patches:
            expected_file_sha = str(patch.get("preimage_sha256", "")).upper()
            if expected_file_sha and base_sha != expected_file_sha:
                file_errors.append(
                    f"manifest preimage mismatch: expected {expected_file_sha}, actual {base_sha}"
                )
            old = str(patch.get("old_text", "")).encode("utf-8")
            new = str(patch.get("new_text", "")).encode("utf-8")
            expected_count = int(patch.get("expected_occurrences", 1))
            old_count = base_bytes.count(old)
            new_count = actual_bytes.count(new)
            if old_count != expected_count:
                file_errors.append(
                    f"old occurrence count for {patch.get('unit_id')}: expected {expected_count}, got {old_count}"
                )
            if new_count != expected_count:
                file_errors.append(
                    f"new occurrence count for {patch.get('unit_id')}: expected {expected_count}, got {new_count}"
                )
        try:
            base_text = base_bytes.decode("utf-8")
            actual_text = actual_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            file_errors.append(f"UTF-8 decode failed: {exc}")
            base_text = actual_text = ""

        normalized_base = base_text
        normalized_actual = actual_text
        for patch in file_patches:
            old_text = str(patch.get("old_text", ""))
            new_text = str(patch.get("new_text", ""))
            normalized_base = normalized_base.replace(old_text, "<DECLARED_TEXT_PATCH>", 1)
            normalized_actual = normalized_actual.replace(new_text, "<DECLARED_TEXT_PATCH>", 1)
        if normalized_base != normalized_actual:
            file_errors.append("content differs outside declared text fields")
        token_diffs = {}
        if base_text and actual_text:
            base_tokens = structural_tokens(base_text)
            actual_tokens = structural_tokens(actual_text)
            token_diffs = {
                key: {"base": base_tokens[key], "actual": actual_tokens[key]}
                for key in base_tokens
                if base_tokens[key] != actual_tokens[key]
            }
            if token_diffs:
                file_errors.append("structural Godot token collections changed")
        errors.extend({"path": rel_text, "reason": detail} for detail in file_errors)
        checked.append({
            "path": rel_text,
            "base_sha256": base_sha,
            "actual_sha256": actual_sha,
            "patch_count": len(file_patches),
            "structural_token_diff_count": len(token_diffs),
            "errors": file_errors,
        })

    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base": str(base_root),
        "actual": str(actual_root),
        "manifest": str(manifest_path),
        "units": str(units_path),
        "checked_files": checked,
        "checked_patch_count": sum(len(items) for items in by_path.values()),
        "checked_unit_count": len(seen_unit_ids),
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
        "proves": "each declared TEXT_PATCH has a matching base preimage and the actual resource differs only at declared text fields while structural resource tokens remain unchanged",
        "not_proven": "translation quality, runtime interaction, font rendering, gameplay, persistence, or release readiness",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "checked_files": len(checked),
        "checked_patch_count": report["checked_patch_count"],
        "error_count": len(errors),
        "verdict": report["verdict"],
    }, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
