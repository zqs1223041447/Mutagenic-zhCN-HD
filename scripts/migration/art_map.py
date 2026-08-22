#!/usr/bin/env python3
"""P4 art acquisition §4-§6 - semantic mapping, placeholders and library build.

Consumes the missing-reference inventory produced by art_scan.py plus the
acquired free packs in runtime/p4_art_downloads/, and builds:

    product/sprites/_acquired/<pack>/   acquired pack stock (+ SOURCE.txt)
    product/sprites/_acquired/ATTRIBUTION.md
    product/sprites/_mapped/<bucket>/   canonical renamed assets (OWN_REMAP +
                                        pack matches); WIRE points here
    product/sprites/_placeholders/<bucket>/  generated stand-in PNGs
    migration/inventory/p4_art_mapping.json  policy + entries[] + coverage
    migration/inventory/p4_art_needs_manual_download.json

Resolution order per missing image reference:
    OWN_REMAP   same-stem .png in product/sprites > 04_recovered/sprites >
                03_raw/sprites
    MAPPED      keyword match against the game-icons.net index (CC BY 3.0)
    PLACEHOLDER generated solid-color + border PNG (pure python, no deps)

Aseprite/PNG twin references of the same asset share one mapped file.
Non-image gaps (.tscn scenes, audio, legacy import refs) are recorded as
PLACEHOLDER entries without files - they are not art assets.

Usage:
    python scripts/migration/art_map.py [--inventory PATH] [--downloads DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import sys
import zipfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

TASK = "P4-ART-MAP"

POLICY = {
    "ART_SOURCE_POLICY": "OWN_RECOVERED_PNG+APPROVED_FREE_PACKS",
    "ASEPRITE_SOURCES": "PERMANENTLY_WAIVED",
    "POE_CDN_ART": "NOT_USED_AS_GAME_STOCK",
}

BUCKET_COLORS = {
    "skills": (106, 79, 191),
    "status": (63, 163, 77),
    "affixes": (200, 162, 39),
    "equipment": (176, 101, 58),
    "items": (79, 134, 192),
    "ui": (154, 160, 166),
    "actors": (200, 80, 80),
    "tiles": (91, 140, 90),
    "vfx": (176, 95, 200),
    "other": (128, 128, 128),
}

STOPWORDS = {"default", "small", "large", "icon", "new", "sprite", "effect"}

MIN_SCORE = 12

# bucket-aware deny list: token must match as word boundary in icon name
BUCKET_DENY: dict[str, set[str]] = {
    "actors": {"orb", "gauge", "leaf", "ruins"},
    "tiles": {"orb", "gauge", "leaf", "ruins"},
}

NON_IMAGE_NOTES = {
    ".tscn": "scene reference gap - owned by scene/WIRE batch, not an art asset",
    ".wav": "audio asset - visual placeholder not applicable",
    ".ogg": "audio asset - visual placeholder not applicable",
    ".stex": "legacy G3 import-cache reference - WIRE should repoint to source texture",
}

NEEDS_MANUAL = [
    {
        "pack": "frosty-rabbid RPG Ability Icons (CC0)",
        "url": "https://frosty-rabbid.itch.io/rpg-ability-icons",
        "url_verified": True,
        "reason": "downloaded via token flow to runtime/p4_art_downloads/frosty-rabbid/ (100 icons 24x24 CC0, v1.2.1 118kB, 103 entries)",
        "purpose": "skill icon alternatives for the skills bucket",
    },
    {
        "pack": "v-ktor RPG Skill Icons (CC0)",
        "url": "https://v-ktor.itch.io/rpg-skill-icons",
        "url_verified": True,
        "reason": "downloaded via token flow to runtime/p4_art_downloads/v-ktor/ (80 icons 64/128 CC0, icons64 614kB + icons128 1855kB)",
        "purpose": "magic/skill icon alternatives for the skills bucket",
    },
    {
        "pack": "kurai7 FREE RPG Skill Icons 16x16 (free commercial, no resell)",
        "url": "https://kurai7.itch.io/40-free-pixel-rpg-skill-icons-16x16-gui-and-status-icons",
        "url_verified": True,
        "reason": "free fallback for paid kurai7 Pack (https://kurai7.itch.io/rpg-skill-icons is paid $3.19); downloaded to runtime/p4_art_downloads/kurai7-free/ (48 icons 16x16 + 32x32)",
        "purpose": "general pixel-art stock for skills/status buckets",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- minimal PNG writer (no third-party deps) --------------------------------
def write_png(path: Path, width: int, height: int,
              fill: tuple[int, int, int], border: tuple[int, int, int],
              border_px: int = 2) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    rows = []
    for y in range(height):
        row = bytearray(b"\x00")
        for x in range(width):
            edge = x < border_px or y < border_px or x >= width - border_px \
                or y >= height - border_px
            row += bytes(border if edge else fill)
        rows.append(bytes(row))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(b"".join(rows), 9))
           + chunk(b"IEND", b""))
    path.write_bytes(png)


def placeholder_colors(bucket: str, stem: str):
    base = BUCKET_COLORS.get(bucket, BUCKET_COLORS["other"])
    digest = hashlib.md5(stem.encode("utf-8")).digest()
    jitter = tuple((digest[i] % 41) - 20 for i in range(3))  # -20..+20
    fill = tuple(max(0, min(255, c + j)) for c, j in zip(base, jitter))
    border = tuple(max(0, min(255, int(c * 0.45))) for c in base)
    return fill, border


# --- matching -----------------------------------------------------------------
def tokenize(stem: str) -> list[str]:
    tokens = [t for t in stem.lower().replace("-", "_").split("_") if t]
    return [t for t in tokens if t not in STOPWORDS]


def match_score(stem: str, tokens: list[str], icon_name: str) -> int:
    """Higher is better; 0 means no match. Word-boundary matching."""
    name = icon_name.lower().replace("-", "_")
    if name == stem.lower():
        return 100
    if not tokens:
        return 0
    name_tokens = name.split("_")
    hits = [t for t in tokens if t in name_tokens]
    if not hits:
        return 0
    score = sum(len(t) for t in hits)
    if len(hits) == len(tokens):
        score += 10 * len(tokens)
    return score


class GameIconsIndex:
    """Name -> zip member index over the game-icons.net archive."""

    def __init__(self, zip_path: Path):
        self.zip_path = zip_path
        self.archive = zipfile.ZipFile(zip_path)
        self.by_name: dict[str, list[dict]] = {}
        for info in self.archive.infolist():
            name = info.filename
            if not name.endswith(".png"):
                continue
            parts = name.split("/")
            if len(parts) < 5 or parts[0] != "icons":
                continue
            author, icon = parts[-2], parts[-1][:-4]
            key = icon.lower()
            self.by_name.setdefault(key, []).append(
                {"zip_path": name, "author": author, "icon": icon})

    def best(self, stem: str, tokens: list[str], bucket: str = "") -> dict | None:
        candidates: list[tuple[int, str, dict]] = []
        deny = BUCKET_DENY.get(bucket, set())
        for key, entries in self.by_name.items():
            for entry in entries:
                # bucket-aware deny: skip icon if its name tokens contain denied word
                if deny:
                    icon_name_tokens = entry["icon"].lower().replace("-", "_").split("_")
                    if any(d in icon_name_tokens for d in deny):
                        continue
                score = match_score(stem, tokens, entry["icon"])
                if score < MIN_SCORE:
                    continue
                # full-hit mandatory
                if tokens:
                    name_tokens = entry["icon"].lower().replace("-", "_").split("_")
                    hits = [t for t in tokens if t in name_tokens]
                    # exact stem match already scored 100; otherwise require all tokens
                    if stem.lower() != entry["icon"].lower().replace("-", "_"):
                        if len(hits) != len(tokens):
                            continue
                if score > 0:
                    candidates.append((score, entry["icon"], entry))
        if not candidates:
            return None
        candidates.sort(key=lambda c: (-c[0], len(c[1]), c[1]))
        return candidates[0][2]

    def extract(self, entry: dict, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self.archive.open(entry["zip_path"]) as src, \
                open(dest, "wb") as dst:
            shutil.copyfileobj(src, dst)


# --- main mapping -------------------------------------------------------------
def build(inventory_path: Path, downloads: Path, product: Path,
          repo_root: Path) -> tuple[dict, list[Path]]:
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    items = inventory["items"]

    sprites = product / "sprites"
    acquired = sprites / "_acquired"
    mapped = sprites / "_mapped"
    placeholders = sprites / "_placeholders"
    for d in (acquired, mapped, placeholders):
        d.mkdir(parents=True, exist_ok=True)

    # own-source stem index (priority order matters)
    own_roots = [
        ("product", product / "sprites"),
        ("04_recovered", repo_root / "04_recovered" / "sprites"),
        ("03_raw", repo_root / "03_raw" / "sprites"),
    ]
    own_index: dict[str, list[dict]] = {}
    own_output_dirs = ("_mapped", "_placeholders", "_acquired")
    for origin, base in own_roots:
        if not base.is_dir():
            continue
        for png in base.rglob("*.png"):
            rel_parts = png.relative_to(base).parts
            if any(part in own_output_dirs for part in rel_parts):
                continue  # never index our own outputs
            own_index.setdefault(png.stem.lower(), []).append(
                {"origin": origin, "path": png})

    gi_zip = downloads / "game-icons.net.png.zip"
    gi_index = GameIconsIndex(gi_zip) if gi_zip.is_file() else None

    entries: list[dict] = []
    resolved_keys: dict[tuple[str, str], dict] = {}
    gi_used: dict[str, set[str]] = {}
    counts = {"OWN_REMAP": 0, "MAPPED": 0, "PLACEHOLDER": 0}

    # deterministic processing: png twins before aseprite twins
    ordered = sorted(items, key=lambda i: (
        i["category"], Path(i["missing_ref"][6:]).stem.lower(),
        i["expected_suffix"] != ".png"))

    for item in ordered:
        ref = item["missing_ref"]
        rel = ref[len("res://"):]
        suffix = item["expected_suffix"]
        bucket = item["category"]
        stem = Path(rel).stem
        entry = {
            "missing_ref": ref,
            "expected_suffix": suffix,
            "category": bucket,
            "bucket": bucket,
            "status": None,
            "mapped_path": None,
            "source": None,
            "license": None,
            "author": None,
            "note": "",
        }

        if suffix not in (".png", ".aseprite"):
            entry["status"] = "PLACEHOLDER"
            entry["note"] = NON_IMAGE_NOTES.get(
                suffix, "non-image reference - no art placeholder applicable")
            if "%s" in ref:
                entry["note"] = "runtime-generated path template - not a static asset"
            counts["PLACEHOLDER"] += 1
            entries.append(entry)
            continue

        key = (bucket, stem.lower())
        shared = resolved_keys.get(key)
        if shared:
            entry.update({
                "status": shared["status"],
                "mapped_path": shared["mapped_path"],
                "source": shared["source"],
                "license": shared["license"],
                "author": shared["author"],
                "note": f"shares mapped file with {shared['missing_ref']}",
            })
            counts[entry["status"]] += 1
            entries.append(entry)
            continue

        # 1) OWN_REMAP
        own_hits = own_index.get(stem.lower())
        if own_hits:
            source = own_hits[0]
            target = mapped / bucket / f"{stem}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source["path"], target)
            entry.update({
                "status": "OWN_REMAP",
                "mapped_path": f"res://sprites/_mapped/{bucket}/{stem}.png",
                "source": source["path"].as_posix(),
                "license": "OWN_RECOVERED_PNG (in-tree asset)",
                "author": "-",
            })
        # 2) MAPPED from game-icons
        elif gi_index is not None:
            tokens = tokenize(stem)
            best = gi_index.best(stem, tokens, bucket)
            if best is not None:
                acq_dir = acquired / "game-icons.net" / "icons" / best["author"]
                acq_file = acq_dir / f"{best['icon']}.png"
                gi_index.extract(best, acq_file)
                target = mapped / bucket / f"{stem}.png"
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(acq_file, target)
                gi_used.setdefault(best["author"], set()).add(best["icon"])
                entry.update({
                    "status": "MAPPED",
                    "mapped_path": f"res://sprites/_mapped/{bucket}/{stem}.png",
                    "source": f"game-icons.net:{best['author']}/{best['icon']}",
                    "license": "CC BY 3.0",
                    "author": best["author"],
                })
        # 3) PLACEHOLDER
        if entry["status"] is None:
            ph_dir = placeholders / bucket
            ph_dir.mkdir(parents=True, exist_ok=True)
            ph_file = ph_dir / f"{stem}.png"
            fill, border = placeholder_colors(bucket, stem)
            write_png(ph_file, 64, 64, fill, border)
            entry.update({
                "status": "PLACEHOLDER",
                "mapped_path": f"res://sprites/_placeholders/{bucket}/{stem}.png",
                "source": None,
                "license": "generated-placeholder",
                "author": "-",
                "note": "no own remap or pack match found; generated stand-in",
            })
        resolved_keys[key] = entry
        counts[entry["status"]] += 1
        entries.append(entry)

    # --- install kenney packs verbatim (tile-sheet stock for WIRE) ----------
    installed_packs: list[Path] = []
    kenney_meta = [
        ("kenney_tiny-dungeon", "https://kenney.nl/assets/tiny-dungeon",
         "CC0 1.0 (public domain)", "Kenney"),
        ("kenney_micro-roguelike", "https://kenney.nl/assets/micro-roguelike",
         "CC0 1.0 (public domain)", "Kenney"),
    ]
    today = utc_now()[:10]
    for pack_id, url, license_line, author in kenney_meta:
        zip_path = downloads / f"{pack_id}.zip"
        if not zip_path.is_file():
            continue
        pack_dir = acquired / pack_id
        pack_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(pack_dir)
        source_lines = [
            f"pack: {pack_id}",
            f"url: {url}",
            f"license: {license_line}",
            f"author: {author}",
            f"downloaded_at: {today}",
            "extracted: full pack (tile-sheet stock; reserved for WIRE batch)",
            f"local_archive: runtime/p4_art_downloads/{pack_id}.zip",
        ]
        (pack_dir / "SOURCE.txt").write_text("\n".join(source_lines) + "\n",
                                             encoding="utf-8")
        installed_packs.append(pack_dir)

    # --- itch packs: frosty-rabbid / v-ktor / kurai7-free (downloaded via token flow) --
    itch_packs = [
        ("frosty-rabbid_rpg-ability-icons",
         "https://frosty-rabbid.itch.io/rpg-ability-icons",
         "CC0 1.0 (public domain)", "frosty_rabbid",
         "frosty-rabbid/rpg icon collection v1.2.1.zip"),
        ("v-ktor_rpg-skill-icons",
         "https://v-ktor.itch.io/rpg-skill-icons",
         "CC0 1.0 (public domain)", "Viktor (v-ktor)",
         "v-ktor/icons64.zip"),  # also icons128.zip handled separately
        ("kurai7_free-rpg-skill-icons",
         "https://kurai7.itch.io/40-free-pixel-rpg-skill-icons-16x16-gui-and-status-icons",
         "Free commercial (no resell, credit not required)", "KURAI (kurai7)",
         "kurai7-free/FREE RPG SKILL ICONS 16x16.zip"),
    ]
    for pack_id, url, license_line, author, rel_zip in itch_packs:
        zip_path = downloads / rel_zip
        if not zip_path.is_file():
            continue
        pack_dir = acquired / pack_id
        pack_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(pack_dir)
        # v-ktor has second zip; handle
        if pack_id == "v-ktor_rpg-skill-icons":
            zip2 = downloads / "v-ktor/icons128.zip"
            if zip2.is_file():
                with zipfile.ZipFile(zip2) as zf:
                    zf.extractall(pack_dir / "128")
        if pack_id == "kurai7_free-rpg-skill-icons":
            zip2 = downloads / "kurai7-free/FREE RPG SKILL ICONS 32x32.zip"
            if zip2.is_file():
                with zipfile.ZipFile(zip2) as zf:
                    zf.extractall(pack_dir / "32x32")
        source_lines = [
            f"pack: {pack_id}",
            f"url: {url}",
            f"license: {license_line}",
            f"author: {author}",
            f"downloaded_at: {today}",
            "extracted: full pack (skill icon stock; reserved for WIRE batch)",
            f"local_archive: runtime/p4_art_downloads/{rel_zip}",
        ]
        (pack_dir / "SOURCE.txt").write_text("\n".join(source_lines) + "\n", encoding="utf-8")
        installed_packs.append(pack_dir)

    # --- game-icons SOURCE.txt (used subset) --------------------------------
    gi_dir = acquired / "game-icons.net"
    if gi_used:
        authors_used = sorted(gi_used)
        used_count = sum(len(v) for v in gi_used.values())
        gi_dir.mkdir(parents=True, exist_ok=True)
        source_lines = [
            "pack: game-icons.net",
            "url: https://game-icons.net/",
            "archive: https://game-icons.net/archives/png/zip/000000/ffffff/game-icons.net.png.zip",
            "license: CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/)",
            f"downloaded_at: {today}",
            f"extracted: used subset only ({used_count} of 4133 icons); "
            "full archive retained at runtime/p4_art_downloads/game-icons.net.png.zip",
            f"authors_in_subset: {', '.join(authors_used)}",
        ]
        (gi_dir / "SOURCE.txt").write_text("\n".join(source_lines) + "\n",
                                           encoding="utf-8")

    # --- ATTRIBUTION.md ------------------------------------------------------
    attr = ["# Art Attribution (P4)", "",
            f"Generated: {utc_now()}", ""]
    if gi_used:
        attr += [
            "## game-icons.net", "",
            "- URL: https://game-icons.net/",
            "- License: CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/)",
            "- Local: `product/sprites/_acquired/game-icons.net/icons/**`",
            "- Used icons by author:",
            ""]
        for author in sorted(gi_used):
            attr.append(f"  - {author}: {len(gi_used[author])} icon(s) "
                        f"({', '.join(sorted(gi_used[author]))})")
        attr.append("")
    attr += ["## Kenney Tiny Dungeon", "",
             "- URL: https://kenney.nl/assets/tiny-dungeon",
             "- License: CC0 1.0 (public domain)",
             "- Local: `product/sprites/_acquired/kenney_tiny-dungeon/`", ""]
    attr += ["## Kenney Micro Roguelike", "",
             "- URL: https://kenney.nl/assets/micro-roguelike",
             "- License: CC0 1.0 (public domain)",
             "- Local: `product/sprites/_acquired/kenney_micro-roguelike/`", ""]
    # --- itch free packs (now downloaded) ---
    if (acquired / "frosty-rabbid_rpg-ability-icons").is_dir():
        attr += ["## frosty-rabbid RPG Ability Icons", "",
                 "- URL: https://frosty-rabbid.itch.io/rpg-ability-icons",
                 "- License: CC0 1.0 (public domain)",
                 "- Local: `product/sprites/_acquired/frosty-rabbid_rpg-ability-icons/`",
                 "- Note: 100 icons 24x24, v1.2.1 (115kB)", ""]
    if (acquired / "v-ktor_rpg-skill-icons").is_dir():
        attr += ["## v-ktor RPG Skill Icons", "",
                 "- URL: https://v-ktor.itch.io/rpg-skill-icons",
                 "- License: CC0 1.0 (public domain)",
                 "- Local: `product/sprites/_acquired/v-ktor_rpg-skill-icons/` (+128 subdir)",
                 "- Note: 80 icons, 64px (614kB) + 128px (1855kB)", ""]
    if (acquired / "kurai7_free-rpg-skill-icons").is_dir():
        attr += ["## kurai7 FREE RPG Skill Icons", "",
                 "- URL: https://kurai7.itch.io/40-free-pixel-rpg-skill-icons-16x16-gui-and-status-icons",
                 "- License: Free commercial (no resell, credit not required)",
                 "- Local: `product/sprites/_acquired/kurai7_free-rpg-skill-icons/` (+32x32 subdir)",
                 "- Note: 48 icons 16x16 (13kB) + 32x32 (14kB); paid full pack https://kurai7.itch.io/rpg-skill-icons ($3.19) NOT used", ""]
    attr += ["## Own recovered PNG remaps", "",
             "- Sources: `04_recovered/sprites/**`, `product/sprites/**`, "
             "`03_raw/sprites/**` (in-tree assets; license follows repo policy)",
             "- Status in mapping table: OWN_REMAP", ""]
    (acquired / "ATTRIBUTION.md").write_text("\n".join(attr), encoding="utf-8")

    # --- mapping table --------------------------------------------------------
    total_inventory = len(items)
    covered = len(entries)
    mapping = {
        "schema_version": 1,
        "task": TASK,
        "generated_at": utc_now(),
        "policy": POLICY,
        "summary": {
            "inventory_total": total_inventory,
            "own_remap": counts["OWN_REMAP"],
            "mapped": counts["MAPPED"],
            "placeholder": counts["PLACEHOLDER"],
        },
        "coverage": {
            "inventory_total": total_inventory,
            "entries": covered,
            "pct": round(100.0 * covered / total_inventory, 2) if total_inventory else 100.0,
        },
        "entries": entries,
    }
    return mapping, installed_packs


def write_needs_manual(out_path: Path) -> None:
    doc = {
        "schema_version": 1,
        "task": "P4-ART-FETCH",
        "generated_at": utc_now(),
        "policy_note": "all verified and downloaded via token flow (see product/sprites/_acquired/*/SOURCE.txt and runtime/p4_art_downloads/*)",
        "items": NEEDS_MANUAL,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inventory", type=Path, default=None)
    ap.add_argument("--downloads", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--needs-manual-out", dest="needs_manual_out", type=Path,
                    default=None)
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    inventory = (args.inventory or (repo_root / "migration" / "inventory"
                                    / "p4_art_missing_inventory.json")).resolve()
    downloads = (args.downloads or (repo_root / "runtime"
                                    / "p4_art_downloads")).resolve()
    product = (args.product or (repo_root / "product")).resolve()
    out = (args.out or (repo_root / "migration" / "inventory"
                        / "p4_art_mapping.json")).resolve()
    needs_out = (args.needs_manual_out or (repo_root / "migration" / "inventory"
                                           / "p4_art_needs_manual_download.json")).resolve()

    mapping, _ = build(inventory, downloads, product, repo_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    write_needs_manual(needs_out)

    print(json.dumps({
        "wrote": str(out),
        "summary": mapping["summary"],
        "coverage_pct": mapping["coverage"]["pct"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
