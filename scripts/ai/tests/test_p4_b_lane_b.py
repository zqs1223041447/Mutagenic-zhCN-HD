#!/usr/bin/env python3
"""Unit tests for P4-BATCH-1 lane B (offline, no engine).

Covers: the three wrapper CLIs' argument/evidence contracts (engine runs are
injected fakes), the on-disk contracts of the restored Pickups scenes, the
F1 VFX pieces (HitBurst / DissolveMob / FloatingDamage / Mob wiring /
PlagueCloudsProjectile guard) and the recorded evidence artifacts.
No Godot binary is ever launched; subprocess calls are injected fakes.
"""
from __future__ import annotations

import contextlib
import io
import json
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


FAKE_ENGINE = {
    "binary": "C:/fake/Godot_v4.7.1-stable_win64.exe",
    "resolved_via": "REPO_RELATIVE",
    "version": "4.7.1",
    "status": "SUCCESS",
}


def marker_line(payload: dict) -> str:
    return "P3_PROBE_RESULT:" + json.dumps(payload)


class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)


class ProbeWrapperCliTest(TempCase):
    """p4_b_vfx_probe / p4_b_loot_real_probe share probe_main plumbing."""

    def _run_wrapper(self, module, payload, expect_code):
        original = common.subprocess.run
        original_discover = common.discover_product_godot
        common.subprocess.run = lambda cmd, **kw: proc(
            0, stdout=marker_line(payload))
        common.discover_product_godot = lambda root: {"engine": dict(FAKE_ENGINE)}
        try:
            out = self.tmp / "evidence.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = module.main(["--out", str(out)])
        finally:
            common.subprocess.run = original
            common.discover_product_godot = original_discover
        self.assertEqual(code, expect_code)
        return json.loads(out.read_text(encoding="utf-8"))

    def test_vfx_wrapper_pass_writes_evidence(self):
        import p4_b_vfx_probe as wrapper
        data = self._run_wrapper(wrapper, {
            "probe_id": "p4_b_vfx_probe", "pass": True}, common.EXIT_PASS)
        self.assertEqual(data["task"], "P4-B")
        self.assertEqual(data["exit_criteria"], ["F1"])
        self.assertEqual(data["verdict"], "PASS")
        self.assertIn("scenes/Mobs/_validate/p4_b_vfx_probe.tscn",
                      data["driver_scene"])

    def test_loot_wrapper_fail_exit_two(self):
        import p4_b_loot_real_probe as wrapper
        data = self._run_wrapper(wrapper, {
            "probe_id": "p4_b_loot_real_probe", "pass": False,
            "errors": ["boom"]}, common.EXIT_FAIL)
        self.assertEqual(data["verdict"], "FAIL")
        self.assertIn("E6", data["exit_criteria"])
        self.assertIn("C1", data["exit_criteria"])

    def test_wrapper_sanitizes_host_paths(self):
        import p4_b_vfx_probe as wrapper
        payload = {"probe_id": "p4_b_vfx_probe", "pass": True,
                   "note": str(REPO / "product")}
        data = self._run_wrapper(wrapper, payload, common.EXIT_PASS)
        self.assertNotIn(str(REPO), json.dumps(data))
        self.assertIn("<repo>", data["result"]["note"])


