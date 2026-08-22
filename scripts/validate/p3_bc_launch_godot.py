#!/usr/bin/env python3
"""P3-BC launcher bridge between combat_harness.py and the Godot runtime.

combat_harness.py renders a request JSON under <out-dir>/requests/ and expects
telemetry under <out-dir>/telemetry/.  The in-game director reads its request
from user://combat_harness/request.json.  This bridge copies the request into
the engine's user dir, boots the product headless through the production
world-entry chain (P3BCHarnessBoot.tscn -> World -> TestLevel harness mode),
and verifies the telemetry landed at the expected host path (the director
writes it there directly; a user-dir copy is used as fallback).

    python scripts/validate/p3_bc_launch_godot.py \
        --scenario cluster_kill_20 --seed 2026082005 \
        --out-dir 10_logs/combat_harness [--timeout 240] [--engine <exe>]

Exit codes: 0 = telemetry written, 3 = runtime ran but no telemetry,
4 = usage / missing inputs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "bootstrap"))
from product_boot_probe import resolve_engine  # noqa: E402

BOOT_SCENE = "res://scenes/Levels/_validate/P3BCHarnessBoot.tscn"
DEFAULT_TIMEOUT = 300


def project_user_dir(product_dir: Path) -> Path | None:
    """Resolve the engine's user:// dir for the product project."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    name = "Mutagenic"
    project_file = product_dir / "project.godot"
    if project_file.is_file():
        match = re.search(r'^config/name="(.*)"\s*$',
                          project_file.read_text(encoding="utf-8"), re.M)
        if match:
            name = match.group(1)
    return Path(appdata) / "Godot" / "app_userdata" / name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--out-dir", required=True,
                        help="same out-dir combat_harness.py run used")
    parser.add_argument("--request", default=None,
                        help="explicit request path override")
    parser.add_argument("--expected-telemetry", default=None,
                        help="explicit telemetry path override")
    parser.add_argument("--engine", default=None, help="godot binary override")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (REPO / out_dir).resolve()
    request_path = (Path(args.request) if args.request
                    else out_dir / "requests" / f"{args.scenario}_{args.seed}.json")
    expected_telemetry = (Path(args.expected_telemetry) if args.expected_telemetry
                          else out_dir / "telemetry" / f"{args.scenario}_{args.seed}.json")
    if not request_path.is_absolute():
        request_path = (REPO / request_path).resolve()
    if not expected_telemetry.is_absolute():
        expected_telemetry = (REPO / expected_telemetry).resolve()
    if not request_path.is_file():
        print(f"ERROR: request file not found: {request_path}")
        return 4

    engine = resolve_engine(REPO)
    binary = args.engine or engine.get("binary")
    if not binary or not Path(binary).is_file():
        print(f"ERROR: godot binary not resolved: {binary!r} "
              f"(via {engine.get('resolved_via')!r})")
        return 4

    user_dir = project_user_dir(REPO / "product")
    if user_dir is None:
        print("ERROR: cannot resolve engine user dir (APPDATA unset)")
        return 4
    harness_dir = user_dir / "combat_harness"
    harness_dir.mkdir(parents=True, exist_ok=True)
    user_request = harness_dir / "request.json"

    # Clean slate so stale artifacts can never satisfy this run.
    if expected_telemetry.exists():
        expected_telemetry.unlink()
    for stale in harness_dir.glob(f"telemetry_{args.scenario}_{args.seed}.json"):
        stale.unlink()
    shutil.copyfile(request_path, user_request)

    cmd = [binary, "--headless", "--path", str(REPO / "product"), BOOT_SCENE]
    print("[p3_bc_launch] cmd:", subprocess.list2cmdline(cmd))
    started = time.monotonic()
    returncode = None
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              timeout=args.timeout)
        returncode = proc.returncode
        tail = "\n".join((proc.stdout or "").splitlines()[-15:])
        if tail.strip():
            print("[p3_bc_launch][stdout tail]\n" + tail)
        err_tail = "\n".join((proc.stderr or "").splitlines()[-10:])
        if err_tail.strip():
            print("[p3_bc_launch][stderr tail]\n" + err_tail)
    except subprocess.TimeoutExpired as exc:
        print(f"[p3_bc_launch] TIMEOUT after {args.timeout}s")
        for stream_name in ("stdout", "stderr"):
            chunk = getattr(exc, stream_name) or b""
            if isinstance(chunk, bytes):
                chunk = chunk.decode("utf-8", errors="replace")
            lines = [ln for ln in str(chunk).splitlines() if ln.strip()]
            if lines:
                print(f"[p3_bc_launch][{stream_name} tail]\n" + "\n".join(lines[-10:]))
    duration_s = int(time.monotonic() - started)

    # The harness request must never leak into a normal gameplay launch.
    try:
        user_request.unlink()
    except OSError:
        pass

    if not expected_telemetry.is_file():
        fallback = harness_dir / f"telemetry_{args.scenario}_{args.seed}.json"
        if fallback.is_file():
            expected_telemetry.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fallback, expected_telemetry)
            print("[p3_bc_launch] telemetry recovered from user-dir copy")

    if expected_telemetry.is_file():
        try:
            payload = json.loads(expected_telemetry.read_text(encoding="utf-8"))
            counters = payload.get("counters", {})
            print(f"[p3_bc_launch] OK in {duration_s}s rc={returncode} "
                  f"scenario={payload.get('scenario_id')} seed={payload.get('seed')} "
                  f"killed={counters.get('killed')}/{counters.get('spawned')} "
                  f"damage_events={counters.get('damage_events')} "
                  f"dashes={counters.get('dashes')} moves={counters.get('player_moves')}")
            return 0
        except (OSError, ValueError) as exc:
            print(f"[p3_bc_launch] telemetry unreadable: {exc}")
            return 3
    print(f"[p3_bc_launch] NO TELEMETRY after {duration_s}s (engine rc={returncode})")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
