#!/usr/bin/env python3
"""P1-WAVE-J tests: drive shipped interactables_convert / scene+gdscript converters."""
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
from migration.interactables_convert import copy_and_convert_interactables  # noqa: E402

INTERACTABLE_SCENE = """[gd_scene load_steps=3 format=2]

[ext_resource path="res://Scenes/Interactables/Chest.gd" type="Script" id=1]
[ext_resource path="res://sprites/interactables/chest.png" type="Texture" id=2]

[node name="Chest" type="Node2D"]
script = ExtResource( 1 )

[node name="Sprite" type="Sprite" parent="."]
texture = ExtResource( 2 )
"""

INTERACTABLE_GD = (
    "extends Node2D\n"
    "class_name Chest\n"
    "onready var lid = get_node(\"Lid\")\n"
    "func _ready():\n"
    "\tlid.connect(\"opened\", self, \"on_lid_opened\")\n"
)

INTERACTABLE_TRES = """[gd_resource type="Resource" load_steps=2 format=2]

[ext_resource path="res://sprites/interactables/chest.png" type="Texture" id=1]

[resource]
sprite = ExtResource( 1 )
"""

LEGACY_INTERACTABLE_GD_RECOVERED = (
    "extends Node2D\n"
    "onready var lever = get_node(\"Lever\")\n"
    "func _ready():\n"
    "\tlever.connect(\"pulled\", self, \"on_lever_pulled\")\n"
)

