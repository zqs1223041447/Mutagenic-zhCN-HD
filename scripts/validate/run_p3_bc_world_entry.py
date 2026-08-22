#!/usr/bin/env python3
"""P3-BC E2 world-entry evidence runner (self-contained).

Drives the P3-BC harness chain end to end: plants a synthetic
``world_entry_probe`` request, boots the product headless through the
production world-entry chain (P3BCHarnessBoot -> World -> TestLevel harness
mode with a real player, read_tiles/set_cells_terrain_connect and
initialize_navmesh), then asserts the three explicit P3-BC assertions from
the in-game telemetry:

    player_present            (player node spawned and inside the tree)
    tile_used_cells_gt_zero   (set_cells_terrain_connect painted tiles)
    navmesh_built             (AStar navmesh has points)

Canonical evidence: migration/conversion/p3_bc_world_entry.json
(--out writes an additional copy for harness evidence dirs).

Exit codes: 0 = PASS, 1 = FAIL/TOOL_FAILED/NOT_FOUND.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CANONICAL_OUT = REPO / "migration" / "conversion" / "p3_bc_world_entry.json"
LAUNCHER = REPO / "scripts" / "validate" / "p3_bc_launch_godot.py"
SCENARIO_ID = "world_entry_probe"
SEED = 2026082299


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=None,
                        help="additional evidence copy (canonical always written)")
    parser.add_argument("--timeout", type=int, default=240,
                        help="engine timeout seconds for the probe run")
    args = parser.parse_args(argv)

    work_dir = REPO / "runtime" / "p3_harness" / "world_entry_probe"
    request_dir = work_dir / "requests"
    telemetry_dir = work_dir / "telemetry"
    request_dir.mkdir(parents=True, exist_ok=True)
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    request_path = request_dir / f"{SCENARIO_ID}_{SEED}.json"
    expected_telemetry = telemetry_dir / f"{SCENARIO_ID}_{SEED}.json"

    # Synthetic request: no mobs, short duration - just prove world entry.
    request = {
        "schema_version": "1.0",
        "scenario": {"id": SCENARIO_ID},
        "seed": SEED,
        "expected_telemetry_path": str(expected_telemetry),
        "game_request": {
            "scenario_id": SCENARIO_ID,
            "seed": SEED,
            "duration": 6.0,
            "plan": [],
        },
    }
    request_path.write_text(
        json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report: dict = {
        "schema_version": 1,
        "task": "P3-BC-E2",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "driver_scene": "res://scenes/Levels/_validate/P3BCHarnessBoot.tscn",
        "request": str(request_path),
        "timeout_s": args.timeout,
    }

    started = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(LAUNCHER),
         "--scenario", SCENARIO_ID, "--seed", str(SEED),
         "--request", str(request_path),
         "--expected-telemetry", str(expected_telemetry),
         "--timeout", str(args.timeout)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO), timeout=args.timeout + 120,
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    report["launcher_returncode"] = proc.returncode
    report["launcher_tail"] = "\n".join((proc.stdout or "").splitlines()[-12:])
    report["launcher_stderr_tail"] = "\n".join((proc.stderr or "").splitlines()[-8:])
    report["duration_ms"] = duration_ms

    world: dict = {}
    counters: dict = {}
    if expected_telemetry.is_file():
        try:
            payload = json.loads(expected_telemetry.read_text(encoding="utf-8"))
            world = payload.get("world") or {}
            counters = payload.get("counters") or {}
            report["telemetry"] = {
                "scenario_id": payload.get("scenario_id"),
                "seed": payload.get("seed"),
                "exit_reason": payload.get("exit_reason"),
                "boot": payload.get("boot"),
                "world": world,
                "runtime_notes": (payload.get("runtime") or {}).get("notes"),
            }
        except ValueError as exc:
            report["telemetry_error"] = f"unreadable telemetry: {exc}"

    used_cells = int(world.get("tile_used_cells") or 0)
    navmesh_points = int(world.get("navmesh_points") or 0)
    assertions = {
        "player_present": bool(world.get("player_in_tree")),
        "tile_used_cells_gt_zero": used_cells > 0,
        "navmesh_built": navmesh_points > 0,
        "tile_used_cells": used_cells,
        "navmesh_points": navmesh_points,
    }
    assertions["all_pass"] = (
        assertions["player_present"]
        and assertions["tile_used_cells_gt_zero"]
        and assertions["navmesh_built"]
    )
    report["p3_bc_assertions"] = assertions
    report["overall"] = "PASS" if assertions["all_pass"] else "FAIL"
    if not report.get("telemetry"):
        report["overall"] = "TOOL_FAILED"
        report["note"] = "no telemetry produced by the engine run"

    _finish(report, args.out)
    return 0 if report["overall"] == "PASS" else 1


def _finish(report: dict, out_copy: Path | None) -> None:
    report["cli"] = (
        "python scripts/validate/run_p3_bc_world_entry.py "
        f"--out {out_copy.as_posix() if out_copy else '<none>'}"
    )
    CANONICAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    CANONICAL_OUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if out_copy:
        copy_path = out_copy if out_copy.is_absolute() else (REPO / out_copy)
        copy_path.parent.mkdir(parents=True, exist_ok=True)
        copy_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"P3-BC-E2 overall={report['overall']} "
          f"assertions={ {k: v for k, v in (report.get('p3_bc_assertions') or {}).items() if k != 'all_pass'} } "
          f"evidence={CANONICAL_OUT}")


if __name__ == "__main__":
    raise SystemExit(main())
