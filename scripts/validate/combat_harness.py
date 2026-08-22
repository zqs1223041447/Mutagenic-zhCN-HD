#!/usr/bin/env python3
"""B1-X5 Combat Test Harness - deterministic scenario driver.

One command, one intent.  Everything is repo-relative; no host absolute path
is hard-coded.  The in-game side (k5-combat-harness MOD / ScenarioDirector.gd)
is a separate declarative artifact; this driver is the host-side contract
keeper: scenario parsing, seeded spawn plan, telemetry validation, assert
evaluation and evidence report.

    python scripts/validate/combat_harness.py scenarios
    python scripts/validate/combat_harness.py describe --scenario cluster_kill_20
    python scripts/validate/combat_harness.py plan --scenario cluster_kill_20 --seed 2026082005
    python scripts/validate/combat_harness.py run --scenario cluster_kill_20 --candidate <exe>
    python scripts/validate/combat_harness.py run --scenario cluster_kill_20 --candidate <exe> --launch "run_in_vm.ps1 -Scenario cluster_kill_20"
    python scripts/validate/combat_harness.py selfcheck

Exit codes (contract):
    0  PASS         every required assertion measured and satisfied
    1  SELFTEST_FAIL internal self-check assertion failed
    2  FAIL         at least one required assertion measured and violated
    3  NOT_PROVEN   runtime did not run / telemetry missing or invalid / a
                    required assertion field was not measured
    4  USAGE        bad arguments or bad scenario/candidate reference
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TELEMETRY_SCHEMA_VERSION = "1.0"
PLAN_VERSION = 1
EXIT_PASS = 0
EXIT_SELFTEST_FAIL = 1
EXIT_FAIL = 2
EXIT_NOT_PROVEN = 3
EXIT_USAGE = 4
SCENARIOS_REL = "scripts/validate/combat_scenarios.json"
TELEMETRY_SCHEMA_REL = "scripts/validate/combat_telemetry_schema.json"
OPS = {"==", "!=", ">=", "<=", ">", "<"}
CAPABILITIES = {"required", "optional"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class ExitCodeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE, f"ERROR: {message}\n")


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


def git_head_sha(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=15,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return "unknown"


def git_branch(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(root), capture_output=True, text=True, timeout=15,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return "detached-or-unknown"


def load_catalog(root: Path) -> dict[str, Any]:
    return read_json(root / SCENARIOS_REL)


def load_telemetry_schema(root: Path) -> dict[str, Any]:
    return read_json(root / TELEMETRY_SCHEMA_REL)


def scenario_contract_errors(scenario: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_keys = (
        "id", "version", "summary", "default_seed", "duration_seconds",
        "end_condition", "spawn", "mob_composition", "asserts",
        "proves", "not_proven", "requires", "stress",
    )
    for key in required_keys:
        if key not in scenario:
            errors.append(f"scenario missing key: {key}")
    if errors:
        return errors
    id_value = scenario["id"]
    if not isinstance(scenario["default_seed"], int):
        errors.append(f"{id_value}: default_seed must be int")
    for idx, assertion in enumerate(scenario["asserts"]):
        for key in ("label", "field", "op", "value", "capability"):
            if key not in assertion:
                errors.append(f"{id_value}.asserts[{idx}]: missing key {key}")
        op = assertion.get("op")
        if op not in OPS:
            errors.append(f"{id_value}.asserts[{idx}]: unknown op {op!r}")
        capability = assertion.get("capability")
        if capability not in CAPABILITIES:
            errors.append(f"{id_value}.asserts[{idx}]: unknown capability {capability!r}")
    for entry in scenario["mob_composition"]:
        if "mob" not in entry or "count" not in entry:
            errors.append(f"{id_value}: composition entry must have mob and count")
    return errors


def all_scenario_errors(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for scenario in catalog.get("scenarios", []):
        if scenario["id"] in seen:
            errors.append(f"duplicate scenario id: {scenario['id']}")
        seen.add(scenario["id"])
        errors.extend(scenario_contract_errors(scenario))
    return errors


def get_scenario(catalog: dict[str, Any], scenario_id: str) -> dict[str, Any] | None:
    for scenario in catalog.get("scenarios", []):
        if scenario["id"] == scenario_id:
            return scenario
    return None


def build_plan(scenario: dict[str, Any], seed: int, catalog: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(seed)
    origin = scenario["spawn"].get("origin", [0.0, 0.0])
    origin_x, origin_y = float(origin[0]), float(origin[1])
    spread = float(scenario["spawn"].get("spread", 200.0))
    mob_resources = catalog.get("mob_resources", {})
    spawns: list[dict[str, Any]] = []
    order = 0
    for entry in scenario["mob_composition"]:
        mob_id = entry["mob"]
        for index in range(int(entry["count"])):
            order += 1
            if mob_id == "random":
                chosen = rng.choice(sorted(mob_resources.keys()))
            else:
                chosen = mob_id
            spawns.append({
                "order": order,
                "mob": chosen,
                "resource": mob_resources.get(chosen),
                "count_index": index,
                "position": [
                    round(origin_x + (rng.random() * 2.0 - 1.0) * spread, 1),
                    round(origin_y + (rng.random() * 2.0 - 1.0) * spread, 1),
                ],
                "elite": rng.random() < 0.05,
                "magic": rng.random() < 0.1,
            })
    plan: dict[str, Any] = {
        "plan_version": PLAN_VERSION,
        "scenario_id": scenario["id"],
        "seed": seed,
        "total_spawn": len(spawns),
        "spawns": spawns,
    }
    plan["plan_sha256"] = sha256_bytes(canonical_json(plan).encode("utf-8"))
    return plan


def get_path(obj: Any, dotted: str) -> Any:
    current = obj
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def compare(actual: Any, op: str, expected: Any) -> bool:
    try:
        if op == "==":
            return actual == expected
        if op == "!=":
            return actual != expected
        if op == ">=":
            return actual >= expected
        if op == "<=":
            return actual <= expected
        if op == ">":
            return actual > expected
        if op == "<":
            return actual < expected
    except TypeError:
        return False
    return False


def validate_telemetry(telemetry: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(telemetry, dict):
        return ["telemetry is not a JSON object"]
    for key in schema.get("root_required", []):
        if key not in telemetry:
            issues.append(f"telemetry missing required root field: {key}")
    props = schema.get("properties", {})
    for key, spec in props.items():
        if key not in telemetry:
            continue
        value = telemetry[key]
        expected_type = spec.get("type")
        if expected_type == "integer" and not isinstance(value, int):
            issues.append(f"telemetry.{key}: expected integer, got {type(value).__name__}")
        elif expected_type == "number" and not isinstance(value, (int, float)):
            issues.append(f"telemetry.{key}: expected number, got {type(value).__name__}")
        elif expected_type == "boolean" and not isinstance(value, bool):
            issues.append(f"telemetry.{key}: expected boolean, got {type(value).__name__}")
        elif expected_type == "string" and not isinstance(value, str):
            issues.append(f"telemetry.{key}: expected string, got {type(value).__name__}")
        elif expected_type == "array" and not isinstance(value, list):
            issues.append(f"telemetry.{key}: expected array, got {type(value).__name__}")
        elif expected_type == "object":
            if not isinstance(value, dict):
                issues.append(f"telemetry.{key}: expected object, got {type(value).__name__}")
            else:
                for nested in spec.get("required", []):
                    if nested not in value:
                        issues.append(f"telemetry.{key}: missing required nested field: {nested}")
        minimum = spec.get("minimum")
        if minimum is not None and isinstance(value, (int, float)) and value < minimum:
            issues.append(f"telemetry.{key}: value {value} below minimum {minimum}")
    return issues


def evaluate_asserts(scenario: dict[str, Any], telemetry: dict[str, Any] | None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for assertion in scenario["asserts"]:
        actual = get_path(telemetry, assertion["field"]) if telemetry else None
        measured = actual is not None
        if measured:
            passed = compare(actual, assertion["op"], assertion["value"])
            status = "pass" if passed else "fail"
        else:
            passed = None
            status = "not_measured"
        results.append({
            "label": assertion["label"],
            "field": assertion["field"],
            "op": assertion["op"],
            "expected": assertion["value"],
            "actual": actual,
            "capability": assertion["capability"],
            "measured": measured,
            "passed": passed,
            "status": status,
        })
    return results


def verdict(assertions: list[dict[str, Any]]) -> str:
    for item in assertions:
        if item["capability"] == "required" and item["status"] == "fail":
            return "FAIL"
    if all(item["capability"] != "required" or item["status"] == "pass" for item in assertions):
        return "PASS"
    return "NOT_PROVEN"


def resolve_candidate(candidate_path: str | None, root: Path) -> dict[str, Any]:
    if not candidate_path:
        return {"provided": False, "path": None, "sha256": None, "exists": None}
    path = Path(candidate_path).resolve()
    info: dict[str, Any] = {
        "provided": True,
        "path": candidate_path,
        "sha256": sha256_file(path) if path.is_file() else None,
        "exists": path.is_file(),
    }
    try:
        resolved = path.resolve()
        info["path_repo_relative"] = str(resolved.relative_to(root)).replace("\\", "/")
    except ValueError:
        info["path_repo_relative"] = None
    return info


def resolve_modset(root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    lock = root / "modset.lock.json"
    if lock.is_file():
        try:
            return json.loads(lock.read_text(encoding="utf-8")).get("id", "lock-present")
        except Exception:
            return "lock-present-unparsed"
    return "none"


def telemetry_mismatch_issues(telemetry: dict[str, Any], scenario_id: str, seed: int) -> list[str]:
    issues: list[str] = []
    if telemetry.get("scenario_id") != scenario_id:
        issues.append(f"telemetry.scenario_id mismatch: got {telemetry.get('scenario_id')!r}, expected {scenario_id!r}")
    if telemetry.get("seed") != seed:
        issues.append(f"telemetry.seed mismatch: got {telemetry.get('seed')!r}, expected {seed!r}")
    if telemetry.get("schema_version") != TELEMETRY_SCHEMA_VERSION:
        issues.append(
            f"telemetry.schema_version mismatch: got {telemetry.get('schema_version')!r}, "
            f"expected {TELEMETRY_SCHEMA_VERSION!r}"
        )
    return issues


def make_report(
    root: Path, scenario: dict[str, Any], seed: int, plan: dict[str, Any],
    candidate: dict[str, Any], telemetry: dict[str, Any] | None,
    telemetry_valid: bool, telemetry_issues: list[str], assertions: list[dict[str, Any]],
    result: str, runtime_info: dict[str, Any], out_paths: dict[str, str],
) -> dict[str, Any]:
    counted_failed_optional = [
        item["label"] for item in assertions
        if item["capability"] == "optional" and item["status"] == "fail"
    ]
    report: dict[str, Any] = {
        "event": "B1-X5 combat-harness scenario run",
        "task_id": "B1-X5",
        "branch": git_branch(root),
        "repo_head_sha": git_head_sha(root),
        "schema_version": TELEMETRY_SCHEMA_VERSION,
        "scenario": {
            "id": scenario["id"],
            "version": scenario.get("version"),
            "summary": scenario.get("summary"),
        },
        "seed": seed,
        "plan": {
            "plan_version": plan.get("plan_version"),
            "plan_sha256": plan.get("plan_sha256"),
            "total_spawn": plan.get("total_spawn"),
        },
        "candidate": candidate,
        "modset": resolve_modset(root, runtime_info.get("modset_explicit")),
        "timestamps": {"started_at": runtime_info["started_at"], "ended_at": utc_now()},
        "boot": telemetry.get("boot") if telemetry else None,
        "counters": telemetry.get("counters") if telemetry else None,
        "perf": telemetry.get("perf") if telemetry else None,
        "capture": telemetry.get("capture") if telemetry else None,
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
        "failed_optional_assertions": counted_failed_optional,
        "result": result,
        "exit_code": {
            "PASS": EXIT_PASS, "FAIL": EXIT_FAIL, "NOT_PROVEN": EXIT_NOT_PROVEN,
        }[result],
        "proves": [
            f"scenario '{scenario['id']}' definition parsed and spawn plan deterministic under seed {seed}",
            "candidate identity resolved (hash / repo HEAD / modset) when a candidate was provided",
            scenario.get("proves", ""),
        ],
        "not_proven": [
            "in-game runtime verdict" if not telemetry or not telemetry_valid else "nothing: runtime executed",
            scenario.get("not_proven", ""),
            "gameplay feel / human S5 acceptance (human gate)",
        ],
        "evidence_paths": out_paths,
    }
    if telemetry and telemetry.get("proves"):
        report["proves"].insert(0, telemetry["proves"])
    if telemetry and telemetry.get("not_proven"):
        report["not_proven"].insert(0, telemetry["not_proven"])
    return report


def run_command(root: Path, args: argparse.Namespace) -> int:
    catalog = load_catalog(root)
    scenario = get_scenario(catalog, args.scenario)
    if scenario is None:
        raise SystemExit(f"ERROR: unknown scenario '{args.scenario}'. Use 'scenarios' to list available ids.")
    seed = args.seed if args.seed is not None else int(scenario["default_seed"])
    plan = build_plan(scenario, seed, catalog)
    candidate = resolve_candidate(args.candidate, root)
    if not args.candidate and not args.dry_run:
        raise SystemExit("ERROR: --candidate is required unless --dry-run is used.")
    if args.candidate and args.dry_run:
        print(f"[dry-run] candidate={args.candidate} sha={candidate['sha256']}")
    out_dir = (args.out_dir or root / "10_logs" / "combat_harness").resolve()
    request_dir = out_dir / "requests"
    telemetry_dir = out_dir / "telemetry"
    report_dir = out_dir / "reports"
    for directory in (request_dir, telemetry_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)
    expected_telemetry = (args.telemetry or telemetry_dir / f"{scenario['id']}_{seed}.json").resolve()
    game_plan: list[dict[str, Any]] = []
    for spawn in plan.get("spawns", []):
        resource = spawn.get("resource")
        if resource is None:
            raise SystemExit(
                f"ERROR: plan spawn {spawn.get('order')} has no resource; "
                f"mob {spawn.get('mob')!r} is missing from catalog mob_resources"
            )
        entry_res, mob_type = resource, None
        if isinstance(resource, dict):
            # Product-tree resources: generic Mob.tscn + MonsterTypes enum id.
            entry_res = resource.get("res")
            mob_type = resource.get("mob_type")
        if not entry_res:
            raise SystemExit(
                f"ERROR: plan spawn {spawn.get('order')} resource has no 'res': {resource!r}"
            )
        game_entry: dict[str, Any] = {
            "res": entry_res,
            "x": float(spawn["position"][0]),
            "y": float(spawn["position"][1]),
            "count": 1,
        }
        if mob_type:
            game_entry["mob_type"] = str(mob_type)
        game_plan.append(game_entry)
    game_request = {
        "schema_version": TELEMETRY_SCHEMA_VERSION,
        "scenario_id": scenario["id"],
        "seed": seed,
        "duration": float(scenario.get("duration_seconds", 30.0)),
        "plan": game_plan,
    }
    request = {
        "schema_version": TELEMETRY_SCHEMA_VERSION,
        "scenario": scenario,
        "seed": seed,
        "plan": plan,
        "mob_resources": catalog.get("mob_resources", {}),
        "expected_telemetry_path": str(expected_telemetry),
        "contract": "ScenarioDirector.gd reads 'game_request' (scenario_id/seed/duration/plan with "
                    "res+x+y+count), seeds Godot RNG with 'seed', spawns per the plan, then writes "
                    "telemetry JSON conforming to combat_telemetry_schema.json to 'expected_telemetry_path'.",
        "game_request": game_request,
    }
    request_path = request_dir / f"{scenario['id']}_{seed}.json"
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    runtime_info: dict[str, Any] = {
        "ran": False, "started_at": utc_now(), "launcher": args.launch,
        "launcher_returncode": None, "modset_explicit": args.modset,
    }
    telemetry: dict[str, Any] | None = None
    if args.launch:
        try:
            # posix=False on Windows keeps drive-letter backslash paths intact
            # (same convention as tests/p3_harness/p3_e2e.py split_command).
            # A fully-quoted launch value (e.g. emitted by p3_e2e templates)
            # arrives with its outer quotes retained by non-posix shlex; strip
            # them so the inner split sees plain space-separated tokens.
            launch_cmd = args.launch.strip()
            if len(launch_cmd) >= 2 and launch_cmd[0] == '"' and launch_cmd[-1] == '"':
                launch_cmd = launch_cmd[1:-1]
            proc = subprocess.run(
                shlex.split(launch_cmd, posix=(os.name != "nt")), cwd=str(root),
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
        telemetry_issues = validate_telemetry(telemetry, load_telemetry_schema(root))
        telemetry_issues.extend(telemetry_mismatch_issues(telemetry, scenario["id"], seed))
        telemetry_valid = not telemetry_issues
    usable = telemetry is not None and telemetry_valid

    assertions = evaluate_asserts(scenario, telemetry if usable else None)
    result = verdict(assertions) if usable else "NOT_PROVEN"

    out_paths = {
        "request": str(request_path),
        "telemetry": str(expected_telemetry) if expected_telemetry.is_file() else None,
        "plan": None,
        "report": str(report_dir / f"{scenario['id']}_{seed}.json"),
    }
    payload = make_report(
        root, scenario, seed, plan, candidate, telemetry if usable else None,
        telemetry_valid, telemetry_issues, assertions, result, runtime_info, out_paths,
    )
    out_paths["report"] = str(report_dir / f"{scenario['id']}_{seed}_{result}.json")
    report_path = report_dir / f"{scenario['id']}_{seed}_{result}.json"
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["evidence_paths"] = out_paths

    print(f"scenario: {scenario['id']}  seed: {seed}  plan_sha256: {plan['plan_sha256']}")
    print(f"candidate: {candidate.get('sha256') or 'N/A'}  result: {result}")
    print(f"telemetry: {'valid' if telemetry_valid else 'missing-or-invalid'} "
          f"({len(telemetry_issues)} issue(s))")
    for item in assertions:
        mark = {"pass": "PASS", "fail": "FAIL", "not_measured": "N/A"}[item["status"]]
        cap = "req" if item["capability"] == "required" else "opt"
        print(f"  [{cap}] {mark} {item['label']:36s} expected {item['op']} {item['expected']} "
              f"actual {item['actual'] if item['measured'] else '<not measured>'}")
    print(f"proves: {payload['proves'][0]}")
    print(f"report: {report_path}")
    return {"PASS": EXIT_PASS, "FAIL": EXIT_FAIL, "NOT_PROVEN": EXIT_NOT_PROVEN}[result]


def scenarios_command(root: Path) -> int:
    catalog = load_catalog(root)
    for scenario in catalog.get("scenarios", []):
        mark = "stress" if scenario.get("stress") else "normal"
        print(f"{scenario['id']:<22} {scenario['version']}  {mark}  {scenario.get('summary', '')}")
    return EXIT_PASS


def describe_command(root: Path, scenario_id: str) -> int:
    catalog = load_catalog(root)
    scenario = get_scenario(catalog, scenario_id)
    if scenario is None:
        raise SystemExit(f"ERROR: unknown scenario '{scenario_id}'. Use 'scenarios' to list ids.")
    print(json.dumps(scenario, ensure_ascii=False, indent=2))
    return EXIT_PASS


def plan_command(root: Path, scenario_id: str, seed: int | None, raw: bool = False) -> int:
    catalog = load_catalog(root)
    scenario = get_scenario(catalog, scenario_id)
    if scenario is None:
        raise SystemExit(f"ERROR: unknown scenario '{scenario_id}'. Use 'scenarios' to list ids.")
    plan = build_plan(scenario, seed if seed is not None else int(scenario["default_seed"]), catalog)
    print(json.dumps(plan, ensure_ascii=False, indent=2 if not raw else None))
    return EXIT_PASS


def selfcheck_command(root: Path, args: argparse.Namespace) -> int:
    try:
        from combat_harness_selftests import run_selfchecks
    except ImportError:
        import importlib.util
        selftests = root / "scripts" / "validate" / "combat_harness_selftests.py"
        spec = importlib.util.spec_from_file_location("combat_harness_selftests", selftests)
        if spec is None or spec.loader is None:
            raise SystemExit("ERROR: combat_harness_selftests.py not found next to the driver.")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        run_selfchecks = module.run_selfchecks
    return run_selfchecks(root, args)


def main(argv: list[str] | None = None) -> int:
    root = resolve_repo_root()
    parser = ExitCodeArgumentParser(prog="combat_harness.py", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scenarios", help="list scenario ids from the catalog")

    p_describe = sub.add_parser("describe", help="print one scenario definition")
    p_describe.add_argument("--scenario", required=True)

    p_plan = sub.add_parser("plan", help="render the deterministic seeded spawn plan")
    p_plan.add_argument("--scenario", required=True)
    p_plan.add_argument("--seed", type=int, default=None)
    p_plan.add_argument("--raw", action="store_true", help="compact single-line JSON output")

    p_run = sub.add_parser("run", help="run a scenario against a candidate and emit an evidence report")
    p_run.add_argument("--scenario", required=True)
    p_run.add_argument("--candidate", default=None)
    p_run.add_argument("--seed", type=int, default=None)
    p_run.add_argument("--out-dir", type=Path, default=None)
    p_run.add_argument("--telemetry", type=Path, default=None)
    p_run.add_argument("--launch", default=None, help="shell command that boots the game/vm")
    p_run.add_argument("--launch-timeout", type=int, default=600)
    p_run.add_argument("--modset", default=None)
    p_run.add_argument("--dry-run", action="store_true", help="render plan/report skeleton without launching")

    p_selfcheck = sub.add_parser("selfcheck", help="run static/structural self-tests and write evidence")
    p_selfcheck.add_argument("--out-dir", type=Path, default=None)
    p_selfcheck.add_argument("--evidence", type=Path, default=None,
                             help="explicit evidence json output path")

    args = parser.parse_args(argv)
    if args.command == "run":
        return run_command(root, args)
    if args.command == "scenarios":
        return scenarios_command(root)
    if args.command == "describe":
        return describe_command(root, args.scenario)
    if args.command == "plan":
        return plan_command(root, args.scenario, args.seed, args.raw)
    if args.command == "selfcheck":
        return selfcheck_command(root, args)
    parser.error(f"unknown command: {args.command}")
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
