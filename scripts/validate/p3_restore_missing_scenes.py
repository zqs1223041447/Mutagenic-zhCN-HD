#!/usr/bin/env python3
"""P3 asset-gap restoration: recover the 8 preload-missing popup scenes.

Boot log (P2-BATCH-3, migration/conversion/p2_batch3_boot_after.json) still
carries 8 SCRIPT ERRORs of the form `Preload file ... does not exist`, plus
two sibling missing scripts (SkillButton.gd / SupportButton.gd).  All sources
exist under 04_recovered/.  This tool restores them into product/ using the
established wave-converter rules (scripts/migration/menu_convert.py):

  * format=2 -> format=3 scene conversion + Godot 4 renames,
  * res://Scenes/ -> res://scenes/ case rewrite,
  * .import / .uid sidecars are never copied,
  * 04_recovered stays byte-identical (fingerprint checked).

Conservative by design:
  * only files MISSING from product/ are written (never overwrites another
    lane's conversions),
  * every destination path must land inside product/scenes/Popups/** (the
    write domain agreed for this lane); anything else is recorded as
    out_of_domain and left untouched,
  * missing binary assets (.aseprite/.png/.wav) referenced by the closure are
    out of scope and only reported.

Usage:
    python scripts/validate/p3_restore_missing_scenes.py [--dry-run] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_MIGRATION = Path(__file__).resolve().parents[1] / "migration"
if str(_MIGRATION) not in sys.path:
    sys.path.insert(0, str(_MIGRATION))

from menu_convert import (  # type: ignore  # noqa: E402
    SKIP_SUFFIXES,
    TEXT_SUFFIXES,
    collect_menu_files,
    convert_file_text,
    product_rel,
    rewrite_scenes_case,
)
from boot_convert import tree_fingerprint  # type: ignore  # noqa: E402

TASK = "P3-C0-ASSET-RESTORE"

# Recovered-relative roots: the 8 preload-missing scenes plus the two missing
# SkillSelect button scripts called out by the same boot log.
RESTORE_ROOTS = (
    "Scenes/Popups/Dialogs/WorldMap/MapNode.tscn",
    "Scenes/Popups/Dialogs/WorldMap/Edge.tscn",
    "Scenes/Popups/Dialogs/TreeSelector/TreeSelector.tscn",
    "Scenes/Popups/Dialogs/SkillLoadoutSelector/SkillLoadoutSelector.tscn",
    "Scenes/Popups/Dialogs/HelpTip/WeaponIntro/WeaponIntro.tscn",
    "Scenes/Popups/Dialogs/OutfitSelector/OutfitOption.tscn",
    "Scenes/Popups/Dialogs/SpecializationPicker/SpecializationOption.tscn",
    "Scenes/Popups/Dialogs/HelpTip/SpecializationTip/SpecializationTip.tscn",
    "Scenes/Popups/Dialogs/SkillSelect/SkillButton.gd",
    "Scenes/Popups/Dialogs/SkillSelect/SupportButton.gd",
)

# This lane's product/ write domain for restored scene assets.
ALLOWED_DEST_PREFIXES = ("scenes/Popups/",)

MISSING_ASSET_SUFFIXES = {".aseprite", ".png", ".wav", ".ogg"}


def is_allowed_dest(dest_rel: str) -> bool:
    rel = dest_rel.replace("\\", "/")
    return any(rel.startswith(p) for p in ALLOWED_DEST_PREFIXES)


def restore(recovered: Path, product: Path, dry_run: bool = False) -> dict:
    before = tree_fingerprint(recovered)
    closure = collect_menu_files(recovered, roots=RESTORE_ROOTS, forbidden=())

    restored: list[str] = []
    skipped_existing: list[str] = []
    out_of_domain: list[str] = []
    missing_assets: list[str] = []

    for rel in closure:
        src = recovered / rel
        if not src.is_file():
            continue
        dest_rel = product_rel(rel)
        if not is_allowed_dest(dest_rel):
            out_of_domain.append(dest_rel)
            continue
        dst = product / dest_rel
        if dst.is_file():
            skipped_existing.append(dest_rel)
            continue
        if src.suffix.lower() in SKIP_SUFFIXES:
            continue
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in TEXT_SUFFIXES:
            text = rewrite_scenes_case(
                convert_file_text(rel, src.read_text(encoding="utf-8", errors="replace")))
            if not dry_run:
                dst.write_text(text, encoding="utf-8", newline="\n")
            restored.append(dest_rel)
        elif src.suffix.lower() in MISSING_ASSET_SUFFIXES:
            # Referenced by the closure but explicitly out of scope this round.
            if dest_rel not in missing_assets:
                missing_assets.append(dest_rel)
        else:
            # Binary non-asset files are not expected from these roots.
            out_of_domain.append(dest_rel + " (binary, not restored by this tool)")

    after = tree_fingerprint(recovered)
    return {
        "closure_size": len(closure),
        "restored": sorted(restored),
        "skipped_existing": sorted(skipped_existing),
        "out_of_domain": sorted(set(out_of_domain)),
        "missing_assets_reported_only": sorted(set(missing_assets)),
        "recovered_unmodified": before == after,
        "dry_run": dry_run,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--recovered", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    recovered = (args.recovered or (root / "04_recovered")).resolve()
    product = (args.product or (root / "product")).resolve()
    out = (args.out or (root / "migration" / "conversion" / "p3_asset_restore.json")).resolve()

    result = restore(recovered, product, dry_run=args.dry_run)
    report = {
        "schema_version": 1,
        "task": TASK,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "recovered_root": "04_recovered",
        "product_dir": "product",
        "write_domain": list(ALLOWED_DEST_PREFIXES),
        "roots": list(RESTORE_ROOTS),
        **result,
        "notes": [
            "Only files missing from product/ are written; existing conversions are never overwritten.",
            "format=2->3 conversion via scripts/migration/menu_convert.py rules; .import/.uid never copied.",
            "Missing binary assets (.aseprite/.png/.wav) stay out of scope and are reported only.",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "restored": len(result["restored"]),
        "skipped_existing": len(result["skipped_existing"]),
        "out_of_domain": len(result["out_of_domain"]),
        "recovered_unmodified": result["recovered_unmodified"],
        "dry_run": result["dry_run"],
    }, ensure_ascii=False))
    for rel in result["restored"]:
        print(f"  restored: {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
