#!/usr/bin/env python3
"""P3-E UI probe CLI (Exit Criteria E7).

Launches the headless driver scene res://scenes/UI/probes/p3_ui_probe.tscn
(open SkillSelect and PassiveTreePopup via PopupManager, verify no crash,
close both, popup stack drains to zero) and emits machine-readable evidence.

    python scripts/validate/p3_ui_probe.py [--out PATH] [--timeout S]
"""

from __future__ import annotations

from pathlib import Path

from p3_probe_common import probe_main

TASK = "P3-E"
PROBE_ID = "p3_ui_probe"


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    return probe_main(
        argv,
        task=TASK,
        probe_id=PROBE_ID,
        exit_criteria=["E7"],
        driver_scene="res://scenes/UI/probes/p3_ui_probe.tscn",
        default_out=root / "migration" / "conversion" / "p3_e_ui.json",
        proves=("the skill screen and the passive tree screen open headlessly "
                "through PopupManager against a seeded character, build their "
                "content (passive nodes instantiate) and close cleanly back "
                "to an empty popup stack without crashing"),
        not_proven=("visual layout/rendering fidelity, controller navigation "
                    "and allocation interactions inside the screens"),
    )


if __name__ == "__main__":
    raise SystemExit(main())
