#!/usr/bin/env python3
"""P1-WAVE-B tests: drive shipped boot_convert, not a reimplementation."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from migration.boot_convert import (  # noqa: E402
    convert_enum_commas,
    convert_gdscript,
    convert_input_object,
    convert_project_godot,
    copy_and_convert_boot,
    inject_class_name,
    remap_keycode,
)


MIN_PROJECT = """config_version=4

[application]
config/name="Mutagenic"
run/main_scene="res://Scenes/LoadGame.tscn"

[autoload]
Utils="*res://Globals/Utils.gd"
Globals="*res://Globals/Globals.gd"
Keybindings="*res://Globals/Keybindings.gd"
GameState="*res://Globals/GameState.gd"

[display]
window/size/width=1280
window/size/height=800
window/size/fullscreen=true

[input]
dash={
"deadzone": 0.5,
"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":0,"physical_scancode":16777237,"unicode":0,"echo":false,"script":null)
, Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":0,"button_index":1,"pressure":0.0,"pressed":false,"script":null)
 ]
}
interact={
"deadzone": 0.5,
"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":0,"physical_scancode":32,"unicode":0,"echo":false,"script":null)
 ]
}
move_left={
"deadzone": 0.5,
"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":0,"physical_scancode":65,"unicode":0,"echo":false,"script":null)
 ]
}
move_right={
"deadzone": 0.5,
"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":0,"physical_scancode":68,"unicode":0,"echo":false,"script":null)
 ]
}
move_up={
"deadzone": 0.5,
"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":0,"physical_scancode":87,"unicode":0,"echo":false,"script":null)
 ]
}
move_down={
"deadzone": 0.5,
"events": [ Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"alt":false,"shift":false,"control":false,"meta":false,"command":false,"pressed":false,"scancode":0,"physical_scancode":83,"unicode":0,"echo":false,"script":null)
 ]
}

[layer_names]
2d_physics/layer_1="Player Collider"

[physics]
2d/default_gravity=0

