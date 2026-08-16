#!/usr/bin/env python3
"""Build translation units from string candidates (dedup, term stats).

Output:
  05_translation/units.json     - unique strings with context and sources
  05_translation/terms.json     - high-frequency word stats (for glossary)

Usage:
    python scripts/build_translation_units.py [-i manifests/strings_candidates.json]
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", type=Path, default=Path("manifests/strings_candidates.json"))
    ap.add_argument("-o", "--outdir", type=Path, default=Path("05_translation"))
    args = ap.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    entries = data["entries"]

    # Accept: translatable, dict_value, uncertain (json all accepted)
    keep_tags = {"translatable", "dict_value", "uncertain"}
    units = defaultdict(lambda: {"text": None, "tags": set(), "kinds": set(),
                                 "sources": [], "lines": []})

    for e in entries:
        if e["tag"] not in keep_tags and e["kind"] != "json":
            continue
        if e["kind"] == "json" and e["tag"] == "non_translatable":
            continue
        u = units[e["text"]]
        u["text"] = e["text"]
        u["tags"].add(e["tag"])
        u["kinds"].add(e["kind"])
        u["sources"].append({"file": e["source"], "line": e["line"],
                             "tag": e["tag"], "context": e.get("context", "")})

    # sort by popularity (from most-used to least)
    ordered = sorted(units.values(), key=lambda u: -len(u["sources"]))
    unit_list = [{
        "text": u["text"],
        "occurrences": len(u["sources"]),
        "tags": sorted(u["tags"]),
        "kinds": sorted(u["kinds"]),
        "sources": u["sources"][:6],
        "source_count": len(u["sources"]),
    } for u in ordered]

    # term frequency (words >= 3 chars, excluding common stopwords)
    stop = set("the a an of to in on at for with without and or from by is are was were "
               "be been being have has had do does did not no you your this that these those "
               "it its they them their we our us as if then than so but also all any can will "
               "would should could may might must new per via into out up down over under".split())
    words = Counter()
    for u in unit_list:
        for w in re.findall(r"[A-Za-z]{3,}", u["text"]):
            if w.lower() not in stop and w[0].isupper():
                words[w] += 1
    terms = [{"word": w, "count": c} for w, c in words.most_common(400)]

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "units.json").write_text(
        json.dumps({"count": len(unit_list), "units": unit_list},
                   indent=1, ensure_ascii=False), encoding="utf-8")
    (args.outdir / "terms.json").write_text(
        json.dumps({"count": len(terms), "terms": terms},
                   indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"units: {len(unit_list)}")
    print(f"terms: {len(terms)}")
    print(f"outdir: {args.outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())