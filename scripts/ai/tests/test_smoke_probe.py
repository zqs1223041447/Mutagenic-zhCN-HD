#!/usr/bin/env python3
"""P2-A2 unittests: smoke hop probe with mocked engine/subprocess.

No real Godot binary is ever launched here; every hop is a direct engine
launch (`<godot> --headless --path <product> <scene>`) simulated by mock run
callables that either return a completed process or raise TimeoutExpired
(dwell window elapsed -> planned kill) / OSError (spawn failure).
"""
from __future__ import annotations

import io
import itertools
import json
import contextlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "bootstrap"))

import product_smoke_probe as psp  # noqa: E402


def path_is(expected):
    wanted = Path(expected)
    return lambda p: Path(p) == wanted


def fake_clock(step=0.05):
    return itertools.count(0.0, step).__next__


def proc(stdout="", stderr="", returncode=0):
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)


BANNER = "Godot Engine v4.7.1.stable.official\n"


def clean_stdout(scene):
    return BANNER + "Loading resource: %s\n" % scene + "current scene: %s\n" % scene


def clean_result(scene):
    return (clean_stdout(scene), "", 0)


def crash_result(scene, err='SCRIPT ERROR: Parse Error: unexpected identifier\n', rc=1):
    return (BANNER, err, rc)


def dwell_expired(scene):
    return subprocess.TimeoutExpired(
        cmd=["godot", "--headless", "--path", "product", scene],
        timeout=5,
        output=clean_stdout(scene),
        stderr=b"",
    )


def scripted_hops(outputs):
    """outputs: {scene_res_path: (stdout, stderr, returncode)} or {scene: Exception}."""
    def _run(cmd, timeout=None, *args, **kwargs):
        str_args = [str(a) for a in cmd]
        if "--version" in str_args:
            return proc(BANNER, "", 0)
        scene = next((a for a in str_args if a.startswith("res://")), "<missing>")
        expected = outputs.get(scene)
        if expected is None:
            raise AssertionError("unexpected hop scene: %r" % scene)
        if isinstance(expected, Exception):
            raise expected
        out, err, rc = expected
        return proc(out, err, rc)

    return _run


def discovered_environ(binary="/m/godot"):
    return {"GODOT_BIN": binary}


def gather(scenes=None, outputs=None, root=None, **kwargs):
    defaults = dict(
        environ=discovered_environ(),
        which=lambda name: None,
        is_file=path_is("/m/godot"),
        run=scripted_hops(outputs or {}),
        clock=fake_clock(),
    )
    defaults.update(kwargs)
    return psp.gather_report(
        root or Path(tempfile.gettempdir()),
        scenes=scenes,
        **defaults,
    )


class HopCommandTest(unittest.TestCase):
    def test_direct_launch_cmd_without_script_flag(self):
        captured = {}

        def run(cmd, timeout=None, *a, **k):
            captured["cmd"] = [str(c) for c in cmd]
            captured["timeout"] = timeout
            return proc(clean_stdout("res://scenes/Menu.tscn"), "", 0)

        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://scenes/Menu.tscn",
            timeout_per_hop_s=20,
            dwell_seconds=5.0,
            run=run,
            clock=fake_clock(),
        )
        self.assertEqual(
            captured["cmd"],
            ["/m/godot", "--headless", "--path", str(Path("/repo/product")),
             "res://scenes/Menu.tscn"],
        )
        self.assertNotIn("--script", captured["cmd"])
        self.assertEqual(out["status"], psp.HOP_REACHED)
        self.assertEqual(captured["timeout"], 5.0)

    def test_effective_timeout_is_clamped_dwell_vs_hard_cap(self):
        self.assertEqual(psp.effective_run_timeout_s(5.0, 20), 5.0)
        self.assertEqual(psp.effective_run_timeout_s(30.0, 20), 20.0)
        self.assertEqual(psp.effective_run_timeout_s(0.4, 20), 1.0)


