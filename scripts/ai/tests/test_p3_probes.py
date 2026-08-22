#!/usr/bin/env python3
"""Unit tests for the P3 C/D/E probes (offline, no engine).

Covers: the shared probe plumbing (result-line parsing, SCRIPT ERROR
extraction, contention retry policy, verdict classification, evidence schema),
the three wrapper CLIs' argument contract, and the p3_harness config wiring
for E4-E7 (implemented=true only for delivered CLIs; E1/E2/E3/E8 untouched).
No Godot binary is ever launched; subprocess calls are injected fakes.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "validate"))

import p3_probe_common as common  # noqa: E402


def proc(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)


class ParseResultLineTest(unittest.TestCase):
    def test_extracts_and_parses_marker_line(self):
        payload = {"probe_id": "x", "pass": True}
        out = "noise\nP3_PROBE_RESULT:" + json.dumps(payload) + "\nmore noise"
        self.assertEqual(common.extract_result_line(out), payload)

    def test_returns_none_when_absent_or_broken(self):
        self.assertIsNone(common.extract_result_line("nothing here"))
        self.assertIsNone(common.extract_result_line("P3_PROBE_RESULT:{broken"))


class ScriptErrorExtractionTest(unittest.TestCase):
    def test_collects_unique_errors_from_both_streams(self):
        out = "SCRIPT ERROR: alpha\nplain"
        err = "SCRIPT ERROR: beta\nSCRIPT ERROR: alpha\n"
        self.assertEqual(common.extract_script_errors(out, err),
                         ["SCRIPT ERROR: alpha", "SCRIPT ERROR: beta"])

    def test_empty_streams(self):
        self.assertEqual(common.extract_script_errors("", ""), [])


class RunDriverTest(TempCase):
    def test_success_attempt_fields(self):
        def run(cmd, capture_output=True, text=True, timeout=None):
            return proc(0, stdout="P3_PROBE_RESULT:{\"pass\": true}\n")
        attempt = common.run_driver(Path("engine"), Path("product"), "res://x.tscn", run=run)
        self.assertEqual(attempt["returncode"], 0)
        self.assertFalse(attempt["timed_out"])
        self.assertIsInstance(attempt["duration_ms"], int)
        self.assertIn("--headless", attempt["cmd"])

    def test_timeout_attempt_is_flagged(self):
        def run(cmd, capture_output=True, text=True, timeout=None):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout or 1,
                                            output=b"partial out", stderr=b"")
        attempt = common.run_driver(Path("engine"), Path("product"), "res://x.tscn", run=run)
        self.assertTrue(attempt["timed_out"])
        self.assertIsNone(attempt["returncode"])


class RetryPolicyTest(TempCase):
    def make_run(self, results):
        calls = {"n": 0}

        def run(cmd, **kwargs):
            index = min(calls["n"], len(results) - 1)
            calls["n"] += 1
            return results[index]
        return run, calls

    def test_clean_exit_runs_once(self):
        sleeps = []
        run, calls = self.make_run([proc(0)])
        final, attempts, flaked = common.execute_with_retry(
            Path("e"), Path("p"), "res://x.tscn", run=run,
            sleep=lambda s: sleeps.append(s))
        self.assertEqual(len(attempts), 1)
        self.assertFalse(flaked)
        self.assertEqual(sleeps, [])

    def test_contention_failure_retries_once_then_flake(self):
        sleeps = []
        bad = proc(1, stderr="Unable to write to cache")
        run, calls = self.make_run([bad, bad])
        final, attempts, flaked = common.execute_with_retry(
            Path("e"), Path("p"), "res://x.tscn", run=run,
            sleep=lambda s: sleeps.append(s))
        self.assertEqual(len(attempts), 2)
        self.assertTrue(flaked)
        self.assertEqual(sleeps, [common.CONTENTION_SLEEP_S])

    def test_plain_failure_does_not_retry(self):
        sleeps = []
        bad = proc(1, stderr="SCRIPT ERROR: logic broke")
        run, calls = self.make_run([bad])
        final, attempts, flaked = common.execute_with_retry(
            Path("e"), Path("p"), "res://x.tscn", run=run,
            sleep=lambda s: sleeps.append(s))
        self.assertEqual(len(attempts), 1)
        self.assertFalse(flaked)
        self.assertEqual(sleeps, [])


class ClassifyTest(unittest.TestCase):
    def test_pass_when_probe_reports_pass(self):
        verdict, _ = common.classify({"returncode": 0}, {"pass": True}, [])
        self.assertEqual(verdict, "PASS")

    def test_fail_with_error_detail(self):
        verdict, detail = common.classify(
            {"returncode": 2}, {"pass": False, "errors": ["boom"]}, [])
        self.assertEqual(verdict, "FAIL")
        self.assertIn("boom", detail)

    def test_blocked_when_no_result_line(self):
        verdict, _ = common.classify({"returncode": None}, None, [])
        self.assertEqual(verdict, "BLOCKED")


class EvidenceSchemaTest(TempCase):
    def test_evidence_carries_contract_fields(self):
        engine = {"binary": "/x/Godot.exe", "resolved_via": "REPO_RELATIVE",
                  "version": "4.7.1", "status": "SUCCESS"}
        final = {"cmd": ["godot"], "returncode": 0, "timed_out": False,
                 "duration_ms": 5, "stdout": "", "stderr": ""}
        evidence = common.build_evidence(
            "P3-C", "p3_combat_probe", ["E4", "E5"], "res://d.tscn",
            "proves-text", "not-proven-text", engine, final,
            [final], False, {"pass": True}, [])
        for key in ("schema_version", "task", "probe_id", "exit_criteria",
                    "generated_at", "driver_scene", "command", "attempts",
                    "flaked", "result", "script_errors", "verdict",
                    "verdict_detail", "proves", "not_proven"):
            self.assertIn(key, evidence)
        self.assertEqual(evidence["verdict"], "PASS")
        self.assertEqual(evidence["binary_name_in_engine"] if False else
                         evidence["engine"]["binary_name"], "Godot.exe")

    def test_write_evidence_creates_parents(self):
        target = self.tmp / "a" / "b" / "evidence.json"
        common.write_evidence({"k": 1}, target)
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"k": 1})


BANNER = "Godot Engine v4.7.1.stable.official\n"


def make_engine_aware_run(probe_stdout):
    def fake_run(cmd, *args, **kwargs):
        if "--version" in [str(a) for a in cmd]:
            return proc(0, stdout=BANNER)
        return proc(0, stdout=probe_stdout)
    return fake_run


class WrapperCliTest(TempCase):
    """The wrappers share probe_main; exercise one with injected fake runs."""

    def test_wrapper_cli_pass_path_writes_evidence(self):
        import p3_combat_probe as wrapper

        original = common.subprocess.run
        common.subprocess.run = make_engine_aware_run(
            'P3_PROBE_RESULT:{"probe_id": "p3_combat_probe", "pass": true}\n')
        try:
            out = self.tmp / "evidence.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = wrapper.main(["--out", str(out), "--root", str(REPO)])
        finally:
            common.subprocess.run = original
        self.assertEqual(code, common.EXIT_PASS)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["task"], "P3-C")
        self.assertEqual(data["exit_criteria"], ["E4", "E5"])
        self.assertEqual(data["verdict"], "PASS")

    def test_wrapper_cli_fail_exit_code_two(self):
        import p3_ui_probe as wrapper

        original = common.subprocess.run
        common.subprocess.run = make_engine_aware_run(
            'P3_PROBE_RESULT:{"pass": false, "errors": ["x"]}\n')
        try:
            out = self.tmp / "evidence.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = wrapper.main(["--out", str(out), "--root", str(REPO)])
        finally:
            common.subprocess.run = original
        self.assertEqual(code, common.EXIT_FAIL)


class HarnessConfigWiringTest(unittest.TestCase):
    """E4-E7 must point at the delivered probe CLIs; E1/E2/E3/E8 untouched."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads(
            (REPO / "tests" / "p3_harness" / "config.json").read_text(encoding="utf-8"))

    def test_wired_steps_are_true_and_reference_delivered_clis(self):
        expected = {
            "E4": "p3_combat_probe",
            "E5": "p3_combat_probe",
            "E6": "p3_loot_probe",
            "E7": "p3_ui_probe",
        }
        for sid, tool in expected.items():
            runner = self.cfg["steps"][sid]["runner"]
            self.assertTrue(runner["implemented"], sid)
            self.assertIn(tool, runner["command_template"], sid)
            self.assertIn("{step_evidence}", runner["command_template"], sid)

    def test_a_b_steps_wired_to_delivered_probes(self):
        # Attempt-2 integration wired E1/E8 -> character-save probe and
        # E2/E3 -> world-movement probe; nothing ships dormant anymore.
        expected = {
            "E1": "p3_a_probe",
            "E2": "p3_b_probe",
            "E3": "p3_b_probe",
            "E8": "p3_a_probe",
        }
        for sid, tool in expected.items():
            runner = self.cfg["steps"][sid]["runner"]
            self.assertTrue(runner["implemented"], sid)
            self.assertIn(tool, runner["command_template"], sid)
            self.assertIn("{step_evidence}", runner["command_template"], sid)

    def test_all_referenced_tools_exist_on_disk(self):
        for name, rel in self.cfg["tools"].items():
            self.assertTrue((REPO / rel).is_file(), f"{name}: {rel}")

    def test_evidence_files_exist_for_wired_steps(self):
        mapping = {
            "p3_c_combat.json": ("E4", "E5"),
            "p3_d_loot.json": ("E6",),
            "p3_e_ui.json": ("E7",),
        }
        for filename, criteria in mapping.items():
            path = REPO / "migration" / "conversion" / filename
            self.assertTrue(path.is_file(), filename)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["verdict"], "PASS", filename)
            self.assertEqual(tuple(data["exit_criteria"]), criteria, filename)


if __name__ == "__main__":
    unittest.main()
