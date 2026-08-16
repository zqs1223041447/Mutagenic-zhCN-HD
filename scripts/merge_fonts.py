#!/usr/bin/env python3
"""Merge CJK glyphs from a Chinese font into the game's fonts, in place.

Uses fontTools.merge with the original font first (so its Latin glyphs and
metrics win on conflict). Outputs merged fonts to --outdir, keyed by
original font name.

Usage:
    python scripts/merge_fonts.py --src 03_raw/Fonts --cjk <zh.ttf> --out 02_tools/fonts_merged
"""

import argparse
import sys
from pathlib import Path

from fontTools.merge import Merger
from fontTools.ttLib import TTFont


def verify_cjk(path: Path, samples: str = "装备生命魔法伤害属性技能"):
    f = TTFont(str(path))
    cmap = f.getBestCmap() or {}
    missing = [ch for ch in samples if ord(ch) not in cmap]
    latin_ok = ord("A") in cmap and ord("a") in cmap and ord("0") in cmap
    f.close()
    return missing, latin_ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=Path("03_raw/Fonts"))
    ap.add_argument("--cjk", type=Path, required=True,
                    default=Path("02_tools/fusion_pixel/fusion-pixel-12px-proportional-zh_hans.ttf"))
    ap.add_argument("--out", type=Path, default=Path("02_tools/fonts_merged"))
    ap.add_argument("--inplace", action="store_true",
                    help="write back into --src instead of --out")
    args = ap.parse_args()

    cjk_ok, latin_ok = verify_cjk(args.cjk)
    if cjk_ok:
        print(f"CJK source missing {cjk_ok}"); return 1

    args.out.mkdir(parents=True, exist_ok=True)
    merger = Merger()
    for f in sorted(args.src.glob("*.ttf")):
        out = f if args.inplace else args.out / f.name
        try:
            merged = merger.merge([str(f), str(args.cjk)])
            merged.save(str(out))
            merger.close()
        except Exception as e:
            print(f"  {f.name}: MERGE FAILED: {e}")
            # retry with fresh merger
            merger = Merger()
            continue
        merger = Merger()
        missing, latin_ok2 = verify_cjk(out)
        size = out.stat().st_size
        status = "OK" if not missing and latin_ok2 else f"BAD missing={missing} latin={latin_ok2}"
        print(f"  {f.name} -> {out.name} ({size/1e6:.1f}MB) {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())