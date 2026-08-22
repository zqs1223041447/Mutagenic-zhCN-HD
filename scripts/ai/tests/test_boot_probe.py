#!/usr/bin/env python3
"""P1-V0 unittests: boot probe classification with mocked engine/subprocess.

No real Godot binary is ever launched here.
"""
from __future__ import annotations

import io
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

import product_boot_probe as pbp  # noqa: E402


def fake_run(stdout="", stderr="", returncode=0):
    return lambda cmd, timeout=None: SimpleNamespace(
        stdout=stdout, stderr=stderr, returncode=returncode
    )


def run_raises(exc):
    def _run(cmd, timeout=None):
        raise exc

    return _run


def path_is(expected):
    """Windows-safe path matcher: compare as Path, never as raw posix string."""
    wanted = Path(expected)
    return lambda p: Path(p) == wanted


def version_then_boot(boot_stdout="", boot_stderr="", boot_returncode=0):
    def _run(cmd, timeout=None):
        args = [str(a) for a in cmd]
        if "--version" in args:
            return SimpleNamespace(stdout="Godot Engine v4.7.1.stable.official\n", stderr="", returncode=0)
        if "--headless" in args:
            return SimpleNamespace(stdout=boot_stdout, stderr=boot_stderr, returncode=boot_returncode)
        raise AssertionError(f"unexpected command: {args}")

    return _run


