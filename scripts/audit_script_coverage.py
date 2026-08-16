"""Audit script coverage between 03_raw (original PCK tree) and 06_worktree.

Question this answers:
  build_pack.py overlays 06_worktree/*.gd, deleting the matching .gde/.gd.remap,
  and then deletes ALL leftover .gde/.remap.  If a script exists in 03_raw as
  .gde but has NO .gd counterpart in 06_worktree, that script is silently
  DROPPED from the final PCK entirely (no .gd, no .gde) -> missing script.

Reports:
  - .gde present in 03_raw
  - .gd  present in 06_worktree
  - .gde with NO matching .gd  (== scripts dropped by current build_pack.py)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "03_raw"
WT = ROOT / "06_worktree"

SKIP_DIRS = {"addons", ".autoconverted"}


def rel_set(base: Path, pattern: str, strip_suffix: str) -> set:
    out = set()
    for p in base.rglob(pattern):
        if not p.is_file():
            continue
        rel = p.relative_to(base)
        if any(sk in rel.parts for sk in SKIP_DIRS):
            continue
        s = str(rel).replace("\\", "/")
        assert s.endswith(strip_suffix), s
        out.add(s[: -len(strip_suffix)])
    return out


gde = rel_set(RAW, "*.gde", ".gde")
remap = rel_set(RAW, "*.gd.remap", ".gd.remap")
gd_raw = rel_set(RAW, "*.gd", ".gd")
gd_wt = rel_set(WT, "*.gd", ".gd")

print(f"03_raw    .gde        : {len(gde)}")
print(f"03_raw    .gd.remap   : {len(remap)}")
print(f"03_raw    .gd (plain) : {len(gd_raw)}")
print(f"06_worktree .gd       : {len(gd_wt)}")

dropped = sorted(gde - gd_wt)
print(f"\n.gde WITHOUT matching 06_worktree/.gd  (DROPPED by build_pack.py): {len(dropped)}")
for d in dropped[:40]:
    print(f"   {d}.gde")
if len(dropped) > 40:
    print(f"   ... and {len(dropped) - 40} more")

extra = sorted(gd_wt - gde)
print(f"\n06_worktree/.gd with NO .gde in 03_raw (new/plain scripts): {len(extra)}")
for e in extra[:20]:
    print(f"   {e}.gd")
if len(extra) > 20:
    print(f"   ... and {len(extra) - 20} more")

# remap targets that would break
print(f"\nremap without matching .gde: {len(sorted(remap - gde))}")
