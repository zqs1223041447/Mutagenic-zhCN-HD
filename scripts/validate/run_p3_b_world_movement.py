#!/usr/bin/env python3
"""P3-B probe CLI: E2 world entry + tile pipeline, E3 movement + dash.

Usage:
    python scripts/validate/run_p3_b_world_movement.py \
        --out migration/conversion/p3_b_world_movement.json --timeout 240
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_probe_common import probe_main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        probe_main(
            sys.argv[1:],
            task="P3-B",
            probe_id="P3-B-E2-E3",
            exit_criteria=["E2", "E3"],
            driver_scene="res://scenes/Levels/_validate/P3BDriver.tscn",
            default_out=Path("migration/conversion/p3_b_world_movement.json"),
            proves=(
                "world entry with a live player on TestLevel exercises "
                "read_tiles -> process_tiles -> set_cells_terrain_connect and "
                "navmesh build (E2); input-driven movement displaces the player "
                "and the dash action fires with cooldown state change (E3)."
            ),
            not_proven=(
                "World.tscn full-chain entry when blocked by out-of-domain parse "
                "errors (recorded in result.world_entry_mode / blocked note); "
                "combat balance or mob AI correctness."
            ),
        )
    )