class BootClassificationTest(unittest.TestCase):
    def test_booted_clean(self):
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            quit_after=600,
            timeout_s=120,
            run=fake_run("Godot Engine v4.7.1\n", "", 0),
            clock=iter([0.0, 0.25]).__next__,
        )
        self.assertEqual(out["status"], "BOOTED")
        self.assertEqual(out["returncode"], 0)
        self.assertEqual(out["script_error_count"], 0)
        self.assertEqual(out["error_lines"], [])
        self.assertFalse(out["timed_out"])
        self.assertIsInstance(out["duration_ms"], int)
        self.assertGreaterEqual(out["duration_ms"], 0)

    def test_booted_with_script_errors(self):
        err = "SCRIPT ERROR: Parse Error: bad token\nAt: res://main.gd:3\nSCRIPT ERROR: second\n"
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            run=fake_run("", err, 0),
            clock=iter([0.0, 0.5]).__next__,
        )
        self.assertEqual(out["status"], "BOOTED_WITH_ERRORS")
        self.assertEqual(out["returncode"], 0)
        self.assertEqual(out["script_error_count"], 2)
        self.assertTrue(any("Parse Error" in ln for ln in out["error_lines"]))

    def test_error_lines_default_cap_is_500(self):
        stdout = "".join(f"SCRIPT ERROR: boom {i}\n" for i in range(600))
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            run=fake_run(stdout, "", 0),
            clock=iter([0.0, 0.1]).__next__,
        )
        self.assertEqual(out["status"], "BOOTED_WITH_ERRORS")
        self.assertEqual(out["script_error_count"], 600)
        self.assertEqual(len(out["error_lines"]), pbp.MAX_ERROR_LINES)
        self.assertTrue(out["error_lines_truncated"])

    def test_max_error_lines_param_controls_cap(self):
        stdout = "".join(f"SCRIPT ERROR: boom {i}\n" for i in range(60))
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            max_error_lines=50,
            run=fake_run(stdout, "", 0),
            clock=iter([0.0, 0.1]).__next__,
        )
        self.assertEqual(out["script_error_count"], 60)
        self.assertEqual(len(out["error_lines"]), 50)
        self.assertTrue(out["error_lines_truncated"])

    def test_max_error_lines_zero_keeps_nothing(self):
        stdout = "SCRIPT ERROR: boom\n"
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            max_error_lines=0,
            run=fake_run(stdout, "", 0),
            clock=iter([0.0, 0.1]).__next__,
        )
        self.assertEqual(out["error_lines"], [])
        self.assertTrue(out["error_lines_truncated"])
        self.assertEqual(sum(out["script_errors_by_class"].values()), 1)

    def test_script_errors_by_class_counts(self):
        err = "\n".join([
            'ERROR: Failed loading resource: res://scenes/missing.tscn',
            "ERROR: Cannot open file 'res://assets/x.png'.",
            "ERROR: File not found: res://fonts/y.ttf",
            "SCRIPT ERROR: Could not resolve class \"FooBar\"",
            "SCRIPT ERROR: Failed to load script \"res://res/bad.gd\" with error -2.",
            "SCRIPT ERROR: Cannot find member \"hp\" in base \"Node\".",
            "SCRIPT ERROR: Identifier \"y\" not declared in the current scope.",
            "SCRIPT ERROR: Parse Error: bad token",
        ])
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            run=fake_run("", err, 0),
            clock=iter([0.0, 0.5]).__next__,
        )
        classes = out["script_errors_by_class"]
        self.assertEqual(classes["missing_asset"], 3)
        self.assertEqual(classes["class_resolve"], 1)
        self.assertEqual(classes["load_fail"], 1)
        self.assertEqual(classes["api_member"], 2)
        self.assertEqual(classes["other"], 1)
        self.assertEqual(set(classes), set(pbp.ERROR_CLASSES) | {"other"})
        self.assertEqual(sum(classes.values()), len(out["error_lines"]))

    def test_script_errors_by_class_counts_all_lines_not_only_kept_ones(self):
        stdout = "".join("SCRIPT ERROR: Parse Error: bad token\n" for _ in range(600))
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            max_error_lines=10,
            run=fake_run(stdout, "", 0),
            clock=iter([0.0, 0.1]).__next__,
        )
        self.assertEqual(out["script_errors_by_class"]["other"], 600)

    def test_clean_boot_has_zeroed_class_map(self):
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            run=fake_run("", "", 0),
            clock=iter([0.0, 0.25]).__next__,
        )
        self.assertEqual(
            out["script_errors_by_class"], pbp.empty_error_class_counts()
        )

    def test_crashed_nonzero_returncode(self):
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            run=fake_run("", "ERROR: segfault-ish\n", 1),
            clock=iter([0.0, 0.2]).__next__,
        )
        self.assertEqual(out["status"], "CRASHED")
        self.assertEqual(out["returncode"], 1)
        self.assertEqual(out["script_error_count"], 0)

    def test_crashed_even_without_error_text(self):
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            run=fake_run("", "", -1073741819),
            clock=iter([0.0, 0.2]).__next__,
        )
        self.assertEqual(out["status"], "CRASHED")

    def test_timeout_is_tool_failed_with_timeout_detail(self):
        exc = subprocess.TimeoutExpired(cmd=["godot", "--headless"], timeout=120, output="partial", stderr=b"bytes-err")
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            timeout_s=120,
            run=run_raises(exc),
            clock=iter([0.0, 120.0]).__next__,
        )
        self.assertEqual(out["status"], "TOOL_FAILED")
        self.assertTrue(out["timed_out"])
        self.assertIn("TIMEOUT", out["detail"])
        self.assertIsNone(out["returncode"])
        self.assertIn("partial", out["stdout"])
        self.assertEqual(out["stderr"], "bytes-err")

    def test_oserror_is_tool_failed_not_timeout(self):
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            run=run_raises(OSError("exec format error")),
            clock=iter([0.0, 0.01]).__next__,
        )
        self.assertEqual(out["status"], "TOOL_FAILED")
        self.assertFalse(out["timed_out"])
        self.assertIsNone(out["returncode"])

    def test_cmd_records_headless_quit_after(self):
        out = pbp.run_boot_probe(
            "/tools/godot471",
            Path("/repo/product"),
            quit_after=7,
            run=fake_run("", "", 0),
            clock=iter([0.0, 0.1]).__next__,
        )
        self.assertEqual(out["cmd"][1:], ["--headless", "--path", str(Path("/repo/product")), "--quit-after", "7"])


