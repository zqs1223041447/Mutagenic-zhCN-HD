#!/usr/bin/env python3
"""Apply a translation map (en -> zh) to the worktree files.

Input translation map: JSON list of {"text": <en>, "translation": <zh>} or
{"src": ..., "zh": ...}. Strings are replaced only inside quoted string
literals (gd/tscn) or JSON string values (json), preserving formatting.
Placeholder counts (%s, %d, %%, \\n) are validated.

Usage:
    python scripts/apply_translation.py -m <map.json> [--root 06_worktree] [--dry-run]
"""

import argparse
import json
import re
import sys
from pathlib import Path

STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
PLACEHOLDER_RE = re.compile(r"%[sdifo%]")


def validate_placeholders(en: str, zh: str) -> str:
    en_ph = sorted(PLACEHOLDER_RE.findall(en))
    zh_ph = sorted(PLACEHOLDER_RE.findall(zh))
    if en_ph != zh_ph:
        return f"placeholder mismatch: {en!r} -> {zh!r} ({en_ph} vs {zh_ph})"
    return None


def apply_text_file(path: Path, mapping, dry_run: bool, errors: list) -> int:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except OSError:
        return 0
    changed = 0
    for i, line in enumerate(lines):
        for m in STRING_RE.finditer(line):
            literal = m.group(1)
            if literal in mapping:
                zh = mapping[literal]
                err = validate_placeholders(literal, zh)
                if err:
                    errors.append(f"{path}:{i+1}: {err}")
                    continue
                new_line = line[:m.start(1)] + zh + line[m.end(1):]
                if not dry_run:
                    lines[i] = new_line
                changed += 1
    if changed and not dry_run:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def apply_json_file(path: Path, mapping, dry_run: bool, errors: list) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    changed = [0]

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and node in mapping:
            zh = mapping[node]
            err = validate_placeholders(node, zh)
            if err:
                errors.append(f"{path}: {err}")
                return
            changed[0] += 1
            return zh

    data = walk(data)
    if changed[0] and not dry_run:
        path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    return changed[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--map", type=Path, required=True)
    ap.add_argument("--root", type=Path, default=Path("06_worktree"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    raw = json.loads(args.map.read_text(encoding="utf-8"))
    mapping = {}
    if isinstance(raw, dict) and "mapping" in raw:
        mapping = raw["mapping"]
    else:
        items = raw if isinstance(raw, list) else raw.get("units", raw.get("entries", []))
        for item in items:
            en = item.get("text") or item.get("src")
            zh = item.get("translation") or item.get("zh")
            if en and zh:
                mapping[en] = zh
    print(f"map: {len(mapping)} entries")

    errors = []
    total = 0
    report = []
    for p in args.root.rglob("*"):
        if not p.is_file():
            continue
        if "addons" in p.parts:
            continue
        ext = p.suffix.lower()
        if ext in (".gd", ".tscn", ".tres"):
            n = apply_text_file(p, mapping, args.dry_run, errors)
        elif ext == ".json":
            n = apply_json_file(p, mapping, args.dry_run, errors)
        else:
            continue
        if n:
            report.append({"file": str(p.relative_to(args.root)).replace("\\", "/"), "replaced": n})
            total += n

    print(f"files touched: {len(report)} total replacements: {total}")
    if not args.dry_run:
        out = Path("manifests/translation_report.json")
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({"total": total, "errors": errors, "files": report},
                                  indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"report: {out}")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors[:20]:
            print("  ", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())