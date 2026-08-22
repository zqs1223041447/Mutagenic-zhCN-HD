#!/usr/bin/env python3
"""P1-WAVE-F: convert the Scenes/Mobs/** tree into product/scenes/Mobs/**.

Never writes 03_raw/** or 04_recovered/**. Only files under Scenes/Mobs/**
are written into product (as product/scenes/Mobs/**); anything already in
product outside this batch's copy range (in particular scenes/Player/Player.gd)
is never touched. An optional exclude list of recovered-relative paths keeps
named mobs (e.g. Scenes/Mobs/Bosses/X.tscn) out of product entirely.
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

MOB_ROOT = "Scenes/Mobs"


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


def copy_and_convert_mobs(
    recovered_root: Path,
    product_root: Path,
    exclude: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Copy+convert recovered Scenes/Mobs/** into product/scenes/Mobs/**.

    .tscn goes through menu_convert.convert_scene_text, .gd through
    boot_convert.convert_gdscript, every other file is copied verbatim.
    Raises if 04_recovered changed during the run.
    """
    recovered_root = Path(recovered_root)
    product_root = Path(product_root)
    before = tree_fingerprint(recovered_root)

    excludes = _normalize_excludes(exclude)
    src_root = recovered_root / MOB_ROOT

    copied: list[str] = []
    converted: list[str] = []
    binaries: list[str] = []
    residuals: list[dict[str, Any]] = []
    excluded: list[str] = []

    if src_root.is_dir():
        for path in sorted(p for p in src_root.rglob("*") if p.is_file()):
            rel = path.relative_to(recovered_root).as_posix()
            if _is_excluded(rel, excludes):
                excluded.append(rel)
                continue
            dest_rel = product_rel(rel)
            dst = product_root / dest_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            suffix = path.suffix.lower()
            if suffix == ".tscn":
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
        raise RuntimeError("04_recovered was modified by mob conversion")

    return {
        "files_copied": len(copied),
        "copied": copied,
        "converted_text_files": converted,
        "binaries": binaries,
        "residuals": residuals,
        "excluded": excluded,
        "recovered_unmodified": True,
    }


def build_wave_f_report(conversion: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "task": "P1-WAVE-F",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_dir": "product",
        "files_copied": conversion.get("files_copied"),
        "converted_text_files": len(conversion.get("converted_text_files") or []),
        "binaries": len(conversion.get("binaries") or []),
        "excluded_count": len(conversion.get("excluded") or []),
        "excluded": conversion.get("excluded"),
        "residuals": conversion.get("residuals"),
        "recovered_unmodified": conversion.get("recovered_unmodified"),
        "notes": [
            "Wave F converts the recovered Scenes/Mobs tree.",
            "Excluded paths never reach product/scenes/Mobs.",
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
    out = (args.out or (root / "migration" / "conversion" / "wave_f_mobs_report.json")).resolve()

    conversion = copy_and_convert_mobs(recovered, product, exclude=args.exclude or ())
    report = build_wave_f_report(conversion)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "task": report["task"],
        "files_copied": report["files_copied"],
        "converted_text_files": report["converted_text_files"],
        "binaries": report["binaries"],
        "excluded_count": report["excluded_count"],
        "recovered_unmodified": report["recovered_unmodified"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
