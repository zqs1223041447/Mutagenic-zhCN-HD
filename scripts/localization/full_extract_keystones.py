import json
import re
from pathlib import Path

root = Path(r"G:\opencode-Mutageni\04_recovered\Globals\Keystones")
result = {}
for kname in ["TreeKeystones.gd", "SupportKeystones.gd", "UniqueKeystones.gd"]:
    f = root / kname
    content = f.read_text(encoding="utf-8")
    lines = content.splitlines()
    entries = []
    cur = None
    for i, l in enumerate(lines, 1):
        s = l.strip()
        m = re.match(r'^"([A-Z][A-Z0-9_]*)"\s*:\s*\{', s)
        if m:
            cur = {"key": m.group(1), "line": i, "name": None, "description": None}
            continue
        if cur is not None:
            mn = re.match(r'^"name":\s*"((?:[^"\\]|\\.)*)",?$', s)
            if mn:
                cur["name"] = {"line": i, "line_text": s, "value": mn.group(1)}
                continue
            md = re.match(r'^"description":\s*"((?:[^"\\]|\\.)*)",?$', s)
            if md:
                cur["description"] = {"line": i, "line_text": s, "value": md.group(1)}
                continue
            if s in ("},", "}"):
                entries.append(cur)
                cur = None
    if cur:
        entries.append(cur)
    result[kname] = entries
    print(f"== {kname}: {len(entries)} entries")
    for e in entries[:5]:
        n = e["name"]["value"] if e["name"] else "???"
        print(f"  {e['key']:35s} | {n}")

Path(r"G:\opencode-Mutageni\10_logs\keystones_extract.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8"
)
print("saved to 10_logs/keystones_extract.json")
