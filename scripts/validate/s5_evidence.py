#!/usr/bin/env python3
"""B2-X2 Combat S5 evidence preparation driver.

Turns Combat S5 from "a human glances at the game once" into a repeatable,
machine-prepared A/B evidence flow where the human only makes the final
experience judgment.

    python scripts/validate/s5_evidence.py aspects
    python scripts/validate/s5_evidence.py describe --aspect player_response
    python scripts/validate/s5_evidence.py plan --aspect camera --scenario cluster_kill_20 --seed 2026082005
    python scripts/validate/s5_evidence.py capture --aspect player_response --side baseline --candidate <exe> [--launch "..."]
    python scripts/validate/s5_evidence.py pair --aspect player_response --baseline <exeA> --candidate <exeB> [--launch "..."]
    python scripts/validate/s5_evidence.py validate --package <dir>
    python scripts/validate/s5_evidence.py checklist --package <dir>
    python scripts/validate/s5_evidence.py selfcheck

Every command is repo-relative; no host absolute path is hard-coded. The
scenario catalog, spawn plan and telemetry schema are REUSED from the B1-X5
combat harness (scripts/validate/combat_scenarios.json +
combat_telemetry_schema.json): an S5 capture references a harness scenario id
and seed, and the harness plan (seed -> spawn composition + positions) is the
single source for both sides.

Exit codes (contract):
    0  EVIDENCE_PREPARED  machine evidence package complete and internally
                          consistent (NOT human acceptance; the human gate
                          stays EVIDENCE_PREPARED until a human fills it)
    1  SELFTEST_FAIL      internal self-check assertion failed
    2  EVIDENCE_FAIL      a side ran but a package element is invalid
                          (telemetry schema violation, scenario/seed mismatch,
                          checklist structure invalid, ...)
    3  NOT_RUN            no launcher / dry-run / required event spine missing /
                          required capture artifacts absent -> skeleton package
                          with explicit NOT_RUN semantics
    4  USAGE              bad arguments, unknown aspect/scenario, missing or
                          nonexistent candidate executable

Boundaries:
- The machine NEVER writes HUMAN_ACCEPTED. Every generated manifest records
  human_gate.machine_status == "EVIDENCE_PREPARED" and leaves the verdict null.
- B2-X0 aggregate candidate: pass Build ID and modset hash via --build-id /
  --modset; without them the manifest records them as unbound.
- B2-X1 event spine: spine counters arrive in telemetry["s5"]["event_spine"].
  Absent spine is NOT_RUN (never FAIL); --require-event-spine turns absence
  into NOT_RUN for the side, the documented pre-X1 semantics.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

S5_SCHEMA_VERSION = 1
PLAN_VERSION = 1
EXIT_EVIDENCE_PREPARED = 0
EXIT_SELFTEST_FAIL = 1
EXIT_EVIDENCE_FAIL = 2
EXIT_NOT_RUN = 3
EXIT_USAGE = 4
ASPECTS_REL = "scripts/validate/s5_aspects.json"
SCENARIOS_REL = "scripts/validate/combat_scenarios.json"
TELEMETRY_SCHEMA_REL = "scripts/validate/combat_telemetry_schema.json"
DEFAULT_OUT_REL = "10_logs/s5_evidence"
MACHINE_GATE_STATUS = "EVIDENCE_PREPARED"
HUMAN_VERDICT_FIELDS = {"verdict", "accepted_sides", "signed_by", "signed_at", "notes"}
RESPONSE_TYPES = {"score_1_5", "yes_no", "free_text", "prefer_side"}
CAPTURE_KINDS = {"screenshot", "frame_sequence", "video", "audio_clip", "telemetry_window"}
SIDES = ("baseline", "candidate")


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
        self.exit(EXIT_USAGE, "ERROR: " + message + "\n")


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


def load_harness_driver(root: Path) -> Any:
    path = root / "scripts" / "validate" / "combat_harness.py"
    spec = importlib.util.spec_from_file_location("combat_harness", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("combat_harness.py (B1-X5) is required next to s5_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_aspects(root: Path) -> dict[str, Any]:
    return read_json(root / ASPECTS_REL)


def load_catalog(root: Path) -> dict[str, Any]:
    return read_json(root / SCENARIOS_REL)


def load_telemetry_schema(root: Path) -> dict[str, Any]:
    return read_json(root / TELEMETRY_SCHEMA_REL)


def aspect_contract_errors(aspect: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_keys = (
        "id", "summary", "wave", "depends_on_event_spine",
        "default_scenario", "scenario_bindings", "checklist",
    )
    for key in required_keys:
        if key not in aspect:
            errors.append("aspect missing key: " + key)
    if errors:
        return errors
    aid = aspect["id"]
    if aspect["wave"] not in ("A", "B"):
        errors.append(aid + ": wave must be A or B")
    for index, binding in enumerate(aspect["scenario_bindings"]):
        if "scenario" not in binding or "camera_start" not in binding or "capture_points" not in binding:
            errors.append(aid + ".scenario_bindings[" + str(index) + "]: missing scenario/camera_start/capture_points")
            continue
        start = binding["camera_start"]
        if not (isinstance(start, list) and len(start) == 2
                and all(isinstance(value, (int, float)) for value in start)):
            errors.append(aid + ".scenario_bindings[" + str(index) + "]: camera_start must be [x, y]")
        seen_points: set[str] = set()
        for point in binding["capture_points"]:
            for key in ("id", "at", "kind", "required", "telemetry_fields"):
                if key not in point:
                    errors.append(aid + "." + binding["scenario"] + ".capture_points: missing key " + key)
            pid = point.get("id")
            if pid in seen_points:
                errors.append(aid + "." + binding["scenario"] + ": duplicate capture point id " + repr(pid))
            seen_points.add(pid)
            if point.get("kind") not in CAPTURE_KINDS:
                errors.append(aid + "." + binding["scenario"] + ": unknown capture kind " + repr(point.get("kind")))
            if not isinstance(point.get("at"), (int, float)):
                errors.append(aid + "." + binding["scenario"] + ": capture point 'at' must be numeric")
    seen_checklist: set[str] = set()
    for item in aspect["checklist"]:
        for key in ("id", "question", "response_type"):
            if key not in item:
                errors.append(aid + ".checklist: missing key " + key)
        cid = item.get("id")
        if cid in seen_checklist:
            errors.append(aid + ".checklist: duplicate id " + repr(cid))
        seen_checklist.add(cid)
        if item.get("response_type") not in RESPONSE_TYPES:
            errors.append(aid + ".checklist: unknown response_type " + repr(item.get("response_type")))
    return errors


def all_aspect_errors(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for aspect in catalog.get("aspects", []):
        if aspect["id"] in seen:
            errors.append("duplicate aspect id: " + aspect["id"])
        seen.add(aspect["id"])
        errors.extend(aspect_contract_errors(aspect))
    return errors


def get_aspect(catalog: dict[str, Any], aspect_id: str) -> dict[str, Any] | None:
    for aspect in catalog.get("aspects", []):
        if aspect["id"] == aspect_id:
            return aspect
    return None


def get_scenario(harness: Any, root: Path, scenario_id: str) -> dict[str, Any] | None:
    return harness.get_scenario(load_catalog(root), scenario_id)


def resolve_binding(aspect: dict[str, Any], scenario_id: str) -> dict[str, Any] | None:
    for binding in aspect["scenario_bindings"]:
        if binding["scenario"] == scenario_id:
            return binding
    return None


def build_capture_plan(
    harness: Any, root: Path, aspect: dict[str, Any],
    scenario: dict[str, Any], seed: int,
) -> dict[str, Any]:
    catalog = load_catalog(root)
    binding = resolve_binding(aspect, scenario["id"])
    if binding is None:
        raise ValueError(
            "aspect '" + aspect["id"] + "' has no binding for scenario '" + scenario["id"] + "'"
        )
    harness_plan = harness.build_plan(scenario, seed, catalog)
    positions_sha = sha256_bytes(
        canonical_json([entry["position"] for entry in harness_plan["spawns"]]).encode("utf-8")
    )
    plan: dict[str, Any] = {
        "plan_version": PLAN_VERSION,
        "aspect_id": aspect["id"],
        "scenario_id": scenario["id"],
        "seed": seed,
        "camera_start": [float(binding["camera_start"][0]), float(binding["camera_start"][1])],
        "spawn": {
            "plan_sha256": harness_plan["plan_sha256"],
            "total_spawn": harness_plan["total_spawn"],
            "composition": [
                {"mob": entry["mob"], "count": entry["count"]}
                for entry in scenario["mob_composition"]
            ],
            "positions_sha256": positions_sha,
        },
        "capture_points": [
            {
                "id": point["id"],
                "at": float(point["at"]),
                "kind": point["kind"],
                "required": bool(point["required"]),
                "telemetry_fields": list(point["telemetry_fields"]),
            }
            for point in binding["capture_points"]
        ],
        "duration_seconds": float(scenario.get("duration_seconds", 0.0)),
    }
    plan["plan_sha256"] = sha256_bytes(canonical_json(plan).encode("utf-8"))
    return plan


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
        info["path_repo_relative"] = str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        info["path_repo_relative"] = None
    return info


def resolve_modset(root: Path, explicit: str | None) -> dict[str, Any]:
    if explicit:
        return {"source": "cli", "value": explicit, "hash": None, "unbound": False}
    lock = root / "modset.lock.json"
    if lock.is_file():
        try:
            content = lock.read_bytes()
            return {
                "source": "modset.lock.json",
                "value": json.loads(content).get("id", "lock-present"),
                "hash": sha256_bytes(content),
                "unbound": False,
            }
        except Exception:
            return {"source": "modset.lock.json", "value": "lock-present-unparsed",
                    "hash": None, "unbound": True}
    return {"source": "none", "value": "none", "hash": None, "unbound": True}


def resolve_build_id(explicit: str | None, candidate: dict[str, Any]) -> dict[str, Any]:
    if explicit:
        return {"value": explicit, "unbound": False}
    if candidate.get("sha256"):
        return {"value": "unbound-" + candidate["sha256"][:12], "unbound": True}
    return {"value": "unbound-unknown", "unbound": True}


def get_path(obj: Any, dotted: str) -> Any:
    current = obj
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def validate_side_telemetry(
    harness: Any, root: Path, telemetry: dict[str, Any],
    scenario_id: str, seed: int,
) -> list[str]:
    issues = harness.validate_telemetry(telemetry, load_telemetry_schema(root))
    if telemetry.get("scenario_id") != scenario_id:
        issues.append("telemetry.scenario_id mismatch: got " + repr(telemetry.get("scenario_id"))
                      + ", expected " + repr(scenario_id))
    if telemetry.get("seed") != seed:
        issues.append("telemetry.seed mismatch: got " + repr(telemetry.get("seed"))
                      + ", expected " + repr(seed))
    return issues


def event_spine_status(telemetry: dict[str, Any] | None) -> dict[str, Any]:
    if telemetry is None:
        return {"status": "NOT_RUN", "contract": "B2-X1", "note": "no telemetry captured"}
    spine = None
    s5 = telemetry.get("s5")
    if isinstance(s5, dict):
        spine = s5.get("event_spine")
    if not isinstance(spine, dict):
        return {"status": "NOT_RUN", "contract": "B2-X1",
                "note": "telemetry present but telemetry.s5.event_spine missing (B2-X1 not integrated)"}
    return {"status": "PRESENT", "contract": spine.get("contract", "B2-X1"),
            "counters": spine.get("counters")}


def camera_start_of(telemetry: dict[str, Any] | None) -> list[float] | None:
    if telemetry is None:
        return None
    s5 = telemetry.get("s5")
    if isinstance(s5, dict) and isinstance(s5.get("camera_start"), list):
        values = s5["camera_start"]
        if len(values) == 2 and all(isinstance(v, (int, float)) for v in values):
            return [float(values[0]), float(values[1])]
    return None


def checklist_template(aspect: dict[str, Any], package_id: str, scenario_id: str, seed: int) -> dict[str, Any]:
    questions = [
        {
            "id": item["id"],
            "question": item["question"],
            "response_type": item["response_type"],
            "judgment": None,
            "comment": None,
        }
        for item in aspect["checklist"]
    ]
    return {
        "checklist_schema_version": S5_SCHEMA_VERSION,
        "aspect_id": aspect["id"],
        "scenario_id": scenario_id,
        "seed": seed,
        "package_id": package_id,
        "instructions": "HUMAN-ONLY. Review the paired baseline/candidate captures of the evidence package, "
                        "then fill 'judgment' (and optionally 'comment') for every question and the conclusion "
                        "block. Save this file as s5_checklist_<aspect>_filled.json inside the package directory. "
                        "The machine only validates the structure of your filled file; it never writes a verdict.",
        "response_types": {
            "score_1_5": "integer 1..5",
            "yes_no": "true | false",
            "free_text": "string",
            "prefer_side": "baseline | candidate | same | unclear",
        },
        "human_gate": {
            "machine_status": MACHINE_GATE_STATUS,
            "note": "machine evidence is PREPARED, not accepted; acceptance is decided by the human only",
        },
        "questions": questions,
        "conclusion": {
            "verdict": None,
            "accepted_sides": None,
            "signed_by": None,
            "signed_at": None,
            "notes": None,
        },
    }


def checklist_template_path(package_dir: Path, aspect_id: str) -> Path:
    return package_dir / ("s5_checklist_" + aspect_id + "_template.json")


def filled_checklist_path(package_dir: Path, aspect_id: str) -> Path:
    return package_dir / ("s5_checklist_" + aspect_id + "_filled.json")


def kind_from_extension(name: str) -> str:
    lowered = name.lower()
    if lowered.endswith((".png", ".jpg", ".jpeg", ".bmp")):
        return "screenshot"
    if lowered.endswith((".webm", ".mp4", ".avi", ".gif")):
        return "video"
    if lowered.endswith((".wav", ".ogg", ".mp3", ".flac")):
        return "audio_clip"
    if lowered.endswith((".json", ".txt", ".csv")):
        return "telemetry_window"
    return "unknown"


def scan_capture_assets(capture_dir: Path, plan: dict[str, Any]) -> dict[str, Any]:
    required_ids = [point["id"] for point in plan["capture_points"] if point["required"]]
    point_kinds = {point["id"]: point["kind"] for point in plan["capture_points"]}
    if not capture_dir.is_dir():
        return {"status": "NOT_RUN", "assets": [], "missing_required": list(required_ids),
                "synthetic": False}
    assets: list[dict[str, Any]] = []
    found: set[str] = set()
    synthetic = (capture_dir / "synthetic.marker").is_file()
    for path in sorted(capture_dir.iterdir()):
        if not path.is_file() or path.name == "synthetic.marker":
            continue
        name = path.name
        point_id = next((pid for pid in point_kinds if name.startswith(pid + "_")), "unbound")
        if point_id != "unbound":
            found.add(point_id)
        assets.append({
            "name": name,
            "point_id": point_id,
            "kind": point_kinds.get(point_id, kind_from_extension(name)),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "repo_relative": None,
            "synthetic": synthetic,
        })
    missing_required = [pid for pid in required_ids if pid not in found]
    status = "OK" if not missing_required else ("PARTIAL" if assets else "NOT_RUN")
    return {"status": status, "assets": assets, "missing_required": missing_required,
            "synthetic": synthetic}


def collect_telemetry_snapshots(telemetry: dict[str, Any] | None, plan: dict[str, Any]) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for point in plan["capture_points"]:
        snapshots.append({
            "id": point["id"],
            "fields": {
                field: get_path(telemetry, field) if telemetry is not None else None
                for field in point["telemetry_fields"]
            },
        })
    return snapshots


def render_request(
    root: Path, aspect: dict[str, Any], scenario: dict[str, Any], seed: int,
    side: str, plan: dict[str, Any], telemetry_path: Path, capture_dir: Path,
) -> dict[str, Any]:
    catalog = load_catalog(root)
    harness_plan_detail = None
    try:
        harness = load_harness_driver(root)
        harness_plan_detail = harness.build_plan(scenario, seed, catalog)
    except Exception:
        harness_plan_detail = None
    return {
        "schema_version": S5_SCHEMA_VERSION,
        "aspect_id": aspect["id"],
        "scenario_id": scenario["id"],
        "seed": seed,
        "side": side,
        "capture_plan": plan,
        "spawn_plan": harness_plan_detail,
        "camera_start": plan["camera_start"],
        "expected_telemetry_path": str(telemetry_path),
        "expected_capture_dir": str(capture_dir),
        "contract": "VM-side capture script reads this request, places the Camera2D at camera_start, "
                    "runs the harness scenario with the seed, captures assets named <capture_point_id>_<n>.<ext> "
                    "into expected_capture_dir, and writes telemetry conforming to combat_telemetry_schema.json "
                    "(B1-X5) with optional s5 extension (event_spine/camera_start/captures/audio) at "
                    "expected_telemetry_path. Screenshots are required; frame sequences / video / audio clips "
                    "are optional capabilities recorded as not_measured when absent.",
    }


def side_context(
    root: Path, aspect: dict[str, Any], scenario: dict[str, Any],
    seed: int, side: str, plan: dict[str, Any],
    package_dir: Path, args: argparse.Namespace,
) -> dict[str, Any]:
    side_dir = package_dir / side
    capture_dir = side_dir / "captures"
    telemetry_dir = side_dir / "telemetry"
    telemetry_path = telemetry_dir / ("telemetry_" + scenario["id"] + "_" + str(seed) + ".json")
    request_path = side_dir / ("s5_request_" + aspect["id"] + "_" + side + "_"
                               + scenario["id"] + "_" + str(seed) + ".json")
    return {
        "side": side,
        "side_dir": side_dir,
        "capture_dir": capture_dir,
        "telemetry_dir": telemetry_dir,
        "telemetry_path": telemetry_path,
        "request_path": request_path,
    }


def launch_side(root: Path, side: str, args: argparse.Namespace, ctx: dict[str, Any]) -> dict[str, Any]:
    template = getattr(args, "launch_" + side, None) or args.launch
    result: dict[str, Any] = {"launched": False, "returncode": None, "error": None}
    if not template:
        result["error"] = "no launcher provided (--launch or --launch-" + side + ")"
        return result
    command = template.replace("{side}", side).replace("{aspect}", args.aspect)
    try:
        proc = subprocess.run(
            shlex.split(command), cwd=str(root),
            capture_output=True, text=True, timeout=args.launch_timeout,
        )
        result["launched"] = True
        result["returncode"] = proc.returncode
        if proc.stdout:
            print("[launcher-" + side + " stdout]\n" + proc.stdout)
        if proc.stderr:
            print("[launcher-" + side + " stderr]\n" + proc.stderr)
    except subprocess.TimeoutExpired:
        result["error"] = "launcher timed out after " + str(args.launch_timeout) + "s"
    return result


def collect_side_evidence(
    root: Path, harness: Any, aspect: dict[str, Any], scenario: dict[str, Any],
    seed: int, side: str, plan: dict[str, Any],
    ctx: dict[str, Any], args: argparse.Namespace,
) -> dict[str, Any]:
    ctx["telemetry_dir"].mkdir(parents=True, exist_ok=True)
    ctx["capture_dir"].mkdir(parents=True, exist_ok=True)
    telemetry_path = ctx["telemetry_path"]
    launch_info = launch_side(root, side, args, ctx)
    telemetry_explicit = args.telemetry and Path(args.telemetry).resolve()
    telemetry: dict[str, Any] | None = None
    telemetry_issues: list[str] = []
    telemetry_valid = False
    if args.dry_run:
        telemetry = None
    else:
        expected_ready = telemetry_explicit is not None and telemetry_explicit.is_file()
        if launch_info["launched"] and not expected_ready:
            deadline = time.monotonic() + max(10, args.launch_timeout // 4)
            while time.monotonic() < deadline:
                if telemetry_path.is_file():
                    break
                time.sleep(1.0)
        candidate_telemetry = telemetry_explicit if expected_ready else None
        if candidate_telemetry is None and telemetry_path.is_file():
            candidate_telemetry = telemetry_path
        if candidate_telemetry is not None:
            try:
                telemetry = read_json(candidate_telemetry)
            except Exception as exc:
                telemetry_issues.append("telemetry unparseable: " + repr(exc))
        if telemetry is not None:
            telemetry_issues = validate_side_telemetry(harness, root, telemetry, scenario["id"], seed)
            telemetry_valid = not telemetry_issues
    captures = scan_capture_assets(ctx["capture_dir"], plan)
    reasons: list[str] = []
    if args.dry_run:
        reasons.append("dry_run_mode")
    if not launch_info["launched"] and not args.dry_run:
        reasons.append("vm_not_launched: " + (launch_info["error"] or "no launcher"))
    if telemetry is None:
        reasons.append("telemetry_missing")
    if telemetry is not None and not telemetry_valid:
        reasons.append("telemetry_invalid")
    if captures["status"] != "OK":
        reasons.append("captures_" + captures["status"].lower()
                       + (": " + ",".join(captures["missing_required"]) if captures["missing_required"] else ""))
    spine = event_spine_status(telemetry if telemetry_valid else None)
    if args.require_event_spine and spine["status"] != "PRESENT":
        reasons.append("required_event_spine_missing")
    result = classify_side_result(reasons)
    telemetry_abs = telemetry_path if telemetry_path.is_file() else None
    telemetry_sha = None
    if telemetry_abs is not None:
        telemetry_sha = sha256_file(telemetry_abs)
    else:
        telemetry_abs = None
    return {
        "side": side,
        "result": result,
        "reasons": reasons,
        "launch": launch_info,
        "telemetry": {
            "provided": telemetry is not None,
            "valid": telemetry_valid,
            "issues": telemetry_issues,
            "path_repo_relative": pkg_rel(ctx["side_dir"], telemetry_abs) if telemetry_abs else None,
            "sha256": telemetry_sha,
        },
        "telemetry_data": telemetry if telemetry_valid else None,
        "telemetry_snapshots": collect_telemetry_snapshots(telemetry if telemetry_valid else None, plan),
        "captures": captures,
        "spine": spine,
        "camera_start_observed": camera_start_of(telemetry if telemetry_valid else None),
        "candidate": resolve_candidate(args.baseline if side == "baseline" else args.candidate, root),
        "build_id": resolve_build_id(args.build_id, resolve_candidate(
            args.baseline if side == "baseline" else args.candidate, root)),
        "modset": resolve_modset(root, args.modset),
        "request_rel": pkg_rel(ctx["side_dir"], ctx["request_path"]),
    }


def usage_exit(message: str) -> None:
    print("ERROR: " + message, file=sys.stderr)
    raise SystemExit(EXIT_USAGE)


def pkg_rel(side_dir: Path, path: Path) -> str | None:
    try:
        return str(path.resolve().relative_to(side_dir.resolve())).replace("\\", "/")
    except ValueError:
        return path_repo_rel_path(path) or str(path)


def path_repo_rel_path(path: Path) -> str | None:
    try:
        return str(path.resolve().relative_to(resolve_repo_root().resolve())).replace("\\", "/")
    except ValueError:
        return None


def path_repo_rel(root: Path, path: Path) -> str | None:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return None


FATAL_REASON_PREFIXES = ("telemetry_invalid",)


def classify_side_result(reasons: list[str]) -> str:
    if any(reason.startswith(FATAL_REASON_PREFIXES) for reason in reasons):
        return "FAIL"
    if reasons:
        return "NOT_RUN"
    return "OK"


def side_payload(side_info: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    telemetry_data = side_info["telemetry_data"]
    return {
        "side": side_info["side"],
        "result": side_info["result"],
        "reasons": side_info["reasons"],
        "candidate": side_info["candidate"],
        "build_id": side_info["build_id"],
        "modset": side_info["modset"],
        "launch": side_info["launch"],
        "telemetry": side_info["telemetry"],
        "telemetry_snapshots": side_info["telemetry_snapshots"],
        "captures": side_info["captures"],
        "spine": side_info["spine"],
        "camera_start_observed": side_info["camera_start_observed"],
        "request_rel": side_info["request_rel"],
        "telemetry_payload": telemetry_data,
        "has_s5_extension": isinstance(telemetry_data, dict) and isinstance(telemetry_data.get("s5"), dict),
    }


def build_manifest(
    root: Path, aspect: dict[str, Any], scenario: dict[str, Any], seed: int,
    plan: dict[str, Any], sides: dict[str, dict[str, Any]],
    kind: str, package_id: str, dry_run: bool,
) -> dict[str, Any]:
    side_records: dict[str, Any] = {}
    for side in SIDES:
        if side not in sides:
            continue
        side_records[side] = side_payload(sides[side], dry_run)
    overall_results = [side_records[side]["result"] for side in side_records]
    if all(result == "OK" for result in overall_results):
        result = "EVIDENCE_PREPARED"
    elif any(result == "FAIL" for result in overall_results):
        result = "EVIDENCE_FAIL"
    else:
        result = "NOT_RUN"
    has_spine = any(side_records.get(side, {}).get("spine", {}).get("status") == "PRESENT"
                    for side in side_records)
    any_synthetic = any(
        any(asset.get("synthetic") for asset in side_records.get(side, {}).get("captures", {}).get("assets", []))
        for side in side_records
    )
    deterministic_core: dict[str, Any] = {
        "schema_version": S5_SCHEMA_VERSION,
        "package_id": package_id,
        "kind": kind,
        "task_id": "B2-X2",
        "result": result,
        "aspect": {"id": aspect["id"], "summary": aspect["summary"],
                   "wave": aspect["wave"], "depends_on_event_spine": aspect["depends_on_event_spine"]},
        "scenario": {"id": scenario["id"], "version": scenario.get("version"),
                     "summary": scenario.get("summary"), "seed": seed},
        "capture_plan": plan,
        "spawn": plan["spawn"],
        "camera": {"start": plan["camera_start"]},
        "synthetic_captures": any_synthetic,
        "sides": {
            side: {
                "result": side_records[side]["result"],
                "reasons": side_records[side]["reasons"],
                "candidate": side_records[side]["candidate"],
                "build_id": side_records[side]["build_id"],
                "modset": side_records[side]["modset"],
                "telemetry": side_records[side]["telemetry"],
                "telemetry_snapshots": side_records[side]["telemetry_snapshots"],
                "captures": side_records[side]["captures"],
                "spine": side_records[side]["spine"],
                "camera_start_observed": side_records[side]["camera_start_observed"],
                "request_rel": side_records[side]["request_rel"],
                "telemetry_payload": side_records[side]["telemetry_payload"],
            }
            for side in side_records
        },
        "event_spine": {
            "status": "PRESENT" if has_spine else "NOT_RUN",
            "contract": "B2-X1",
            "note": "telemetry.s5.event_spine present on at least one side" if has_spine
                    else "B2-X1 event spine not observed; NOT_RUN (never FAIL)",
        },
        "human_gate": {
            "machine_status": MACHINE_GATE_STATUS,
            "verdict": None,
            "note": "machine only prepares evidence; HUMAN_ACCEPTED must come from a human-filled checklist",
        },
        "dry_run": dry_run,
        "proves": [
            "same scenario id '" + scenario["id"] + "', seed " + str(seed)
            + ", same spawn composition/positions (plan sha " + plan["spawn"]["plan_sha256"][:12]
            + ") and same camera start " + str(plan["camera_start"]) + " declared for both sides",
            "candidate identity bound (sha/build id/modset) per side",
            "machine evidence package structure and telemetry contract valid" if not dry_run
            else "machine skeleton package rendered (dry-run; nothing was executed)",
        ],
        "not_proven": [
            "human experience judgment (HUMAN-ONLY checklist)",
            "in-game runtime evidence" if dry_run else "",
            "B2-X1 event spine semantics when event_spine.status is NOT_RUN",
        ],
    }
    deterministic_core["not_proven"] = [item for item in deterministic_core["not_proven"] if item]
    core_sha = sha256_bytes(canonical_json(deterministic_core).encode("utf-8"))
    manifest = dict(deterministic_core)
    manifest["repo_head_sha"] = git_head_sha(root)
    manifest["branch"] = git_branch(root)
    manifest["volatile"] = {
        "started_at": utc_now(),
        "generator": "scripts/validate/s5_evidence.py",
    }
    manifest["deterministic_core_sha256"] = core_sha
    return manifest


def write_package(
    root: Path, harness: Any, aspect: dict[str, Any], scenario: dict[str, Any],
    seed: int, plan: dict[str, Any], package_dir: Path,
    kind: str, package_id: str, args: argparse.Namespace,
    sides: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[Path]]:
    package_dir.mkdir(parents=True, exist_ok=True)
    for side in sides:
        ctx = side_context(root, aspect, scenario, seed, side, plan, package_dir, args)
        ctx["side_dir"].mkdir(parents=True, exist_ok=True)
        ctx["telemetry_dir"].mkdir(parents=True, exist_ok=True)
        ctx["capture_dir"].mkdir(parents=True, exist_ok=True)
        request = render_request(root, aspect, scenario, seed, side, plan,
                                 ctx["telemetry_path"], ctx["capture_dir"])
        ctx["request_path"].write_text(
            json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = build_manifest(root, aspect, scenario, seed, plan, sides, kind, package_id,
                              bool(args.dry_run))
    manifest_path = package_dir / "package_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template = checklist_template(aspect, package_id, scenario["id"], seed)
    template_path = checklist_template_path(package_dir, aspect["id"])
    template_path.write_text(
        json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest, [manifest_path, template_path]


def _preflight_common(root: Path, args: argparse.Namespace) -> tuple[Any, dict[str, Any], dict[str, Any], int]:
    harness = load_harness_driver(root)
    aspects = load_aspects(root)
    aspect = get_aspect(aspects, args.aspect)
    if aspect is None:
        usage_exit("ERROR: unknown aspect '" + args.aspect + "'. Use 'aspects' to list ids.")
    scenario_id = args.scenario or aspect["default_scenario"]
    scenario = get_scenario(harness, root, scenario_id)
    if scenario is None:
        usage_exit("ERROR: unknown scenario '" + scenario_id + "'. Use the harness 'scenarios' command to list ids.")
    if resolve_binding(aspect, scenario_id) is None:
        usage_exit("ERROR: aspect '" + args.aspect + "' has no binding for scenario '" + scenario_id + "'")
    seed = args.seed if args.seed is not None else int(scenario["default_seed"])
    plan = build_capture_plan(harness, root, aspect, scenario, seed)
    return harness, aspect, scenario, plan, seed


def aspects_command(root: Path) -> int:
    catalog = load_aspects(root)
    errors = all_aspect_errors(catalog)
    if errors:
        print("ERROR: aspect catalog contract errors:")
        for error in errors:
            print("  - " + error)
        return EXIT_EVIDENCE_FAIL
    harness = load_harness_driver(root)
    known_scenarios = {scenario["id"] for scenario in load_catalog(root).get("scenarios", [])}
    for aspect in catalog.get("aspects", []):
        bindings = aspect["scenario_bindings"]
        missing = [binding["scenario"] for binding in bindings if binding["scenario"] not in known_scenarios]
        pending = " PENDING-SPINE" if aspect["depends_on_event_spine"] else ""
        extra = (" bindings-missing: " + ",".join(missing)) if missing else ""
        print(aspect["id"] + "\t" + aspect["wave"] + "-wave" + pending
              + "\tdefault=" + aspect["default_scenario"]
              + "\tbindings=" + ",".join(binding["scenario"] for binding in bindings) + extra)
    return EXIT_EVIDENCE_PREPARED


def describe_command(root: Path, aspect_id: str) -> int:
    catalog = load_aspects(root)
    aspect = get_aspect(catalog, aspect_id)
    if aspect is None:
        usage_exit("ERROR: unknown aspect '" + aspect_id + "'. Use 'aspects' to list ids.")
    print(json.dumps(aspect, ensure_ascii=False, indent=2))
    return EXIT_EVIDENCE_PREPARED


def plan_command(root: Path, args: argparse.Namespace) -> int:
    harness, aspect, scenario, plan, seed = _preflight_common(root, args)
    print(json.dumps(plan, ensure_ascii=False, indent=2 if not args.raw else None))
    return EXIT_EVIDENCE_PREPARED


def _side_candidate_paths(args: argparse.Namespace, side: str) -> str | None:
    if side == "baseline":
        return args.baseline
    return args.candidate


def _check_side_candidates(args: argparse.Namespace, root: Path, sides: list[str] | None = None) -> list[str]:
    errors: list[str] = []
    for side in (sides or SIDES):
        path = _side_candidate_paths(args, side)
        if not path:
            errors.append("missing --" + side + " candidate executable")
            continue
        resolved = Path(path).resolve()
        if not resolved.is_file():
            errors.append("--" + side + " candidate not found: " + path)
    return errors


def run_capture_command(root: Path, args: argparse.Namespace) -> int:
    harness, aspect, scenario, plan, seed = _preflight_common(root, args)
    if args.side not in SIDES:
        usage_exit("ERROR: --side must be baseline|candidate")
    if not args.dry_run:
        errors = _check_side_candidates(args, root, [args.side])
        if errors:
            usage_exit("ERROR: " + "; ".join(errors))
    package_id = "b2x2-" + aspect["id"] + "-" + scenario["id"] + "-" + str(seed) + "-" + args.side
    out_dir = (args.out_dir or root / DEFAULT_OUT_REL).resolve()
    package_dir = out_dir / package_id
    ctx = side_context(root, aspect, scenario, seed, args.side, plan, package_dir, args)
    sides = {args.side: collect_side_evidence(root, harness, aspect, scenario, seed, args.side,
                                               plan, ctx, args)}
    manifest, written = write_package(root, harness, aspect, scenario, seed, plan, package_dir,
                                      "s5_evidence_capture", package_id, args, sides)
    return finish_command(manifest, package_dir, sides)


def run_pair_command(root: Path, args: argparse.Namespace) -> int:
    harness, aspect, scenario, plan, seed = _preflight_common(root, args)
    if not args.dry_run:
        errors = _check_side_candidates(args, root)
        if errors:
            usage_exit("ERROR: " + "; ".join(errors))
    package_id = "b2x2-" + aspect["id"] + "-" + scenario["id"] + "-" + str(seed)
    out_dir = (args.out_dir or root / DEFAULT_OUT_REL).resolve()
    package_dir = out_dir / package_id
    sides: dict[str, dict[str, Any]] = {}
    for side in SIDES:
        ctx = side_context(root, aspect, scenario, seed, side, plan, package_dir, args)
        sides[side] = collect_side_evidence(root, harness, aspect, scenario, seed, side,
                                            plan, ctx, args)
    manifest, written = write_package(root, harness, aspect, scenario, seed, plan, package_dir,
                                      "s5_evidence_pair", package_id, args, sides)
    return finish_command(manifest, package_dir, sides)


def finish_command(manifest: dict[str, Any], package_dir: Path,
                   sides: dict[str, dict[str, Any]]) -> int:
    result = manifest["result"]
    print("package: " + manifest["package_id"])
    print("aspect: " + manifest["aspect"]["id"] + "  scenario: " + manifest["scenario"]["id"]
          + "  seed: " + str(manifest["scenario"]["seed"]))
    print("capture_plan_sha256: " + manifest["capture_plan"]["plan_sha256"])
    print("camera_start: " + str(manifest["camera"]["start"]))
    print("event_spine: " + manifest["event_spine"]["status"])
    for side in SIDES:
        if side not in sides:
            continue
        side_info = sides[side]
        print("side '" + side + "': result=" + side_info["result"]
              + " telemetry=" + ("valid" if side_info["telemetry"]["valid"] else "missing-or-invalid")
              + " captures=" + side_info["captures"]["status"]
              + (" reasons=" + "; ".join(side_info["reasons"]) if side_info["reasons"] else ""))
    print("human_gate: " + manifest["human_gate"]["machine_status"]
          + " (verdict pending human, machine never accepts)")
    print("result: " + result)
    print("package_dir: " + str(package_dir))
    return {
        "EVIDENCE_PREPARED": EXIT_EVIDENCE_PREPARED,
        "EVIDENCE_FAIL": EXIT_EVIDENCE_FAIL,
        "NOT_RUN": EXIT_NOT_RUN,
    }[result]


def validate_command(root: Path, args: argparse.Namespace) -> int:
    package_dir = Path(args.package).resolve()
    manifest_path = package_dir / "package_manifest.json"
    issues: list[str] = []
    if not manifest_path.is_file():
        usage_exit("ERROR: not an s5 evidence package (package_manifest.json missing): " + args.package)
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        usage_exit("ERROR: package_manifest.json unparseable: " + repr(exc))
    harness = load_harness_driver(root)
    for key in ("schema_version", "package_id", "kind", "aspect", "scenario", "capture_plan",
                "sides", "event_spine", "human_gate", "deterministic_core_sha256"):
        if key not in manifest:
            issues.append("manifest missing key: " + key)
    if "human_gate" in manifest and manifest["human_gate"].get("machine_status") != MACHINE_GATE_STATUS:
        issues.append("human_gate.machine_status must be EVIDENCE_PREPARED in machine output")
    for side in SIDES:
        if side not in manifest.get("sides", {}):
            continue
        side_info = manifest["sides"][side]
        telemetry = side_info.get("telemetry", {})
        telemetry_payload = side_info.get("telemetry_payload")
        if telemetry_payload is not None and side_info.get("result") != "NOT_RUN":
            side_issues = validate_side_telemetry(harness, root, telemetry_payload,
                                                  manifest["scenario"]["id"],
                                                  manifest["scenario"]["seed"])
            issues.extend(side_issues)
    for required_file in ("s5_checklist_" + manifest["aspect"]["id"] + "_template.json",):
        if not (package_dir / required_file).is_file():
            issues.append("missing required file: " + required_file)
    if issues:
        print("ERROR: package validation failed:")
        for issue in issues:
            print("  - " + issue)
        return EXIT_EVIDENCE_FAIL
    print("package OK: " + manifest["package_id"])
    print("  result: " + manifest["result"])
    print("  event_spine: " + manifest["event_spine"]["status"])
    print("  human_gate.machine_status: " + manifest["human_gate"]["machine_status"])
    return EXIT_EVIDENCE_PREPARED


def checklist_command(root: Path, args: argparse.Namespace) -> int:
    package_dir = Path(args.package).resolve()
    manifest_path = package_dir / "package_manifest.json"
    if not manifest_path.is_file():
        usage_exit("ERROR: not an s5 evidence package (package_manifest.json missing): " + args.package)
    manifest = read_json(manifest_path)
    aspect_id = manifest["aspect"]["id"]
    template_path = checklist_template_path(package_dir, aspect_id)
    filled_path = filled_checklist_path(package_dir, aspect_id)
    issues: list[str] = []
    template: dict[str, Any] = {}
    if template_path.is_file():
        template = read_json(template_path)
    if not filled_path.is_file():
        issues.append("filled checklist not found: " + filled_path.name
                      + " (the human must copy the template and fill judgments)")
    else:
        filled = read_json(filled_path)
        if filled.get("package_id") != manifest.get("package_id"):
            issues.append("filled checklist package_id does not match manifest")
        if filled.get("aspect_id") != aspect_id:
            issues.append("filled checklist aspect_id does not match manifest")
        if filled.get("human_gate", {}).get("machine_status") != MACHINE_GATE_STATUS:
            issues.append("filled checklist must keep human_gate.machine_status=EVIDENCE_PREPARED")
        template_questions = {q["id"]: q for q in template.get("questions", [])}
        seen: set[str] = set()
        for question in filled.get("questions", []):
            qid = question.get("id")
            if qid in seen:
                issues.append("duplicate question id in filled checklist: " + repr(qid))
            seen.add(qid)
            spec = template_questions.get(qid)
            if spec is None:
                issues.append("unknown question id in filled checklist: " + repr(qid))
                continue
            response_type = spec.get("response_type")
            judgment = question.get("judgment")
            if judgment is None:
                issues.append("unanswered question: " + qid)
            elif response_type == "score_1_5" and not (isinstance(judgment, int) and 1 <= judgment <= 5):
                issues.append("question " + qid + ": score_1_5 must be integer 1..5")
            elif response_type == "yes_no" and not isinstance(judgment, bool):
                issues.append("question " + qid + ": yes_no must be boolean")
            elif response_type == "free_text" and not isinstance(judgment, str):
                issues.append("question " + qid + ": free_text must be string")
            elif response_type == "prefer_side" and judgment not in ("baseline", "candidate", "same", "unclear"):
                issues.append("question " + qid + ": prefer_side must be baseline|candidate|same|unclear")
        conclusion = filled.get("conclusion", {})
        if conclusion.get("verdict") is None:
            issues.append("conclusion.verdict is empty (human must record accept/reject)")
        if not isinstance(conclusion.get("signed_by"), str) or not conclusion.get("signed_by"):
            issues.append("conclusion.signed_by is empty")
        if not isinstance(conclusion.get("signed_at"), str) or not conclusion.get("signed_at"):
            issues.append("conclusion.signed_at is empty")
    summary: dict[str, Any] = {
        "package_id": manifest.get("package_id"),
        "aspect_id": aspect_id,
        "checklist": "template-present" if template else "template-missing",
        "filled": "present" if filled_path.is_file() else "missing",
        "issues": issues,
        "valid": not issues,
        "note": "structural validation only; acceptance semantics are decided by the human signature",
    }
    summary_path = package_dir / ("s5_checklist_review_" + aspect_id + ".json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if issues:
        print("ERROR: checklist validation failed:")
        for issue in issues:
            print("  - " + issue)
        return EXIT_EVIDENCE_FAIL
    print("checklist structurally valid: package " + summary["package_id"] + " aspect " + aspect_id)
    verdict = read_json(filled_path).get("conclusion", {}).get("verdict")
    print("human verdict recorded (from human-filled file): " + repr(verdict))
    print("review summary: " + str(summary_path))
    return EXIT_EVIDENCE_PREPARED


def selfcheck_command(root: Path, args: argparse.Namespace) -> int:
    selftests = root / "scripts" / "validate" / "s5_evidence_selftests.py"
    if not selftests.is_file():
        usage_exit("ERROR: s5_evidence_selftests.py not found next to the driver.")
    spec = importlib.util.spec_from_file_location("s5_evidence_selftests", selftests)
    if spec is None or spec.loader is None:
        usage_exit("ERROR: cannot load s5_evidence_selftests.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_selfchecks(root, args)


def main(argv: list[str] | None = None) -> int:
    root = resolve_repo_root()
    parser = ExitCodeArgumentParser(prog="s5_evidence.py", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("aspects", help="list aspect ids, wave and scenario bindings")

    p_describe = sub.add_parser("describe", help="print one aspect definition")
    p_describe.add_argument("--aspect", required=True)

    p_plan = sub.add_parser("plan", help="render the deterministic S5 capture plan")
    p_plan.add_argument("--aspect", required=True)
    p_plan.add_argument("--scenario", default=None)
    p_plan.add_argument("--seed", type=int, default=None)
    p_plan.add_argument("--raw", action="store_true", help="compact single-line JSON output")

    p_capture = sub.add_parser("capture", help="capture one side (baseline|candidate) for one aspect")
    p_capture.add_argument("--aspect", required=True)
    p_capture.add_argument("--side", choices=list(SIDES), required=True)
    p_capture.add_argument("--baseline", default=None, help="baseline executable (used for side=baseline)")
    p_capture.add_argument("--candidate", default=None, help="candidate executable (used for side=candidate)")
    p_capture.add_argument("--scenario", default=None)
    p_capture.add_argument("--seed", type=int, default=None)
    p_capture.add_argument("--out-dir", type=Path, default=None)
    p_capture.add_argument("--launch", default=None, help="launcher command; {side} and {aspect} are substituted")
    p_capture.add_argument("--launch-baseline", default=None)
    p_capture.add_argument("--launch-candidate", default=None)
    p_capture.add_argument("--launch-timeout", type=int, default=600)
    p_capture.add_argument("--telemetry", type=Path, default=None, help="explicit telemetry json path")
    p_capture.add_argument("--build-id", default=None)
    p_capture.add_argument("--modset", default=None)
    p_capture.add_argument("--require-event-spine", action="store_true",
                           help="turn missing B2-X1 spine telemetry into NOT_RUN")
    p_capture.add_argument("--dry-run", action="store_true",
                           help="render skeleton package without launching or reading telemetry")

    p_pair = sub.add_parser("pair", help="produce the baseline+candidate paired S5 evidence package")
    p_pair.add_argument("--aspect", required=True)
    p_pair.add_argument("--baseline", default=None)
    p_pair.add_argument("--candidate", default=None)
    p_pair.add_argument("--scenario", default=None)
    p_pair.add_argument("--seed", type=int, default=None)
    p_pair.add_argument("--out-dir", type=Path, default=None)
    p_pair.add_argument("--launch", default=None, help="launcher command; {side} and {aspect} are substituted")
    p_pair.add_argument("--launch-baseline", default=None)
    p_pair.add_argument("--launch-candidate", default=None)
    p_pair.add_argument("--launch-timeout", type=int, default=600)
    p_pair.add_argument("--telemetry", type=Path, default=None)
    p_pair.add_argument("--build-id", default=None)
    p_pair.add_argument("--modset", default=None)
    p_pair.add_argument("--require-event-spine", action="store_true",
                        help="turn missing B2-X1 spine telemetry into NOT_RUN")
    p_pair.add_argument("--dry-run", action="store_true",
                        help="render skeleton package without launching or reading telemetry")

    p_validate = sub.add_parser("validate", help="structurally validate an existing evidence package")
    p_validate.add_argument("--package", required=True)

    p_checklist = sub.add_parser("checklist", help="validate a human-filled S5 checklist (never writes verdicts)")
    p_checklist.add_argument("--package", required=True)

    p_selfcheck = sub.add_parser("selfcheck", help="run static/structural self-tests and write evidence")
    p_selfcheck.add_argument("--out-dir", type=Path, default=None)
    p_selfcheck.add_argument("--evidence", type=Path, default=None,
                             help="explicit evidence json output path")

    args = parser.parse_args(argv)
    if args.command == "aspects":
        return aspects_command(root)
    if args.command == "describe":
        return describe_command(root, args.aspect)
    if args.command == "plan":
        return plan_command(root, args)
    if args.command == "capture":
        return run_capture_command(root, args)
    if args.command == "pair":
        return run_pair_command(root, args)
    if args.command == "validate":
        return validate_command(root, args)
    if args.command == "checklist":
        return checklist_command(root, args)
    if args.command == "selfcheck":
        return selfcheck_command(root, args)
    parser.error("unknown command: " + args.command)
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
