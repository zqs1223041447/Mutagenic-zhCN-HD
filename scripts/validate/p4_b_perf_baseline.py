#!/usr/bin/env python3
"""P4-B F2 performance-baseline probe CLI.

Spawns --count real Mob.tscn instances headless, samples per-frame wall
times, and records a machine-specific BASELINE (frame-ms percentiles + FPS +
machine environment summary).  First measurement only: this is explicitly
NOT a PASS/FAIL performance gate; verdicts are BASELINE (data captured and
sane), FAIL (sanity checks failed), BLOCKED/FLAKE (tool/engine trouble).

Repeatable and parameterized:

    python scripts/validate/p4_b_perf_baseline.py [--counts 50,100]
        [--frames 600] [--out PATH] [--timeout S]

The default evidence file merges every requested count into one artifact:
migration/conversion/p4_b_perf_baseline.json.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_BOOTSTRAP = Path(__file__).resolve().parents[1] / "bootstrap"
_VALIDATE = Path(__file__).resolve().parent
for _p in (_BOOTSTRAP, _VALIDATE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from product_toolchain import discover_product_godot  # type: ignore  # noqa: E402
from p3_probe_common import (  # type: ignore  # noqa: E402
    CONTENTION_SLEEP_S,
    RESULT_MARKER,
    extract_result_line,
    extract_script_errors,
    looks_like_contention,
)

TASK = "P4-B"
PROBE_ID = "p4_b_perf_baseline"
DRIVER_SCENE = "res://scenes/Mobs/_validate/p4_b_perf_probe.tscn"

EXIT_BASELINE = 0
EXIT_FAIL = 2
EXIT_NOT_PROVEN = 3


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_attempt(engine_binary: Path, product_dir: Path, count: int,
                frames: int, timeout_s: int) -> dict:
    cmd = [
        str(engine_binary), "--headless", "--path", str(product_dir),
        DRIVER_SCENE, "--", f"--count={count}", f"--frames={frames}",
    ]
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout_s)
        out, err, rc, timed_out = (
            proc.stdout or "", proc.stderr or "", proc.returncode, False)
    except subprocess.TimeoutExpired as exc:
        out_raw = exc.output or b""
        err_raw = exc.stderr or b""
        out = out_raw.decode("utf-8", errors="replace") if isinstance(
            out_raw, bytes) else out_raw
        err = err_raw.decode("utf-8", errors="replace") if isinstance(
            err_raw, bytes) else err_raw
        rc, timed_out = None, True
    return {
        "cmd": cmd,
        "returncode": rc,
        "timed_out": timed_out,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "stdout": out,
        "stderr": err,
    }


def execute_with_retry(engine_binary: Path, product_dir: Path, count: int,
                       frames: int, timeout_s: int,
                       sleep=time.sleep) -> tuple[dict, list[dict], bool]:
    """One contention retry after CONTENTION_SLEEP_S (parallel-lane cache)."""
    attempts: list[dict] = []
    for index in range(2):
        attempt = run_attempt(engine_binary, product_dir, count, frames,
                              timeout_s)
        attempts.append(attempt)
        if attempt["returncode"] in (0, 2) or index == 1:
            break
        if looks_like_contention(attempt):
            sleep(CONTENTION_SLEEP_S)
        else:
            break
    flaked = len(attempts) > 1 and attempts[-1]["returncode"] not in (0, 2)
    return attempts[-1], attempts, flaked


def machine_env_summary() -> dict:
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }


def sanitize(obj):
    root_str = str(Path(__file__).resolve().parents[2])

    def walk(node):
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, str):
            return node.replace(root_str, "<repo>").replace(
                root_str.replace("\\", "/"), "<repo>")
        return node

    return walk(obj)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="P4-B F2: high-density mob performance baseline "
                    "(first measurement, no PASS/FAIL gate)")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--product", type=Path, default=None)
    parser.add_argument("--counts", type=str, default="50",
                        help="comma-separated mob counts, e.g. 50,100")
    parser.add_argument("--frames", type=int, default=600,
                        help="sampled process frames per run")
    parser.add_argument("--out", type=Path, default=None,
                        help="evidence JSON path")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parents[2]).resolve()
    product = (args.product or (root / "product")).resolve()
    out = (args.out or root / "migration" / "conversion"
           / "p4_b_perf_baseline.json").resolve()

    counts: list[int] = []
    for token in args.counts.split(","):
        token = token.strip()
        if token:
            counts.append(max(1, int(token)))

    discovery = discover_product_godot(root)
    engine = discovery.get("engine") or {}
    evidence = {
        "schema_version": 1,
        "task": TASK,
        "probe_id": PROBE_ID,
        "exit_criteria": ["F2"],
        "generated_at": utc_now(),
        "gate": "NONE (baseline recording only)",
        "engine": {
            "binary_name": Path(str(engine.get("binary"))).name if engine.get("binary") else None,
            "resolved_via": engine.get("resolved_via"),
            "version": engine.get("version"),
            "status": engine.get("status"),
        },
        "driver_scene": DRIVER_SCENE,
        "frames_per_run": args.frames,
        "machine_env": {
            "python_side": machine_env_summary(),
        },
        "runs": {},
        "script_errors": [],
        "baseline_captured": False,
        "verdict": "BLOCKED",
        "verdict_detail": "",
        "proves": ("per-frame wall-time percentiles (p50/p95/p99/max) and FPS "
                   "for N simultaneously simulated real mobs on this machine, "
                   "recorded as a repeatable baseline with full environment "
                   "summary"),
        "not_proven": ("rendering/GPU cost (headless mode); any PASS/FAIL "
                       "performance gate (explicitly out of scope for the "
                       "first measurement)"),
    }

    if engine.get("status") != "SUCCESS" or not engine.get("binary"):
        evidence["verdict_detail"] = (
            f"engine binary not found ({engine.get('status')})")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(sanitize(evidence), ensure_ascii=False,
                                  indent=2) + "\n", encoding="utf-8")
        print(f"{PROBE_ID}=BLOCKED evidence={out}")
        return EXIT_NOT_PROVEN

    engine_binary = Path(str(engine["binary"]))
    all_ok = True
    for count in counts:
        final, attempts, flaked = execute_with_retry(
            engine_binary, product, count, args.frames, args.timeout)
        result = extract_result_line(final["stdout"])
        script_errors = extract_script_errors(final["stdout"],
                                              final["stderr"])
        for line in script_errors:
            if line not in evidence["script_errors"]:
                evidence["script_errors"].append(line)

        run_record = {
            "count": count,
            "command": final["cmd"],
            "returncode": final["returncode"],
            "timed_out": final["timed_out"],
            "duration_ms": final["duration_ms"],
            "attempts": len(attempts),
            "flaked": flaked,
            "result": result,
        }
        if result is None:
            run_record["verdict"] = "FLAKE" if flaked else "BLOCKED"
            run_record["detail"] = "no P3_PROBE_RESULT line in driver output"
            all_ok = False
        elif result.get("pass") is True:
            run_record["verdict"] = "BASELINE"
            run_record["detail"] = "baseline captured (sanity checks passed)"
            if result.get("env"):
                evidence["machine_env"]["godot_side"] = result["env"]
        else:
            run_record["verdict"] = "FAIL"
            run_record["detail"] = "; ".join(result.get("errors") or [])
            all_ok = False
        evidence["runs"][str(count)] = run_record

    evidence["baseline_captured"] = all_ok
    evidence["verdict"] = "BASELINE" if all_ok else "FAIL"
    evidence["verdict_detail"] = (
        "all requested counts captured" if all_ok
        else "one or more runs failed sanity/blocked; see runs[*].verdict")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sanitize(evidence), ensure_ascii=False,
                              indent=2) + "\n", encoding="utf-8")
    print(f"{PROBE_ID}={evidence['verdict']} counts={counts} "
          f"evidence={out}")
    return EXIT_BASELINE if all_ok else EXIT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
