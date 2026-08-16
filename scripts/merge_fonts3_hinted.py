#!/usr/bin/env python3
"""Merge CJK glyphs INTO game fonts PRESERVING TrueType hinting.

The base merge_fonts2.py rebuilds glyph outlines via pens, which discards
TrueType 'program' (hinting) instructions.  Godot 3.5 DynamicFont enables
hinting by default, so hinted glyphs render far sharper at small sizes.

When the CJK source has the SAME unitsPerEm as the target (e.g. Deng.ttf
upem=2048 == rsans upem=2048), we deep-copy the glyph table entries
(including program) and only scale metrics — outlines need no transform,
so hinting survives intact.  Composite glyphs are decomposed via pens.

Usage:
    python scripts/merge_fonts3_hinted.py --src 03_raw/Fonts --cjk <zh.ttf> --out 02_tools/fonts_merged_hinted
"""

import argparse
import sys
from copy import deepcopy
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

    # drop variable-font tables that break manual edits
    for tag in ("gvar", "fvar", "HVAR", "VVAR", "MVAR", "STAT"):
        if tag in t:
            del t[tag]

    t_upem = t["head"].unitsPerEm
    c_upem = c["head"].unitsPerEm
    scale = t_upem / c_upem
    same_upem = (t_upem == c_upem)
    t_cmap = t.getBestCmap()
    c_cmap = c.getBestCmap()
    t_glyph_order = set(t.getGlyphOrder())
    glyf_t = t["glyf"]
    glyf_c = c["glyf"]
    hmtx_t = t["hmtx"]
    hmtx_c = c["hmtx"]
    c_glyphset = c.getGlyphSet()

    added = 0
    skipped = 0
    added_names = set()
    copied_with_hint = 0

    for cp, gname in sorted(c_cmap.items()):
        if not in_ranges(cp):
            continue
        if gname in t_glyph_order:
            skipped += 1
            continue
        if gname not in c_glyphset:
            skipped += 1
            continue

        src_glyph = glyf_c[gname]
        ncont = getattr(src_glyph, "numberOfContours", 0)

        if same_upem and ncont >= 0:
            # same unitsPerEm: deep-copy the glyph entry INCLUDING the
            # TrueType program (hinting instructions).  Outlines need no
            # transform so hints stay valid.
            new_glyph = deepcopy(src_glyph)
            glyf_t[gname] = new_glyph
            has_hint = bool(getattr(src_glyph, "program", None)
                            and src_glyph.program.bytecode)
            if has_hint:
                copied_with_hint += 1
        else:
            # differing upem or composite: decompose + rebuild (hint lost,
            # but geometric correctness is what matters here)
            try:
                rec = DecomposingRecordingPen(c_glyphset)
                src_glyph.draw(rec, glyf_c)
                pen = TTGlyphPen(t.getGlyphSet())
                tpen = TransformPen(pen, (scale, 0, 0, scale, 0, 0))
                rec.replay(tpen)
                new_glyph = pen.glyph()
                if new_glyph.numberOfContours == 0:
                    skipped += 1
                    continue
                new_glyph.recalcBounds(glyf_t)
                glyf_t[gname] = new_glyph
            except Exception:
                skipped += 1
                continue

        adv, lsb = hmtx_c[gname]
        hmtx_t[gname] = (int(round(adv * scale)), int(round(lsb * scale)))
        added_names.add(gname)
        added += 1

    if added:
        for table in t["cmap"].tables:
            if table.isUnicode():
                for cp, gname in sorted(c_cmap.items()):
                    if in_ranges(cp) and gname in added_names:
                        table.cmap[cp] = gname
        if t["cmap"].tables:
            t["cmap"].tables[0].cmap = dict(sorted(t["cmap"].tables[0].cmap.items()))

    t.save(str(out_path))
    return added, skipped, copied_with_hint


def verify(path: Path, samples: str = "装备掠夺魔盒伤害以技能，范围："):
    f = TTFont(str(path))
    cmap = f.getBestCmap() or {}
    missing = [ch for ch in samples if ord(ch) not in cmap]
    latin_ok = all(ord(x) in cmap for x in "Aa0")
    f.close()
    return missing, latin_ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=Path("03_raw/Fonts"))
    ap.add_argument("--cjk", type=Path, default=Path("C:/Windows/Fonts/Deng.ttf"))
    ap.add_argument("--out", type=Path, default=Path("02_tools/fonts_merged_hinted"))
    args = ap.parse_args()

    if not args.cjk.exists():
        print("CJK font missing:", args.cjk)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    rc = 0
    for f in sorted(args.src.glob("*.ttf")):
        out = args.out / f.name
        try:
            added, skipped, hinted = merge_font(f, args.cjk, out)
            missing, latin = verify(out)
            status = "OK" if not missing and latin else f"BAD missing={missing} latin={latin}"
            size = out.stat().st_size
            print(f"  {f.name}: +{added} glyphs (skip {skipped}, hint-preserved {hinted}) {size/1e6:.1f}MB {status}")
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