#!/usr/bin/env python3
"""P1-WAVE-D tests: drive shipped world_convert / scene+gdscript converters."""
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
from migration.world_convert import copy_and_convert_world  # noqa: E402


WORLD_SCENE = """[gd_scene load_steps=3 format=2]

[ext_resource path="res://Scenes/World.gd" type="Script" id=1]

[node name="World" type="Node2D"]
script = ExtResource( 1 )

[node name="Level" type="YSort" parent="."]
z_index = 512
"""


class WorldConvertTest(unittest.TestCase):
    def test_ysort_and_pool_arrays(self):
        out = convert_scene_text(WORLD_SCENE + "points = PoolVector2Array( 0, 32 )\n")
        self.assertIn("format=3", out)
        self.assertNotIn('type="YSort"', out)
        self.assertIn('type="Node2D"', out)
        self.assertIn("y_sort_enabled = true", out)
        self.assertIn("PackedVector2Array", out)

    def test_player_movement_renames(self):
        src = (
            "extends RigidBody2D\n"
            "func _physics_process(delta):\n"
            "\tif Input.is_mouse_button_pressed(BUTTON_LEFT):\n"
            "\t\tpathing_target = get_global_mouse_position()\n"
            "\tif Input.is_action_just_pressed(\"dash\"):\n"
            "\t\tapply_central_impulse(velocity.normalized() * Constants.DASH_AMOUNT)\n"
            "\tthread.start(self, \"_load_tiles\")\n"
        )
        out = convert_gdscript(src)
        self.assertIn("MOUSE_BUTTON_LEFT", out)
        self.assertNotRegex(out, r"(?<![A-Z_])BUTTON_LEFT")
        self.assertIn('Input.is_action_just_pressed("dash")', out)
        self.assertIn("apply_central_impulse", out)
        self.assertIn('thread.start(Callable(self, "_load_tiles"))', out)

    def test_copy_world_does_not_touch_recovered(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"
            (recovered / "Scenes" / "Player").mkdir(parents=True)
            (recovered / "Scenes" / "Levels" / "Default").mkdir(parents=True)
            (recovered / "Scenes" / "World.tscn").write_text(WORLD_SCENE, encoding="utf-8")
            (recovered / "Scenes" / "World.gd").write_text(
                "extends Node2D\nvar player_scene = preload(\"res://Scenes/Player/Player.tscn\")\n",
                encoding="utf-8",
            )
            (recovered / "Scenes" / "Player" / "Player.tscn").write_text(
                '[gd_scene format=2]\n[ext_resource path="res://Scenes/Player/Player.gd" type="Script" id=1]\n'
                '[node name="Player" type="RigidBody2D"]\nscript = ExtResource( 1 )\n',
                encoding="utf-8",
            )
            (recovered / "Scenes" / "Player" / "Player.gd").write_text(
                "extends RigidBody2D\nfunc _physics_process(d):\n\tInput.is_mouse_button_pressed(BUTTON_LEFT)\n",
                encoding="utf-8",
            )
            (recovered / "Scenes" / "Levels" / "BaseLevel.tscn").write_text("[gd_scene format=2]\n", encoding="utf-8")
            (recovered / "Scenes" / "Levels" / "BaseLevel.gd").write_text("extends Node2D\n", encoding="utf-8")
            (recovered / "Scenes" / "Levels" / "SpawnLocation.tscn").write_text("[gd_scene format=2]\n", encoding="utf-8")
            (recovered / "Scenes" / "Levels" / "Default" / "DefaultLevel.tscn").write_text(
                "[gd_scene format=2]\n", encoding="utf-8"
            )
            (recovered / "Scenes" / "Skills" / "GenericSkill.tscn").parent.mkdir(parents=True, exist_ok=True)
            (recovered / "Scenes" / "Skills" / "GenericSkill.tscn").write_text("[gd_scene format=2]\n", encoding="utf-8")
            before = hashlib.sha256((recovered / "Scenes" / "World.gd").read_bytes()).hexdigest()
            result = copy_and_convert_world(recovered, product)
            after = hashlib.sha256((recovered / "Scenes" / "World.gd").read_bytes()).hexdigest()
            self.assertEqual(before, after)
            self.assertTrue(result["recovered_unmodified"])
            self.assertTrue((product / "scenes" / "World.tscn").is_file())
            self.assertTrue((product / "scenes" / "Player" / "Player.gd").is_file())
            player = (product / "scenes" / "Player" / "Player.gd").read_text(encoding="utf-8")
            self.assertIn("MOUSE_BUTTON_LEFT", player)
            world = (product / "scenes" / "World.tscn").read_text(encoding="utf-8")
            self.assertIn("y_sort_enabled = true", world)
            self.assertFalse((product / "scenes" / "Skills" / "GenericSkill.tscn").is_file())


if __name__ == "__main__":
    unittest.main()