class DiscoveryAndReportTest(unittest.TestCase):
    def test_not_found_short_circuits_and_never_boots(self):
        def forbidden_run(cmd, timeout=None):
            raise AssertionError("engine must not be launched when NOT_FOUND")

        report = pbp.gather_report(
            Path(tempfile.gettempdir()),
            environ={},
            which=lambda name: None,
            is_file=lambda p: False,
            run=forbidden_run,
        )
        self.assertEqual(report["overall"], "NOT_FOUND")
        self.assertEqual(report["boot"]["status"], "NOT_FOUND")
        self.assertTrue(report["engine"]["tool_missing"])
        self.assertEqual(report["boot"]["cmd"], [])
        self.assertNotEqual(report["overall"], "PASS")
        self.assertEqual(
            report["boot"]["script_errors_by_class"], pbp.empty_error_class_counts()
        )

    def test_delegation_via_product_toolchain_env_binary(self):
        report = pbp.gather_report(
            Path("."),
            environ={"GODOT_BIN": "/x/godot"},
            which=lambda name: None,
            is_file=path_is("/x/godot"),
            run=version_then_boot(),
            clock=iter([0.0, 0.3]).__next__,
        )
        self.assertEqual(report["overall"], "BOOTED")
        self.assertEqual(report["engine"]["resolved_via"], "ENV:GODOT_BIN")
        self.assertEqual(report["engine"]["version"], "4.7.1")

    def test_fallback_used_when_toolchain_import_unavailable(self):
        saved = pbp._toolchain_discover
        pbp._toolchain_discover = None
        try:
            report = pbp.gather_report(
                Path("."),
                environ={"GODOT4": "/e/godot4"},
                which=lambda name: None,
                is_file=path_is("/e/godot4"),
                run=fake_run("", "", 0),
            )
        finally:
            pbp._toolchain_discover = saved
        self.assertEqual(report["overall"], "BOOTED")
        self.assertEqual(report["engine"]["resolved_via"], "ENV:GODOT4")
        self.assertIn("fallback", json.dumps(report))

    def test_fallback_order_path_before_env_before_repo(self):
        saved = pbp._toolchain_discover
        pbp._toolchain_discover = None
        try:
            root = Path("/root")
            repo_hit = root / "02_tools/godot/godot.exe"
            known = {Path("/p/godot"), Path("/e/godot"), repo_hit}
            report = pbp.gather_report(
                root,
                environ={"GODOT_BIN": "/e/godot"},
                which=lambda name: "/p/godot" if name in ("godot", "godot4") else None,
                is_file=lambda p: Path(p) in known,
                run=fake_run("", "", 0),
            )
            self.assertEqual(report["engine"]["resolved_via"].split(":")[0], "PATH")

            report = pbp.gather_report(
                root,
                environ={"GODOT_BIN": "/e/godot"},
                which=lambda name: None,
                is_file=lambda p: Path(p) in known,
                run=fake_run("", "", 0),
            )
            self.assertEqual(report["engine"]["resolved_via"].split(":")[0], "ENV")

            report = pbp.gather_report(
                root,
                environ={},
                which=lambda name: None,
                is_file=path_is(repo_hit),
                run=fake_run("", "", 0),
            )
            self.assertEqual(report["engine"]["resolved_via"], "REPO_RELATIVE")
        finally:
            pbp._toolchain_discover = saved

    def test_json_structure_and_exit_codes(self):
        report = pbp.gather_report(
            Path("."),
            environ={"MUTAGENIC_GODOT_4": "/m/godot"},
            which=lambda name: None,
            is_file=path_is("/m/godot"),
            run=version_then_boot("hi\n", "SCRIPT ERROR: x\n", 0),
            clock=iter([0.0, 0.4]).__next__,
        )
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["task"], "P1-V0")
        self.assertTrue(report["generated_at"].endswith("Z"))
        self.assertEqual(report["overall"], report["boot"]["status"])
        for key in (
            "status", "detail", "returncode", "timed_out", "script_error_count",
            "script_errors_by_class", "error_lines", "error_lines_truncated",
            "duration_ms", "quit_after", "timeout_s", "max_error_lines",
            "cmd", "stdout_head", "stderr_head",
        ):
            self.assertIn(key, report["boot"], key)
        self.assertEqual(report["boot"]["quit_after"], pbp.DEFAULT_QUIT_AFTER)
        self.assertEqual(report["boot"]["timeout_s"], pbp.DEFAULT_TIMEOUT_S)
        self.assertEqual(report["boot"]["max_error_lines"], pbp.MAX_ERROR_LINES)
        payload = json.dumps(report, ensure_ascii=False)
        self.assertIsInstance(json.loads(payload), dict)
        self.assertEqual(pbp.exit_code_for(report), 1)
        clean = pbp.gather_report(
            Path("."),
            environ={"MUTAGENIC_GODOT_4": "/m/godot"},
            which=lambda name: None,
            is_file=path_is("/m/godot"),
            run=version_then_boot(),
        )
        self.assertEqual(pbp.exit_code_for(clean), 0)

    def test_cmd_sanitized_of_host_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with tempfile.TemporaryDirectory() as host_td:
                product = root / "product"
                foreign_engine = Path(host_td) / "Godot.exe"
                self.assertTrue(foreign_engine.is_absolute())
                cmd = [
                    str(foreign_engine),
                    "--headless",
                    "--path",
                    str(product),
                    "--quit-after",
                    "600",
                ]
                sanitized = pbp.sanitize_cmd(cmd, root)
                self.assertEqual(sanitized[0], "Godot.exe")
                self.assertEqual(sanitized[1:3], ["--headless", "--path"])
                self.assertEqual(sanitized[3], "<repo>/product")
                self.assertEqual(sanitized[4:], ["--quit-after", "600"])
                self.assertTrue(all(str(root) not in a for a in sanitized))
                self.assertTrue(all(str(host_td) not in a for a in sanitized))

            report = pbp.gather_report(
                root,
                product_dir=root / "product",
                environ={},
                which=lambda name: None,
                is_file=lambda p: True,
                run=fake_run("", "", 0),
            )
            joined = json.dumps(report)
            self.assertNotIn(str(root), joined)


