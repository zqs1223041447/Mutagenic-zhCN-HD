#!/usr/bin/env python3
"""Generate C5-L16: zone names (Levels.gd), monster names (MonsterStats.gd),
starter build names/descriptions (StarterBuilds.gd), minimap/map mod text
(MapMods.gd, Minimap.gd, MapNode.gd), and remaining edge UI strings.

Each unit old_text/new_text = the full stripped serialized source line.
Translations follow docs/zh_CN_glossary.md. Every old_text is verified:
exact line match at the declared line number and occurrence count.
Internal identifiers (config keys, MonsterType enum keys, template keys) stay
English; only player-visible display values are translated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_recovered"
OUT = ROOT / "mods/c5-l16-zones-monsters-ui-zhcn/mod.json"
TARGET_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"

TESTS = [
    "locked_units_and_preimages",
    "exact_unit_application",
    "resource_contract",
    "declared_delta",
    "compiled_script_load",
    "pck_checksum",
    "exe_structure",
    "pck_roundtrip",
    "boot",
    "phase_checkpoint_zones_monsters_ui_zhcn",
]

# (rel_path, line_no, old_line, new_line, source_text, translation, occurrences)
ENTRIES = [
    # ============ Globals/Levels.gd : zone names (display only) ============
    ("Globals/Levels.gd", 76, '"name": "Chilly Cavern", ', '"name": "寒霜洞窟", ', "Chilly Cavern", "寒霜洞窟", 1),
    ("Globals/Levels.gd", 86, '"name": "Musty Den", ', '"name": "霉味巢穴", ', "Musty Den", "霉味巢穴", 1),
    ("Globals/Levels.gd", 96, '"name": "Gemling Cave", ', '"name": "宝石洞穴", ', "Gemling Cave", "宝石洞穴", 1),
    ("Globals/Levels.gd", 106, '"name": "Pit", ', '"name": "深坑", ', "Pit", "深坑", 1),
    ("Globals/Levels.gd", 116, '"name": "Grasslands", ', '"name": "草原", ', "Grasslands", "草原", 1),
    ("Globals/Levels.gd", 126, '"name": "Blood Shrine", ', '"name": "血祭神殿", ', "Blood Shrine", "血祭神殿", 1),
    ("Globals/Levels.gd", 136, '"name": "Catacombs", ', '"name": "地下墓穴", ', "Catacombs", "地下墓穴", 1),
    ("Globals/Levels.gd", 146, '"name": "Field of Despair", ', '"name": "绝望原野", ', "Field of Despair", "绝望原野", 1),
    ("Globals/Levels.gd", 156, '"name": "Sandstorm", ', '"name": "沙暴", ', "Sandstorm", "沙暴", 1),
    ("Globals/Levels.gd", 166, '"name": "Dungeon", ', '"name": "地牢", ', "Dungeon", "地牢", 1),
    ("Globals/Levels.gd", 176, '"name": "The Gatekeeper", ', '"name": "守门者", ', "The Gatekeeper", "守门者", 1),
    ("Globals/Levels.gd", 187, '"name": "Sludge", ', '"name": "泥沼怪", ', "Sludge", "泥沼怪", 1),
    ("Globals/Levels.gd", 198, '"name": "Mutated Spider", ', '"name": "变异蜘蛛", ', "Mutated Spider", "变异蜘蛛", 1),
    ("Globals/Levels.gd", 209, '"name": "Spirit of the Ancients", ', '"name": "远古之灵", ', "Spirit of the Ancients", "远古之灵", 1),
    ("Globals/Levels.gd", 220, '"name": "Challenge Ladder 1", ', '"name": "挑战天梯 1", ', "Challenge Ladder 1", "挑战天梯 1", 1),
    ("Globals/Levels.gd", 231, '"name": "Challenge Ladder 2", ', '"name": "挑战天梯 2", ', "Challenge Ladder 2", "挑战天梯 2", 1),
    ("Globals/Levels.gd", 242, '"name": "Challenge Ladder 3", ', '"name": "挑战天梯 3", ', "Challenge Ladder 3", "挑战天梯 3", 1),
    ("Globals/Levels.gd", 253, '"name": "Challenge Ladder 4", ', '"name": "挑战天梯 4", ', "Challenge Ladder 4", "挑战天梯 4", 1),
    ("Globals/Levels.gd", 264, '"name": "Hideout", ', '"name": "藏身处", ', "Hideout", "藏身处", 1),
    ("Globals/Levels.gd", 274, '"name": "Testing Zone", ', '"name": "测试区域", ', "Testing Zone", "测试区域", 1),

    # ============ Globals/MonsterStats/MonsterStats.gd : monster names ============
    ("Globals/MonsterStats/MonsterStats.gd", 5, '"name": "Training Dummy", ', '"name": "训练假人", ', "Training Dummy", "训练假人", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 19, '"name": "Skeleton Archer", ', '"name": "骷髅弓箭手", ', "Skeleton Archer", "骷髅弓箭手", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 35, '"name": "Dark Ninja", ', '"name": "暗影忍者", ', "Dark Ninja", "暗影忍者", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 53, '"name": "Skeleton Hexer", ', '"name": "骷髅咒术师", ', "Skeleton Hexer", "骷髅咒术师", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 70, '"name": "Ice Golem", ', '"name": "寒冰魔像", ', "Ice Golem", "寒冰魔像", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 85, '"name": "Attack Dog", ', '"name": "攻击犬", ', "Attack Dog", "攻击犬", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 103, '"name": "Shock Dog", ', '"name": "闪电犬", ', "Shock Dog", "闪电犬", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 121, '"name": "Skeleton Assassin", ', '"name": "骷髅刺客", ', "Skeleton Assassin", "骷髅刺客", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 137, '"name": "Chilly Bones", ', '"name": "寒骨", ', "Chilly Bones", "寒骨", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 154, '"name": "Skeleton Mage", ', '"name": "骷髅法师", ', "Skeleton Mage", "骷髅法师", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 170, '"name": "Fire Bomber", ', '"name": "火焰爆破者", ', "Fire Bomber", "火焰爆破者", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 186, '"name": "Skeleton Sparker", ', '"name": "骷髅电击者", ', "Skeleton Sparker", "骷髅电击者", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 202, '"name": "Zombie", ', '"name": "僵尸", ', "Zombie", "僵尸", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 217, '"name": "Spider", ', '"name": "蜘蛛", ', "Spider", "蜘蛛", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 233, '"name": "Skeletor", ', '"name": "骷髅王", ', "Skeletor", "骷髅王", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 249, '"name": "The Gatekeeper", ', '"name": "守门者", ', "The Gatekeeper", "守门者", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 269, '"name": "Sludge", ', '"name": "泥沼怪", ', "Sludge", "泥沼怪", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 289, '"name": "Spirit of the Ancients", ', '"name": "远古之灵", ', "Spirit of the Ancients", "远古之灵", 1),
    ("Globals/MonsterStats/MonsterStats.gd", 310, '"name": "Mutated Spider", ', '"name": "变异蜘蛛", ', "Mutated Spider", "变异蜘蛛", 1),

    # ============ Globals/MapMods.gd : map mod prefixes ============
    ("Globals/MapMods.gd", 281, 'var prefix = "Enemies have "', 'var prefix = "敌人拥有 "', '"Enemies have "', '"敌人拥有 "', 1),
    ("Globals/MapMods.gd", 283, 'prefix = "Players have "', 'prefix = "玩家拥有 "', '"Players have "', '"玩家拥有 "', 1),

    # ============ Scenes/Minimap/Minimap.gd ============
    ("Scenes/Minimap/Minimap.gd", 30, 'label.text = "Zone Mods"', 'label.text = "区域词缀"', "Zone Mods", "区域词缀", 1),
    ("Scenes/Minimap/Minimap.gd", 46, 'label.text = "Players have 25% More Movement Speed"', 'label.text = "玩家拥有 25% 更多移动速度"', "Players have 25% More Movement Speed", "玩家拥有 25% 更多移动速度", 1),
    ("Scenes/Minimap/Minimap.gd", 52, 'label.text = str(stepify(Globals.stage_iiq * 100.0, 1)) + "% Increased Quantity of Items Found"', 'label.text = str(stepify(Globals.stage_iiq * 100.0, 1)) + "% 物品掉落数量增加"', '"% Increased Quantity of Items Found"', '"% 物品掉落数量增加"', 1),
    ("Scenes/Minimap/Minimap.gd", 59, 'label.text = str(stepify(Globals.stage_iir * 100.0, 1)) + "% Increased Rarity of Items Found"', 'label.text = str(stepify(Globals.stage_iir * 100.0, 1)) + "% 物品掉落稀有度增加"', '"% Increased Rarity of Items Found"', '"% 物品掉落稀有度增加"', 1),

    # ============ Scenes/Popups/Dialogs/WorldMap/MapNode.gd ============
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.gd", 22, '$MapButton / StatInfoContainer / VBoxContainer / ZoneLabel.text = "Zone Level: " + str(zone_level)', '$MapButton / StatInfoContainer / VBoxContainer / ZoneLabel.text = "区域等级：" + str(zone_level)', '"Zone Level: "', '"区域等级："', 1),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.gd", 42, '$MapButton / StatInfoContainer / VBoxContainer / ItemQuanityLabel.text = str(stepify(iiq * 100.0, 1)) + "% Increased Quantity of Items Found"', '$MapButton / StatInfoContainer / VBoxContainer / ItemQuanityLabel.text = str(stepify(iiq * 100.0, 1)) + "% 物品掉落数量增加"', '"% Increased Quantity of Items Found"', '"% 物品掉落数量增加"', 1),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.gd", 45, '$MapButton / StatInfoContainer / VBoxContainer / ItemRarityLabel.text = str(stepify(iir * 100.0, 1)) + "% Increased Rarity of Items Found"', '$MapButton / StatInfoContainer / VBoxContainer / ItemRarityLabel.text = str(stepify(iir * 100.0, 1)) + "% 物品掉落稀有度增加"', '"% Increased Rarity of Items Found"', '"% 物品掉落稀有度增加"', 1),

    # ============ Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.gd ============
    ("Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.gd", 21, '$DropLevel.text = "Minimum Drop Level: " + str(data.min_level_requirement)', '$DropLevel.text = "最低掉落等级：" + str(data.min_level_requirement)', '"Minimum Drop Level: "', '"最低掉落等级："', 1),

    # ============ Scenes/Stats.gd : entity name ============
    ("Scenes/Stats.gd", 2194, 'return "You"', 'return "你"', "You", "你", 1),

    # ============ Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.gd ============
    ("Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.gd", 83, 'popup.label = "New Name"', 'popup.label = "新名称"', "New Name", "新名称", 1),

    # ============ Scenes/Popups/Dialogs/GeneEditor/GeneButton.gd ============
    ("Scenes/Popups/Dialogs/GeneEditor/GeneButton.gd", 138, 'popup.window_title = "Permanently Delete this Item?"', 'popup.window_title = "永久删除该物品？"', "Permanently Delete this Item?", "永久删除该物品？", 1),

    # ============ Scenes/Popups/Dialogs/GeneEditor/CraftButton.gd ============
    ("Scenes/Popups/Dialogs/GeneEditor/CraftButton.gd", 15, '$CostBox / CostLabel.text = "Free"', '$CostBox / CostLabel.text = "免费"', "Free", "免费", 1),

    # ============ Globals/StarterBuilds.gd : starter build names/descriptions ============
    ("Globals/StarterBuilds.gd", 6, '"name": "Lightning Starter", ', '"name": "闪电开局", ', "Lightning Starter", "闪电开局", 1),
    ("Globals/StarterBuilds.gd", 7, '"description": "Deal massive damage with Lightning Skills.", ', '"description": "使用闪电技能造成大量伤害。", ', "Deal massive damage with Lightning Skills.", "使用闪电技能造成大量伤害。", 1),
    ("Globals/StarterBuilds.gd", 36, '"name": "Fire Starter", ', '"name": "火焰开局", ', "Fire Starter", "火焰开局", 1),
    ("Globals/StarterBuilds.gd", 37, '"description": "Set enemies on fire with Fire Skills", ', '"description": "使用火焰技能点燃敌人。", ', "Set enemies on fire with Fire Skills", "使用火焰技能点燃敌人。", 1),
    ("Globals/StarterBuilds.gd", 66, '"name": "Cold Starter", ', '"name": "寒冰开局", ', "Cold Starter", "寒冰开局", 1),
    ("Globals/StarterBuilds.gd", 67, '"description": "Freeze your enemies with Cold Skills.", ', '"description": "使用寒冰技能冻结敌人。", ', "Freeze your enemies with Cold Skills.", "使用寒冰技能冻结敌人。", 1),
    ("Globals/StarterBuilds.gd", 98, '"name": "Gunner", ', '"name": "枪手", ', "Gunner", "枪手", 1),
    ("Globals/StarterBuilds.gd", 99, '"description": "Mow down enemies with a machine gun.", ', '"description": "用机枪扫射敌人。", ', "Mow down enemies with a machine gun.", "用机枪扫射敌人。", 1),
    ("Globals/StarterBuilds.gd", 129, '"name": "Destroyer", ', '"name": "毁灭者", ', "Destroyer", "毁灭者", 1),
    ("Globals/StarterBuilds.gd", 130, '"description": "Blast down enemies with a powerful shotgun.", ', '"description": "用强力霰弹枪轰杀敌人。", ', "Blast down enemies with a powerful shotgun.", "用强力霰弹枪轰杀敌人。", 1),
    ("Globals/StarterBuilds.gd", 160, '"name": "Bleed Archer", ', '"name": "流血弓手", ', "Bleed Archer", "流血弓手", 1),
    ("Globals/StarterBuilds.gd", 161, '"description": "Damage enemies with a powerful bow attack.", ', '"description": "用强力弓箭攻击伤害敌人。", ', "Damage enemies with a powerful bow attack.", "用强力弓箭攻击伤害敌人。", 1),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_patches(entries):
    patches = []
    for rel, line_no, old, new, src, tr, occurrences in entries:
        src_path = SRC / rel
        content = src_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        if line_no - 1 >= len(lines):
            raise SystemExit(f"line out of range: {rel}:{line_no}")
        actual = lines[line_no - 1].strip()
        old_s = old.strip()
        new_s = new.strip()
        if old_s != actual:
            raise SystemExit(f"line mismatch {rel}:{line_no}\n expected: {old_s!r}\n actual:   {actual!r}")
        count = content.count(old_s)
        if count != occurrences:
            raise SystemExit(f"occurrence {count} != {occurrences} for {old_s!r} at {rel}:{line_no}")
        preimage = sha256_file(src_path).upper()
        col = actual.find('"') + 2
        unit_id = f"{rel}:{line_no}:{col}"
        patches.append({
            "path": rel,
            "field": "text",
            "classification": "TEXT_PATCH",
            "unit_id": unit_id,
            "old_text": old_s,
            "new_text": new_s,
            "preimage_sha256": preimage,
            "expected_occurrences": occurrences,
            "source_text": src,
            "translation": tr,
            "placeholders": [],
            "format_tokens": [],
            "tests": [
                "unit_id_exact_match",
                "placeholder_conservation",
                "token_conservation",
                "resource_contract",
                "declared_delta",
                "compiled_script_load",
            ],
        })
    return patches


def main():
    patches = build_patches(ENTRIES)
    files = sorted({p["path"] for p in patches})
    manifest = {
        "id": "c5-l16-zones-monsters-ui-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": TARGET_SHA,
        "dependencies": [],
        "conflicts": [],
        "scope": f"C5-L16: zone names (Levels.gd), monster names (MonsterStats.gd), map mod prefixes (MapMods.gd), minimap/world-map labels (Minimap.gd, MapNode.gd), unique help drop level, entity name (Stats.gd), gene editor edge strings (GeneLoadout/GeneButton/CraftButton), starter build names+descriptions (StarterBuilds.gd); {len(patches)} units across {len(files)} scripts; internal keys/identifiers untouched",
        "entities": [
            {"kind": "localization_unit", "id": p["unit_id"], "classification": "DISPLAY_SAFE",
             "confidence": "INFERENCE_HIGH",
             "expected_runtime_effect": f"displays {p['translation']}"}
            for p in patches
        ],
        "patches": patches,
        "asset_overlays": [],
        "tests": TESTS,
        "not_proven": "visual layout quality, persistence, gameplay, broad localization, or release readiness",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest written: {OUT}")
    print(f"patches: {len(patches)}")
    print(f"files: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
