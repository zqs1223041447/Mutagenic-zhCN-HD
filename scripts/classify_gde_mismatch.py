"""Cross-reference .gde mismatches against intentional edits in 06_worktree.

04_recovered = pristine decompiled source (never edited)
06_worktree  = editable copy (contains our intentional modifications)

A .gde that differs from the original is EXPECTED when its .gd was edited.
It is only a pipeline defect when the .gd is byte-identical to 04_recovered
yet the produced .gde still differs from 03_raw.

Usage:
    python scripts/classify_gde_mismatch.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "03_raw"
REC = ROOT / "04_recovered"
WT = ROOT / "06_worktree"
OUT = ROOT / "07_compiled"


def main() -> int:
    originals = sorted(RAW.rglob("*.gde"))
    edited, unedited_ok, unedited_bad, missing_src = [], [], [], []

    for gde_orig in originals:
        rel = gde_orig.relative_to(RAW)
        gd_rel = rel.with_suffix(".gd")
        ours = OUT / rel
        if not ours.exists():
            continue

        same_gde = ours.read_bytes() == gde_orig.read_bytes()

        rec = REC / gd_rel
        wt = WT / gd_rel
        if not rec.exists() or not wt.exists():
            missing_src.append(str(gd_rel))
            continue

        gd_edited = rec.read_bytes() != wt.read_bytes()

        if same_gde:
            continue                       # identical .gde -> nothing to explain
        if gd_edited:
            edited.append(str(rel))        # differs because we edited the source
        else:
            unedited_bad.append(str(rel))  # differs with NO edit -> pipeline defect

    # also count how many edited scripts exist overall
    total_edited = 0
    for rec in REC.rglob("*.gd"):
        wt = WT / rec.relative_to(REC)
        if wt.exists() and wt.read_bytes() != rec.read_bytes():
            total_edited += 1

    print(f"originals with a generated .gde : {len(originals)}")
    print(f"edited .gd in 06_worktree total : {total_edited}\n")
    print(f".gde differs BECAUSE .gd edited : {len(edited)}   (expected)")
    print(f".gde differs with NO edit       : {len(unedited_bad)}   (pipeline defect)")
    print(f"source missing for comparison   : {len(missing_src)}")

    if unedited_bad:
        print(f"\nPIPELINE DEFECTS ({len(unedited_bad)}), first 20:")
        for n in unedited_bad[:20]:
            o = (OUT / n).stat().st_size
            r = (RAW / n).stat().st_size
            print(f"  - {n}: ours={o} orig={r}")
    if edited:
        print(f"\nexplained by edits ({len(edited)}), first 10:")
        for n in edited[:10]:
            print(f"  - {n}")

    ok = not unedited_bad
    print(f"\nVERDICT: {'PASS - every mismatch is explained by an intentional edit' if ok else 'FAIL - unexplained mismatches remain'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
