#!/usr/bin/env python3
"""P4-A probe CLI: C2 saved-position application on world re-entry.

Usage:
    python scripts/validate/p4_a_position_probe.py \
        --out migration/conversion/p4_a_position_apply.json --timeout 300
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
            task="P4-A",
            probe_id="P4-A-C2",
            exit_criteria=["C2"],
            driver_scene="res://scenes/Levels/_validate/P4APositionDriver.tscn",
            default_out=Path("migration/conversion/p4_a_position_apply.json"),
            proves=(
                "do_save_game persists the H2 position field {x,y,level}; a "
                "later world entry teleports the player to the saved position "
                "(applied after the default spawn logic); saves without the "
                "position field keep the default Vector2.ZERO spawn."
            ),
            not_proven=(
                "cross-level position restore (level mismatch guard is asserted "
                "by code review only); save-file portability across machines."
            ),
        )
    )
