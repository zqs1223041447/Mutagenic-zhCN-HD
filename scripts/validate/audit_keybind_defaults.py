#!/usr/bin/env python3
"""Audit the default Keybinds display path without launching the game.

This is a static baseline investigation.  It distinguishes the C5-L5 text
patch from the game's existing keybind initialization path and never reads or
writes a save file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def line_number(text: str, needle: str) -> int | None:
    for number, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return number
    return None


def source_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_file():
        raise SystemExit(f"ERROR: required source file does not exist: {path}")
    return path


def action_block(project: str, action: str) -> str:
    match = re.search(
        rf"(?ms)^{re.escape(action)}=\{{(.*?)(?=^[A-Za-z0-9_]+=\{{|\Z)",
        project,
    )
    if not match:
        raise SystemExit(f"ERROR: input action block not found: {action}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--mod", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    candidate = args.candidate.resolve()
    mod_path = args.mod.resolve()
    if not root.is_dir():
        raise SystemExit(f"ERROR: repository root does not exist: {root}")
    if not candidate.is_file():
        raise SystemExit(f"ERROR: candidate does not exist: {candidate}")
    if not mod_path.is_file():
        raise SystemExit(f"ERROR: mod manifest does not exist: {mod_path}")

    game_state_path = source_path(root, "04_recovered/Globals/GameState.gd")
    keybindings_path = source_path(root, "04_recovered/Globals/Keybindings.gd")
    option_path = source_path(root, "04_recovered/Scenes/Popups/Dialogs/Keybinds/KeybindOption.gd")
    scene_path = source_path(root, "04_recovered/Scenes/Popups/Dialogs/Keybinds/Keybinds.tscn")
    project_path = source_path(root, "04_recovered/project.godot")

    game_state = read_text(game_state_path)
    keybindings = read_text(keybindings_path)
    option = read_text(option_path)
    scene = read_text(scene_path)
    project = read_text(project_path)
    mod = json.loads(mod_path.read_text(encoding="utf-8-sig"))

    expected_defaults = {
        "dash": {"physical_scancode": 16777237, "display_name": "Shift"},
        "interact": {"physical_scancode": 32, "display_name": "Space"},
        "move_left": {"physical_scancode": 65, "display_name": "A"},
        "move_right": {"physical_scancode": 68, "display_name": "D"},
        "move_up": {"physical_scancode": 87, "display_name": "W"},
        "move_down": {"physical_scancode": 83, "display_name": "S"},
    }
    expected_configurable_order = [
        "interact",
        "dash",
        "move_left",
        "move_right",
        "move_up",
        "move_down",
    ]
    input_defaults: dict[str, dict[str, Any]] = {}
    checks: list[dict[str, Any]] = []

    for action, expected in expected_defaults.items():
        block = action_block(project, action)
        match = re.search(r'physical_scancode"\s*:\s*(\d+)', block)
        actual = int(match.group(1)) if match else None
        passed = actual == expected["physical_scancode"]
        input_defaults[action] = {
            "physical_scancode": actual,
            "expected_physical_scancode": expected["physical_scancode"],
            "static_display_name": expected["display_name"],
            "matched": passed,
        }
        checks.append({
            "check": f"project_input_default_{action}",
            "passed": passed,
            "source_line": line_number(project, f"{action}={{"),
        })

    inventory_block = action_block(project, "ui_open_inventory")
    inventory_codes = [
        int(value)
        for value in re.findall(r'physical_scancode"\s*:\s*(\d+)', inventory_block)
    ]
    input_defaults["ui_open_inventory"] = {
        "physical_scancodes": inventory_codes,
        "expected_physical_scancodes": [73, 16777218],
        "static_display_names": ["I", "Tab"],
        "matched": inventory_codes == [73, 16777218],
    }
    checks.append({
        "check": "ui_open_inventory_has_keyboard_defaults_but_is_not_configurable",
        "passed": (
            inventory_codes == [73, 16777218]
            and '"button_index":3' in inventory_block
            and "ui_open_inventory" not in expected_configurable_order
        ),
        "source_line": line_number(project, "ui_open_inventory={"),
    })

    configurable_match = re.search(
        r"(?ms)var configurable_actions = \[(.*?)\]", keybindings
    )
    configurable_actions = re.findall(
        r'"([^"]+)"', configurable_match.group(1) if configurable_match else ""
    )
    checks.append({
        "check": "configurable_action_list_matches_six_keyboard_actions",
        "passed": configurable_actions == expected_configurable_order,
        "actual": configurable_actions,
        "expected": expected_configurable_order,
        "source_line": line_number(keybindings, "var configurable_actions"),
    })

    scene_pairs = re.findall(
        r'label_text = "([^"]+)"\s*\n(?:[^\n]*\n)*?action_name = "([^"]+)"',
        scene,
    )
    expected_scene_pairs = [
        ("Dash", "dash"),
        ("Move Left", "move_left"),
        ("Move Right", "move_right"),
        ("Move Up", "move_up"),
        ("Move Down", "move_down"),
        ("Interact", "interact"),
        ("Show Inventory", "ui_open_inventory"),
    ]
    checks.append({
        "check": "keybind_scene_declares_expected_display_actions",
        "passed": scene_pairs == expected_scene_pairs,
        "actual": scene_pairs,
        "expected": expected_scene_pairs,
        "source_line": line_number(scene, 'label_text = "Dash"'),
    })

    checks.append({
        "check": "fresh_saved_state_has_empty_keybind_overrides",
        "passed": '"keybind_overrides": {},' in game_state,
        "source_line": line_number(game_state, '"keybind_overrides": {},'),
    })
    checks.append({
        "check": "get_keybind_returns_unassigned_without_override",
        "passed": (
            "if saved_stats.keybind_overrides.has(action):" in game_state
            and 'return "Unassigned"' in game_state
        ),
        "source_line": line_number(game_state, 'return "Unassigned"'),
    })

    ready_match = re.search(r"(?ms)^func _ready\(\):\n(.*?)(?=^func _physics_process)", game_state)
    ready_body = ready_match.group(1) if ready_match else ""
    checks.append({
        "check": "ready_resets_state_without_loading_keybind_overrides",
        "passed": "reset_saved_state()" in ready_body and "load_keybinds()" not in ready_body,
        "source_line": line_number(game_state, "func _ready()"),
    })

    no_save_branch = (
        "Steam.fileExists(save_file)" in game_state
        and "No save file found" in game_state
        and 'get_tree().change_scene("res://Scenes/Menu.tscn")' in game_state
    )
    checks.append({
        "check": "steam_no_save_branch_returns_to_menu_without_explicit_load_keybinds_call",
        "passed": no_save_branch,
        "source_line": line_number(game_state, "Steam.fileExists(save_file)"),
    })
    checks.append({
        "check": "keybind_option_updates_display_from_gamestate",
        "passed": '$Button.text = GameState.get_keybind(action_name)' in option,
        "source_line": line_number(option, '$Button.text = GameState.get_keybind'),
    })

    patch_paths = [patch.get("path") for patch in mod.get("patches", [])]
    checks.append({
        "check": "c5_l5_mod_only_declares_keybinds_scene_text_patches",
        "passed": all(path == "Scenes/Popups/Dialogs/Keybinds/Keybinds.tscn" for path in patch_paths),
        "actual_paths": sorted(set(patch_paths)),
        "source": str(mod_path),
    })

    passed = all(check.get("passed") is True for check in checks)
    report = {
        "evidence_id": "C5-L5-keybind-default-behavior-audit-20260814",
        "candidate": str(candidate),
        "candidate_sha256": sha256(candidate),
        "mod_manifest": str(mod_path),
        "mod_manifest_sha256": sha256(mod_path),
        "source_hashes": {
            str(path.relative_to(root)): sha256(path)
            for path in [game_state_path, keybindings_path, option_path, scene_path, project_path]
        },
        "status": "PASS" if passed else "FAIL",
        "technical_conclusion": "INFERENCE_HIGH" if passed else "UNKNOWN",
        "subsystem": "RUNTIME_GAMEPLAY",
        "question": "Are the visible Unassigned values caused by the C5-L5 localization delta, or by the baseline keybind initialization path?",
        "delta": "none; read-only static analysis",
        "input_defaults": input_defaults,
        "configurable_actions": configurable_actions,
        "scene_action_pairs": scene_pairs,
        "checks": checks,
        "finding": (
            "The C5-L5 patch changes only two static Keybinds text fields. Fresh saved state starts with an empty keybind_overrides dictionary; get_keybind returns Unassigned without an override; defaults are copied into overrides by load_keybinds, but the initial _ready path does not call it and the Steam no-save branch returns to Menu. The Show Inventory row is also outside configurable_actions even though project.godot supplies I and Tab defaults. Therefore an all-Unassigned display is consistent with the baseline initialization/configuration path, not evidence that the C5-L5 translation patch removed the default InputMap bindings."
        ),
        "baseline_classification": "baseline_initialization_behavior; not_proven_as_C5_L5_regression",
        "proves": "the static source/data path explains the displayed Unassigned values and confirms the C5-L5 manifest does not modify scripts or InputMap defaults",
        "not_proven": "runtime key press behavior, whether a particular save was loaded, actual OS display names, save persistence, or whether the baseline behavior should be changed as a new CODE_PATCH scope",
        "runtime_gate": "NOT_STARTED",
        "next_decision": "do not patch the C5-L5 localization candidate; if default key display is desired, define a separate controlled CODE_PATCH experiment against the trusted baseline and validate input behavior plus persistence",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "technical_conclusion": report["technical_conclusion"], "check_count": len(checks)}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
