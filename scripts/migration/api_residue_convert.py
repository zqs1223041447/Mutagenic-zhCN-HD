#!/usr/bin/env python3
"""P1-WAVE-K: mechanical API residue fixer for migrated product scripts.

Never writes 03_raw/** or 04_recovered/** and never touches non-.gd
files: the caller points it at a product root (or an explicit list of
product-relative .gd paths) and every rewrite is restricted to
deterministic, semantically equivalent renames:

- TYPE_REAL -> TYPE_FLOAT,
- Label.ALIGN_LEFT/CENTER/RIGHT and bare ALIGN_* in assignment or
  comparison context -> HORIZONTAL_ALIGNMENT_*,
- rect_size -> size, rect_scale -> scale,
  rect_min_size -> custom_minimum_size, rect_position -> position,
- standalone statement update() / self.update() -> queue_redraw(),
- Engine.get_screen_refresh_rate( -> DisplayServer.screen_get_refresh_rate(
- Input.get_action_list( -> InputMap.action_get_ids(
- Input.get_scancode_string( -> OS.get_keycode_string(

Anything whose Godot 4 rewrite changes read/write semantics is NOT
touched textually; it is reported under residuals as MANUAL_REVIEW:
OS.window_*, OS.vsync_enabled, Directory usage, yield() and
Engine.set_target_fps(. dry_run=True reports what would change without
writing any file.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Iterable, Union

_Repl = Union[str, Callable[[re.Match], str]]


def _align_qualified_repl(match: re.Match) -> str:
    return "HORIZONTAL_ALIGNMENT_" + match.group(2)


def _align_bare_repl(match: re.Match) -> str:
    return f"{match.group(1)}{match.group(2)}HORIZONTAL_ALIGNMENT_{match.group(3)}"


# (pattern name, regex, replacement), applied line by line in order.
_REPLACE_RULES: tuple[tuple[str, re.Pattern, _Repl], ...] = (
    (
        "TYPE_REAL",
        re.compile(r"\bTYPE_REAL\b"),
        "TYPE_FLOAT",
    ),
    (
        "Label.ALIGN_*",
        re.compile(r"\b([A-Za-z_]\w*)\.ALIGN_(LEFT|CENTER|RIGHT)\b"),
        _align_qualified_repl,
    ),
    (
        "ALIGN_*",
        re.compile(r"(==|!=|>=|<=|[=<>])([ \t]*)ALIGN_(LEFT|CENTER|RIGHT)\b"),
        _align_bare_repl,
    ),
    (
        "rect_size",
        re.compile(r"\brect_size\b"),
        "size",
    ),
    (
        "rect_scale",
        re.compile(r"\brect_scale\b"),
        "scale",
    ),
    (
        "rect_min_size",
        re.compile(r"\brect_min_size\b"),
        "custom_minimum_size",
    ),
    (
        "rect_position",
        re.compile(r"\brect_position\b"),
        "position",
    ),
    (
        "update()",
        re.compile(r"^([ \t]*)(?:self\.)?update\(\)([ \t]*(?:#.*)?)$"),
        r"\1queue_redraw()\2",
    ),
    (
        "Engine.get_screen_refresh_rate(",
        re.compile(r"\bEngine\.get_screen_refresh_rate\s*\("),
        "DisplayServer.screen_get_refresh_rate(",
    ),
    (
        "Input.get_action_list(",
        re.compile(r"\bInput\.get_action_list\s*\("),
        "InputMap.action_get_ids(",
    ),
    (
        "Input.get_scancode_string(",
        re.compile(r"\bInput\.get_scancode_string\s*\("),
        "OS.get_keycode_string(",
    ),
)

# (pattern name, regex, reason): reported under residuals, never rewritten.
_RESIDUAL_RULES: tuple[tuple[str, re.Pattern, str], ...] = (
    (
        "OS.window_*",
        re.compile(r"\bOS\.window_\w+"),
        "MANUAL_REVIEW: OS.window_* read/write semantics differ; needs DisplayServer window mode API rewrite",
    ),
    (
        "OS.vsync_enabled",
        re.compile(r"\bOS\.vsync_enabled\b"),
        "MANUAL_REVIEW: OS.vsync_enabled read/write semantics differ; needs DisplayServer.window_set_vsync_mode rewrite",
    ),
    (
        "Directory",
        re.compile(r"\bDirectory\s*(\(|\.)"),
        "MANUAL_REVIEW: Directory new/open/list_dir_begin needs DirAccess semantic rewrite",
    ),
    (
        "yield(",
        re.compile(r"\byield\s*\("),
        "MANUAL_REVIEW: yield() coroutine/signal semantics need await rewrite",
    ),
    (
        "Engine.set_target_fps(",
        re.compile(r"\bEngine\.set_target_fps\s*\("),
        "MANUAL_REVIEW: Engine.set_target_fps is Engine.max_fps property setter in Godot 4; textual rewrite unsafe",
    ),
)


def _resolve_targets(product_root: Path, files: Iterable[str] | None) -> list[tuple[str, Path]]:
    """Return sorted (product-relative posix path, absolute Path) pairs."""
    if files is None:
        return sorted(
            (p.relative_to(product_root).as_posix(), p)
            for p in product_root.rglob("*.gd")
            if p.is_file()
        )
    resolved: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for item in files or ():
        candidate = Path(str(item).replace("\\", "/"))
        if candidate.is_absolute():
            try:
                rel = candidate.resolve().relative_to(product_root.resolve()).as_posix()
            except ValueError:
                continue
            path = candidate
        else:
            rel = candidate.as_posix().strip("/")
            path = product_root / candidate
        if rel in seen:
            continue
        if path.suffix.lower() != ".gd" or not path.is_file():
            continue
        seen.add(rel)
        resolved.append((rel, path))
    resolved.sort()
    return resolved


def _split_eol(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def fix_api_residues(
    product_root: Path,
    files: Iterable[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Mechanically fix deterministic Godot 4 API residues in product .gd files.

    files is an optional iterable of product-relative (or absolute) .gd
    paths; when omitted every *.gd under product_root is scanned. Lines
    are rewritten only via the fixed rule table above; everything else is
    left byte-identical. Residual patterns are reported, never rewritten.
    With dry_run=True no file is modified but the report is complete.
    """
    product_root = Path(product_root)
    files_changed: list[str] = []
    replacements: list[dict[str, Any]] = []
    residuals: list[dict[str, Any]] = []

    for rel, path in _resolve_targets(product_root, files):
        try:
            original = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            residuals.append({
                "file": rel,
                "line": 0,
                "pattern": "<unreadable>",
                "reason": "MANUAL_REVIEW: file could not be read as UTF-8; skipped untouched",
            })
            continue

        out_lines: list[str] = []
        file_changed = False
        for lineno, raw in enumerate(original.splitlines(keepends=True), start=1):
            body, eol = _split_eol(raw)
            current = body
            for pattern_name, rx, repl in _REPLACE_RULES:
                if not rx.search(current):
                    continue
                before = current
                current = rx.sub(repl, current)
                replacements.append({
                    "file": rel,
                    "line": lineno,
                    "pattern": pattern_name,
                    "before": before,
                    "after": current,
                })
            if current != body:
                file_changed = True
            for pattern_name, rx, reason in _RESIDUAL_RULES:
                if rx.search(current):
                    residuals.append({
                        "file": rel,
                        "line": lineno,
                        "pattern": pattern_name,
                        "reason": reason,
                    })
            out_lines.append(current + eol)

        if file_changed:
            files_changed.append(rel)
            if not dry_run:
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    handle.write("".join(out_lines))

    return {
        "files_changed": files_changed,
        "replacements": replacements,
        "residuals": residuals,
        "total_replacements": len(replacements),
        "dry_run": dry_run,
    }
