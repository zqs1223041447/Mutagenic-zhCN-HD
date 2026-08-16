#!/usr/bin/env python3
"""Split remaining translation units into parallel batches.

Produces 05_translation/batch_N_input.json files containing:
  the unit text, tags, kinds, a couple of source contexts.

Usage:
    python scripts/prepare_batches.py [--n 4] [--already 05_translation/batch1_ui.json]
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=Path, default=Path("05_translation/units.json"))
    ap.add_argument("--glossary", type=Path, default=Path("05_translation/glossary.json"))
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--already", type=Path, default=Path("05_translation/batch1_ui.json"))
    ap.add_argument("--outdir", type=Path, default=Path("05_translation"))
    args = ap.parse_args()

    units = json.loads(args.units.read_text(encoding="utf-8"))["units"]
    already = {x["text"] for x in json.loads(args.already.read_text(encoding="utf-8"))}
    glossary = json.loads(args.glossary.read_text(encoding="utf-8"))

    remaining = [u for u in units if u["text"] not in already]
    # sort by occurrence (most used first), stable
    remaining.sort(key=lambda u: -u["occurrences"])
    print(f"remaining units: {len(remaining)}")

    batches = [[] for _ in range(args.n)]
    for i, u in enumerate(remaining):
        batches[i % args.n].append(u)

    args.outdir.mkdir(parents=True, exist_ok=True)
    for i, b in enumerate(batches):
        out = args.outdir / f"batch_{i + 1}_input.json"
        out.write_text(json.dumps({
            "batch": i + 1,
            "glossary": glossary["terms"],
            "glossary_notes": glossary["meta"],
            "instructions": (
                "Translate each 'text' to Simplified Chinese for a dark-fantasy ARPG. "
                "Rules: (1) use the glossary for consistent terms; keep game terminology "
                "consistent with PoE Chinese conventions; (2) preserve ALL format "
                "placeholders exactly (%s %d %f %% \\n, curly-brace or $tokens); "
                "(3) do NOT translate pure identifiers/paths/single chars/numbers "
                "(mark as skip); (4) keep punctuation structure like : ; - ; "
                "(5) Chinese should be concise for UI fit; (6) proper nouns: use "
                "clever ARPG-style Chinese names (e.g. Sanguine Decay -> 血性衰败). "
                "Output STRICT JSON: a list of {\"text\": <exact source>, "
                "\"translation\": <zh> or \"skip\": true}."
            ),
            "units": [{
                "text": u["text"],
                "tags": u["tags"],
                "kinds": u["kinds"],
                "occurrences": u["occurrences"],
                "contexts": [f"{s['file']}:{s['line']} | {s['context']}" for s in u["sources"][:3]],
            } for u in b],
        }, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"  {out}: {len(b)} units")
    return 0


if __name__ == "__main__":
    sys.exit(main())