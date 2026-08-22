#!/usr/bin/env python3
"""P1-X0: write a Godot 4.7.1 product seed and a classified conversion report.

Never writes 03_raw/** or 04_recovered/**. Headless import is optional and is
NOT_RUN when Godot 4.7.1 is missing — that is recorded, never rewritten as PASS.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONFIG_VERSION_RE = re.compile(r"(?m)^config_version\s*=\s*(\d+)\s*$")
FEATURES_RE = re.compile(r'config/features\s*=\s*PackedStringArray\((.*)\)')
NAME_RE = re.compile(r'(?m)^config/name\s*=\s*"(.*)"\s*$')

SEED_PROJECT = """; Engine configuration file.
; P1-X0 Godot 4.7.1 conversion seed. Generated; edit via tools, not by hand.

config_version=5

[application]

config/name="Mutagenic"
config/description="Godot 4.7.1 Product conversion seed (P1-X0)"
run/main_scene="res://scenes/seed.tscn"
config/features=PackedStringArray("4.7", "Forward Plus")
config/icon="res://icon.svg"

[display]

window/size/viewport_width=1280
window/size/viewport_height=800

[rendering]

renderer/rendering_method="forward_plus"
textures/canvas_textures/default_texture_filter=0
"""

SEED_SCENE = """[gd_scene format=3 uid="uid://bq8seedmutagenic"]

[node name="SeedRoot" type="Node2D"]
"""

SEED_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <rect width="128" height="128" fill="#0b0b0f"/>
  <rect x="16" y="16" width="96" height="96" fill="#1a1a24" stroke="#7cf0c2" stroke-width="4"/>
  <circle cx="64" cy="64" r="22" fill="#7cf0c2"/>
</svg>
"""

SEED_GITIGNORE = """.godot/
*.translation
"""


def parse_project_identity(text: str) -> dict[str, Any]:
    cv_match = CONFIG_VERSION_RE.search(text)
    config_version = int(cv_match.group(1)) if cv_match else None
    features_raw = None
    features: list[str] = []
    fm = FEATURES_RE.search(text)
    if fm:
        features_raw = fm.group(1)
        features = re.findall(r'"([^"]+)"', features_raw)
    name_m = NAME_RE.search(text)
    godot4 = bool(
        config_version is not None
        and config_version >= 5
        and not any(f.startswith("3.") for f in features)
        and (not features or any(f.startswith("4.") for f in features))
    )
    godot3 = bool(config_version is not None and config_version <= 4)
    return {
        "config_version": config_version,
        "features": features,
        "features_raw": features_raw,
        "name": name_m.group(1) if name_m else None,
        "is_godot4": godot4 and not godot3,
        "is_godot3": godot3,
    }


def is_godot4_project_text(text: str) -> bool:
    return bool(parse_project_identity(text)["is_godot4"])


def write_product_seed(product_dir: Path) -> dict[str, str]:
    product_dir = Path(product_dir)
    scenes = product_dir / "scenes"
    scenes.mkdir(parents=True, exist_ok=True)
    files = {
        "project.godot": SEED_PROJECT,
        "icon.svg": SEED_ICON,
        "scenes/seed.tscn": SEED_SCENE,
        ".gitignore": SEED_GITIGNORE,
    }
    written: dict[str, str] = {}
    for rel, content in files.items():
        path = product_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        written[rel] = path.as_posix()
    return written


