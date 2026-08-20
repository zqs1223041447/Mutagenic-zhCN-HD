#!/usr/bin/env python3
"""Static/structural self-tests for the B2-X2 Combat S5 evidence driver.

Runs without any game/VM: aspect catalog parsing, scenario-binding resolution
against the B1-X5 harness catalog, deterministic capture-plan and manifest
generation, dry-run/NOT_RUN semantics, candidate-absence exit codes, telemetry
schema compatibility with the harness, human-gate hygiene (machine never emits
HUMAN_ACCEPTED), checklist template/filled validation and portability/secret
hygiene of the X2-owned files.  Emits an evidence JSON.
"""

from __future__ import annotations

import base64
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

EXPECTED_ASPECT_IDS = [
    "player_response",
    "enemy_hit_reaction",
    "kill_feel",
    "camera",
    "audio",
]
S5_FILES = [
    "scripts/validate/s5_evidence.py",
    "scripts/validate/s5_evidence_selftests.py",
    "scripts/validate/s5_aspects.json",
]
_BS = chr(92)
_COLON = chr(58)
_NBS = r"[^" + _BS + _BS + r"]"
_UNC = (_BS * 4) + _NBS + "+" + (_BS * 2) + _NBS + "+" + (_BS * 2)
ABS_PATH_PATTERN = re.compile(
    r"(?i)\b[a-z]" + _COLON + _BS + _BS + r"|\b[a-z]" + _COLON + r"/|" + _UNC
)
PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


def _import_driver(root: Path) -> Any:
    import importlib.util
    path = root / "scripts" / "validate" / "s5_evidence.py"
    spec = importlib.util.spec_from_file_location("s5_evidence", path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run(root: Path, *args: str, cwd: Path | None = None, timeout: int = 180) -> subprocess.CompletedProcess:
    driver = root / "scripts" / "validate" / "s5_evidence.py"
    return subprocess.run(
        [sys.executable, str(driver), *args],
        capture_output=True, text=True, timeout=timeout, cwd=str(cwd or root),
    )


def _valid_telemetry(scenario_id: str, seed: int, killed: int = 20) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "scenario_id": scenario_id,
        "seed": seed,
        "started_at": "2026-08-20T00:00:00Z",
        "ended_at": "2026-08-20T00:00:30Z",
        "boot": {"ok": True, "fatal_count": 0, "alert_count": 0},
        "counters": {
            "spawned": 20, "alive": 0, "killed": killed,
            "duplicate_deaths": 0, "damage_events": 40, "melee_hits": 30,
            "crits": 2, "projectiles": 10, "triggers": 0,
            "player_moves": 50, "dashes": 4,
        },
        "perf": {"frames": 1800, "fps_avg": 60.0, "fps_min": 55.0, "fps_max": 62.0,
                 "frame_pacing_p95_ms": 17.5},
        "capture": {"screenshots": ["run_0001.png"], "video": None},
        "runtime": {"exit_code": 0, "in_game_result": "PASS", "notes": []},
        "proves": "fixture telemetry used by s5 evidence self-tests",
        "not_proven": "nothing; synthetic fixture",
    }


def _telemetry_with_spine(scenario_id: str, seed: int) -> dict[str, Any]:
    telemetry = _valid_telemetry(scenario_id, seed)
    telemetry["s5"] = {
        "event_spine": {
            "contract": "b2-x1-spine-v1",
            "counters": {"direct_hit": 10, "dot_tick": 5, "crit": 2, "kill": 20,
                         "duplicate_kill": 0, "heavy": 1},
        },
        "camera_start": [90.0, -240.0],
        "captures": {"screenshots": ["cluster_peak_0.png"], "video": None},
        "audio": {"voice_peak": 3, "clips": []},
    }
    return telemetry


