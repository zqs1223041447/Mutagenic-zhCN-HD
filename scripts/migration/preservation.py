#!/usr/bin/env python3
"""P1-X3: preservation contracts scanned from recovered sources.

Counts come from files under the recovered tree. AGENT.MD approximate numbers
are not a source of truth and are never copied into the contract.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FAMILIES = (
    "classes",
    "specializations",
    "skills",
    "supports",
    "passives",
    "keystones",
    "stats",
    "tags",
    "equipment_slots",
    "equipment_data",
    "input_actions",
    "save_keys",
    "combat_critical_ids",
)


def delimiter_delta(text: str, opener: str, closer: str) -> int:
    depth = 0
    quote: str | None = None
    escape = False
    for char in text:
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in ('"', "'"):
            quote = char
        elif char == "#":
            break
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
    return depth


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
    if not match:
        return None
    return balanced_block(text, match.start(), opener, closer)


def top_level_keys(block: str) -> list[str]:
    keys: list[str] = []
    depth = 0
    for line in block.splitlines():
        if depth == 1:
            match = re.match(r'\s*(?:"([^"]+)"|([A-Za-z_][A-Za-z0-9_.]*))\s*:\s*', line)
            if match:
                keys.append(match.group(1) or match.group(2))
        depth += delimiter_delta(line, "{", "}")
    return keys


def nested_quoted_keys(block: str, parent: str | None = None) -> list[tuple[str, str | None]]:
    """Top-level keys plus one nested level of quoted/identifier keys."""
    records: list[tuple[str, str | None]] = []
    depth = 0
    current_parent: str | None = parent
    parent_at_depth: dict[int, str | None] = {0: parent}
    for line in block.splitlines():
        before = depth
        if before >= 1:
            match = re.match(r'\s*(?:"([^"]+)"|([A-Za-z_][A-Za-z0-9_.]*))\s*:\s*', line)
            if match:
                key = match.group(1) or match.group(2)
                if before == 1:
                    records.append((key, parent))
                    current_parent = key
                    parent_at_depth[1] = key
                elif before == 2:
                    records.append((key, current_parent))
        depth += delimiter_delta(line, "{", "}")
        if depth < 2:
            current_parent = parent_at_depth.get(1, parent)
    return records


def array_strings(text: str, name: str) -> list[str]:
    match = re.search(rf"\b(?:var|const)\s+{re.escape(name)}\s*=", text)
    if not match:
        return []
    block = balanced_block(text, match.start(), "[", "]")
    if not block:
        return []
    return re.findall(r'"((?:\\.|[^"\\])*)"', block)


def enum_members(text: str, name: str) -> list[str]:
    match = re.search(rf"\benum\s+{re.escape(name)}\s*{{", text)
    if not match:
        return []
    block = balanced_block(text, match.start(), "{", "}")
    if not block:
        return []
    values: list[str] = []
    for line in block.splitlines()[1:]:
        code = line.split("#", 1)[0].replace(",", " ")
        for item in re.findall(r"\b[A-Z][A-Z0-9_]*\b", code):
            if item not in values:
                values.append(item)
    return values


def input_action_ids(project_text: str) -> list[str]:
    section = re.search(r"(?ms)^\[input\]\s*\n(?P<body>.*?)(?=^\[[^\]]+\]\s*$|\Z)", project_text)
    if not section:
        return []
    return sorted(re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=", section.group("body")))


def _rel(recovered: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(recovered.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


def _records(ids: Iterable[str], source_file: str, family: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ident in ids:
        if ident in seen:
            continue
        seen.add(ident)
        out.append({
            "id": ident,
            "family": family,
            "source_file": source_file.replace("\\", "/"),
            "source_kind": "recovered_source_scan",
        })
    return out


def _family(name: str, records: list[dict[str, Any]], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "name": name,
        "count": len(records),
        "ids": [r["id"] for r in records],
        "records": records,
    }
    if extra:
        payload.update(extra)
    return payload


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def scan_json_node_ids(path: Path) -> list[str]:
    data = json.loads(read_text(path))
    nodes = data.get("nodes") if isinstance(data, dict) else None
    if not isinstance(nodes, list):
        return []
    ids: list[str] = []
    for node in nodes:
        if isinstance(node, dict) and node.get("id") is not None:
            ids.append(str(node["id"]))
    return ids


def scan_preservation(recovered: Path) -> dict[str, Any]:
    recovered = Path(recovered)
    files: dict[str, Path] = {
        "classes": recovered / "Globals" / "PlayableClasses.gd",
        "skills": recovered / "Globals" / "Skills.gd",
        "supports": recovered / "Globals" / "SkillSupports.gd",
        "tags": recovered / "Globals" / "SkillTags.gd",
        "stats": recovered / "Globals" / "StatsInfo.gd",
        "genes": recovered / "Globals" / "Genes.gd",
        "project": recovered / "project.godot",
        "game_state": recovered / "Globals" / "GameState.gd",
        "constants": recovered / "Globals" / "Constants.gd",
        "status": recovered / "Globals" / "StatusEffects.gd",
        "tree_keystones": recovered / "Globals" / "Keystones" / "TreeKeystones.gd",
        "unique_keystones": recovered / "Globals" / "Keystones" / "UniqueKeystones.gd",
        "support_keystones": recovered / "Globals" / "Keystones" / "SupportKeystones.gd",
        "passive_tree": recovered / "passive_tree_data" / "passive_tree_gen.json",
        "tree_data": recovered / "passive_tree_data" / "tree_data.json",
        "slot_requirements": recovered / "Globals" / "SlotRequirements.gd",
    }

    missing = [name for name, path in files.items() if not path.is_file()]
    texts: dict[str, str] = {}
    for name, path in files.items():
        if path.is_file() and path.suffix.lower() != ".json":
            texts[name] = read_text(path)

    classes_text = texts.get("classes", "")
    class_ids = top_level_keys(variable_block(classes_text, "PLAYABLE_CLASSES") or "{}")
    spec_ids = top_level_keys(variable_block(classes_text, "PLAYABLE_SPECIALIZATIONS") or "{}")

    skill_ids = top_level_keys(variable_block(texts.get("skills", ""), "config") or "{}")
    support_ids = top_level_keys(variable_block(texts.get("supports", ""), "supports") or "{}")

    tag_ids = enum_members(texts.get("tags", ""), "Tags")
    stat_ids: list[str] = []
    seen_stats: set[str] = set()
    for array_name in ("stat_list", "character_sheet_list", "all_skill_list", "damage_list", "skill_sort_list"):
        for ident in array_strings(texts.get("stats", ""), array_name):
            if ident not in seen_stats:
                seen_stats.add(ident)
                stat_ids.append(ident)

    slot_ids = top_level_keys(variable_block(texts.get("genes", ""), "GeneSlot") or "{}")
    base_type_ids = top_level_keys(variable_block(texts.get("genes", ""), "BaseType") or "{}")

    input_ids = input_action_ids(texts.get("project", ""))

    save_records: list[dict[str, Any]] = []
    gs = texts.get("game_state", "")
    gs_rel = _rel(recovered, files["game_state"]) if files["game_state"].is_file() else "Globals/GameState.gd"
    for var_name in ("global_configuration", "initial_configuration"):
        block = variable_block(gs, var_name) or "{}"
        for key, parent in nested_quoted_keys(block, parent=var_name):
            ident = f"{parent}.{key}" if parent else key
            save_records.append({
                "id": ident,
                "family": "save_keys",
                "source_file": gs_rel.replace("\\", "/"),
                "source_kind": "recovered_source_scan",
                "parent": parent,
            })

    keystone_ids: list[str] = []
    keystone_records: list[dict[str, Any]] = []
    for key in ("tree_keystones", "unique_keystones", "support_keystones"):
        block = variable_block(texts.get(key, ""), "keystones") or "{}"
        ids = top_level_keys(block)
        rel = _rel(recovered, files[key]) if files[key].is_file() else key
        for ident in ids:
            if ident in keystone_ids:
                continue
            keystone_ids.append(ident)
            keystone_records.append({
                "id": ident,
                "family": "keystones",
                "source_file": rel.replace("\\", "/"),
                "source_kind": "recovered_source_scan",
            })

    passive_ids: list[str] = []
    passive_source = files["passive_tree"]
    if passive_source.is_file():
        passive_ids = scan_json_node_ids(passive_source)
        passive_rel = _rel(recovered, passive_source)
    elif files["tree_data"].is_file():
        passive_ids = scan_json_node_ids(files["tree_data"])
        passive_rel = _rel(recovered, files["tree_data"])
    else:
        passive_rel = "passive_tree_data/passive_tree_gen.json"

    combat_ids = enum_members(texts.get("constants", ""), "StatusFlags")
    combat_records = _records(combat_ids, _rel(recovered, files["constants"]) if files["constants"].is_file() else "Globals/Constants.gd", "combat_critical_ids")
    if "dash" in input_ids:
        combat_records.append({
            "id": "dash",
            "family": "combat_critical_ids",
            "source_file": _rel(recovered, files["project"]) if files["project"].is_file() else "project.godot",
            "source_kind": "recovered_source_scan",
        })
    for skill_id in skill_ids:
        combat_records.append({
            "id": f"skill:{skill_id}",
            "family": "combat_critical_ids",
            "source_file": _rel(recovered, files["skills"]) if files["skills"].is_file() else "Globals/Skills.gd",
            "source_kind": "recovered_source_scan",
        })

    families = {
        "classes": _family("classes", _records(class_ids, _rel(recovered, files["classes"]), "classes")),
        "specializations": _family("specializations", _records(spec_ids, _rel(recovered, files["classes"]), "specializations")),
        "skills": _family("skills", _records(skill_ids, _rel(recovered, files["skills"]), "skills")),
        "supports": _family("supports", _records(support_ids, _rel(recovered, files["supports"]), "supports")),
        "passives": _family("passives", _records(passive_ids, passive_rel, "passives")),
        "keystones": _family("keystones", keystone_records),
        "stats": _family("stats", _records(stat_ids, _rel(recovered, files["stats"]), "stats")),
        "tags": _family("tags", _records(tag_ids, _rel(recovered, files["tags"]), "tags")),
        "equipment_slots": _family("equipment_slots", _records(slot_ids, _rel(recovered, files["genes"]), "equipment_slots")),
        "equipment_data": _family("equipment_data", _records(base_type_ids, _rel(recovered, files["genes"]), "equipment_data")),
        "input_actions": _family("input_actions", _records(input_ids, _rel(recovered, files["project"]), "input_actions")),
        "save_keys": _family("save_keys", save_records),
        "combat_critical_ids": _family("combat_critical_ids", combat_records),
    }

    counts = {name: families[name]["count"] for name in REQUIRED_FAMILIES}
    source_files = sorted({
        rec["source_file"]
        for fam in families.values()
        for rec in fam["records"]
        if rec.get("source_file")
    })

    return {
        "schema_version": 1,
        "task": "P1-X3",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_of_truth": "recovered_source_scan",
        "recovered_root": recovered.name if recovered.name else recovered.as_posix(),
        "missing_anchor_files": missing,
        "families": families,
        "counts": counts,
        "source_files": source_files,
        "required_families": list(REQUIRED_FAMILIES),
        "agent_md_approx_not_used": True,
    }


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--recovered", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    root = (args.root or _repo_root_from_here()).resolve()
    recovered = (args.recovered or (root / "04_recovered")).resolve()
    out = (args.out or (root / "migration" / "preservation" / "contracts.json")).resolve()
    if not recovered.is_dir():
        print(json.dumps({"verdict": "FAIL", "error": f"recovered tree missing: {recovered}"}))
        return 2
    report = scan_preservation(recovered)
    # recovered_root should be repo-relative when possible
    try:
        report["recovered_root"] = recovered.relative_to(root).as_posix()
    except ValueError:
        report["recovered_root"] = recovered.as_posix()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "source_of_truth": report["source_of_truth"],
        "counts": report["counts"],
        "missing_anchor_files": report["missing_anchor_files"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
