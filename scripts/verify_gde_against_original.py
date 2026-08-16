"""Verify every generated .gde against the original in 03_raw, byte for byte.

This is the real correctness gate for the compile+encrypt pipeline: it covers
ALL scripts that have an original counterpart (not an alphabetical sample), so
Globals/ and Scenes/ are included, and it reports per-directory results.

A mismatch means our .gdc bytecode or the GDEC container differs from what the
game shipped -- FAIL CLOSED.

Usage:
    python scripts/verify_gde_against_original.py
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "03_raw"
OUT = ROOT / "07_compiled"


def top_dir(rel: Path) -> str:
    return rel.parts[0] if len(rel.parts) > 1 else "<root>"


def main() -> int:
    originals = sorted(RAW.rglob("*.gde"))
    if not originals:
        sys.exit("ERROR: no .gde found in 03_raw")

    stats = defaultdict(lambda: {"match": 0, "diff": 0, "missing": 0})
    diffs, missing = [], []

    for gde_orig in originals:
        rel = gde_orig.relative_to(RAW)
        bucket = stats[top_dir(rel)]
        ours = OUT / rel
        if not ours.exists():
            bucket["missing"] += 1
            missing.append(str(rel))
            continue
        if ours.read_bytes() == gde_orig.read_bytes():
            bucket["match"] += 1
        else:
            bucket["diff"] += 1
            diffs.append((str(rel), ours.stat().st_size, gde_orig.stat().st_size))

    total_match = sum(s["match"] for s in stats.values())
    total_diff = sum(s["diff"] for s in stats.values())
    total_missing = sum(s["missing"] for s in stats.values())

    print(f"originals in 03_raw: {len(originals)}\n")
    print(f"{'directory':<24}{'match':>8}{'diff':>8}{'missing':>9}")
    print("-" * 49)
    for d in sorted(stats):
        s = stats[d]
        print(f"{d:<24}{s['match']:>8}{s['diff']:>8}{s['missing']:>9}")
    print("-" * 49)
    print(f"{'TOTAL':<24}{total_match:>8}{total_diff:>8}{total_missing:>9}")

    if diffs:
        print(f"\nmismatched ({len(diffs)}), first 15:")
        for name, a, b in diffs[:15]:
            print(f"  - {name}: ours={a} orig={b}")
    if missing:
        print(f"\nmissing from 07_compiled ({len(missing)}), first 15:")
        for m in missing[:15]:
            print(f"  - {m}")

    ok = total_diff == 0 and total_missing == 0
    print(f"\nVERDICT: {'PASS - all .gde byte-identical to original' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
