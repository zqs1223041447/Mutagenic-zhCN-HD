#!/usr/bin/env python3
"""secret_scan: redaction, key-file content protection, env files, CLI gates."""
from __future__ import annotations

import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import repo_util  # noqa: E402
import secret_scan  # noqa: E402
from test_helpers import commit_all, make_repo, seed_repo, temp_area  # noqa: E402


class RedactionTest(unittest.TestCase):
    def _run(self, rel: str, text: str):
        return secret_scan.scan_text(rel, text)

    def test_key_value_redacted(self):
        raw_secret = "sk-abcdefghijklmnopqrstuvwxyz123456"
        findings = self._run("scripts/demo.py", f'api_key = "{raw_secret}"\n')
        kv = [f for f in findings if f["rule"] == "key_value"]
        self.assertTrue(kv, "api_key pair must be detected by key_value rule")
        self.assertIn("<redacted", kv[0]["key"])
        self.assertNotIn(raw_secret, kv[0]["key"])
        for f in findings:
            self.assertIn("<redacted", f["key"])

    def test_aws_github_slack_openai(self):
        text = ("aws = 'AKIAIOSFODNN7EXAMPLE'\n"
                "ghp = 'ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'\n"
                "slack = 'xoxb-123456789012-abcdefghij'\n"
                "sk = 'sk-abcdefghijklmnopqrstuvwxyz123456'\n")
        findings = self._run("scripts/demo.py", text)
        rules = {f["rule"] for f in findings}
        self.assertIn("aws_access_key", rules)
        self.assertIn("github_pat", rules)
        self.assertIn("slack_token", rules)
        self.assertIn("openai_sk", rules)
        for f in findings:
            self.assertNotIn(f["secret_length"] and f["key"].split("=")[-1], ["raw"])

    def test_private_key_block(self):
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----\n"
        findings = self._run("scripts/demo.py", text)
        self.assertTrue(any(f["rule"] == "private_key_block" for f in findings))
        self.assertNotIn("MIIEowIBAAKCAQEA", findings[0]["key"])

    def test_env_file(self):
        text = "DATABASE_PASSWORD=supersecret1234\nAPI_KEY=abc123def456ghi789\n"
        findings = self._run(".env", text)
        self.assertEqual(len(findings), 2)
        for f in findings:
            self.assertIn("<redacted", f["key"])
            self.assertNotIn("supersecret1234", f["key"])
            self.assertNotIn("abc123def456ghi789", f["key"])

    def test_plain_env_without_sensitive_name_ignored(self):
        findings = self._run(".env", "FOO=bar123456\n")
        self.assertEqual(findings, [])

    def test_cli_never_prints_raw(self):
        raw = "sk-abcdefghijklmnopqrstuvwxyz123456"
        with temp_area() as a:
            base = Path(a)
            repo = make_repo(base)
            seed_repo(repo)
            p = repo / "scripts" / "leak.py"
            p.write_text(f'api_key = "{raw}"\n', encoding="utf-8")
            commit_all(repo)
            old = os.getcwd()
            os.chdir(str(repo))
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = secret_scan.main([])
                out = buf.getvalue()
            finally:
                os.chdir(old)
        self.assertEqual(rc, 1)
        self.assertNotIn(raw, out)
        self.assertIn("<redacted", out)


class KeyFileTest(unittest.TestCase):
    def test_key_file_never_emits_content(self):
        hex_key = "A1B2C3D4E5F60718293A4B5C6D7E8F90" * 2
        with temp_area() as a:
            root = Path(a) / "sweep"
            (root / "manifests").mkdir(parents=True)
            (root / "manifests" / "script_key.txt").write_bytes((hex_key + "\n").encode("utf-8"))
            reports = secret_scan._scan_ignored_key_files(root)
        self.assertTrue(reports)
        entry = reports[0]
        self.assertEqual(entry["rule"], "key_file_presence")
        self.assertEqual(entry["secret_length"], len(hex_key) + 1)
        self.assertNotIn(hex_key, str(entry))
        self.assertTrue(entry["sha256"])

    def test_key_file_name_recognition(self):
        self.assertTrue(secret_scan.is_key_file("manifests/script_key.txt"))
        self.assertTrue(secret_scan.is_key_file("script_key.txt"))
        self.assertFalse(secret_scan.is_key_file("manifests/raw_manifest.json"))

    def test_scan_files_skips_key_file_and_fixtures(self):
        with temp_area() as a:
            root = Path(a)
            (root / "manifests").mkdir(parents=True)
            (root / "manifests" / "script_key.txt").write_text("A" * 64, encoding="utf-8")
            (root / "tests" / "fixtures").mkdir(parents=True)
            (root / "tests" / "fixtures" / "secret_dummy.py").write_text(
                'api_key = "sk-abcdefghijklmnopqrstuvwxyz123456"\n', encoding="utf-8")
            findings = secret_scan.scan_files(root, [
                "manifests/script_key.txt", "tests/fixtures/secret_dummy.py",
            ])
        self.assertEqual(findings, [])


class RealRepoScanTest(unittest.TestCase):
    def test_full_repo_no_secrets(self):
        root = repo_util.find_repo_root()
        findings = secret_scan.scan_repo(root)
        self.assertEqual(findings, [])

    def test_ignored_sweep_redacts_key_file(self):
        root = repo_util.find_repo_root()
        key_rel = "manifests/script_key.txt"
        if not (root / key_rel).is_file():
            self.skipTest("local key file absent - nothing to sweep")
        raw = (root / key_rel).read_text(encoding="utf-8", errors="replace").strip()
        reports = secret_scan._scan_ignored_key_files(root)
        self.assertTrue(reports)
        entry = [r for r in reports if r["file"] == key_rel]
        self.assertTrue(entry)
        self.assertNotIn(raw[:16], str(entry), "key content must never leak")
        buf = io.StringIO()
        with redirect_stdout(buf):
            secret_scan.main(["--scan-ignored"])
        self.assertNotIn(raw[:16], buf.getvalue())


if __name__ == "__main__":
    unittest.main()