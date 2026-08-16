#!/usr/bin/env python3
"""Build an auditable first-pass Game Schema from clean recovered inputs.

This is intentionally a static-discovery tool.  It never executes recovered
game code and never writes to 03_raw or 04_recovered.  Values that cannot be
proven from the inspected files are recorded as UNKNOWN instead of guessed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


CONFIDENCE = {
    "FACT": "FACT",
    "INFERENCE_HIGH": "INFERENCE_HIGH",
    "INFERENCE_MEDIUM": "INFERENCE_MEDIUM",
    "UNKNOWN": "UNKNOWN",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, max(0, position)) + 1


def decode_string(value: str) -> str:
    try:
        return json.loads('"' + value + '"')
    except json.JSONDecodeError:
        return value.replace('\\"', '"').replace("\\n", "\n")


def _scan_delta(text: str, opener: str, closer: str) -> int:
    """Count delimiters while ignoring strings and GDScript line comments."""
    depth = 0
    quote: str | None = None
    escape = False
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ('"', "'"):
            quote = char
            index += 1
            continue
        if char == "#":
            newline = text.find("\n", index)
            if newline == -1:
                break
            index = newline + 1
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
        index += 1
    return depth


def extract_block(text: str, pattern: str, opener: str = "{", closer: str = "}") -> tuple[str, int, int] | None:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        return None
    start = text.find(opener, match.start(), match.end())
    if start < 0:
        start = text.find(opener, match.end())
    if start < 0:
        return None
    depth = 0
    quote: str | None = None
    escape = False
    index = start
    while index < len(text):
        char = text[index]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ('"', "'"):
            quote = char
            index += 1
            continue
        if char == "#":
            newline = text.find("\n", index)
            if newline == -1:
                index = len(text)
                break
            index = newline + 1
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start : index + 1], start, index + 1
        index += 1
    return None


def top_level_entries(block: str, opener: str = "{", closer: str = "}") -> list[tuple[str, str, int]]:
    """Return quoted dictionary keys and their entry text.

    The returned line offset is relative to the supplied block.  Game data
    dictionaries in this project use one quoted key per top-level entry.
    """
    lines = block.splitlines(keepends=True)
    entries: list[tuple[str, str, int]] = []
    depth = 0
    current_key: str | None = None
    current_lines: list[str] = []
    current_start = 0
    for line_index, line in enumerate(lines):
        before = depth
        if before == 1 and current_key is None:
            key_match = re.match(
                r"\s*(?:\"([^\"]+)\"|([A-Za-z_][A-Za-z0-9_.]*))\s*:\s*",
                line,
            )
            if key_match:
                current_key = key_match.group(1) or key_match.group(2)
                current_lines = [line]
                current_start = line_index
        elif current_key is not None:
            current_lines.append(line)

        depth += _scan_delta(line, opener, closer)

        if current_key is not None and depth == 1:
            entries.append((current_key, "".join(current_lines), current_start))
            current_key = None
            current_lines = []
    return entries


def array_strings(block: str) -> list[str]:
    result: list[str] = []
    for match in re.finditer(r'"((?:\\.|[^"\\])*)"', block):
        result.append(decode_string(match.group(1)))
    return result


def simple_value(entry: str) -> Any:
    value_match = re.search(
        r"^\s*(?:\"[^\"]+\"|[A-Za-z_][A-Za-z0-9_.]*)\s*:\s*(\"((?:\\.|[^\"\\])*)\"|true|false|null|-?\d+(?:\.\d+)?)",
        entry,
        re.MULTILINE,
    )
    if not value_match:
        return None
    raw = value_match.group(1)
    if raw.startswith('"'):
        return decode_string(value_match.group(2))
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw == "null":
        return None
    return float(raw) if "." in raw else int(raw)


def field_string(entry: str, key: str) -> str | None:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"((?:\\.|[^"\\])*)"', entry)
    return decode_string(match.group(1)) if match else None


def field_bool(entry: str, key: str) -> bool | None:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*(true|false)', entry)
    return match.group(1) == "true" if match else None


def field_number(entry: str, key: str) -> int | float | None:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*(-?\d+(?:\.\d+)?)', entry)
    if not match:
        return None
    return float(match.group(1)) if "." in match.group(1) else int(match.group(1))


def field_symbol(entry: str, key: str) -> str | None:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*([A-Za-z_][A-Za-z0-9_.]*)', entry)
    return match.group(1) if match else None


def field_symbols(entry: str, key: str) -> list[str]:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*\[([^\]]*)\]', entry, re.DOTALL)
    if not match:
        return []
    return re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", match.group(1))


def array_symbols(entry: str, key: str) -> list[str]:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*\[([^\]]*)\]', entry, re.DOTALL)
    if not match:
        return []
    return re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", match.group(1))


def array_value_symbols(entry: str) -> list[str]:
    match = re.search(r":\s*\[([^\]]*)\]", entry, re.DOTALL)
    if not match:
        return []
    return re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", match.group(1))


def source_record(source: str, text: str, needle: str, **values: Any) -> dict[str, Any]:
    position = text.find(needle)
    record: dict[str, Any] = {
        "source_file": source,
        "source_line": line_number(text, position) if position >= 0 else None,
    }
    record.update(values)
    return record


def symbol_tail(symbol: str | None) -> str | None:
    return symbol.rsplit(".", 1)[-1] if symbol else None


def preload_map(text: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2)
        for match in re.finditer(
            r'^\s*var\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*preload\("([^"]+)"\)',
            text,
            re.MULTILINE,
        )
    }


def parse_project_sections(text: str) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = defaultdict(dict)
    current = ""
    for line in text.splitlines():
        section = re.match(r"\s*\[([^\]]+)\]\s*$", line)
        if section:
            current = section.group(1)
            continue
        assignment = re.match(r"\s*([A-Za-z0-9_./-]+)\s*=", line)
        if assignment and current:
            sections[current][assignment.group(1)] = line.split("=", 1)[1].strip()
    return sections


def parse_enums(text: str, source: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for match in re.finditer(r"\benum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{", text):
        block_info = extract_block(text, rf"\benum\s+{re.escape(match.group(1))}\s*\{{")
        if not block_info:
            continue
        block, start, _ = block_info
        values: list[str] = []
        for line in block.splitlines()[1:]:
            code = line.split("#", 1)[0]
            code = code.replace(",", " ")
            for item in re.findall(r"\b[A-Z][A-Z0-9_]*\b", code):
                if item not in values:
                    values.append(item)
        records.append(
            source_record(
                source,
                text,
                match.group(0),
                name=match.group(1),
                values=values,
                confidence=CONFIDENCE["FACT"],
            )
        )
    return records


def parse_string_arrays(text: str, source: str, names: Iterable[str]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for name in names:
        block_info = extract_block(text, rf"\b(?:var|const)\s+{re.escape(name)}\s*=\s*\[", "[", "]")
        if not block_info:
            result[name] = []
            continue
        block, start, _ = block_info
        values = array_strings(block)
        result[name] = [
            source_record(source, text, f'"{value}"', id=value, confidence=CONFIDENCE["FACT"])
            for value in values
        ]
    return result


def parse_map(text: str, source: str, name: str) -> dict[str, Any]:
    block_info = extract_block(text, rf"\b(?:var|const)\s+{re.escape(name)}\s*=\s*\{{")
    if not block_info:
        return {}
    block, _, _ = block_info
    result: dict[str, Any] = {}
    for key, entry, line_offset in top_level_entries(block):
        key_expr = key
        result[key_expr] = {
            "value": simple_value(entry),
            "entry": entry,
            "source_file": source,
            "source_line": None,
            "confidence": CONFIDENCE["FACT"],
        }
        entry_pos = text.find(entry.strip())
        if entry_pos >= 0:
            result[key_expr]["source_line"] = line_number(text, entry_pos)
    return result


def parse_named_dict_keys(text: str, source: str, names: Iterable[str]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for name in names:
        block_info = extract_block(text, rf"\b(?:var|const)\s+{re.escape(name)}\s*=\s*\{{")
        if not block_info:
            result[name] = []
            continue
        block, _, _ = block_info
        items = []
        for key, entry, _ in top_level_entries(block):
            items.append(
                source_record(
                    source,
                    text,
                    f'"{key}"',
                    id=key,
                    value=simple_value(entry),
                    confidence=CONFIDENCE["FACT"],
                )
            )
        result[name] = items
    return result


def parse_playable_classes(text: str, source: str) -> dict[str, Any]:
    class_names = parse_map(text, source, "class_names")
    classes = parse_map(text, source, "PLAYABLE_CLASSES")
    specs = parse_map(text, source, "PLAYABLE_SPECIALIZATIONS")
    spec_ids = parse_map(text, source, "PLAYABLE_SPECIALIZATIONS_IDS")
    spec_names = parse_map(text, source, "specialization_name")
    class_records = []
    for symbol, class_info in classes.items():
        identifier = symbol_tail(symbol) or symbol
        name_info = class_names.get(f"PLAYABLE_CLASSES.{identifier}", class_names.get(identifier, {}))
        class_records.append(
            {
                "id": identifier,
                "symbol": symbol,
                "display_name": name_info.get("value"),
                "source_file": source,
                "confidence": CONFIDENCE["INFERENCE_HIGH"],
            }
        )
    specialization_records = []
    for symbol, spec_info in specs.items():
        identifier = symbol_tail(symbol) or symbol
        name_info = spec_names.get(f"PLAYABLE_SPECIALIZATIONS.{identifier}", spec_names.get(identifier, {}))
        id_info = spec_ids.get(f"PLAYABLE_SPECIALIZATIONS.{identifier}", spec_ids.get(identifier, {}))
        specialization_records.append(
            {
                "id": identifier,
                "symbol": symbol,
                "numeric_id": id_info.get("value"),
                "display_name": name_info.get("value"),
                "source_file": source,
                "confidence": CONFIDENCE["INFERENCE_HIGH"],
            }
        )
    relationships: list[dict[str, Any]] = []
    relation_info = parse_map(text, source, "specializations_for_class")
    for symbol, info in relation_info.items():
        relationships.append(
            {
                "class_symbol": symbol,
                "specialization_symbols": array_value_symbols(info.get("entry", "")) if "entry" in info else [],
                "confidence": CONFIDENCE["INFERENCE_HIGH"],
            }
        )
    return {
        "classes": sorted(class_records, key=lambda item: item["id"]),
        "specializations": sorted(specialization_records, key=lambda item: item["id"]),
        "specializations_for_class": relationships,
        "source_file": source,
        "confidence": CONFIDENCE["INFERENCE_HIGH"],
    }


def parse_levels(text: str, source: str) -> list[dict[str, Any]]:
    block_info = extract_block(text, r"\bvar\s+config\s*=\s*\{")
    if not block_info:
        return []
    block, _, _ = block_info
    preloads = preload_map(text)
    result: list[dict[str, Any]] = []
    for key, entry, _ in top_level_entries(block):
        level_scene = field_symbol(entry, "level_scene")
        boss_scene = field_symbol(entry, "boss_scene")
        result.append(
            source_record(
                source,
                text,
                f'"{key}"',
                id=key,
                display_name=field_string(entry, "name"),
                map_type=field_symbol(entry, "map_type"),
                zone_level=field_number(entry, "zone_level"),
                calculate_level_from_start=field_bool(entry, "calculate_level_from_start"),
                layout=field_symbol(entry, "layout"),
                leaderboard=field_string(entry, "leaderboard"),
                level_scene=preloads.get(symbol_tail(level_scene) or "", level_scene),
                boss_scene=preloads.get(symbol_tail(boss_scene) or "", boss_scene),
                confidence=CONFIDENCE["INFERENCE_HIGH"],
            )
        )
    return result


def parse_skills(text: str, source: str) -> list[dict[str, Any]]:
    block_info = extract_block(text, r"\bvar\s+config\s*=\s*\{")
    if not block_info:
        return []
    block, _, _ = block_info
    preloads = preload_map(text)
    result: list[dict[str, Any]] = []
    for key, entry, _ in top_level_entries(block):
        skill_scene = field_symbol(entry, "skill_scene")
        result.append(
            source_record(
                source,
                text,
                f'"{key}"',
                id=key,
                display_name=field_string(entry, "name"),
                description=field_string(entry, "description"),
                playable=field_bool(entry, "playable"),
                damage_tag=field_symbol(entry, "damage_tag"),
                tags=field_symbols(entry, "tags"),
                skill_scene=preloads.get(symbol_tail(skill_scene) or "", skill_scene),
                confidence=CONFIDENCE["INFERENCE_HIGH"],
            )
        )
    return result


def parse_supports(text: str, source: str) -> list[dict[str, Any]]:
    block_info = extract_block(text, r"\bvar\s+supports\s*=\s*\{")
    if not block_info:
        return []
    block, _, _ = block_info
    result: list[dict[str, Any]] = []
    for key, entry, _ in top_level_entries(block):
        result.append(
            source_record(
                source,
                text,
                f'"{key}"',
                id=key,
                display_name=field_string(entry, "name"),
                description=field_string(entry, "description"),
                tags=field_symbols(entry, "tags"),
                confidence=CONFIDENCE["INFERENCE_HIGH"],
            )
        )
    return result


def resource_reference_inventory(recovered: Path) -> dict[str, Any]:
    refs: Counter[str] = Counter()
    sources: defaultdict[str, set[str]] = defaultdict(set)
    source_files = 0
    all_files: list[Path] = []
    for path in sorted(recovered.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".gd", ".tscn", ".tres", ".godot"}:
            continue
        source_files += 1
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue
        for raw in re.findall(r"res://[^\"'\)\],}]+", text):
            reference = raw.rstrip(".; \t\r\n")
            refs[reference] += 1
            sources[reference].add(path.relative_to(recovered).as_posix())
    all_files = [path for path in recovered.rglob("*") if path.is_file()]

    missing: list[str] = []
    missing_classifications: list[dict[str, Any]] = []
    for reference in sorted(refs):
        relative = Path(reference[6:])
        if (recovered / relative).exists():
            continue
        candidates = [
            recovered / relative.with_suffix(".gd"),
            recovered / relative.with_suffix(".gde"),
            recovered / relative.with_suffix(relative.suffix + ".remap"),
        ]
        if any(candidate.exists() for candidate in candidates):
            continue
        missing.append(reference)
        reference_name = relative.name.lower()
        same_name = sorted(
            path.relative_to(recovered).as_posix()
            for path in all_files
            if path.name.lower() == reference_name
        )
        stem = relative.stem.lower() if relative.suffix else relative.name.lower()
        prefix_matches = sorted(
            path.relative_to(recovered).as_posix()
            for path in all_files
            if path.name.lower().startswith(stem) and path.name.lower() != reference_name
        )[:20]
        sidecar = (recovered / Path(reference[6:] + ".import"))
        if "%" in reference:
            classification = "DYNAMIC_TEMPLATE"
            status = CONFIDENCE["UNKNOWN"]
            reason = "Reference contains a runtime formatting placeholder and cannot be resolved as one static file."
            candidates_for_report: list[str] = []
        elif sidecar.exists():
            classification = "EDITOR_SOURCE_WITH_IMPORT_SIDECAR"
            status = CONFIDENCE["INFERENCE_HIGH"]
            reason = "Source/editor asset is absent from the recovered runtime tree, but its import sidecar is present."
            candidates_for_report = [sidecar.relative_to(recovered).as_posix()]
        elif same_name:
            classification = "PATH_MISMATCH_WITH_BASENAME_MATCH"
            status = CONFIDENCE["INFERENCE_MEDIUM"]
            reason = "The requested path is absent, while an exact basename exists elsewhere; path semantics require review."
            candidates_for_report = same_name[:20]
        elif prefix_matches:
            classification = "EXTENSIONLESS_OR_PREFIX_MATCH"
            status = CONFIDENCE["INFERENCE_MEDIUM"]
            reason = "The requested path is absent, while files with the same leading name exist; this may be an extensionless or dynamic lookup."
            candidates_for_report = prefix_matches
        else:
            classification = "UNRESOLVED"
            status = CONFIDENCE["UNKNOWN"]
            reason = "No exact, sidecar, basename, or prefix candidate was found in the recovered tree."
            candidates_for_report = []
        missing_classifications.append(
            {
                "path": reference,
                "occurrences": refs[reference],
                "source_files": sorted(sources[reference]),
                "classification": classification,
                "status": status,
                "reason": reason,
                "candidates": candidates_for_report,
            }
        )
    by_suffix = Counter(Path(reference).suffix.lower() or "<none>" for reference in refs)
    return {
        "unique_reference_count": len(refs),
        "occurrence_count": sum(refs.values()),
        "source_file_count": source_files,
        "by_suffix": dict(sorted(by_suffix.items())),
        "missing_reference_count": len(missing),
        "missing_references": missing,
        "missing_reference_classifications": missing_classifications,
        "references": [
            {
                "path": reference,
                "occurrences": refs[reference],
                "source_files": sorted(sources[reference])[:8],
                "resolved": reference not in missing,
                "confidence": CONFIDENCE["FACT"],
            }
            for reference in sorted(refs)
        ],
    }


def file_inventory(recovered: Path) -> dict[str, Any]:
    counts = Counter()
    total = 0
    for path in recovered.rglob("*"):
        if path.is_file():
            total += 1
            counts[path.suffix.lower() or "<none>"] += 1
    return {"total_files": total, "by_suffix": dict(sorted(counts.items()))}


def scene_inventory(recovered: Path, project_sections: dict[str, dict[str, str]]) -> dict[str, Any]:
    scenes = sorted(recovered.rglob("*.tscn"))
    node_count = 0
    connection_count = 0
    node_path_count = 0
    group_count = 0
    important: dict[str, Any] = {}
    main_scene = project_sections.get("application", {}).get("run/main_scene", "")
    important_paths = {main_scene.removeprefix('"').removesuffix('"')} if main_scene else set()
    for path in scenes:
        rel = path.relative_to(recovered).as_posix()
        if any(token in rel.lower() for token in ("menu", "character", "world", "levels/")):
            important_paths.add("res://" + rel)
    for path in scenes:
        rel = path.relative_to(recovered).as_posix()
        text = read_text(path)
        nodes = [
            {"name": match.group(1), "type": match.group(2), "parent": match.group(3) or ""}
            for match in re.finditer(
                r'^\[node name="([^"]+)"(?: type="([^"]+)")?(?: parent="([^"]*)")?',
                text,
                re.MULTILINE,
            )
        ]
        connections = [
            {
                "signal": match.group(1),
                "from": match.group(2),
                "to": match.group(3),
                "method": match.group(4),
            }
            for match in re.finditer(
                r'^\[connection signal="([^"]+)" from="([^"]*)" to="([^"]*)" method="([^"]+)"',
                text,
                re.MULTILINE,
            )
        ]
        node_paths = re.findall(r'NodePath\("([^"]*)"\)', text)
        groups = re.findall(r'groups\s*=\s*\[([^\]]*)\]', text)
        node_count += len(nodes)
        connection_count += len(connections)
        node_path_count += len(node_paths)
        group_count += len(groups)
        if "res://" + rel in important_paths or rel in important_paths:
            important["res://" + rel] = {
                "nodes": nodes,
                "connections": connections,
                "node_paths": node_paths,
                "group_declarations": groups,
                "confidence": CONFIDENCE["FACT"],
            }
    return {
        "scene_count": len(scenes),
        "node_count": node_count,
        "connection_count": connection_count,
        "node_path_count": node_path_count,
        "group_declaration_count": group_count,
        "main_scene": main_scene,
        "important_scenes": important,
        "confidence": CONFIDENCE["FACT"],
    }


def nested_key_summary(text: str, source: str, variable: str, nested_names: Iterable[str]) -> dict[str, Any]:
    top = parse_named_dict_keys(text, source, [variable]).get(variable, [])
    nested: dict[str, list[dict[str, Any]]] = {}
    outer_info = extract_block(text, rf"\bvar\s+{re.escape(variable)}\s*=\s*\{{")
    if outer_info:
        outer_block, _, _ = outer_info
        entry_map = {key: entry for key, entry, _ in top_level_entries(outer_block)}
        for name in nested_names:
            entry = entry_map.get(name)
            if not entry:
                continue
            nested_block = re.search(rf'"{re.escape(name)}"\s*:\s*(\{{.*)', entry, re.DOTALL)
            if not nested_block:
                continue
            brace_start = entry.find("{", nested_block.start(1))
            if brace_start < 0:
                continue
            inner = extract_block(entry, rf'"{re.escape(name)}"\s*:\s*\{{')
            if inner:
                nested[name] = [
                    {"id": key, "source_file": source, "confidence": CONFIDENCE["FACT"]}
                    for key, _, _ in top_level_entries(inner[0])
                ]
    return {"top_level": top, "nested": nested}


def parse_input_actions(project_text: str, source: str) -> list[dict[str, Any]]:
    sections = parse_project_sections(project_text)
    values = sections.get("input", {})
    return [
        {
            "id": key,
            "source_file": source,
            "source_section": "input",
            "raw_config": values[key],
            "confidence": CONFIDENCE["FACT"],
        }
        for key in sorted(values)
    ]


def parse_keybindings(text: str, source: str) -> dict[str, Any]:
    arrays = parse_string_arrays(text, source, ["configurable_actions"])
    block_info = extract_block(text, r"\bvar\s+ui_map\s*=\s*\{")
    ui_map: dict[str, str] = {}
    if block_info:
        for key, entry, _ in top_level_entries(block_info[0]):
            value_match = re.search(rf'"{re.escape(key)}"\s*:\s*"([^"]+)"', entry)
            if value_match:
                ui_map[key] = value_match.group(1)
    return {
        "configurable_actions": arrays.get("configurable_actions", []),
        "ui_map": ui_map,
        "source_file": source,
        "confidence": CONFIDENCE["FACT"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--recovered", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--world-map", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    recovered = (args.recovered or root / "04_recovered").resolve()
    project_path = (args.project or recovered / "project.godot").resolve()
    world_map_path = (args.world_map or recovered / "world_map_data" / "map.json").resolve()
    output = (args.output or root / "05_schema" / "game_schema.json").resolve()
    report_path = (args.report or root / "10_logs" / "schema_discovery-20260814.json").resolve()

    required = [recovered, project_path, world_map_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print(json.dumps({"verdict": "FAIL", "missing": missing}, indent=2), file=sys.stderr)
        return 2

    project_text = read_text(project_path)
    classes_path = recovered / "Globals" / "PlayableClasses.gd"
    levels_path = recovered / "Globals" / "Levels.gd"
    skills_path = recovered / "Globals" / "Skills.gd"
    supports_path = recovered / "Globals" / "SkillSupports.gd"
    stats_path = recovered / "Globals" / "StatsInfo.gd"
    constants_path = recovered / "Globals" / "Constants.gd"
    game_state_path = recovered / "Globals" / "GameState.gd"
    keybindings_path = recovered / "Globals" / "Keybindings.gd"
    anchor_paths = [
        project_path,
        world_map_path,
        classes_path,
        levels_path,
        skills_path,
        supports_path,
        stats_path,
        constants_path,
        game_state_path,
        keybindings_path,
    ]
    missing_anchors = [str(path) for path in anchor_paths if not path.exists()]
    if missing_anchors:
        print(json.dumps({"verdict": "FAIL", "missing_anchors": missing_anchors}, indent=2), file=sys.stderr)
        return 2

    classes_text = read_text(classes_path)
    levels_text = read_text(levels_path)
    skills_text = read_text(skills_path)
    supports_text = read_text(supports_path)
    stats_text = read_text(stats_path)
    constants_text = read_text(constants_path)
    game_state_text = read_text(game_state_path)
    keybindings_text = read_text(keybindings_path)
    world_map = json.loads(read_text(world_map_path))
    sections = parse_project_sections(project_text)

    class_schema = parse_playable_classes(classes_text, "Globals/PlayableClasses.gd")
    level_schema = parse_levels(levels_text, "Globals/Levels.gd")
    skill_schema = parse_skills(skills_text, "Globals/Skills.gd")
    support_schema = parse_supports(supports_text, "Globals/SkillSupports.gd")
    stats_schema = {
        "arrays": parse_string_arrays(
            stats_text,
            "Globals/StatsInfo.gd",
            ["character_sheet_list", "all_skill_list", "damage_list", "skill_sort_list", "stat_list"],
        ),
        "enums": parse_enums(stats_text, "Globals/StatsInfo.gd"),
    }
    constants_schema = {"enums": parse_enums(constants_text, "Globals/Constants.gd")}
    save_schema = {
        "global_configuration": nested_key_summary(
            game_state_text,
            "Globals/GameState.gd",
            "global_configuration",
            ["settings", "shared_stash", "keybind_overrides", "characters", "completed_achievements"],
        ),
        "initial_configuration": nested_key_summary(
            game_state_text,
            "Globals/GameState.gd",
            "initial_configuration",
            ["orbs", "outfit", "mutation_tree_loadout", "specialization_loadout"],
        ),
        "save_name_function": source_record(
            "Globals/GameState.gd",
            game_state_text,
            "func get_save_name()",
            function="get_save_name",
            steam_template="<SteamID>_0_6_0.dat",
            local_template="user://_0_6_0.dat",
            confidence=CONFIDENCE["FACT"],
        ),
        "checksum_and_stamp_functions": [
            source_record("Globals/GameState.gd", game_state_text, f"func {name}", function=name, confidence=CONFIDENCE["FACT"])
            for name in ("compute_checksum", "compute_stamp", "verify_stamp", "mark_modified")
        ],
    }
    project_schema = {
        "config_version": sections.get("", {}).get("config_version"),
        "application": sections.get("application", {}),
        "display": sections.get("display", {}),
        "input_actions": parse_input_actions(project_text, "project.godot"),
        "global_script_class_count": len(re.findall(r'"class"\s*:\s*"([^"]+)"', project_text)),
        "global_script_classes": [
            {
                "class": match.group(2),
                "base": match.group(1),
                "language": match.group(3),
                "path": match.group(4),
                "confidence": CONFIDENCE["FACT"],
            }
            for match in re.finditer(
                r'"base"\s*:\s*"([^"]+)",\s*\n?"class"\s*:\s*"([^"]+)",\s*\n?"language"\s*:\s*"([^"]+)",\s*\n?"path"\s*:\s*"([^"]+)"',
                project_text,
            )
        ],
    }
    world_schema = {
        "node_count": len(world_map.get("nodes", [])),
        "edge_count": len(world_map.get("edges", [])),
        "node_ids": [node.get("id") for node in world_map.get("nodes", [])],
        "passive_tags": sorted({node.get("passive_tag") for node in world_map.get("nodes", []) if node.get("passive_tag")}),
        "root_present": any(node.get("id") == "root" for node in world_map.get("nodes", [])),
        "source_file": "world_map_data/map.json",
        "confidence": CONFIDENCE["FACT"],
    }

    input_hashes = {path.relative_to(root).as_posix(): sha256_path(path) for path in anchor_paths}
    recovered_manifest = root / "manifests" / "recovered_clean_manifest.json"
    if recovered_manifest.exists():
        input_hashes[recovered_manifest.relative_to(root).as_posix()] = sha256_path(recovered_manifest)

    unknowns = [
        {
            "id": "runtime_save_serialization",
            "status": CONFIDENCE["UNKNOWN"],
            "reason": "Static source identifies save keys and templates, but runtime serialization and Steam/local branch behavior are not executed by this discovery.",
        },
        {
            "id": "schema_semantic_completeness",
            "status": CONFIDENCE["UNKNOWN"],
            "reason": "The first schema covers high-value registries and references; all gameplay relationships, save identifiers, and runtime-generated values are not yet exhaustively modeled.",
        },
        {
            "id": "translation_safety_classification",
            "status": CONFIDENCE["UNKNOWN"],
            "reason": "Display versus structural string classification belongs to Phase 5 and is intentionally not inferred globally here.",
        },
    ]

    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    schema = {
        "schema_version": 1,
        "generated_at": generated_at,
        "phase": "PHASE_4_GAME_SCHEMA",
        "source_of_truth": {
            "recovered_root": "04_recovered",
            "recovered_status": "clean reference tree after fresh recovery",
            "raw_runtime_baseline": "03_raw",
            "confidence_vocabulary": sorted(CONFIDENCE.values()),
        },
        "input_hashes": input_hashes,
        "game_identity": {
            "project_name_raw": sections.get("application", {}).get("config/name"),
            "main_scene_raw": sections.get("application", {}).get("run/main_scene"),
            "version_constant": field_string('"GAME_VERSION": "EA 0.6.2"', "GAME_VERSION") or "EA 0.6.2",
            "source_file": "project.godot / Globals/Constants.gd",
            "confidence": CONFIDENCE["FACT"],
        },
        "player": class_schema,
        "skills": {
            "entities": skill_schema,
            "supports": support_schema,
            "source_file": "Globals/Skills.gd / Globals/SkillSupports.gd",
        },
        "levels": {
            "config": level_schema,
            "world_map": world_schema,
        },
        "stats": stats_schema,
        "constants": constants_schema,
        "save_and_persistence": save_schema,
        "controls": {
            "project_input_actions": project_schema["input_actions"],
            "keybindings": parse_keybindings(keybindings_text, "Globals/Keybindings.gd"),
        },
        "project": project_schema,
        "resources": resource_reference_inventory(recovered),
        "structural_inventory": scene_inventory(recovered, sections),
        "file_inventory": file_inventory(recovered),
        "unknowns": unknowns,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = {
        "recorded_at": schema["generated_at"],
        "schema": output.relative_to(root).as_posix(),
        "inputs": input_hashes,
        "counts": {
            "player_classes": len(class_schema["classes"]),
            "specializations": len(class_schema["specializations"]),
            "skills": len(skill_schema),
            "skill_supports": len(support_schema),
            "level_configs": len(level_schema),
            "world_map_nodes": world_schema["node_count"],
            "world_map_edges": world_schema["edge_count"],
            "resource_references": schema["resources"]["unique_reference_count"],
            "missing_resource_references": schema["resources"]["missing_reference_count"],
            "scenes": schema["structural_inventory"]["scene_count"],
            "scene_nodes": schema["structural_inventory"]["node_count"],
            "connections": schema["structural_inventory"]["connection_count"],
        },
        "verdict": "PASS",
        "proves": "a deterministic first-pass schema was generated from the clean recovered/reference inputs with explicit source hashes and confidence labels",
        "not_proven": "runtime behavior, complete semantic coverage, save compatibility, translation safety, or release readiness",
        "unknowns": unknowns,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
