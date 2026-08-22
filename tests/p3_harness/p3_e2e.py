#!/usr/bin/env python3
"""P3 End-to-End Automation Harness - step driver (skeleton).

Drives the P3 playable baseline (character -> world -> combat -> pickup ->
UI -> save) as eight independently checkable steps mapped to the P3 exit
criteria E1-E8.  This phase ships the framework only: every step defaults to
NOT_RUN because its runner hook (see tests/p3_harness/config.json) is
reserved for a later attempt.  The generic runner executor is already wired,
so filling a step means flipping "implemented": true and adjusting its
command template in the config - no driver changes required.

Single-command run with a machine-readable JSON report:

    python tests/p3_harness/p3_e2e.py                      # all steps
    python tests/p3_harness/p3_e2e.py --steps E1,E3        # subset
    python tests/p3_harness/p3_e2e.py --json-only          # stdout = JSON
    python tests/p3_harness/p3_e2e.py --out path/report.json
    python tests/p3_harness/p3_e2e.py --list-steps

Exit codes (aligned with scripts/validate/combat_harness.py):
    0  PASS     - at least one executed step passed, none failed
    2  FAIL     - at least one executed step failed
    3  NOT_RUN  - skeleton mode: no step produced PASS/FAIL yet
    4  USAGE    - bad arguments/config (unknown step id, unreadable config)

No Godot binary is launched by this skeleton: runners stay dormant until an
attempt flips implemented=true in the config.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# --- Exit-code contract -----------------------------------------------------
EXIT_PASS = 0
EXIT_FAIL = 2
EXIT_NOT_RUN = 3
EXIT_USAGE = 4

# --- Step/status constants ---------------------------------------------------
HARNESS_ID = "P3-E2E"
SCHEMA_VERSION = "1.0"
STEP_ORDER = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_NOT_RUN = "NOT_RUN"
STATUS_SKIP = "SKIP"
RESULT_KEYS = ("step_id", "status", "detail", "evidence_path")

DEFAULT_CONFIG_REL = "tests/p3_harness/config.json"
DEFAULT_REPORT_REL = "runtime/p3_harness_report.json"
DEFAULT_NOT_RUN_NOTE = (
    "runner hook reserved (implemented=false); see tests/p3_harness/config.json"
)
SKIP_NOTE = "not selected (use --steps to include)"


class UsageError(ValueError):
    """Bad CLI selection or command-template placeholder."""


class ConfigError(ValueError):
    """Malformed or incomplete harness config."""


@dataclass
class HarnessContext:
    """Everything a check function needs; `run` is injectable for tests."""

    config: dict
    repo_root: Path
    report_path: Path
    run: Callable[..., Any] = field(default=subprocess.run)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git_head_sha(root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(root),
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode == 0:
        return proc.stdout.strip() or None
    return None


# --- Config ------------------------------------------------------------------
def load_config(path: Path) -> dict:
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"config unreadable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config is not valid JSON: {path} ({exc})") from exc
    if not isinstance(cfg, dict):
        raise ConfigError(f"config root must be an object: {path}")
    steps = cfg.get("steps")
    if not isinstance(steps, dict):
        raise ConfigError("config missing 'steps' object")
    missing = [sid for sid in STEP_ORDER if sid not in steps]
    if missing:
        raise ConfigError(f"config steps missing ids: {missing}")
    extra = sorted(set(steps) - set(STEP_ORDER))
    if extra:
        raise ConfigError(f"config steps carry unknown ids: {extra}")
    return cfg


def parse_step_selection(spec: str | None) -> list[str]:
    """'E1,E3' -> ['E1', 'E3']; None -> every step. Dedupes, keeps order."""
    if spec is None or not spec.strip():
        return list(STEP_ORDER)
    selected: list[str] = []
    for token in spec.split(","):
        sid = token.strip().upper()
        if not sid:
            continue
        if sid not in STEP_ORDER:
            raise UsageError(f"unknown step id: {token.strip()!r} (known: {', '.join(STEP_ORDER)})")
        if sid not in selected:
            selected.append(sid)
    if not selected:
        raise UsageError("empty --steps selection")
    return selected


def resolve_out_path(out_arg: Path | None, cfg: dict, root: Path) -> Path:
    if out_arg is not None:
        return out_arg if out_arg.is_absolute() else (Path.cwd() / out_arg).resolve()
    rel = cfg.get("default_report_path") or DEFAULT_REPORT_REL
    return (root / rel).resolve()


# --- Step results -------------------------------------------------------------
def make_result(step_id: str, status: str, detail: str,
                evidence_path: str | None = None) -> dict:
    return {
        "step_id": step_id,
        "status": status,
        "detail": detail,
        "evidence_path": evidence_path,
    }


def step_context(ctx: HarnessContext, step_id: str) -> dict[str, str]:
    """Format placeholders available to runner command templates."""
    cfg = ctx.config
    evidence_dir = ctx.repo_root / cfg.get(
        "evidence_dir", "runtime/p3_harness/evidence")
    scenes = cfg.get("scene_paths") or {}
    tools = cfg.get("tools") or {}
    values: dict[str, str] = {
        "python": sys.executable,
        "repo_root": str(ctx.repo_root),
        "product_dir": str(ctx.repo_root / cfg.get("product_dir", "product")),
        "godot_bin": os.environ.get("GODOT_BIN", "godot"),
        "report": str(ctx.report_path),
        "out_dir": str(ctx.report_path.parent),
        "evidence_dir": str(evidence_dir),
        "step_evidence": str(evidence_dir / f"{step_id.lower()}_evidence.json"),
    }
    for key, val in scenes.items():
        values[f"{key}_scene"] = str(val)
    for key, rel in tools.items():
        values[key] = str(ctx.repo_root / rel)
    return values


def render_command(template: str, values: dict[str, str]) -> str:
    try:
        return template.format(**values).strip()
    except KeyError as exc:
        raise UsageError(f"unknown placeholder {exc} in command template") from exc


def split_command(rendered: str) -> list[str]:
    # Normalize to forward slashes so a single posix-aware tokenizer works on
    # every platform; Windows accepts forward-slash paths for executables/args.
    return shlex.split(rendered.replace("\\", "/"), posix=True)


def execute_runner(step_id: str, runner: dict, values: dict[str, str],
                   run: Callable[..., Any] | None = None) -> dict:
    """Generic runner hook executor. Only reached when implemented=true."""
    run = run or subprocess.run
    template = runner.get("command_template")
    if not template:
        return make_result(step_id, STATUS_FAIL,
                           "runner implemented=true but command_template is null")
    timeout_s = float(runner.get("timeout_s", 300))
    try:
        argv = split_command(render_command(template, values))
    except UsageError as exc:
        return make_result(step_id, STATUS_FAIL, f"template error: {exc}")
    started = time.monotonic()
    try:
        proc = run(argv, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return make_result(step_id, STATUS_FAIL,
                           f"runner timed out after {timeout_s:g}s")
    except OSError as exc:
        return make_result(step_id, STATUS_FAIL, f"runner spawn failed: {exc}")
    duration_ms = int((time.monotonic() - started) * 1000)
    evidence_raw = values.get("step_evidence")
    evidence_path = evidence_raw if evidence_raw and Path(evidence_raw).is_file() else None
    if proc.returncode == 0:
        return make_result(step_id, STATUS_PASS,
                           f"runner rc=0 in {duration_ms}ms", evidence_path)
    tail = ""
    combined = (proc.stderr or "") + (proc.stdout or "")
    lines = [ln for ln in combined.splitlines() if ln.strip()]
    if lines:
        tail = f"; last: {lines[-1][:200]}"
    return make_result(step_id, STATUS_FAIL,
                       f"runner rc={proc.returncode} in {duration_ms}ms{tail}",
                       evidence_path)


# --- Per-step check functions (one per exit criterion E1-E8) ------------------
def run_step(step_id: str, ctx: HarnessContext) -> dict:
    step_cfg = ctx.config["steps"][step_id]
    runner = step_cfg.get("runner") or {}
    if not runner.get("implemented", False):
        note = runner.get("note") or DEFAULT_NOT_RUN_NOTE
        if "implemented=false" not in note:
            note = f"{note} [runner hook reserved: implemented=false]"
        return make_result(step_id, STATUS_NOT_RUN, note)
    return execute_runner(step_id, runner, step_context(ctx, step_id), run=ctx.run)


def check_e1(ctx: HarnessContext) -> dict:
    """E1: LoadGame reaches character selectable/selected."""
    return run_step("E1", ctx)


def check_e2(ctx: HarnessContext) -> dict:
    """E2: Enter TestLevel without blocking errors."""
    return run_step("E2", ctx)


def check_e3(ctx: HarnessContext) -> dict:
    """E3: Movement + Dash position assertion."""
    return run_step("E3", ctx)


def check_e4(ctx: HarnessContext) -> dict:
    """E4: Active skill release produces combat events."""
    return run_step("E4", ctx)


def check_e5(ctx: HarnessContext) -> dict:
    """E5: Kill a mob."""
    return run_step("E5", ctx)


def check_e6(ctx: HarnessContext) -> dict:
    """E6: Pickup drop lands in inventory."""
    return run_step("E6", ctx)


def check_e7(ctx: HarnessContext) -> dict:
    """E7: Skill screen and passive tree screen open without crash."""
    return run_step("E7", ctx)


def check_e8(ctx: HarnessContext) -> dict:
    """E8: Save -> Load restores key state."""
    return run_step("E8", ctx)


CHECKS: dict[str, Callable[[HarnessContext], dict]] = {
    "E1": check_e1,
    "E2": check_e2,
    "E3": check_e3,
    "E4": check_e4,
    "E5": check_e5,
    "E6": check_e6,
    "E7": check_e7,
    "E8": check_e8,
}


# --- Report assembly -----------------------------------------------------------
def classify_overall(results: list[dict]) -> str:
    statuses = [r["status"] for r in results]
    if STATUS_FAIL in statuses:
        return STATUS_FAIL
    if STATUS_PASS in statuses:
        return STATUS_PASS
    return STATUS_NOT_RUN


def proves_not_proven(overall: str, results: list[dict]) -> tuple[str, str]:
    executed = [r for r in results if r["status"] in (STATUS_PASS, STATUS_FAIL)]
    if overall == STATUS_PASS:
        return ("all executed P3 exit-criteria steps passed end to end",
                "steps skipped via --steps are unproven")
    if overall == STATUS_FAIL:
        failed = ", ".join(r["step_id"] for r in results if r["status"] == STATUS_FAIL)
        return (f"harness executed its runners; failing steps isolate the break: {failed}",
                "passing steps still depend on their runner's own not_proven scope")
    if executed:
        return ("harness mechanics: step execution, result accounting, report schema",
                "no P3 gameplay behavior - every executed step failed before proving anything")
    return ("framework skeleton executes end-to-end and emits a schema-valid report",
            "no P3 gameplay behavior - every step's runner is unimplemented "
            "(implemented=false in tests/p3_harness/config.json)")


def build_report(cfg: dict, selected: list[str], results: list[dict],
                 root: Path) -> dict:
    summary = {
        "total": len(results),
        "pass": sum(1 for r in results if r["status"] == STATUS_PASS),
        "fail": sum(1 for r in results if r["status"] == STATUS_FAIL),
        "not_run": sum(1 for r in results if r["status"] == STATUS_NOT_RUN),
        "skip": sum(1 for r in results if r["status"] == STATUS_SKIP),
    }
    overall = classify_overall(results)
    proves, not_proven = proves_not_proven(overall, results)
    return {
        "harness_id": HARNESS_ID,
        "schema_version": SCHEMA_VERSION,
        "ran_at": utc_now(),
        "repo_head_sha": git_head_sha(root),
        "selected_steps": list(selected),
        "steps": results,
        "summary": summary,
        "result": overall,
        "proves": proves,
        "not_proven": not_proven,
    }


def write_report(report: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def exit_code_for(report: dict) -> int:
    result = report["result"]
    if result == STATUS_PASS:
        return EXIT_PASS
    if result == STATUS_FAIL:
        return EXIT_FAIL
    return EXIT_NOT_RUN


# --- CLI ------------------------------------------------------------------------
def run_harness(cfg: dict, selected: list[str], out_path: Path,
                root: Path, run: Callable[..., Any] | None = None) -> tuple[dict, int]:
    ctx = HarnessContext(config=cfg, repo_root=root, report_path=out_path,
                         run=run or subprocess.run)
    results = [
        CHECKS[sid](ctx) if sid in selected
        else make_result(sid, STATUS_SKIP, SKIP_NOTE)
        for sid in STEP_ORDER
    ]
    report = build_report(cfg, selected, results, root)
    write_report(report, out_path)
    return report, exit_code_for(report)


def print_human(report: dict, out_path: Path) -> None:
    print(f"[{HARNESS_ID}] selected: {', '.join(report['selected_steps'])}")
    for step in report["steps"]:
        print(f"[{step['status']}] {step['step_id']}: {step['detail']}")
    s = report["summary"]
    print(f"summary: pass={s['pass']} fail={s['fail']} "
          f"not_run={s['not_run']} skip={s['skip']} -> {report['result']}")
    print(f"report: {out_path}")


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to cp1252; step details carry non-ASCII notes.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=None,
                        help="JSON report path (default: runtime/p3_harness_report.json)")
    parser.add_argument("--steps", default=None,
                        help="comma-separated subset, e.g. E1,E3 (default: all)")
    parser.add_argument("--config", type=Path, default=None,
                        help="harness config path (default: tests/p3_harness/config.json)")
    parser.add_argument("--json-only", action="store_true",
                        help="print the JSON report to stdout instead of a human summary")
    parser.add_argument("--list-steps", action="store_true",
                        help="list steps and runner readiness, then exit")
    args = parser.parse_args(argv)

    root = repo_root()
    config_path = args.config if args.config else root / DEFAULT_CONFIG_REL
    try:
        cfg = load_config(config_path)
        selected = parse_step_selection(args.steps)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE

    if args.list_steps:
        for sid in STEP_ORDER:
            step = cfg["steps"][sid]
            ready = bool((step.get("runner") or {}).get("implemented", False))
            print(f"{sid}\t{'READY' if ready else 'NOT_RUN'}\t{step.get('title', '')}")
        return EXIT_PASS

    out_path = resolve_out_path(args.out, cfg, root)
    report, code = run_harness(cfg, selected, out_path, root)
    if args.json_only:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report, out_path)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
