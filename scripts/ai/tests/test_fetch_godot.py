#!/usr/bin/env python3
"""fetch_godot tests: official 4.7.1 URL, repo-relative dest, no host drives."""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "bootstrap"))

import fetch_godot as fg  # noqa: E402


class FetchGodotTest(unittest.TestCase):
    def test_url_is_official_4_7_1(self):
        url = fg.official_url("windows")
        self.assertTrue(url.startswith("https://github.com/godotengine/godot-builds/releases/download/"))
        self.assertIn("4.7.1-stable", url)
        self.assertIn("Godot_v4.7.1-stable_win64.exe.zip", url)
        linux = fg.official_url("linux")
        self.assertIn("Godot_v4.7.1-stable_linux.x86_64.zip", linux)

    def test_dest_is_repo_relative(self):
        dest = fg.dest_dir(Path("some-root"))
        self.assertEqual(dest.as_posix(), "some-root/02_tools/godot")
        src = Path(fg.__file__).read_text(encoding="utf-8")
        self.assertNotIn("C:\\", src)
        self.assertNotIn("G:\\", src)
        self.assertNotIn("/Users/", src)

    def test_fetch_extracts_without_network(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("Godot_v4.7.1-stable_win64.exe", b"fake-godot")
        payload = buf.getvalue()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = fg.fetch_godot(root, platform="windows", download=lambda url: payload)
            self.assertEqual(result["status"], "FETCHED")
            self.assertEqual(result["wanted"], "4.7.1")
            self.assertEqual(result["dest"], "02_tools/godot")
            written = root / "02_tools" / "godot" / "Godot_v4.7.1-stable_win64.exe"
            self.assertTrue(written.is_file())
            self.assertEqual(written.read_bytes(), b"fake-godot")
            self.assertTrue((root / "02_tools" / "godot" / "VERSION.txt").is_file())


if __name__ == "__main__":
    unittest.main()
