#!/usr/bin/env python3
"""Manually merge CJK glyphs (scaled) into the game fonts.

Copies CJK Unified / Fullwidth / CJK-punct glyphs from a source CJK font
into each target font, scaling glyph outlines and metrics from the source
unitsPerEm to the target's. Latin glyphs in the target are never touched.

Usage:
    python scripts/merge_fonts2.py --src 03_raw/Fonts --cjk <zh.ttf> --out 02_tools/fonts_merged
"""

import argparse
import sys
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

CJK_RANGES = [
    (0x4E00, 0x9FFF),   # CJK Unified
    (0x3400, 0x4DBF),   # Ext A
    (0xF900, 0xFAFF),   # Compat
    (0x3000, 0x303F),   # CJK punct
    (0xFF00, 0xFFEF),   # Fullwidth
    (0x2010, 0x2027),   # dash/quote-ish
    (0x2028, 0x202E),
    (0x00B7, 0x00B7),   # middle dot
    (0x2018, 0x201F),   # quotes
    (0x2026, 0x2026),   # ellipsis
    (0xFE30, 0xFE4F),   # CJK compat forms
]


def in_ranges(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in CJK_RANGES)


def merge_font(target_path: Path, cjk_path: Path, out_path: Path):
    t = TTFont(str(target_path))
    c = TTFont(str(cjk_path))

    # variable fonts: drop variation tables that break manual edits
    for tag in ("gvar", "fvar", "HVAR", "VVAR", "MVAR", "STAT"):
        if tag in t:
            del t[tag]

    scale = t["head"].unitsPerEm / c["head"].unitsPerEm
    t_cmap = t.getBestCmap()
    c_cmap = c.getBestCmap()
    t_glyph_order = set(t.getGlyphOrder())
    glyf_t = t["glyf"]
    glyf_c = c["glyf"]
    hmtx_t = t["hmtx"]
    hmtx_c = c["hmtx"]

    added = 0
    skipped = 0
    added_names = set()
    cjk_glyphset = c.getGlyphSet()
    for cp, gname in sorted(c_cmap.items()):
        if not in_ranges(cp):
            continue
        if gname in t_glyph_order:
            skipped += 1
            continue
        if gname not in cjk_glyphset:
            skipped += 1
            continue
        # decompose composite to simple outlines
        rec = DecomposingRecordingPen(cjk_glyphset)
        try:
            glyf_c[gname].draw(rec, glyf_c)
        except Exception:
            skipped += 1
            continue
        # draw scaled into a new glyph
        pen = TTGlyphPen(t.getGlyphSet())
        tpen = TransformPen(pen, (scale, 0, 0, scale, 0, 0))
        try:
            rec.replay(tpen)
            new_glyph = pen.glyph()
        except Exception:
            skipped += 1
            continue
        if new_glyph.numberOfContours == 0:
            skipped += 1
            continue
        new_glyph.recalcBounds(glyf_t)
        glyf_t[gname] = new_glyph
        adv, lsb = hmtx_c[gname]
        hmtx_t[gname] = (int(round(adv * scale)), int(round(lsb * scale)))
        added_names.add(gname)
        added += 1

    # extend cmap: add new glyph names per codepoint
    if added:
        for table in t["cmap"].tables:
            if table.isUnicode():
                for cp, gname in sorted(c_cmap.items()):
                    if in_ranges(cp) and gname in added_names:
                        table.cmap[cp] = gname
        if t["cmap"].tables:
            t["cmap"].tables[0].cmap = dict(sorted(t["cmap"].tables[0].cmap.items()))

    t.save(str(out_path))
    return added, skipped


def verify(path: Path, samples: str = "装备生命魔法伤害属性技能，。！？"):
    f = TTFont(str(path))
    cmap = f.getBestCmap() or {}
    missing = [ch for ch in samples if ord(ch) not in cmap]
    latin_ok = all(ord(x) in cmap for x in "Aa0")
    f.close()
    return missing, latin_ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=Path("03_raw/Fonts"))
    ap.add_argument("--cjk", type=Path, default=Path(
        "02_tools/fusion_pixel/fusion-pixel-12px-proportional-zh_hans.ttf"))
    ap.add_argument("--out", type=Path, default=Path("02_tools/fonts_merged"))
    ap.add_argument("--inplace", action="store_true")
    args = ap.parse_args()

    if not args.cjk.exists():
        print("CJK font missing:", args.cjk)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    rc = 0
    for f in sorted(args.src.glob("*.ttf")):
        out = f if args.inplace else args.out / f.name
        try:
            added, skipped = merge_font(f, args.cjk, out)
            missing, latin = verify(out)
            size = out.stat().st_size
            status = "OK" if not missing and latin else f"BAD missing={missing} latin={latin}"
            print(f"  {f.name}: +{added} glyphs (skip {skipped}) {size/1e6:.1f}MB {status}")
            if missing or not latin:
                rc = 1
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  {f.name}: FAILED {e}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())