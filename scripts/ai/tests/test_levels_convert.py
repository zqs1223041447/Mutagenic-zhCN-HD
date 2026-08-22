#!/usr/bin/env python3
"""P1-WAVE-I tests: drive shipped levels_convert / scene+gdscript converters."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "migration"))

from migration.boot_convert import convert_gdscript  # noqa: E402
from migration.menu_convert import convert_scene_text  # noqa: E402
from migration.levels_convert import copy_and_convert_levels  # noqa: E402

LEVEL_SCENE = """[gd_scene load_steps=3 format=2]

[ext_resource path="res://Scenes/Levels/Level01.gd" type="Script" id=1]
[ext_resource path="res://sprites/levels/level_tileset.png" type="Texture" id=2]

[node name="Level01" type="Node2D"]
script = ExtResource( 1 )

[node name="Sprite" type="Sprite" parent="."]
texture = ExtResource( 2 )
"""

LEVEL_GD = (
    "extends Node2D\n"
    "class_name Level01\n"
    "onready var spawn = get_node(\"Spawn\")\n"
    "func _ready():\n"
    "\tspawn.connect(\"entered\", self, \"on_spawn_entered\")\n"
)

LEVEL_TRES = """[gd_resource type="Resource" load_steps=2 format=2]

[ext_resource path="res://sprites/levels/level_tileset.png" type="Texture" id=1]

