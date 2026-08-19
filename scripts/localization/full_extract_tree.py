#!/usr/bin/env python3
"""Extract passive tree text sources: JSON tree data, Keystones, StatsInfo stat_name, SkillTags TagNames."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "10_logs/full_tree_text_extract.json"
result = {}

# 1. passive_tree_data JSON files (03_raw holds runtime; 04_recovered may hold source copies)
for base_name in ["03_raw", "04_recovered"]:
    d = ROOT / base_name / "passive_tree_data"
    if d.is_dir():
        files = sorted(d.rglob("*.json"))
        print(f"== {base_name}/passive_tree_data: {len(files)} json files")
        sample = {}
        total_nodes = 0
        for f in files[:400]:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  parse fail {f.relative_to(d)}: {e}")
                continue
            # guess structure: list of nodes or dict keyed by id
            nodes = data if isinstance(data, list) else list(data.values())
            if isinstance(data, dict) and all(isinstance(v, dict) for v in nodes):
                total_nodes += len(nodes)
                for n in nodes:
                    if "name" in n or "description" in n:
                        name = n.get("name", "")
                        desc = n.get("description", "")
                        if name or desc:
                            sample.setdefault(f.relative_to(d).as_posix(), []).append(
                                {"name": name, "description": desc, "fields": list(n.keys())}
                            )
        result[f"{base_name}_tree"] = {"files": len(files), "nodes": total_nodes, "samples": dict(list(sample.items())[:3])}
        for k, v in list(sample.items())[:3]:
            print(f"  {k}: {len(v)} text-bearing nodes, fields={v[0]['fields']}")
            for n in v[:2]:
                print(f"    name={n['name'][:60]!r} desc={n['description'][:80]!r}")

# 2. Keystone files
keystone_dir = ROOT / "04_recovered/Globals/Keystones"
if keystone_dir.is_dir():
    print(f"\n== Keystones dir: {[p.name for p in keystone_dir.iterdir()]}")
    for f in sorted(keystone_dir.glob("*.gd")):
        content = f.read_text(encoding="utf-8")
        names = re.findall(r'"name":\s*"([^"]+)"', content)
        descs = re.findall(r'"description":\s*"([^"]+)"', content)
        print(f"  {f.name}: name-count={len(names)} desc-count={len(descs)}")
        result[f"keystones/{f.name}"] = {"names": names, "descs": descs[:3]}
else:
    # search for keystone-like files anywhere
    print("\n== no Keystones dir; searching for keystone files")
    for f in ROOT.joinpath("04_recovered/Globals").rglob("*Keystone*.gd"):
        print(f"  found: {f.relative_to(ROOT)}")

# 3. StatsInfo.stat_name
si = ROOT / "04_recovered/Globals/StatsInfo.gd"
if si.is_file():
    content = si.read_text(encoding="utf-8")
    lines = content.splitlines()
    stats = []
    in_dict = False
    for i, l in enumerate(lines, 1):
        m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"([^"]*)"', l)
        if m and ('stat_name' in l or in_dict):
            stats.append({"key": m.group(1), "value": m.group(2), "line": i})
        if 'stat_name' in l:
            in_dict = True
        if in_dict and i > 600:
            break
    result["StatsInfo_stat_name"] = {"count": len(stats), "entries": stats}
    print(f"\n== StatsInfo.stat_name: {len(stats)} entries")
    for s in stats[:40]:
        print(f"  {s['line']:5d} {s['key']:30s} = {s['value']}")

# 4. SkillTags.TagNames
st = ROOT / "04_recovered/Globals/SkillTags.gd"
if st.is_file():
    content = st.read_text(encoding="utf-8")
    tags = re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"([^"]*)"', content)
    result["SkillTags_TagNames"] = {"count": len(tags), "entries": tags}
    print(f"\n== SkillTags TagNames: {len(tags)} entries")
    for k, v in tags[:40]:
        print(f"  {k:30s} = {v}")

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nsaved to {OUT}")
