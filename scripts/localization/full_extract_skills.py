#!/usr/bin/env python3
"""Extract ALL skill + support name/description field lines from 04_recovered for full translation."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "10_logs/full_skill_text_extract.json"

def extract_entities(path: Path):
    """Parse dict-of-dicts: internal_key -> { 'name': ..., 'description': ..., ... }"""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    entities = []
    current = None
    for i, l in enumerate(lines, 1):
        stripped = l.strip()
        m = re.match(r'^"([A-Za-z0-9_]+)"\s*:\s*\{', stripped)
        if m:
            current = {"key": m.group(1), "line": i, "name": None, "description": None}
            continue
        if current is not None:
            mn = re.match(r'^"name":\s*"((?:[^"\\]|\\.)*)",?$', stripped)
            if mn:
                current["name"] = {"line": i, "line_text": stripped, "value": mn.group(1)}
                continue
            md = re.match(r'^"description":\s*"((?:[^"\\]|\\.)*)",?$', stripped)
            if md:
                current["description"] = {"line": i, "line_text": stripped, "value": md.group(1)}
                continue
            if stripped == "}," or stripped == "}":
                entities.append(current)
                current = None
    if current is not None:
        entities.append(current)
    return entities


result = {}
for name in ["Skills.gd", "SkillSupports.gd"]:
    p = ROOT / "04_recovered/Globals" / name
    entities = extract_entities(p)
    result[name] = {
        "count": len(entities),
        "entities": entities,
    }
    print(f"== {name}: {len(entities)} entities")
    for e in entities:
        n = e["name"]["value"] if e["name"] else "???"
        d = e["description"]["value"] if e["description"] else "???"
        print(f"  {e['key']:24s} | {n:28s} | {(d[:70] + '...') if d and len(d) > 70 else d}")

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nsaved to {OUT}")
