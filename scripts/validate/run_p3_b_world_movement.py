#!/usr/bin/env python3
"""P3-B probe CLI: E2 world entry + tile pipeline, E3 movement + dash.

Usage:
    python scripts/validate/run_p3_b_world_movement.py \
        --out migration/conversion/p3_h1_world_chain.json --timeout 240

P3-H1: default entry path is the production World.tscn chain
(world_entry_mode="world_scene"); manual_assembly remains as documented
fallback when out-of-domain parse errors block scene load.

The shared p3_probe_common.probe_main writes raw engine argv into
evidence["command"]; this wrapper post-sanitizes host-absolute paths to
"<repo>/..." so migration/conversion/*.json stays clean for abs_path_scan.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_probe_common import probe_main  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def _sanitize_evidence(out_path: Path) -> None:
    """Mask host-absolute paths in the evidence 'command' field."""
    try:
        data = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    changed = False
    for key in ("command",):
        val = data.get(key)
        if isinstance(val, list):
            data[key] = [
                "<repo>/" + str(p).replace("\\", "/").split("/Mutagenic-zhCN-HD/", 1)[-1]
                if "Mutagenic-zhCN-HD" in str(p) else p
                for p in val
            ]
            changed = True
    if changed:
        out_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    argv = sys.argv[1:]
    out = Path("migration/conversion/p3_b_world_movement.json")
    if "--out" in argv:
        idx = argv.index("--out")
        if idx + 1 < len(argv):
            out = Path(argv[idx + 1])
    code = probe_main(
        argv,
        task="P3-B",
        probe_id="P3-B-E2-E3",
        exit_criteria=["E2", "E3"],
        driver_scene="res://scenes/Levels/_validate/P3BDriver.tscn",
        default_out=out,
        proves=(
            "production world entry: change_scene_to_file(World.tscn) loads, "
            "World.switch_levels spawns Player + TestLevel, tile pipeline "
            "(read_tiles -> set_cells_terrain_connect -> navmesh) runs with a "
            "live player (E2); input-driven movement displaces the player and "
            "the dash action fires with cooldown state change (E3)."
        ),
        not_proven=(
            "GUI/HUD visual fidelity inside World; combat balance; dash "
            "displacement magnitude (state-change assertion per spec)."
        ),
    )
    out_path = out if out.is_absolute() else (REPO / out)
    _sanitize_evidence(out_path)
    raise SystemExit(code)