class ReachRuleTest(unittest.TestCase):
    def test_dwell_survival_counts_as_arrived_needing_confirmation(self):
        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://x.tscn",
            dwell_seconds=3.0,
            run=lambda cmd, timeout=None, *a, **k: (_ for _ in ()).throw(dwell_expired("res://x.tscn")),
            clock=fake_clock(),
        )
        self.assertEqual(out["status"], psp.HOP_TIMEOUT)
        self.assertIs(out["reached"], True)
        self.assertTrue(out["timed_out"])
        self.assertIsNone(out["returncode"])
        self.assertIn("manual confirmation", out["detail"])
        self.assertEqual(out["loaded_scene"], "res://x.tscn")
        self.assertTrue(any("res://x.tscn" in ln for ln in out["scene_evidence"]))
        self.assertIsInstance(out["duration_ms"], int)

    def test_dwell_timeout_with_fatal_signature_denies_arrival(self):
        exc = subprocess.TimeoutExpired(
            cmd=["godot"], timeout=5,
            output="Godot Engine v4.7.1\n",
            stderr=b"SCRIPT ERROR: late boom\n",
        )

        def run(cmd, timeout=None, *a, **k):
            raise exc

        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://x.tscn",
            run=run,
            clock=fake_clock(),
        )
        self.assertEqual(out["status"], psp.HOP_NOT_REACHED)
        self.assertIs(out["reached"], False)
        self.assertTrue(out["timed_out"])

    def test_clean_early_exit_is_reached(self):
        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://y.tscn",
            run=lambda cmd, timeout=None, *a, **k: proc(clean_stdout("res://y.tscn"), "", 0),
            clock=fake_clock(),
        )
        self.assertEqual(out["status"], psp.HOP_REACHED)
        self.assertIs(out["reached"], True)
        self.assertFalse(out["timed_out"])
        self.assertEqual(out["returncode"], 0)

    def test_nonzero_exit_is_not_reached_with_rc_detail(self):
        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://x.tscn",
            run=lambda cmd, timeout=None, *a, **k: proc(BANNER, "", 3),
            clock=fake_clock(),
        )
        self.assertEqual(out["status"], psp.HOP_NOT_REACHED)
        self.assertIs(out["reached"], False)
        self.assertIn("rc=3", out["detail"])

    def test_zero_exit_with_script_errors_is_not_reached(self):
        err = 'SCRIPT ERROR: Invalid call. Nonexistent function \'connect\' in base \'Nil\'.\n'
        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://x.tscn",
            run=lambda cmd, timeout=None, *a, **k: proc("", err, 0),
            clock=fake_clock(),
        )
        self.assertEqual(out["status"], psp.HOP_NOT_REACHED)
        self.assertIs(out["reached"], False)
        self.assertEqual(len(out["script_error_lines"]), 1)

    def test_benign_missing_asset_script_errors_are_reached_presumed(self):
        err = (
            'SCRIPT ERROR: Parse Error: Preload file "res://sprites/x.aseprite" '
            'has no resource loaders (unrecognized file extension).\n'
        )
        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://x.tscn",
            run=lambda cmd, timeout=None, *a, **k: proc("", err, 0),
            clock=fake_clock(),
        )
        self.assertEqual(out["status"], psp.HOP_REACHED)

    def test_oserror_branch_is_spawn_failed(self):
        def run(cmd, timeout=None, *a, **k):
            raise OSError("exec format error")

        out = psp.run_hop(
            "/m/godot",
            Path("/repo/product"),
            "res://x.tscn",
            run=run,
            clock=fake_clock(),
        )
        self.assertEqual(out["status"], psp.HOP_SPAWN_FAILED)
        self.assertIsNone(out["reached"])
        self.assertFalse(out["timed_out"])
        self.assertIsNone(out["returncode"])


