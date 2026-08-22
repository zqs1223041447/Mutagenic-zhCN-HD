#!/usr/bin/env python3
"""P3-BC E2 world-entry evidence runner.

Drives the existing P3BDriver scene (production path: character -> World ->
TestLevel with a real player, read_tiles/set_cells_terrain_connect and
initialize_navmesh) headless, parses the driver's P3B_RESULT_JSON marker and
records the three explicit P3-BC assertions on top of the driver result:

    player_present            (player node spawned inside the level layer)
    tile_used_cells_gt_zero   (set_cells_terrain_connect painted tiles)
    navmesh_built             (AStar navmesh has points)

Canonical evidence: migration/conversion/p3_bc_world_entry.json
(--out writes an additional copy for harness evidence dirs).

Exit codes: 0 = PASS, 1 = FAIL/TOOL_FAILED/NOT_FOUND.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_BOOTSTRAP = REPO / "scripts" / "bootstrap"
if str(_BOOTSTRAP) not in sys.path:
    sys.path.insert(0, str(_BOOTSTRAP))

try:
    from product_toolchain import discover_product_godot  # type: ignore
except ImportError:  # older bootstrap layout
    from product_boot_probe import resolve_engine as _resolve_engine  # type: ignore

    def discover_product_godot(root: Path) -> dict:
        info = _resolve_engine(root)
        return {"engine": {
            "binary": info.get("binary"),
            "resolved_via": info.get("resolved_via"),
            "version": info.get("version"),
            "status": info.get("tool_status"),
        }}

CANONICAL_OUT = REPO / "migration" / "conversion" / "p3_bc_world_entry.json"
MARKER = "P3B_RESULT_JSON<<<"
DRIVER_SCENE = "res://scenes/Levels/_validate/P3BDriver.tscn"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=None,
                        help="additional evidence copy (canonical always written)")
    parser.add_argument("--timeout", type=int, default=360)
    args = parser.parse_args(argv)

    discovery = discover_product_godot(REPO)
    engine = discovery.get("engine") or {}
    report: dict = {
        "schema_version": 1,
        "task": "P3-BC-E2",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "engine": {
            "binary_name": Path(str(engine.get("binary"))).name if engine.get("binary") else None,
            "resolved_via": engine.get("resolved_via"),
            "version": engine.get("version"),
            "status": engine.get("status"),
        },
        "driver_scene": DRIVER_SCENE,
        "timeout_s": args.timeout,
    }

    binary = engine.get("binary")
    if not binary or engine.get("status") != "SUCCESS":
        report.update({"overall": "NOT_FOUND",
                       "note": f"godot binary not resolved: {engine!r}"})
        _finish(report, args.out)
        return 1

    cmd = [str(binary), "--headless", "--path", str(REPO / "product"), DRIVER_SCENE]
    report["cmd"] = [c.replace(str(REPO), "<repo>") for c in cmd]
    started = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              timeout=args.timeout)
        rc, stdout, stderr = proc.returncode, proc.stdout or "", proc.stderr or ""
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        rc, timed_out = None, True
        stdout = _as_text(exc.stdout)
        stderr = _as_text(exc.stderr)
    duration_ms = int((time.monotonic() - started) * 1000)

    marker_re = re.compile(re.escape(MARKER) + r"(.*?)>>>", re.S)
    match = marker_re.search(stdout)
    driver_result = None
    if match:
        try:
            driver_result = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            report["marker_parse_error"] = str(exc)

    script_errors = sum(
        1 for line in (stdout + stderr).splitlines()
        if "SCRIPT ERROR" in line.upper()
    )
    e2 = (driver_result or {}).get("e2") or {}
    used_cells = int(e2.get("tile_used_cells") or 0)
    navmesh_points = int(e2.get("navmesh_points") or 0)
    assertions = {
        "player_present": bool(e2.get("player_spawned")),
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

    if timed_out:
        overall, note = "TOOL_FAILED", f"TIMEOUT after {args.timeout}s"
    elif rc not in (0, 1):
        overall, note = "TOOL_FAILED", f"abnormal engine exit rc={rc}"
    elif driver_result is None:
        overall, note = "TOOL_FAILED", "result marker not found in stdout"
    elif bool(driver_result.get("all_pass")) and assertions["all_pass"]:
        overall, note = "PASS", ""
    else:
        overall, note = "FAIL", "driver reported failure or P3-BC assertions unmet"

    report.update({
        "returncode": rc,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "driver_result": driver_result,
        "script_error_total": script_errors,
        "p3_bc_assertions": assertions,
        "overall": overall,
        "note": note,
        "stdout_head": stdout[:2000],
        "stderr_head": stderr[:2000],
    })
    _finish(report, args.out)
    return 0 if overall == "PASS" else 1


def _as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


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
