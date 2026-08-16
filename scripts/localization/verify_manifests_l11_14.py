import json
from pathlib import Path

for name in ["c5-l11-passive-tree-zhcn", "c5-l12-stats-tags-zhcn", "c5-l13-dynamic-ui-zhcn", "c5-l14-static-scenes-zhcn"]:
    p = Path(r"G:\opencode-Mutageni\mods") / name / "mod.json"
    if p.is_file():
        m = json.load(open(p, encoding="utf-8"))
        files = set(x["path"] for x in m["patches"])
        kinds = set(x.get("classification") for x in m["patches"])
        print(f"{name}: patches={len(m['patches'])} files={len(files)} kinds={kinds}")
    else:
        print(f"{name}: MISSING")