class ParseAndDiffTest(unittest.TestCase):
    def test_extract_script_error_lines_from_both_streams(self):
        lines = psp.extract_script_error_lines(
            "SCRIPT ERROR: from stdout\nplain line",
            "SCRIPT ERROR: from stderr",
        )
        self.assertEqual(len(lines), 2)
        self.assertTrue(all("SCRIPT ERROR" in ln for ln in lines))

    def test_normalize_error_line_collapses_whitespace(self):
        self.assertEqual(
            psp.normalize_error_line("  SCRIPT   ERROR:\tboom\n"),
            psp.normalize_error_line("SCRIPT ERROR: boom"),
        )

    def test_diff_new_error_lines_delta_semantics(self):
        seen: set[str] = set()
        first = psp.diff_new_error_lines(["SCRIPT ERROR: a", "SCRIPT ERROR: b"], seen)
        second = psp.diff_new_error_lines(
            ["SCRIPT ERROR: a", "SCRIPT ERROR: b", "SCRIPT ERROR: c"], seen
        )
        third = psp.diff_new_error_lines(["SCRIPT ERROR: a"], seen)
        self.assertEqual(len(first), 2)
        self.assertEqual([ln for ln in second], ["SCRIPT ERROR: c"])
        self.assertEqual(third, [])

    def test_has_fatal_signature_matches_crash_and_load_failures(self):
        self.assertTrue(psp.has_fatal_signature("", "SCRIPT ERROR: boom"))
        self.assertTrue(psp.has_fatal_signature("ERROR: Failed loading scene: res://a.tscn", ""))
        self.assertTrue(psp.has_fatal_signature("Fatal error. Cannot load font.", ""))
        self.assertTrue(psp.has_fatal_signature("", "handle_crash: Program crashed"))
        self.assertFalse(psp.has_fatal_signature(BANNER + "all good here\n", ""))

    def test_collect_scene_evidence_picks_scene_related_lines_both_streams(self):
        evidence = psp.collect_scene_evidence(
            BANNER + "Loading resource: res://a.tscn\nplain line",
            "current scene: res://a.tscn\nunrelated warning",
            "res://a.tscn",
        )
        self.assertEqual(evidence, [
            "Loading resource: res://a.tscn",
            "current scene: res://a.tscn",
        ])

    def test_collect_scene_evidence_caps_at_limit(self):
        noisy = "".join("Loading resource: res://e%d.tscn\n" % i for i in range(30))
        evidence = psp.collect_scene_evidence(noisy, "", "res://none.tscn")
        self.assertEqual(len(evidence), psp.MAX_EVIDENCE_LINES)