LEGACY_INTERACTABLE_GD_WAVE_F = (
    "extends Node\n"
    "@onready var lever = get_node(\"Lever\")\n"
    "func _ready():\n"
    "\tlever.connect(\"pulled\", Callable(self, \"on_lever_pulled\"))\n"
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
    scene_dir = recovered / "Scenes" / "Interactables"
    scene_dir.mkdir(parents=True)
    (scene_dir / "Chest.tscn").write_text(INTERACTABLE_SCENE, encoding="utf-8")
    (scene_dir / "Chest.gd").write_text(INTERACTABLE_GD, encoding="utf-8")
    (scene_dir / "Chest.tres").write_text(INTERACTABLE_TRES, encoding="utf-8")
    sprite_dir = recovered / "sprites" / "interactables"
    sprite_dir.mkdir(parents=True)
    (sprite_dir / "chest.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00chst")
    (sprite_dir / "chest.png.import").write_text(
        "[remap]\nimporter=\"texture\"\n", encoding="utf-8")
    (sprite_dir / "chest.png.uid").write_text(
        "uid://bchestpng\n", encoding="utf-8")


class InteractablesConvertTest(unittest.TestCase):
    def test_interactable_scene_conversion(self):
        out = convert_scene_text(INTERACTABLE_SCENE)
        self.assertIn("format=3", out)
        self.assertIn('type="Sprite2D"', out)
        self.assertIn('type="Texture2D"', out)
        self.assertIn('ExtResource("1")', out)

        tres_out = convert_scene_text(INTERACTABLE_TRES)
        self.assertIn("format=3", tres_out)
        self.assertIn('ExtResource("1")', tres_out)

    def test_interactable_gdscript_conversion(self):
        out = convert_gdscript(INTERACTABLE_GD)
        self.assertIn("@onready var lid", out)
        self.assertIn("Callable(self, \"on_lid_opened\")", out)

    def test_multiple_roots_copy_convert_skip_sidecars(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            _seed_recovered(recovered)
            before_hashes = _fingerprint(recovered)

            result = copy_and_convert_interactables(
                recovered, product,
                roots=("Scenes/Interactables", "sprites/interactables"))

            after_hashes = _fingerprint(recovered)
            self.assertEqual(before_hashes, after_hashes)
            self.assertTrue(result["recovered_unmodified"])

            # Both roots converted into product layout
            tscn = (product / "scenes" / "Interactables" / "Chest.tscn").read_text(encoding="utf-8")
            gd = (product / "scenes" / "Interactables" / "Chest.gd").read_text(encoding="utf-8")
            tres = (product / "scenes" / "Interactables" / "Chest.tres").read_text(encoding="utf-8")
            self.assertIn("format=3", tscn)
            self.assertIn('type="Sprite2D"', tscn)
            self.assertIn("res://scenes/Interactables/Chest.gd", tscn)
            self.assertIn("@onready var lid", gd)
            self.assertIn("Callable(self, \"on_lid_opened\")", gd)
            self.assertIn("format=3", tres)

            # Binary copied verbatim; .import/.uid sidecars never copied
            self.assertEqual(
                (product / "sprites" / "interactables" / "chest.png").read_bytes(),
                b"\x89PNG\r\n\x1a\n\x00\x00\x00chst")
            self.assertFalse((product / "sprites" / "interactables" / "chest.png.import").exists())
            self.assertFalse((product / "sprites" / "interactables" / "chest.png.uid").exists())

            # Bookkeeping matches disk state
            self.assertEqual(result["files_copied"], len(result["copied"]))
            self.assertEqual(result["files_copied"], 4)
            self.assertEqual(len(result["converted_text_files"]), 3)
            self.assertEqual(result["binaries"], ["sprites/interactables/chest.png"])
            self.assertEqual(result["skipped_existing"], [])
            self.assertEqual(result["excluded"], [])
            self.assertEqual(result["residuals"], [])

    def test_exclude_file_and_directory_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            _seed_recovered(recovered)
            (recovered / "Scenes" / "Interactables" / "LegacyLever.gd").write_text(
                LEGACY_INTERACTABLE_GD_RECOVERED, encoding="utf-8")
            legacy_dir = recovered / "Scenes" / "Interactables" / "Legacy"
            legacy_dir.mkdir()
            (legacy_dir / "OldBarrel.tscn").write_text(
                INTERACTABLE_SCENE.replace("Chest", "OldBarrel"), encoding="utf-8")

            result = copy_and_convert_interactables(
                recovered,
                product,
                roots=("Scenes/Interactables", "sprites/interactables"),
                exclude=(
                    "Scenes/Interactables/LegacyLever.gd",
                    "Scenes/Interactables/Legacy",
                ),
            )

            # Excluded recovered file and directory prefix never reach product
            self.assertNotIn("scenes/Interactables/LegacyLever.gd", result["copied"])
            self.assertNotIn("scenes/Interactables/Legacy/OldBarrel.tscn", result["copied"])
            self.assertFalse((product / "scenes" / "Interactables" / "LegacyLever.gd").exists())
            self.assertFalse((product / "scenes" / "Interactables" / "Legacy").exists())
            self.assertEqual(sorted(result["excluded"]), [
                "Scenes/Interactables/Legacy/OldBarrel.tscn",
                "Scenes/Interactables/LegacyLever.gd",
            ])

            # Non-excluded siblings still converted
            tscn = (product / "scenes" / "Interactables" / "Chest.tscn").read_text(encoding="utf-8")
            self.assertIn("format=3", tscn)

    def test_preexisting_destination_not_overwritten_and_out_of_scope_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = Path(td) / "04_recovered"
            product = Path(td) / "product"

            _seed_recovered(recovered)

            # Pre-seed product with a migrated Chest.gd and a foreign Player file
            existing_file = product / "scenes" / "Interactables" / "Chest.gd"
            existing_file.parent.mkdir(parents=True)
            existing_file.write_text(LEGACY_INTERACTABLE_GD_WAVE_F, encoding="utf-8")
            player_dir = product / "scenes" / "Player"
            player_dir.mkdir()
            player_file = player_dir / "Player.gd"
            player_file.write_text(PLAYER_CONTENT, encoding="utf-8")

            result = copy_and_convert_interactables(
                recovered, product, roots=("Scenes/Interactables",))

            # Existing destination untouched and reported via skipped_existing
            self.assertEqual(existing_file.read_text(encoding="utf-8"), LEGACY_INTERACTABLE_GD_WAVE_F)
            self.assertIn("scenes/Interactables/Chest.gd", result["skipped_existing"])
            self.assertNotIn("scenes/Interactables/Chest.gd", result["copied"])

            # Out-of-scope files were not deleted or corrupted
            self.assertTrue(player_file.is_file())
            self.assertEqual(player_file.read_text(encoding="utf-8"), PLAYER_CONTENT)

            # Missing roots are silently ignored (only the given root is walked)
            self.assertFalse((product / "sprites").exists())


if __name__ == "__main__":
    unittest.main()
