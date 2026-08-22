#!/usr/bin/env python3
"""P4-A probe CLI: R1 readability + R2 camera/screen feedback assertions.

Usage:
    python scripts/validate/p4_a_readability_probe.py \
        --out migration/conversion/p4_a_readability_feedback.json --timeout 300
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
            probe_id="P4-A-R1-R2",
            exit_criteria=["R1", "R2"],
            driver_scene="res://scenes/Levels/_validate/P4AFeedbackDriver.tscn",
            default_out=Path("migration/conversion/p4_a_readability_feedback.json"),
            proves=(
                "enemy hit flash (modulate overbright tween fires and restores), "
                "elite ring marker attachment, kill zoom punch, player red "
                "vignette flash, screen shake offset jitter and Engine.time_scale "
                "hit-stop — each asserted to fire AND restore inside the real "
                "World.tscn chain."
            ),
            not_proven=(
                "subjective feel/tuning quality (human judgement); visual "
                "correctness of the hit_flash shader on textured sprites."
            ),
        )
    )
