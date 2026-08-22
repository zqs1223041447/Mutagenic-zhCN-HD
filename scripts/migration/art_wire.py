#!/usr/bin/env python3
"""P4-WIRE - mechanically rewrite missing-art references to mapped assets.

Reads migration/inventory/p4_art_mapping.json and rewrites references inside
product/scenes/** (.tscn/.tres/.gd):

  OWN_REMAP / MAPPED entries  -> res://sprites/_mapped/<bucket>/<stem>.png
  PLACEHOLDER (image) entries -> res://sprites/_placeholders/<bucket>/<stem>.png
  non-image entries           -> registered only, NOT wired (scene/audio gaps)

Type contract handling: .aseprite references are consumed as SpriteFrames
(AnimatedSprite2D.frames).  A raw .png cannot satisfy that, so for every
.aseprite-derived reference the tool generates a single-frame SpriteFrames
wrapper resource under product/sprites/_acquired/generated_spriteframes/
(new files only; existing library files stay untouched) and points the
reference there, preserving type="SpriteFrames".

Idempotent: after a successful run the old paths are gone; re-running
performs zero rewrites.

Usage:
    python scripts/migration/art_wire.py [--mapping PATH] [--product PATH]
                                         [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TASK = "P4-WIRE"

SPRITEFRAMES_TEMPLATE = """[gd_resource type="SpriteFrames" load_steps=2 format=3]

[ext_resource type="Texture2D" path="{png}" id="1"]

[resource]
animations = [{{
"frames": [{{"duration": 1.0, "texture": ExtResource("1")}}],
"loop": true,
"name": &"default",
"speed": 5.0
}}]
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_spriteframes_wrapper(product: Path, png_res: str,
                                bucket: str, stem: str) -> str | None:
    """Create (once) a single-frame SpriteFrames .tres wrapping a mapped PNG.

    Returns the res:// path of the wrapper, or None when the wrapped PNG is
    missing."""
    png_abs = product / png_res[len("res://"):].replace("/", "\\")
    if not png_abs.is_file():
        return None
    wrapper_res = (f"res://sprites/_acquired/generated_spriteframes/"
                   f"{bucket}/{stem}.spriteframes.tres")
    wrapper_abs = product / wrapper_res[len("res://"):].replace("/", "\\")
    if not wrapper_abs.is_file():
        wrapper_abs.parent.mkdir(parents=True, exist_ok=True)
        wrapper_abs.write_text(
            SPRITEFRAMES_TEMPLATE.format(png=png_res), encoding="utf-8")
    return wrapper_res


def build_rewrite_plan(mapping: dict, product: Path) -> tuple[dict, list[dict]]:
    """missing_ref -> {png: str, sfrs: str, status, bucket} plus skip records."""
    plan: dict[str, dict] = {}
    skipped: list[dict] = []
    for entry in mapping["entries"]:
        ref = entry["missing_ref"]
        status = entry["status"]
        mapped_path = entry.get("mapped_path")
        if not mapped_path:
            skipped.append({
                "missing_ref": ref,
                "expected_suffix": entry["expected_suffix"],
                "reason": entry.get("note") or "non-image gap - registered only",
            })
            continue
        png_abs = product / mapped_path[len("res://"):].replace("/", "\\")
        if not png_abs.is_file():
            skipped.append({
                "missing_ref": ref,
                "expected_suffix": entry["expected_suffix"],
                "reason": f"mapped file missing on disk: {mapped_path}",
            })
            continue
        rel = ref[len("res://"):]
        stem = Path(rel).stem
        bucket = entry.get("bucket") or entry["category"]
        plan[ref] = {
            "png": mapped_path,
            "sfrs": ensure_spriteframes_wrapper(product, mapped_path, bucket, stem),
            "status": status,
            "bucket": bucket,
            "stem": stem,
        }
    return plan, skipped


def rewrite_files(product: Path, plan: dict) -> tuple[list[dict], Counter]:
    per_file: list[dict] = []
    by_status: Counter[str] = Counter()
    total_refs = 0

    sources = sorted(list((product / "scenes").rglob("*.tscn"))
                     + list((product / "scenes").rglob("*.tres"))
                     + list((product / "scenes").rglob("*.gd")))
    for path in sources:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        original = text
        file_rewrites = 0
        file_hits: Counter[str] = Counter()

        is_scene_text = path.suffix in (".tscn", ".tres")
        for ref, spec in plan.items():
            if ref not in text:
                continue
            spec = dict(spec)
            spec["ref"] = ref
            if is_scene_text:
                pattern = re_ext_resource(ref)
                new_text, n = pattern.subn(
                    lambda m: rewrite_ext_resource_line(m, spec), text)
            else:
                # gd preload/load: aseprite assumed SpriteFrames usage
                target = spec["png"]
                if ref.lower().endswith(".aseprite") and spec["sfrs"]:
                    target = spec["sfrs"]
                old_token = f'"{ref}"'
                new_token = f'"{target}"'
                n = text.count(old_token)
                new_text = text.replace(old_token, new_token)
            if n:
                text = new_text
                file_rewrites += n
                file_hits[spec["status"]] += n
                by_status[spec["status"]] += n
                total_refs += n

        if file_rewrites:
            path.write_text(text, encoding="utf-8", newline="")
            rel = path.relative_to(product.parent).as_posix()
            per_file.append({
                "file": rel,
                "rewrites": file_rewrites,
                "by_status": dict(file_hits),
            })

    return per_file, by_status


_RE_CACHE: dict[str, "re.Pattern[str]"] = {}


def re_ext_resource(ref: str) -> "re.Pattern[str]":
    """Match the full [ext_resource ...] block that references `ref`."""
    if ref not in _RE_CACHE:
        escaped = re.escape(ref)
        _RE_CACHE[ref] = re.compile(
            r"\[ext_resource\s+(?P<body>[^\]]*" + escaped + r"[^\]]*)\]")
    return _RE_CACHE[ref]


def rewrite_ext_resource_line(match: "re.Match[str]", spec: dict) -> str:
    body = match.group("body")
    type_match = re.search(r'type="([^"]*)"', body)
    rtype = type_match.group(1) if type_match else "Texture2D"
    target = spec["png"]
    if rtype == "SpriteFrames" and spec.get("sfrs"):
        target = spec["sfrs"]
    new_body = body.replace(spec["ref"], target)
    return "[ext_resource " + new_body + "]"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mapping", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    mapping_path = (args.mapping or (repo_root / "migration" / "inventory"
                                     / "p4_art_mapping.json")).resolve()
    product = (args.product or (repo_root / "product")).resolve()
    out = (args.out or (repo_root / "migration" / "conversion"
                        / "p4_wire_report.json")).resolve()

    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    plan, skipped = build_rewrite_plan(mapping, product)
    per_file, by_status = rewrite_files(product, plan)

    report = {
        "schema_version": 1,
        "task": TASK,
        "generated_at": utc_now(),
        "plan_size": len(plan),
        "rewrites": {
            "files_changed": len(per_file),
            "references_rewritten": sum(by_status.values()),
            "by_status": dict(by_status),
        },
        "registered_not_wired": len(skipped),
        "skipped": skipped,
        "per_file": sorted(per_file, key=lambda f: -f["rewrites"]),
        "errors": [],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "plan_size": report["plan_size"],
        "files_changed": report["rewrites"]["files_changed"],
        "references_rewritten": report["rewrites"]["references_rewritten"],
        "by_status": report["rewrites"]["by_status"],
        "registered_not_wired": report["registered_not_wired"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
