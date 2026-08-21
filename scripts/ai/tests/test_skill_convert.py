#!/usr/bin/env python3
"""P1-WAVE-G tests: drive shipped skill_convert / scene+gdscript converters."""
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
from migration.skill_convert import copy_and_convert_skills  # noqa: E402

SKILL_SCENE = """[gd_scene load_steps=3 format=2]

[ext_resource path="res://Scenes/Skills/Fireball.gd" type="Script" id=1]
[ext_resource path="res://sprites/skills/fireball.png" type="Texture" id=2]

[node name="Fireball" type="Node2D"]
script = ExtResource( 1 )

[node name="Sprite" type="Sprite" parent="."]
texture = ExtResource( 2 )
"""

SKILL_GD = (
    "extends Node2D\n"
    "class_name Fireball\n"
    "onready var cooldown = get_node(\"Cooldown\")\n"
    "func _ready():\n"
    "\tcooldown.connect(\"expired\", self, \"on_cooldown_expired\")\n"
)

SKILL_TRES = """[gd_resource type="Resource" load_steps=2 format=2]

[ext_resource path="res://sprites/skills/fireball.png" type="Texture" id=1]

[resource]
icon = ExtResource( 1 )
"""

GENERIC_SKILL_GD_WAVE_E = (
    "extends Node\n"
    "@onready var body = get_node(\"Body\")\n"
    "func _ready():\n"
    "\tbody.connect(\"died\", Callable(self, \"on_died\"))\n"
)

