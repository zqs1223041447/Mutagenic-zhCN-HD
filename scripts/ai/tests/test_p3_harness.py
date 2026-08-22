#!/usr/bin/env python3
"""Unit tests for the P3 E2E harness skeleton (offline, no Godot).

Covers: report schema validation, --steps selection logic, NOT_RUN default
behavior, the dormant runner-hook executor (via injected fake run callables)
and config/source hygiene.  Every run writes its report into a temp dir;
no engine binary is ever launched and nothing inside the repo is written.
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
HARNESS_DIR = REPO / "tests" / "p3_harness"
sys.path.insert(0, str(HARNESS_DIR))

import p3_e2e as p3  # noqa: E402


def run_main(args):
    buf_out, buf_err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = p3.main(args)
    return code, buf_out.getvalue(), buf_err.getvalue()


def fake_proc(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def out_path(self, name="p3_report.json"):
        return self.tmp / name


class ReportSchemaTest(TempCase):
    def test_default_run_all_steps_not_run_writes_schema_valid_report(self):
        out = self.tmp / "nested" / "deep" / "report.json"
        code, stdout, _ = run_main(["--out", str(out)])
        self.assertEqual(code, p3.EXIT_NOT_RUN)
        data = json.loads(out.read_text(encoding="utf-8"))
        for key in ("harness_id", "schema_version", "ran_at", "steps",
                    "summary", "result", "proves", "not_proven"):
            self.assertIn(key, data)
        self.assertEqual(data["harness_id"], p3.HARNESS_ID)
        self.assertEqual(data["schema_version"], p3.SCHEMA_VERSION)
        self.assertEqual([s["step_id"] for s in data["steps"]], p3.STEP_ORDER)
        for step in data["steps"]:
            self.assertEqual(set(step.keys()), set(p3.RESULT_KEYS))
            self.assertIn(step["status"],
                          (p3.STATUS_PASS, p3.STATUS_FAIL,
                           p3.STATUS_NOT_RUN, p3.STATUS_SKIP))
            self.assertIsInstance(step["detail"], str)
            self.assertTrue(step["detail"])
        summary = data["summary"]
        self.assertEqual(summary, {"total": 8, "pass": 0, "fail": 0,
                                   "not_run": 8, "skip": 0})
        self.assertEqual(data["result"], "NOT_RUN")
        self.assertTrue(data["proves"])
        self.assertTrue(data["not_proven"])

    def test_json_only_prints_report_to_stdout(self):
        out = self.out_path()
        code, stdout, _ = run_main(["--out", str(out), "--json-only"])
        self.assertEqual(code, p3.EXIT_NOT_RUN)
        parsed = json.loads(stdout)
        self.assertEqual(parsed["harness_id"], p3.HARNESS_ID)
        self.assertEqual(len(parsed["steps"]), 8)
        # file content matches what was printed
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), parsed)

    def test_human_mode_does_not_dump_json(self):
        out = self.out_path()
        code, stdout, _ = run_main(["--out", str(out)])
        self.assertEqual(code, p3.EXIT_NOT_RUN)
        self.assertFalse(stdout.lstrip().startswith("{"))
        self.assertIn("NOT_RUN", stdout)
        self.assertIn(str(out), stdout)


class StepSelectionTest(TempCase):
    def test_none_selects_every_step_in_order(self):
        self.assertEqual(p3.parse_step_selection(None), p3.STEP_ORDER)

    def test_subset_preserves_order_and_dedupes(self):
        self.assertEqual(p3.parse_step_selection("E3,E1,E3"), ["E3", "E1"])

    def test_whitespace_and_case_tolerated(self):
        self.assertEqual(p3.parse_step_selection(" e2 ,E7 "),
                         ["E2", "E7"])

    def test_unknown_step_raises_usage_error(self):
        with self.assertRaises(p3.UsageError):
            p3.parse_step_selection("E9")

    def test_empty_selection_raises_usage_error(self):
        with self.assertRaises(p3.UsageError):
            p3.parse_step_selection(" , ")

    def test_cli_unknown_step_exits_usage_without_writing_report(self):
        out = self.out_path()
        code, _, err = run_main(["--steps", "E42", "--out", str(out)])
        self.assertEqual(code, p3.EXIT_USAGE)
        self.assertIn("E42", err)
        self.assertFalse(out.exists())

    def test_selected_steps_run_others_marked_skip(self):
        out = self.out_path()
        code, _, _ = run_main(["--steps", "E1,E3", "--out", str(out)])
        self.assertEqual(code, p3.EXIT_NOT_RUN)
        data = json.loads(out.read_text(encoding="utf-8"))
        by_id = {s["step_id"]: s for s in data["steps"]}
        self.assertEqual(data["selected_steps"], ["E1", "E3"])
        self.assertEqual(by_id["E1"]["status"], "NOT_RUN")
        self.assertEqual(by_id["E3"]["status"], "NOT_RUN")
        for sid in ("E2", "E4", "E5", "E6", "E7", "E8"):
            self.assertEqual(by_id[sid]["status"], "SKIP", sid)
            self.assertIn("--steps", by_id[sid]["detail"])
        self.assertEqual(data["summary"],
                         {"total": 8, "pass": 0, "fail": 0,
                          "not_run": 2, "skip": 6})
        self.assertEqual(data["result"], "NOT_RUN")


class NotRunDefaultTest(TempCase):
    def make_ctx(self, run=None):
        cfg = p3.load_config(HARNESS_DIR / "config.json")
        return p3.HarnessContext(config=cfg, repo_root=REPO,
                                 report_path=self.out_path(), run=run)

    def test_every_check_defaults_to_not_run_without_spawning(self):
        def forbidden_run(*a, **k):
            raise AssertionError("dormant runner must never spawn a process")

        ctx = self.make_ctx(run=forbidden_run)
        for sid in p3.STEP_ORDER:
            result = p3.CHECKS[sid](ctx)
            self.assertEqual(set(result.keys()), set(p3.RESULT_KEYS), sid)
            self.assertEqual(result["status"], "NOT_RUN", sid)
            self.assertIn("implemented=false", result["detail"], sid)
            self.assertIsNone(result["evidence_path"], sid)

    def test_default_report_path_resolution(self):
        self.assertEqual(p3.resolve_out_path(None, {}, REPO),
                         REPO / "runtime" / "p3_harness_report.json")
        custom = self.tmp / "x.json"
        self.assertEqual(p3.resolve_out_path(custom, {}, REPO), custom.resolve())


class RunnerHookTest(TempCase):
    """The generic executor is exercised with injected fakes - no Godot."""

    def make_values(self):
        return {"python": sys.executable, "repo_root": str(self.tmp),
                "step_evidence": str(self.tmp / "e1_evidence.json")}

    def test_render_command_substitutes_placeholders(self):
        rendered = p3.render_command("{python} {repo_root}", self.make_values())
        self.assertEqual(rendered, f"{sys.executable} {self.tmp}")

    def test_render_command_rejects_unknown_placeholder(self):
        with self.assertRaises(p3.UsageError):
            p3.render_command("{does_not_exist}", {})

    def test_rc_zero_classified_pass(self):
        seen = {}
        def run(argv, **kwargs):
            seen["argv"] = argv
            return fake_proc(0, stdout="ok\n")
        runner = {"implemented": True, "timeout_s": 5,
                  "command_template": "{python} --version"}
        result = p3.execute_runner("E1", runner, self.make_values(), run=run)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("rc=0", result["detail"])
        self.assertTrue(seen["argv"])

    def test_rc_nonzero_classified_fail_with_tail(self):
        runner = {"implemented": True, "command_template": "{python} x"}
        result = p3.execute_runner(
            "E5", runner, self.make_values(),
            run=lambda *a, **k: fake_proc(3, stderr="boom\n"))
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("rc=3", result["detail"])
        self.assertIn("boom", result["detail"])

    def test_timeout_and_spawn_failure_classified_fail(self):
        runner = {"implemented": True, "command_template": "{python} x",
                  "timeout_s": 1}
        def timeout_run(*a, **k):
            raise subprocess.TimeoutExpired(cmd=["x"], timeout=1)
        result = p3.execute_runner("E2", runner, self.make_values(), run=timeout_run)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("timed out", result["detail"])

        def oserror_run(*a, **k):
            raise OSError("no exec")
        result = p3.execute_runner("E2", runner, self.make_values(), run=oserror_run)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("spawn failed", result["detail"])

    def test_implemented_without_template_is_fail_not_crash(self):
        runner = {"implemented": True}
        result = p3.execute_runner("E6", runner, self.make_values(),
                                   run=lambda *a, **k: fake_proc(0))
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("command_template", result["detail"])

    def test_template_error_is_fail_not_crash(self):
        runner = {"implemented": True, "command_template": "{missing_key}"}
        result = p3.execute_runner("E7", runner, {"python": "x"},
                                   run=lambda *a, **k: fake_proc(0))
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("template error", result["detail"])

    def test_step_context_exposes_scenes_tools_and_step_evidence(self):
        cfg = p3.load_config(HARNESS_DIR / "config.json")
        ctx = p3.HarnessContext(config=cfg, repo_root=REPO,
                                report_path=self.out_path())
        values = p3.step_context(ctx, "E2")
        self.assertEqual(values["test_level_scene"],
                         "res://scenes/Levels/TestLevel/TestLevel.tscn")
        self.assertEqual(values["load_game_scene"], "res://scenes/LoadGame.tscn")
        self.assertTrue(values["boot_probe"].endswith("product_boot_probe.py"))
        self.assertTrue(values["combat_harness"].endswith("combat_harness.py"))
        self.assertTrue(values["step_evidence"].endswith("e2_evidence.json"))


class ConfigContractTest(TempCase):
    def setUp(self):
        super().setUp()
        self.cfg = p3.load_config(HARNESS_DIR / "config.json")

    def test_config_loads_with_all_steps(self):
        self.assertEqual(sorted(self.cfg["steps"]), sorted(p3.STEP_ORDER))

    def test_every_runner_ships_dormant(self):
        for sid, step in self.cfg["steps"].items():
            runner = step.get("runner") or {}
            self.assertFalse(runner.get("implemented", False),
                             f"{sid} must ship implemented=false")
            self.assertTrue(step.get("title"), sid)
            self.assertTrue(step.get("exit_criteria"), sid)

    def test_scene_paths_are_res_paths_matching_product_tree(self):
        scenes = self.cfg["scene_paths"]
        for key in ("load_game", "menu", "test_level"):
            self.assertTrue(scenes[key].startswith("res://"), key)
        rel = scenes["test_level"].removeprefix("res://").replace("/", "\\")
        self.assertTrue((REPO / "product" / rel).is_file(),
                        scenes["test_level"])

    def test_referenced_tools_exist_in_repo(self):
        for name, rel in self.cfg["tools"].items():
            self.assertTrue((REPO / rel).is_file(), f"{name}: {rel}")

    def test_default_report_path_constant(self):
        self.assertEqual(self.cfg["default_report_path"],
                         "runtime/p3_harness_report.json")

    def test_malformed_configs_rejected(self):
        bad = self.tmp / "bad.json"
        bad.write_text("{ not json", encoding="utf-8")
        with self.assertRaises(p3.ConfigError):
            p3.load_config(bad)
        bad.write_text('{"steps": {}}', encoding="utf-8")
        with self.assertRaises(p3.ConfigError):
            p3.load_config(bad)


class HygieneTest(unittest.TestCase):
    FILES = [HARNESS_DIR / "p3_e2e.py", HARNESS_DIR / "config.json"]

    def test_sources_have_no_host_drive_literals(self):
        for path in self.FILES:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("C:\\", text, path.name)
            self.assertNotIn("G:\\", text, path.name)
            self.assertNotIn("C:/Users", text, path.name)

    def test_no_godot_binary_invocation_in_skeleton_source(self):
        src = (HARNESS_DIR / "p3_e2e.py").read_text(encoding="utf-8")
        self.assertNotIn("godot4", src.lower().replace("_", ""))
        self.assertNotIn("--headless", src)


if __name__ == "__main__":
    unittest.main()
