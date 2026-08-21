#!/usr/bin/env python3
"""P1-WAVE-B: convert Boot / Project / Autoload / Input from recovered 3.5.3.

Never writes 03_raw/** or 04_recovered/**. Product receives converted copies.
Zero Godot import errors are not required; errors are classified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GODOT3_SPKEY = 16777216
GODOT4_SPECIAL = 4194304

DATA_DIRS = (
    "passive_tree_data",
    "skillgen",
    "world_map_data",
)

COLOR_CONSTANTS = (
    "white", "black", "red", "green", "blue", "transparent",
    "yellow", "gray", "grey", "orange", "purple", "cyan", "magenta",
)

CONNECT3_RE = re.compile(
    r"""\.connect\s*\(\s*(["'][^"']+["'])\s*,\s*([^,]+?)\s*,\s*(["'][^"']+["'])\s*\)"""
)
CONNECT4_RE = re.compile(
    r"""\.connect\s*\(\s*(["'][^"']+["'])\s*,\s*([^,]+?)\s*,\s*(["'][^"']+["'])\s*,\s*(\[[^\]]*\])\s*\)"""
)
YIELD_RE = re.compile(
    r"""\byield\s*\(\s*(.+?)\s*,\s*(["'][^"']+["'])\s*\)"""
)
EXPORT_RE = re.compile(r"\bexport\s*(?:\([^)]*\))?\s+var\b")
PACKED_JOIN_RE = re.compile(
    r"PackedStringArray\s*\(([^)]*)\)\s*\.join\s*\(([^)]*)\)"
)
JSON_PARSE_IF_RE = re.compile(
    r"var\s+(\w+)\s*=\s*JSON\.parse_string\(([^)]+)\)\s*\n"
    r"(\s+)if\s+\1\.error\s*==\s*OK\s+and\s+typeof\(\1\.result\)\s*==\s*TYPE_DICTIONARY:",
    re.MULTILINE,
)
FILE_NEW_RE = re.compile(r"(?m)^(\s*)var\s+(\w+)\s*=\s*File\.new\(\)\s*\n")
FILE_OPEN_RE = re.compile(
    r"(?m)^(\s*)(\w+)\.open\s*\(([^,]+),\s*FileAccess\.(READ|WRITE|READ_WRITE)\)\s*$"
)
ENUM_HEAD_RE = re.compile(r"\benum\s+[A-Za-z_][A-Za-z0-9_]*\s*\{")
ENUM_MEMBER_RE = re.compile(
    r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*=\s*[^,#]+)?(\s*,)?(\s*(#.*)?)?$"
)
GLOBAL_CLASS_RE = re.compile(
    r'"class"\s*:\s*"([A-Za-z_][A-Za-z0-9_]*)"[\s\S]{0,200}?"path"\s*:\s*"(res://[^"]+)"'
    r'|"path"\s*:\s*"(res://[^"]+)"[\s\S]{0,200}?"class"\s*:\s*"([A-Za-z_][A-Za-z0-9_]*)"'
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_fingerprint(root: Path) -> dict[str, str]:
    root = Path(root)
    out: dict[str, str] = {}
    if not root.is_dir():
        return out
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        out[rel] = sha256_file(path)
    return out


def remap_keycode(code: int) -> int:
    if code >= GODOT3_SPKEY:
        return GODOT4_SPECIAL + (code - GODOT3_SPKEY)
    return code


def split_top_level(text: str, sep: str = ",") -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    quote: str | None = None
    escape = False
    for ch in text:
        if quote:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            buf.append(ch)
            continue
        if ch in "([{":
            depth += 1
            buf.append(ch)
            continue
        if ch in ")]}":
            depth -= 1
            buf.append(ch)
            continue
        if ch == sep and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def find_object_span(text: str, start: int) -> tuple[int, int] | None:
    idx = text.find("Object(", start)
    if idx < 0:
        return None
    depth = 0
    quote: str | None = None
    escape = False
    for j in range(idx + len("Object"), len(text)):
        ch = text[j]
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return idx, j + 1
    return None


def parse_object_ctor(blob: str) -> tuple[str, list[tuple[str, str]]]:
    inner = blob[len("Object("):-1]
    parts = split_top_level(inner)
    if not parts:
        return "Unknown", []
    typ = parts[0].strip()
    props: list[tuple[str, str]] = []
    for part in parts[1:]:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        props.append((key.strip().strip('"'), value.strip()))
    return typ, props


def compact_ctor_value(value: str) -> str:
    def _compact(match: re.Match[str]) -> str:
        args = ", ".join(a.strip() for a in match.group(2).split(","))
        return f"{match.group(1)}({args})"

    return re.sub(r"(Vector2|Vector3|Color|Rect2)\(\s*([^)]*?)\s*\)", _compact, value)


def convert_input_object(blob: str) -> str:
    typ, props = parse_object_ctor(blob)
    mapped: list[tuple[str, str]] = []
    seen: set[str] = set()

    def put(key: str, value: str) -> None:
        if key in seen:
            return
        seen.add(key)
        mapped.append((key, value))

    key_aliases = {
        "alt": "alt_pressed",
        "shift": "shift_pressed",
        "control": "ctrl_pressed",
        "meta": "meta_pressed",
        "scancode": "keycode",
        "physical_scancode": "physical_keycode",
        "doubleclick": "double_click",
    }
    drop = {"command"}
    if typ == "InputEventJoypadButton":
        key_aliases["pressed"] = "button_pressed"

    for key, value in props:
        if key in drop:
            continue
        out_key = key_aliases.get(key, key)
        if out_key in {"keycode", "physical_keycode"}:
            try:
                value = str(remap_keycode(int(value)))
            except ValueError:
                pass
        put(out_key, compact_ctor_value(value))

    if typ in {"InputEventKey", "InputEventMouseButton"}:
        if "window_id" not in seen:
            put("window_id", "0")
    if typ == "InputEventKey" and "location" not in seen:
        put("location", "0")

    body = ",".join(f'"{k}":{v}' for k, v in mapped)
    return f"Object({typ},{body})"


def convert_input_section(body: str) -> str:
    out: list[str] = []
    i = 0
    while True:
        span = find_object_span(body, i)
        if span is None:
            out.append(body[i:])
            break
        start, end = span
        out.append(body[i:start])
        out.append(convert_input_object(body[start:end]))
        i = end
    return "".join(out)


def iter_sections(text: str) -> list[tuple[str | None, str]]:
    pattern = re.compile(r"(?m)^\[([^\]]+)\]\s*$")
    matches = list(pattern.finditer(text))
    if not matches:
        return [(None, text)]
    sections: list[tuple[str | None, str]] = []
    preamble = text[: matches[0].start()]
    sections.append((None, preamble))
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections.append((match.group(1), text[match.end():end]))
    return sections


def parse_autoloads(project_text: str) -> list[dict[str, str]]:
    section = re.search(r"(?ms)^\[autoload\]\s*\n(.*?)(?=^\[[^\]]+\]\s*$|\Z)", project_text)
    if not section:
        return []
    items: list[dict[str, str]] = []
    for match in re.finditer(r'(?m)^([A-Za-z0-9_]+)="\*?(res://[^"]+)"', section.group(1)):
        items.append({"name": match.group(1), "path": match.group(2)})
    return items


def parse_input_actions(project_text: str) -> list[str]:
    section = re.search(r"(?ms)^\[input\]\s*\n(.*?)(?=^\[[^\]]+\]\s*$|\Z)", project_text)
    if not section:
        return []
    return [m.group(1) for m in re.finditer(r"(?m)^([A-Za-z0-9_]+)\s*=", section.group(1))]


def _application_body(original: str, main_scene: str) -> str:
    name = "Mutagenic"
    match = re.search(r'config/name\s*=\s*"(.*)"', original)
    if match:
        name = match.group(1)
    return (
        f'\nconfig/name="{name}"\n'
        f'config/description="Godot 4.7.1 Product (P1-WAVE-B boot/autoload/input)"\n'
        f'run/main_scene="{main_scene}"\n'
        f'config/features=PackedStringArray("4.7", "Forward Plus")\n'
        f'config/icon="res://icon.svg"\n\n'
    )


def convert_display_body(_original: str) -> str:
    return (
        "\n"
        "window/size/viewport_width=1280\n"
        "window/size/viewport_height=800\n"
        "window/stretch/aspect=\"keep_height\"\n"
        "\n"
    )


def convert_physics_body(_original: str) -> str:
    return (
        "\n"
        "2d/default_gravity=0.0\n"
        "2d/default_gravity_vector=Vector2(0, 0)\n"
        "2d/default_linear_damp=0.0\n"
        "\n"
    )


def convert_rendering_body(_original: str) -> str:
    return (
        "\n"
        "renderer/rendering_method=\"forward_plus\"\n"
        "textures/canvas_textures/default_texture_filter=0\n"
        "2d/snap/snap_2d_transforms_to_pixel=true\n"
        "2d/snap/snap_2d_vertices_to_pixel=true\n"
        "environment/defaults/default_clear_color=Color(0.254902, 0.254902, 0.254902, 1)\n"
        "\n"
    )


def convert_project_godot(text: str, *, main_scene: str = "res://scenes/seed.tscn") -> dict[str, Any]:
    sections = {name: body for name, body in iter_sections(text) if name is not None}
    autoloads = parse_autoloads(text)
    actions = parse_input_actions(text)
    input_body = convert_input_section(sections.get("input") or "")
    autoload_body = sections.get("autoload") or ""
    layer_body = sections.get("layer_names") or ""
    gui_body = sections.get("gui") or "\n\n"

    out = (
        "; Engine configuration file.\n"
        "; P1-WAVE-B Godot 4.7.1 boot/autoload/input conversion. Generated; do not hand-edit.\n"
        "\n"
        "config_version=5\n"
        "\n"
        "[application]\n"
        + _application_body(sections.get("application") or "", main_scene)
        + "[autoload]\n"
        + autoload_body
        + "[display]\n"
        + convert_display_body(sections.get("display") or "")
        + "[gui]\n"
        + gui_body
        + "[input]\n"
        + input_body
        + "[layer_names]\n"
        + layer_body
        + "[physics]\n"
        + convert_physics_body(sections.get("physics") or "")
        + "[rendering]\n"
        + convert_rendering_body(sections.get("rendering") or "")
    )
    if "config_version=4" in out or 'PackedStringArray("3.' in out:
        raise ValueError("converted project still looks like Godot 3")
    return {
        "text": out,
        "autoloads": autoloads,
        "input_actions": actions,
        "main_scene": main_scene,
        "config_version": 5,
    }


def _yield_repl(match: re.Match[str]) -> str:
    obj = match.group(1).strip()
    sig = match.group(2)[1:-1]
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", sig):
        return f"await {obj}.{sig}"
    return f"await {obj}"


def _connect3_repl(match: re.Match[str]) -> str:
    return f".connect({match.group(1)}, Callable({match.group(2).strip()}, {match.group(3)}))"


def _connect4_repl(match: re.Match[str]) -> str:
    binds = match.group(4).strip()[1:-1].strip()
    bind_call = f".bind({binds})" if binds else ""
    return (
        f".connect({match.group(1)}, "
        f"Callable({match.group(2).strip()}, {match.group(3)}){bind_call})"
    )


def _comma_enum_body(body: str) -> str:
    lines = body.split("\n")
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out.append(line)
            continue
        match = ENUM_MEMBER_RE.match(line.rstrip())
        if not match or match.group(4):
            out.append(line)
            continue
        indent, name, assign = match.group(1), match.group(2), match.group(3) or ""
        comment = ""
        if "#" in line:
            comment = " " + line[line.index("#"):].rstrip("\n")
        out.append(f"{indent}{name}{assign},{comment}")
    return "\n".join(out)


def convert_enum_commas(text: str) -> str:
    pieces: list[str] = []
    idx = 0
    while True:
        match = ENUM_HEAD_RE.search(text, idx)
        if not match:
            pieces.append(text[idx:])
            break
        pieces.append(text[idx:match.end()])
        depth = 1
        pos = match.end()
        quote: str | None = None
        while pos < len(text) and depth:
            ch = text[pos]
            if quote:
                if ch == quote:
                    quote = None
            elif ch in ("'", '"'):
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        pieces.append(_comma_enum_body(text[match.end():pos]))
        idx = pos
    return "".join(pieces)


def parse_global_classes(project_text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for match in GLOBAL_CLASS_RE.finditer(project_text):
        if match.group(1) and match.group(2):
            items.append({"name": match.group(1), "path": match.group(2)})
        elif match.group(3) and match.group(4):
            items.append({"name": match.group(4), "path": match.group(3)})
    return items


def inject_class_name(text: str, name: str) -> str:
    if re.search(rf"(?m)^class_name\s+{re.escape(name)}\b", text):
        return text
    match = re.search(r"(?m)^extends\s+[^\n]+\n", text)
    if match:
        return text[: match.end()] + f"class_name {name}\n" + text[match.end():]
    return f"class_name {name}\n" + text


def convert_gdscript(text: str) -> str:
    out = text
    out = re.sub(r"(?m)^tool\s*$", "@tool", out)
    out = re.sub(r"\bonready\s+var\b", "@onready var", out)
    out = EXPORT_RE.sub("@export var", out)
    out = re.sub(r"\bextends\s+Reference\b", "extends RefCounted", out)
    out = re.sub(r"\bKinematicBody2D\b", "CharacterBody2D", out)
    out = re.sub(r"\bParticles2D\b", "GPUParticles2D", out)
    out = re.sub(r"\bAnimatedSprite\b(?!2D)", "AnimatedSprite2D", out)
    out = re.sub(r"\bVisibilityNotifier2D\b", "VisibleOnScreenNotifier2D", out)
    out = re.sub(r"\bPosition2D\b", "Marker2D", out)
    out = re.sub(r"\bTextureProgress\b", "TextureProgressBar", out)
    out = re.sub(r"\bLight2D\b", "PointLight2D", out)
    out = re.sub(r"\bPoolStringArray\b", "PackedStringArray", out)
    out = re.sub(r"\bPoolByteArray\b", "PackedByteArray", out)
    out = re.sub(r"\bPoolVector2Array\b", "PackedVector2Array", out)
    out = re.sub(r"\bPoolRealArray\b", "PackedFloat32Array", out)
    out = re.sub(r"\bPoolIntArray\b", "PackedInt32Array", out)
    out = re.sub(r"\bVisualServer\b", "RenderingServer", out)
    out = re.sub(r"\bPhysics2DServer\b", "PhysicsServer2D", out)
    out = re.sub(r"\.instance\s*\(", ".instantiate(", out)
    out = re.sub(r"\bfuncref\s*\(", "Callable(", out)
    out = re.sub(r"\bparse_json\s*\(", "JSON.parse_string(", out)
    out = re.sub(r"\bto_json\s*\(", "JSON.stringify(", out)
    out = re.sub(r"\bJSON\.print\s*\(", "JSON.stringify(", out)
    out = re.sub(r"\bJSON\.parse\s*\(", "JSON.parse_string(", out)
    out = re.sub(r"\bOS\.get_ticks_msec\s*\(", "Time.get_ticks_msec(", out)
    out = re.sub(r"\bOS\.get_unix_time\s*\(", "Time.get_unix_time_from_system(", out)
    out = re.sub(r"\bOS\.get_screen_refresh_rate\s*\(", "DisplayServer.screen_get_refresh_rate(", out)
    out = re.sub(r"\bEngine\.iterations_per_second\b", "Engine.physics_ticks_per_second", out)
    out = re.sub(
        r"\$[A-Za-z0-9_]+(?:\s*/\s*[A-Za-z0-9_]+)+",
        lambda m: re.sub(r"\s*/\s*", "/", m.group(0)),
        out,
    )
    out = re.sub(r"\brand_range\s*\(", "randf_range(", out)
    out = re.sub(r"\bstepify\s*\(", "snapped(", out)
    out = re.sub(r"\bstr2var\b", "str_to_var", out)
    out = re.sub(r"\bvar2str\b", "var_to_str", out)
    out = re.sub(r"\.change_scene\s*\(", ".change_scene_to_file(", out)
    out = re.sub(r"Node\.PAUSE_MODE_PROCESS", "Node.PROCESS_MODE_ALWAYS", out)
    out = re.sub(r"Node\.PAUSE_MODE_STOP", "Node.PROCESS_MODE_PAUSABLE", out)
    out = re.sub(r"Node\.PAUSE_MODE_INHERIT", "Node.PROCESS_MODE_INHERIT", out)
    out = re.sub(r"\bPAUSE_MODE_PROCESS\b", "PROCESS_MODE_ALWAYS", out)
    out = re.sub(r"\bPAUSE_MODE_STOP\b", "PROCESS_MODE_PAUSABLE", out)
    out = re.sub(r"\bPAUSE_MODE_INHERIT\b", "PROCESS_MODE_INHERIT", out)
    out = re.sub(r"\bpause_mode\b", "process_mode", out)
    for name in COLOR_CONSTANTS:
        out = re.sub(rf"\bColor\.{name}\b", f"Color.{name.upper()}", out)
    out = CONNECT4_RE.sub(_connect4_repl, out)
    out = CONNECT3_RE.sub(_connect3_repl, out)
    out = YIELD_RE.sub(_yield_repl, out)
    out = PACKED_JOIN_RE.sub(r"\2.join(PackedStringArray(\1))", out)
    out = re.sub(r"\bFile\.(READ|WRITE|READ_WRITE)\b", r"FileAccess.\1", out)
    out = FILE_NEW_RE.sub("", out)
    out = FILE_OPEN_RE.sub(r"\1var \2 = FileAccess.open(\3, FileAccess.\4)", out)
    out = re.sub(r"\b\w+\.file_exists\s*\(", "FileAccess.file_exists(", out)
    out = JSON_PARSE_IF_RE.sub(
        r"var \1 = JSON.parse_string(\2)\n\3if \1 != null and typeof(\1) == TYPE_DICTIONARY:",
        out,
    )
    out = re.sub(r"\bjson\.result\b", "json", out)
    out = convert_enum_commas(out)
    return out


def residual_script_blockers(rel: str, text: str) -> list[dict[str, Any]]:
    residuals: list[dict[str, Any]] = []
    rules = (
        (r"\bFile\.new\s*\(", "File.new"),
        (r"\bDirectory\.new\s*\(", "Directory.new"),
        (r"\byield\s*\(", "yield"),
        (r"(?<!@)\bonready\s+var\b", "onready"),
        (r"\bPool(String|Byte|Int|Real|Vector2)Array\b", "PoolArray"),
        (r"\bpause_mode\b", "pause_mode"),
    )
    for pattern, name in rules:
        if re.search(pattern, text):
            residuals.append({"path": rel, "pattern": name})
    return residuals


def copy_and_convert_boot(
    recovered: Path,
    product: Path,
    *,
    main_scene: str = "res://scenes/seed.tscn",
) -> dict[str, Any]:
    recovered = Path(recovered)
    product = Path(product)
    before = tree_fingerprint(recovered)
    product.mkdir(parents=True, exist_ok=True)
    (product / "scenes").mkdir(parents=True, exist_ok=True)

    source_project = recovered / "project.godot"
    source_text = source_project.read_text(encoding="utf-8")
    converted = convert_project_godot(source_text, main_scene=main_scene)
    class_by_rel = {}
    for item in parse_global_classes(source_text):
        path = item["path"]
        if path.startswith("res://"):
            class_by_rel[path[len("res://"):]] = item["name"]
    (product / "project.godot").write_text(converted["text"], encoding="utf-8", newline="\n")

    globals_src = recovered / "Globals"
    globals_dst = product / "Globals"
    if globals_dst.exists():
        shutil.rmtree(globals_dst)
    scripts_converted = 0
    residuals: list[dict[str, Any]] = []
    copied_scripts: list[str] = []
    for src in sorted(p for p in globals_src.rglob("*") if p.is_file()):
        rel = src.relative_to(recovered).as_posix()
        dst = product / src.relative_to(recovered)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() == ".gd":
            text = convert_gdscript(src.read_text(encoding="utf-8", errors="replace"))
            class_name = class_by_rel.get(src.relative_to(recovered).as_posix())
            if class_name:
                text = inject_class_name(text, class_name)
            dst.write_text(text, encoding="utf-8", newline="\n")
            scripts_converted += 1
            copied_scripts.append("product/" + src.relative_to(recovered).as_posix())
            residuals.extend(residual_script_blockers(rel, text))
        else:
            shutil.copy2(src, dst)

    data_copied: list[str] = []
    for name in DATA_DIRS:
        src_dir = recovered / name
        if not src_dir.is_dir():
            continue
        dst_dir = product / name
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        data_copied.append(name)

    after = tree_fingerprint(recovered)
    if after != before:
        raise RuntimeError("04_recovered was modified by boot conversion")

    return {
        "autoloads": converted["autoloads"],
        "input_actions": converted["input_actions"],
        "scripts_converted": scripts_converted,
        "copied_scripts": copied_scripts,
        "data_copied": data_copied,
        "residuals": residuals,
        "main_scene": main_scene,
        "recovered_unmodified": True,
        "recovered_files": len(before),
    }


def classify_import_errors(engine: dict[str, Any], import_output: dict[str, Any] | None) -> list[dict[str, Any]]:
    status = engine.get("status")
    if status != "SUCCESS":
        return [{
            "category": "ENGINE",
            "severity": "blocker",
            "message": f"engine status {status}",
            "dependency": "godot_4_7_1_binary",
        }]
    if not import_output:
        return [{
            "category": "IMPORT",
            "severity": "blocker",
            "message": "import not run",
            "dependency": "godot_import",
        }]
    errors: list[dict[str, Any]] = []
    combined = (import_output.get("stdout") or "") + "\n" + (import_output.get("stderr") or "")
    for line in combined.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if "ERROR" in upper or "PARSE ERROR" in upper or "FAILED TO LOAD" in upper or "SCRIPT ERROR" in upper:
            errors.append({
                "category": "PARSE" if "PARSE" in upper else "IMPORT",
                "severity": "blocker",
                "message": stripped[:500],
                "dependency": "godot_import",
            })
        elif "WARNING" in upper:
            errors.append({
                "category": "IMPORT",
                "severity": "warning",
                "message": stripped[:500],
                "dependency": "godot_import",
            })
    if import_output.get("returncode") not in (0, None) and not any(e["severity"] == "blocker" for e in errors):
        errors.append({
            "category": "IMPORT",
            "severity": "blocker",
            "message": f"headless import exit {import_output.get('returncode')}",
            "dependency": "godot_import",
        })
    return errors


def build_wave_b_report(
    product: Path,
    conversion: dict[str, Any],
    engine: dict[str, Any] | None = None,
    import_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    engine = engine or {"status": "NOT_FOUND", "tool_missing": True}
    import_errors = classify_import_errors(engine, import_output)
    if engine.get("status") == "SUCCESS" and import_output is not None:
        import_status = "RAN"
        import_result = "ERRORS_CLASSIFIED" if any(e.get("severity") == "blocker" for e in import_errors) else "CLEAN"
    else:
        import_status = "NOT_RUN"
        import_result = engine.get("status") or "NOT_RUN"
    project_text = (product / "project.godot").read_text(encoding="utf-8") if (product / "project.godot").is_file() else ""
    return {
        "schema_version": 1,
        "task": "P1-WAVE-B",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_dir": "product",
        "project": {
            "godot4": "config_version=5" in project_text and 'PackedStringArray("4.7"' in project_text,
            "main_scene": conversion.get("main_scene"),
            "autoload_count": len(conversion.get("autoloads") or []),
            "input_action_count": len(conversion.get("input_actions") or []),
            "input_actions": conversion.get("input_actions") or [],
            "required_actions_present": all(
                a in (conversion.get("input_actions") or [])
                for a in ("dash", "interact", "move_left", "move_right", "move_up", "move_down")
            ),
        },
        "scripts_converted": conversion.get("scripts_converted"),
        "data_copied": conversion.get("data_copied"),
        "residuals": conversion.get("residuals"),
        "recovered_unmodified": conversion.get("recovered_unmodified"),
        "engine": {
            "status": engine.get("status"),
            "version": engine.get("version"),
            "resolved_via": engine.get("resolved_via"),
            "tool_missing": bool(engine.get("tool_missing") or engine.get("status") in {"NOT_FOUND", "TOOL_MISSING"}),
        },
        "import_parse": {
            "status": import_status,
            "result": import_result,
            "returncode": None if not import_output else import_output.get("returncode"),
            "errors": import_errors,
            "error_count": len(import_errors),
            "blocker_count": sum(1 for e in import_errors if e.get("severity") == "blocker"),
            "zero_errors_required": False,
        },
        "notes": [
            "Wave B converts Boot/Project/Autoload/Input only.",
            "Missing preloaded scenes/sounds are classified import errors, not silent success.",
            "04_recovered remains immutable.",
        ],
    }


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--recovered", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--import-parse", action="store_true")
    args = ap.parse_args(argv)

    root = (args.root or _repo_root_from_here()).resolve()
    recovered = (args.recovered or (root / "04_recovered")).resolve()
    product = (args.product or (root / "product")).resolve()
    out = (args.out or (root / "migration" / "conversion" / "wave_b_boot_report.json")).resolve()

    conversion = copy_and_convert_boot(recovered, product)

    bootstrap = root / "scripts" / "bootstrap"
    if str(bootstrap) not in sys.path:
        sys.path.insert(0, str(bootstrap))
    from product_toolchain import discover_product_godot, run_headless_import  # type: ignore

    discovery = discover_product_godot(root)
    import_output = None
    if args.import_parse and discovery.get("engine", {}).get("status") == "SUCCESS":
        import_output = run_headless_import(discovery["engine"]["binary"], product)

    report = build_wave_b_report(product, conversion, engine=discovery.get("engine"), import_output=import_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "autoloads": report["project"]["autoload_count"],
        "input_actions": report["project"]["input_action_count"],
        "scripts_converted": report["scripts_converted"],
        "engine": report["engine"]["status"],
        "import_parse": report["import_parse"]["status"],
        "import_result": report["import_parse"]["result"],
        "recovered_unmodified": report["recovered_unmodified"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
