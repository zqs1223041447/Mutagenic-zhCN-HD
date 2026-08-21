#!/usr/bin/env python3
"""P1-WAVE-F tests: drive shipped mob_convert / scene+gdscript converters."""
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
from migration.mob_convert import copy_and_convert_mobs  # noqa: E402

MOB_SCENE = """[gd_scene load_steps=3 format=2]

[ext_resource path="res://Scenes/Mobs/Grunt.gd" type="Script" id=1]
[ext_resource path="res://sprites/mobs/grunt.png" type="Texture" id=2]

[node name="Grunt" type="KinematicBody2D"]
script = ExtResource( 1 )

[node name="Sprite" type="Sprite" parent="."]
texture = ExtResource( 2 )

[node name="Health" type="Node" parent="."]
"""

MOB_GD = (
    "extends Node\n"
    "class_name Grunt\n"
    "onready var health = get_node(\"Health\")\n"
    "func _ready():\n"
    "\thealth.connect(\"health_changed\", self, \"on_health_changed\")\n"
)

BOSS_SCENE = "[gd_scene load_steps=2 format=2]\n\n[ext_resource path=\"res://Scenes/Mobs/Bosses/X.gd\" type=\"Script\" id=1]\n"

PLAYER_CONTENT = (
    "extends RigidBody2D\n"
    "func _physics_process(delta):\n"
    "\tif Input.is_action_just_pressed(\"dash\"):\n"
    "\t\tapply_central_impulse(Vector2(100, 0))\n"
)


class MobConvertTest(unittest.TestCase):
    def test_mob_scene_conversion(self):
        out = convert_scene_text(MOB_SCENE)
        self.assertIn("format=3", out)
        self.assertIn('type="CharacterBody2D"', out)
        self.assertIn('type="Sprite2D"', out)
        self.assertIn('type="Texture2D"', out)
        self.assertIn('ExtResource("1")', out)

    def test_mob_gdscript_conversion(self):
        out = convert_gdscript(MOB_GD)
        self.assertIn("@onready var health", out)
        self.assertIn("Callable(self, \"on_health_changed\")", out)

    def test_exclude_keeps_boss_out_of_product(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            (recovered / "Scenes" / "Mobs" / "Bosses").mkdir(parents=True)
            (recovered / "Scenes" / "Mobs" / "Grunt.gd").write_text(MOB_GD, encoding="utf-8")
            (recovered / "Scenes" / "Mobs" / "Bosses" / "X.tscn").write_text(BOSS_SCENE, encoding="utf-8")

            result = copy_and_convert_mobs(recovered, product, exclude=["Scenes/Mobs/Bosses/X.tscn"])

            self.assertTrue((product / "scenes" / "Mobs" / "Grunt.gd").is_file())
            self.assertFalse((product / "scenes" / "Mobs" / "Bosses" / "X.tscn").is_file())
            self.assertFalse((product / "scenes" / "Mobs" / "Bosses").exists())
            self.assertEqual(result["excluded"], ["Scenes/Mobs/Bosses/X.tscn"])
            self.assertTrue(result["recovered_unmodified"])

    def test_copy_mobs_does_not_touch_recovered_and_out_of_scope_files(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            # Set up recovered tree fixture
            (recovered / "Scenes" / "Mobs" / "Bosses").mkdir(parents=True)
            (recovered / "Scenes" / "Mobs" / "sprites").mkdir(parents=True)

            (recovered / "Scenes" / "Mobs" / "Grunt.tscn").write_text(MOB_SCENE, encoding="utf-8")
            (recovered / "Scenes" / "Mobs" / "Grunt.gd").write_text(MOB_GD, encoding="utf-8")
            (recovered / "Scenes" / "Mobs" / "Bosses" / "X.tscn").write_text(BOSS_SCENE, encoding="utf-8")
            png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00mob"
            (recovered / "Scenes" / "Mobs" / "sprites" / "grunt.png").write_bytes(png_bytes)

            before_hashes = {
                p.relative_to(recovered).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in recovered.rglob("*") if p.is_file()
            }

            # Pre-seed product with Player.gd and a foreign Mobs file outside the copy range
            player_dir = product / "scenes" / "Player"
            player_dir.mkdir(parents=True)
            player_file = player_dir / "Player.gd"
            player_file.write_text(PLAYER_CONTENT, encoding="utf-8")
            keepme = product / "scenes" / "Mobs" / "Custom" / "KeepMe.gd"
            keepme.parent.mkdir(parents=True)
            keepme_content = "# kept\n"
            keepme.write_text(keepme_content, encoding="utf-8")

            result = copy_and_convert_mobs(recovered, product, exclude=["Scenes/Mobs/Bosses/X.tscn"])

            after_hashes = {
                p.relative_to(recovered).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in recovered.rglob("*") if p.is_file()
            }
            self.assertEqual(before_hashes, after_hashes)
            self.assertTrue(result["recovered_unmodified"])

            # Converted text assets land under product/scenes/
            grunt_tscn = (product / "scenes" / "Mobs" / "Grunt.tscn").read_text(encoding="utf-8")
            grunt_gd = (product / "scenes" / "Mobs" / "Grunt.gd").read_text(encoding="utf-8")
            self.assertIn("format=3", grunt_tscn)
            self.assertIn('type="CharacterBody2D"', grunt_tscn)
            self.assertIn("@onready var health", grunt_gd)
            self.assertIn("Callable(self, \"on_health_changed\")", grunt_gd)
            self.assertIn("res://scenes/Mobs/Grunt.gd", grunt_tscn)

            # Binary copied verbatim
            self.assertEqual((product / "scenes" / "Mobs" / "sprites" / "grunt.png").read_bytes(), png_bytes)

            # Excluded boss never reaches product
            self.assertFalse((product / "scenes" / "Mobs" / "Bosses" / "X.tscn").is_file())
            self.assertEqual(result["excluded"], ["Scenes/Mobs/Bosses/X.tscn"])

            # Result bookkeeping matches disk state
            self.assertEqual(result["files_copied"], len(result["copied"]))
            self.assertEqual(result["files_copied"], 3)
            self.assertEqual(len(result["converted_text_files"]), 2)
            self.assertEqual(result["binaries"], ["scenes/Mobs/sprites/grunt.png"])

            # Out-of-scope files were not deleted or corrupted
            self.assertTrue(player_file.is_file())
            self.assertEqual(player_file.read_text(encoding="utf-8"), PLAYER_CONTENT)
            self.assertTrue(keepme.is_file())
            self.assertEqual(keepme.read_text(encoding="utf-8"), keepme_content)


if __name__ == "__main__":
    unittest.main()
