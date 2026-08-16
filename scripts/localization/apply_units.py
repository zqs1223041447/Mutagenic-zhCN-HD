#!/usr/bin/env python3
"""Apply a unit-id keyed localization batch to a generated worktree.

This is intentionally narrower than the historical apply_translation.py:
there is no global text lookup.  Each entry must identify one exact source
literal by unit_id, target file preimage hash, source text and occurrence
location.  The input worktree is expected to be generated separately from
the immutable baseline; this script never edits 03_raw or 04_recovered.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


LITERAL_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
PLACEHOLDER_RE = re.compile(r"%(?:\d+)?[sdifoc%]")
FORMAT_TOKEN_RE = re.compile(r"\\[nrt]|[\r\n\t]|\{[^{}]+\}|\$[A-Za-z_][A-Za-z0-9_]*")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def decode_literal(raw: str) -> str:
    try:
        return json.loads('"' + raw + '"')
    except json.JSONDecodeError:
        return raw.replace(r'\"', '"').replace(r"\n", "\n").replace(r"\t", "\t")


def encode_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)[1:-1]


def load_mapping(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "units" in raw:
        items = raw["units"]
    elif isinstance(raw, dict) and "entries" in raw:
        items = raw["entries"]
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError("mapping must be a list or an object with units/entries")
    return items


def validate_translation(source: str, translation: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(translation, str) or not translation:
        errors.append("translation must be a non-empty string")
        return errors
    if PLACEHOLDER_RE.findall(source) != PLACEHOLDER_RE.findall(translation):
        errors.append(f"placeholder mismatch: {PLACEHOLDER_RE.findall(source)} != {PLACEHOLDER_RE.findall(translation)}")
    if FORMAT_TOKEN_RE.findall(source) != FORMAT_TOKEN_RE.findall(translation):
        errors.append(f"format token mismatch: {FORMAT_TOKEN_RE.findall(source)} != {FORMAT_TOKEN_RE.findall(translation)}")
    return errors


def find_literal(text: str, line_number: int, column: int, source: str) -> tuple[int, int, str] | None:
    for match in LITERAL_RE.finditer(text):
        start = match.start(1)
        actual_line = text.count("\n", 0, start) + 1
        line_start = text.rfind("\n", 0, start) + 1
        actual_column = start - line_start + 1
        if actual_line == line_number and actual_column == column:
            value = decode_literal(match.group(1))
            if value == source:
                return start, match.end(1), match.group(1)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("06_worktree"))
    parser.add_argument("--units", type=Path, default=Path("05_schema/localization_units.json"))
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("10_logs/localization_apply_report.json"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    units_path = args.units.resolve()
    mapping_path = args.mapping.resolve()
    report_path = args.output.resolve()
    if not root.is_dir() or not units_path.exists() or not mapping_path.exists():
        print("missing root, units, or mapping", file=sys.stderr)
        return 2

    units_data = json.loads(units_path.read_text(encoding="utf-8"))
    unit_by_id = {unit["unit_id"]: unit for unit in units_data.get("entries", [])}
    items = load_mapping(mapping_path)
    errors: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    by_file: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        unit_id = item.get("unit_id")
        translation = item.get("translation") or item.get("zh")
        if not unit_id or unit_id in seen_ids:
            errors.append({"unit_id": unit_id, "reason": "missing_or_duplicate_unit_id"})
            continue
        seen_ids.add(unit_id)
        unit = unit_by_id.get(unit_id)
        if not unit:
            errors.append({"unit_id": unit_id, "reason": "unit_not_in_locked_extraction"})
            continue
        if unit.get("classification") != "DISPLAY_SAFE":
            errors.append({"unit_id": unit_id, "reason": "unit_is_not_DISPLAY_SAFE", "classification": unit.get("classification")})
            continue
        source_relative = unit["source"]
        target = root / Path(source_relative)
        if not target.exists():
            errors.append({"unit_id": unit_id, "reason": "target_missing", "target": source_relative})
            continue
        expected_file_sha = item.get("expected_file_sha256") or unit.get("source_file_sha256")
        if expected_file_sha and sha256_path(target) != expected_file_sha:
            errors.append({"unit_id": unit_id, "reason": "target_preimage_mismatch", "target": source_relative, "expected": expected_file_sha, "actual": sha256_path(target)})
            continue
        token_errors = validate_translation(unit["text"], translation)
        if token_errors:
            errors.append({"unit_id": unit_id, "reason": "translation_contract_failed", "details": token_errors})
            continue
        by_file.setdefault(source_relative, []).append({"unit": unit, "translation": translation})

    for source_relative, file_changes in by_file.items():
        target = root / Path(source_relative)
        original_bytes = target.read_bytes()
        original_text = original_bytes.decode("utf-8")
        working_text = original_text
        replacements: list[dict[str, Any]] = []
        for change in sorted(file_changes, key=lambda item: (item["unit"]["line"], item["unit"]["column"]), reverse=True):
            unit = change["unit"]
            found = find_literal(working_text, unit["line"], unit["column"], unit["text"])
            if not found:
                errors.append({"unit_id": unit["unit_id"], "reason": "exact_literal_not_found_after_prior_changes", "target": source_relative})
                continue
            start, end, raw = found
            replacement = encode_literal(change["translation"])
            working_text = working_text[:start] + replacement + working_text[end:]
            replacements.append({
                "unit_id": unit["unit_id"],
                "source": unit["text"],
                "translation": change["translation"],
                "line": unit["line"],
                "column": unit["column"],
                "source_sha256": hashlib.sha256(unit["text"].encode("utf-8")).hexdigest().upper(),
            })
        if replacements and not args.dry_run:
            target.write_text(working_text, encoding="utf-8", newline="")
        if replacements:
            changes.append({
                "file": source_relative,
                "preimage_sha256": hashlib.sha256(original_bytes).hexdigest().upper(),
                "postimage_sha256": hashlib.sha256(working_text.encode("utf-8")).hexdigest().upper(),
                "replacements": list(reversed(replacements)),
            })

    report = {
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "root": str(root),
        "units": str(units_path),
        "mapping": str(mapping_path),
        "dry_run": args.dry_run,
        "mapping_count": len(items),
        "changed_file_count": len(changes),
        "replacement_count": sum(len(item["replacements"]) for item in changes),
        "changes": changes,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
        "proves": "only exact DISPLAY_SAFE unit IDs with matching target literals and preserved placeholders/tokens were applied" if not errors else "the requested translation batch was rejected or partially rejected",
        "not_proven": "translation quality, runtime display, font coverage, gameplay, persistence, or release readiness",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