[resource]
tileset = ExtResource( 1 )
"""

LEGACY_LEVEL_GD_RECOVERED = (
    "extends Node2D\n"
    "onready var door = get_node(\"Door\")\n"
    "func _ready():\n"
    "\tdoor.connect(\"opened\", self, \"on_door_opened\")\n"
)

LEGACY_LEVEL_GD_WAVE_F = (
    "extends Node\n"
    "@onready var door = get_node(\"Door\")\n"
    "func _ready():\n"
    "\tdoor.connect(\"opened\", Callable(self, \"on_door_opened\"))\n"
)

PLAYER_CONTENT = (
    "extends RigidBody2D\n"
    "func _physics_process(delta):\n"
    "\tif Input.is_action_just_pressed(\"dash\"):\n"
    "\t\tapply_central_impulse(Vector2(100, 0))\n"
)


def _fingerprint(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*") if p.is_file()
    }


def _seed_recovered(recovered: Path) -> None:
    scene_dir = recovered / "Scenes" / "Levels"
    scene_dir.mkdir(parents=True)
    (scene_dir / "Level01.tscn").write_text(LEVEL_SCENE, encoding="utf-8")
    (scene_dir / "Level01.gd").write_text(LEVEL_GD, encoding="utf-8")
    (scene_dir / "Level01.tres").write_text(LEVEL_TRES, encoding="utf-8")
    sprite_dir = recovered / "sprites" / "levels"
    sprite_dir.mkdir(parents=True)
    (sprite_dir / "level_tileset.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00lvl")
    (sprite_dir / "level_tileset.png.import").write_text(
        "[remap]\nimporter=\"texture\"\n", encoding="utf-8")
    (sprite_dir / "level_tileset.gd.uid").write_text(
        "uid://bleveltileset\n", encoding="utf-8")


class LevelsConvertTest(unittest.TestCase):
    def test_level_scene_conversion(self):
        out = convert_scene_text(LEVEL_SCENE)
        self.assertIn("format=3", out)
        self.assertIn('type="Sprite2D"', out)
        self.assertIn('type="Texture2D"', out)
        self.assertIn('ExtResource("1")', out)

        tres_out = convert_scene_text(LEVEL_TRES)
        self.assertIn("format=3", tres_out)
        self.assertIn('ExtResource("1")', tres_out)

    def test_level_gdscript_conversion(self):
        out = convert_gdscript(LEVEL_GD)
        self.assertIn("@onready var spawn", out)
        self.assertIn("Callable(self, \"on_spawn_entered\")", out)

    def test_multiple_roots_copy_convert_skip_sidecars(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            _seed_recovered(recovered)
            before_hashes = _fingerprint(recovered)

            result = copy_and_convert_levels(
                recovered, product, roots=("Scenes/Levels", "sprites/levels"))

            after_hashes = _fingerprint(recovered)
            self.assertEqual(before_hashes, after_hashes)
            self.assertTrue(result["recovered_unmodified"])

            # Both roots converted into product layout
            tscn = (product / "scenes" / "Levels" / "Level01.tscn").read_text(encoding="utf-8")
            gd = (product / "scenes" / "Levels" / "Level01.gd").read_text(encoding="utf-8")
            tres = (product / "scenes" / "Levels" / "Level01.tres").read_text(encoding="utf-8")
            self.assertIn("format=3", tscn)
            self.assertIn('type="Sprite2D"', tscn)
            self.assertIn("res://scenes/Levels/Level01.gd", tscn)
            self.assertIn("@onready var spawn", gd)
            self.assertIn("Callable(self, \"on_spawn_entered\")", gd)
            self.assertIn("format=3", tres)

            # Binary copied verbatim; .import/.uid sidecars never copied
            self.assertEqual(
                (product / "sprites" / "levels" / "level_tileset.png").read_bytes(),
                b"\x89PNG\r\n\x1a\n\x00\x00\x00lvl")
            self.assertFalse((product / "sprites" / "levels" / "level_tileset.png.import").exists())
            self.assertFalse((product / "sprites" / "levels" / "level_tileset.gd.uid").exists())

            # Bookkeeping matches disk state
            self.assertEqual(result["files_copied"], len(result["copied"]))
            self.assertEqual(result["files_copied"], 4)
            self.assertEqual(len(result["converted_text_files"]), 3)
            self.assertEqual(result["binaries"], ["sprites/levels/level_tileset.png"])
            self.assertEqual(result["skipped_existing"], [])
            self.assertEqual(result["excluded"], [])

    def test_exclude_and_existing_files_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            _seed_recovered(recovered)
            (recovered / "Scenes" / "Levels" / "LegacyArena.gd").write_text(
                LEGACY_LEVEL_GD_RECOVERED, encoding="utf-8")

            result = copy_and_convert_levels(
                recovered,
                product,
                roots=("Scenes/Levels", "sprites/levels"),
                exclude=("Scenes/Levels/LegacyArena.gd",),
            )

            # Excluded recovered sibling never reaches product
            self.assertNotIn("scenes/Levels/LegacyArena.gd", result["copied"])
            self.assertFalse((product / "scenes" / "Levels" / "LegacyArena.gd").exists())

            # Non-excluded siblings still converted
            tscn = (product / "scenes" / "Levels" / "Level01.tscn").read_text(encoding="utf-8")
            self.assertIn("format=3", tscn)
            self.assertEqual(result["excluded"], ["Scenes/Levels/LegacyArena.gd"])

    def test_preexisting_destination_not_overwritten_and_out_of_scope_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            _seed_recovered(recovered)

            # Pre-seed product with a migrated Level01.gd and a foreign Player file
            existing_file = product / "scenes" / "Levels" / "Level01.gd"
            existing_file.parent.mkdir(parents=True)
            existing_file.write_text(LEGACY_LEVEL_GD_WAVE_F, encoding="utf-8")
            player_dir = product / "scenes" / "Player"
            player_dir.mkdir()
            player_file = player_dir / "Player.gd"
            player_file.write_text(PLAYER_CONTENT, encoding="utf-8")

            result = copy_and_convert_levels(
                recovered, product, roots=("Scenes/Levels",))

            # Existing destination untouched and reported via skipped_existing
            self.assertEqual(existing_file.read_text(encoding="utf-8"), LEGACY_LEVEL_GD_WAVE_F)
            self.assertIn("scenes/Levels/Level01.gd", result["skipped_existing"])
            self.assertNotIn("scenes/Levels/Level01.gd", result["copied"])

            # Out-of-scope files were not deleted or corrupted
            self.assertTrue(player_file.is_file())
            self.assertEqual(player_file.read_text(encoding="utf-8"), PLAYER_CONTENT)

            # Missing roots are silently ignored (only the given root is walked)
            self.assertFalse((product / "sprites").exists())


if __name__ == "__main__":
    unittest.main()
