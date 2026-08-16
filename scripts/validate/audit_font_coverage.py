#!/usr/bin/env python3
"""Audit font glyph coverage and provenance for a controlled localization build.

This is an evidence-producing read-only audit.  It never modifies 03_raw,
04_recovered, or any font directory.  Coverage is reported per font file and
per requested code point; missing license evidence is kept explicit rather
than inferred from a filename.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from fontTools.ttLib import TTFont


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def names(font: TTFont) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {
        "family": [],
        "subfamily": [],
        "full": [],
        "version": [],
        "description": [],
        "copyright": [],
        "trademark": [],
        "manufacturer": [],
        "designer": [],
        "vendor_url": [],
        "designer_url": [],
        "license_description": [],
        "license_info_url": [],
    }
    ids = {
        0: "copyright",
        1: "family",
        2: "subfamily",
        4: "full",
        5: "version",
        7: "trademark",
        8: "manufacturer",
        9: "designer",
        10: "description",
        11: "vendor_url",
        12: "designer_url",
        13: "license_description",
        14: "license_info_url",
    }
    for record in font["name"].names:
        key = ids.get(record.nameID)
        if key is None:
            continue
        try:
            value = record.toUnicode()
        except Exception:
            continue
        if value and value not in result[key]:
            result[key].append(value)
    return result


def audit_file(path: Path, required: list[str], license_paths: list[Path]) -> dict:
    font = TTFont(path, lazy=True)
    cmap: set[int] = set()
    for table in font["cmap"].tables:
        cmap.update(table.cmap.keys())
    required_map = {char: ord(char) in cmap for char in required}
    metadata = names(font)
    fs_type = font["OS/2"].fsType if "OS/2" in font else None
    font_license_metadata = bool(metadata["license_description"] or metadata["license_info_url"])
    license_evidence = [
        str(candidate.resolve())
        for candidate in license_paths
        if candidate.is_file()
    ]
    return {
        "path": str(path.resolve()),
        "size": path.stat().st_size,
        "sha256": sha256(path),
        "family_names": metadata,
        "os2_fs_type": fs_type,
        "has_license_metadata": font_license_metadata,
        "cmap_codepoint_count": len(cmap),
        "required_glyphs": required_map,
        "missing_required_glyphs": [char for char, present in required_map.items() if not present],
        "license_evidence": license_evidence,
        "license_status": "PASS" if license_evidence else "UNKNOWN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", action="append", type=Path, default=[])
    parser.add_argument("--font", action="append", type=Path, default=[])
    parser.add_argument("--required-text", default="开始游戏")
    parser.add_argument("--license-root", action="append", type=Path, default=[])
    parser.add_argument("--license-file", action="append", type=Path, default=[])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if not args.font_dir and not args.font:
        parser.error("provide at least one --font-dir or --font")

    required = list(dict.fromkeys(args.required_text))
    license_names = {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE", "OFL.txt"}
    license_paths: list[Path] = []
    for root in args.license_root:
        if root.is_file() and root.name in license_names:
            license_paths.append(root)
        elif root.is_dir():
            license_paths.extend(
                p for p in root.rglob("*") if p.is_file() and p.name in license_names
            )
    for license_file in args.license_file:
        if license_file.is_file():
            license_paths.append(license_file)
        else:
            missing_dirs.append(str(license_file.resolve()))

    files: list[Path] = []
    missing_dirs: list[str] = []
    for directory in args.font_dir:
        if not directory.is_dir():
            missing_dirs.append(str(directory.resolve()))
            continue
        files.extend(sorted(p for p in directory.iterdir() if p.suffix.lower() in {".ttf", ".otf"}))
    for font_file in args.font:
        if not font_file.is_file():
            missing_dirs.append(str(font_file.resolve()))
            continue
        if font_file.suffix.lower() not in {".ttf", ".otf"}:
            missing_dirs.append(str(font_file.resolve()))
            continue
        files.append(font_file)

    audits = [audit_file(path, required, license_paths) for path in files]
    coverage_ok = bool(audits) and all(not item["missing_required_glyphs"] for item in audits)
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "font_directories": [str(path.resolve()) for path in args.font_dir],
        "font_files": [str(path.resolve()) for path in args.font],
        "required_text": args.required_text,
        "required_codepoints": {char: f"U+{ord(char):04X}" for char in required},
        "missing_directories": missing_dirs,
        "license_search_roots": [str(path.resolve()) for path in args.license_root],
        "license_files": [str(path.resolve()) for path in args.license_file],
        "license_evidence": [str(path.resolve()) for path in license_paths],
        "fonts": audits,
        "font_count": len(audits),
        "coverage_gate": "PASS" if coverage_ok else "FAIL",
        "license_gate": "PASS" if license_paths else "UNKNOWN",
        "verdict": "PASS" if coverage_ok and not missing_dirs else "FAIL",
        "proves": "the audited font files have or lack the requested glyphs according to their cmap tables, with hashes and available license evidence recorded",
        "not_proven": "font rendering quality, fallback behavior, layout, clipping, license rights when no evidence file was found, or runtime use by the candidate EXE",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "font_count": report["font_count"],
        "coverage_gate": report["coverage_gate"],
        "license_gate": report["license_gate"],
        "verdict": report["verdict"],
    }, ensure_ascii=False))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
