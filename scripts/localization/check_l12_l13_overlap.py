import json
from pathlib import Path

MODS = Path(__file__).resolve().parents[2] / "mods"
m12 = json.load(open(MODS / "c5-l12-stats-tags-zhcn/mod.json", encoding="utf-8"))
m13 = json.load(open(MODS / "c5-l13-dynamic-ui-zhcn/mod.json", encoding="utf-8"))

def norm(p):
    return json.dumps(
        {k: p.get(k) for k in ("path", "old_text", "new_text", "expected_occurrences")},
        ensure_ascii=False, sort_keys=True,
    )

e12 = {norm(p): p for p in m12["patches"] if p["path"] == "Scenes/Popups/EscapeMenu.gd"}
e13 = {norm(p): p for p in m13["patches"] if p["path"] == "Scenes/Popups/EscapeMenu.gd"}
print("L12 EscapeMenu patches:", len(e12))
print("L13 EscapeMenu patches:", len(e13))
overlap = set(e12) & set(e13)
print("identical overlap (safe, resolver collapses):", len(overlap))
conflict = set(e12) ^ set(e13)
print("non-identical total:", len(conflict))
for k in conflict:
    src = "L12" if k in e12 else "L13"
    p = (e12 if k in e12 else e13)[k]
    print(f"  [{src}] {p['path']}:{p.get('unit_id','?')} old={p['old_text'][:80]!r}")

# also check L13 vs L12 on other shared files
files12 = set(p["path"] for p in m12["patches"])
files13 = set(p["path"] for p in m13["patches"])
print("\nshared files L12/L13:", files12 & files13)
