#!/usr/bin/env python3
"""P1-X1: repeatable Godot 3.5.3 → 4.7.1 incompatibility inventory + blocker DAG.

Pure functions over a recovered tree (or fixtures). Never writes 03_raw / 04_recovered.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCAN_SUFFIXES = {".gd", ".tscn", ".tres", ".godot", ".shader", ".gdshader", ".cfg"}

# (regex, rule_id, severity, godot4_dependency)
SCRIPT_RULES: list[tuple[re.Pattern[str], str, str, str]] = [
    (re.compile(r"\byield\s*\("), "yield_to_await", "blocker", "await"),
    (re.compile(r"\bfuncref\s*\("), "funcref_to_callable", "blocker", "Callable"),
    (re.compile(r"\.instance\s*\("), "packedscene_instance", "blocker", "instantiate"),
    (re.compile(r"\bonready\s+var\b"), "onready", "warning", "@onready"),
    (re.compile(r"\bexport\s*\("), "export_hint", "warning", "@export"),
    (re.compile(r"\bsetget\b"), "setget", "warning", "property_getter_setter"),
    (re.compile(r"\bKinematicBody2D\b"), "kinematic_body_2d", "blocker", "CharacterBody2D"),
    (re.compile(r"\bKinematicBody\b"), "kinematic_body_3d", "blocker", "CharacterBody3D"),
    (re.compile(r"\bParticles2D\b"), "particles2d", "blocker", "GPUParticles2D"),
    (re.compile(r"\bAnimatedSprite\b(?!2D)"), "animated_sprite", "blocker", "AnimatedSprite2D"),
    (re.compile(r"\bYSort\b"), "ysort", "blocker", "y_sort_enabled"),
    (re.compile(r"\bVisibilityNotifier2D\b"), "visibility_notifier", "blocker", "VisibleOnScreenNotifier2D"),
    (re.compile(r"\bPosition2D\b"), "position2d", "blocker", "Marker2D"),
    (re.compile(r"\bFile\s*\.\s*new\s*\("), "file_new", "blocker", "FileAccess"),
    (re.compile(r"\bDirectory\s*\.\s*new\s*\("), "directory_new", "blocker", "DirAccess"),
    (re.compile(r"\bJSON\.print\b"), "json_print", "blocker", "JSON.stringify"),
    (re.compile(r"\bJSON\.parse\b"), "json_parse", "warning", "JSON.parse_string"),
    (re.compile(r"\bPoolStringArray\b"), "pool_string_array", "blocker", "PackedStringArray"),
    (re.compile(r"\bPoolByteArray\b"), "pool_byte_array", "blocker", "PackedByteArray"),
    (re.compile(r"\bPoolVector2Array\b"), "pool_vector2_array", "blocker", "PackedVector2Array"),
    (re.compile(r"\bPoolRealArray\b"), "pool_real_array", "blocker", "PackedFloat32Array"),
    (re.compile(r"\bPoolIntArray\b"), "pool_int_array", "blocker", "PackedInt32Array"),
    (re.compile(r"\bVisualServer\b"), "visual_server", "blocker", "RenderingServer"),
    (re.compile(r"\bPhysics2DServer\b"), "physics2d_server", "blocker", "PhysicsServer2D"),
    (re.compile(r"\bOS\.get_ticks_msec\b"), "os_ticks", "warning", "Time.get_ticks_msec"),
    (re.compile(r"\bOS\.get_unix_time\b"), "os_unix_time", "warning", "Time.get_unix_time_from_system"),
    (re.compile(r"\bColor\.(white|black|red|green|blue|transparent|yellow|gray|grey)\b"), "color_constant", "warning", "Color.UPPERCASE"),
    (re.compile(r"\.connect\s*\(\s*['\"]"), "connect_string", "warning", "Callable.connect"),
    (re.compile(r"\bpause_mode\b"), "pause_mode", "warning", "process_mode"),
    (re.compile(r"(?m)^tool\s*$"), "tool_keyword", "warning", "@tool"),
    (re.compile(r"\bextends\s+Reference\b"), "reference_class", "blocker", "RefCounted"),
    (re.compile(r"\.change_scene\s*\("), "change_scene", "blocker", "change_scene_to_file"),
    (re.compile(r"\brand_range\s*\("), "rand_range", "warning", "randf_range"),
    (re.compile(r"\bstr2var\b"), "str2var", "warning", "str_to_var"),
    (re.compile(r"\bvar2str\b"), "var2str", "warning", "var_to_str"),
    (re.compile(r"\bparse_json\b"), "parse_json", "blocker", "JSON.parse_string"),
    (re.compile(r"\bto_json\b"), "to_json", "blocker", "JSON.stringify"),
    (re.compile(r"\bTextureProgress\b"), "texture_progress", "blocker", "TextureProgressBar"),
    (re.compile(r"\bLight2D\b"), "light2d", "blocker", "PointLight2D"),
    (re.compile(r"\bNavigation2D\b"), "navigation2d", "blocker", "NavigationRegion2D"),
    (re.compile(r"\bTween\.new\s*\("), "tween_new", "warning", "create_tween"),
]

SCENE_TYPES: dict[str, tuple[str, str]] = {
    "KinematicBody2D": ("CharacterBody2D", "blocker"),
    "KinematicBody": ("CharacterBody3D", "blocker"),
    "Particles2D": ("GPUParticles2D", "blocker"),
    "AnimatedSprite": ("AnimatedSprite2D", "blocker"),
    "YSort": ("y_sort_enabled", "blocker"),
    "VisibilityNotifier2D": ("VisibleOnScreenNotifier2D", "blocker"),
    "VisibilityEnabler2D": ("VisibleOnScreenEnabler2D", "blocker"),
    "Position2D": ("Marker2D", "blocker"),
    "Light2D": ("PointLight2D", "blocker"),
    "TextureProgress": ("TextureProgressBar", "blocker"),
    "ToolButton": ("Button", "warning"),
    "Spatial": ("Node3D", "blocker"),
    "Sprite": ("Sprite2D", "warning"),
    "Navigation2D": ("NavigationRegion2D", "blocker"),
    "NavigationPolygonInstance": ("NavigationRegion2D", "blocker"),
    "Reference": ("RefCounted", "blocker"),
    "Tween": ("Tween", "warning"),
}

RESOURCE_RULES: list[tuple[re.Pattern[str], str, str, str]] = [
    (re.compile(r"\bformat\s*=\s*2\b"), "resource_format_2", "blocker", "resource_format_3"),
    (re.compile(r"\bProceduralSky\b"), "procedural_sky", "blocker", "Sky"),
    (re.compile(r"\bDynamicFont(Data)?\b"), "dynamic_font", "blocker", "FontFile"),
    (re.compile(r"\bStreamTexture\b"), "stream_texture", "blocker", "CompressedTexture2D"),
    (re.compile(r"\bParticlesMaterial\b"), "particles_material", "blocker", "ParticleProcessMaterial"),
    (re.compile(r"\bSpatialMaterial\b"), "spatial_material", "blocker", "StandardMaterial3D"),
    (re.compile(r"\bhint_color\b"), "hint_color", "warning", "source_color"),
    (re.compile(r"\bGradientTexture\b(?!1D|2D)"), "gradient_texture", "warning", "GradientTexture1D"),
]

SETTINGS_RULES: list[tuple[re.Pattern[str], str, str, str]] = [
    (re.compile(r"(?m)^config_version\s*=\s*4\s*$"), "config_version_4", "blocker", "config_version_5"),
    (re.compile(r"_global_script_classes\s*="), "global_script_classes", "blocker", "class_name"),
    (re.compile(r"window/size/width\s*="), "window_width", "blocker", "window/size/viewport_width"),
    (re.compile(r"window/size/height\s*="), "window_height", "blocker", "window/size/viewport_height"),
    (re.compile(r"window/size/fullscreen\s*="), "window_fullscreen", "warning", "window/size/mode"),
    (re.compile(r"\bPoolStringArray\b"), "pool_string_array", "blocker", "PackedStringArray"),
    (re.compile(r"(?m)^\[gdnative\]\s*$"), "gdnative", "blocker", "GDExtension"),
    (re.compile(r"Color\(\s+\d"), "color_spaces", "warning", "Color_no_spaces"),
    (re.compile(r"Object\(InputEvent"), "input_object_legacy", "blocker", "input_map_godot4"),
]

TYPE_ATTR_RE = re.compile(r'\btype\s*=\s*"([A-Za-z0-9_]+)"')
FORMAT_HEADER_RE = re.compile(r"\[gd_scene[^\]]*format\s*=\s*2")
EXT_RESOURCE_PATH_RE = re.compile(r"\[ext_resource[^\]]*path\s*=")


def _item(
    category: str,
    path: str,
    severity: str,
    dependency: str,
    rule: str,
    line: int | None = None,
    count: int = 1,
    detail: str = "",
) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "category": category,
        "path": path.replace("\\", "/"),
        "severity": severity,
        "dependency": dependency,
        "rule": rule,
        "count": count,
    }
    if line is not None:
        rec["line"] = line
    if detail:
        rec["detail"] = detail
    return rec


def _collect_regex(category: str, path: str, text: str, rules: Iterable[tuple[re.Pattern[str], str, str, str]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    lines = text.splitlines()
    for pattern, rule, severity, dependency in rules:
        hits: list[int] = []
        for idx, line in enumerate(lines, 1):
            if pattern.search(line):
                hits.append(idx)
        if not hits and pattern.search(text):
            hits = [1]
        if hits:
            items.append(_item(category, path, severity, dependency, rule, line=hits[0], count=len(hits)))
    return items


def scan_script_text(path: str, text: str) -> list[dict[str, Any]]:
    return _collect_regex("Script", path, text, SCRIPT_RULES)


def scan_scene_text(path: str, text: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if FORMAT_HEADER_RE.search(text) or re.search(r"\[gd_scene[^\]]*format\s*=\s*2", text):
        items.append(_item("Scene", path, "blocker", "scene_format_3", "scene_format_2", line=1))
    if EXT_RESOURCE_PATH_RE.search(text) and "uid=" not in text.split("\n", 1)[0]:
        items.append(_item("Scene", path, "warning", "ext_resource_uid", "ext_resource_path", line=1))
    counts: dict[str, list[int]] = defaultdict(list)
    for idx, line in enumerate(text.splitlines(), 1):
        m = TYPE_ATTR_RE.search(line)
        if not m:
            continue
        ntype = m.group(1)
        if ntype in SCENE_TYPES:
            counts[ntype].append(idx)
    for ntype, lines in counts.items():
        dep, severity = SCENE_TYPES[ntype]
        items.append(_item("Scene", path, severity, dep, f"node_type_{ntype}", line=lines[0], count=len(lines)))
    return items


def scan_resource_text(path: str, text: str) -> list[dict[str, Any]]:
    return _collect_regex("Resource", path, text, RESOURCE_RULES)


def scan_settings_text(path: str, text: str) -> list[dict[str, Any]]:
    return _collect_regex("Settings", path, text, SETTINGS_RULES)


def scan_file_text(path: str, text: str) -> list[dict[str, Any]]:
    lower = path.replace("\\", "/").lower()
    if lower.endswith(".gd"):
        return scan_script_text(path, text)
    if lower.endswith(".tscn"):
        return scan_scene_text(path, text)
    if lower.endswith(".godot"):
        return scan_settings_text(path, text)
    if lower.endswith((".tres", ".shader", ".gdshader", ".cfg")):
        items = scan_resource_text(path, text)
        if lower.endswith(".cfg"):
            items.extend(scan_settings_text(path, text))
        return items
    return []


def iter_scan_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in SCAN_SUFFIXES:
            yield path


def scan_tree(root: Path, recovered_label: str | None = None) -> dict[str, Any]:
    root = Path(root)
    items: list[dict[str, Any]] = []
    files_scanned = 0
    for path in iter_scan_files(root):
        files_scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()
        if recovered_label:
            rel = f"{recovered_label.rstrip('/')}/{rel}"
        items.extend(scan_file_text(rel, text))
    categories = sorted({i["category"] for i in items})
    return {
        "schema_version": 1,
        "task": "P1-X1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_root": recovered_label or root.as_posix(),
        "files_scanned": files_scanned,
        "item_count": len(items),
        "categories": categories,
        "items": items,
        "blocker_dag": build_blocker_dag(items),
    }


def build_blocker_dag(items: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for item in items:
        key = (item["category"], item["dependency"])
        node = groups.get(key)
        if node is None:
            node = {
                "id": f"{item['category']}:{item['dependency']}",
                "category": item["category"],
                "dependency": item["dependency"],
                "severity": item["severity"],
                "count": 0,
                "example_paths": [],
            }
            groups[key] = node
        node["count"] += int(item.get("count") or 1)
        if item.get("severity") == "blocker":
            node["severity"] = "blocker"
        path = item.get("path")
        if path and path not in node["example_paths"] and len(node["example_paths"]) < 5:
            node["example_paths"].append(path)

    nodes = sorted(groups.values(), key=lambda n: (n["category"], n["dependency"]))
    edges: list[dict[str, str]] = []
    settings_ids = [n["id"] for n in nodes if n["category"] == "Settings"]
    script_ids = [n["id"] for n in nodes if n["category"] == "Script"]
    scene_ids = [n["id"] for n in nodes if n["category"] == "Scene"]
    resource_ids = [n["id"] for n in nodes if n["category"] == "Resource"]

    root_settings = next((i for i in settings_ids if i.endswith("config_version_5") or "config_version" in i), None)
    if root_settings:
        for other in script_ids + scene_ids + resource_ids + [i for i in settings_ids if i != root_settings]:
            edges.append({"from": root_settings, "to": other, "reason": "engine/settings upgrade precedes content conversion"})
    for s in script_ids:
        dep = s.split(":", 1)[-1]
        for sc in scene_ids:
            if sc.endswith(dep) or dep in sc:
                edges.append({"from": s, "to": sc, "reason": "script node type and scene node type must convert together"})
    for r in resource_ids:
        for sc in scene_ids:
            edges.append({"from": r, "to": sc, "reason": "scene instances depend on converted resources"})
            break

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--recovered", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    root = (args.root or _repo_root_from_here()).resolve()
    recovered = (args.recovered or (root / "04_recovered")).resolve()
    out = (args.out or (root / "migration" / "inventory" / "compat_inventory.json")).resolve()
    if not recovered.is_dir():
        print(json.dumps({"verdict": "FAIL", "error": f"recovered tree missing: {recovered}"}), flush=True)
        return 2
    report = scan_tree(recovered, recovered_label="04_recovered")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "files_scanned": report["files_scanned"],
        "item_count": report["item_count"],
        "categories": report["categories"],
        "dag_nodes": report["blocker_dag"]["node_count"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
