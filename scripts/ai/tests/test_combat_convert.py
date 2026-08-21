#!/usr/bin/env python3
"""P1-WAVE-E tests: drive shipped combat_convert / scene+gdscript converters."""
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
from migration.combat_convert import copy_and_convert_combat  # noqa: E402
from migration.menu_convert import convert_scene_text  # noqa: E402

PROJECTILE_SCENE = """[gd_scene load_steps=3 format=2]

[ext_resource path="res://Scenes/Projectiles/Projectile.gd" type="Script" id=1]
[ext_resource path="res://sprites/effects/glow.png" type="Texture" id=2]

[node name="Projectile" type="Area2D"]
script = ExtResource( 1 )

[node name="Sprite" type="AnimatedSprite" parent="."]

[node name="Glow" type="Sprite" parent="."]
texture = ExtResource( 2 )
"""


class CombatConvertTest(unittest.TestCase):
    def test_projectile_scene_conversion(self):
        out = convert_scene_text(PROJECTILE_SCENE)
        self.assertIn("format=3", out)
        self.assertIn('type="AnimatedSprite2D"', out)
        self.assertIn('type="Sprite2D"', out)
        self.assertIn('type="Texture2D"', out)

    def test_generic_skill_gdscript_conversion(self):
        src = (
            "extends Node2D\n"
            "class_name GenericSkill\n"
            "onready var stats = get_parent().get_node(\"Stats\")\n"
            "export (Texture) var texture\n"
            "func _ready():\n"
            "\tstats.connect(\"stats_changed\", self, \"recompute_supported_stats\")\n"
        )
        out = convert_gdscript(src)
        self.assertIn("@onready var stats", out)
        self.assertIn("Callable(self, \"recompute_supported_stats\")", out)

    def test_copy_combat_does_not_touch_recovered_and_preserves_player(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            # Set up recovered tree fixture
            (recovered / "Scenes" / "Skills").mkdir(parents=True)
            (recovered / "Scenes" / "Projectiles").mkdir(parents=True)
            (recovered / "Scenes" / "StatusEffects" / "Generic").mkdir(parents=True)
            (recovered / "Scenes" / "Mobs").mkdir(parents=True)

            generic_skill_src = (
                "extends Node2D\nclass_name GenericSkill\n"
                "onready var stats = get_node(\"Stats\")\n"
                "func _ready():\n\tstats.connect(\"stats_changed\", self, \"on_change\")\n"
            )
            (recovered / "Scenes" / "Skills" / "GenericSkill.gd").write_text(generic_skill_src, encoding="utf-8")
            (recovered / "Scenes" / "Projectiles" / "Projectile.tscn").write_text(PROJECTILE_SCENE, encoding="utf-8")
            (recovered / "Scenes" / "Projectiles" / "Projectile.gd").write_text(
                "extends Area2D\nclass_name Projectile\nexport var does_hit = true\n", encoding="utf-8"
            )
            (recovered / "Scenes" / "StatusEffects" / "BaseEffect.gd").write_text(
                "extends Node\nclass_name BaseEffect\nexport var permanent = false\n", encoding="utf-8"
            )
            (recovered / "Scenes" / "StatusEffects" / "Generic" / "Vulnerable.tscn").write_text(
                "[gd_scene format=2]\n", encoding="utf-8"
            )
            # Forbidden mob scene fixture
            (recovered / "Scenes" / "Mobs" / "Mob.tscn").write_text("[gd_scene format=2]\n", encoding="utf-8")

            # Pre-seed product with player containing dash
            player_dir = product / "scenes" / "Player"
            player_dir.mkdir(parents=True)
            player_file = player_dir / "Player.gd"
            player_content = (
                "extends RigidBody2D\n"
                "func _physics_process(delta):\n"
                "\tif Input.is_action_just_pressed(\"dash\"):\n"
                "\t\tapply_central_impulse(Vector2(100, 0))\n"
            )
            player_file.write_text(player_content, encoding="utf-8")

            before_hashes = {
                p.relative_to(recovered).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in recovered.rglob("*") if p.is_file()
            }

            result = copy_and_convert_combat(recovered, product)

            after_hashes = {
                p.relative_to(recovered).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in recovered.rglob("*") if p.is_file()
            }
            self.assertEqual(before_hashes, after_hashes)
            self.assertTrue(result["recovered_unmodified"])

            # Verify combat assets converted into product/scenes/
            self.assertTrue((product / "scenes" / "Skills" / "GenericSkill.gd").is_file())
            self.assertTrue((product / "scenes" / "Projectiles" / "Projectile.tscn").is_file())
            self.assertTrue((product / "scenes" / "Projectiles" / "Projectile.gd").is_file())
            self.assertTrue((product / "scenes" / "StatusEffects" / "BaseEffect.gd").is_file())
            self.assertTrue((product / "scenes" / "StatusEffects" / "Generic" / "Vulnerable.tscn").is_file())

            # Check format / syntax transformations
            proj_text = (product / "scenes" / "Projectiles" / "Projectile.tscn").read_text(encoding="utf-8")
            self.assertIn("format=3", proj_text)
            skill_text = (product / "scenes" / "Skills" / "GenericSkill.gd").read_text(encoding="utf-8")
            self.assertIn("@onready var stats", skill_text)

            # Verify forbidden Mob was NOT copied
            self.assertFalse((product / "scenes" / "Mobs" / "Mob.tscn").is_file())

            # Verify pre-seeded Dash Player file was not deleted or corrupted
            self.assertTrue(player_file.is_file())
            self.assertEqual(player_file.read_text(encoding="utf-8"), player_content)


if __name__ == "__main__":
    unittest.main()
