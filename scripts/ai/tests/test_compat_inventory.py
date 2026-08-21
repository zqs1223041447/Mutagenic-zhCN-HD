#!/usr/bin/env python3
"""P1-X1 unittests: drive shipped inventory scanner, not a reimplementation."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from migration.inventory import (  # noqa: E402
    build_blocker_dag,
    scan_file_text,
    scan_resource_text,
    scan_scene_text,
    scan_script_text,
    scan_settings_text,
    scan_tree,
)

REQUIRED_FIELDS = ("category", "path", "severity", "dependency")

SCRIPT_FIXTURE = """extends KinematicBody2D
onready var sprite = $Sprite
func _ready():
\tyield(get_tree(), "idle_frame")
\tvar n = packed.instance()
\tvar f = File.new()
"""

SCENE_FIXTURE = """[gd_scene load_steps=2 format=2]

[node name="Mob" type="KinematicBody2D"]
[node name="Fx" type="Particles2D"]
"""

RESOURCE_FIXTURE = """[gd_resource type="Environment" load_steps=2 format=2]

[sub_resource type="ProceduralSky" id=1]
"""

SETTINGS_FIXTURE = """config_version=4

[application]
config/name="Mutagenic"

[display]
window/size/width=1280
window/size/height=800
"""


def _assert_fields(test: unittest.TestCase, items: list) -> None:
    test.assertTrue(items, "scanner must report at least one item for the fixture")
    for item in items:
        for field in REQUIRED_FIELDS:
            test.assertIn(field, item)
            test.assertTrue(item[field], f"{field} must be non-empty")


class CompatInventoryTest(unittest.TestCase):
    def test_script_scanner_fields(self):
        items = scan_script_text("Globals/Player.gd", SCRIPT_FIXTURE)
        _assert_fields(self, items)
        self.assertTrue(all(i["category"] == "Script" for i in items))
        deps = {i["dependency"] for i in items}
        self.assertIn("await", deps)
        self.assertIn("instantiate", deps)
        self.assertIn("FileAccess", deps)

    def test_scene_scanner_fields(self):
        items = scan_scene_text("Scenes/Mob.tscn", SCENE_FIXTURE)
        _assert_fields(self, items)
        self.assertTrue(all(i["category"] == "Scene" for i in items))
        deps = {i["dependency"] for i in items}
        self.assertIn("scene_format_3", deps)
        self.assertIn("CharacterBody2D", deps)

    def test_resource_scanner_fields(self):
        items = scan_resource_text("default_env.tres", RESOURCE_FIXTURE)
        _assert_fields(self, items)
        self.assertTrue(all(i["category"] == "Resource" for i in items))

    def test_settings_scanner_fields(self):
        items = scan_settings_text("project.godot", SETTINGS_FIXTURE)
        _assert_fields(self, items)
        self.assertTrue(all(i["category"] == "Settings" for i in items))
        deps = {i["dependency"] for i in items}
        self.assertIn("config_version_5", deps)

    def test_scan_tree_and_blocker_dag(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "Globals").mkdir()
            (root / "Scenes").mkdir()
            (root / "Globals" / "Player.gd").write_text(SCRIPT_FIXTURE, encoding="utf-8")
            (root / "Scenes" / "Mob.tscn").write_text(SCENE_FIXTURE, encoding="utf-8")
            (root / "default_env.tres").write_text(RESOURCE_FIXTURE, encoding="utf-8")
            (root / "project.godot").write_text(SETTINGS_FIXTURE, encoding="utf-8")
            report = scan_tree(root, recovered_label="04_recovered")
        cats = set(report["categories"])
        self.assertEqual(cats, {"Script", "Scene", "Resource", "Settings"})
        _assert_fields(self, report["items"])
        dag = report["blocker_dag"]
        self.assertIn("nodes", dag)
        self.assertIn("edges", dag)
        self.assertGreater(dag["node_count"], 0)
        node_cats = {n["category"] for n in dag["nodes"]}
        self.assertEqual(node_cats, {"Script", "Scene", "Resource", "Settings"})

    def test_build_blocker_dag_on_empty_is_still_a_dag(self):
        dag = build_blocker_dag([])
        self.assertEqual(dag["nodes"], [])
        self.assertEqual(dag["edges"], [])
        self.assertEqual(dag["node_count"], 0)

    def test_scan_file_text_dispatches_by_suffix(self):
        self.assertTrue(scan_file_text("x.gd", SCRIPT_FIXTURE))
        self.assertTrue(scan_file_text("x.tscn", SCENE_FIXTURE))
        self.assertTrue(scan_file_text("x.tres", RESOURCE_FIXTURE))
        self.assertTrue(scan_file_text("project.godot", SETTINGS_FIXTURE))


if __name__ == "__main__":
    unittest.main()