class CliTest(unittest.TestCase):
    def test_main_writes_out_file_and_summary(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "evidence" / "boot.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = pbp.main(
                    ["--root", str(root), "--out", str(out)],
                    environ={},
                    which=lambda name: None,
                    is_file=lambda p: False,
                )
            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["overall"], "NOT_FOUND")
            line = buf.getvalue().strip().splitlines()[-1]
            self.assertIn("boot=NOT_FOUND", line)

    def test_main_booted_end_to_end_with_mocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            binary = root / "Godot.exe"
            out = root / "boot.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = pbp.main(
                    ["--root", str(root), "--out", str(out)],
                    environ={"MUTAGENIC_GODOT_4": str(binary)},
                    which=lambda name: None,
                    is_file=lambda p: Path(p) == binary,
                    run=version_then_boot(),
                    clock=iter([0.0, 0.3]).__next__,
                )
            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["boot"]["status"], "BOOTED")
            self.assertEqual(data["boot"]["cmd"][0], "<repo>/Godot.exe")
            self.assertIn("boot=BOOTED", buf.getvalue())

    def test_main_accepts_max_error_lines_flag(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            binary = root / "Godot.exe"
            out = root / "boot.json"
            code = pbp.main(
                ["--root", str(root), "--out", str(out), "--max-error-lines", "7"],
                environ={"MUTAGENIC_GODOT_4": str(binary)},
                which=lambda name: None,
                is_file=lambda p: Path(p) == binary,
                run=version_then_boot(),
                clock=iter([0.0, 0.3]).__next__,
            )
            self.assertEqual(code, 0)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["boot"]["max_error_lines"], 7)
            self.assertIn("script_errors_by_class", data["boot"])

    def test_main_crashed_exit_code_one(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            binary = root / "Godot.exe"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = pbp.main(
                    ["--root", str(root)],
                    environ={"MUTAGENIC_GODOT_4": str(binary)},
                    which=lambda name: None,
                    is_file=lambda p: Path(p) == binary,
                    run=version_then_boot(boot_stderr="SCRIPT ERROR: fatal\n", boot_returncode=3),
                    clock=iter([0.0, 0.3]).__next__,
                )
            self.assertEqual(code, 1)
            self.assertIn("boot=CRASHED", buf.getvalue())


class SourceHygieneTest(unittest.TestCase):
    def test_source_has_no_host_drive_literals(self):
        src = (REPO / "scripts" / "bootstrap" / "product_boot_probe.py").read_text(encoding="utf-8")
        self.assertNotIn("C:\\", src)
        self.assertNotIn("G:\\", src)
        self.assertNotIn("C:/Users", src)


if __name__ == "__main__":
    unittest.main()
