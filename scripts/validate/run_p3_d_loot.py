#!/usr/bin/env python3
"""P3-D probe CLI: E6 loot loop (drop spawn -> pickup -> queryable inventory).

Usage:
    python scripts/validate/run_p3_d_loot.py \
        --out migration/conversion/p3_d_loot.json --timeout 300
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p3_probe_common import cli_main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        cli_main(
            task_id="P3-D",
            marker="P3D_RESULT_JSON<<<",
            driver_scene="res://scenes/Levels/_validate/P3DDriver.tscn",
            default_out="migration/conversion/p3_d_loot.json",
        )
    )
