#!/usr/bin/env python3
"""P1-WAVE-E: convert Combat / Projectile / Status foundation into product/.

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
from typing import Any, Iterable

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from boot_convert import classify_import_errors, residual_script_blockers, tree_fingerprint  # type: ignore
from menu_convert import (  # type: ignore
    SKIP_SUFFIXES,
    TEXT_SUFFIXES,
    collect_menu_files,
    convert_file_text,
    product_rel,
    res_to_rel,
    rewrite_scenes_case,
)

ROOTS = (
    "Scenes/Skills/GenericSkill.gd",
    "Scenes/Projectiles/Projectile.tscn",
    "Scenes/Projectiles/Projectile.gd",
    "Scenes/StatusEffects/BaseEffect.gd",
    "Scenes/StatusEffects/Generic/",
)

FORBIDDEN = (
    "Scenes/Mobs/",
    "Scenes/Levels/",
    "Scenes/Player/",
    "Scenes/World.tscn",
    "Scenes/World.gd",
    "Scenes/GeneEditor/",
    "Scenes/PassiveTree/",
)


def _normalize_roots(recovered: Path, roots: Iterable[str]) -> list[str]:
    expanded: list[str] = []
    for r in roots:
        rel = res_to_rel(r)
        p = recovered / rel
        if p.is_dir():
            for child in sorted(p.rglob("*")):
                if child.is_file():
                    expanded.append(child.relative_to(recovered).as_posix())
        else:
            expanded.append(rel)
    return expanded


def copy_and_convert_combat(
    recovered: Path,
    product: Path,
    roots: Iterable[str] | None = None,
    forbidden: Iterable[str] | None = None,
) -> dict[str, Any]:
    recovered = Path(recovered)
    product = Path(product)
    before = tree_fingerprint(recovered)
    expanded_roots = _normalize_roots(recovered, roots or ROOTS)
    forbidden_prefixes = forbidden if forbidden is not None else FORBIDDEN
    files = collect_menu_files(recovered, roots=expanded_roots, forbidden=forbidden_prefixes)
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
        raise RuntimeError("04_recovered was modified by combat conversion")

    return {
        "files_copied": len(copied),
        "copied": copied,
        "converted_text_files": converted,
        "binaries": binaries,
        "residuals": residuals,
        "recovered_unmodified": True,
        "main_scene_unchanged": True,
    }


def build_wave_e_report(
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
        "scenes/Skills/GenericSkill.gd",
        "scenes/Projectiles/Projectile.tscn",
        "scenes/Projectiles/Projectile.gd",
        "scenes/StatusEffects/BaseEffect.gd",
    ]
    present = {rel: (product / rel).is_file() for rel in required}
    projectile_tscn = product / "scenes" / "Projectiles" / "Projectile.tscn"
    projectile_text = projectile_tscn.read_text(encoding="utf-8") if projectile_tscn.is_file() else ""
    generic_skill_gd = product / "scenes" / "Skills" / "GenericSkill.gd"
    generic_skill_text = generic_skill_gd.read_text(encoding="utf-8") if generic_skill_gd.is_file() else ""
    player_gd = product / "scenes" / "Player" / "Player.gd"
    player_text = player_gd.read_text(encoding="utf-8") if player_gd.is_file() else ""
    project = (product / "project.godot").read_text(encoding="utf-8") if (product / "project.godot").is_file() else ""

    return {
        "schema_version": 1,
        "task": "P1-WAVE-E",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_dir": "product",
        "project": {
            "main_scene_still_loadgame": 'run/main_scene="res://scenes/LoadGame.tscn"' in project,
            "projectile_format3": "format=3" in projectile_text,
            "generic_skill_callable": "Callable(" in generic_skill_text or "connect(" in generic_skill_text,
            "dash_impulse_present": "dash" in player_text and "apply_central_impulse" in player_text,
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
            "Wave E converts Combat / Projectile / Status effect foundation.",
            "Mob AI and full skill tree are subsequent waves; missing preloads stay classified.",
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
    out = (args.out or (root / "migration" / "conversion" / "wave_e_combat_report.json")).resolve()

    conversion = copy_and_convert_combat(recovered, product)

    bootstrap = root / "scripts" / "bootstrap"
    if str(bootstrap) not in sys.path:
        sys.path.insert(0, str(bootstrap))
    from product_toolchain import discover_product_godot, run_headless_import  # type: ignore

    discovery = discover_product_godot(root)
    import_output = None
    if args.import_parse and discovery.get("engine", {}).get("status") == "SUCCESS":
        import_output = run_headless_import(discovery["engine"]["binary"], product)

    report = build_wave_e_report(product, conversion, engine=discovery.get("engine"), import_output=import_output)
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
