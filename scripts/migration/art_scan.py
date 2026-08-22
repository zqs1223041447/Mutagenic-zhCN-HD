#!/usr/bin/env python3
"""P4 art acquisition §3 - missing-reference inventory scanner.

Scans every res:// resource reference inside product/ (.tscn / .tres / .gd),
checks existence against the product tree, and emits a machine-readable
inventory of missing references with referrers and semantic categories.

Only reads product/**; writes nothing outside --out.

Usage:
    python scripts/migration/art_scan.py [--root PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TASK = "P4-ART-SCAN"

# Quoted res:// references cover all three carriers:
#   .tscn/.tres : [ext_resource ... path="res://..."]
#   .gd         : preload("res://...") / load("res://...")
REF_RE = re.compile(r'"(res://[^"\n]+)"')

# Category rules, first match wins. Keys align 1:1 with the _mapped/ buckets
# defined by the P4 plan (skills/status/affixes/equipment/items/ui/actors/
# tiles/vfx); everything else falls back to "other".
CATEGORY_RULES = [
    ("skills", ("sprites/skills/", "sprites/projectiles/", "scenes/skills/",
                "scenes/projectiles/")),
    ("status", ("sprites/aura_effects/", "sprites/effects/",
                "sprites/status_effects/", "sprites/gui/passives")),
    ("equipment", ("sprites/uniques/", "sprites/equipment/")),
    ("items", ("sprites/drops/", "sprites/items/", "sprites/pickups/")),
    ("actors", ("sprites/player/", "sprites/monsters/")),
    ("tiles", ("sprites/environment/", "sprites/tiles/", "sprites/worldmap/",
               "sprites/hideout/")),
    ("vfx", ("sprites/particles/", "sprites/fx/", "sprites/shaders/")),
    ("ui", ("sprites/gui/",)),
]


def classify(ref_rel: str) -> str:
    p = ref_rel.lower()
    for category, prefixes in CATEGORY_RULES:
        if any(p.startswith(prefix) for prefix in prefixes):
            return category
    return "other"


def extract_refs(text: str) -> list[str]:
    refs = []
    for match in REF_RE.finditer(text):
        ref = match.group(1).strip()
        # uid:// style and directory-ish refs are not file references
        if ref.startswith("res://uid") or ref.endswith("/"):
            continue
        refs.append(ref)
    return refs


def scan(root: Path) -> dict:
    referrers: dict[str, list[str]] = {}
    total_refs = 0

    sources = sorted(
        list(root.rglob("*.tscn"))
        + list(root.rglob("*.tres"))
        + list(root.rglob("*.gd"))
    )
    for path in sources:
        rel = path.relative_to(root.parent).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for ref in extract_refs(text):
            total_refs += 1
            referrers.setdefault(ref, [])
            if rel not in referrers[ref]:
                referrers[ref].append(rel)

    missing_items = []
    suffix_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()

    for ref in sorted(referrers):
        rel_path = ref[len("res://"):]
        if (root / rel_path).exists():
            continue
        suffix = Path(rel_path).suffix.lower() or "(none)"
        category = classify(rel_path)
        suffix_counter[suffix] += 1
        category_counter[category] += 1
        missing_items.append({
            "missing_ref": ref,
            "expected_suffix": suffix,
            "category": category,
            "referrers": sorted(referrers[ref]),
            "referrer_count": len(referrers[ref]),
        })

    return {
        "schema_version": 1,
        "task": TASK,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scan_root": "product",
        "files_scanned": len(sources),
        "totals": {
            "references_total": total_refs,
            "references_unique": len(referrers),
            "missing_unique": len(missing_items),
        },
        "missing_by_suffix": dict(suffix_counter.most_common()),
        "missing_by_category": dict(category_counter.most_common()),
        "items": missing_items,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None,
                    help="product dir (default: <repo>/product)")
    ap.add_argument("--out", type=Path, default=None,
                    help="inventory JSON path "
                         "(default: migration/inventory/p4_art_missing_inventory.json)")
    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    root = (args.root or (repo_root / "product")).resolve()
    out = (args.out or (repo_root / "migration" / "inventory"
                        / "p4_art_missing_inventory.json")).resolve()

    report = scan(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")

    totals = report["totals"]
    print(json.dumps({
        "wrote": str(out),
        "files_scanned": report["files_scanned"],
        "references_total": totals["references_total"],
        "references_unique": totals["references_unique"],
        "missing_unique": totals["missing_unique"],
        "by_category": report["missing_by_category"],
        "by_suffix": report["missing_by_suffix"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
