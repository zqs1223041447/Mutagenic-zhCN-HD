#!/usr/bin/env python3
"""P1-WAVE-D: convert World / Spawn / Movement into product/.

Never writes 03_raw/** or 04_recovered/**. Does not change main_scene
(LoadGame remains the boot scene). Zero import errors are not required.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from boot_convert import classify_import_errors, residual_script_blockers, tree_fingerprint  # type: ignore
from menu_convert import (  # type: ignore
    TEXT_SUFFIXES,
    SKIP_SUFFIXES,
    collect_menu_files,
    convert_file_text,
    product_rel,
    rewrite_scenes_case,
)

ROOTS = (
    "Scenes/World.tscn",
    "Scenes/World.gd",
    "Scenes/Player/Player.tscn",
    "Scenes/Levels/BaseLevel.tscn",
    "Scenes/Levels/BaseLevel.gd",
    "Scenes/Levels/Default/DefaultLevel.tscn",
    "Scenes/Levels/SpawnLocation.tscn",
    "Scenes/Levels/LevelLoader.tscn",
    "Scenes/Levels/NavMesh.tscn",
    "Scenes/GUI/GUI.tscn",
    "Scenes/Stats.tscn",
    "Scenes/Popups/EscapeMenu.tscn",
    "Scenes/IdleFrame.gd",
    "Shaders/ScreenSpaceGI.tres",
)

FORBIDDEN = (
    "Scenes/Skills/",
    "Scenes/Projectiles/",
    "Scenes/GeneEditor/",
    "Scenes/PassiveTree/",
    "Scenes/Mobs/",
    "Scenes/StatusEffects/",
    "Scenes/AreaSkill",
    "Scenes/Explosions/",
    "Scenes/GroundDegens/",
    "Scenes/KeystoneCycles/",
    "Scenes/ShaderExplosions/",
)


def copy_and_convert_world(recovered: Path, product: Path) -> dict[str, Any]:
    recovered = Path(recovered)
    product = Path(product)
    before = tree_fingerprint(recovered)
    files = collect_menu_files(recovered, roots=ROOTS, forbidden=FORBIDDEN)
    copied: list[str] = []
    converted: list[str] = []
    binaries: list[str] = []
    residuals: list[dict[str, Any]] = []

    for rel in files:
        src = recovered / rel
        dest_rel = product_rel(rel)
        dst = product / dest_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in SKIP_SUFFIXES:
            continue
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

    after = tree_fingerprint(recovered)
    if after != before:
        raise RuntimeError("04_recovered was modified by world conversion")

    return {
        "files_copied": len(copied),
        "copied": copied,
        "converted_text_files": converted,
        "binaries": binaries,
        "residuals": residuals,
        "recovered_unmodified": True,
        "main_scene_unchanged": True,
    }


def build_wave_d_report(
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
    required = [
        "scenes/World.tscn",
        "scenes/World.gd",
        "scenes/Player/Player.tscn",
        "scenes/Player/Player.gd",
        "scenes/Levels/BaseLevel.tscn",
        "scenes/Levels/BaseLevel.gd",
        "scenes/Levels/SpawnLocation.tscn",
        "scenes/Levels/Default/DefaultLevel.tscn",
    ]
    present = {rel: (product / rel).is_file() for rel in required}
    world = product / "scenes" / "World.tscn"
    world_text = world.read_text(encoding="utf-8") if world.is_file() else ""
    player_gd = product / "scenes" / "Player" / "Player.gd"
    player_text = player_gd.read_text(encoding="utf-8") if player_gd.is_file() else ""
    project = (product / "project.godot").read_text(encoding="utf-8") if (product / "project.godot").is_file() else ""
    return {
        "schema_version": 1,
        "task": "P1-WAVE-D",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_dir": "product",
        "project": {
            "main_scene_still_loadgame": 'run/main_scene="res://scenes/LoadGame.tscn"' in project,
            "world_format3": "format=3" in world_text,
            "ysort_folded": 'type="YSort"' not in world_text and "y_sort_enabled = true" in world_text,
            "dash_impulse_present": "dash" in player_text and "apply_central_impulse" in player_text,
            "mouse_button_godot4": "MOUSE_BUTTON_LEFT" in player_text,
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
            "Wave D converts World / Player movement (incl. Dash) / BaseLevel spawn.",
            "Skills, projectiles, and mobs are not this wave; missing preloads stay classified.",
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
    out = (args.out or (root / "migration" / "conversion" / "wave_d_world_report.json")).resolve()

    conversion = copy_and_convert_world(recovered, product)

    bootstrap = root / "scripts" / "bootstrap"
    if str(bootstrap) not in sys.path:
        sys.path.insert(0, str(bootstrap))
    from product_toolchain import discover_product_godot, run_headless_import  # type: ignore

    discovery = discover_product_godot(root)
    import_output = None
    if args.import_parse and discovery.get("engine", {}).get("status") == "SUCCESS":
        import_output = run_headless_import(discovery["engine"]["binary"], product)

    report = build_wave_d_report(product, conversion, engine=discovery.get("engine"), import_output=import_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out),
        "files_copied": report["files_copied"],
        "all_required_present": report["project"]["all_required_present"],
        "dash_impulse_present": report["project"]["dash_impulse_present"],
        "engine": report["engine"]["status"],
        "import_parse": report["import_parse"]["status"],
        "import_result": report["import_parse"]["result"],
        "recovered_unmodified": report["recovered_unmodified"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
