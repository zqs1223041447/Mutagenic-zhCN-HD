#!/usr/bin/env python3
"""P1-WAVE-K tests: drive shipped api_residue_convert.fix_api_residues."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from migration.api_residue_convert import fix_api_residues  # noqa: E402

REPLACEABLE_GD = (
    "extends Control\n"
    "func _ready():\n"
    "\tvar t: int = TYPE_REAL\n"
    "\tlabel.align = Label.ALIGN_RIGHT\n"
    "\tif alignment == ALIGN_CENTER:\n"
    "\t\talignment = ALIGN_LEFT\n"
    "\tvar s: Vector2 = rect_size\n"
    "\tscale = rect_scale\n"
    "\trect_min_size = Vector2(10, 20)\n"
    "\trect_position = Vector2.ZERO\n"
    "\tvar fps := Engine.get_screen_refresh_rate()\n"
    "\tvar actions := Input.get_action_list()\n"
    "\tprint(Input.get_scancode_string(KEY_A))\n"
    "\tself.update()\n"
    "\tupdate()  # redraw panel\n"
)

RESIDUAL_GD = (
    "extends Node\n"
    "func _ready():\n"
    "\tif OS.window_fullscreen:\n"
    "\t\tOS.window_borderless = false\n"
    "\tOS.vsync_enabled = true\n"
    "\tvar d = Directory.new()\n"
    "\td.open(\"res://data\")\n"
    "\td.list_dir_begin()\n"
    "\tyield(get_tree().create_timer(1.0), \"timeout\")\n"
    "\tEngine.set_target_fps(60)\n"
)

CONTEXT_SENSITIVE_GD = (
    "extends Control\n"
    "var arr := [ALIGN_RIGHT]\n"
    "var MY_ALIGN_RIGHT := 1\n"
    "func takes(a: int = ALIGN_LEFT):\n"
    "\tpass\n"
)

CLEAN_GD = (
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


def _seed_product(product: Path) -> None:
    (product / "scenes" / "ui").mkdir(parents=True)
    (product / "scenes" / "ui" / "residue.gd").write_text(REPLACEABLE_GD, encoding="utf-8")
    (product / "scenes" / "ui" / "residuals.gd").write_text(RESIDUAL_GD, encoding="utf-8")
    (product / "scenes" / "ui" / "context.gd").write_text(CONTEXT_SENSITIVE_GD, encoding="utf-8")
    (product / "scenes" / "Player").mkdir(parents=True)
    (product / "scenes" / "Player" / "Player.gd").write_text(CLEAN_GD, encoding="utf-8")


class ApiResidueConvertTest(unittest.TestCase):
    def test_replaceable_rules_rewrite_expected(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            _seed_product(product)

            result = fix_api_residues(product)

            out = (product / "scenes" / "ui" / "residue.gd").read_text(encoding="utf-8")
            self.assertIn("TYPE_FLOAT", out)
            self.assertNotIn("TYPE_REAL", out)
            self.assertIn("label.align = HORIZONTAL_ALIGNMENT_RIGHT", out)
            self.assertIn("if alignment == HORIZONTAL_ALIGNMENT_CENTER:", out)
            self.assertIn("alignment = HORIZONTAL_ALIGNMENT_LEFT", out)
            self.assertIn("var s: Vector2 = size", out)
            self.assertIn("scale = scale", out)
            self.assertIn("custom_minimum_size = Vector2(10, 20)", out)
            self.assertIn("position = Vector2.ZERO", out)
            self.assertNotIn("rect_size", out)
            self.assertNotIn("rect_scale", out)
            self.assertNotIn("rect_min_size", out)
            self.assertNotIn("rect_position", out)
            self.assertIn("DisplayServer.screen_get_refresh_rate()", out)
            self.assertIn("InputMap.action_get_ids()", out)
            self.assertIn("OS.get_keycode_string(KEY_A)", out)
            self.assertIn("\tqueue_redraw()", out)
            self.assertIn("\tqueue_redraw()  # redraw panel", out)
            self.assertNotIn("self.update()", out)
            self.assertNotIn("update()", out.replace("queue_redraw()", ""))
            self.assertEqual(result["files_changed"],
                             ["scenes/ui/context.gd", "scenes/ui/residue.gd"])
            self.assertEqual(
                len([r for r in result["replacements"] if r["file"] == "scenes/ui/residue.gd"]),
                13,
            )
            # context.gd contributes exactly one rewrite (default parameter)
            self.assertEqual(
                len([r for r in result["replacements"] if r["file"] == "scenes/ui/context.gd"]),
                1,
            )
            self.assertEqual(result["total_replacements"], len(result["replacements"]))

    def test_bare_align_only_in_assignment_or_comparison_context(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            _seed_product(product)

            result = fix_api_residues(product, files=("scenes/ui/context.gd",))

            out = (product / "scenes" / "ui" / "context.gd").read_text(encoding="utf-8")
            # Array literal context is not assignment/comparison: untouched
            self.assertIn("var arr := [ALIGN_RIGHT]", out)
            # Identifier containing ALIGN_* is never partially rewritten
            self.assertIn("var MY_ALIGN_RIGHT := 1", out)
            # Default parameter value is an assignment context
            self.assertIn("func takes(a: int = HORIZONTAL_ALIGNMENT_LEFT):", out)
            self.assertEqual(result["files_changed"], ["scenes/ui/context.gd"])

    def test_residuals_flagged_but_never_rewritten(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            _seed_product(product)

            result = fix_api_residues(product)

            self.assertEqual((product / "scenes" / "ui" / "residuals.gd").read_text(
                encoding="utf-8"), RESIDUAL_GD)
            flagged = {
                r["pattern"]
                for r in result["residuals"]
                if r["file"] == "scenes/ui/residuals.gd"
            }
            self.assertEqual(flagged, {
                "OS.window_*",
                "OS.vsync_enabled",
                "Directory",
                "yield(",
                "Engine.set_target_fps(",
            })
            for entry in result["residuals"]:
                self.assertIn("MANUAL_REVIEW", entry["reason"])

    def test_dry_run_reports_without_modifying_files(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            _seed_product(product)
            before = _fingerprint(product)

            result = fix_api_residues(product, dry_run=True)
            after = _fingerprint(product)

            self.assertEqual(before, after)
            self.assertTrue(result["dry_run"])
            self.assertTrue(result["files_changed"])
            self.assertTrue(result["total_replacements"] > 0)
            self.assertTrue(any(
                r["pattern"] == "OS.window_*" for r in result["residuals"]))

    def test_clean_files_untouched_and_absent_from_report(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            _seed_product(product)
            before = _fingerprint(product)

            result = fix_api_residues(product)

            self.assertEqual(_fingerprint(product)["scenes/Player/Player.gd"],
                             before["scenes/Player/Player.gd"])
            self.assertEqual((product / "scenes" / "Player" / "Player.gd").read_text(
                encoding="utf-8"), CLEAN_GD)
            self.assertNotIn("scenes/Player/Player.gd", result["files_changed"])
            self.assertFalse(any(
                r["file"] == "scenes/Player/Player.gd"
                for r in result["replacements"]))
            self.assertFalse(any(
                r["file"] == "scenes/Player/Player.gd"
                for r in result["residuals"]))

    def test_explicit_file_list_limits_scope(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            _seed_product(product)
            before = _fingerprint(product)

            result = fix_api_residues(
                product,
                files=("scenes\\ui\\residue.gd", "scenes/Player/missing.gd"),
            )

            # Only the listed existing .gd file was rewritten
            self.assertEqual(_fingerprint(product)["scenes/ui/residuals.gd"],
                             before["scenes/ui/residuals.gd"])
            self.assertEqual((product / "scenes" / "ui" / "residuals.gd").read_text(
                encoding="utf-8"), RESIDUAL_GD)
            self.assertEqual(result["files_changed"], ["scenes/ui/residue.gd"])
            self.assertFalse(result["residuals"])
            # Missing files are silently ignored like missing roots elsewhere
            self.assertFalse((product / "scenes" / "Player" / "missing.gd").exists())


if __name__ == "__main__":
    unittest.main()
