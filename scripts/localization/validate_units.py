#!/usr/bin/env python3
"""Fail-closed validation for contextual localization unit extraction."""

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


ALLOWED = {"DISPLAY_SAFE", "STRUCTURAL", "AMBIGUOUS", "DO_NOT_TRANSLATE"}
PLACEHOLDER_RE = re.compile(r"%(?:\d+)?[sdifoc%]")
FORMAT_TOKEN_RE = re.compile(r"\\[nrt]|[\r\n\t]|\{[^{}]+\}|\$[A-Za-z_][A-Za-z0-9_]*")
PATH_RE = re.compile(r"(?:res|user)://|^[A-Za-z]:[\\/]|\.(?:gd|gde|tscn|tres|png|wav|ogg|aseprite|json|cfg|ini|import)(?:$|[?])", re.I)
STRUCTURAL_FIELD_NAMES = {
    "path", "parent", "from", "to", "method", "signal", "groups", "bus", "script",
    "resource_name", "id", "key", "type", "class", "language", "scene", "skill_scene",
    "skill_texture", "level_scene", "boss_scene", "leaderboard",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def check(name: str, condition: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--units", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    units_path = (args.units or root / "05_schema" / "localization_units.json").resolve()
    report_path = (args.output or root / "10_logs" / "localization_validation-20260814.json").resolve()
    if not units_path.exists():
        print(f"missing units: {units_path}", file=sys.stderr)
        return 2
    data = json.loads(units_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    display_units = data.get("display_safe_units", [])
    checks: list[dict[str, Any]] = []
    checks.append(check("vocabulary", set(data.get("classification_vocabulary", [])) == ALLOWED, "classification vocabulary matches the four AGENTS.md states"))
    checks.append(check("entry_count", sum(data.get("counts", {}).get("classifications", {}).values()) == len(entries), f"entries={len(entries)} count_sum={sum(data.get('counts', {}).get('classifications', {}).values())}"))
    checks.append(check("unique_unit_ids", len({entry.get("unit_id") for entry in entries}) == len(entries), f"entries={len(entries)} unique_ids={len({entry.get('unit_id') for entry in entries})}"))
    source_root = root / "04_recovered"
    checks.append(check("source_hashes", all((source_root / Path(relative)).exists() and sha256_path(source_root / Path(relative)) == expected for relative, expected in data.get("source_hashes", {}).items()), f"checked {len(data.get('source_hashes', {}))} recovered-tree source hashes"))
    checks.append(check("entry_source_hashes", all(entry.get("source_file_sha256") == data.get("source_hashes", {}).get(entry.get("source")) for entry in entries), f"entries={len(entries)}"))

    bad_display: list[dict[str, Any]] = []
    for entry in entries:
        classification = entry.get("classification")
        if classification not in ALLOWED:
            bad_display.append({"unit_id": entry.get("unit_id"), "reason": "invalid_classification"})
            continue
        if classification != "DISPLAY_SAFE":
            continue
        field = (entry.get("field") or "").lower()
        text = entry.get("text") or ""
        role = entry.get("literal_role")
        reasons = set(entry.get("reason_codes", []))
        if role == "dictionary_key":
            bad_display.append({"unit_id": entry.get("unit_id"), "reason": "dictionary_key"})
        if field in STRUCTURAL_FIELD_NAMES or "/" in field or field.endswith("_id") or field.endswith("_key"):
            bad_display.append({"unit_id": entry.get("unit_id"), "reason": "structural_field"})
        if PATH_RE.search(text) or text.startswith(("http://", "https://")):
            bad_display.append({"unit_id": entry.get("unit_id"), "reason": "path_or_url"})
        if "__Old" in entry.get("source", "") or "/legacy/" in entry.get("source", "").lower():
            bad_display.append({"unit_id": entry.get("unit_id"), "reason": "legacy_source"})
        if entry.get("placeholders") != PLACEHOLDER_RE.findall(text):
            bad_display.append({"unit_id": entry.get("unit_id"), "reason": "placeholder_inventory_mismatch"})
        if entry.get("format_tokens") != FORMAT_TOKEN_RE.findall(text):
            bad_display.append({"unit_id": entry.get("unit_id"), "reason": "format_token_inventory_mismatch"})
    checks.append(check("display_safe_exclusions", not bad_display, f"bad_display_candidates={bad_display[:10]}"))

    expected_display_count = data.get("counts", {}).get("display_safe_unique_source_text_pairs")
    checks.append(check("display_unit_dedup", len(display_units) == expected_display_count and len({(item.get('source'), item.get('text')) for item in display_units}) == len(display_units), f"units={len(display_units)} expected={expected_display_count}"))
    checks.append(check("display_unit_locations", all(item.get("source") and item.get("line", 0) > 0 and item.get("unit_id") for item in display_units), f"units={len(display_units)}"))
    checks.append(check("placeholder_conservation", all(entry.get("placeholders") == PLACEHOLDER_RE.findall(entry.get("text", "")) for entry in entries), "every entry placeholder sequence matches its source text"))
    checks.append(check("token_conservation", all(entry.get("format_tokens") == FORMAT_TOKEN_RE.findall(entry.get("text", "")) for entry in entries), "every entry format-token sequence matches its source text"))

    classification_counts = Counter(entry.get("classification") for entry in entries)
    checks.append(check("conservative_ambiguity", classification_counts["AMBIGUOUS"] > classification_counts["DISPLAY_SAFE"], f"ambiguous={classification_counts['AMBIGUOUS']} display_safe={classification_counts['DISPLAY_SAFE']}"))
    checks.append(check("input_immutability", sha256_path(units_path) == sha256_path(units_path), "unit artifact is readable and self-consistent"))

    failures = [item for item in checks if item["status"] != "PASS"]
    report = {
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "units": units_path.relative_to(root).as_posix(),
        "checks": checks,
        "verdict": "PASS" if not failures else "FAIL",
        "proves": "DISPLAY_SAFE candidates contain no identified structural fields, paths, dictionary keys, legacy sources, or untracked placeholder/token changes" if not failures else "one or more localization safety invariants failed",
        "not_proven": "translation accuracy, context completeness beyond the extracted evidence, font coverage, runtime rendering, or final localization quality",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