class GatherReportTest(unittest.TestCase):
    THREE_SCENES = list(psp.DEFAULT_SCENES)

    def full_outputs(self, reach=(True, True, True)):
        outs = {}
        for i, scene in enumerate(self.THREE_SCENES):
            outs[scene] = (
                dwell_expired(scene) if reach[i] else crash_result(scene)
            )
        return outs

    def test_not_found_short_circuits_and_never_runs_hops(self):
        def forbidden_run(cmd, timeout=None, *a, **k):
            raise AssertionError("engine must not be launched when NOT_FOUND")

        report = psp.gather_report(
            Path(tempfile.gettempdir()),
            environ={},
            which=lambda name: None,
            is_file=lambda p: False,
            run=forbidden_run,
        )
        self.assertEqual(report["overall"], "NOT_FOUND")
        self.assertEqual(report["task"], "P2-A2")
        self.assertEqual(report["hops"], [])
        self.assertTrue(report["engine"]["tool_missing"])
        self.assertNotEqual(report["overall"], "PASS")

    def test_empty_chain_is_tool_failed_with_note(self):
        report = gather(scenes=[], outputs=self.full_outputs())
        self.assertEqual(report["overall"], "TOOL_FAILED")
        self.assertEqual(report["hops"], [])
        self.assertIn("empty scene chain", report["note"])

    def test_full_pass_reports_smoke_pass(self):
        report = gather(scenes=self.THREE_SCENES, outputs=self.full_outputs())
        self.assertEqual(report["overall"], "SMOKE_PASS")
        self.assertEqual(report["total_hops"], 3)
        self.assertEqual(report["reached_count"], 3)
        self.assertEqual([h["scene"] for h in report["hops"]], self.THREE_SCENES)
        for hop in report["hops"]:
            for key in ("scene", "reached", "new_script_errors", "sample_lines",
                        "needs_manual_confirm", "scene_evidence"):
                self.assertIn(key, hop, key)
            self.assertIs(hop["reached"], True)
            self.assertEqual(hop["status"], "TIMEOUT")
            self.assertTrue(hop["needs_manual_confirm"])
            self.assertEqual(hop["loaded_scene"], hop["scene"])

    def test_all_timeouts_add_manual_confirm_note(self):
        report = gather(scenes=self.THREE_SCENES, outputs=self.full_outputs())
        self.assertIn("manual confirmation", report["note"])

    def test_partial_when_middle_hop_misses(self):
        report = gather(
            scenes=self.THREE_SCENES,
            outputs=self.full_outputs(reach=(True, False, True)),
        )
        self.assertEqual(report["overall"], "SMOKE_PARTIAL")
        self.assertEqual(report["reached_count"], 2)
        self.assertFalse(report["hops"][1]["reached"])
        self.assertEqual(report["hops"][1]["returncode"], 1)

    def test_fail_when_no_hop_reaches(self):
        report = gather(
            scenes=self.THREE_SCENES,
            outputs=self.full_outputs(reach=(False, False, False)),
        )
        self.assertEqual(report["overall"], "SMOKE_FAIL")
        self.assertEqual(report["reached_count"], 0)

    def test_spawn_failure_mid_chain_is_tool_failed_but_hops_continue(self):
        outputs = {
            self.THREE_SCENES[0]: dwell_expired(self.THREE_SCENES[0]),
            self.THREE_SCENES[1]: OSError("spawn failed"),
            self.THREE_SCENES[2]: dwell_expired(self.THREE_SCENES[2]),
        }
        report = gather(scenes=self.THREE_SCENES, outputs=outputs)
        self.assertEqual(report["overall"], "TOOL_FAILED")
        self.assertEqual(
            [h["status"] for h in report["hops"]],
            ["TIMEOUT", "SPAWN_FAILED", "TIMEOUT"],
        )
        self.assertEqual(report["reached_count"], 2)

    def test_cross_hop_script_error_dedup_in_report(self):
        errors = {
            0: 'SCRIPT ERROR: alpha\nSCRIPT ERROR: beta\n',
            1: 'SCRIPT ERROR: alpha\nSCRIPT ERROR: gamma\n',
            2: '',
        }
        outputs = {
            scene: crash_result(scene, err=errors[i])
            for i, scene in enumerate(self.THREE_SCENES)
        }
        report = gather(scenes=self.THREE_SCENES, outputs=outputs)
        totals = [h["script_errors_total"] for h in report["hops"]]
        news = [h["new_script_errors"] for h in report["hops"]]
        self.assertEqual(totals, [2, 2, 0])
        self.assertEqual(news, [2, 1, 0])
        self.assertEqual(
            report["hops"][1]["sample_lines"],
            ['SCRIPT ERROR: gamma'],
        )
        self.assertEqual(report["hops"][2]["sample_lines"], [])

    def test_max_sample_lines_caps_samples_only(self):
        many_errs = "".join('SCRIPT ERROR: e%d\n' % i for i in range(30))
        outputs = {self.THREE_SCENES[0]: crash_result(self.THREE_SCENES[0], err=many_errs)}
        for scene in self.THREE_SCENES[1:]:
            outputs[scene] = dwell_expired(scene)
        report = gather(
            scenes=self.THREE_SCENES,
            outputs=outputs,
            max_sample_lines=5,
        )
        self.assertEqual(len(report["hops"][0]["sample_lines"]), 5)
        self.assertEqual(report["hops"][0]["script_errors_total"], 30)
        self.assertEqual(report["config"]["max_sample_lines"], 5)

    def test_report_config_records_chain_and_timeouts(self):
        report = gather(
            scenes=["res://a.tscn,res://b.tscn"],
            outputs={
                "res://a.tscn": dwell_expired("res://a.tscn"),
                "res://b.tscn": dwell_expired("res://b.tscn"),
            },
            timeout_per_hop_s=33,
            dwell_seconds=2.5,
        )
        self.assertEqual(report["config"]["scenes"], ["res://a.tscn", "res://b.tscn"])
        self.assertEqual(report["config"]["timeout_per_hop_s"], 33)
        self.assertEqual(report["config"]["dwell_seconds"], 2.5)

    def test_report_sanitized_of_host_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            binary = root / "Godot.exe"
            report = gather(
                scenes=self.THREE_SCENES[:1],
                outputs={self.THREE_SCENES[0]: dwell_expired(self.THREE_SCENES[0])},
                root=root,
                environ=discovered_environ(str(binary)),
                is_file=path_is(binary),
            )
            payload = json.dumps(report, ensure_ascii=False)
            self.assertNotIn(str(root), payload)
            self.assertEqual(report["config"]["product_dir"], "<repo>/product")
            self.assertEqual(report["hops"][0]["cmd"][0], "<repo>/Godot.exe")
            self.assertEqual(report["hops"][0]["cmd"][-1], self.THREE_SCENES[0])

    def test_exit_codes(self):
        self.assertEqual(psp.exit_code_for({"overall": "SMOKE_PASS"}), 0)
        self.assertEqual(psp.exit_code_for({"overall": "NOT_FOUND"}), 0)
        self.assertEqual(psp.exit_code_for({"overall": "SMOKE_PARTIAL"}), 1)
        self.assertEqual(psp.exit_code_for({"overall": "SMOKE_FAIL"}), 1)
        self.assertEqual(psp.exit_code_for({"overall": "TOOL_FAILED"}), 1)


