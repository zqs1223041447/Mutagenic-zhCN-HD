#!/usr/bin/env python3
"""Shared engine-probe plumbing for the P3 C/D/E probes.

Provides engine discovery, headless driver-scene execution with one
contention retry (the concurrent validation lane may hold the .godot cache),
P3_PROBE_RESULT JSON parsing, SCRIPT ERROR extraction, verdict classification
and evidence-JSON emission.

Exit-code contract (aligned with scripts/validate/combat_harness.py):
    0  PASS        - probe reported pass=true, no fatal signature
    2  FAIL        - probe ran and reported pass=false
    3  NOT_PROVEN  - tool/engine missing or blocked; nothing proven
    4  USAGE       - bad arguments
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_BOOTSTRAP = Path(__file__).resolve().parents[1] / "bootstrap"
if str(_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP))

from product_toolchain import discover_product_godot  # type: ignore  # noqa: E402
from product_smoke_probe import has_fatal_signature  # type: ignore  # noqa: E402

EXIT_PASS = 0
EXIT_FAIL = 2
EXIT_NOT_PROVEN = 3
EXIT_USAGE = 4

RESULT_MARKER = "P3_PROBE_RESULT:"
CONTENTION_SLEEP_S = 30


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_result_line(stdout: str) -> dict | None:
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith(RESULT_MARKER):
            try:
                return json.loads(line[len(RESULT_MARKER):])
            except json.JSONDecodeError:
                return None
    return None


def extract_script_errors(stdout: str, stderr: str) -> list[str]:
    lines = []
    for stream in (stdout, stderr):
        for line in (stream or "").splitlines():
            stripped = line.strip()
            if stripped.startswith("SCRIPT ERROR:") and stripped not in lines:
                lines.append(stripped)
    return lines


def run_driver(engine_binary: Path, product_dir: Path, driver_scene: str,
               timeout_s: int = 180,
               run=None) -> dict:
    """Run one headless driver-scene attempt."""
    cmd = [str(engine_binary), "--headless", "--path", str(product_dir), driver_scene]
    runner = run or subprocess.run
    started = time.monotonic()
    try:
        proc = runner(cmd, capture_output=True, text=True, timeout=timeout_s)
        out, err, rc, timed_out = proc.stdout or "", proc.stderr or "", proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        out = (exc.output or b"").decode("utf-8", errors="replace") if isinstance(exc.output, bytes) else (exc.output or "")
        err = (exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rc, timed_out = None, True
    duration_ms = int((time.monotonic() - started) * 1000)
    return {
        "cmd": cmd,
        "returncode": rc,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "stdout": out,
        "stderr": err,
    }


def looks_like_contention(attempt: dict) -> bool:
    """Heuristics for .godot cache/import contention with a parallel lane."""
    if attempt["timed_out"] or attempt["returncode"] is None:
        return True
    combined = (attempt["stdout"] or "") + (attempt["stderr"] or "")
    markers = (
        "Unable to write to cache",
        "Error opening file for write",
        ".godot/imported",
        "Failed loading resource: res://.godot",
        "handle_crash",
    )
    return any(marker in combined for marker in markers)


def execute_with_retry(engine_binary: Path, product_dir: Path, driver_scene: str,
                       timeout_s: int = 180, max_attempts: int = 2,
                       run=None, sleep=time.sleep) -> tuple[dict, list[dict], bool]:
    """Run the driver; on contention-looking failures wait 30s and retry once.

    Returns (final_attempt, all_attempts, flaked).
    """
    attempts: list[dict] = []
    for index in range(max_attempts):
        attempt = run_driver(engine_binary, product_dir, driver_scene,
                             timeout_s=timeout_s, run=run)
        attempts.append(attempt)
        clean_exit = attempt["returncode"] in (0, 2)
        if clean_exit or index == max_attempts - 1:
            break
        if looks_like_contention(attempt):
            sleep(CONTENTION_SLEEP_S)
        else:
            break
    flaked = len(attempts) > 1 and attempts[-1]["returncode"] not in (0, 2)
    return attempts[-1], attempts, flaked


def classify(attempt: dict, result: dict | None,
             script_errors: list[str]) -> tuple[str, str]:
    """-> (verdict, detail)."""
    if result is None:
        detail = "no P3_PROBE_RESULT line in driver output"
        if has_fatal_signature(attempt.get("stdout") or "", attempt.get("stderr") or ""):
            return "BLOCKED", detail + "; fatal signature present"
        return ("FAIL" if attempt["returncode"] in (0, 2) else "BLOCKED"), detail
    if result.get("pass") is True:
        return "PASS", "probe assertions satisfied"
    return "FAIL", "probe assertions failed: " + "; ".join(result.get("errors") or [])


def build_evidence(task: str, probe_id: str, exit_criteria: list[str],
                   driver_scene: str, proves: str, not_proven: str,
                   engine: dict, final: dict, attempts: list[dict],
                   flaked: bool, result: dict | None,
                   script_errors: list[str]) -> dict:
    verdict, detail = classify(final, result, script_errors)
    if flaked and verdict != "PASS":
        verdict = "FLAKE"
    return {
        "schema_version": 1,
        "task": task,
        "probe_id": probe_id,
        "exit_criteria": exit_criteria,
        "generated_at": utc_now(),
        "engine": {
            "binary_name": Path(str(engine.get("binary"))).name if engine.get("binary") else None,
            "resolved_via": engine.get("resolved_via"),
            "version": engine.get("version"),
            "status": engine.get("status"),
        },
        "driver_scene": driver_scene,
        "command": final.get("cmd"),
        "returncode": final.get("returncode"),
        "timed_out": final.get("timed_out"),
        "duration_ms": final.get("duration_ms"),
        "attempts": len(attempts),
        "flaked": flaked,
        "result": result,
        "script_errors": script_errors,
        "verdict_detail": detail,
        "verdict": verdict,
        "proves": proves,
        "not_proven": not_proven,
    }


def write_evidence(evidence: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe_main(argv: list[str] | None, *, task: str, probe_id: str,
               exit_criteria: list[str], driver_scene: str, default_out: Path,
               proves: str, not_proven: str) -> int:
    ap = argparse.ArgumentParser(description=f"{probe_id}: {proves}")
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--product", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None,
                    help="evidence JSON path")
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    product = (args.product or (root / "product")).resolve()
    out = (args.out or default_out).resolve()

    discovery = discover_product_godot(root)
    engine = discovery.get("engine") or {}
    if engine.get("status") != "SUCCESS" or not engine.get("binary"):
        print(f"ERROR: engine binary not found ({engine.get('status')})", file=sys.stderr)
        evidence = build_evidence(task, probe_id, exit_criteria, driver_scene,
                                  proves, not_proven, engine,
                                  {"cmd": None, "returncode": None, "timed_out": False,
                                   "duration_ms": 0, "stdout": "", "stderr": ""},
                                  [], False, None, [])
        write_evidence(evidence, out)
        print(f"{probe_id}=BLOCKED evidence={out}")
        return EXIT_NOT_PROVEN

    final, attempts, flaked = execute_with_retry(
        Path(str(engine["binary"])), product, driver_scene,
        timeout_s=args.timeout)
    result = extract_result_line(final["stdout"])
    script_errors = extract_script_errors(final["stdout"], final["stderr"])

    evidence = build_evidence(task, probe_id, exit_criteria, driver_scene,
                              proves, not_proven, engine, final, attempts,
                              flaked, result, script_errors)
    write_evidence(evidence, out)

    verdict = evidence["verdict"]
    print(f"{probe_id}={verdict} "
          f"(rc={final['returncode']}, script_errors={len(script_errors)}, "
          f"flaked={flaked}) evidence={out}")
    if verdict == "PASS":
        return EXIT_PASS
    if verdict in ("FAIL", "FLAKE"):
        return EXIT_FAIL
    return EXIT_NOT_PROVEN
