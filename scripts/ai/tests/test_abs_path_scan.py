#!/usr/bin/env python3
"""abs_path_scan: positive/negative classification tests.

Proves:
  - production hardcode fixture            -> production_hardcode / FAIL
  - docs placeholder example               -> docs_example / INFO (no FAIL)
  - provenance manifest "source"           -> provenance_metadata / WARN (no FAIL, file untouched)
  - Windows font default                   -> local_config (no FAIL)
  - bootstrap_deploy.py                    -> no hits
  - res:// / user:// / https:// / http://  -> no hits
  - Windows drive + UNC + posix-user paths -> detected
"""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import abs_path_scan  # noqa: E402
import repo_util  # noqa: E402
from test_helpers import TEST_ROOT, commit_all, make_repo, seed_repo, temp_area  # noqa: E402


class ClassifyTest(unittest.TestCase):
    def test_production_hardcode(self):
        cls, _ = abs_path_scan.classify("scripts/nlmod/build_mod.py", r"G:\opencode-Mutageni")
        self.assertEqual(cls, "production_hardcode")
        cls, _ = abs_path_scan.classify("scripts/foo.py", r"D:\tools\gdre")
        self.assertEqual(cls, "production_hardcode")
        cls, _ = abs_path_scan.classify("scripts/foo.py", "/Users/alice/mutagenic")
        self.assertEqual(cls, "production_hardcode")

    def test_provenance_metadata(self):
        cls, _ = abs_path_scan.classify("manifests/recovered_clean_manifest.json",
                                        r"F:\SteamLibrary\steamapps\common\Mutagenic", "source")
        self.assertEqual(cls, "provenance_metadata")
        cls, _ = abs_path_scan.classify("status.json", r"C:\Users\ZQS\AppData\Roaming\Godot",
                                        "gate_scope.persistence_track")
        self.assertEqual(cls, "provenance_metadata")
        cls, _ = abs_path_scan.classify("04_recovered/Globals/Stats.gd", r"G:\anything")
        self.assertEqual(cls, "provenance_metadata")

    def test_local_config(self):
        cls, _ = abs_path_scan.classify("tools.lock.json", "F:/SteamLibrary/steamapps/common/Mutagenic",
                                        "project_root")
        self.assertEqual(cls, "local_config")
        cls, _ = abs_path_scan.classify("scripts/merge_fonts3_hinted.py", "C:/Windows/Fonts/Deng.ttf")
        self.assertEqual(cls, "local_config")

    def test_docs_example_and_placeholder(self):
        cls, _ = abs_path_scan.classify("docs/DEPLOYMENT.md", r"C:\path\to\Mutagenic.exe")
        self.assertEqual(cls, "docs_example")
        cls, _ = abs_path_scan.classify("scripts/foo.py", r"C:\path\to\Mutagenic.exe")
        self.assertEqual(cls, "docs_example")

    def test_test_fixture(self):
        cls, _ = abs_path_scan.classify("tests/fixtures/x.py", r"C:\Users\Someone")
        self.assertEqual(cls, "test_fixture")
        cls, _ = abs_path_scan.classify("scripts/ai/tests/fixtures/production_hardcode.py",
                                        r"C:\Users\Someone\Mutagenic")
        self.assertEqual(cls, "test_fixture")

    def test_severity_mapping(self):
        self.assertEqual(abs_path_scan.CLASS_SEVERITY["production_hardcode"], "FAIL")
        self.assertEqual(abs_path_scan.CLASS_SEVERITY["docs_example"], "INFO")


class ScanTextTest(unittest.TestCase):
    def test_schemes_are_ignored(self):
        text = 'scene = "res://Scenes/Menu.tscn"\nsave = "user://_0_6_0.dat"\n'
        text += 'link = "https://discord.gg/TzF3aRWnhZ"\nhttp = "http://example.com/x"\n'
        hits = abs_path_scan.scan_text("scripts/sample.py", text, Path("scripts/sample.py"))
        self.assertEqual(hits, [])

    def test_drive_and_unc_detected(self):
        text = 'ROOT = Path(r"G:\\opencode-Mutageni")\nshare = "\\\\host\\share\\dir"\n'
        hits = abs_path_scan.scan_text("scripts/sample.py", text, Path("scripts/sample.py"))
        classes = [h["classification"] for h in hits]
        self.assertIn("production_hardcode", classes)
        self.assertTrue(any("\\\\host\\share" in h["matched"] for h in hits))

    def test_line_numbers(self):
        text = 'a = 1\nROOT = Path(r"D:\\x\\y")\n'
        hits = abs_path_scan.scan_text("scripts/sample.py", text, Path("scripts/sample.py"))
        self.assertEqual(hits[0]["line"], 2)


