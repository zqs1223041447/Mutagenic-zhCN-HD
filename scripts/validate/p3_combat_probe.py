#!/usr/bin/env python3
"""P3-C combat probe CLI (Exit Criteria E4/E5).

Launches the headless driver scene res://scenes/Mobs/probes/p3_combat_probe.tscn
(instantiate >=1 skill + >=1 mob, skill hit lowers HP, zero HP triggers
death/removal) and emits machine-readable evidence.

    python scripts/validate/p3_combat_probe.py [--out PATH] [--timeout S]
"""

from __future__ import annotations

from pathlib import Path

from p3_probe_common import probe_main

TASK = "P3-C"
PROBE_ID = "p3_combat_probe"


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    return probe_main(
        argv,
        task=TASK,
        probe_id=PROBE_ID,
        exit_criteria=["E4", "E5"],
        driver_scene="res://scenes/Mobs/probes/p3_combat_probe.tscn",
        default_out=root / "migration" / "conversion" / "p3_c_combat.json",
        proves=("a real instantiated skill node produces a damage bundle that "
                "reduces a real instantiated mob's HP (E4) and driving it to "
                "zero fires the died signal, runs Mob._on_death and removes "
                "the mob from the tree (E5), headlessly"),
        not_proven=("player-cast playable skills through the projectile layer, "
                    "visual/audio feedback, and drop-table spawning (Pickups "
                    "scenes still absent from product/)"),
    )


if __name__ == "__main__":
    raise SystemExit(main())
