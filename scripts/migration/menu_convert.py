#!/usr/bin/env python3
"""P1-WAVE-C: convert Menu / Character / Save boot surface into product/.

Never writes 03_raw/** or 04_recovered/**. Does not rewrite the whole
project.godot — only run/main_scene. Zero import errors are not required.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from boot_convert import (  # type: ignore
    classify_import_errors,
    convert_gdscript,
    residual_script_blockers,
    tree_fingerprint,
)

ROOTS = (
    "Scenes/LoadGame.tscn",
    "Scenes/LoadGame.gd",
    "Scenes/Menu.tscn",
    "Scenes/Menu.gd",
    "Scenes/Popups/PopupBase.gd",
    "Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn",
    "Scenes/SoundEffect.tscn",
    "Themes/MainTheme.tres",
)

FORBIDDEN_PREFIXES = (
    "Scenes/Levels/",
    "Scenes/Mobs/",
    "Scenes/Skills/",
    "Scenes/Projectiles/",
    "Scenes/Player/",
    "Scenes/GeneEditor/",
    "Scenes/PassiveTree/",
    "Scenes/AreaSkill",
    "Scenes/Explosions/",
    "Scenes/GroundDegens/",
    "Scenes/KeystoneCycles/",
    "Scenes/Particles/",
    "Scenes/Pickups/",
    "Scenes/ShaderExplosions/",
    "Scenes/StatusEffects/",
    "Scenes/Interactables/",
    "Scenes/World.tscn",
    "Scenes/World.gd",
)

SKIP_SUFFIXES = {".import", ".uid"}
TEXT_SUFFIXES = {".gd", ".tscn", ".tres", ".godot", ".shader", ".gdshader", ".cfg"}
RES_RE = re.compile(r"res://([^\"'\s]+)")
EXT_LINE_RE = re.compile(r"^(\[ext_resource\s+)(.+?)(\])\s*$")
ATTR_RE = re.compile(r'([A-Za-z0-9_]+)=(?:"([^"]*)"|([^\s\]]+))')
TYPE_ATTR_RE = re.compile(r'\btype\s*=\s*"([A-Za-z0-9_]+)"')

EXT_TYPE_MAP = {
    "Texture": "Texture2D",
    "DynamicFontData": "FontFile",
    "DynamicFont": "FontFile",
    "StreamTexture": "CompressedTexture2D",
}
NODE_TYPE_MAP = {
    "KinematicBody2D": "CharacterBody2D",
    "Particles2D": "GPUParticles2D",
    "AnimatedSprite": "AnimatedSprite2D",
    "VisibilityNotifier2D": "VisibleOnScreenNotifier2D",
    "Position2D": "Marker2D",
    "TextureProgress": "TextureProgressBar",
    "Light2D": "PointLight2D",
    "YSort": "Node2D",
    "Reference": "RefCounted",
    "Sprite": "Sprite2D",
    "ToolButton": "Button",
}
PAUSE_MODE_MAP = {"0": "0", "1": "1", "2": "3"}


def res_to_rel(res_path: str) -> str:
    path = res_path.strip()
    if path.startswith("res://"):
        path = path[len("res://"):]
    return path.replace("\\", "/")


def product_rel(rel: str) -> str:
    """Seed already lives in product/scenes/; keep one case for export/CI."""
    rel = rel.replace("\\", "/")
    if rel.startswith("Scenes/"):
        return "scenes/" + rel[len("Scenes/"):]
    return rel


def rewrite_scenes_case(text: str) -> str:
    return text.replace("res://Scenes/", "res://scenes/")


def is_forbidden(rel: str, prefixes: Iterable[str] | None = None) -> bool:
    rel = rel.replace("\\", "/")
    prefixes = tuple(prefixes) if prefixes is not None else FORBIDDEN_PREFIXES
    return any(rel.startswith(p) or rel == p.rstrip("/") for p in prefixes)


def parse_attrs(blob: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for match in ATTR_RE.finditer(blob):
        key = match.group(1)
        out[key] = match.group(2) if match.group(2) is not None else match.group(3)
    return out


def convert_ext_resource_line(line: str) -> str:
    match = EXT_LINE_RE.match(line.rstrip("\n"))
    if not match:
        return line
    attrs = parse_attrs(match.group(2))
    typ = EXT_TYPE_MAP.get(attrs.get("type", ""), attrs.get("type", "Resource"))
    path = attrs.get("path", "")
    ident = attrs.get("id", "0").strip()
    ident = ident.strip('"')
    return f'[ext_resource type="{typ}" path="{path}" id="{ident}"]\n'


def _rewrite_type_attr(match: re.Match[str]) -> str:
    original = match.group(1)
    mapped = NODE_TYPE_MAP.get(original, EXT_TYPE_MAP.get(original, original))
    return f'type="{mapped}"'


def convert_scene_text(text: str) -> str:
    out = text.replace("format=2", "format=3")
    out = re.sub(
        r'(\[node [^\]]*?)type="YSort"([^\]]*\])',
        r"\1type=\"Node2D\"\2\ny_sort_enabled = true",
        out,
    )
    lines: list[str] = []
    for line in out.splitlines(keepends=True):
        if line.startswith("[ext_resource"):
            newline = "\n" if line.endswith("\n") else ""
            converted = convert_ext_resource_line(line)
            if not converted.endswith("\n") and newline:
                converted += newline
            lines.append(converted)
        else:
            lines.append(line)
    out = "".join(lines)
    out = re.sub(r"ExtResource\(\s*([0-9]+)\s*\)", r'ExtResource("\1")', out)
    out = re.sub(r"SubResource\(\s*([0-9]+)\s*\)", r'SubResource("\1")', out)
    out = TYPE_ATTR_RE.sub(_rewrite_type_attr, out)
    out = re.sub(r"\bmargin_left\b", "offset_left", out)
    out = re.sub(r"\bmargin_right\b", "offset_right", out)
    out = re.sub(r"\bmargin_top\b", "offset_top", out)
    out = re.sub(r"\bmargin_bottom\b", "offset_bottom", out)
    out = re.sub(r"\brect_min_size\b", "custom_minimum_size", out)
    out = re.sub(r"\bcustom_styles/", "theme_override_styles/", out)
    out = re.sub(r"\bcustom_fonts/", "theme_override_fonts/", out)
    out = re.sub(r"\bcustom_colors/", "theme_override_colors/", out)
    out = re.sub(r"\bcustom_constants/", "theme_override_constants/", out)
    out = re.sub(r"(?m)^expand = true\s*$", "expand_mode = 1", out)
    out = re.sub(
        r"(?m)^pause_mode = ([0-2])\s*$",
        lambda m: f"process_mode = {PAUSE_MODE_MAP.get(m.group(1), m.group(1))}",
        out,
    )

    def _compact(match: re.Match[str]) -> str:
        args = ", ".join(a.strip() for a in match.group(2).split(","))
        return f"{match.group(1)}({args})"

    out = re.sub(r"(Vector2|Vector3|Color|Rect2)\(\s*([^)]*?)\s*\)", _compact, out)
    out = re.sub(r"\bPoolRealArray\b", "PackedFloat32Array", out)
    out = re.sub(r"\bPoolVector2Array\b", "PackedVector2Array", out)
    out = re.sub(r"\bPoolStringArray\b", "PackedStringArray", out)
    out = re.sub(r"\bPoolIntArray\b", "PackedInt32Array", out)
    out = re.sub(r"\bshader_param/", "shader_parameter/", out)
    return out


def extract_res_paths(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for match in RES_RE.finditer(text):
        rel = match.group(1).replace("\\", "/")
        if rel not in seen:
            seen.add(rel)
            found.append(rel)
    return found


def collect_menu_files(
    recovered: Path,
    roots: Iterable[str] | None = None,
    forbidden: Iterable[str] | None = None,
) -> list[str]:
    recovered = Path(recovered)
    queue = [res_to_rel(r) for r in (roots or ROOTS)]
    seen: set[str] = set()
    ordered: list[str] = []
    while queue:
        rel = queue.pop(0)
        if rel in seen or is_forbidden(rel, forbidden):
            continue
        src = recovered / rel
        if not src.is_file():
            seen.add(rel)
            continue
        if src.suffix.lower() in SKIP_SUFFIXES:
            continue
        seen.add(rel)
        ordered.append(rel)
        if src.suffix.lower() in TEXT_SUFFIXES:
            text = src.read_text(encoding="utf-8", errors="replace")
            for dep in extract_res_paths(text):
                if dep not in seen and not is_forbidden(dep, forbidden):
                    queue.append(dep)
    return ordered


def convert_file_text(rel: str, text: str) -> str:
    lower = rel.replace("\\", "/").lower()
    if lower.endswith(".gd"):
        return convert_gdscript(text)
    if lower.endswith((".tscn", ".tres")):
        return convert_scene_text(text)
    return text


def set_main_scene(project_text: str, scene: str) -> str:
    if re.search(r"(?m)^run/main_scene=", project_text):
        return re.sub(r'(?m)^run/main_scene=.*$', f'run/main_scene="{scene}"', project_text)
    if "[application]" in project_text:
        return project_text.replace("[application]", f'[application]\nrun/main_scene="{scene}"', 1)
    return project_text + f'\n[application]\nrun/main_scene="{scene}"\n'


def copy_and_convert_menu(
    recovered: Path,
    product: Path,
    *,
    main_scene: str = "res://scenes/LoadGame.tscn",
) -> dict[str, Any]:
    recovered = Path(recovered)
    product = Path(product)
    before = tree_fingerprint(recovered)
    files = collect_menu_files(recovered)
    copied: list[str] = []
    converted: list[str] = []
    binaries: list[str] = []
    missing: list[str] = []
    residuals: list[dict[str, Any]] = []

    for rel in files:
        src = recovered / rel
        dest_rel = product_rel(rel)
        dst = product / dest_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in TEXT_SUFFIXES:
            text = rewrite_scenes_case(convert_file_text(rel, src.read_text(encoding="utf-8", errors="replace")))
            dst.write_text(text, encoding="utf-8", newline="\n")
            converted.append(dest_rel)
            if src.suffix.lower() == ".gd":
                residuals.extend(residual_script_blockers(dest_rel, text))
        else:
            shutil.copy2(src, dst)
            binaries.append(dest_rel)
        copied.append(dest_rel)

    # Globals already copied in Wave B still point at res://Scenes/; fold to scenes/.
    globals_dir = product / "Globals"
    if globals_dir.is_dir():
        for path in globals_dir.rglob("*.gd"):
            text = path.read_text(encoding="utf-8")
            folded = rewrite_scenes_case(text)
            if folded != text:
                path.write_text(folded, encoding="utf-8", newline="\n")

    main_scene = rewrite_scenes_case(main_scene)
    project_path = product / "project.godot"
    if project_path.is_file():
        project_path.write_text(
            set_main_scene(project_path.read_text(encoding="utf-8"), main_scene),
            encoding="utf-8",
            newline="\n",
        )

    after = tree_fingerprint(recovered)
    if after != before:
        raise RuntimeError("04_recovered was modified by menu conversion")

    for rel in files:
        if not (recovered / rel).is_file():
            missing.append(rel)

    return {
        "main_scene": main_scene,
        "files_copied": len(copied),
        "copied": copied,
        "converted_text_files": converted,
        "binaries": binaries,
        "missing": missing,
        "residuals": residuals,
        "recovered_unmodified": True,
    }


def build_wave_c_report(
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
    required = [
        "scenes/LoadGame.tscn",
        "scenes/LoadGame.gd",
        "scenes/Menu.tscn",
        "scenes/Menu.gd",
        "scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn",
        "scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.gd",
    ]
    present = {rel: (product / rel).is_file() for rel in required}
    loadgame = product / "scenes" / "LoadGame.tscn"
    load_text = loadgame.read_text(encoding="utf-8") if loadgame.is_file() else ""
    return {
        "schema_version": 1,
        "task": "P1-WAVE-C",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_dir": "product",
        "project": {
            "main_scene": conversion.get("main_scene"),
            "main_scene_in_project": 'run/main_scene="res://scenes/LoadGame.tscn"' in project_text,
            "loadgame_format3": "format=3" in load_text,
            "required_present": present,
            "all_required_present": all(present.values()),
        },
        "files_copied": conversion.get("files_copied"),
        "converted_text_files": len(conversion.get("converted_text_files") or []),
        "binaries": len(conversion.get("binaries") or []),
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
            "Wave C converts Menu / Character Select / Save boot surface only.",
            "Missing combat/world preloads remain classified errors.",
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
    out = (args.out or (root / "migration" / "conversion" / "wave_c_menu_report.json")).resolve()

    conversion = copy_and_convert_menu(recovered, product)

    bootstrap = root / "scripts" / "bootstrap"
    if str(bootstrap) not in sys.path:
        sys.path.insert(0, str(bootstrap))
    from product_toolchain import discover_product_godot, run_headless_import  # type: ignore

    discovery = discover_product_godot(root)
    import_output = None
    if args.import_parse and discovery.get("engine", {}).get("status") == "SUCCESS":
        import_output = run_headless_import(discovery["engine"]["binary"], product)

    report = build_wave_c_report(product, conversion, engine=discovery.get("engine"), import_output=import_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "files_copied": report["files_copied"],
        "main_scene": report["project"]["main_scene"],
        "all_required_present": report["project"]["all_required_present"],
        "engine": report["engine"]["status"],
        "import_parse": report["import_parse"]["status"],
        "import_result": report["import_parse"]["result"],
        "recovered_unmodified": report["recovered_unmodified"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