class FixtureScanTest(unittest.TestCase):
    """Fixtures live under scripts/ai/tests/fixtures - must never FAIL scans."""

    def test_production_hardcode_fixture_classified(self):
        hits = self._scan_fixture("production_hardcode.py", "scripts/ai/tests/fixtures/production_hardcode.py")
        self.assertTrue(hits)
        self.assertTrue(all(h["classification"] != "production_hardcode" for h in hits),
                        "fixtures must not count as production_hardcode")

    def test_docs_example_fixture(self):
        hits = self._scan_fixture("docs_example.py", "scripts/ai/tests/fixtures/docs_example.py")
        self.assertTrue(all(h["classification"] == "docs_example" for h in hits))

    def test_provenance_fixture(self):
        hits = self._scan_fixture("provenance_manifest.json", "scripts/ai/tests/fixtures/provenance_manifest.json")
        self.assertTrue(hits)
        self.assertTrue(all(h["classification"] == "provenance_metadata" for h in hits))

    def test_windows_font_fixture(self):
        hits = self._scan_fixture("windows_font_default.py", "scripts/ai/tests/fixtures/windows_font_default.py")
        self.assertTrue(all(h["classification"] == "local_config" for h in hits))

    def test_scheme_fixture(self):
        hits = self._scan_fixture("scheme_only.py", "scripts/ai/tests/fixtures/scheme_only.py")
        self.assertEqual(hits, [])

    @staticmethod
    def _scan_fixture(name: str, rel: str):
        fixture = TEST_ROOT / rel
        text = fixture.read_text(encoding="utf-8")
        return abs_path_scan.scan_text(rel, text, fixture)


class CliIntegrationTest(unittest.TestCase):
    """CLI-level: hardcode fixture FAILs the scan; docs/provenance do not."""

    def setUp(self):
        self.area = temp_area()
        self.base = Path(self.area.name)
        self.repo = make_repo(self.base)
        seed_repo(self.repo)
        self.orig_cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.orig_cwd)
        self.area.cleanup()

    def _write_tracked(self, rel: str, content: str):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        commit_all(self.repo, f"add {rel}")

    def test_hardcode_fixture_fails_cli(self):
        self._write_tracked("scripts/evil.py", 'from pathlib import Path\nROOT = Path(r"C:\\Users\\Someone\\Mutagenic")\n')
        os.chdir(str(self.repo))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = abs_path_scan.main([])
        out = buf.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn("production_hardcode", out)
        self.assertIn("scripts/evil.py", out)

    def test_docs_example_does_not_fail_cli(self):
        self._write_tracked("docs/example.py", 'shutil.copy("C:\\\\path\\\\to\\\\Mutagenic.exe", "00_original\\\\x.exe")\n')
        os.chdir(str(self.repo))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = abs_path_scan.main([])
        self.assertEqual(rc, 0)

    def test_provenance_manifest_does_not_fail_and_is_untouched(self):
        content = '{"source": "F:\\\\SteamLibrary\\\\steamapps\\\\common\\\\Mutagenic\\\\rec"}\n'
        self._write_tracked("manifests/recovered_clean_manifest.json", content)
        path = self.repo / "manifests" / "recovered_clean_manifest.json"
        before = path.read_bytes()
        os.chdir(str(self.repo))
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = abs_path_scan.main([])
        self.assertEqual(rc, 0)
        self.assertIn("provenance_metadata", buf.getvalue())
        self.assertEqual(path.read_bytes(), before, "scanner must never rewrite provenance files")

    def test_non_repo_cwd_fails_gracefully(self):
        os.chdir(str(self.base))
        with redirect_stdout(io.StringIO()):
            rc = abs_path_scan.main([])
        self.assertEqual(rc, 2)


class RealRepoScanTest(unittest.TestCase):
    """First-round portability sweep over the actual repo (this worktree)."""

    def test_full_repo_no_production_hardcode(self):
        root = repo_util.find_repo_root()
        hits = abs_path_scan.scan_repo(root)
        fails = [h for h in hits if h["severity"] == "FAIL"]
        self.assertEqual(fails, [], f"production hardcode found: {fails}")

    def test_bootstrap_deploy_clean(self):
        root = repo_util.find_repo_root()
        hits = abs_path_scan.scan_files(root, ["scripts/bootstrap_deploy.py"])
        self.assertEqual(hits, [])

    def test_recovered_manifest_source_is_provenance(self):
        root = repo_util.find_repo_root()
        hits = abs_path_scan.scan_files(root, ["manifests/recovered_clean_manifest.json"])
        self.assertTrue(hits)
        self.assertTrue(all(h["classification"] == "provenance_metadata" for h in hits))
        for h in hits:
            self.assertIn("SteamLibrary", h["matched"])

    def test_json_report_shape(self):
        root = repo_util.find_repo_root()
        hits = abs_path_scan.scan_repo(root)
        report = json.dumps([h for h in hits[:1]], ensure_ascii=False)
        for key in ("file", "line", "matched", "classification", "severity", "remediation"):
            self.assertIn(f'"{key}"', report)


if __name__ == "__main__":
    unittest.main()