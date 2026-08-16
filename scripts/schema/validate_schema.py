#!/usr/bin/env python3
"""Independently validate the first-pass Game Schema against its inputs."""

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


ALLOWED_CONFIDENCE = {
    "FACT",
    "INFERENCE_HIGH",
    "INFERENCE_MEDIUM",
    "INFERENCE_LOW",
    "UNKNOWN",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def balanced_block(text: str, start: int, opener: str = "{", closer: str = "}") -> str | None:
    brace = text.find(opener, start)
    if brace < 0:
        return None
    depth = 0
    quote: str | None = None
    escape = False
    index = brace
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
            if newline < 0:
                break
            index = newline + 1
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[brace : index + 1]
        index += 1
    return None


def variable_block(text: str, name: str, opener: str = "{", closer: str = "}") -> str | None:
    match = re.search(rf"\b(?:var|const)\s+{re.escape(name)}\s*=", text)
    return balanced_block(text, match.start() if match else -1, opener, closer) if match else None


def top_level_keys(block: str) -> list[str]:
    lines = block.splitlines()
    keys: list[str] = []
    depth = 0
    for line in lines:
        if depth == 1:
            match = re.match(r'\s*(?:"([^"]+)"|([A-Za-z_][A-Za-z0-9_.]*))\s*:\s*', line)
            if match:
                keys.append(match.group(1) or match.group(2))
        depth += delimiter_delta(line, "{", "}")
    return keys


def delimiter_delta(text: str, opener: str, closer: str) -> int:
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
        elif char == "#":
            break
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
        index += 1
    return depth


def array_values(text: str, name: str) -> list[str]:
    match = re.search(rf"\b(?:var|const)\s+{re.escape(name)}\s*=", text)
    if not match:
        return []
    block = balanced_block(text, match.start(), "[", "]")
    return re.findall(r'"((?:\\.|[^"\\])*)"', block or "")


def input_action_ids(project_text: str) -> list[str]:
    section = re.search(r"(?ms)^\[input\]\s*\n(?P<body>.*?)(?=^\[[^\]]+\]\s*$|\Z)", project_text)
    if not section:
        return []
    return sorted(re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=", section.group("body")))


def check(name: str, condition: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    schema_path = (args.schema or root / "05_schema" / "game_schema.json").resolve()
    output_path = (args.output or root / "10_logs" / "schema_validation-20260814.json").resolve()
    if not schema_path.exists():
        print(f"missing schema: {schema_path}", file=sys.stderr)
        return 2
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    hashes = schema.get("input_hashes", {})
    hash_failures: list[str] = []
    for relative, expected in hashes.items():
        path = root / Path(relative)
        if not path.exists() or sha256_path(path) != expected:
            hash_failures.append(relative)
    checks.append(check("input_hashes", not hash_failures, f"checked {len(hashes)} recorded inputs; mismatches={hash_failures}"))

    recovered = root / "04_recovered"
    project = recovered / "project.godot"
    classes_text = (recovered / "Globals" / "PlayableClasses.gd").read_text(encoding="utf-8")
    skills_text = (recovered / "Globals" / "Skills.gd").read_text(encoding="utf-8")
    supports_text = (recovered / "Globals" / "SkillSupports.gd").read_text(encoding="utf-8")
    levels_text = (recovered / "Globals" / "Levels.gd").read_text(encoding="utf-8")
    stats_text = (recovered / "Globals" / "StatsInfo.gd").read_text(encoding="utf-8")
    project_text = project.read_text(encoding="utf-8")

    expected_classes = {"ROGUE", "WARRIOR", "MAGE", "TANK"}
    expected_specs = {"WARLOCK", "MERCENARY", "VAMPIRE", "MARKSMAN", "SHAMAN", "FIEND", "TITAN", "BATTLEMAGE"}
    source_classes = set(top_level_keys(variable_block(classes_text, "PLAYABLE_CLASSES") or ""))
    source_specs = set(top_level_keys(variable_block(classes_text, "PLAYABLE_SPECIALIZATIONS") or ""))
    schema_classes = {item.get("id") for item in schema.get("player", {}).get("classes", [])}
    schema_specs = {item.get("id") for item in schema.get("player", {}).get("specializations", [])}
    checks.append(check("player_classes", source_classes == expected_classes == schema_classes, f"source={sorted(source_classes)} schema={sorted(schema_classes)}"))
    checks.append(check("specializations", source_specs == expected_specs == schema_specs, f"source_count={len(source_specs)} schema_count={len(schema_specs)}"))

    spec_ids = [item.get("numeric_id") for item in schema.get("player", {}).get("specializations", [])]
    checks.append(check("specialization_numeric_ids", sorted(spec_ids) == list(range(1, 9)), f"ids={sorted(spec_ids)}"))
    relationships = schema.get("player", {}).get("specializations_for_class", [])
    checks.append(check("class_specialization_relationships", len(relationships) == 4 and all(len(item.get("specialization_symbols", [])) == 2 for item in relationships), f"relations={len(relationships)}; each_pair={[len(item.get('specialization_symbols', [])) for item in relationships]}"))

    source_skill_ids = set(top_level_keys(variable_block(skills_text, "config") or ""))
    source_support_ids = set(top_level_keys(variable_block(supports_text, "supports") or ""))
    source_level_ids = set(top_level_keys(variable_block(levels_text, "config") or ""))
    schema_skill_ids = {item.get("id") for item in schema.get("skills", {}).get("entities", [])}
    schema_support_ids = {item.get("id") for item in schema.get("skills", {}).get("supports", [])}
    schema_level_ids = {item.get("id") for item in schema.get("levels", {}).get("config", [])}
    checks.append(check("skill_registry", source_skill_ids == schema_skill_ids and len(source_skill_ids) == 53, f"source={len(source_skill_ids)} schema={len(schema_skill_ids)}"))
    checks.append(check("support_registry", source_support_ids == schema_support_ids and len(source_support_ids) == 60, f"source={len(source_support_ids)} schema={len(schema_support_ids)}"))
    checks.append(check("level_registry", source_level_ids == schema_level_ids and len(source_level_ids) == 20, f"source={len(source_level_ids)} schema={len(schema_level_ids)}"))

    array_names = ["character_sheet_list", "all_skill_list", "damage_list", "skill_sort_list", "stat_list"]
    array_checks = {}
    for name in array_names:
        source_values = array_values(stats_text, name)
        schema_values = [item.get("id") for item in schema.get("stats", {}).get("arrays", {}).get(name, [])]
        array_checks[name] = len(source_values) == len(schema_values) and source_values == schema_values and len(set(schema_values)) == len(schema_values)
    checks.append(check("stat_arrays", all(array_checks.values()), f"arrays={array_checks}"))

    world_map = json.loads((recovered / "world_map_data" / "map.json").read_text(encoding="utf-8"))
    world = schema.get("levels", {}).get("world_map", {})
    checks.append(check("world_map", len(world_map.get("nodes", [])) == world.get("node_count") and len(world_map.get("edges", [])) == world.get("edge_count") and world.get("root_present") is True, f"nodes={world.get('node_count')} edges={world.get('edge_count')} root={world.get('root_present')}"))

    scene_count = sum(1 for path in recovered.rglob("*.tscn") if path.is_file())
    file_count = sum(1 for path in recovered.rglob("*") if path.is_file())
    structural = schema.get("structural_inventory", {})
    checks.append(check("recovered_inventory", file_count == schema.get("file_inventory", {}).get("total_files") and scene_count == structural.get("scene_count") and file_count == 5058 and scene_count == 356, f"files={file_count}/{schema.get('file_inventory', {}).get('total_files')} scenes={scene_count}/{structural.get('scene_count')}"))

    source_inputs = input_action_ids(project_text)
    schema_inputs = sorted(item.get("id") for item in schema.get("controls", {}).get("project_input_actions", []))
    checks.append(check("project_input_actions", source_inputs == schema_inputs and len(source_inputs) == 27, f"source={len(source_inputs)} schema={len(schema_inputs)}"))

    missing = schema.get("resources", {}).get("missing_references", [])
    classified = schema.get("resources", {}).get("missing_reference_classifications", [])
    classification_counts = Counter(item.get("classification") for item in classified)
    checks.append(check("reference_classifications", len(missing) == len(classified) == schema.get("resources", {}).get("missing_reference_count") and set(missing) == {item.get("path") for item in classified}, f"missing={len(missing)} classifications={dict(classification_counts)}"))
    checks.append(check("reference_classification_safety", classification_counts.get("UNRESOLVED", 0) == 0 and classification_counts.get("DYNAMIC_TEMPLATE", 0) == 1, f"counts={dict(classification_counts)}"))

    entity_records = []
    entity_records.extend(schema.get("player", {}).get("classes", []))
    entity_records.extend(schema.get("player", {}).get("specializations", []))
    entity_records.extend(schema.get("skills", {}).get("entities", []))
    entity_records.extend(schema.get("skills", {}).get("supports", []))
    entity_records.extend(schema.get("levels", {}).get("config", []))
    invalid_confidence = [record for record in entity_records if record.get("confidence") not in ALLOWED_CONFIDENCE]
    checks.append(check("confidence_labels", not invalid_confidence and len(entity_records) == len({(record.get("source_file"), record.get("id")) for record in entity_records}), f"records={len(entity_records)} invalid={len(invalid_confidence)}"))

    unknown_ids = {item.get("id") for item in schema.get("unknowns", [])}
    required_unknowns = {"runtime_save_serialization", "schema_semantic_completeness", "translation_safety_classification"}
    checks.append(check("unknowns_explicit", required_unknowns.issubset(unknown_ids), f"unknowns={sorted(unknown_ids)}"))

    failures = [item for item in checks if item["status"] != "PASS"]
    report = {
        "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "schema": schema_path.relative_to(root).as_posix(),
        "checks": checks,
        "verdict": "PASS" if not failures else "FAIL",
        "proves": "the generated schema matches the current hashed recovered/reference inputs and satisfies registry, inventory, classification, and confidence invariants" if not failures else "one or more schema invariants failed",
        "not_proven": "runtime behavior, exhaustive semantics, save compatibility, translation safety, or release readiness",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