GENERIC_SKILL_GD_RECOVERED = (
    "extends Node\n"
    "onready var body = get_node(\"Body\")\n"
    "func _ready():\n"
    "\tbody.connect(\"died\", self, \"on_died\")\n"
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


class SkillConvertTest(unittest.TestCase):
    def test_skill_scene_conversion(self):
        out = convert_scene_text(SKILL_SCENE)
        self.assertIn("format=3", out)
        self.assertIn('type="Sprite2D"', out)
        self.assertIn('type="Texture2D"', out)
        self.assertIn('ExtResource("1")', out)

        tres_out = convert_scene_text(SKILL_TRES)
        self.assertIn("format=3", tres_out)
        self.assertIn('ExtResource("1")', tres_out)

    def test_skill_gdscript_conversion(self):
        out = convert_gdscript(SKILL_GD)
        self.assertIn("@onready var cooldown", out)
        self.assertIn("Callable(self, \"on_cooldown_expired\")", out)

    def test_generic_skill_excluded_and_preexisting_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            (recovered / "Scenes" / "Skills").mkdir(parents=True)
            (recovered / "Scenes" / "Skills" / "GenericSkill.gd").write_text(
                GENERIC_SKILL_GD_RECOVERED, encoding="utf-8")
            (recovered / "Scenes" / "Skills" / "Fireball.tscn").write_text(SKILL_SCENE, encoding="utf-8")

            wave_e_file = product / "scenes" / "Skills" / "GenericSkill.gd"
            wave_e_file.parent.mkdir(parents=True)
            wave_e_file.write_text(GENERIC_SKILL_GD_WAVE_E, encoding="utf-8")

            result = copy_and_convert_skills(recovered, product)

            # Wave E content untouched
            self.assertTrue(wave_e_file.is_file())
            self.assertEqual(wave_e_file.read_text(encoding="utf-8"), GENERIC_SKILL_GD_WAVE_E)
            self.assertIn("Scenes/Skills/GenericSkill.gd", result["excluded"])
            self.assertIn("scenes/Skills/GenericSkill.gd", result["skipped_existing"])
            self.assertNotIn("scenes/Skills/GenericSkill.gd", result["copied"])

            # Non-excluded sibling still converted
            fireball = (product / "scenes" / "Skills" / "Fireball.tscn").read_text(encoding="utf-8")
            self.assertIn("format=3", fireball)

    def test_copy_skills_does_not_touch_recovered_and_out_of_scope_files(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            # Set up recovered tree fixture
            (recovered / "Scenes" / "Skills").mkdir(parents=True)
            (recovered / "Scenes" / "Skills" / "GenericSkill.gd").write_text(
                GENERIC_SKILL_GD_RECOVERED, encoding="utf-8")
            (recovered / "Scenes" / "Skills" / "Fireball.tscn").write_text(SKILL_SCENE, encoding="utf-8")
            (recovered / "Scenes" / "Skills" / "Fireball.gd").write_text(SKILL_GD, encoding="utf-8")
            (recovered / "Scenes" / "Skills" / "SkillBook.tres").write_text(SKILL_TRES, encoding="utf-8")
            png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00skill"
            (recovered / "sprites" / "skills").mkdir(parents=True)
            (recovered / "sprites" / "skills" / "fireball.png").write_bytes(png_bytes)
            (recovered / "sprites" / "skills" / "fireball.png.import").write_text(
                "[remap]\nimporter=\"texture\"\n", encoding="utf-8")

            before_hashes = _fingerprint(recovered)

            # Pre-seed product with Player.gd and a foreign Skills file outside the copy range
            player_dir = product / "scenes" / "Player"
            player_dir.mkdir(parents=True)
            player_file = player_dir / "Player.gd"
            player_file.write_text(PLAYER_CONTENT, encoding="utf-8")
            wave_e_file = product / "scenes" / "Skills" / "GenericSkill.gd"
            wave_e_file.parent.mkdir(parents=True)
            wave_e_file.write_text(GENERIC_SKILL_GD_WAVE_E, encoding="utf-8")

            result = copy_and_convert_skills(recovered, product)

            after_hashes = _fingerprint(recovered)
            self.assertEqual(before_hashes, after_hashes)
            self.assertTrue(result["recovered_unmodified"])

            # Converted text assets land under product/scenes/Skills
            fireball_tscn = (product / "scenes" / "Skills" / "Fireball.tscn").read_text(encoding="utf-8")
            fireball_gd = (product / "scenes" / "Skills" / "Fireball.gd").read_text(encoding="utf-8")
            skillbook_tres = (product / "scenes" / "Skills" / "SkillBook.tres").read_text(encoding="utf-8")
            self.assertIn("format=3", fireball_tscn)
            self.assertIn('type="Sprite2D"', fireball_tscn)
            self.assertIn("format=3", skillbook_tres)
            self.assertIn("@onready var cooldown", fireball_gd)
            self.assertIn("Callable(self, \"on_cooldown_expired\")", fireball_gd)
            self.assertIn("res://scenes/Skills/Fireball.gd", fireball_tscn)

            # Binary copied verbatim
            self.assertEqual(
                (product / "sprites" / "skills" / "fireball.png").read_bytes(), png_bytes)

            # .import metadata is never copied (repo convention: Godot regenerates it)
            self.assertFalse((product / "sprites" / "skills" / "fireball.png.import").exists())

            # Excluded Wave E file never overwritten
            self.assertEqual(wave_e_file.read_text(encoding="utf-8"), GENERIC_SKILL_GD_WAVE_E)
            self.assertEqual(result["excluded"], ["Scenes/Skills/GenericSkill.gd"])
            self.assertEqual(result["skipped_existing"], ["scenes/Skills/GenericSkill.gd"])

            # Result bookkeeping matches disk state
            self.assertEqual(result["files_copied"], len(result["copied"]))
            self.assertEqual(result["files_copied"], 4)
            self.assertEqual(len(result["converted_text_files"]), 3)
            self.assertEqual(result["binaries"], ["sprites/skills/fireball.png"])

            # Out-of-scope files were not deleted or corrupted
            self.assertTrue(player_file.is_file())
            self.assertEqual(player_file.read_text(encoding="utf-8"), PLAYER_CONTENT)


if __name__ == "__main__":
    unittest.main()