def classify_engine_import_errors(engine: dict[str, Any], import_output: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    status = engine.get("status")
    if status in {"NOT_FOUND", "TOOL_MISSING"}:
        return [{
            "category": "ENGINE_MISSING",
            "path": "product/",
            "severity": "blocker",
            "dependency": "godot_4_7_1_binary",
            "message": "Godot 4.7.1 binary not found; headless import/parse was not executed",
        }]
    if status == "VERSION_MISMATCH":
        return [{
            "category": "ENGINE_VERSION",
            "path": "product/",
            "severity": "blocker",
            "dependency": "godot_4_7_1_binary",
            "message": f"Found Godot {engine.get('version')!r}, want 4.7.1",
        }]
    if status == "TOOL_FAILED":
        return [{
            "category": "ENGINE_FAILED",
            "path": "product/",
            "severity": "blocker",
            "dependency": "godot_4_7_1_binary",
            "message": engine.get("detail") or "Godot binary failed to run",
        }]
    if status == "MISSING_PRIVATE":
        return [{
            "category": "PRIVATE_ASSET",
            "path": "product/",
            "severity": "blocker",
            "dependency": "private_devkit",
            "message": "Private assets missing; Product engine invocation blocked",
        }]
    if status != "SUCCESS":
        return [{
            "category": "ENGINE_UNKNOWN",
            "path": "product/",
            "severity": "blocker",
            "dependency": "godot_4_7_1_binary",
            "message": f"Unexpected engine status {status!r}",
        }]
    errors: list[dict[str, Any]] = []
    if not import_output:
        return errors
    combined = (import_output.get("stdout") or "") + "\n" + (import_output.get("stderr") or "")
    for line in combined.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        upper = stripped.upper()
        if "ERROR" in upper or "PARSE ERROR" in upper or "FAILED TO LOAD" in upper or "SCRIPT ERROR" in upper:
            errors.append({
                "category": "PARSE" if "PARSE" in upper else "IMPORT",
                "path": "product/",
                "severity": "blocker",
                "dependency": "godot_import",
                "message": stripped[:500],
            })
        elif "WARNING" in upper:
            errors.append({
                "category": "IMPORT",
                "path": "product/",
                "severity": "warning",
                "dependency": "godot_import",
                "message": stripped[:500],
            })
    if import_output.get("returncode") not in (0, None) and not errors:
        errors.append({
            "category": "IMPORT",
            "path": "product/",
            "severity": "blocker",
            "dependency": "godot_import",
            "message": f"headless import exit {import_output.get('returncode')}",
        })
    return errors


def build_conversion_report(
    product_dir: Path,
    engine: dict[str, Any] | None = None,
    import_output: dict[str, Any] | None = None,
    recovered_unmodified: bool | None = None,
) -> dict[str, Any]:
    product_dir = Path(product_dir)
    project_path = product_dir / "project.godot"
    text = project_path.read_text(encoding="utf-8") if project_path.is_file() else ""
    identity = parse_project_identity(text) if text else {
        "config_version": None, "features": [], "is_godot4": False, "is_godot3": False, "name": None,
    }
    engine = engine or {"status": "NOT_FOUND", "tool_missing": True}
    engine_status = engine.get("status")
    import_errors = classify_engine_import_errors(engine, import_output)
    if engine_status == "SUCCESS" and import_output is not None:
        import_status = "RAN"
        if any(e.get("severity") == "blocker" for e in import_errors):
            import_result = "ERRORS_CLASSIFIED"
        else:
            import_result = "CLEAN"
    else:
        import_status = "NOT_RUN"
        import_result = engine_status if engine_status != "SUCCESS" else "NOT_RUN"

    static_errors: list[dict[str, Any]] = []
    if not project_path.is_file():
        static_errors.append({
            "category": "SETTINGS",
            "path": "product/project.godot",
            "severity": "blocker",
            "dependency": "project_identity",
            "message": "product/project.godot missing",
        })
    elif identity.get("is_godot3"):
        static_errors.append({
            "category": "SETTINGS",
            "path": "product/project.godot",
            "severity": "blocker",
            "dependency": "config_version_5",
            "message": "seed still declares Godot 3.x",
        })
    elif not identity.get("is_godot4"):
        static_errors.append({
            "category": "SETTINGS",
            "path": "product/project.godot",
            "severity": "blocker",
            "dependency": "config_version_5",
            "message": "seed is not recognized as Godot 4",
        })

    return {
        "schema_version": 1,
        "task": "P1-X0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "product_dir": "product",
        "seed": {
            "project_godot": "product/project.godot",
            "main_scene": "res://scenes/seed.tscn",
            "identity": identity,
        },
        "static_parse": {
            "status": "PASS" if identity.get("is_godot4") and not static_errors else "FAIL",
            "godot4": bool(identity.get("is_godot4")),
            "errors": static_errors,
        },
        "engine": {
            "status": engine_status,
            "version": engine.get("version"),
            "resolved_via": engine.get("resolved_via"),
            "tool_missing": bool(engine.get("tool_missing") or engine_status in {"NOT_FOUND", "TOOL_MISSING"}),
        },
        "import_parse": {
            "status": import_status,
            "result": import_result,
            "errors": import_errors,
            "zero_errors_required": False,
        },
        "recovered_unmodified": recovered_unmodified,
        "notes": [
            "Zero conversion/import errors are not required for P1-X0.",
            "ENGINE_MISSING / NOT_FOUND is an honest classification, not PASS.",
        ],
    }


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--import-parse", action="store_true", help="attempt Godot headless import when binary exists")
    args = ap.parse_args(argv)

    root = (args.root or _repo_root_from_here()).resolve()
    product = (args.product or (root / "product")).resolve()
    out = (args.out or (root / "migration" / "conversion" / "seed_report.json")).resolve()

    write_product_seed(product)

    bootstrap = root / "scripts" / "bootstrap"
    if str(bootstrap) not in sys.path:
        sys.path.insert(0, str(bootstrap))
    from product_toolchain import discover_product_godot, run_headless_import  # type: ignore

    discovery = discover_product_godot(root)
    import_output = None
    if args.import_parse and discovery.get("engine", {}).get("status") == "SUCCESS":
        import_output = run_headless_import(discovery["engine"]["binary"], product)

    report = build_conversion_report(
        product,
        engine=discovery.get("engine"),
        import_output=import_output,
        recovered_unmodified=None,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "static_parse": report["static_parse"]["status"],
                      "engine": report["engine"]["status"], "import_parse": report["import_parse"]["status"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
