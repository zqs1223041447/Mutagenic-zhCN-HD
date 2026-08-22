#!/usr/bin/env python3
"""Offline structural self-tests for the B3-X3 density benchmark scaffold.

Runs without any game/VM: matrix contract, pressure ladder counts (5/20/50/100),
seed determinism, dry-run skeleton, telemetry envelope validation, metric
derivation, threshold evaluation (draft, informational), base-schema
compatibility, entrance reuse, portability and secret hygiene of the
benchmark-owned files.  Emits an evidence JSON under 10_logs/.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

EXPECTED_LEVEL_IDS = ["density_5", "density_20", "density_50", "density_100"]
BENCHMARK_FILES = [
    "scripts/benchmark/density_benchmark.py",
    "scripts/benchmark/density_benchmark_selftests.py",
    "scripts/benchmark/density_matrix.json",
    "scripts/benchmark/density_telemetry_schema.json",
]
_BS = chr(92)
_NBS = r"[^" + _BS + _BS + r"]"
_UNC = (_BS * 4) + _NBS + "+" + (_BS * 2) + _NBS + "+" + (_BS * 2)
ABS_PATH_PATTERN = re.compile(
    r"(?i)\b[a-z]" + chr(58) + _BS + _BS + r"|\b[a-z]" + chr(58) + r"/|" + _UNC
)


def _import_driver(root: Path) -> Any:
    path = root / "scripts" / "benchmark" / "density_benchmark.py"
    spec = importlib.util.spec_from_file_location("density_benchmark", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(root: Path, *args: str, cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    driver = root / "scripts" / "benchmark" / "density_benchmark.py"
    return subprocess.run(
        [sys.executable, str(driver), *args],
        capture_output=True, text=True, timeout=timeout, cwd=str(cwd or root),
    )


def _valid_telemetry(level_id: str, seed: int, killed: int, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "schema_version": "1.0",
        "scenario_id": level_id,
        "seed": seed,
        "started_at": "2026-08-20T00:00:00Z",
        "ended_at": "2026-08-20T00:01:00Z",
        "boot": {"ok": True, "fatal_count": 0, "alert_count": 0},
        "counters": {
            "spawned": killed, "alive": 0, "killed": killed,
            "duplicate_deaths": 0, "damage_events": killed * 4,
            "melee_hits": killed * 2, "crits": 2, "projectiles": 10,
            "triggers": 0, "player_moves": 50, "dashes": 4,
        },
        "perf": {"frames": 1800, "fps_avg": 60.0, "fps_min": 55.0, "fps_max": 62.0,
                 "frame_pacing_p95_ms": 17.5, "frame_pacing_p99_ms": 20.0,
                 "frame_pacing_max_ms": 25.0, "fps_p1": 40.0},
        "metrics": {
            "duration_seconds": 60.0,
            "frames": 1800,
            "frame_time": {"avg_ms": 16.667, "p95_ms": 17.5, "p99_ms": 20.0, "max_ms": 25.0},
            "fps": {"avg": 60.0, "min": 55.0, "p1": 40.0},
            "event_rate": {"events_total": killed * 7, "events_per_second": 2.0},
            "voice_budget": {"max_concurrent": 12, "over_budget_count": 0},
            "camera_budget": {
                "impulses_total": 120, "max_amplitude": 3.2, "max_offset": 2.8,
                "capped_amplitude_count": 4, "capped_offset_count": 0,
            },
        },
        "capture": {"screenshots": ["run_0001.png"], "video": None},
        "runtime": {"exit_code": 0, "in_game_result": "PASS", "notes": []},
        "proves": "fixture telemetry used by density benchmark self-tests",
        "not_proven": "nothing; synthetic fixture",
    }
    if extra:
        data.update(extra)
    return data


def _legacy_telemetry(level_id: str, seed: int, killed: int) -> dict[str, Any]:
    data = _valid_telemetry(level_id, seed, killed)
    data.pop("metrics")
    for key in ("frame_pacing_p99_ms", "frame_pacing_max_ms", "fps_p1"):
        data["perf"].pop(key, None)
    return data


# ---------------------------------------------------------------- test cases

def tc_matrix_parses(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    matrix = driver.load_matrix(root)
    errors = driver.matrix_contract_errors(matrix)
    ids = [level["id"] for level in matrix.get("levels", [])]
    if errors:
        return False, f"matrix contract errors: {errors}"
    if ids != EXPECTED_LEVEL_IDS:
        return False, f"expected {EXPECTED_LEVEL_IDS}, got {ids}"
    return True, f"{len(ids)} ladder levels, zero contract errors"


def tc_level_plan_counts(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    combat = driver.load_driver(root)
    matrix = driver.load_matrix(root)
    catalog = combat.read_json(root / combat.SCENARIOS_REL)
    expected = {"density_5": 5, "density_20": 20, "density_50": 50, "density_100": 100}
    for level_id, count in expected.items():
        level = driver.get_level(matrix, level_id)
        assert level is not None
        plan = combat.build_plan(level, int(level["default_seed"]), catalog)
        if plan["total_spawn"] != count:
            return False, f"{level_id}: plan total {plan['total_spawn']} != {count}"
    return True, "plan totals render 5/20/50/100 on-screen enemies exactly"


def tc_plan_determinism_same_seed(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    matrix = driver.load_matrix(root)
    level = driver.get_level(matrix, "density_50")
    assert level is not None
    seed = int(level["default_seed"])
    plan_a = driver.build_plan_from_level(root, driver.load_driver(root), level, seed)
    plan_b = driver.build_plan_from_level(root, driver.load_driver(root), level, seed)
    if plan_a["plan_sha256"] != plan_b["plan_sha256"]:
        return False, "same seed produced different plans"
    return True, f"same seed -> identical plan (sha {plan_a['plan_sha256'][:12]}...), total {plan_a['total_spawn']}"


def tc_plan_determinism_diff_seed(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    matrix = driver.load_matrix(root)
    level = driver.get_level(matrix, "density_100")
    assert level is not None
    seed = int(level["default_seed"])
    plan_a = driver.build_plan_from_level(root, driver.load_driver(root), level, seed)
    plan_b = driver.build_plan_from_level(root, driver.load_driver(root), level, seed + 1)
    if plan_a["plan_sha256"] == plan_b["plan_sha256"]:
        return False, "different seeds produced identical plans"
    return True, "different seed -> different plan"


def tc_plan_bounds(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    matrix = driver.load_matrix(root)
    level = driver.get_level(matrix, "density_100")
    assert level is not None
    plan = driver.build_plan_from_level(root, driver.load_driver(root), level, int(level["default_seed"]))
    origin = level["spawn"]["origin"]
    spread = float(level["spawn"]["spread"])
    for entry in plan["spawns"]:
        dx = entry["position"][0] - origin[0]
        dy = entry["position"][1] - origin[1]
        if abs(dx) > spread or abs(dy) > spread:
            return False, f"spawn {entry['order']} out of bounds: {entry['position']}"
    return True, "all spawn positions within declared spread"


def tc_thresholds_all_draft(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    matrix = driver.load_matrix(root)
    thresholds = matrix.get("thresholds", {})
    if not thresholds.get("draft"):
        return False, "thresholds block not marked draft"
    if "calibration_note" not in thresholds:
        return False, "thresholds block missing calibration_note"
    non_draft = [name for name, spec in thresholds.items()
                 if name not in ("draft", "calibration_note") and not spec.get("draft")]
    if non_draft:
        return False, f"thresholds not marked draft: {non_draft}"
    return True, "every threshold entry is draft with calibration note present"


def tc_entrance_reuse(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    matrix = driver.load_matrix(root)
    entrance = matrix.get("entrance", {})
    if entrance.get("routing") != "goto_test_level":
        return False, f"entrance routing must reuse goto_test_level, got {entrance.get('routing')!r}"
    if entrance.get("new_in_game_system") != "none":
        return False, "scaffold must declare zero new in-game systems"
    launcher = root / entrance.get("launcher_relative_path", "")
    if not launcher.is_file():
        return False, f"launcher not found at {entrance.get('launcher_relative_path')}"
    return True, "entrance reuses goto_test_level via the existing launcher; no new in-game system"


def tc_dry_run_skeleton(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    isolated = out_dir / "dry_run_skeleton"
    proc = _run(root, "run", "--scenario", "100", "--candidate", str(driver.__file__),
                "--dry-run", "--out-dir", str(isolated))
    if proc.returncode != driver.load_driver(root).EXIT_NOT_PROVEN:
        return False, f"expected exit NOT_PROVEN(3), got {proc.returncode}: {proc.stdout} {proc.stderr}"
    report_path = isolated / "reports" / "density_100_2026083004_NOT_PROVEN.json"
    if not report_path.is_file():
        return False, f"report skeleton not written: {report_path.name}"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for key in ("level", "seed", "plan", "candidate", "entrance", "timestamps", "metrics",
                "thresholds", "runtime", "telemetry", "assertions", "result", "proves", "not_proven"):
        if key not in report:
            return False, f"report skeleton missing contract field: {key}"
    if report["result"] != "NOT_PROVEN":
        return False, f"expected NOT_PROVEN skeleton, got {report['result']}"
    if not report["thresholds"]["draft"]:
        return False, "report thresholds must stay draft"
    return True, "dry-run skeleton: NOT_PROVEN exit 3, contract fields present, thresholds draft"


def tc_telemetry_pass(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    level_id, seed = "density_100", 2026083004
    telemetry = _valid_telemetry(level_id, seed, killed=100)
    telemetry_path = out_dir / "telemetry" / f"{level_id}_{seed}.json"
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    proc = _run(root, "run", "--scenario", "100", "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--telemetry", str(telemetry_path))
    if proc.returncode != driver.load_driver(root).EXIT_PASS:
        return False, f"expected exit PASS(0), got {proc.returncode}: {proc.stdout} {proc.stderr}"
    return True, "envelope telemetry killed=100 -> PASS (exit 0), thresholds informational"


def tc_telemetry_fail(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    level_id, seed = "density_100", 2026083004
    telemetry = _valid_telemetry(level_id, seed, killed=99)
    telemetry_path = out_dir / "telemetry" / f"{level_id}_{seed}.json"
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    proc = _run(root, "run", "--scenario", "100", "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--telemetry", str(telemetry_path))
    if proc.returncode != driver.load_driver(root).EXIT_FAIL:
        return False, f"expected exit FAIL(2), got {proc.returncode}: {proc.stdout} {proc.stderr}"
    return True, "telemetry killed=99 -> FAIL (exit 2)"


def tc_telemetry_invalid_not_proven(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    level_id, seed = "density_20", 2026083002
    telemetry = _valid_telemetry(level_id, seed, killed=20, extra={"counters": {}})
    telemetry_path = out_dir / "telemetry" / f"{level_id}_{seed}.json"
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    proc = _run(root, "run", "--scenario", "20", "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--telemetry", str(telemetry_path))
    if proc.returncode != driver.load_driver(root).EXIT_NOT_PROVEN:
        return False, f"expected exit NOT_PROVEN(3), got {proc.returncode}: {proc.stdout} {proc.stderr}"
    return True, "schema-invalid telemetry (empty counters) -> NOT_PROVEN (exit 3)"


def tc_metrics_exact_envelope(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    telemetry = _valid_telemetry("density_100", 2026083004, killed=100)
    metrics = driver.compute_metrics(telemetry)
    assert metrics is not None
    if not metrics["exact_envelope"]:
        return False, "expected exact envelope flag"
    if metrics["frame_time"]["avg_ms"] != 16.667:
        return False, f"frame_time avg_ms wrong: {metrics['frame_time']['avg_ms']}"
    if metrics["frame_time"]["p99_ms"] != 20.0:
        return False, f"frame_time p99 wrong: {metrics['frame_time']['p99_ms']}"
    if metrics["event_rate"]["derived"]:
        return False, "exact envelope must not be marked derived"
    if metrics["voice_budget"]["max_concurrent"] != 12:
        return False, f"voice gauge wrong: {metrics['voice_budget']['max_concurrent']}"
    if metrics["camera_budget"]["capped_amplitude_count"] != 4:
        return False, "camera gauge wrong"
    return True, "exact envelope metrics computed (frame-time p95/p99, fps p1, event-rate, voice/camera gauges)"


def tc_metrics_legacy_derived(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    telemetry = _legacy_telemetry("density_20", 2026083002, killed=20)
    metrics = driver.compute_metrics(telemetry)
    assert metrics is not None
    if metrics["exact_envelope"]:
        return False, "legacy telemetry must be marked non-envelope"
    if not metrics["event_rate"]["derived"]:
        return False, "legacy event rate must be derived from counters"
    expected_events = 20 * 4 + 20 * 2 + 2 + 10
    if metrics["event_rate"]["events_total"] != expected_events:
        return False, f"derived events total {metrics['event_rate']['events_total']} != {expected_events}"
    if metrics["frame_time"]["avg_ms"] != round(1000.0 / 60.0, 3):
        return False, f"derived frame_time avg wrong: {metrics['frame_time']['avg_ms']}"
    return True, "legacy telemetry -> derived metrics (event rate from counters, avg frame-time from fps)"


def tc_threshold_evaluation(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    matrix = driver.load_matrix(root)
    thresholds = matrix["thresholds"]
    telemetry = _valid_telemetry("density_100", 2026083004, killed=100)
    metrics = driver.compute_metrics(telemetry)
    assert metrics is not None
    evaluations = driver.evaluate_thresholds(metrics, thresholds)
    names = {item["name"] for item in evaluations}
    expected = {"frame_time_p95_ms", "frame_time_p99_ms", "fps_avg", "fps_p1",
                "voice_max_concurrent", "voice_over_budget_count",
                "camera_max_amplitude", "camera_max_offset", "camera_capped_ratio"}
    if names != expected:
        return False, f"threshold evaluations missing/extra: {names ^ expected}"
    for item in evaluations:
        if item["status"] != "pass":
            return False, f"fixture should pass every draft threshold: {item}"
    telemetry["metrics"]["voice_budget"]["max_concurrent"] = 20
    telemetry["metrics"]["camera_budget"]["capped_amplitude_count"] = 40
    metrics = driver.compute_metrics(telemetry)
    assert metrics is not None
    evaluations = driver.evaluate_thresholds(metrics, thresholds)
    by_name = {item["name"]: item["status"] for item in evaluations}
    if by_name["voice_max_concurrent"] != "fail" or by_name["camera_capped_ratio"] != "fail":
        return False, f"over-budget fixture must fail voice/camera thresholds: {by_name}"
    return True, "draft thresholds evaluate pass/fail but stay informational"


def tc_base_schema_compat(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    density_schema = driver.load_telemetry_schema(root)
    base_schema = driver.load_driver(root).load_telemetry_schema(root)
    missing_required = [key for key in base_schema.get("root_required", [])
                        if key not in density_schema.get("root_required", [])]
    missing_props = [key for key in base_schema.get("properties", {})
                     if key not in density_schema.get("properties", {})]
    if missing_required or missing_props:
        return False, f"density schema not a superset: required {missing_required}, props {missing_props}"
    telemetry = _valid_telemetry("density_100", 2026083004, killed=100)
    base_issues = driver.load_driver(root).validate_telemetry(telemetry, base_schema)
    density_issues = driver.load_driver(root).validate_telemetry(telemetry, density_schema)
    if base_issues or density_issues:
        return False, f"fixture must validate against both schemas: base {base_issues}, density {density_issues}"
    return True, "density telemetry schema is a superset of the combat schema; fixture valid under both"


def tc_usage_errors_nonzero(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    checks = [
        ("run", "--scenario", "does_not_exist"),
        ("describe", "--scenario", "does_not_exist"),
        ("plan", "--scenario", "does_not_exist"),
        ("run", "--scenario", "20"),
    ]
    for args in checks:
        proc = _run(root, *args, "--out-dir", str(out_dir))
        if proc.returncode == 0:
            return False, f"expected nonzero exit for {args}, got 0"
    return True, "unknown level / missing candidate -> nonzero exit codes"


def tc_repo_root_from_any_cwd(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    cwd = root / "tests" / "density_benchmark"
    cwd.mkdir(parents=True, exist_ok=True)
    proc = _run(root, "levels", cwd=cwd)
    if proc.returncode != 0:
        return False, f"levels from nested cwd failed: {proc.stderr}"
    if "density_100" not in proc.stdout:
        return False, "levels output missing expected level id"
    return True, "driver resolves repo root from nested cwd"


def tc_game_request_contract(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    level_id, seed = "density_50", 2026083003
    proc = _run(root, "run", "--scenario", "50", "--candidate", str(driver.__file__),
                "--seed", str(seed), "--out-dir", str(out_dir), "--dry-run")
    if proc.returncode != driver.load_driver(root).EXIT_NOT_PROVEN:
        return False, f"expected dry-run exit NOT_PROVEN, got {proc.returncode}"
    request_path = out_dir / "requests" / f"{level_id}_{seed}.json"
    if not request_path.is_file():
        return False, f"request file not written: {request_path.name}"
    payload = driver.read_json(request_path)
    game = payload.get("game_request")
    if not isinstance(game, dict):
        return False, "request payload missing 'game_request' object"
    if game.get("scenario_id") != level_id:
        return False, f"game_request.scenario_id mismatch: {game.get('scenario_id')!r}"
    plan = game.get("plan")
    if not isinstance(plan, list) or len(plan) != 50:
        return False, f"game_request.plan must flatten 50 spawns, got {type(plan).__name__} len {len(plan) if isinstance(plan, list) else '?'}"
    for entry in plan:
        for key in ("res", "x", "y", "count"):
            if key not in entry:
                return False, f"game_request.plan entry missing '{key}': {entry}"
        if not isinstance(entry["res"], str) or not entry["res"].startswith("res://"):
            return False, f"game_request.plan entry res invalid: {entry['res']!r}"
        if entry["count"] != 1:
            return False, f"game_request.plan entry count must be 1: {entry}"
    return True, "game_request reuses the existing ScenarioDirector contract with 50 flattened spawns"


def tc_no_mods_touched(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--", "mods/"],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        return False, f"git status failed: {proc.stderr}"
    if proc.stdout.strip():
        return False, f"mods/ must stay untouched by the scaffold, git status: {proc.stdout.strip()}"
    return True, "no mods/ changes introduced (no gameplay density values touched)"


def tc_abs_path_scan(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    hits: list[str] = []
    for relative in BENCHMARK_FILES:
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
    return True, "no drive-letter / UNC absolute paths in benchmark-owned files"


def tc_secret_scan(root: Path, driver: Any, out_dir: Path) -> tuple[bool, str]:
    patterns = ["script" + "_key", r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY",
                r"(?i)password\s*=\s*['\"][^'\"]+['\"]", "api" + "[_-]?" + "key"]
    hits: list[str] = []
    for relative in BENCHMARK_FILES:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            if re.search(pattern, text):
                hits.append(f"{relative}: {pattern}")
    if hits:
        return False, f"secret-like tokens found: {hits}"
    return True, "no secret-like tokens in benchmark-owned files"


TESTS: list[tuple[str, Callable[[Path, Any, Path], tuple[bool, str]]]] = [
    ("matrix_parses", tc_matrix_parses),
    ("level_plan_counts_5_20_50_100", tc_level_plan_counts),
    ("plan_determinism_same_seed", tc_plan_determinism_same_seed),
    ("plan_determinism_diff_seed", tc_plan_determinism_diff_seed),
    ("plan_positions_within_spread", tc_plan_bounds),
    ("thresholds_all_draft", tc_thresholds_all_draft),
    ("entrance_reuses_goto_test_level", tc_entrance_reuse),
    ("report_skeleton_dry_run", tc_dry_run_skeleton),
    ("telemetry_valid_pass", tc_telemetry_pass),
    ("telemetry_required_fail", tc_telemetry_fail),
    ("telemetry_invalid_not_proven", tc_telemetry_invalid_not_proven),
    ("metrics_exact_envelope", tc_metrics_exact_envelope),
    ("metrics_legacy_derived", tc_metrics_legacy_derived),
    ("threshold_evaluation_informational", tc_threshold_evaluation),
    ("base_schema_compat", tc_base_schema_compat),
    ("usage_errors_nonzero", tc_usage_errors_nonzero),
    ("repo_root_from_any_cwd", tc_repo_root_from_any_cwd),
    ("game_request_contract", tc_game_request_contract),
    ("no_mods_touched", tc_no_mods_touched),
    ("abs_path_scan_benchmark_files", tc_abs_path_scan),
    ("secret_scan_benchmark_files", tc_secret_scan),
]


def run_selfchecks(root: Path, args: Any) -> int:
    driver = _import_driver(root)
    out_dir = (args.out_dir or root / "10_logs" / "benchmark_selfcheck").resolve()
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
        "evidence_id": "B3-X3-density-benchmark-selfcheck",
        "task_id": "B3-X3",
        "ran_at": driver.load_driver(root).utc_now(),
        "repo_head_sha": driver.load_driver(root).git_head_sha(root),
        "branch": driver.load_driver(root).git_branch(root),
        "repo_root": "<repo_root>",
        "driver_sha256": driver.load_driver(root).sha256_file(root / "scripts" / "benchmark" / "density_benchmark.py"),
        "python_version": sys.version.split()[0],
        "tests": results,
        "summary": {"total": total, "passed": passed, "failed": total - passed},
        "result": "PASS" if all_ok else "FAIL",
        "proves": "the density benchmark scaffold parses its 5/20/50/100 pressure ladder, renders deterministic "
                  "seeded plans that reuse the existing game_request/ScenarioDirector contract, validates the "
                  "benchmark telemetry envelope (superset of the combat schema), derives metrics from legacy "
                  "telemetry, evaluates draft thresholds informationally, reuses goto_test_level for entrance, "
                  "keeps all thresholds draft, leaves mods/ untouched and carries no host-absolute paths or "
                  "secrets in benchmark-owned files",
        "not_proven": "in-game execution, real frame-time/FPS/event-rate/voice/camera measurements, threshold "
                      "calibration (needs VM runs with a benchmark-capable candidate), gameplay density changes",
    }
    evidence_path = (args.evidence or out_dir / "density_benchmark_selfcheck_evidence.json").resolve()
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"selfcheck evidence: {evidence_path}")
    print(f"summary: {passed}/{total} passed -> {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else driver.load_driver(root).EXIT_SELFTEST_FAIL


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--evidence", type=Path, default=None)
    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[1]
    raise SystemExit(run_selfchecks(repo_root, args))
