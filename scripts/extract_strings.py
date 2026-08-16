#!/usr/bin/env python3
"""Extract translatable string candidates from the worktree with context.

Safety rules (AGENTS.md §7.2): node paths, res:// paths, signals, groups,
input actions, animations, dict keys, enum strings, file names are NOT
translatable and get tagged (not dropped, so review is possible).

Usage:
    python scripts/extract_strings.py [--root 06_worktree] [-o manifests/strings_candidates.json] [--kind gd|tscn|json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
GD_STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')

# prefixes that mark non-translatable strings when the string appears after these tokens
NON_TRANSLATABLE_PREFIX = (
    "res://", "user://", "get_node(", "NodePath(", "preload(", "load(",
    "animation.", "play(", "signal ", "group ", "add_to_group(", "is_in_group(",
    "remove_from_group(", "set_collision_layer", "input", "ui_", "&",
    "ActionName", "input_map", "OS.", "DirAccess", "File.", "class_name ",
)
UI_CONTEXT_RE = re.compile(
    r"(\.text\s*=|\.set_text\s*\(|\.add_item\s*\(|\.set_tooltip\s*\(|\.hint_tooltip\s*=|"
    r"\.placeholder_text\s*=|\.set_placeholder|\.title\s*=|tr\s*\(|\.set_message\s*\(|"
    r"\.append_text\s*\(|\btoast\w*\s*\(|\.set_html\s*\()"
)
LOG_CONTEXT_RE = re.compile(
    r"print\s*\(|push_warning\s*\(|push_error\s*\(|printerr\s*\(|printt\s*\(|printraw\s*\("
)

HEURISTIC_TEXT = re.compile(
    r"[A-Za-z]{3,}(?:\s+[A-Za-z]{2,}){1,}"          # multiple words
    r"|^[A-Z][a-z]+$"                                # single capitalized word
    r"|[%$]?\d+[.,]?\d*\s*[A-Za-z%]+(?:\s+[A-Za-z%]+)*"  # numbers/units
)


def classify_gd_string(text: str, line_prefix: str) -> str:
    """Return tag: translatable / non_translatable / uncertain."""
    t = text
    if len(t) < 2:
        return "non_translatable"
    if t.startswith(NON_TRANSLATABLE_PREFIX):
        return "non_translatable"
    if t in ("true", "false", "null", "nil", "0", "1"):
        return "non_translatable"
    # identifier-ish / dict key context
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", t):
        return "non_translatable"  # identifiers, action names, node names
    if "res://" in t or "user://" in t:
        return "non_translatable"
    # UI context on the line?
    if UI_CONTEXT_RE.search(line_prefix):
        return "translatable"
    # log output: print/push_error etc. - not user-facing
    if LOG_CONTEXT_RE.search(line_prefix):
        return "log"
    # dict value (enum display name mapping etc.)
    if re.search(r":\s*$", line_prefix) or re.search(r'["\w]+\s*:\s*"', line_prefix):
        return "dict_value"
    # natural language heuristic
    if HEURISTIC_TEXT.search(t):
        return "uncertain"
    return "non_translatable"


def extract_gd(path: Path, root: Path) -> list:
    out = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for m in GD_STRING_RE.finditer(line):
            text = m.group(1)
            tag = classify_gd_string(text, line)
            if tag == "non_translatable":
                continue
            out.append({
                "source": str(path.relative_to(root)).replace("\\", "/"),
                "kind": "gd", "line": i, "text": text, "tag": tag,
                "context": line.strip()[:160],
            })
    return out


def extract_tscn(path: Path, root: Path) -> list:
    out = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    props = {
        "text": "text", "hint_tooltip": "tooltip", "placeholder_text": "placeholder",
        "title": "title", "button_text": "button_text", "message": "message",
    }
    for i, line in enumerate(lines, 1):
        for prop, kind in props.items():
            m = re.search(rf"\b{prop}\s*=\s*\"((?:[^\"\\]|\\.)*)\"", line)
            if m:
                t = m.group(1)
                if len(t) >= 2 and not t.startswith("res://"):
                    out.append({
                        "source": str(path.relative_to(root)).replace("\\", "/"),
                        "kind": "tscn", "line": i, "text": t, "tag": "translatable",
                        "context": line.strip()[:160],
                    })
    return out


def extract_json(path: Path, root: Path) -> list:
    out = []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return out

    def walk(node, key_hint):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key_hint)
        elif isinstance(node, str):
            t = node
            if len(t) < 2:
                return
            if t.startswith("res://") or t.startswith("user://"):
                return
            # keys that are ids/lookup values
            if key_hint in ("id", "type", "tag", "key", "path", "class", "value",
                            "color", "position", "uuid", "icon", "texture", "name_id",
                            "from", "to", "source", "target", "node", "edge",
                            "passive_tag", "tags", "requires"):
                return
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", t):
                return
            if re.fullmatch(r"[\d.+-]+", t):
                return
            # hex-ish node/edge ids like '0c533', 'c99d1'
            if re.fullmatch(r"[0-9a-fA-F]{3,8}", t):
                return
            out.append({
                "source": str(path.relative_to(root)).replace("\\", "/"),
                "kind": "json", "line": 0, "text": t, "tag": "uncertain",
                "context": f"key={key_hint}",
            })

    walk(data, None)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("04_recovered"),
                    help="source tree (use 04_recovered: unmodified English)")
    ap.add_argument("-o", "--output", type=Path, default=Path("manifests/strings_candidates.json"))
    ap.add_argument("--kind", default="all", choices=["all", "gd", "tscn", "json"])
    args = ap.parse_args()

    root = args.root
    all_entries = []
    kinds = ["gd", "tscn", "json"] if args.kind == "all" else [args.kind]

    import collections
    stats = collections.Counter()

    if "gd" in kinds:
        for p in root.rglob("*.gd"):
            if "addons" in p.parts:
                continue
            entries = extract_gd(p, root)
            all_entries.extend(entries)
            stats["gd"] += len(entries)
    if "tscn" in kinds:
        for p in root.rglob("*.tscn"):
            if "addons" in p.parts:
                continue
            entries = extract_tscn(p, root)
            all_entries.extend(entries)
            stats["tscn"] += len(entries)
    if "json" in kinds:
        for p in root.rglob("*.json"):
            if "addons" in p.parts:
                continue
            entries = extract_json(p, root)
            all_entries.extend(entries)
            stats["json"] += len(entries)

    # de-dup identical (source, text) pairs
    seen = set()
    dedup = []
    for e in all_entries:
        k = (e["source"], e["text"])
        if k in seen:
            continue
        seen.add(k)
        dedup.append(e)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "tool": "scripts/extract_strings.py",
        "count": len(dedup),
        "by_kind": dict(stats),
        "entries": dedup,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"extracted: {len(dedup)} candidates by_kind={dict(stats)}")
    print(f"output: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

