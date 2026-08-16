#!/usr/bin/env python3
"""Extract ALL passive tree node names from PassiveTagStats.gd + full keystone dicts."""
import json
import re
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")
OUT = ROOT / "10_logs/full_passive_text_extract.json"
result = {}

# PassiveTagStats.gd: stats dict = passive_tag -> { "name": ... }
p = ROOT / "04_recovered/Globals/PassiveTagStats.gd"
content = p.read_text(encoding="utf-8")
lines = content.splitlines()
nodes = []
current = None
for i, l in enumerate(lines, 1):
    s = l.strip()
    m = re.match(r'^"([a-z0-9_]+)"\s*:\s*\{', s)
    if m:
        current = {"key": m.group(1), "line": i, "name": None, "has_desc": False}
        continue
    if current is not None:
        mn = re.match(r'^"name":\s*"((?:[^"\\]|\\.)*)",?$', s)
        if mn:
            current["name"] = {"line": i, "line_text": s, "value": mn.group(1)}
            continue
        md = re.match(r'^"description":\s*"', s)
        if md:
            current["has_desc"] = True
            continue
        if s == "}," or s == "}":
            nodes.append(current)
            current = None
if current is not None:
    nodes.append(current)

result["PassiveTagStats"] = {
    "count": len(nodes),
    "with_name": sum(1 for n in nodes if n["name"]),
    "with_desc": sum(1 for n in nodes if n["has_desc"]),
    "nodes": nodes,
}
print(f"== PassiveTagStats: {len(nodes)} nodes, {sum(1 for n in nodes if n['name'])} with name, {sum(1 for n in nodes if n['has_desc'])} with description")
for n in nodes[:30]:
    name = n["name"]["value"] if n["name"] else "???"
    print(f"  {n['key']:35s} | {name}")

# Keystones
for kname in ["TreeKeystones.gd", "SupportKeystones.gd", "UniqueKeystones.gd"]:
    kp = ROOT / "04_recovered/Globals/Keystones" / kname
    if not kp.is_file():
        continue
    kcontent = kp.read_text(encoding="utf-8")
    klines = kcontent.splitlines()
    kentries = []
    kcurrent = None
    for i, l in enumerate(klines, 1):
        s = l.strip()
        km = re.match(r'^"([a-z0-9_]+)"\s*:\s*\{', s)
        if km:
            kcurrent = {"key": km.group(1), "line": i, "name": None, "description": None}
            continue
        if kcurrent is not None:
            kn = re.match(r'^"name":\s*"((?:[^"\\]|\\.)*)",?$', s)
            if kn:
                kcurrent["name"] = {"line": i, "line_text": s, "value": kn.group(1)}
                continue
            kd = re.match(r'^"description":\s*"((?:[^"\\]|\\.)*)",?$', s)
            if kd:
                kcurrent["description"] = {"line": i, "line_text": s, "value": kd.group(1)}
                continue
            if s == "}," or s == "}":
                kentries.append(kcurrent)
                kcurrent = None
    if kcurrent is not None:
        kentries.append(kcurrent)
    result[kname] = {"count": len(kentries), "entries": kentries}
    print(f"\n== {kname}: {len(kentries)} entries")
    for e in kentries[:12]:
        n = e["name"]["value"] if e["name"] else "???"
        d = e["description"]["value"] if e["description"] else ""
        print(f"  {e['key']:35s} | {n:30s} | {d[:60]}")

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nsaved to {OUT}")
