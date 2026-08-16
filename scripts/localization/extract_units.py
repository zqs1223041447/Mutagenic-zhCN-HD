#!/usr/bin/env python3
"""Extract contextual localization units without modifying game inputs.

The extractor is deliberately conservative.  It records quoted literals with
their owning file, line, field and nearby structural context, then classifies
each candidate as DISPLAY_SAFE, STRUCTURAL, AMBIGUOUS, or DO_NOT_TRANSLATE.
Only DISPLAY_SAFE is eligible for a later translation manifest.  This script
does not apply translations and does not write to 04_recovered or 06_worktree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


TEXT_EXTENSIONS = {".gd", ".tscn", ".tres", ".res", ".json", ".cfg", ".ini", ".import"}
EXCLUDED_PARTS = {"addons"}
MIN_TEXT_LENGTH = 2
PLACEHOLDER_RE = re.compile(r"%(?:\d+)?[sdifoc%]")
FORMAT_TOKEN_RE = re.compile(r"\\[nrt]|[\r\n\t]|\{[^{}]+\}|\$[A-Za-z_][A-Za-z0-9_]*")
PATH_RE = re.compile(r"(?:res|user)://|^[A-Za-z]:[\\/]|\.(?:gd|gde|tscn|tres|png|wav|ogg|aseprite|json|cfg|ini|import)(?:$|[?])", re.I)
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_./:-]*$")
NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?%?$", re.I)

DISPLAY_FIELDS = {
    "text",
    "tooltip",
    "hint_tooltip",
    "dialog_text",
    "placeholder_text",
    "window_title",
    "title",
    "label",
    "description",
    "display_name",
    "name_for_display",
}
STRUCTURAL_FIELDS = {
    "path",
    "parent",
    "from",
    "to",
    "method",
    "signal",
    "groups",
    "bus",
    "script",
    "resource_name",
    "resource_local_to_scene",
    "id",
    "key",
    "type",
    "class",
    "language",
    "scene",
    "skill_scene",
    "skill_texture",
    "level_scene",
    "boss_scene",
    "leaderboard",
}
STRUCTURAL_CONTEXT_RE = re.compile(
    r"(?:NodePath|ExtResource|SubResource|connection|preload|load\(|get_node|change_scene|user://|res://|InputMap|signal\s|enum\s|class_name|\.has\(|\.get\(|\bkeys?\b)",
    re.I,
)
LOG_CONTEXT_RE = re.compile(r"\b(?:print|push_error|push_warning|printerr|assert)\s*\(", re.I)
CODE_ASSIGNMENT_RE = re.compile(r"(?:^|[.\s])(?:text|tooltip|hint_tooltip|dialog_text|placeholder_text)\s*=", re.I)
LITERAL_RE = re.compile(r'"((?:\\.|[^"\\])*)"')


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


def encode_literal(raw: str) -> str:
    return raw.replace('\\"', '"')


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, max(0, position)) + 1


def previous_nonempty(lines: list[str], index: int) -> str:
    for pos in range(index - 1, -1, -1):
        if lines[pos].strip():
            return lines[pos].strip()
    return ""


def current_node_context(lines: list[str], index: int) -> dict[str, str | None]:
    node_name: str | None = None
    node_type: str | None = None
    node_parent: str | None = None
    for pos in range(index, -1, -1):
        match = re.match(
            r'^\[node name="([^"]+)"(?: type="([^"]+)")?(?: parent="([^"]*)")?',
            lines[pos].strip(),
        )
        if match:
            node_name, node_type, node_parent = match.group(1), match.group(2), match.group(3)
            break
    return {"node_name": node_name, "node_type": node_type, "node_parent": node_parent}


def field_from_line(line: str, extension: str) -> tuple[str | None, str | None]:
    if extension == ".tscn" or extension in {".tres", ".res", ".import"}:
        assignment = re.match(r"\s*([A-Za-z0-9_./-]+)\s*=\s*", line)
        if assignment:
            return assignment.group(1), "resource_property"
    if extension == ".gd":
        assignment = re.search(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*", line)
        if assignment:
            return assignment.group(1), "code_assignment"
        dictionary = re.search(r'"([^"\\]+)"\s*:\s*', line)
        if dictionary:
            return dictionary.group(1), "dictionary_value"
        if LOG_CONTEXT_RE.search(line):
            return "log_message", "log"
        return None, "code_literal"
    if extension == ".json":
        dictionary = re.search(r'"([^"\\]+)"\s*:\s*', line)
        return (dictionary.group(1), "json_value") if dictionary else (None, "json_literal")
    return None, "literal"


def literal_role(line: str, start: int, end: int) -> str:
    """Identify dictionary keys versus values for the current literal."""
    after = line[end:]
    before = line[:start]
    if re.match(r"\s*:", after):
        return "dictionary_key"
    if re.search(r"(?:^|[:=\[,({])\s*$", before):
        return "value"
    return "literal"


def classify(
    value: str,
    field: str | None,
    context_kind: str,
    line: str,
    file_path: str,
    node: dict[str, str | None],
    role: str,
) -> tuple[str, str, list[str]]:
    reasons: list[str] = []
    if "__Old" in file_path or "/legacy/" in file_path.lower():
        return "DO_NOT_TRANSLATE", "legacy_or_reference_only_source", ["legacy_or_reference_only_source"]
    if role == "dictionary_key":
        return "STRUCTURAL", "dictionary_key", ["dictionary_key"]
    if line.lstrip().startswith(("[node ", "[ext_resource", "[sub_resource", "[connection")):
        return "STRUCTURAL", "scene_structural_declaration", ["scene_structural_declaration"]
    if not value.strip() or len(value.strip()) < MIN_TEXT_LENGTH:
        return "DO_NOT_TRANSLATE", "empty_or_too_short", ["empty_or_too_short"]
    if NUMERIC_RE.fullmatch(value.strip()):
        return "DO_NOT_TRANSLATE", "numeric_or_percent_literal", ["numeric_or_percent_literal"]
    if PATH_RE.search(value) or value.startswith("http://") or value.startswith("https://"):
        return "STRUCTURAL", "path_or_url", ["path_or_url"]
    if PLACEHOLDER_RE.search(value) or FORMAT_TOKEN_RE.search(value):
        reasons.append("contains_placeholder_or_format_token")
    if field and field.lower() in STRUCTURAL_FIELDS:
        return "STRUCTURAL", "structural_field", reasons + ["structural_field"]
    if field and ("/" in field or field.lower().endswith("_id") or field.lower().endswith("_key")):
        return "STRUCTURAL", "structured_key_or_path_field", reasons + ["structured_key_or_path_field"]
    if field and field.lower() in DISPLAY_FIELDS:
        if reasons:
            return "DISPLAY_SAFE", "display_field_with_tokens", reasons + ["display_field_with_tokens"]
        return "DISPLAY_SAFE", "declared_display_field", ["declared_display_field"]
    if STRUCTURAL_CONTEXT_RE.search(line) or STRUCTURAL_CONTEXT_RE.search(file_path):
        return "STRUCTURAL", "structural_context", reasons + ["structural_context"]
    if LOG_CONTEXT_RE.search(line) or context_kind == "log":
        return "DO_NOT_TRANSLATE", "developer_log_or_diagnostic", reasons + ["developer_log_or_diagnostic"]
    if node.get("node_type") in {"Label", "Button", "LinkButton", "WindowDialog", "AcceptDialog", "ConfirmationDialog", "LineEdit"}:
        return "DISPLAY_SAFE", "visible_control_literal", reasons + ["visible_control_literal"]
    if context_kind == "dictionary_value" and (field or "").lower() in DISPLAY_FIELDS:
        return "DISPLAY_SAFE", "semantic_dictionary_display_field", reasons + ["semantic_dictionary_display_field"]
    if IDENTIFIER_RE.fullmatch(value.strip()) and ("_" in value or value.isupper() or value[:1].islower()):
        return "AMBIGUOUS", "identifier_like_literal", reasons + ["identifier_like_literal"]
    return "AMBIGUOUS", "insufficient_context", reasons + ["insufficient_context"]


def semantic_tags(file_path: str, field: str | None, node: dict[str, str | None]) -> list[str]:
    lower = file_path.lower()
    tags: set[str] = set()
    if "/scenes/" in f"/{lower}" or lower.startswith("scenes/"):
        tags.add("scene")
    if "/popups/" in f"/{lower}" or "/dialogs/" in f"/{lower}":
        tags.add("ui_dialog")
    if "characterselect" in lower or "character_select" in lower:
        tags.add("character_selection")
    if "/skills/" in f"/{lower}" or lower.endswith("/skills.gd"):
        tags.add("skill")
    if "keystone" in lower or "passivetree" in lower:
        tags.add("passive_tree")
    if "/genes/" in f"/{lower}" or lower.endswith("/genes.gd") or "equipment" in lower:
        tags.add("equipment_gene")
    if "monster" in lower or "/mobs/" in f"/{lower}":
        tags.add("enemy")
    if "level" in lower or "worldmap" in lower or "map" in lower:
        tags.add("map_level")
    if "gamestate" in lower or "save" in lower:
        tags.add("save_persistence")
    if "constants" in lower or "statsinfo" in lower:
        tags.add("game_schema")
    if field and field.lower() in {"text", "title", "label", "tooltip", "hint_tooltip", "dialog_text", "placeholder_text"}:
        tags.add("ui_text")
    if field and field.lower() in {"name", "display_name"}:
        tags.add("display_name")
    if field and field.lower() == "description":
        tags.add("description")
    if node.get("node_type") in {"Label", "Button", "LinkButton", "WindowDialog", "AcceptDialog", "ConfirmationDialog", "LineEdit"}:
        tags.add("visible_control")
    return sorted(tags)


def extract_file(root: Path, path: Path) -> list[dict[str, Any]]:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError):
        return []
    if not text:
        return []
    relative = path.relative_to(root).as_posix()
    extension = path.suffix.lower()
    lines = text.splitlines()
    entries: list[dict[str, Any]] = []
    for match in LITERAL_RE.finditer(text):
        line_index = text.count("\n", 0, match.start())
        line_start = text.rfind("\n", 0, match.start(1)) + 1
        line = lines[line_index] if line_index < len(lines) else ""
        field, context_kind = field_from_line(line, extension)
        node = current_node_context(lines, line_index) if extension == ".tscn" else {"node_name": None, "node_type": None, "node_parent": None}
        raw_value = match.group(1)
        value = decode_literal(raw_value)
        start = match.start(1) - line_start
        end = match.end(1) - line_start
        role = literal_role(line, start, end)
        classification, reason, reason_codes = classify(value, field, context_kind or "literal", line, relative, node, role)
        placeholder_tokens = PLACEHOLDER_RE.findall(value)
        format_tokens = FORMAT_TOKEN_RE.findall(value)
        entries.append(
            {
                "unit_id": f"{relative}:{line_index + 1}:{start + 1}",
                "source": relative,
                "line": line_index + 1,
                "column": start + 1,
                "field": field,
                "context_kind": context_kind,
                "literal_role": role,
                "node": node,
                "semantic_tags": semantic_tags(relative, field, node),
                "text": value,
                "raw_literal": raw_value,
                "occurrence_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest().upper(),
                "placeholders": placeholder_tokens,
                "format_tokens": format_tokens,
                "classification": classification,
                "classification_reason": reason,
                "reason_codes": reason_codes,
                "surrounding_line": line.strip(),
                "previous_nonempty_line": previous_nonempty(lines, line_index),
                "confidence": "FACT" if classification in {"STRUCTURAL", "DO_NOT_TRANSLATE"} else "INFERENCE_HIGH" if classification == "DISPLAY_SAFE" else "INFERENCE_MEDIUM",
            }
        )
    return entries


def source_hashes(root: Path, files: Iterable[Path]) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): sha256_path(path) for path in files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--recovered", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    recovered = (args.recovered or root / "04_recovered").resolve()
    output = (args.output or root / "05_schema" / "localization_units.json").resolve()
    report_path = (args.report or root / "10_logs" / "localization_extraction-20260814.json").resolve()
    if not recovered.is_dir():
        print(json.dumps({"verdict": "FAIL", "reason": "missing_recovered_root"}), file=sys.stderr)
        return 2

    files = [
        path
        for path in sorted(recovered.rglob("*"))
        if path.is_file()
        and path.suffix.lower() in TEXT_EXTENSIONS
        and not EXCLUDED_PARTS.intersection(path.relative_to(recovered).parts)
    ]
    all_entries: list[dict[str, Any]] = []
    for path in files:
        all_entries.extend(extract_file(recovered, path))

    file_hashes = {path.relative_to(recovered).as_posix(): sha256_path(path) for path in files}
    for entry in all_entries:
        entry["source_file_sha256"] = file_hashes[entry["source"]]
    display_entries = [entry for entry in all_entries if entry["classification"] == "DISPLAY_SAFE"]
    classifications = Counter(entry["classification"] for entry in all_entries)
    contexts = Counter(entry["context_kind"] for entry in all_entries)
    unique_display: dict[tuple[str, str], dict[str, Any]] = {}
    all_text_counts = Counter(entry["text"] for entry in all_entries)
    display_text_counts = Counter(entry["text"] for entry in display_entries)
    source_text_counts = Counter((entry["source"], entry["text"]) for entry in display_entries)
    for entry in display_entries:
        key = (entry["source"], entry["text"])
        unique_display.setdefault(key, entry)

    result = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_root": "04_recovered",
        "source_file_count": len(files),
        "source_hashes": file_hashes,
        "classification_vocabulary": ["DISPLAY_SAFE", "STRUCTURAL", "AMBIGUOUS", "DO_NOT_TRANSLATE"],
        "placeholder_regex": PLACEHOLDER_RE.pattern,
        "format_token_regex": FORMAT_TOKEN_RE.pattern,
        "entries": all_entries,
        "display_safe_units": [
            {
                "unit_id": entry["unit_id"],
                "source": entry["source"],
                "line": entry["line"],
                "field": entry["field"],
                "node": entry["node"],
                "semantic_tags": entry["semantic_tags"],
                "text": entry["text"],
                "occurrences_in_file": source_text_counts[(entry["source"], entry["text"])],
                "occurrences_display_total": display_text_counts[entry["text"]],
                "occurrences_all_total": all_text_counts[entry["text"]],
                "placeholders": entry["placeholders"],
                "format_tokens": entry["format_tokens"],
                "classification": entry["classification"],
                "confidence": entry["confidence"],
            }
            for entry in sorted(unique_display.values(), key=lambda item: (item["source"], item["line"], item["column"]))
        ],
        "counts": {
            "total_quoted_literals": len(all_entries),
            "unique_texts": len({entry["text"] for entry in all_entries}),
            "display_safe_occurrences": len(display_entries),
            "display_safe_unique_source_text_pairs": len(unique_display),
            "classifications": dict(sorted(classifications.items())),
            "context_kinds": dict(sorted(contexts.items())),
            "placeholder_occurrences": sum(bool(entry["placeholders"]) for entry in all_entries),
            "format_token_occurrences": sum(bool(entry["format_tokens"]) for entry in all_entries),
        },
        "proves": "contextual localization candidates were extracted from the clean recovered tree without modifying it, with classification, source location, placeholders, format tokens, and input hashes",
        "not_proven": "translation quality, glyph coverage, runtime display, semantic completeness, or that every AMBIGUOUS candidate is safe to translate",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = {
        "generated_at": result["generated_at"],
        "units": output.relative_to(root).as_posix(),
        "source_file_count": len(files),
        "counts": result["counts"],
        "verdict": "PASS",
        "proves": result["proves"],
        "not_proven": result["not_proven"],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