def _harness_module(root: Path) -> Any:
    import importlib.util
    path = root / "scripts" / "validate" / "combat_harness.py"
    spec = importlib.util.spec_from_file_location("combat_harness", path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _package_manifest(package_dir: Path) -> dict[str, Any]:
    return json.loads((package_dir / "package_manifest.json").read_text(encoding="utf-8"))


def _core_of(manifest: dict[str, Any]) -> str:
    keys = set(manifest)
    for volatile in ("volatile", "repo_head_sha", "branch", "deterministic_core_sha256"):
        keys.discard(volatile)
    core = {key: manifest[key] for key in sorted(keys)}
    return json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _fixture_exe(root: Path, name: str) -> Path:
    fixture_dir = root / "10_logs" / "s5_evidence_selfcheck"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    path = fixture_dir / name
    if not path.is_file():
        path.write_bytes(b"MUT-DUMMY-EXE-" + name.encode("utf-8"))
    return path


def _capture_dir_for_pair(root: Path, out_dir: Path, aspect_id: str, scenario_id: str,
                          seed: int, side: str) -> Path:
    return out_dir / ("b2x2-" + aspect_id + "-" + scenario_id + "-" + str(seed)) / side / "captures"


def tc_aspects_catalog_parses(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_aspects(root)
    errors = driver.all_aspect_errors(catalog)
    if errors:
        return False, "aspect catalog contract errors: " + "; ".join(errors)
    return True, str(len(catalog.get("aspects", []))) + " aspects, zero contract errors"


def tc_five_aspect_ids_present(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_aspects(root)
    ids = [aspect["id"] for aspect in catalog.get("aspects", [])]
    missing = [expected for expected in EXPECTED_ASPECT_IDS if expected not in ids]
    if missing:
        return False, "missing aspect ids: " + ",".join(missing)
    return True, "all five required S5 aspects present"


def tc_aspect_bindings_resolve_in_harness_catalog(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_aspects(root)
    scenarios = _harness_module(root).load_catalog(root)
    known = {scenario["id"] for scenario in scenarios.get("scenarios", [])}
    bad: list[str] = []
    for aspect in catalog.get("aspects", []):
        for binding in aspect["scenario_bindings"]:
            if binding["scenario"] not in known:
                bad.append(aspect["id"] + "->" + binding["scenario"])
    if bad:
        return False, "bindings not in B1-X5 catalog: " + ",".join(bad)
    return True, "every aspect scenario binding resolves in combat_scenarios.json"


def tc_plan_determinism_same_seed(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    harness = _harness_module(root)
    catalog = driver.load_aspects(root)
    aspect = driver.get_aspect(catalog, "player_response")
    scenario = driver.get_scenario(harness, root, "movement_dash_smoke")
    assert aspect is not None and scenario is not None
    seed = int(scenario["default_seed"])
    plan_a = driver.build_capture_plan(harness, root, aspect, scenario, seed)
    plan_b = driver.build_capture_plan(harness, root, aspect, scenario, seed)
    if plan_a["plan_sha256"] != plan_b["plan_sha256"]:
        return False, "same seed produced different capture plans"
    return True, "same seed -> identical capture plan (sha " + plan_a["plan_sha256"][:12] + "...)"


def tc_plan_determinism_diff_seed(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    harness = _harness_module(root)
    catalog = driver.load_aspects(root)
    aspect = driver.get_aspect(catalog, "player_response")
    scenario = driver.get_scenario(harness, root, "movement_dash_smoke")
    assert aspect is not None and scenario is not None
    seed = int(scenario["default_seed"])
    plan_a = driver.build_capture_plan(harness, root, aspect, scenario, seed)
    plan_b = driver.build_capture_plan(harness, root, aspect, scenario, seed + 1)
    if plan_a["plan_sha256"] == plan_b["plan_sha256"]:
        return False, "different seeds produced identical capture plans"
    return True, "different seed -> different capture plan"


def tc_camera_start_declared_and_shared(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    harness = _harness_module(root)
    catalog = driver.load_aspects(root)
    bad: list[str] = []
    for aspect in catalog.get("aspects", []):
        for binding in aspect["scenario_bindings"]:
            scenario = driver.get_scenario(harness, root, binding["scenario"])
            if scenario is None:
                continue
            seed = int(scenario["default_seed"])
            plan = driver.build_capture_plan(harness, root, aspect, scenario, seed)
            start = plan["camera_start"]
            if start != [float(binding["camera_start"][0]), float(binding["camera_start"][1])]:
                bad.append(aspect["id"] + "/" + binding["scenario"] + " camera_start drift")
            if len(start) != 2:
                bad.append(aspect["id"] + "/" + binding["scenario"] + " camera_start not [x,y]")
    if bad:
        return False, "; ".join(bad)
    return True, "camera_start rendered in plan for every binding (same value on both sides by construction)"


def tc_plan_spawn_reuses_harness_plan(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    harness = _harness_module(root)
    catalog = driver.load_aspects(root)
    aspect = driver.get_aspect(catalog, "kill_feel")
    scenario = driver.get_scenario(harness, root, "cluster_kill_20")
    assert aspect is not None and scenario is not None
    seed = int(scenario["default_seed"])
    plan = driver.build_capture_plan(harness, root, aspect, scenario, seed)
    harness_plan = harness.build_plan(scenario, seed, harness.load_catalog(root))
    if plan["spawn"]["plan_sha256"] != harness_plan["plan_sha256"]:
        return False, "capture plan does not reuse the harness vertical-slice plan sha"
    if plan["spawn"]["total_spawn"] != harness_plan["total_spawn"]:
        return False, "capture plan spawn total differs from harness plan"
    return True, "capture plan spawn comes from the B1-X5 harness plan (same sha, same total)"


def tc_pair_dry_run_skeleton(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    proc = _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
                "--seed", str(seed), "--out-dir", str(out_dir), "--dry-run")
    if proc.returncode != driver.EXIT_NOT_RUN:
        return False, "expected exit " + str(driver.EXIT_NOT_RUN) + " (NOT_RUN) on dry-run, got " + str(proc.returncode)
    package_dir = out_dir / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    manifest = _package_manifest(package_dir)
    if manifest["result"] != "NOT_RUN":
        return False, "dry-run must have result NOT_RUN, got " + manifest["result"]
    for side in ("baseline", "candidate"):
        if manifest["sides"][side]["result"] != "NOT_RUN":
            return False, side + " dry-run must be NOT_RUN"
        if "telemetry_missing" not in manifest["sides"][side]["reasons"]:
            return False, side + " dry-run should record telemetry_missing reason"
    if manifest["human_gate"]["machine_status"] != driver.MACHINE_GATE_STATUS:
        return False, "human gate must stay EVIDENCE_PREPARED on dry-run"
    template = package_dir / ("s5_checklist_player_response_template.json")
    if not template.is_file():
        return False, "checklist template not written"
    if manifest.get("synthetic_captures") is not False:
        return False, "dry-run must not claim synthetic/real captures"
    return True, "pair dry-run -> exit 3, NOT_RUN skeleton, template + manifest written, no captures claimed"


def tc_manifest_determinism_same_inputs(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    out_a = out_dir / "det_a"
    out_b = out_dir / "det_b"
    for out in (out_a, out_b):
        proc = _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
                    "--seed", str(seed), "--out-dir", str(out), "--dry-run")
        if proc.returncode != driver.EXIT_NOT_RUN:
            return False, "dry-run exit mismatch in determinism setup"
    pkg_a = out_a / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    pkg_b = out_b / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    man_a = _package_manifest(pkg_a)
    man_b = _package_manifest(pkg_b)
    core_a = _core_of(man_a)
    core_b = _core_of(man_b)
    if core_a != core_b:
        return False, "deterministic cores differ for identical inputs"
    recomputed = driver.sha256_bytes(core_a.encode("utf-8"))
    if recomputed != man_a["deterministic_core_sha256"]:
        return False, "recorded deterministic_core_sha256 does not match recomputed core"
    return True, "identical inputs -> identical deterministic core + matching recorded sha"


def tc_manifest_determinism_diff_seed(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id = "movement_dash_smoke"
    out_a = out_dir / "det_diff_a"
    out_b = out_dir / "det_diff_b"
    for out, seed in ((out_a, 2026082001), (out_b, 2026082002)):
        proc = _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
                    "--seed", str(seed), "--out-dir", str(out), "--dry-run")
        if proc.returncode != driver.EXIT_NOT_RUN:
            return False, "dry-run exit mismatch in determinism diff setup"
    pkg_a = out_a / ("b2x2-player_response-" + scenario_id + "-2026082001")
    pkg_b = out_b / ("b2x2-player_response-" + scenario_id + "-2026082002")
    if _core_of(_package_manifest(pkg_a)) == _core_of(_package_manifest(pkg_b)):
        return False, "different seeds produced identical deterministic cores"
    return True, "different seed -> different deterministic core"


def tc_telemetry_s5_extension_passes_harness_schema(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    harness = _harness_module(root)
    telemetry = _telemetry_with_spine("cluster_kill_20", 2026082005)
    issues = harness.validate_telemetry(telemetry, driver.load_telemetry_schema(root))
    if issues:
        return False, "s5-extension telemetry fails harness schema: " + "; ".join(issues)
    return True, "telemetry with s5 extension stays compatible with combat_telemetry_schema.json"


def tc_missing_candidate_usage_exit(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    checks = [
        ("pair", "--aspect", "player_response", "--scenario", scenario_id, "--seed", str(seed),
         "--out-dir", str(out_dir)),
        ("pair", "--aspect", "player_response", "--scenario", scenario_id, "--seed", str(seed),
         "--baseline", str(_fixture_exe(root, "base.exe")), "--out-dir", str(out_dir)),
        ("pair", "--aspect", "player_response", "--scenario", scenario_id, "--seed", str(seed),
         "--baseline", str(_fixture_exe(root, "base.exe")),
         "--candidate", str(out_dir / "does_not_exist.exe"), "--out-dir", str(out_dir)),
    ]
    for args in checks:
        proc = _run(root, *args)
        if proc.returncode != driver.EXIT_USAGE:
            return False, "expected exit " + str(driver.EXIT_USAGE) + " (USAGE) for missing/nonexistent candidate, got " + str(proc.returncode)
    return True, "missing or nonexistent candidate -> stable USAGE exit 4"


def tc_missing_vm_not_run(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    base = _fixture_exe(root, "base.exe")
    cand = _fixture_exe(root, "cand.exe")
    proc = _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
                "--seed", str(seed), "--baseline", str(base), "--candidate", str(cand),
                "--out-dir", str(out_dir))
    if proc.returncode != driver.EXIT_NOT_RUN:
        return False, "expected exit " + str(driver.EXIT_NOT_RUN) + " (NOT_RUN) without VM launcher, got " + str(proc.returncode)
    package_dir = out_dir / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    manifest = _package_manifest(package_dir)
    for side in ("baseline", "candidate"):
        reasons = manifest["sides"][side]["reasons"]
        if not any(reason.startswith("vm_not_launched") for reason in reasons):
            return False, side + " should record vm_not_launched reason, got " + ",".join(reasons)
        if manifest["sides"][side]["result"] != "NOT_RUN":
            return False, side + " without VM must be NOT_RUN"
    return True, "no VM launcher -> exit 3, machine-readable manifest with vm_not_launched reasons"


def tc_require_event_spine_missing_not_run(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    telemetry_path = out_dir / ("telemetry_" + scenario_id + "_" + str(seed) + ".json")
    telemetry_path.write_text(json.dumps(_valid_telemetry(scenario_id, seed)), encoding="utf-8")
    base = _fixture_exe(root, "base.exe")
    proc = _run(root, "capture", "--aspect", "player_response", "--side", "baseline",
                "--scenario", scenario_id, "--seed", str(seed), "--baseline", str(base),
                "--telemetry", str(telemetry_path), "--require-event-spine",
                "--out-dir", str(out_dir))
    if proc.returncode != driver.EXIT_NOT_RUN:
        return False, "expected NOT_RUN for missing required spine, got " + str(proc.returncode)
    package_dir = out_dir / ("b2x2-player_response-" + scenario_id + "-" + str(seed) + "-baseline")
    manifest = _package_manifest(package_dir)
    if manifest["event_spine"]["status"] != "NOT_RUN":
        return False, "spine status should be NOT_RUN, got " + manifest["event_spine"]["status"]
    if not any(reason.startswith("required_event_spine_missing") for reason in manifest["sides"]["baseline"]["reasons"]):
        return False, "should record required_event_spine_missing reason"
    return True, "--require-event-spine with absent B2-X1 spine -> exit 3 NOT_RUN (documented pre-X1 semantic)"


def tc_full_evidence_prepared_with_synthetic_captures(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    telemetry_path = out_dir / ("telemetry_ok_" + scenario_id + "_" + str(seed) + ".json")
    telemetry_path.write_text(json.dumps(_valid_telemetry(scenario_id, seed)), encoding="utf-8")
    base = _fixture_exe(root, "base.exe")
    cand = _fixture_exe(root, "cand.exe")
    launch = shlex.join([sys.executable, "-c", "print(1)"])
    for side in ("baseline", "candidate"):
        capture_dir = _capture_dir_for_pair(root, out_dir, "player_response", scenario_id, seed, side)
        capture_dir.mkdir(parents=True, exist_ok=True)
        (capture_dir / "synthetic.marker").write_bytes(b"synthetic-test-only")
        for point in ("start_frame", "dash_start", "dash_recover", "move_strafe"):
            (capture_dir / (point + "_0.png")).write_bytes(PNG_1PX)
    proc = _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
                "--seed", str(seed), "--baseline", str(base), "--candidate", str(cand),
                "--telemetry", str(telemetry_path), "--launch", launch,
                "--build-id", "20260820-120000-abcdef", "--modset", "mock-modset-hash",
                "--out-dir", str(out_dir))
    if proc.returncode != driver.EXIT_EVIDENCE_PREPARED:
        return False, "expected EVIDENCE_PREPARED (0), got " + str(proc.returncode) + ": " + proc.stdout + proc.stderr
    package_dir = out_dir / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    manifest = _package_manifest(package_dir)
    if manifest["result"] != "EVIDENCE_PREPARED":
        return False, "expected EVIDENCE_PREPARED result"
    if manifest["synthetic_captures"] is not True:
        return False, "manifest must label synthetic captures"
    for side in ("baseline", "candidate"):
        side_info = manifest["sides"][side]
        if side_info["result"] != "OK":
            return False, side + " should be OK, got " + side_info["result"] + " reasons=" + ",".join(side_info["reasons"])
        if side_info["candidate"]["sha256"] is None:
            return False, side + " candidate sha missing"
        if side_info["build_id"]["unbound"]:
            return False, side + " build_id must be bound when --build-id given"
        if side_info["modset"]["value"] != "mock-modset-hash":
            return False, side + " modset must come from --modset"
        if not all(asset["synthetic"] for asset in side_info["captures"]["assets"]):
            return False, side + " capture assets must be labeled synthetic"
    return True, "full machine-prepared pair with labeled-synthetic captures + bound build id/modset -> EVIDENCE_PREPARED (0)"


def tc_human_gate_never_auto_accepted(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    hits: list[str] = []
    for package_dir in out_dir.rglob("package_manifest.json"):
        manifest = json.loads(package_dir.read_text(encoding="utf-8"))
        gate = manifest.get("human_gate", {})
        if gate.get("machine_status") != driver.MACHINE_GATE_STATUS:
            hits.append(package_dir.name + ": machine_status " + str(gate.get("machine_status")))
        if gate.get("verdict") is not None:
            hits.append(package_dir.name + ": machine-set verdict present")
        if manifest.get("result") == "HUMAN_ACCEPTED":
            hits.append(package_dir.name + ": result claims HUMAN_ACCEPTED")
    for template in out_dir.rglob("s5_checklist_*_template.json"):
        text = template.read_text(encoding="utf-8")
        if "HUMAN_ACCEPTED" in text:
            hits.append(template.name + ": template contains HUMAN_ACCEPTED")
    if hits:
        return False, "; ".join(hits[:10])
    return True, "no generated manifest/template claims HUMAN_ACCEPTED; machine gate stays EVIDENCE_PREPARED"


def tc_checklist_template_structure(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
         "--seed", str(seed), "--out-dir", str(out_dir), "--dry-run")
    package_dir = out_dir / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    template = json.loads((package_dir / "s5_checklist_player_response_template.json").read_text(encoding="utf-8"))
    if template["human_gate"]["machine_status"] != driver.MACHINE_GATE_STATUS:
        return False, "template human gate must be EVIDENCE_PREPARED"
    if template["conclusion"]["verdict"] is not None:
        return False, "template verdict must start null"
    for question in template["questions"]:
        if question["judgment"] is not None:
            return False, "template judgments must start null: " + question["id"]
    if not template["questions"]:
        return False, "empty checklist"
    return True, str(len(template["questions"])) + " unanswered questions; machine gate EVIDENCE_PREPARED; verdict null"


def tc_checklist_end_to_end_structural(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
         "--seed", str(seed), "--out-dir", str(out_dir), "--dry-run")
    package_dir = out_dir / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    source_template = json.loads((package_dir / "s5_checklist_player_response_template.json").read_text(encoding="utf-8"))
    filled = json.loads(json.dumps(source_template))
    for question in filled["questions"]:
        rtype = question["response_type"]
        question["judgment"] = 4 if rtype == "score_1_5" else (
            True if rtype == "yes_no" else ("candidate" if rtype == "prefer_side" else "fixture note"))
    filled["conclusion"] = {
        "verdict": "accept_candidate", "accepted_sides": ["candidate"],
        "signed_by": "fixture-human", "signed_at": "2026-08-20T00:00:00Z",
        "notes": "TEST FIXTURE only; synthetic human input, not real acceptance evidence.",
    }
    (package_dir / "s5_checklist_player_response_filled.json").write_text(
        json.dumps(filled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    proc = _run(root, "checklist", "--package", str(package_dir))
    if proc.returncode != driver.EXIT_EVIDENCE_PREPARED:
        return False, "structurally valid filled checklist should pass, got " + str(proc.returncode) + ": " + proc.stdout + proc.stderr
    review = json.loads((package_dir / "s5_checklist_review_player_response.json").read_text(encoding="utf-8"))
    if review["valid"] is not True:
        return False, "review summary must record valid structural state"
    broken = json.loads(json.dumps(source_template))
    for question in broken["questions"]:
        question["judgment"] = None
    (package_dir / "s5_checklist_player_response_filled.json").write_text(
        json.dumps(broken, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    proc_broken = _run(root, "checklist", "--package", str(package_dir))
    if proc_broken.returncode != driver.EXIT_EVIDENCE_FAIL:
        return False, "unanswered checklist must fail structurally, got " + str(proc_broken.returncode)
    return True, "filled checklist (fixture) validates; broken checklist fails with exit 2; driver never writes verdict"


def tc_validate_package_structure(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "movement_dash_smoke", 2026082001
    _run(root, "pair", "--aspect", "player_response", "--scenario", scenario_id,
         "--seed", str(seed), "--out-dir", str(out_dir), "--dry-run")
    package_dir = out_dir / ("b2x2-player_response-" + scenario_id + "-" + str(seed))
    proc = _run(root, "validate", "--package", str(package_dir))
    if proc.returncode != driver.EXIT_EVIDENCE_PREPARED:
        return False, "dry-run package should validate structurally, got " + str(proc.returncode) + ": " + proc.stdout + proc.stderr
    (package_dir / "s5_checklist_player_response_template.json").unlink()
    proc_missing = _run(root, "validate", "--package", str(package_dir))
    if proc_missing.returncode != driver.EXIT_EVIDENCE_FAIL:
        return False, "package missing checklist template must fail structure validation, got " + str(proc_missing.returncode)
    return True, "validate --package enforces required structure (template present) with exit 0/2"


def tc_usage_unknown_aspect_scenario(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    for args in (("pair", "--aspect", "does_not_exist"), ("plan", "--aspect", "player_response",
                 "--scenario", "does_not_exist"), ("describe", "--aspect", "does_not_exist")):
        proc = _run(root, *args)
        if proc.returncode == 0:
            return False, "expected nonzero exit for " + " ".join(args[:3])
    return True, "unknown aspect / scenario -> stable nonzero usage exit"


def tc_repo_root_from_any_cwd(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    cwd = root / "tests" / "s5_evidence"
    cwd.mkdir(parents=True, exist_ok=True)
    proc = _run(root, "aspects", cwd=cwd)
    if proc.returncode != 0:
        return False, "aspects from nested cwd failed: " + proc.stderr
    if "player_response" not in proc.stdout:
        return False, "aspects output missing expected id"
    return True, "driver resolves repo root from nested cwd"


def tc_abs_path_scan_s5_files(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    hits: list[str] = []
    for relative in S5_FILES:
        path = root / relative
        if not path.is_file():
            hits.append("missing file: " + relative)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if ABS_PATH_PATTERN.search(line):
                hits.append(relative + ":" + str(line_number) + ": " + line.strip()[:100])
    if hits:
        return False, "absolute host paths found: " + "; ".join(hits[:10])
    return True, "no drive-letter / UNC absolute paths in X2-owned files"


def tc_secret_scan_s5_files(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    patterns = ["script" + "_key", r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY",
                r"(?i)password\s*=\s*['\"][^'\"]+['\"]", "api" + "[_-]?" + "key"]
    hits: list[str] = []
    for relative in S5_FILES:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            if re.search(pattern, text):
                hits.append(relative + ": " + pattern)
    if hits:
        return False, "secret-like tokens found: " + str(hits)
    return True, "no secret-like tokens in X2-owned files"


TESTS: list[tuple[str, Callable[[Path, Any, Path], tuple[bool, str]]]] = [
    ("aspects_catalog_parses", tc_aspects_catalog_parses),
    ("five_aspect_ids_present", tc_five_aspect_ids_present),
    ("aspect_bindings_resolve_in_harness_catalog", tc_aspect_bindings_resolve_in_harness_catalog),
    ("capture_plan_determinism_same_seed", tc_plan_determinism_same_seed),
    ("capture_plan_determinism_diff_seed", tc_plan_determinism_diff_seed),
    ("camera_start_declared_and_shared", tc_camera_start_declared_and_shared),
    ("capture_plan_spawn_reuses_harness_plan", tc_plan_spawn_reuses_harness_plan),
    ("pair_dry_run_skeleton_not_run", tc_pair_dry_run_skeleton),
    ("manifest_determinism_same_inputs", tc_manifest_determinism_same_inputs),
    ("manifest_determinism_diff_seed", tc_manifest_determinism_diff_seed),
    ("telemetry_s5_extension_passes_harness_schema", tc_telemetry_s5_extension_passes_harness_schema),
    ("missing_candidate_usage_exit", tc_missing_candidate_usage_exit),
    ("missing_vm_not_run", tc_missing_vm_not_run),
    ("require_event_spine_missing_not_run", tc_require_event_spine_missing_not_run),
    ("full_evidence_prepared_synthetic_captures", tc_full_evidence_prepared_with_synthetic_captures),
    ("human_gate_never_auto_accepted", tc_human_gate_never_auto_accepted),
    ("checklist_template_structure", tc_checklist_template_structure),
    ("checklist_end_to_end_structural", tc_checklist_end_to_end_structural),
    ("validate_package_structure", tc_validate_package_structure),
    ("usage_unknown_aspect_scenario", tc_usage_unknown_aspect_scenario),
    ("repo_root_from_any_cwd", tc_repo_root_from_any_cwd),
    ("abs_path_scan_s5_files", tc_abs_path_scan_s5_files),
    ("secret_scan_s5_files", tc_secret_scan_s5_files),
]


def run_selfchecks(root: Path, args: Any) -> int:
    driver = _import_driver(root)
    out_dir = (args.out_dir or root / "10_logs" / "s5_evidence_selfcheck").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for name, test in TESTS:
        test_out = out_dir / name
        test_out.mkdir(parents=True, exist_ok=True)
        try:
            ok, detail = test(root, driver, test_out)
        except Exception as exc:
            ok, detail = False, "exception: " + repr(exc)
        results.append({"id": name, "passed": ok, "detail": detail})
        print("[" + ("PASS" if ok else "FAIL") + "] " + name + ": " + detail)
    passed = sum(1 for item in results if item["passed"])
    total = len(results)
    all_ok = passed == total
    evidence = {
        "evidence_id": "B2-X2-s5-evidence-selfcheck",
        "task_id": "B2-X2",
        "ran_at": driver.utc_now(),
        "repo_head_sha": driver.git_head_sha(root),
        "branch": driver.git_branch(root),
        "repo_root": "<repo_root>",
        "driver_sha256": driver.sha256_file(root / "scripts" / "validate" / "s5_evidence.py"),
        "python_version": sys.version.split()[0],
        "tests": results,
        "summary": {"total": total, "passed": passed, "failed": total - passed},
        "result": "PASS" if all_ok else "FAIL",
        "proves": "the S5 evidence flow parses its aspect catalog, resolves every aspect scenario binding "
                  "against the B1-X5 harness catalog, reuses the harness spawn plan and telemetry schema, is "
                  "deterministic (plan + manifest core), produces dry-run/NOT_RUN skeletons with stable exit "
                  "codes (USAGE 4 / NOT_RUN 3 / EVIDENCE_FAIL 2 / EVIDENCE_PREPARED 0), keeps the machine "
                  "human gate at EVIDENCE_PREPARED (never HUMAN_ACCEPTED), validates human-filled checklist "
                  "structure without writing verdicts, and carries no host-absolute paths or secrets",
        "not_proven": "in-game execution, real screenshots/frame sequences/video/audio, real B2-X0 aggregate "
                      "candidate build ids, real B2-X1 event spine telemetry, human S5 acceptance",
    }
    evidence_path = (args.evidence or out_dir / "s5_evidence_selfcheck_evidence.json").resolve()
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("selfcheck evidence: " + str(evidence_path))
    print("summary: " + str(passed) + "/" + str(total) + " passed -> " + ("PASS" if all_ok else "FAIL"))
    return 0 if all_ok else driver.EXIT_SELFTEST_FAIL


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--evidence", type=Path, default=None)
    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[1]
    raise SystemExit(run_selfchecks(repo_root, args))