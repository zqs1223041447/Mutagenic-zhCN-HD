#!/usr/bin/env python3
"""P1-WAVE-C tests: drive shipped menu_convert / convert_gdscript."""
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
from migration.menu_convert import (  # noqa: E402
    collect_menu_files,
    convert_scene_text,
    copy_and_convert_menu,
    set_main_scene,
)


LOADGAME_SCENE = """[gd_scene load_steps=5 format=2]

[ext_resource path="res://Themes/MainTheme.tres" type="Theme" id=1]
[ext_resource path="res://Scenes/LoadGame.gd" type="Script" id=2]
[ext_resource path="res://sprites/splash/background_blurred.png" type="Texture" id=3]

[sub_resource type="StyleBoxFlat" id=1]
bg_color = Color( 0, 0, 0, 1 )

[node name="LoadGame" type="PanelContainer"]
anchor_right = 1.0
margin_left = -1.0
theme = ExtResource( 1 )
custom_styles/panel = SubResource( 1 )
script = ExtResource( 2 )

[node name="TextureRect" type="TextureRect" parent="."]
margin_right = 1280.0
texture = ExtResource( 3 )
expand = true
stretch_mode = 7
"""


class MenuConvertTest(unittest.TestCase):
    def test_scene_format_and_ext_resource(self):
        out = convert_scene_text(LOADGAME_SCENE)
        self.assertIn("format=3", out)
        self.assertNotIn("format=2", out)
        self.assertIn('id="1"', out)
        self.assertIn('type="Texture2D"', out)
        self.assertIn('ExtResource("1")', out)
        self.assertIn('SubResource("1")', out)
        self.assertIn("offset_left", out)
        self.assertNotIn("margin_left", out)
        self.assertIn("theme_override_styles/panel", out)
        self.assertIn("expand_mode = 1", out)
        self.assertIn("Color(0, 0, 0, 1)", out)

    def test_loadgame_script_renames(self):
        src = (
            "extends PanelContainer\n"
            "func _ready() -> void :\n"
            "\tvar refresh = OS.get_screen_refresh_rate()\n"
            "\tEngine.iterations_per_second = 60\n"
            "\t$CenterContainer / VBoxContainer / StartButton.grab_focus()\n"
            "\tGameState.connect(\"changed\", self, \"render\")\n"
        )
        out = convert_gdscript(src)
        self.assertIn("DisplayServer.screen_get_refresh_rate()", out)
        self.assertIn("Engine.physics_ticks_per_second", out)
        self.assertIn("$CenterContainer/VBoxContainer/StartButton", out)
        self.assertNotIn(" / ", out.split("connect", 1)[0])
        self.assertIn("Callable(self, \"render\")", out)

    def test_set_main_scene(self):
        text = 'config_version=5\n[application]\nrun/main_scene="res://scenes/seed.tscn"\n'
        out = set_main_scene(text, "res://scenes/LoadGame.tscn")
        self.assertIn('run/main_scene="res://scenes/LoadGame.tscn"', out)
        self.assertNotIn("seed.tscn", out)

    def test_copy_does_not_touch_recovered(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"
            (recovered / "Scenes").mkdir(parents=True)
            (recovered / "Themes").mkdir()
            (recovered / "sprites" / "splash").mkdir(parents=True)
            (recovered / "Scenes" / "LoadGame.tscn").write_text(LOADGAME_SCENE, encoding="utf-8")
            (recovered / "Scenes" / "LoadGame.gd").write_text(
                "extends PanelContainer\nfunc _ready():\n\tOS.get_screen_refresh_rate()\n",
                encoding="utf-8",
            )
            (recovered / "Scenes" / "Menu.tscn").write_text(
                '[gd_scene format=2]\n[ext_resource path="res://Scenes/Menu.gd" type="Script" id=1]\n'
                '[node name="Menu" type="PanelContainer"]\nscript = ExtResource( 1 )\n',
                encoding="utf-8",
            )
            (recovered / "Scenes" / "Menu.gd").write_text("extends PanelContainer\n", encoding="utf-8")
            (recovered / "Themes" / "MainTheme.tres").write_text(
                '[gd_resource type="Theme" format=2]\n', encoding="utf-8"
            )
            png = recovered / "sprites" / "splash" / "background_blurred.png"
            png.write_bytes(b"\x89PNG\r\n")
            (product / "project.godot").parent.mkdir(parents=True)
            (product / "project.godot").write_text(
                'config_version=5\n[application]\nrun/main_scene="res://scenes/seed.tscn"\n',
                encoding="utf-8",
            )
            before = hashlib.sha256((recovered / "Scenes" / "LoadGame.gd").read_bytes()).hexdigest()
            result = copy_and_convert_menu(recovered, product)
            after = hashlib.sha256((recovered / "Scenes" / "LoadGame.gd").read_bytes()).hexdigest()
            self.assertEqual(before, after)
            self.assertTrue(result["recovered_unmodified"])
            self.assertTrue((product / "scenes" / "LoadGame.tscn").is_file())
            scene = (product / "scenes" / "LoadGame.tscn").read_text(encoding="utf-8")
            self.assertIn("format=3", scene)
            self.assertIn("res://scenes/", scene)
            gd = (product / "scenes" / "LoadGame.gd").read_text(encoding="utf-8")
            self.assertIn("DisplayServer.screen_get_refresh_rate()", gd)
            project = (product / "project.godot").read_text(encoding="utf-8")
            self.assertIn("LoadGame.tscn", project)
            self.assertTrue((product / "sprites" / "splash" / "background_blurred.png").is_file())

    def test_collect_skips_forbidden_world(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td)
            (recovered / "Scenes").mkdir()
            (recovered / "Scenes" / "LoadGame.tscn").write_text(
                '[gd_scene format=2]\n[ext_resource path="res://Scenes/World.tscn" type="PackedScene" id=1]\n'
                '[ext_resource path="res://Scenes/LoadGame.gd" type="Script" id=2]\n',
                encoding="utf-8",
            )
            (recovered / "Scenes" / "LoadGame.gd").write_text("extends Node\n", encoding="utf-8")
            (recovered / "Scenes" / "World.tscn").write_text("[gd_scene format=2]\n", encoding="utf-8")
            files = collect_menu_files(recovered, roots=["Scenes/LoadGame.tscn"])
            self.assertIn("Scenes/LoadGame.tscn", files)
            self.assertNotIn("Scenes/World.tscn", files)


if __name__ == "__main__":
    unittest.main()
