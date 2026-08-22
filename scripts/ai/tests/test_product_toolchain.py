#!/usr/bin/env python3
"""P1-X2 unittests: drive shipped product_toolchain discovery."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "bootstrap"))

import product_toolchain as pt  # noqa: E402


class FakeProc(SimpleNamespace):
    pass


class ProductToolchainTest(unittest.TestCase):
    def test_missing_binary_is_not_found_never_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = pt.discover_product_godot(
                root,
                environ={},
                which=lambda name: None,
                is_file=lambda p: False,
                run=lambda cmd: FakeProc(stdout="", stderr="", returncode=0),
            )
        self.assertEqual(result["engine"]["status"], "NOT_FOUND")
        self.assertTrue(result["engine"]["tool_missing"])
        self.assertFalse(result["engine"]["binary_present"])
        self.assertEqual(result["overall"], "NOT_FOUND")
        self.assertNotEqual(result["engine"]["status"], "PASS")
        self.assertNotEqual(result["overall"], "PASS")
        self.assertEqual(result["private_assets"]["status"], "MISSING_PRIVATE")

    def test_success_requires_version_4_7_1(self):
        wanted = Path("/tools/godot471")  # posix, not a host drive letter in production source
        result = pt.discover_product_godot(
            Path("."),
            environ={"MUTAGENIC_GODOT_4": str(wanted)},
            which=lambda name: None,
            is_file=lambda p: Path(p) == wanted,
            run=lambda cmd: FakeProc(stdout="Godot Engine v4.7.1.stable.official\n", stderr="", returncode=0),
        )
        self.assertEqual(result["engine"]["status"], "SUCCESS")
        self.assertEqual(result["engine"]["version"], "4.7.1")
        self.assertTrue(result["engine"]["binary_present"])
        self.assertEqual(result["overall"], "SUCCESS")
        self.assertNotEqual(result["overall"], "PASS")

    def test_wrong_version_is_mismatch_not_pass(self):
        wanted = Path("/tools/godot42")
        result = pt.discover_product_godot(
            Path("."),
            environ={"MUTAGENIC_GODOT_4": str(wanted)},
            which=lambda name: None,
            is_file=lambda p: Path(p) == wanted,
            run=lambda cmd: FakeProc(stdout="4.2.2.stable\n", stderr="", returncode=0),
        )
        self.assertEqual(result["engine"]["status"], "VERSION_MISMATCH")
        self.assertEqual(result["engine"]["version"], "4.2.2")
        self.assertNotEqual(result["engine"]["status"], "PASS")
        self.assertNotEqual(result["overall"], "PASS")
        self.assertNotEqual(result["overall"], "SUCCESS")

    def test_binary_crash_is_tool_failed(self):
        wanted = Path("/tools/broken-godot")
        result = pt.discover_product_godot(
            Path("."),
            environ={"GODOT_BIN": str(wanted)},
            which=lambda name: None,
            is_file=lambda p: Path(p) == wanted,
            run=lambda cmd: (_ for _ in ()).throw(OSError("exec format error")),
        )
        self.assertEqual(result["engine"]["status"], "TOOL_FAILED")
        self.assertNotEqual(result["overall"], "PASS")

    def test_private_present_does_not_invent_engine_success(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "00_original").mkdir()
            (root / "00_original" / "Mutagenic.exe").write_bytes(b"x")
            (root / "manifests").mkdir()
            (root / "manifests" / "script_key.txt").write_text("ab" * 32, encoding="utf-8")
            result = pt.discover_product_godot(
                root,
                environ={},
                which=lambda name: None,
                is_file=lambda p: Path(p).is_file(),
                run=lambda cmd: FakeProc(stdout="", stderr="", returncode=0),
            )
        self.assertEqual(result["private_assets"]["status"], "PRESENT")
        self.assertEqual(result["engine"]["status"], "NOT_FOUND")
        self.assertEqual(result["overall"], "NOT_FOUND")

    def test_parse_godot_version(self):
        self.assertEqual(pt.parse_godot_version("4.7.1.stable.official"), "4.7.1")
        self.assertEqual(pt.parse_godot_version("Godot Engine v4.7.1.stable.official [hash]"), "4.7.1")
        self.assertTrue(pt.version_is_wanted("4.7.1"))
        self.assertFalse(pt.version_is_wanted("4.2.2"))
        self.assertFalse(pt.version_is_wanted(None))

    def test_source_has_no_host_drive_literals(self):
        src = (REPO / "scripts" / "bootstrap" / "product_toolchain.py").read_text(encoding="utf-8")
        self.assertNotIn("C:\\", src)
        self.assertNotIn("G:\\", src)
        self.assertNotIn("C:/Users", src)
        self.assertNotIn("G:/Mutageni", src)

    def test_headless_not_called_classification_without_binary(self):
        with tempfile.TemporaryDirectory() as td:
            product = Path(td)
            out = pt.run_headless_import(
                "/tools/godot471",
                product,
                run=lambda cmd: FakeProc(stdout="Godot Engine 4.7.1\n", stderr="", returncode=0),
            )
        self.assertEqual(out["status"], "RAN")
        self.assertEqual(out["cmd_name"], "godot471")

    def test_sanitize_omits_host_path(self):
        result = {
            "engine": {"binary": "Z:/host/godot.exe", "binary_name": "godot.exe", "status": "SUCCESS"},
            "overall": "SUCCESS",
        }
        cleaned = pt.sanitize_for_commit(result)
        self.assertEqual(cleaned["engine"]["binary"], "godot.exe")
        self.assertTrue(cleaned["engine"]["binary_host_path_omitted"])


if __name__ == "__main__":
    unittest.main()
