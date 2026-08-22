#!/usr/bin/env python3
"""P1-WAVE-I: copy+convert Levels assets from 04_recovered into product.

Never writes 03_raw/** or 04_recovered/**. Like equipment_convert this module
hardcodes no source directories: the caller passes the recovered-relative
roots to copy (e.g. ("Scenes/Levels",)) because the concrete level scene
layout is decided by a parallel investigation task and handed over by
the integrator. Within every root the rules are fixed:

- .tscn/.tres go through menu_convert.convert_scene_text +
  menu_convert.rewrite_scenes_case,
- .gd goes through boot_convert.convert_gdscript +
  boot_convert.residual_script_blockers,
- .import/.uid sidecars are never copied (Godot regenerates them),
- anything else is copied verbatim as binary.

Excluded paths never reach product. Destinations that already exist are left
untouched and recorded in skipped_existing. Raises RuntimeError if
04_recovered changed during the run.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any, Iterable

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from boot_convert import convert_gdscript, residual_script_blockers, tree_fingerprint  # type: ignore
from menu_convert import convert_scene_text, product_rel, rewrite_scenes_case  # type: ignore

_TEXT_SUFFIXES = {".tscn", ".tres"}
_SKIP_SUFFIXES = {".import", ".uid"}


def _normalize_roots(recovered_root: Path, roots: Iterable[str]) -> list[Path]:
    normalized: list[Path] = []
    for item in roots or ():
        rel = str(item).replace("\\", "/").strip("/")
        if rel:
            normalized.append(recovered_root / rel)
    return normalized


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


def copy_and_convert_levels(
    recovered_root: Path,
    product_root: Path,
    roots: Iterable[str],
    exclude: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Copy+convert the caller-selected recovered roots into product.

    roots are recovered-relative directories (e.g. ("Scenes/Levels",));
    missing roots are silently ignored so callers can pass a superset.
    Excluded paths (files or directory prefixes) never reach product.
    Destinations that already exist are left untouched and reported via
    skipped_existing. Raises if 04_recovered changed during run.
    """
    recovered_root = Path(recovered_root)
    product_root = Path(product_root)
    before = tree_fingerprint(recovered_root)

    excludes = _normalize_excludes(exclude)
    src_roots = _normalize_roots(recovered_root, roots)

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
        raise RuntimeError("04_recovered was modified by levels conversion")

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
