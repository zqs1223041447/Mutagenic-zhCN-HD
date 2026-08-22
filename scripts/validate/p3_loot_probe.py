#!/usr/bin/env python3
"""P3-D loot probe CLI (Exit Criteria E6).

Launches the headless driver scene res://scenes/UI/probes/p3_loot_probe.tscn
(drop stub collides with a player-group test entity; the REAL Stats.add_orb
inventory API credits the pickup and the orb_pickup signal fires) and emits
machine-readable evidence.

    python scripts/validate/p3_loot_probe.py [--out PATH] [--timeout S]
"""

from __future__ import annotations

from pathlib import Path

from p3_probe_common import probe_main

TASK = "P3-D"
PROBE_ID = "p3_loot_probe"


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    return probe_main(
        argv,
        task=TASK,
        probe_id=PROBE_ID,
        exit_criteria=["E6"],
        driver_scene="res://scenes/UI/probes/p3_loot_probe.tscn",
        default_out=root / "migration" / "conversion" / "p3_d_loot.json",
        proves=("a spawned drop picked up through real Area2D collision with a "
                "player-group entity lands in queryable inventory state "
                "(Stats.metrics.orbs.blue 0 -> 3) with the orb_pickup signal "
                "emitted by production code"),
        not_proven=("the real OrbPickup/GenePickup scenes (product/scenes/"
                    "Pickups/** missing, outside this lane's write domain); "
                    "the drop itself is a test stub mirroring Pickup.gd's "
                    "collision contract"),
    )


if __name__ == "__main__":
    raise SystemExit(main())
