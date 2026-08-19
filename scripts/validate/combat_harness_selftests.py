#!/usr/bin/env python3
"""Static/structural self-tests for the B1-X5 combat harness driver.

Runs without any game/VM: scenario catalog parsing, seed determinism, report
skeleton, telemetry validation, assert verdicts, exit-code contract and
portability/secret hygiene of the X5-owned files.  Emits an evidence JSON.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

EXPECTED_SCENARIO_IDS = [
    "movement_dash_smoke",
    "single_melee_hit",
    "single_ranged_pack",
    "rapid_hit_10s",
    "cluster_kill_20",
    "projectile_density",
    "chain_pierce_trigger",
    "stress_random_300",
]
X5_FILES = [
    "scripts/validate/combat_harness.py",
    "scripts/validate/combat_harness_selftests.py",
    "scripts/validate/combat_scenarios.json",
    "scripts/validate/combat_telemetry_schema.json",
]
_BS = chr(92)
_COLON = chr(58)
_NBS = r"[^" + _BS + _BS + r"]"
_UNC = (_BS * 4) + _NBS + "+" + (_BS * 2) + _NBS + "+" + (_BS * 2)
ABS_PATH_PATTERN = re.compile(
    r"(?i)\b[a-z]" + _COLON + _BS + _BS + r"|\b[a-z]" + _COLON + r"/|" + _UNC
)


def _import_driver(root: Path) -> Any:
    import importlib.util
    path = root / "scripts" / "validate" / "combat_harness.py"
    spec = importlib.util.spec_from_file_location("combat_harness", path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _run(root: Path, *args: str, cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    driver = root / "scripts" / "validate" / "combat_harness.py"
    return subprocess.run(
        [sys.executable, str(driver), *args],
        capture_output=True, text=True, timeout=timeout, cwd=str(cwd or root),
    )


def _valid_telemetry(scenario_id: str, seed: int, killed: int = 20, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "schema_version": "1.0",
        "scenario_id": scenario_id,
        "seed": seed,
        "started_at": "2026-08-20T00:00:00Z",
        "ended_at": "2026-08-20T00:00:30Z",
        "boot": {"ok": True, "fatal_count": 0, "alert_count": 0},
        "counters": {
            "spawned": 20, "alive": 0, "killed": killed,
            "duplicate_deaths": 0, "damage_events": 40,
            "melee_hits": 30, "crits": 2, "projectiles": 10,
            "triggers": 0, "player_moves": 50, "dashes": 4,
        },
        "perf": {"frames": 1800, "fps_avg": 60.0, "fps_min": 55.0, "fps_max": 62.0, "frame_pacing_p95_ms": 17.5},
        "capture": {"screenshots": ["run_0001.png"], "video": None},
        "runtime": {"exit_code": 0, "in_game_result": "PASS", "notes": []},
        "proves": "fixture telemetry used by driver self-tests",
        "not_proven": "nothing; synthetic fixture",
    }
    if extra:
        data.update(extra)
    return data


def tc_catalog_parses(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_catalog(root)
    errors = driver.all_scenario_errors(catalog)
    ids = [s["id"] for s in catalog.get("scenarios", [])]
    if errors:
        return False, f"contract errors: {errors}"
    if len(ids) != len(EXPECTED_SCENARIO_IDS):
        return False, f"expected {len(EXPECTED_SCENARIO_IDS)} scenarios, got {len(ids)}"
    return True, f"{len(ids)} scenarios, zero contract errors"


def tc_expected_ids_present(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_catalog(root)
    ids = [s["id"] for s in catalog.get("scenarios", [])]
    missing = [expected for expected in EXPECTED_SCENARIO_IDS if expected not in ids]
    if missing:
        return False, f"missing scenario ids: {missing}"
    return True, "all eight expected scenario ids present"


def tc_plan_determinism_same_seed(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_catalog(root)
    scenario = driver.get_scenario(catalog, "cluster_kill_20")
    assert scenario is not None
    seed = int(scenario["default_seed"])
    plan_a = driver.build_plan(scenario, seed, catalog)
    plan_b = driver.build_plan(scenario, seed, catalog)
    if plan_a["plan_sha256"] != plan_b["plan_sha256"]:
        return False, "same seed produced different plans"
    expected_total = sum(int(entry["count"]) for entry in scenario["mob_composition"])
    if plan_a["total_spawn"] != expected_total:
        return False, f"plan total {plan_a['total_spawn']} != composition {expected_total}"
    return True, f"same seed -> identical plan (sha {plan_a['plan_sha256'][:12]}...), total {plan_a['total_spawn']}"


def tc_plan_determinism_diff_seed(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_catalog(root)
    scenario = driver.get_scenario(catalog, "cluster_kill_20")
    assert scenario is not None
    seed = int(scenario["default_seed"])
    plan_a = driver.build_plan(scenario, seed, catalog)
    plan_b = driver.build_plan(scenario, seed + 1, catalog)
    if plan_a["plan_sha256"] == plan_b["plan_sha256"]:
        return False, "different seeds produced identical plans"
    return True, "different seed -> different plan"


def tc_plan_bounds(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_catalog(root)
    scenario = driver.get_scenario(catalog, "cluster_kill_20")
    assert scenario is not None
    plan = driver.build_plan(scenario, int(scenario["default_seed"]), catalog)
    origin = scenario["spawn"]["origin"]
    spread = float(scenario["spawn"]["spread"])
    for entry in plan["spawns"]:
        dx = entry["position"][0] - origin[0]
        dy = entry["position"][1] - origin[1]
        if abs(dx) > spread or abs(dy) > spread:
            return False, f"spawn {entry['order']} out of bounds: {entry['position']}"
    return True, "all spawn positions within declared spread"


def tc_stress_plan_count(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    catalog = driver.load_catalog(root)
    scenario = driver.get_scenario(catalog, "stress_random_300")
    assert scenario is not None
    plan = driver.build_plan(scenario, int(scenario["default_seed"]), catalog)
    if plan["total_spawn"] != 300:
        return False, f"stress plan total {plan['total_spawn']} != 300"
    return True, "stress_random_300 plan renders 300 random spawns"


def tc_report_skeleton_dry_run(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id = "cluster_kill_20"
    proc = _run(root, "run", "--scenario", scenario_id, "--candidate", str(driver.__file__),
                "--dry-run", "--out-dir", str(out_dir))
    if proc.returncode != driver.EXIT_NOT_PROVEN:
        return False, f"expected exit {driver.EXIT_NOT_PROVEN} (NOT_PROVEN), got {proc.returncode}: {proc.stdout} {proc.stderr}"
    report_path = out_dir / "reports" / f"{scenario_id}_{2026082005}_NOT_PROVEN.json"
    if not report_path.is_file():
        return False, f"report skeleton not written: {report_path.name}"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for key in ("scenario", "seed", "candidate", "timestamps", "boot", "counters", "perf",
                "capture", "runtime", "assertions", "result", "proves", "not_proven"):
        if key not in report:
            return False, f"report skeleton missing contract field: {key}"
    if report["result"] != "NOT_PROVEN":
        return False, f"expected NOT_PROVEN skeleton, got {report['result']}"
    return True, "dry-run skeleton: NOT_PROVEN, exit 3, all contract fields present"


def tc_telemetry_pass(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "cluster_kill_20", 2026082005
    telemetry = _valid_telemetry(scenario_id, seed, killed=20)
    telemetry_path = out_dir / "telemetry" / f"{scenario_id}_{seed}.json"
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    proc = _run(root, "run", "--scenario", scenario_id, "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--telemetry", str(telemetry_path))
    if proc.returncode != driver.EXIT_PASS:
        return False, f"expected exit {driver.EXIT_PASS} (PASS), got {proc.returncode}: {proc.stdout} {proc.stderr}"
    return True, "valid telemetry with killed=20 -> PASS (exit 0)"


def tc_telemetry_fail(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "cluster_kill_20", 2026082005
    telemetry = _valid_telemetry(scenario_id, seed, killed=19)
    telemetry_path = out_dir / "telemetry" / f"{scenario_id}_{seed}.json"
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    proc = _run(root, "run", "--scenario", scenario_id, "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--telemetry", str(telemetry_path))
    if proc.returncode != driver.EXIT_FAIL:
        return False, f"expected exit {driver.EXIT_FAIL} (FAIL), got {proc.returncode}: {proc.stdout} {proc.stderr}"
    return True, "telemetry killed=19 -> FAIL (exit 2)"


def tc_telemetry_invalid_not_proven(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "cluster_kill_20", 2026082005
    telemetry = _valid_telemetry(scenario_id, seed, killed=20, extra={"counters": {}})
    telemetry_path = out_dir / "telemetry" / f"{scenario_id}_{seed}.json"
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    proc = _run(root, "run", "--scenario", scenario_id, "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--telemetry", str(telemetry_path))
    if proc.returncode != driver.EXIT_NOT_PROVEN:
        return False, f"expected exit {driver.EXIT_NOT_PROVEN}, got {proc.returncode}: {proc.stdout} {proc.stderr}"
    return True, "schema-invalid telemetry -> NOT_PROVEN (exit 3)"


def tc_usage_errors_nonzero(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    checks = [
        ("run", "--scenario", "does_not_exist"),
        ("describe", "--scenario", "does_not_exist"),
        ("plan", "--scenario", "does_not_exist"),
        ("run", "--scenario", "cluster_kill_20"),
    ]
    for args in checks:
        proc = _run(root, *args, "--out-dir", str(out_dir))
        if proc.returncode == 0:
            return False, f"expected nonzero exit for {args}, got 0"
    return True, "unknown scenario / missing candidate -> nonzero exit codes"


def tc_repo_root_from_any_cwd(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    cwd = root / "tests" / "combat_harness"
    cwd.mkdir(parents=True, exist_ok=True)
    proc = _run(root, "scenarios", cwd=cwd)
    if proc.returncode != 0:
        return False, f"scenarios from nested cwd failed: {proc.stderr}"
    if "cluster_kill_20" not in proc.stdout:
        return False, "scenarios output missing expected id"
    return True, "driver resolves repo root from nested cwd"


def tc_abs_path_scan(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    hits: list[str] = []
    for relative in X5_FILES:
        path = root / relative
        if not path.is_file():
            hits.append(f"missing file: {relative}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if ABS_PATH_PATTERN.search(line):
                hits.append(f"{relative}:{line_number}: {line.strip()[:100]}")
    if hits:
        return False, "absolute host paths found: " + "; ".join(hits[:10])
    return True, "no drive-letter / UNC absolute paths in X5-owned files"


def tc_secret_scan(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    patterns = ["script" + "_key", r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY",
                r"(?i)password\s*=\s*['\"][^'\"]+['\"]", "api" + "[_-]?" + "key"]
    hits: list[str] = []
    for relative in X5_FILES:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                hits.append(f"{relative}: {pattern}")
    if hits:
        return False, f"secret-like tokens found: {hits}"
    return True, "no secret-like tokens in X5-owned files"


def tc_game_request_contract(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id, seed = "cluster_kill_20", 2026082005
    proc = _run(root, "run", "--scenario", scenario_id, "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--dry-run")
    if proc.returncode != driver.EXIT_NOT_PROVEN:
        return False, f"expected dry-run exit {driver.EXIT_NOT_PROVEN}, got {proc.returncode}: {proc.stdout} {proc.stderr}"
    request_path = out_dir / "requests" / f"{scenario_id}_{seed}.json"
    if not request_path.is_file():
        return False, f"request file not written: {request_path.name}"
    payload = driver.read_json(request_path)
    game = payload.get("game_request")
    if not isinstance(game, dict):
        return False, "request payload missing 'game_request' object"
    if game.get("scenario_id") != scenario_id:
        return False, f"game_request.scenario_id mismatch: {game.get('scenario_id')!r}"
    if game.get("seed") != seed:
        return False, f"game_request.seed mismatch: {game.get('seed')!r}"
    if not isinstance(game.get("duration"), (int, float)) or game["duration"] <= 0:
        return False, f"game_request.duration invalid: {game.get('duration')!r}"
    plan = game.get("plan")
    if not isinstance(plan, list) or len(plan) != 20:
        return False, f"game_request.plan must flatten 20 spawns, got {type(plan).__name__} len {len(plan) if isinstance(plan, list) else '?'}"
    for entry in plan:
        for key in ("res", "x", "y", "count"):
            if key not in entry:
                return False, f"game_request.plan entry missing '{key}': {entry}"
        if not isinstance(entry["res"], str) or not entry["res"].startswith("res://"):
            return False, f"game_request.plan entry res invalid: {entry['res']!r}"
        if entry["count"] != 1:
            return False, f"game_request.plan entry count must be 1 per flattened spawn: {entry}"
    return True, "game_request mirrors the 20 spawned mobs as res/x/y/count plan entries"


def tc_plan_cli_deterministic(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    scenario_id = "cluster_kill_20"
    seed = "2026082005"
    first = _run(root, "plan", "--scenario", scenario_id, "--seed", seed, "--raw")
    second = _run(root, "plan", "--scenario", scenario_id, "--seed", seed, "--raw")
    if first.returncode != 0 or second.returncode != 0:
        return False, "plan subcommand failed"
    if first.stdout != second.stdout:
        return False, "plan CLI output differs for the same seed"
    return True, "plan CLI is byte-identical for the same seed"


TESTS: list[tuple[str, Callable[[Path, Any, Path], tuple[bool, str]]]] = [
    ("catalog_parses", tc_catalog_parses),
    ("expected_scenario_ids_present", tc_expected_ids_present),
    ("plan_determinism_same_seed", tc_plan_determinism_same_seed),
    ("plan_determinism_diff_seed", tc_plan_determinism_diff_seed),
    ("plan_positions_within_spread", tc_plan_bounds),
    ("stress_random_300_plan_count", tc_stress_plan_count),
    ("report_skeleton_dry_run", tc_report_skeleton_dry_run),
    ("telemetry_valid_pass", tc_telemetry_pass),
    ("telemetry_required_fail", tc_telemetry_fail),
    ("telemetry_invalid_not_proven", tc_telemetry_invalid_not_proven),
    ("usage_errors_nonzero", tc_usage_errors_nonzero),
    ("repo_root_from_any_cwd", tc_repo_root_from_any_cwd),
    ("abs_path_scan_x5_files", tc_abs_path_scan),
    ("secret_scan_x5_files", tc_secret_scan),
    ("plan_cli_byte_identical", tc_plan_cli_deterministic),
    ("game_request_contract", tc_game_request_contract),
]


def run_selfchecks(root: Path, args: Any) -> int:
    driver = _import_driver(root)
    out_dir = (args.out_dir or root / "10_logs" / "combat_harness_selfcheck").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for name, test in TESTS:
        try:
            ok, detail = test(root, driver, out_dir)
        except Exception as exc:
            ok, detail = False, f"exception: {exc!r}"
        results.append({"id": name, "passed": ok, "detail": detail})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    passed = sum(1 for item in results if item["passed"])
    total = len(results)
    all_ok = passed == total
    evidence = {
        "evidence_id": "B1-X5-combat-harness-selfcheck",
        "task_id": "B1-X5",
        "ran_at": driver.utc_now(),
        "repo_head_sha": driver.git_head_sha(root),
        "branch": driver.git_branch(root),
        "repo_root": "<repo_root>",
        "driver_sha256": driver.sha256_file(root / "scripts" / "validate" / "combat_harness.py"),
        "python_version": sys.version.split()[0],
        "tests": results,
        "summary": {"total": total, "passed": passed, "failed": total - passed},
        "result": "PASS" if all_ok else "FAIL",
        "proves": "the harness driver parses its scenario catalog, is seed-deterministic, emits the telemetry "
                  "contract, classifies PASS/FAIL/NOT_PROVEN, enforces its exit-code contract, resolves the repo "
                  "root from any cwd and carries no host-absolute paths or secrets in X5-owned files",
        "not_proven": "in-game execution, real FPS/frame pacing, real kill/death behavior, candidate builds",
    }
    evidence_path = (args.evidence or out_dir / "combat_harness_selfcheck_evidence.json").resolve()
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"selfcheck evidence: {evidence_path}")
    print(f"summary: {passed}/{total} passed -> {'PASS' if all_ok else 'FAIL'}")
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
