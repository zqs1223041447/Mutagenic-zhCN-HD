#!/usr/bin/env python3
"""B3-X3 Density Benchmark scaffold driver (baseline framework only).

Defines the four-level on-screen density pressure ladder (5/20/50/100) and
the metric/threshold envelope for future density experiments.  This driver is
a *framework*: it changes no gameplay density value and introduces no new
in-game system or bus.  Everything is repo-relative; no host absolute path.

Reuse (single source of truth):
  * plan rendering / seed determinism     -> scripts/validate/combat_harness.py build_plan
  * mob resources / scenario contract     -> scripts/validate/combat_scenarios.json
  * telemetry validation                  -> combat telemetry schema + density envelope
  * level entrance                        -> goto_test_level routing in
                                            scripts/validate/launch_harness_game.py
                                            (F10 key sequence, k5 ScenarioDirector consumes
                                            the game_request; no new game-side system)

    python scripts/benchmark/density_benchmark.py levels
    python scripts/benchmark/density_benchmark.py describe --scenario 50
    python scripts/benchmark/density_benchmark.py plan --scenario 100 --seed 2026083004
    python scripts/benchmark/density_benchmark.py run --scenario 100 --candidate <exe> --dry-run
    python scripts/benchmark/density_benchmark.py run --scenario 100 --candidate <exe> --apdata <vm_dir>
    python scripts/benchmark/density_benchmark.py run --scenario 100 --candidate <exe> --launch "<vm hook>"
    python scripts/benchmark/density_benchmark.py selftest

Exit codes (contract, mirrors combat_harness):
    0  PASS         every required assertion measured and satisfied
    1  SELFTEST_FAIL internal self-check assertion failed
    2  FAIL         at least one required assertion measured and violated
    3  NOT_PROVEN   runtime did not run / telemetry missing or invalid / a
                    required assertion field was not measured
    4  USAGE        bad arguments or bad scenario/candidate reference
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MATRIX_REL = "scripts/benchmark/density_matrix.json"
TELEMETRY_SCHEMA_REL = "scripts/benchmark/density_telemetry_schema.json"
COMBAT_HARNESS_REL = "scripts/validate/combat_harness.py"
COMBAT_CATALOG_REL = "scripts/validate/combat_scenarios.json"
LAUNCHER_REL = "scripts/validate/launch_harness_game.py"
LEVEL_ALIASES = {"5": "density_5", "20": "density_20", "50": "density_50", "100": "density_100"}
SCENARIO_PREFIX = "density_"
THRESHOLD_MAP = [
    ("frame_time_p95_ms", "frame_time.p95_ms", "max"),
    ("frame_time_p99_ms", "frame_time.p99_ms", "max"),
    ("fps_avg", "fps.avg", "min"),
    ("fps_p1", "fps.p1", "min"),
    ("voice_max_concurrent", "voice_budget.max_concurrent", "max"),
    ("voice_over_budget_count", "voice_budget.over_budget_count", "max"),
    ("camera_max_amplitude", "camera_budget.max_amplitude", "max"),
    ("camera_max_offset", "camera_budget.max_offset", "max"),
]


def _import_combat_driver(root: Path) -> Any:
    path = root / COMBAT_HARNESS_REL
    spec = importlib.util.spec_from_file_location("combat_harness", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"ERROR: combat harness not found at {COMBAT_HARNESS_REL}")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_driver(root: Path) -> Any:
    return _import_combat_driver(root)


def resolve_repo_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(script_dir), capture_output=True, text=True, timeout=15,
        )
        if proc.returncode == 0:
            root = Path(proc.stdout.strip()).resolve()
            if root.is_dir():
                return root
    except Exception:
        pass
    return script_dir.parents[1]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_matrix(root: Path) -> dict[str, Any]:
    return read_json(root / MATRIX_REL)


def load_telemetry_schema(root: Path) -> dict[str, Any]:
    return read_json(root / TELEMETRY_SCHEMA_REL)


def matrix_contract_errors(matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(matrix.get("levels"), list):
        return ["matrix missing levels list"]
    entrance = matrix.get("entrance", {})
    for key in ("routing", "launcher_relative_path", "new_in_game_system"):
        if key not in entrance:
            errors.append(f"entrance missing key: {key}")
    seen: set[str] = set()
    for level in matrix["levels"]:
        level_id = level.get("id")
        if level_id in seen:
            errors.append(f"duplicate level id: {level_id}")
        seen.add(level_id)
        for key in ("id", "label", "version", "summary", "default_seed", "duration_seconds",
                    "end_condition", "spawn", "player", "mob_composition", "metrics", "asserts",
                    "proves", "not_proven", "requires", "stress"):
            if key not in level:
                errors.append(f"level {level_id}: missing key {key}")
        total = sum(int(entry.get("count", 0)) for entry in level.get("mob_composition", []))
        if level.get("label") and str(total) != str(level.get("label")):
            errors.append(f"level {level_id}: composition total {total} != label {level.get('label')}")
        for idx, assertion in enumerate(level.get("asserts", [])):
            for key in ("label", "field", "op", "value", "capability"):
                if key not in assertion:
                    errors.append(f"level {level_id}.asserts[{idx}]: missing key {key}")
        if not level.get("stress"):
            errors.append(f"level {level_id}: every ladder level must be marked stress")
    thresholds = matrix.get("thresholds", {})
    if not thresholds.get("draft"):
        errors.append("thresholds must be marked draft until real data calibrates them")
    for name, spec in thresholds.items():
        if name in ("draft", "calibration_note"):
            continue
        if not isinstance(spec, dict) or not spec.get("draft"):
            errors.append(f"threshold {name}: must be marked draft")
    return errors


def normalize_scenario_id(raw: str) -> str:
    value = str(raw).strip()
    if value in LEVEL_ALIASES:
        return LEVEL_ALIASES[value]
    if value.startswith(SCENARIO_PREFIX) and value[len(SCENARIO_PREFIX):] in LEVEL_ALIASES:
        return value
    raise SystemExit(f"ERROR: unknown level '{raw}'. Use 5|20|50|100 or density_5/20/50/100.")


def get_level(matrix: dict[str, Any], level_id: str) -> dict[str, Any] | None:
    for level in matrix.get("levels", []):
        if level["id"] == level_id:
            return level
    return None


def get_path(obj: Any, dotted: str) -> Any:
    current = obj
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def wall_duration(telemetry: dict[str, Any]) -> float | None:
    try:
        start = datetime.fromisoformat(telemetry.get("started_at", "").replace("Z", "+00:00"))
        end = datetime.fromisoformat(telemetry.get("ended_at", "").replace("Z", "+00:00"))
        delta = (end - start).total_seconds()
        return round(delta, 3) if delta > 0 else None
    except Exception:
        return None


def compute_metrics(telemetry: dict[str, Any] | None) -> dict[str, Any] | None:
    if telemetry is None:
        return None
    envelope = telemetry.get("metrics")
    envelope = envelope if isinstance(envelope, dict) else {}
    perf = telemetry.get("perf") if isinstance(telemetry.get("perf"), dict) else {}
    counters = telemetry.get("counters") if isinstance(telemetry.get("counters"), dict) else {}
    exact = bool(envelope)
    duration = envelope.get("duration_seconds")
    if not isinstance(duration, (int, float)) or duration <= 0:
        duration = wall_duration(telemetry)
    fps_avg = perf.get("fps_avg")
    frame_time_raw = envelope.get("frame_time") if isinstance(envelope.get("frame_time"), dict) else None
    fps_raw = envelope.get("fps") if isinstance(envelope.get("fps"), dict) else None
    frame_time = {
        "avg_ms": (
            frame_time_raw.get("avg_ms") if frame_time_raw
            else (round(1000.0 / fps_avg, 3) if isinstance(fps_avg, (int, float)) and fps_avg > 0 else None)
        ),
        "p95_ms": frame_time_raw.get("p95_ms") if frame_time_raw else perf.get("frame_pacing_p95_ms"),
        "p99_ms": frame_time_raw.get("p99_ms") if frame_time_raw else perf.get("frame_pacing_p99_ms"),
        "max_ms": frame_time_raw.get("max_ms") if frame_time_raw else perf.get("frame_pacing_max_ms"),
    }
    fps = {
        "avg": fps_raw.get("avg") if fps_raw else fps_avg,
        "min": fps_raw.get("min") if fps_raw else perf.get("fps_min"),
        "p1": fps_raw.get("p1") if fps_raw else perf.get("fps_p1"),
    }
    event_rate_raw = envelope.get("event_rate") if isinstance(envelope.get("event_rate"), dict) else None
    event_fields = ("damage_events", "melee_hits", "crits", "projectiles", "triggers")
    if isinstance(event_rate_raw, dict) and isinstance(event_rate_raw.get("events_total"), int):
        events_total = event_rate_raw["events_total"]
        event_rate: dict[str, Any] = {
            "events_total": events_total,
            "events_per_second": round(events_total / duration, 3) if duration and duration > 0 else None,
            "derived": False,
        }
    else:
        events_total = sum(int(counters.get(key, 0) or 0) for key in event_fields)
        event_rate = {
            "events_total": events_total,
            "events_per_second": round(events_total / duration, 3) if duration and duration > 0 else None,
            "derived": True,
        }
    voice_raw = envelope.get("voice_budget") if isinstance(envelope.get("voice_budget"), dict) else None
    camera_raw = envelope.get("camera_budget") if isinstance(envelope.get("camera_budget"), dict) else None
    return {
        "duration_seconds": duration,
        "frames": envelope.get("frames") if envelope.get("frames") is not None else perf.get("frames"),
        "frame_time": frame_time,
        "fps": fps,
        "event_rate": event_rate,
        "voice_budget": {
            "max_concurrent": voice_raw.get("max_concurrent") if voice_raw else None,
            "over_budget_count": voice_raw.get("over_budget_count") if voice_raw else None,
        },
        "camera_budget": {
            "impulses_total": camera_raw.get("impulses_total") if camera_raw else None,
            "max_amplitude": camera_raw.get("max_amplitude") if camera_raw else None,
            "max_offset": camera_raw.get("max_offset") if camera_raw else None,
            "capped_amplitude_count": camera_raw.get("capped_amplitude_count") if camera_raw else None,
            "capped_offset_count": camera_raw.get("capped_offset_count") if camera_raw else None,
        },
        "exact_envelope": exact,
    }


def evaluate_thresholds(metrics: dict[str, Any] | None, thresholds: dict[str, Any]) -> list[dict[str, Any]]:
    if metrics is None:
        return []
    results: list[dict[str, Any]] = []
    for name, path, direction in THRESHOLD_MAP:
        spec = thresholds.get(name)
        if not isinstance(spec, dict):
            continue
        value = get_path(metrics, path)
        expected = spec.get("max") if direction == "max" else spec.get("min")
        if expected is None:
            continue
        if value is None:
            results.append({
                "name": name, "path": path, "draft": bool(spec.get("draft", True)),
                "measured": False, "actual": None, "expected": expected, "status": "not_measured",
            })
            continue
        passed = value <= expected if direction == "max" else value >= expected
        results.append({
            "name": name, "path": path, "draft": bool(spec.get("draft", True)),
            "measured": True, "actual": value, "expected": expected, "status": "pass" if passed else "fail",
        })
    ratio_spec = thresholds.get("camera_capped_ratio")
    if isinstance(ratio_spec, dict):
        impulses = metrics["camera_budget"].get("impulses_total")
        capped = metrics["camera_budget"].get("capped_amplitude_count")
        expected = ratio_spec.get("max")
        if expected is not None and isinstance(impulses, (int, float)) and isinstance(capped, (int, float)) \
                and impulses > 0:
            ratio = round(capped / impulses, 4)
            results.append({
                "name": "camera_capped_ratio", "path": "camera_budget.capped_amplitude_count/impulses_total",
                "draft": bool(ratio_spec.get("draft", True)), "measured": True, "actual": ratio,
                "expected": expected, "status": "pass" if ratio <= expected else "fail",
            })
    return results


def build_plan_from_level(root: Path, driver: Any, level: dict[str, Any], seed: int) -> dict[str, Any]:
    catalog = read_json(root / COMBAT_CATALOG_REL)
    return driver.build_plan(level, seed, catalog)


def game_request_from_plan(driver: Any, level: dict[str, Any], seed: int, plan: dict[str, Any],
                           catalog: dict[str, Any]) -> dict[str, Any]:
    game_plan: list[dict[str, Any]] = []
    for spawn in plan.get("spawns", []):
        resource = spawn.get("resource")
        if resource is None:
            raise SystemExit(
                f"ERROR: plan spawn {spawn.get('order')} has no resource; "
                f"mob {spawn.get('mob')!r} is missing from the combat catalog mob_resources"
            )
        game_plan.append({
            "res": resource,
            "x": float(spawn["position"][0]),
            "y": float(spawn["position"][1]),
            "count": 1,
        })
    return {
        "schema_version": driver.TELEMETRY_SCHEMA_VERSION,
        "scenario_id": level["id"],
        "seed": seed,
        "duration": float(level.get("duration_seconds", 60.0)),
        "plan": game_plan,
    }


def default_launch_command(root: Path, driver: Any, request_path: Path, telemetry_path: Path,
                           candidate_path: str, apdata: str) -> str:
    command = [
        sys.executable,
        str(root / LAUNCHER_REL),
        "--request", str(request_path),
        "--candidate", candidate_path,
        "--expected-telemetry", str(telemetry_path),
        "--apdata", apdata,
    ]
    return shlex.join(command)


def levels_command(root: Path) -> int:
    matrix = load_matrix(root)
    errors = matrix_contract_errors(matrix)
    if errors:
        print("ERROR: matrix contract invalid:")
        for error in errors:
            print(f"  - {error}")
        return 4
    for level in matrix["levels"]:
        print(f"{level['id']:<10} {level['version']}  stress={str(level.get('stress')).lower():5s}  "
              f"{level.get('summary', '')}")
    return 0


def describe_command(root: Path, raw: str) -> int:
    level_id = normalize_scenario_id(raw)
    level = get_level(load_matrix(root), level_id)
    if level is None:
        raise SystemExit(f"ERROR: unknown level '{level_id}'. Use 'levels' to list ids.")
    print(json.dumps(level, ensure_ascii=False, indent=2))
    return 0


def plan_command(root: Path, driver: Any, raw: str, seed: int | None, raw_json: bool = False) -> int:
    matrix = load_matrix(root)
    level_id = normalize_scenario_id(raw)
    level = get_level(matrix, level_id)
    if level is None:
        raise SystemExit(f"ERROR: unknown level '{level_id}'. Use 'levels' to list ids.")
    seed = seed if seed is not None else int(level["default_seed"])
    plan = build_plan_from_level(root, driver, level, seed)
    print(json.dumps(plan, ensure_ascii=False, indent=2 if not raw_json else None))
    return 0


def run_command(root: Path, driver: Any, args: argparse.Namespace) -> int:
    matrix = load_matrix(root)
    level_id = normalize_scenario_id(args.scenario)
    level = get_level(matrix, level_id)
    if level is None:
        raise SystemExit(f"ERROR: unknown level '{level_id}'. Use 'levels' to list ids.")
    seed = args.seed if args.seed is not None else int(level["default_seed"])
    plan = build_plan_from_level(root, driver, level, seed)
    candidate = driver.resolve_candidate(args.candidate, root)
    if not args.candidate and not args.dry_run:
        raise SystemExit("ERROR: --candidate is required unless --dry-run is used.")
    if args.candidate and args.dry_run:
        print(f"[dry-run] candidate={args.candidate} sha={candidate['sha256']}")

    out_dir = (args.out_dir or root / "10_logs" / "benchmark").resolve()
    request_dir = out_dir / "requests"
    telemetry_dir = out_dir / "telemetry"
    report_dir = out_dir / "reports"
    for directory in (request_dir, telemetry_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)
    expected_telemetry = (args.telemetry or telemetry_dir / f"{level_id}_{seed}.json").resolve()
    catalog = read_json(root / COMBAT_CATALOG_REL)
    game_request = game_request_from_plan(driver, level, seed, plan, catalog)
    request = {
        "schema_version": driver.TELEMETRY_SCHEMA_VERSION,
        "level": level,
        "seed": seed,
        "plan": plan,
        "mob_resources": catalog.get("mob_resources", {}),
        "expected_telemetry_path": str(expected_telemetry),
        "contract": "reuse k5-combat-harness ScenarioDirector.gd: it reads 'game_request' "
                    "(scenario_id/seed/duration/plan with res+x+y+count), seeds Godot RNG with 'seed', "
                    "spawns per the plan, then writes telemetry JSON conforming to "
                    "combat_telemetry_schema.json (optionally with the density benchmark envelope) to "
                    "'expected_telemetry_path'. Entrance: goto_test_level via the existing launcher "
                    "key sequence; no new in-game system.",
        "game_request": game_request,
    }
    request_path = request_dir / f"{level_id}_{seed}.json"
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    runtime_info: dict[str, Any] = {
        "ran": False, "started_at": driver.utc_now(), "launcher": args.launch,
        "launcher_returncode": None, "modset_explicit": args.modset,
    }
    launch = args.launch
    if args.candidate and not args.dry_run and launch is None and args.apdata:
        launch = default_launch_command(root, driver, request_path, expected_telemetry,
                                        args.candidate, args.apdata)
        runtime_info["launcher"] = launch
    telemetry: dict[str, Any] | None = None
    if launch:
        try:
            proc = subprocess.run(
                shlex.split(launch), cwd=str(root),
                capture_output=True, text=True, timeout=args.launch_timeout,
            )
            runtime_info["ran"] = True
            runtime_info["launcher_returncode"] = proc.returncode
            if proc.stdout:
                print(f"[launcher stdout]\n{proc.stdout}")
            if proc.stderr:
                print(f"[launcher stderr]\n{proc.stderr}")
            deadline = time.monotonic() + max(10, args.launch_timeout // 4)
            while time.monotonic() < deadline:
                if expected_telemetry.is_file():
                    break
                time.sleep(1.0)
        except subprocess.TimeoutExpired:
            print(f"ERROR: launcher timed out after {args.launch_timeout}s; treating run as NOT_PROVEN.")
    else:
        print(f"[no launcher] expected telemetry at: {expected_telemetry}")

    if expected_telemetry.is_file():
        try:
            telemetry = read_json(expected_telemetry)
        except Exception as exc:
            print(f"ERROR: telemetry file not parseable: {exc}")
    elif args.telemetry:
        print(f"WARNING: telemetry file not found: {expected_telemetry}")

    telemetry_valid = False
    telemetry_issues: list[str] = []
    if telemetry is not None:
        telemetry_issues = driver.validate_telemetry(telemetry, load_telemetry_schema(root))
        telemetry_issues.extend(driver.telemetry_mismatch_issues(telemetry, level_id, seed))
        telemetry_valid = not telemetry_issues
    usable = telemetry is not None and telemetry_valid

    assertions = driver.evaluate_asserts(level, telemetry if usable else None)
    result = driver.verdict(assertions) if usable else "NOT_PROVEN"
    metrics = compute_metrics(telemetry if usable else None)
    thresholds = evaluate_thresholds(metrics, matrix.get("thresholds", {}))
    threshold_statuses = {item["name"]: item["status"] for item in thresholds}

    out_paths = {
        "request": str(request_path),
        "telemetry": str(expected_telemetry) if expected_telemetry.is_file() else None,
        "plan": None,
        "report": str(report_dir / f"{level_id}_{seed}_{result}.json"),
    }
    payload: dict[str, Any] = {
        "event": "B3-X3 density benchmark level run (baseline framework)",
        "task_id": "B3-X3",
        "branch": driver.git_branch(root),
        "repo_head_sha": driver.git_head_sha(root),
        "schema_version": driver.TELEMETRY_SCHEMA_VERSION,
        "level": {
            "id": level["id"],
            "label": level.get("label"),
            "version": level.get("version"),
            "summary": level.get("summary"),
        },
        "seed": seed,
        "plan": {
            "plan_version": plan.get("plan_version"),
            "plan_sha256": plan.get("plan_sha256"),
            "total_spawn": plan.get("total_spawn"),
        },
        "candidate": candidate,
        "modset": driver.resolve_modset(root, runtime_info.get("modset_explicit")),
        "entrance": matrix.get("entrance"),
        "timestamps": {"started_at": runtime_info["started_at"], "ended_at": driver.utc_now()},
        "metrics": metrics,
        "thresholds": {
            "draft": bool(matrix.get("thresholds", {}).get("draft", True)),
            "calibration_note": matrix.get("thresholds", {}).get("calibration_note"),
            "evaluations": thresholds,
            "summary": threshold_statuses,
        },
        "runtime": {
            "ran": runtime_info.get("ran", False),
            "in_game_exit_code": telemetry.get("runtime", {}).get("exit_code") if telemetry else None,
            "in_game_result": telemetry.get("runtime", {}).get("in_game_result") if telemetry else None,
            "launcher": runtime_info.get("launcher"),
            "launcher_returncode": runtime_info.get("launcher_returncode"),
        },
        "telemetry": {
            "provided": telemetry is not None,
            "valid": telemetry_valid,
            "issues": telemetry_issues,
        },
        "assertions": assertions,
        "result": result,
        "exit_code": {
            "PASS": driver.EXIT_PASS, "FAIL": driver.EXIT_FAIL, "NOT_PROVEN": driver.EXIT_NOT_PROVEN,
        }[result],
        "proves": [
            f"level '{level_id}' definition parses, its seeded spawn plan is deterministic under seed {seed} "
            "and the request reuses the existing game_request/ScenarioDirector contract (no new in-game system)",
            "candidate identity resolved when a candidate was provided",
            "metric envelope computed and draft thresholds evaluated without touching any gameplay value",
            level.get("proves", ""),
        ],
        "not_proven": [
            "in-game runtime verdict" if not usable else "nothing: runtime executed",
            "real density telemetry (frame-time p95/p99, voice/camera budget gauges) without a "
            "benchmark-capable candidate on the VM",
            "threshold calibration: all thresholds are drafts and never gate PASS/FAIL until real data lands",
            level.get("not_proven", ""),
        ],
        "evidence_paths": out_paths,
    }
    if telemetry and telemetry.get("proves"):
        payload["proves"].insert(0, telemetry["proves"])
    if telemetry and telemetry.get("not_proven"):
        payload["not_proven"].insert(0, telemetry["not_proven"])
    report_path = report_dir / f"{level_id}_{seed}_{result}.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["evidence_paths"]["report"] = str(report_path)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
    print(f"level: {level_id}  seed: {seed}  plan_sha256: {plan['plan_sha256']}")
    print(f"candidate: {candidate.get('sha256') or 'N/A'}  result: {result}")
    print(f"telemetry: {'valid' if telemetry_valid else 'missing-or-invalid'} "
          f"({len(telemetry_issues)} issue(s))")
    for item in assertions:
        mark = {"pass": "PASS", "fail": "FAIL", "not_measured": "N/A"}[item["status"]]
        cap = "req" if item["capability"] == "required" else "opt"
        print(f"  [{cap}] {mark} {item['label']:32s} expected {item['op']} {item['expected']} "
              f"actual {item['actual'] if item['measured'] else '<not measured>'}")
    if metrics:
        print(f"metrics: duration={metrics['duration_seconds']}s frames={metrics['frames']} "
              f"exact_envelope={metrics['exact_envelope']}")
        print(f"  frame_time(ms): avg={metrics['frame_time']['avg_ms']} "
              f"p95={metrics['frame_time']['p95_ms']} p99={metrics['frame_time']['p99_ms']}")
        print(f"  fps: avg={metrics['fps']['avg']} min={metrics['fps']['min']} "
              f"p1={metrics['fps']['p1']}")
        print(f"  event_rate: {metrics['event_rate']['events_per_second']}/s "
              f"({metrics['event_rate']['events_total']} events, derived={metrics['event_rate']['derived']})")
        print(f"  voice_budget: max_concurrent={metrics['voice_budget']['max_concurrent']} "
              f"over_budget={metrics['voice_budget']['over_budget_count']}")
        print(f"  camera_budget: max_amplitude={metrics['camera_budget']['max_amplitude']} "
              f"capped={metrics['camera_budget']['capped_amplitude_count']}/"
              f"{metrics['camera_budget']['impulses_total']}")
    if thresholds:
        print(f"thresholds (draft, informational only): "
              + ", ".join(f"{item['name']}={item['status']}" for item in thresholds))
    print(f"proves: {payload['proves'][0]}")
    print(f"report: {report_path}")
    return {"PASS": driver.EXIT_PASS, "FAIL": driver.EXIT_FAIL, "NOT_PROVEN": driver.EXIT_NOT_PROVEN}[result]


def selfcheck_command(root: Path, args: argparse.Namespace) -> int:
    try:
        from density_benchmark_selftests import run_selfchecks
    except ImportError:
        selftests = root / "scripts" / "benchmark" / "density_benchmark_selftests.py"
        spec = importlib.util.spec_from_file_location("density_benchmark_selftests", selftests)
        if spec is None or spec.loader is None:
            raise SystemExit("ERROR: density_benchmark_selftests.py not found next to the driver.")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        run_selfchecks = module.run_selfchecks
    return run_selfchecks(root, args)


def main(argv: list[str] | None = None) -> int:
    root = resolve_repo_root()
    driver = _import_combat_driver(root)

    class _Parser(argparse.ArgumentParser):
        def error(self, message: str) -> None:
            self.print_usage(sys.stderr)
            raise SystemExit(4)

    parser = _Parser(prog="density_benchmark.py", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("levels", help="list pressure ladder levels from the matrix")

    p_describe = sub.add_parser("describe", help="print one level definition")
    p_describe.add_argument("--scenario", required=True)

    p_plan = sub.add_parser("plan", help="render the deterministic seeded spawn plan")
    p_plan.add_argument("--scenario", required=True)
    p_plan.add_argument("--seed", type=int, default=None)
    p_plan.add_argument("--raw", action="store_true", help="compact single-line JSON output")

    p_run = sub.add_parser("run", help="run a density level against a candidate and emit an evidence report")
    p_run.add_argument("--scenario", required=True)
    p_run.add_argument("--candidate", default=None)
    p_run.add_argument("--seed", type=int, default=None)
    p_run.add_argument("--out-dir", type=Path, default=None)
    p_run.add_argument("--telemetry", type=Path, default=None)
    p_run.add_argument("--launch", default=None, help="shell command that boots the game/vm")
    p_run.add_argument("--launch-timeout", type=int, default=600)
    p_run.add_argument("--apdata", default=None,
                       help="VM deployment APPDATA dir for the default launcher hook")
    p_run.add_argument("--modset", default=None)
    p_run.add_argument("--dry-run", action="store_true",
                       help="render plan/request/report skeleton without launching")
    p_run.add_argument("--json", action="store_true", help="print the structured JSON summary to stdout")

    p_selfcheck = sub.add_parser("selftest", help="run offline self-tests and write evidence")
    p_selfcheck.add_argument("--out-dir", type=Path, default=None)
    p_selfcheck.add_argument("--evidence", type=Path, default=None)

    args = parser.parse_args(argv)
    if args.command == "run":
        return run_command(root, driver, args)
    if args.command == "levels":
        return levels_command(root)
    if args.command == "describe":
        return describe_command(root, args.scenario)
    if args.command == "plan":
        return plan_command(root, driver, args.scenario, args.seed, args.raw)
    if args.command == "selftest":
        return selfcheck_command(root, args)
    parser.error(f"unknown command: {args.command}")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
