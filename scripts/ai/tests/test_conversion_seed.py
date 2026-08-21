#!/usr/bin/env python3
"""P1-X0 unittests: drive shipped conversion_seed, not a reimplementation."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from migration.conversion_seed import (  # noqa: E402
    SEED_PROJECT,
    build_conversion_report,
    classify_engine_import_errors,
    is_godot4_project_text,
    parse_project_identity,
    write_product_seed,
)


class ConversionSeedTest(unittest.TestCase):
    def test_seed_text_is_godot4_not_3(self):
        ident = parse_project_identity(SEED_PROJECT)
        self.assertTrue(ident["is_godot4"])
        self.assertFalse(ident["is_godot3"])
        self.assertGreaterEqual(ident["config_version"], 5)
        self.assertTrue(any(f.startswith("4.") for f in ident["features"]))
        self.assertFalse(any(f.startswith("3.") for f in ident["features"]))
        self.assertTrue(is_godot4_project_text(SEED_PROJECT))

    def test_godot3_project_is_rejected(self):
        godot3 = "config_version=4\n[application]\nconfig/name=\"Mutagenic\"\n"
        ident = parse_project_identity(godot3)
        self.assertTrue(ident["is_godot3"])
        self.assertFalse(ident["is_godot4"])
        self.assertFalse(is_godot4_project_text(godot3))

    def test_write_product_seed_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            written = write_product_seed(product)
            project = product / "project.godot"
            self.assertTrue(project.is_file())
            self.assertIn("project.godot", written)
            text = project.read_text(encoding="utf-8")
            self.assertTrue(is_godot4_project_text(text))
            self.assertTrue((product / "scenes" / "seed.tscn").is_file())
            scene = (product / "scenes" / "seed.tscn").read_text(encoding="utf-8")
            self.assertIn("format=3", scene)
            self.assertNotIn("config_version=4", text)

    def test_missing_engine_is_classified_not_pass(self):
        errors = classify_engine_import_errors({"status": "NOT_FOUND", "tool_missing": True})
        self.assertTrue(errors)
        self.assertEqual(errors[0]["category"], "ENGINE_MISSING")
        self.assertEqual(errors[0]["severity"], "blocker")
        self.assertEqual(errors[0]["dependency"], "godot_4_7_1_binary")
        categories = {e["category"] for e in errors}
        self.assertNotIn("PASS", categories)

    def test_report_import_not_run_when_engine_missing(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td) / "product"
            write_product_seed(product)
            report = build_conversion_report(
                product,
                engine={"status": "NOT_FOUND", "tool_missing": True},
                import_output=None,
            )
            self.assertTrue(report["seed"]["identity"]["is_godot4"])
            self.assertEqual(report["static_parse"]["status"], "PASS")
            self.assertEqual(report["import_parse"]["status"], "NOT_RUN")
            self.assertEqual(report["engine"]["status"], "NOT_FOUND")
            self.assertNotEqual(report["import_parse"]["result"], "PASS")
            self.assertTrue(any(e["category"] == "ENGINE_MISSING" for e in report["import_parse"]["errors"]))


if __name__ == "__main__":
    unittest.main()
