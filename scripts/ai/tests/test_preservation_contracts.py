#!/usr/bin/env python3
"""P1-X3 unittests: preservation counts come from a recovered-source scan.

AGENT.MD approximate numbers are not a source of truth. A tiny fixture must
not produce those approx counts.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from migration.preservation import (  # noqa: E402
    REQUIRED_FAMILIES,
    scan_preservation,
)

# AGENT.MD approximate scale — tests prove a fixture does not yield these.
AGENT_MD_APPROX = {
    "classes": 4,
    "specializations": 8,
    "skills": 53,
    "supports": 60,
    "passives": 326,
    "keystones": 88,
    "stats": 149,
    "tags": 24,
}

CLASSES_GD = """extends Node
var PLAYABLE_CLASSES = {
\t"ROGUE": "ROGUE",
\t"MAGE": "MAGE",
}
var PLAYABLE_SPECIALIZATIONS = {
\t"WARLOCK": "WARLOCK",
}
"""

SKILLS_GD = """extends Node
var config = {
\t"Arc": { "name": "Arc" },
}
"""

SUPPORTS_GD = """extends Node
var supports = {
\t"AddedFire": { "name": "Added Fire" },
\t"AddedCold": { "name": "Added Cold" },
}
"""

TAGS_GD = """extends Node
enum Tags{
\tPROJECTILE,
\tAREA,
\tFIRE,
}
"""

STATS_GD = """extends Node
var stat_list = [
\t"health_max",
\t"movement_speed",
]
"""

GENES_GD = """extends Node
var GeneSlot = {
\t"WEAPON": "WEP",
\t"BODY": "BOD",
}
var BaseType = {
\t"MELEE_WEAPON": "MELEE_WEAPON",
}
"""

GAME_STATE_GD = """extends Node
var global_configuration = {
\t"save_version": 1,
\t"settings": {
\t\t"enable_music": true,
\t},
\t"characters": {},
}
var initial_configuration = {
\t"character_name": "default",
\t"orbs": { "blue": 0 },
}
"""

CONSTANTS_GD = """extends Node
enum StatusFlags{
\tCHILLED
\tBURNING
}
"""

PROJECT_GODOT = """config_version=4
[input]
dash={
"deadzone": 0.5,
"events": []
}
move_left={
"deadzone": 0.5,
"events": []
}
"""

TREE_KEYSTONES = """extends Node
var keystones = {
\t"TREE_GOLIATH": { "name": "Goliath" },
}
"""

UNIQUE_KEYSTONES = """extends Node
var keystones = {
\t"UNIQUE_FOO": { "name": "Foo" },
}
"""

SUPPORT_KEYSTONES = """extends Node
var keystones = {
}
"""

STATUS_GD = """extends Node
var status_effects = {
}
"""

PASSIVE_JSON = """{"nodes": [{"id": "root"}, {"id": "n1"}, {"id": "n2"}], "edges": []}
"""

SLOT_REQ = """extends Node
const requirements = {
\t"primary": { "level": 1 },
}
"""


def _write_fixture(root: Path) -> Path:
    recovered = root / "04_recovered"
    (recovered / "Globals" / "Keystones").mkdir(parents=True)
    (recovered / "passive_tree_data").mkdir(parents=True)
    (recovered / "Globals" / "PlayableClasses.gd").write_text(CLASSES_GD, encoding="utf-8")
    (recovered / "Globals" / "Skills.gd").write_text(SKILLS_GD, encoding="utf-8")
    (recovered / "Globals" / "SkillSupports.gd").write_text(SUPPORTS_GD, encoding="utf-8")
    (recovered / "Globals" / "SkillTags.gd").write_text(TAGS_GD, encoding="utf-8")
    (recovered / "Globals" / "StatsInfo.gd").write_text(STATS_GD, encoding="utf-8")
    (recovered / "Globals" / "Genes.gd").write_text(GENES_GD, encoding="utf-8")
    (recovered / "Globals" / "GameState.gd").write_text(GAME_STATE_GD, encoding="utf-8")
    (recovered / "Globals" / "Constants.gd").write_text(CONSTANTS_GD, encoding="utf-8")
    (recovered / "Globals" / "StatusEffects.gd").write_text(STATUS_GD, encoding="utf-8")
    (recovered / "Globals" / "SlotRequirements.gd").write_text(SLOT_REQ, encoding="utf-8")
    (recovered / "Globals" / "Keystones" / "TreeKeystones.gd").write_text(TREE_KEYSTONES, encoding="utf-8")
    (recovered / "Globals" / "Keystones" / "UniqueKeystones.gd").write_text(UNIQUE_KEYSTONES, encoding="utf-8")
    (recovered / "Globals" / "Keystones" / "SupportKeystones.gd").write_text(SUPPORT_KEYSTONES, encoding="utf-8")
    (recovered / "project.godot").write_text(PROJECT_GODOT, encoding="utf-8")
    (recovered / "passive_tree_data" / "passive_tree_gen.json").write_text(PASSIVE_JSON, encoding="utf-8")
    return recovered


class PreservationContractsTest(unittest.TestCase):
    def test_fixture_counts_come_from_scan_not_agent_md(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = _write_fixture(Path(td))
            report = scan_preservation(recovered)
        self.assertEqual(report["source_of_truth"], "recovered_source_scan")
        self.assertTrue(report["agent_md_approx_not_used"])
        for family in REQUIRED_FAMILIES:
            self.assertIn(family, report["families"])
            self.assertGreater(report["families"][family]["count"], 0, family)
        self.assertEqual(report["counts"]["classes"], 2)
        self.assertEqual(report["counts"]["specializations"], 1)
        self.assertEqual(report["counts"]["skills"], 1)
        self.assertEqual(report["counts"]["supports"], 2)
        self.assertEqual(report["counts"]["passives"], 3)
        self.assertEqual(report["counts"]["keystones"], 2)
        self.assertEqual(report["counts"]["stats"], 2)
        self.assertEqual(report["counts"]["tags"], 3)
        self.assertEqual(report["counts"]["equipment_slots"], 2)
        self.assertGreaterEqual(report["counts"]["save_keys"], 2)
        self.assertIn("dash", report["families"]["input_actions"]["ids"])
        # A scan that copied AGENT.MD approx would not match this fixture.
        for family, approx in AGENT_MD_APPROX.items():
            self.assertNotEqual(
                report["counts"][family], approx,
                f"{family} matched AGENT.MD approx {approx}; scanner is not reading the fixture",
            )

    def test_records_point_at_recovered_files(self):
        with tempfile.TemporaryDirectory() as td:
            recovered = _write_fixture(Path(td))
            report = scan_preservation(recovered)
        for family, payload in report["families"].items():
            self.assertTrue(payload["records"], family)
            for rec in payload["records"]:
                self.assertEqual(rec["source_kind"], "recovered_source_scan")
                self.assertTrue(rec["source_file"], family)
                self.assertFalse(str(rec["source_file"]).replace("\\", "/").endswith("AGENT.MD"))

    def test_shipped_scanner_does_not_hardcode_agent_md_counts(self):
        src = (REPO / "scripts" / "migration" / "preservation.py").read_text(encoding="utf-8")
        self.assertNotIn("passive_nodes = 326", src)
        self.assertNotIn('"skills": 53', src)
        self.assertNotIn("base_classes = 4", src)
        self.assertNotIn("AGENT_MD_APPROX", src)
        self.assertIn("recovered_source_scan", src)


if __name__ == "__main__":
    unittest.main()