[rendering]
environment/default_clear_color=Color( 0.254902, 0.254902, 0.254902, 1 )
"""


class BootConvertTest(unittest.TestCase):
    def test_remap_special_keys(self):
        self.assertEqual(remap_keycode(16777221), 4194309)
        self.assertEqual(remap_keycode(32), 32)
        self.assertEqual(remap_keycode(65), 65)

    def test_input_event_key_uses_godot4_fields(self):
        blob = (
            'Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"",'
            '"device":0,"alt":false,"shift":false,"control":false,"meta":false,'
            '"command":false,"pressed":false,"scancode":0,"physical_scancode":16777221,'
            '"unicode":0,"echo":false,"script":null)'
        )
        out = convert_input_object(blob)
        self.assertIn("physical_keycode", out)
        self.assertIn("4194309", out)
        self.assertNotIn("physical_scancode", out)
        self.assertNotIn("scancode", out)
        self.assertIn("alt_pressed", out)
        self.assertIn("ctrl_pressed", out)
        self.assertNotIn('"command"', out)

    def test_project_is_godot4_and_keeps_actions_and_autoloads(self):
        result = convert_project_godot(MIN_PROJECT)
        text = result["text"]
        self.assertIn("config_version=5", text)
        self.assertIn('PackedStringArray("4.7"', text)
        self.assertNotIn("config_version=4", text)
        self.assertIn("window/size/viewport_width=1280", text)
        self.assertNotIn("window/size/width=", text)
        self.assertIn("dash=", text)
        self.assertTrue(result["input_actions"])
        for action in ("dash", "interact", "move_left", "move_right", "move_up", "move_down"):
            self.assertIn(action, result["input_actions"])
        names = [a["name"] for a in result["autoloads"]]
        self.assertEqual(names, ["Utils", "Globals", "Keybindings", "GameState"])
        self.assertIn("res://scenes/seed.tscn", text)
        self.assertNotIn("C:\\", text)
        self.assertNotIn("G:\\", text)

    def test_gdscript_mechanical_transforms(self):
        src = (
            "extends Node\n"
            "onready var powerups = []\n"
            "func _ready():\n"
            "\tpause_mode = Node.PAUSE_MODE_PROCESS\n"
            "\tSteam.connect(\"overlay_toggled\", self, \"_on_overlay\")\n"
            "\tyield(Steam, \"leaderboard_find_result\")\n"
            "\treturn PoolStringArray(names).join(\", \")\n"
            "\tvar f = File.new()\n"
            "\tvar datafile = \"res://passive_tree_data/passive_tree_gen.json\"\n"
            "\tf.open(datafile, File.READ)\n"
            "\tif f.file_exists(datafile):\n"
            "\t\tvar data = f.get_as_text()\n"
            "\t\tvar json = JSON.parse(data)\n"
            "\t\tif json.error == OK and typeof(json.result) == TYPE_DICTIONARY:\n"
            "\t\t\ttree_data = json.result\n"
        )
        out = convert_gdscript(src)
        self.assertIn("@onready var powerups", out)
        self.assertNotRegex(out, r"(?<!@)onready\s+var")
        self.assertIn("process_mode = Node.PROCESS_MODE_ALWAYS", out)
        self.assertNotIn("pause_mode", out)
        self.assertIn('Callable(self, "_on_overlay")', out)
        self.assertIn("await Steam.leaderboard_find_result", out)
        self.assertNotIn("yield(", out)
        self.assertIn('", ".join(PackedStringArray(names))', out)
        self.assertIn("FileAccess.open", out)
        self.assertNotIn("File.new()", out)
        self.assertIn("JSON.parse_string", out)
        self.assertIn("json != null", out)
        self.assertIn("snapped(", convert_gdscript("return stepify(amount, 0.01)\n"))

    def test_enum_commas_and_class_name(self):
        src = "enum ScalingType{\n\tFLAT\n\tPERCENT\n\tMORE\n}\n"
        out = convert_enum_commas(src)
        self.assertIn("FLAT,", out)
        self.assertIn("PERCENT,", out)
        self.assertIn("MORE,", out)
        injected = inject_class_name("extends Node\n\nvar x = 1\n", "GeneMods")
        self.assertIn("class_name GeneMods", injected)
        self.assertEqual(inject_class_name(injected, "GeneMods").count("class_name GeneMods"), 1)

    def test_copy_does_not_touch_recovered(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"
            gdir = recovered / "Globals"
            gdir.mkdir(parents=True)
            (recovered / "project.godot").write_text(MIN_PROJECT, encoding="utf-8")
            (gdir / "Utils.gd").write_text("extends Node\nonready var x = 1\n", encoding="utf-8")
            (gdir / "Globals.gd").write_text("extends Node\n", encoding="utf-8")
            (gdir / "Keybindings.gd").write_text("extends Node\n", encoding="utf-8")
            (gdir / "GameState.gd").write_text("extends Node\n", encoding="utf-8")
            data = recovered / "passive_tree_data"
            data.mkdir()
            (data / "passive_tree_gen.json").write_text('{"nodes":[]}\n', encoding="utf-8")
            before = hashlib.sha256((recovered / "Globals" / "Utils.gd").read_bytes()).hexdigest()
            result = copy_and_convert_boot(recovered, product)
            after = hashlib.sha256((recovered / "Globals" / "Utils.gd").read_bytes()).hexdigest()
            self.assertEqual(before, after)
            self.assertTrue(result["recovered_unmodified"])
            converted = (product / "Globals" / "Utils.gd").read_text(encoding="utf-8")
            self.assertIn("@onready var x", converted)
            self.assertTrue((product / "project.godot").is_file())
            self.assertTrue((product / "passive_tree_data" / "passive_tree_gen.json").is_file())
            self.assertIn("dash=", (product / "project.godot").read_text(encoding="utf-8"))
            self.assertEqual(result["scripts_converted"], 4)


if __name__ == "__main__":
    unittest.main()