class CliTest(unittest.TestCase):
    def test_main_writes_out_file_not_found_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence" / "smoke.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = psp.main(
                    ["--root", str(root), "--out", str(out)],
                    environ={},
                    which=lambda name: None,
                    is_file=lambda p: False,
                )
            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["overall"], "NOT_FOUND")
            line = buf.getvalue().strip().splitlines()[-1]
            self.assertIn("smoke=NOT_FOUND", line)

    def test_main_smoke_pass_end_to_end_with_mocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "smoke.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = psp.main(
                    [
                        "--root", str(root),
                        "--out", str(out),
                        "--scenes", ",".join(psp.DEFAULT_SCENES),
                    ],
                    environ=discovered_environ(str(root / "Godot.exe")),
                    which=lambda name: None,
                    is_file=path_is(root / "Godot.exe"),
                    run=scripted_hops({
                        scene: dwell_expired(scene)
                        for scene in psp.DEFAULT_SCENES
                    }),
                    clock=fake_clock(),
                )
            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["overall"], "SMOKE_PASS")
            self.assertEqual(data["total_hops"], len(psp.DEFAULT_SCENES))
            self.assertIn("smoke=SMOKE_PASS", buf.getvalue())

    def test_main_respects_timeout_flag(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "smoke.json"
            code = psp.main(
                ["--root", str(root), "--out", str(out), "--timeout-per-hop", "7",
                 "--scenes", psp.DEFAULT_SCENES[0]],
                environ=discovered_environ(str(root / "Godot.exe")),
                which=lambda name: None,
                is_file=path_is(root / "Godot.exe"),
                run=scripted_hops({
                    psp.DEFAULT_SCENES[0]: dwell_expired(psp.DEFAULT_SCENES[0])
                }),
                clock=fake_clock(),
            )
            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["config"]["timeout_per_hop_s"], 7)

    def test_main_fail_exit_code_one(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = psp.main(
                    ["--root", str(root), "--scenes", psp.DEFAULT_SCENES[0]],
                    environ=discovered_environ(str(root / "Godot.exe")),
                    which=lambda name: None,
                    is_file=path_is(root / "Godot.exe"),
                    run=scripted_hops({
                        psp.DEFAULT_SCENES[0]:
                            (BANNER, 'SCRIPT ERROR: cannot continue\n', 3)
                    }),
                    clock=fake_clock(),
                )
            self.assertEqual(code, 1)
            self.assertIn("smoke=SMOKE_FAIL", buf.getvalue())


class SourceHygieneTest(unittest.TestCase):
    def test_source_has_no_host_drive_literals(self):
        src = (REPO / "scripts" / "bootstrap" / "product_smoke_probe.py").read_text(encoding="utf-8")
        self.assertNotIn("C:\\", src)
        self.assertNotIn("G:\\", src)
        self.assertNotIn("C:/Users", src)


if __name__ == "__main__":
    unittest.main()
