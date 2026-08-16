#!/usr/bin/env python3
"""Merge batch translation results into one translation map with validation.

Validates: every source unit has exactly one entry, placeholders preserved,
no duplicate/conflicting translations, skip entries excluded.

Usage:
    python scripts/merge_translations.py [--batches batch_1_result.json ...] [-o map.json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"%[sdifo%]")


def validate(en: str, zh: str):
    errs = []
    en_ph = sorted(PLACEHOLDER_RE.findall(en))
    zh_ph = sorted(PLACEHOLDER_RE.findall(zh))
    if en_ph != zh_ph:
        errs.append(f"placeholder mismatch: {en!r} -> {zh!r} ({en_ph} vs {zh_ph})")
    if zh == en and len(zh) > 1:
        # unchanged non-trivial string: warn (may be legit for proper nouns)
        errs.append(f"unchanged: {en!r}")
    if any(c in "\"'\\" for c in zh):
        pass  # allowed inside literals; apply script handles raw insert
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", nargs="*",
                    default=[f"05_translation/batch_{i}_result.json" for i in range(1, 5)])
    ap.add_argument("-o", "--output", type=Path, default=Path("05_translation/translation_map.json"))
    ap.add_argument("--units", type=Path, default=Path("05_translation/units.json"))
    ap.add_argument("--extra-map", type=Path, default=Path("05_translation/batch1_ui.json"),
                    help="already-applied map (batch1) that counts toward expected units")
    args = ap.parse_args()

    units = json.loads(args.units.read_text(encoding="utf-8"))["units"]
    expected = {u["text"] for u in units}

    mapping = {}
    errors = []
    seen_src = set()
    total = 0
    if args.extra_map and args.extra_map.exists():
        for item in json.loads(args.extra_map.read_text(encoding="utf-8")):
            src = item.get("text")
            zh = item.get("translation")
            if src and zh:
                mapping[src] = zh
                seen_src.add(src)
                total += 1
    for bf in args.batches:
        bf = Path(bf)
        if not bf.exists():
            print(f"missing batch: {bf}")
            return 1
        items = json.loads(bf.read_text(encoding="utf-8"))
        for item in items:
            src = item.get("text")
            if src in seen_src:
                errors.append(f"duplicate source in results: {src!r}")
                continue
            seen_src.add(src)
            if item.get("skip"):
                continue
            zh = item.get("translation")
            if not zh:
                errors.append(f"no translation for {src!r}")
                continue
            for e in validate(src, zh):
                errors.append(e)
            mapping[src] = zh
            total += 1

    missing = expected - seen_src
    if missing:
        errors.append(f"MISSING {len(missing)} units, e.g. {sorted(missing)[:5]}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "count": total,
        "mapping": mapping,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"merged: {total} translations, {len(expected)} expected units")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors[:30]:
            print("  ", e)
        return 1
    print(f"output: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())