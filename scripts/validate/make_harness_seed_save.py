#!/usr/bin/env python3
"""B3-X0 S2 seed-save generator for the combat harness runtime.

Builds a GameState-compatible local save (user://_0_6_0.dat) so the isolated
APPDATA runtime boots straight into the character select with a playable
character.  Mirrors the schema in 04_recovered/Globals/GameState.gd:

  * file top level == GameState.global_configuration shape (do_save_game()
    serializes `saved_stats`, which IS that dict: save_version, settings,
    shared_stash, keybind_overrides, characters, completed_achievements,
    timestamp, checksum, stamp);
  * character == GameState.initial_configuration shape merged by GameState.migrate()
    (character_name/account_xp/account_level/... /mutation_tree_loadout
    {"class": "WARRIOR", "passives": ["root_warrior"]} /specialization_loadout
    {"class": null, "passives": ["root"]} /skill_loadout from
    generate_new_skill_loadout()/gene_loadout/orbs/outfit/help_tips/...);
  * mutation_tree_loadout.class must be non-null or migrate() erases the
    character; status fields must not reference removed classes;
  * needs_starter=false so the StarterPicker popup never blocks Hideout input;
  * stamp/checksum stay null on purpose: verify_stamp() tolerates a null stamp
    (marks the save modded and re-serializes it on load), which also gives the
    launcher a disk-level rewrite signal ("save_loaded").

Tooling-only: no game assets or recovered sources are touched.

Usage:
    python scripts/validate/make_harness_seed_save.py --out <path>
        [--character-name default] [--class-id WARRIOR] [--root-node root_warrior]
        [--account-level 1]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def make_settings() -> dict:
    return {
        "enable_music": True,
        "enable_sfx": True,
        "enable_drops": True,
        "enable_floating_damage": True,
        "enable_fullscreen": False,
        "enable_fx": True,
        "enable_status_bars": True,
        "enable_vsync": True,
        "enable_stats_panel": True,
        "enable_health_globe": True,
        "enable_floating_xp": True,
        "show_advanced_mods": True,
        "hide_low_level": False,
        "volume": {"music": 100, "sfx": 100, "drops": 100},
    }


def make_skill_loadout() -> dict:
    return {
        "primary": {"skill": None, "supports": {"a": None, "b": None, "c": None,
                                                "d": None, "e": None, "f": None}},
        "secondary": {"skill": None, "supports": {"a": None, "b": None,
                                                  "c": None, "d": None}},
        "support_one": {"skill": None, "supports": {"a": None, "b": None,
                                                    "c": None, "d": None}},
        "support_two": {"skill": None, "supports": {"a": None, "b": None}},
        "support_three": {"skill": None, "supports": {"a": None}},
        "support_four": {"skill": None, "supports": {"a": None}},
    }


def make_gene_loadout() -> dict:
    return {
        "WEAPON": {"slot_1": None, "slot_2": None},
        "BODY": {"slot_1": None},
        "HELMET": {"slot_1": None},
        "PANTS": {"slot_1": None},
        "GLOVES": {"slot_1": None},
        "BOOTS": {"slot_1": None},
        "BELT": {"slot_1": None},
        "AMULET": {"slot_1": None},
        "RING": {"slot_1": None, "slot_2": None},
        "MINOR": {"slot_1": None, "slot_2": None, "slot_3": None, "slot_4": None,
                  "slot_5": None, "slot_6": None, "slot_7": None, "slot_8": None},
    }


def make_character(name: str, class_id: str, root_node: str,
                   account_level: int) -> dict:
    return {
        "character_name": name,
        "account_level": account_level,
        "account_xp": 0,
        "account_xp_next": 50,
        "next_gene_id": 0,
        "needs_starter": False,
        "orbs": {"blue": 0, "green": 0, "red": 0, "gold": 0, "freeze": 0,
                 "corruption": 0, "tear": 0, "moon_shard": 0, "sun_shard": 0},
        "recent_stage": None,
        "completed_stages": {"root": True},
        "outfit": {"helmet": None, "head": None, "feet": None, "hands": None,
                   "pants": None, "back": None},
        "help_tips": {},
        "new_item_ids": {},
        "new_item_types": {},
        "tutorial_events": {},
        "mutation_tree_loadout": {"class": class_id, "passives": [root_node]},
        "specialization_loadout": {"class": None, "passives": ["root"]},
        "skill_loadout": make_skill_loadout(),
        "gene_loadout": make_gene_loadout(),
        "genes": {},
        "stored_mods": {},
        "filters": {},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--character-name", default="default")
    ap.add_argument("--class-id", default="WARRIOR")
    ap.add_argument("--root-node", default="root_warrior")
    ap.add_argument("--account-level", type=int, default=1)
    args = ap.parse_args()

    save = {
        "save_version": 1,
        "settings": make_settings(),
        "shared_stash": {},
        "keybind_overrides": {},
        "characters": {
            args.character_name: make_character(
                args.character_name, args.class_id, args.root_node,
                args.account_level),
        },
        "completed_achievements": [],
        "timestamp": 0,
        "checksum": None,
        "stamp": None,
    }

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(save, ensure_ascii=False, indent=2) + "\n"
    out.write_text(text, encoding="utf-8")

    print(f"seed save written: {out}")
    print(f"sha256: {hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    print(f"bytes: {len(text.encode('utf-8'))}")
    print(f"character: {args.character_name} class={args.class_id} "
          f"root={args.root_node} needs_starter=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())