#!/usr/bin/env python3
"""NL2MOD core: turn a structured mod intent into a preimage-guarded mod.json.

This is the deterministic "Layer 2" of the NL2MOD framework:
  natural language (AI) -> structured intent (JSON) -> this generator -> mod.json

The AI (orchestrator) is responsible for Layer 1 (parsing user language and
locating the exact file/field via docs/ai/source-map.md + 04_recovered). This
script only validates the intent against the real recovered source and emits a
manifest that the existing build pipeline can consume unchanged.

Usage:
    python scripts/nlmod/nlmod.py --intent intent.json --out mods/<id>/mod.json

intent.json shape:
{
  "id": "mm-monster-speed-skeleton-archer",
  "scope": "human-readable why",
  "patch_type": "CODE_PATCH" | "VALUE_PATCH" | "RESOURCE_PATCH" | "TEXT_PATCH",
  "patches": [
    {
      "path": "Globals/MonsterStats/MonsterStats.gd",
      "classification": "CODE_PATCH",
      "anchor": "string that must appear once (or N times) in the recovered file",
      "old_text": "exact text to replace (must include the value to change)",
      "new_text": "replacement text",
      "expected_occurrences": 1
    }
  ]
}

The generator verifies:
  - anchor appears exactly `expected_occurrences` times in 04_recovered/<path>
  - old_text count == expected_occurrences
  - emits mod.json with preimage_sha256 = sha256 of the WHOLE recovered file
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(r"G:\opencode-Mutageni")
RECOVERED = PROJECT / "04_recovered"
ORIGINAL_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a preimage-guarded mod.json from structured intent")
    ap.add_argument("--intent", type=Path, required=True, help="intent JSON (see module docstring)")
    ap.add_argument("--out", type=Path, required=True, help="output mod.json path")
    ap.add_argument("--base", type=Path, default=RECOVERED, help="recovered source root (default 04_recovered)")
    args = ap.parse_args()

    intent = json.loads(args.intent.read_text(encoding="utf-8"))
    mod_id = intent["id"]
    if args.out.exists():
        raise SystemExit(f"ERROR: refusing to overwrite existing manifest: {args.out}")

    generated = {
        "id": mod_id,
        "version": "0.1.0",
        "patch_type": intent.get("patch_type", "CODE_PATCH"),
        "target_original_sha256": intent.get("target_original_sha256", ORIGINAL_SHA),
        "dependencies": intent.get("dependencies", []),
        "conflicts": intent.get("conflicts", []),
        "scope": intent.get("scope", f"NL2MOD-generated: {mod_id}"),
        "entities": intent.get("entities", []),
        "patches": [],
        "asset_overlays": intent.get("asset_overlays", []),
        "tests": intent.get("tests", ["preimage_exact_match", "declared_delta", "pck_checksum", "boot"]),
        "not_proven": intent.get("not_proven", "release readiness"),
    }

    for p in intent.get("patches", []):
        rel = p["path"]
        src = (args.base / rel).resolve()
        if not src.exists():
            raise SystemExit(f"ERROR: recovered source not found: {src}")
        text = src.read_text(encoding="utf-8")
        whole_sha = sha256_bytes(src.read_bytes())

        anchor = p.get("anchor")
        if anchor:
            a_count = text.count(anchor)
            exp_a = p.get("expected_occurrences", 1)
            if a_count != exp_a:
                raise SystemExit(
                    f"ERROR: anchor occurrence mismatch in {rel}: expected {exp_a}, got {a_count}\n"
                    f"anchor: {anchor!r}"
                )

        old_text = p["old_text"]
        o_count = text.count(old_text)
        exp_o = p.get("expected_occurrences", 1)
        if o_count != exp_o:
            raise SystemExit(
                f"ERROR: old_text occurrence mismatch in {rel}: expected {exp_o}, got {o_count}\n"
                f"old_text: {old_text!r}"
            )
        if old_text == p["new_text"]:
            raise SystemExit(f"ERROR: old_text == new_text in {rel}")

        generated["patches"].append(
            {
                "path": p["path"],
                "unit_id": p.get("unit_id", f"{p['path']}::{mod_id}"),
                "classification": p.get("classification", "CODE_PATCH"),
                "old_text": old_text,
                "new_text": p["new_text"],
                "preimage_sha256": whole_sha,
                "expected_occurrences": exp_o,
                "placeholders": p.get("placeholders", []),
                "format_tokens": p.get("format_tokens", []),
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(generated, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: wrote {args.out}")
    print(f"    {len(generated['patches'])} patch(es), preimage-guarded, target SHA {ORIGINAL_SHA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
