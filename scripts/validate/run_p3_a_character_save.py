#!/usr/bin/env python3
"""P3-A probe CLI: E1 character entry + E8 save/load roundtrip.

Usage:
    python scripts/validate/run_p3_a_character_save.py \
        --out migration/conversion/p3_a_character_save.json --timeout 240
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
            task="P3-A",
            probe_id="P3-A-E1-E8",
            exit_criteria=["E1", "E8"],
            driver_scene="res://scenes/Levels/_validate/P3ADriver.tscn",
            default_out=Path("migration/conversion/p3_a_character_save.json"),
            proves=(
                "headless boot reaches Menu via LoadGame; StartButton opens the "
                "CharacterSelect popup; a character can be created and selected "
                "(E1); do_save_game writes a parsable save whose identity/class/"
                "account_level/account_xp survive GameState.load_game (E8)."
            ),
            not_proven=(
                "player-position persistence (save schema defines no position "
                "field); rendering/input fidelity of the real UI."
            ),
        )
    )
