#!/usr/bin/env python3
"""Unit tests for P3-H2 (position save persistence) and P3-H3 (error convergence).

Offline only - no engine binary is launched:

  H2  * GameState.gd source contract (schema default, capture hook,
        omit-without-world semantics)
      * pure-python mirror of migrate()/merge_in_saved_data() proving old
        saves without a position field load cleanly while new saves keep it
      * evidence lock-in for migration/conversion/p3_h2_position_save.json
  H3a * every Projectile-family script that overrides _ready chains
        super._ready(); Projectile.gd itself does not (parent is Area2D)
      * no Pool*Array G3 residue in any Projectiles scene
  H3b * FloatingDamage uses create_tween()/tween_property, no
        interpolate_property; scene carries no legacy Tween node
      * combat probe evidence shows zero script errors (residual gone)
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GAMESTATE = REPO / "product" / "Globals" / "GameState.gd"
PROJECTILES = REPO / "product" / "scenes" / "Projectiles"
FLOATING_GD = REPO / "product" / "scenes" / "Particles" / "FloatingDamage.gd"
FLOATING_TSCN = REPO / "product" / "scenes" / "Particles" / "FloatingDamage.tscn"
H2_EVIDENCE = REPO / "migration" / "conversion" / "p3_h2_position_save.json"
COMBAT_EVIDENCE = REPO / "migration" / "conversion" / "p3_c_combat.json"

# The 15 Projectile subclasses that override _ready (flat hierarchy; all
# extend Projectile directly).
EXPECTED_SUPER_READY = [
    "MeleeSkills/ShockwaveProjectile.gd",
    "Skills/BaneProjectile.gd",
    "Skills/BladeShieldProjectile.gd",
    "Skills/BloodSlashProjectile.gd",
    "Skills/BrittleProjectile.gd",
    "Skills/DebilitateProjectile.gd",
    "Skills/EnergizedAxeProjectile.gd",
    "Skills/HinderProjectile.gd",
    "Skills/HypothermiaProjectile.gd",
    "Skills/PlagueCloudsProjectile.gd",
    "Skills/PolarizeProjectile.gd",
    "Skills/ProtractProjectile.gd",
    "Skills/ScorchProjectile.gd",
    "Skills/SharknadoShardProjectile.gd",
    "Skills/SharknadoShotProjectile.gd",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _initial_configuration_block() -> str:
    src = _read(GAMESTATE)
    start = src.index("var initial_configuration")
    end = src.index("var saved_stats")
    return src[start:end]


# --- pure-python mirror of the GDScript merge semantics ----------------------
def merge_in_saved_data(current: dict, new: dict, ignore=None,
                        override: bool = False) -> None:
    """Mirrors GameState.merge_in_saved_data(): fills missing keys from `new`,
    recurses into dict-dict overlaps, overrides existing scalars only when
    override=True."""
    for key, value in new.items():
        if ignore is not None and key == ignore:
            continue
        if key in current:
            if isinstance(value, dict) and isinstance(current[key], dict):
                merge_in_saved_data(current[key], value, ignore, override)
            elif override:
                current[key] = value
        else:
            current[key] = value


def migrate_characters(saved_characters: dict,
                       initial_configuration: dict) -> dict:
    """Mirrors the per-character part of GameState.migrate(): wholesale
    character replacement, initial_configuration backfill, then erase of
    class-less characters (the rule that motivated create_new_character in
    the H2 driver)."""
    characters = saved_characters
    for name in list(characters.keys()):
        char = characters[name]
        merge_in_saved_data(char, initial_configuration)
        tree = char.get("mutation_tree_loadout", {})
        if isinstance(tree, dict) and "class" in tree and tree["class"] is None:
            del characters[name]
    return characters


class H2GameStateSourceContract(unittest.TestCase):
    def test_initial_configuration_defines_null_position_default(self):
        block = _initial_configuration_block()
        self.assertRegex(block, r'"position"\s*:\s*null')

    def test_do_save_game_captures_position_before_serialization(self):
        src = _read(GAMESTATE)
        do_start = src.index("func do_save_game()")
        capture_start = src.index("func capture_player_position()")
        # capture must exist and be invoked from do_save_game's body
        self.assertIn("capture_player_position()", src[do_start:])
        # declared before use keeps the call site inside do_save_game's body
        self.assertLess(capture_start, do_start)

    def test_capture_omits_field_without_world_context(self):
        body = _read(GAMESTATE)
        start = body.index("func capture_player_position()")
        end = body.index("func do_save_game()")
        capture = body[start:end]
        self.assertIn("stats.erase(\"position\")", capture)
        self.assertIn("get_global(\"player\")", capture)
        self.assertIn("is_inside_tree", capture)

    def test_capture_writes_x_y_level(self):
        body = _read(GAMESTATE)
        start = body.index("func capture_player_position()")
        end = body.index("func do_save_game()")
        capture = body[start:end]
        self.assertIn('"x"', capture)
        self.assertIn('"y"', capture)
        self.assertIn('"level"', capture)


class H2SchemaBackwardCompatTest(unittest.TestCase):
    """Pure-python mirror of the GDScript merge rules."""

    INITIAL = {
        "character_name": "default",
        "account_level": 1,
        "mutation_tree_loadout": {"class": None, "passives": []},
        "filters": {},
        "position": None,
    }

    def test_old_save_without_position_loads_cleanly(self):
        saved_chars = {
            "legacy": {
                "character_name": "legacy",
                "account_level": 7,
                "mutation_tree_loadout": {"class": "MAGE", "passives": ["root_mage"]},
                # no "position" key at all - pre-H2 save shape
            }
        }
        chars = migrate_characters(saved_chars, self.INITIAL)
        self.assertIn("legacy", chars)
        self.assertIsNone(chars["legacy"]["position"])
        self.assertEqual(chars["legacy"]["account_level"], 7)

    def test_new_save_keeps_written_position(self):
        pos = {"x": 123.5, "y": -77.25, "level": "p3_h2_probe"}
        saved_chars = {
            "P3ProbeChar": {
                "character_name": "P3ProbeChar",
                "mutation_tree_loadout": {"class": "MAGE", "passives": ["root_mage"]},
                "position": pos,
            }
        }
        chars = migrate_characters(saved_chars, self.INITIAL)
        self.assertEqual(chars["P3ProbeChar"]["position"], pos)

    def test_classless_character_is_erased_by_migrate(self):
        chars = migrate_characters(
            {"ghost": {"character_name": "ghost",
                       "mutation_tree_loadout": {"class": None, "passives": []}}},
            self.INITIAL)
        self.assertNotIn("ghost", chars)

    def test_merge_does_not_override_existing_scalars(self):
        current = {"account_level": 9}
        merge_in_saved_data(current, {"account_level": 1}, override=False)
        self.assertEqual(current["account_level"], 9)


class H2EvidenceLockInTest(unittest.TestCase):
    def test_evidence_exists_and_passes(self):
        self.assertTrue(H2_EVIDENCE.is_file(), f"missing {H2_EVIDENCE}")
        data = json.loads(_read(H2_EVIDENCE))
        self.assertEqual(data["verdict"], "PASS")
        result = data["result"]
        for key in ("memory_position_written", "file_has_position_field",
                    "file_position_roundtrip_shape", "reloaded_character_present",
                    "reloaded_position_within_tolerance",
                    "no_world_context_omits_field"):
            self.assertTrue(result.get(key), key)
        pos = result["reloaded_position_values"]
        self.assertEqual(pos["level"], "p3_h2_probe")


class H3aSuperReadyContract(unittest.TestCase):
    def _gd_files(self):
        return sorted(PROJECTILES.rglob("*.gd"))

    def test_expected_files_call_super_ready(self):
        for rel in EXPECTED_SUPER_READY:
            src = _read(PROJECTILES / rel)
            self.assertIn("super._ready()", src, rel)

    def test_every_projectile_subclass_overriding_ready_chains_super(self):
        checked = 0
        for path in self._gd_files():
            src = _read(path)
            extends = re.search(r"^extends\s+(\w+)", src, re.M)
            if extends is None or extends.group(1) != "Projectile":
                continue
            if not re.search(r"^func _ready\(", src, re.M):
                continue
            rel = path.relative_to(PROJECTILES).as_posix()
            self.assertIn("super._ready()", src, f"{rel} overrides _ready "
                          "without chaining super._ready()")
            checked += 1
        self.assertGreaterEqual(checked, len(EXPECTED_SUPER_READY))

    def test_base_projectile_does_not_call_super(self):
        src = _read(PROJECTILES / "Projectile.gd")
        self.assertNotIn("super._ready()", src)

    def test_no_pool_array_residue_in_projectile_scenes(self):
        offenders = []
        for tscn in PROJECTILES.rglob("*.tscn"):
            text = _read(tscn)
            if re.search(r"\bPool(Color|Real|Vector2|Vector3|Int|String)Array\b", text):
                offenders.append(tscn.relative_to(PROJECTILES).as_posix())
        self.assertEqual(offenders, [])

    def test_super_is_first_statement_of_ready(self):
        for rel in EXPECTED_SUPER_READY:
            lines = _read(PROJECTILES / rel).splitlines()
            idx = next(i for i, ln in enumerate(lines)
                       if ln.startswith("func _ready("))
            for line in lines[idx + 1:]:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                self.assertTrue(stripped.startswith("super._ready()"),
                                f"{rel}: first statement of _ready must be "
                                f"super._ready(), found: {stripped}")
                break


class H3bFloatingDamageTweenTest(unittest.TestCase):
    def test_gdscript_uses_godot4_tween_api(self):
        src = _read(FLOATING_GD)
        self.assertIn("create_tween()", src)
        self.assertIn("tween_property(", src)
        self.assertNotIn("interpolate_property", src)
        self.assertNotIn("$Label/Tween", src)
        self.assertNotIn("tween_all_completed", src)

    def test_scene_has_no_legacy_tween_node_or_g3_label_props(self):
        src = _read(FLOATING_TSCN)
        self.assertNotRegex(src, r'name="Tween"')
        self.assertNotRegex(src, r'^align\s*=', re.M)
        self.assertNotRegex(src, r'^valign\s*=', re.M)
        self.assertIn("horizontal_alignment", src)
        self.assertIn("vertical_alignment", src)

    def test_combat_probe_evidence_shows_zero_script_errors(self):
        self.assertTrue(COMBAT_EVIDENCE.is_file(), f"missing {COMBAT_EVIDENCE}")
        data = json.loads(_read(COMBAT_EVIDENCE))
        self.assertEqual(data["verdict"], "PASS")
        self.assertEqual(data["script_errors"], [])


if __name__ == "__main__":
    unittest.main()