class PerfWrapperCliTest(TempCase):
    def _patch(self, module, payloads):
        original_run = module.subprocess.run
        original_discover = module.discover_product_godot
        responses = list(payloads)

        def fake_run(cmd, **kwargs):
            if not isinstance(cmd, list):
                
                return proc(0, stdout="", stderr="")
            return proc(0, stdout=marker_line(responses.pop(0)))
        module.subprocess.run = fake_run
        module.discover_product_godot = lambda root: {"engine": dict(FAKE_ENGINE)}
        return original_run, original_discover

    def test_baseline_recorded_for_two_counts(self):
        import p4_b_perf_baseline as perf
        frame_ms = {"min": 0.5, "p50": 6.9, "p95": 7.5, "p99": 8.0,
                    "max": 13.0, "mean": 6.9}
        payload = {"probe_id": "p4_b_perf_probe", "pass": True,
                   "requested_count": 50, "sample_frames": 600,
                   "spawned": 50, "samples_taken": 600,
                   "frame_ms": frame_ms, "fps": {"avg_from_mean_ms": 144.9},
                   "env": {"mode": "headless"}}
        originals = self._patch(perf, [payload, dict(payload, requested_count=100,
                                                     spawned=100)])
        try:
            out = self.tmp / "baseline.json"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = perf.main(["--counts", "50,100", "--frames", "600",
                                  "--out", str(out)])
        finally:
            perf.subprocess.run, perf.discover_product_godot = originals
        self.assertEqual(code, perf.EXIT_BASELINE)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["verdict"], "BASELINE")
        self.assertTrue(data["baseline_captured"])
        self.assertEqual(sorted(data["runs"].keys()), ["100", "50"])
        self.assertEqual(data["gate"], "NONE (baseline recording only)")
        self.assertIn("python_side", data["machine_env"])
        # user args must reach the driver after a -- separator
        for run in data["runs"].values():
            cmd = run["command"]
            self.assertIn("--", cmd)
            self.assertIn("--count=%s" % run["count"], cmd)

    def test_sanity_failure_is_fail_not_blocked(self):
        import p4_b_perf_baseline as perf
        payload = {"probe_id": "p4_b_perf_probe", "pass": False,
                   "errors": ["sanity check failed"], "frame_ms": {},
                   "env": {}}
        originals = self._patch(perf, [payload])
        try:
            out = self.tmp / "baseline.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = perf.main(["--counts", "50", "--out", str(out)])
        finally:
            perf.subprocess.run, perf.discover_product_godot = originals
        self.assertEqual(code, perf.EXIT_FAIL)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["verdict"], "FAIL")

    def test_sanitize_replaces_repo_root(self):
        import p4_b_perf_baseline as perf
        cleaned = perf.sanitize({"cmd": [str(REPO / "x"), "ok"],
                                 "nested": [str(REPO)]})
        self.assertEqual(cleaned["cmd"][0], "<repo>\\x")
        self.assertEqual(cleaned["nested"][0], "<repo>")


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


class SceneContractTest(unittest.TestCase):
    """On-disk contracts for the restored/modified product files."""

    def test_orb_pickup_scene_restored(self):
        tscn = read("product/scenes/Pickups/Orb/OrbPickup.tscn")
        self.assertIn("res://scenes/Pickups/Pickup.tscn", tscn)
        self.assertIn("res://scenes/Pickups/Orb/OrbPickup.gd", tscn)
        self.assertIn("does_vaccuum = true", tscn)
        self.assertIn("radius = 75.0", tscn)
        self.assertIn("AnimatedSprite2D", tscn)

    def test_orb_pickup_script_contract(self):
        gd = read("product/scenes/Pickups/Orb/OrbPickup.gd")
        self.assertIn('extends "res://scenes/Pickups/Pickup.gd"', gd)
        
        self.assertNotIn("rand_range(", gd)
        self.assertIn("randf_range(", gd)
        
        self.assertIn("ResourceLoader.exists(COLLECT_SOUND)", gd)
        self.assertIn("add_orb(orb_type, amount)", gd)

    def test_portal_pickup_scene_restored(self):
        tscn = read("product/scenes/Pickups/Portal/PortalPickup.tscn")
        self.assertIn("persistent = true", tscn)
        self.assertIn("text = \"Portal to Hideout\"", tscn)
        self.assertIn("GPUParticles2D", tscn)

    def test_portal_pickup_script_uses_g4_title_api(self):
        gd = read("product/scenes/Pickups/Portal/PortalPickup.gd")
        self.assertIn('extends "res://scenes/Pickups/Pickup.gd"', gd)
        self.assertIn("popup.title =", gd)
        self.assertNotIn("window_title", gd)
        self.assertIn("TintedConfirmationDialog.tscn", gd)
        self.assertIn("DeathScreen.tscn", gd)


