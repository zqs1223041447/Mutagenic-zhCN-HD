#!/usr/bin/env python3
"""P1-WAVE-G: convert the Skills surface into product/scenes/Skills/** and
product/sprites/skills/**.

Never writes 03_raw/** or 04_recovered/**. Only two source groups are copied
into product: Scenes/Skills/** (as product/scenes/Skills/**) and
sprites/skills/** (binary verbatim as product/sprites/skills/**).
Scenes/Skills/GenericSkill.gd was already migrated in Wave E and stays out of
this batch via the default exclude list. Any destination that already exists
is never overwritten; it is recorded in skipped_existing instead.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from boot_convert import convert_gdscript, residual_script_blockers, tree_fingerprint  # type: ignore
from menu_convert import convert_scene_text, product_rel, rewrite_scenes_case  # type: ignore

SKILL_SCENE_ROOT = "Scenes/Skills"
SKILL_SPRITE_ROOT = "sprites/skills"
DEFAULT_EXCLUDE = ("Scenes/Skills/GenericSkill.gd",)

_TEXT_SUFFIXES = {".tscn", ".tres"}
_SKIP_SUFFIXES = {".import", ".uid"}


def _normalize_excludes(exclude: Iterable[str] | None) -> set[str]:
    entries: set[str] = set()
    for item in exclude or ():
        rel = str(item).replace("\\", "/").strip("/")
        if rel:
            entries.add(rel)
    return entries


def _is_excluded(rel: str, excludes: set[str]) -> bool:
    for entry in excludes:
        if rel == entry or rel.startswith(entry + "/"):
            return True
    return False


def copy_and_convert_skills(
    recovered_root: Path,
    product_root: Path,
    exclude: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Copy+convert recovered Scenes/Skills/** and sprites/skills/** into product.

    .tscn/.tres go through menu_convert.convert_scene_text, .gd through
    boot_convert.convert_gdscript, every other file is copied verbatim.
    Excluded paths (default: Scenes/Skills/GenericSkill.gd, migrated in Wave E)
    never reach product. Destinations that already exist are left untouched and
    reported via skipped_existing. Raises if 04_recovered changed during run.
    """
    recovered_root = Path(recovered_root)
    product_root = Path(product_root)
    before = tree_fingerprint(recovered_root)

    excludes = _normalize_excludes(DEFAULT_EXCLUDE if exclude is None else exclude)
    src_roots = (
        recovered_root / SKILL_SCENE_ROOT,
        recovered_root / SKILL_SPRITE_ROOT,
    )

    copied: list[str] = []
    converted: list[str] = []
    binaries: list[str] = []
    residuals: list[dict[str, Any]] = []
    skipped_existing: list[str] = []
    excluded: list[str] = []

    for src_root in src_roots:
        if not src_root.is_dir():
            continue
        for path in sorted(p for p in src_root.rglob("*") if p.is_file()):
            rel = path.relative_to(recovered_root).as_posix()
            dest_rel = product_rel(rel)
            dst = product_root / dest_rel
            if _is_excluded(rel, excludes):
                excluded.append(rel)
                if dst.is_file():
                    skipped_existing.append(dest_rel)
                continue
            if dst.is_file():
                skipped_existing.append(dest_rel)
                continue
            suffix = path.suffix.lower()
            if suffix in _SKIP_SUFFIXES:
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            if suffix in _TEXT_SUFFIXES:
                text = rewrite_scenes_case(convert_scene_text(path.read_text(encoding="utf-8", errors="replace")))
                dst.write_text(text, encoding="utf-8", newline="\n")
                converted.append(dest_rel)
            elif suffix == ".gd":
                text = rewrite_scenes_case(convert_gdscript(path.read_text(encoding="utf-8", errors="replace")))
                dst.write_text(text, encoding="utf-8", newline="\n")
                converted.append(dest_rel)
                residuals.extend(residual_script_blockers(dest_rel, text))
            else:
                shutil.copy2(path, dst)
                binaries.append(dest_rel)
            copied.append(dest_rel)

    after = tree_fingerprint(recovered_root)
    if after != before:
        raise RuntimeError("04_recovered was modified by skill conversion")

    return {
        "files_copied": len(copied),
        "copied": copied,
        "converted_text_files": converted,
        "binaries": binaries,
        "skipped_existing": skipped_existing,
        "excluded": excluded,
        "residuals": residuals,
        "recovered_unmodified": True,
    }


def build_wave_g_report(conversion: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "task": "P1-WAVE-G",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_dir": "product",
        "files_copied": conversion.get("files_copied"),
        "converted_text_files": len(conversion.get("converted_text_files") or []),
        "binaries": len(conversion.get("binaries") or []),
        "skipped_existing": conversion.get("skipped_existing"),
        "skipped_existing_count": len(conversion.get("skipped_existing") or []),
        "excluded_count": len(conversion.get("excluded") or []),
        "excluded": conversion.get("excluded"),
        "residuals": conversion.get("residuals"),
        "recovered_unmodified": conversion.get("recovered_unmodified"),
        "notes": [
            "Wave G converts the recovered Scenes/Skills and sprites/skills trees.",
            "Scenes/Skills/GenericSkill.gd is excluded (already migrated in Wave E).",
            "Existing product files are never overwritten.",
            "04_recovered remains immutable.",
        ],
    }


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--recovered", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--exclude", action="append", default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    root = (args.root or _repo_root_from_here()).resolve()
    recovered = (args.recovered or (root / "04_recovered")).resolve()
    product = (args.product or (root / "product")).resolve()
    out = (args.out or (root / "migration" / "conversion" / "wave_g_skills_report.json")).resolve()

    conversion = copy_and_convert_skills(recovered, product, exclude=args.exclude)
    report = build_wave_g_report(conversion)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "task": report["task"],
        "files_copied": report["files_copied"],
        "converted_text_files": report["converted_text_files"],
        "binaries": report["binaries"],
        "skipped_existing_count": report["skipped_existing_count"],
        "excluded_count": report["excluded_count"],
        "recovered_unmodified": report["recovered_unmodified"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
