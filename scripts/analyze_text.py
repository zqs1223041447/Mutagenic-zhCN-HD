#!/usr/bin/env python3
"""Quantify translatable text in the recovered PCK (03_raw).

Reports quoted-string stats per extension for text-like files
(.tscn / .tres / .res / .json / .import / .gd / .txt).

Usage:
    python scripts/analyze_text.py [--dir 03_raw] [--min-len 2]
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

TEXT_EXTS = {".tscn", ".tres", ".res", ".json", ".import", ".gd", ".txt", ".cfg", ".ini"}
STRING_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


def main() -> int:
    ap = argparse.ArgumentParser(description="Quantify translatable strings in PCK dump")
    ap.add_argument("--dir", type=Path, default=Path("03_raw"))
    ap.add_argument("--min-len", type=int, default=2)
    ap.add_argument("-m", "--manifest", type=Path, default=None,
                    help="recovered_manifest.json to iterate instead of scanning disk")
    args = ap.parse_args()

    stats = defaultdict(lambda: {"files": 0, "strings": 0, "chars": 0})
    if args.manifest:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        relpaths = [f["relpath"] for f in manifest["files"]]
    else:
        relpaths = [str(p.relative_to(args.dir)).replace("\\", "/")
                    for p in args.dir.rglob("*") if p.is_file()]

    for rp in relpaths:
        ext = Path(rp).suffix.lower()
        if ext not in TEXT_EXTS:
            continue
        p = args.dir / rp
        try:
            d = p.read_bytes()
        except OSError:
            continue
        if not d:
            continue
        printable = sum(1 for b in d if b in (9, 10, 13) or 32 <= b < 127)
        if printable / len(d) < 0.9:
            continue
        txt = d.decode("utf-8", "replace")
        strings = [s for s in STRING_RE.findall(txt) if len(s) >= args.min_len]
        stats[ext]["files"] += 1
        stats[ext]["strings"] += len(strings)
        stats[ext]["chars"] += sum(len(s) for s in strings)

    print(f"{'ext':>8} {'files':>6} {'strings':>8} {'chars':>10}")
    total_s = total_c = 0
    for ext in sorted(stats, key=lambda e: -stats[e]["strings"]):
        s = stats[ext]
        print(f"{ext:>8} {s['files']:>6} {s['strings']:>8} {s['chars']:>10}")
        total_s += s["strings"]
        total_c += s["chars"]
    print(f"{'TOTAL':>8} {'':>6} {total_s:>8} {total_c:>10}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