class VfxContractTest(unittest.TestCase):
    def test_hit_burst_element_colors_and_lifecycle(self):
        gd = read("product/scenes/Particles/HitBurst.gd")
        for tag_value in ("11:", "12:", "13:", "14:", "15:"):
            self.assertIn(tag_value, gd)
        self.assertIn("finished.connect(_on_finished)", gd)
        self.assertIn("is_fx_enabled", gd)
        self.assertTrue((REPO / "product/scenes/Particles/HitBurst.tscn").is_file())

    def test_dissolve_mob_timing_configurable(self):
        gd = read("product/scenes/Mobs/DissolveMob.gd")
        self.assertIn("@export var dissolve_duration := 0.25", gd)
        self.assertIn("@export var dissolve_delay := 0.0", gd)
        self.assertIn("timer.wait_time = max(dissolve_duration + dissolve_delay, 0.01)",
                      gd)

    def test_floating_damage_rhythm_tiers(self):
        gd = read("product/scenes/Particles/FloatingDamage.gd")

        def block(name: str) -> str:
            segment = gd[gd.index("const %s" % name):]
            return segment[:segment.index("}")]

        normal_block = block("RHYTHM_NORMAL")
        crit_block = block("RHYTHM_CRIT")
        self.assertIn('"duration": 0.25', normal_block)
        self.assertIn('"duration": 0.4', crit_block)
        self.assertIn('"pop_scale": 2.0', crit_block)
        self.assertIn('"pop_scale": 1.0', normal_block)

    def test_mob_hit_wiring_order(self):
        gd = read("product/scenes/Mobs/Mob.gd")
        fill_health = gd.index("stats.fill_health()")
        prior_init = gd.index("_hit_vfx_prior_health = stats.health")
        connect = gd.index('"_on_hit_vfx_health_changed"')
        
        self.assertLess(prior_init, connect)
        self.assertLess(fill_health, prior_init)
        self.assertIn("preload(\"res://scenes/Particles/HitBurst.tscn\")", gd)
        self.assertIn("dissolve.dissolve_duration = death_dissolve_duration", gd)

    def test_plague_clouds_guard(self):
        gd = read("product/scenes/Projectiles/Skills/PlagueCloudsProjectile.gd")
        self.assertIn('get_node_or_null("GPUParticles2D")', gd)


class EvidenceArtifactTest(unittest.TestCase):
    def test_vfx_evidence_pass(self):
        data = json.loads(read("migration/conversion/p4_b_vfx.json"))
        self.assertEqual(data["verdict"], "PASS")
        self.assertEqual(data["exit_criteria"], ["F1"])
        self.assertTrue(data["result"]["pass"])
        self.assertEqual(data["script_errors"], [])

    def test_loot_real_evidence_pass(self):
        data = json.loads(read("migration/conversion/p4_b_loot_real.json"))
        self.assertEqual(data["verdict"], "PASS")
        self.assertIn("E6", data["exit_criteria"])
        result = data["result"]
        self.assertTrue(result["orb_drop"]["pass"])
        self.assertTrue(result["elite_drop_chain"]["pass"])
        self.assertTrue(result["portal"]["pass"])

    def test_perf_baseline_artifact_shape(self):
        data = json.loads(read("migration/conversion/p4_b_perf_baseline.json"))
        self.assertEqual(data["verdict"], "BASELINE")
        self.assertEqual(data["gate"], "NONE (baseline recording only)")
        for count in ("50", "100"):
            run = data["runs"][count]
            self.assertEqual(run["verdict"], "BASELINE")
            self.assertTrue(run["result"]["pass"])
            self.assertEqual(run["result"]["spawned"], int(count))
            for key in ("p50", "p95", "max"):
                self.assertGreater(run["result"]["frame_ms"][key], 0.0)
        self.assertIn("python_side", data["machine_env"])
        self.assertIn("godot_side", data["machine_env"])


if __name__ == "__main__":
    unittest.main()
