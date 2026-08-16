#!/usr/bin/env python3
"""Generate C5-L12: stat display names (StatsInfo.gd stat_name), skill tag names
(SkillTags.gd TagNames), and runtime stat prefixes (Base/Added/Increased/More)
used in StatsInfo.gd render functions and EscapeMenu.gd stat breakdown.

Each unit old_text/new_text = the full stripped serialized source line.
Translations follow the zh_CN glossary (docs/zh_CN_glossary.md).
Every old_text is verified: exact line match at the declared line number and
occurrence count == expected (1, or 2 for identical duplicated lines).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")
OUT = ROOT / "mods/c5-l12-stats-tags-zhcn/mod.json"

TARGET_ORIGINAL_SHA256 = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"

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
    "phase_checkpoint_skills_tree_zhcn",
]

# ---- stat_name dict (key -> zh_CN), keys in source-file order (line 515-696) ----
STAT_NAME_TRANSLATIONS = {
    "health_max": "最大生命",
    "health_regen": "生命再生",
    "health_regen_percent": "最大生命再生",
    "health_recovery_rate": "生命再生速率",
    "constitution": "体质",
    "strength": "力量",
    "agility": "敏捷",
    "wisdom": "智慧",
    "finesse": "灵巧",
    "swiftness_boon": "迅捷恩惠上限",
    "precision_boon": "精准恩惠上限",
    "toughness_boon": "坚韧恩惠上限",
    "boon_duration": "恩惠持续时间",
    "projectile_count": "投射物数量",
    "movement_speed": "移动速度",
    "projectile_speed": "投射物速度",
    "cast_speed": "施法速度",
    "mitigation": "护甲",
    "evasion": "闪避",
    "crit_chance": "暴击几率",
    "crit_multi": "暴击伤害倍率",
    "physical_resistance": "物理抗性",
    "lightning_resistance": "闪电抗性",
    "cold_resistance": "寒冷抗性",
    "fire_resistance": "火焰抗性",
    "toxic_resistance": "毒素抗性",
    "maximum_physical_resistance": "物理抗性上限",
    "maximum_lightning_resistance": "闪电抗性上限",
    "maximum_cold_resistance": "寒冷抗性上限",
    "maximum_fire_resistance": "火焰抗性上限",
    "maximum_toxic_resistance": "毒素抗性上限",
    "curse_resistance": "诅咒抗性",
    "block_chance": "格挡几率",
    "life_gain_on_block": "格挡时回复生命",
    "life_gain_on_hit": "命中时回复生命",
    "ailment_avoidance": "异常回避",
    "crit_resistance": "暴击抗性",
    "all_damage": "伤害",
    "damage_per_boon": "每恩惠获得伤害",
    "damage_per_25_attributes": "每 25 点总属性获得伤害",
    "projectile_damage": "投射物伤害",
    "area_damage": "范围伤害",
    "dot_damage": "持续伤害倍率",
    "hit_damage": "命中伤害",
    "physical_damage": "物理伤害",
    "lightning_damage": "闪电伤害",
    "cold_damage": "寒冷伤害",
    "fire_damage": "火焰伤害",
    "toxic_damage": "毒素伤害",
    "physical_penetration": "物理穿透",
    "lightning_penetration": "闪电穿透",
    "cold_penetration": "寒冷穿透",
    "fire_penetration": "火焰穿透",
    "toxic_penetration": "毒素穿透",
    "elemental_penetration": "元素穿透",
    "physical_ailment_effect": "物理异常效果",
    "lightning_ailment_effect": "闪电异常效果",
    "cold_ailment_effect": "寒冷异常效果",
    "fire_ailment_effect": "火焰异常效果",
    "toxic_ailment_effect": "毒素异常效果",
    "physical_ailment_chance": "物理异常几率",
    "lightning_ailment_chance": "闪电异常几率",
    "cold_ailment_chance": "寒冷异常几率",
    "fire_ailment_chance": "火焰异常几率",
    "toxic_ailment_chance": "毒素异常几率",
    "ailment_duration": "异常持续时间",
    "amplify_ailment_chance": "强化异常几率",
    "vulnerable_chance": "命中时施加易伤的几率",
    "vulnerable_effect": "易伤效果",
    "exposure_chance": "命中时施加暴露的几率",
    "exposure_effect": "暴露效果",
    "infection_count": "感染传播数量",
    "swiftness_boon_on_hit_chance": "命中时获得迅捷恩惠的几率",
    "toughness_boon_on_hit_chance": "命中时获得坚韧恩惠的几率",
    "precision_boon_on_crit_chance": "暴击时获得精准恩惠的几率",
    "toughness_boon_on_get_hit_chance": "受击时获得坚韧恩惠的几率",
    "swiftness_boon_on_kill_chance": "击杀时获得迅捷恩惠的几率",
    "precision_boon_on_kill_chance": "击杀时获得精准恩惠的几率",
    "toughness_boon_on_kill_chance": "击杀时获得坚韧恩惠的几率",
    "extra_physical_as_lightning_per_swiftness": "每迅捷恩惠物理伤害额外获得闪电伤害",
    "extra_physical_as_cold_per_precision": "每精准恩惠物理伤害额外获得寒冷伤害",
    "extra_physical_as_fire_per_toughness": "每坚韧恩惠物理伤害额外获得火焰伤害",
    "aoe_per_precision": "每精准恩惠提高范围效果",
    "aoe_per_swiftness": "每迅捷恩惠提高范围效果",
    "aoe_per_toughtness": "每坚韧恩惠提高范围效果",
    "physical_per_25_strength": "每 25 力量获得物理伤害",
    "lightning_per_25_agility": "每 25 敏捷获得闪电伤害",
    "fire_per_25_constitution": "每 25 体质获得火焰伤害",
    "cold_per_25_wisdom": "每 25 智慧获得寒冷伤害",
    "toxic_per_25_finesse": "每 25 灵巧获得毒素伤害",
    "life_regen_per_wisdom": "每智慧每秒生命再生",
    "cold_per_precision": "每精准恩惠获得寒冷伤害",
    "lightning_per_swiftness": "每迅捷恩惠获得闪电伤害",
    "fire_per_toughness": "每坚韧恩惠获得火焰伤害",
    "damage_per_swiftness": "每迅捷恩惠获得伤害",
    "damage_per_precision": "每精准恩惠获得伤害",
    "damage_per_toughness": "每坚韧恩惠获得伤害",
    "crit_multi_per_precision": "每精准恩惠提高暴击伤害倍率",
    "dot_damage_per_precision": "每精准恩惠提高持续伤害倍率",
    "projectile_speed_per_swiftness": "每迅捷恩惠提高投射物速度",
    "armor_per_toughness": "每坚韧恩惠获得护甲",
    "health_regen_percent_toughness_boon": "每坚韧恩惠每秒回复最大生命值",
    "damage": "伤害",
    "skill_effectiveness": "技能伤害效率",
    "damage_effectiveness": "额外伤害效率",
    "skill_pierce": "穿透",
    "skill_chain": "连锁",
    "base_duration": "技能持续时间",
    "cooldown": "技能冷却",
    "increased_duration": "技能持续时间",
    "area_of_effect": "范围效果",
    "self_duration": "增益持续时间",
    "incoming_damage": "受到的伤害",
    "radius": "技能半径",
    "curse_effect": "诅咒效果",
    "aura_effect": "光环效果",
    "conversion_physical_to_lightning": "物理伤害转化为闪电伤害",
    "conversion_physical_to_cold": "物理伤害转化为寒冷伤害",
    "conversion_physical_to_fire": "物理伤害转化为火焰伤害",
    "conversion_physical_to_toxic": "物理伤害转化为毒素伤害",
    "conversion_lightning_to_cold": "闪电伤害转化为寒冷伤害",
    "conversion_lightning_to_fire": "闪电伤害转化为火焰伤害",
    "conversion_lightning_to_toxic": "闪电伤害转化为毒素伤害",
    "conversion_cold_to_fire": "寒冷伤害转化为火焰伤害",
    "conversion_cold_to_toxic": "寒冷伤害转化为毒素伤害",
    "conversion_fire_to_toxic": "火焰伤害转化为毒素伤害",
    "extra_physical_as_lightning": "物理伤害额外获得闪电伤害",
    "extra_physical_as_cold": "物理伤害额外获得寒冷伤害",
    "extra_physical_as_fire": "物理伤害额外获得火焰伤害",
    "extra_physical_as_toxic": "物理伤害额外获得毒素伤害",
    "extra_lightning_as_cold": "闪电伤害额外获得寒冷伤害",
    "extra_lightning_as_fire": "闪电伤害额外获得火焰伤害",
    "extra_lightning_as_toxic": "闪电伤害额外获得毒素伤害",
    "extra_cold_as_fire": "寒冷伤害额外获得火焰伤害",
    "extra_cold_as_toxic": "寒冷伤害额外获得毒素伤害",
    "extra_fire_as_toxic": "火焰伤害额外获得毒素伤害",
    "physical_taken_as_lightning": "物理伤害承受为闪电伤害",
    "physical_taken_as_cold": "物理伤害承受为寒冷伤害",
    "physical_taken_as_fire": "物理伤害承受为火焰伤害",
    "physical_taken_as_toxic": "物理伤害承受为毒素伤害",
    "lightning_taken_as_cold": "闪电伤害承受为寒冷伤害",
    "lightning_taken_as_fire": "闪电伤害承受为火焰伤害",
    "lightning_taken_as_toxic": "闪电伤害承受为毒素伤害",
    "cold_taken_as_fire": "寒冷伤害承受为火焰伤害",
    "cold_taken_as_toxic": "寒冷伤害承受为毒素伤害",
    "fire_taken_as_toxic": "火焰伤害承受为毒素伤害",
    "extra_cold_as_fire_against_frozen": "对冻结敌人的寒冷伤害额外获得火焰伤害",
    "extra_cold_as_fire_against_chilled": "对寒冷敌人的寒冷伤害额外获得火焰伤害",
    "extra_lightning_as_cold_against_electrocuted": "对感电敌人的闪电伤害额外获得寒冷伤害",
}

# ---- TagNames dict (Tags.<NAME> -> zh_CN), keys in source-file order ----
TAG_NAME_TRANSLATIONS = {
    "Tags.PROJECTILE": "投射物",
    "Tags.AREA": "范围",
    "Tags.CURSE": "诅咒",
    "Tags.PASSIVE": "被动",
    "Tags.CASTABLE": "可施放",
    "Tags.CHAINING": "连锁",
    "Tags.TRIGGERABLE": "可触发",
    "Tags.BUFF": "增益",
    "Tags.DURATION": "持续时间",
    "Tags.HIT": "命中",
    "Tags.BOMB": "炸弹",
    "Tags.FIRE": "火焰",
    "Tags.COLD": "寒冷",
    "Tags.LIGHTNING": "闪电",
    "Tags.PHYSICAL": "物理",
    "Tags.TOXIC": "毒素",
    "Tags.DAMAGING": "伤害性",
    "Tags.UTILITY": "实用",
    "Tags.ELEMENTAL": "元素",
    "Tags.DOT": "持续伤害",
    "Tags.AURA": "光环",
    "Tags.MELEE": "近战",
    "Tags.ATTACK": "攻击",
    "Tags.SPELL": "法术",
}

# ---- runtime prefix literals: (rel_path, line_no, old_line, new_line, expected_occurrences) ----
PREFIX_ENTRIES = [
    ("Globals/StatsInfo.gd", 924,
     'return "Added " + stat_name[stat] + tag_postfix',
     'return "额外 " + stat_name[stat] + tag_postfix', 1),
    ("Globals/StatsInfo.gd", 928,
     'return "Increased " + stat_name[stat] + tag_postfix',
     'return "提高 " + stat_name[stat] + tag_postfix', 1),
    ("Globals/StatsInfo.gd", 930,
     'return "More " + stat_name[stat] + tag_postfix',
     'return "更多 " + stat_name[stat] + tag_postfix', 1),
    ("Globals/StatsInfo.gd", 955,
     'return str(stepify(amount, stepified)) + " Added " + stat_name[stat] + tag_postfix',
     'return str(stepify(amount, stepified)) + " 额外 " + stat_name[stat] + tag_postfix', 2),
    ("Globals/StatsInfo.gd", 960,
     'return str(round(amount * 100)) + "% Increased " + stat_name[stat] + tag_postfix',
     'return str(round(amount * 100)) + "% 提高 " + stat_name[stat] + tag_postfix', 1),
    ("Globals/StatsInfo.gd", 965,
     'return str(round(amount * 100)) + "% More " + stat_name[stat] + tag_postfix',
     'return str(round(amount * 100)) + "% 更多 " + stat_name[stat] + tag_postfix', 1),
    ("Globals/StatsInfo.gd", 1011,
     'return str(stepify(amount, stepified)) + " Added " + stat_name[stat] + tag_postfix',
     'return str(stepify(amount, stepified)) + " 额外 " + stat_name[stat] + tag_postfix', 2),
    ("Globals/StatsInfo.gd", 1019,
     'return str(amount * 100) + "% Increased " + stat_name[stat] + tag_postfix',
     'return str(amount * 100) + "% 提高 " + stat_name[stat] + tag_postfix', 1),
    ("Globals/StatsInfo.gd", 1024,
     'return str(amount * 100) + "% More " + stat_name[stat] + tag_postfix',
     'return str(amount * 100) + "% 更多 " + stat_name[stat] + tag_postfix', 1),
    ("Globals/StatsInfo.gd", 1044,
     'control.add_text(min_max(min_string, max_string) + " Added " + stat_name[stat] + tag_postfix)',
     'control.add_text(min_max(min_string, max_string) + " 额外 " + stat_name[stat] + tag_postfix)', 1),
    ("Globals/StatsInfo.gd", 1048,
     'control.add_text(min_max(min_string, max_string) + " Increased " + stat_name[stat] + tag_postfix)',
     'control.add_text(min_max(min_string, max_string) + " 提高 " + stat_name[stat] + tag_postfix)', 1),
    ("Globals/StatsInfo.gd", 1050,
     'control.add_text(min_max(min_string, max_string) + " More " + stat_name[stat] + tag_postfix)',
     'control.add_text(min_max(min_string, max_string) + " 更多 " + stat_name[stat] + tag_postfix)', 1),
    ("Scenes/Popups/EscapeMenu.gd", 171,
     'label.stat_name = "Base " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "基础 " + StatsInfo.stat_name[stat] + ":"', 2),
    ("Scenes/Popups/EscapeMenu.gd", 177,
     'label.stat_name = "Added " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "额外 " + StatsInfo.stat_name[stat] + ":"', 2),
    ("Scenes/Popups/EscapeMenu.gd", 182,
     'label.stat_name = "Increased " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "提高 " + StatsInfo.stat_name[stat] + ":"', 2),
    ("Scenes/Popups/EscapeMenu.gd", 188,
     'label.stat_name = "More " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "更多 " + StatsInfo.stat_name[stat] + ":"', 2),
    ("Scenes/Popups/EscapeMenu.gd", 204,
     'label.stat_name = "Base " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "基础 " + StatsInfo.stat_name[stat] + ":"', 2),
    ("Scenes/Popups/EscapeMenu.gd", 211,
     'label.stat_name = "Added " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "额外 " + StatsInfo.stat_name[stat] + ":"', 2),
    ("Scenes/Popups/EscapeMenu.gd", 217,
     'label.stat_name = "Increased " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "提高 " + StatsInfo.stat_name[stat] + ":"', 2),
    ("Scenes/Popups/EscapeMenu.gd", 223,
     'label.stat_name = "More " + StatsInfo.stat_name[stat] + ":"',
     'label.stat_name = "更多 " + StatsInfo.stat_name[stat] + ":"', 2),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_patch(rel: str, line_no: int, old_text: str, new_text: str,
               preimage: str, expected: int, source_text: str, translation: str) -> dict:
    col = old_text.find('"') + 1
    return {
        "path": rel,
        "field": "text",
        "classification": "TEXT_PATCH",
        "unit_id": f"{rel}:{line_no}:{col}",
        "old_text": old_text,
        "new_text": new_text,
        "preimage_sha256": preimage,
        "expected_occurrences": expected,
        "source_text": source_text,
        "translation": translation,
        "placeholders": [],
        "format_tokens": [],
        "tests": TESTS,
    }


def parse_dict_block(lines, header, line_pattern):
    """Find `header` line, parse entries until closing `}`.
    Returns list of (line_no, key, value, comma_suffix)."""
    start = next((i for i, l in enumerate(lines) if l.strip() == header), None)
    if start is None:
        raise SystemExit(f"header not found: {header!r}")
    entries = []
    i = start + 1
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "}":
            return entries
        if not stripped:
            i += 1
            continue
        m = line_pattern.match(stripped)
        if not m:
            raise SystemExit(f"unparseable line {i + 1}: {stripped!r}")
        entries.append((i + 1, m.group(1), m.group(2), m.group(3)))
        i += 1
    raise SystemExit(f"unterminated dict block starting at line {start + 1}")


def build_dict_patches(src_path: Path, header: str, pattern: re.Pattern,
                       table: dict, quoted_key: bool, content: str, lines) -> list:
    rel = src_path.relative_to(ROOT / "04_recovered").as_posix()
    preimage = sha256_file(src_path).upper()
    entries = parse_dict_block(lines, header, pattern)
    actual_keys = [e[1] for e in entries]
    if actual_keys != list(table.keys()):
        for i, (a, b) in enumerate(zip(actual_keys, table.keys())):
            if a != b:
                raise SystemExit(
                    f"key order mismatch in {rel}: entry {i} expected {b!r} got {a!r} "
                    f"(parsed {len(actual_keys)} entries, table {len(table)})")
        raise SystemExit(
            f"key count mismatch in {rel}: parsed {len(actual_keys)}, table {len(table)}")
    patches = []
    for line_no, key, old_value, comma in entries:
        old_text = f'{key}: "{old_value}"{comma}' if not quoted_key else f'"{key}": "{old_value}"{comma}'
        if lines[line_no - 1].strip() != old_text:
            raise SystemExit(f"line mismatch {rel}:{line_no}\n expected: {old_text}\n actual:   {lines[line_no - 1].strip()}")
        count = content.count(old_text)
        if count != 1:
            raise SystemExit(f"occurrence {count} for {old_text!r} at {rel}:{line_no} (must be 1)")
        new_value = table[key]
        new_text = f'"{key}": "{new_value}"{comma}' if quoted_key else f'{key}: "{new_value}"{comma}'
        patches.append(make_patch(rel, line_no, old_text, new_text, preimage, 1,
                                  old_value, new_value))
    return patches


def build_prefix_patches(files: dict, entries: list) -> list:
    patches = []
    for rel, line_no, old_line, new_line, expected in entries:
        src_path = ROOT / "04_recovered" / rel
        content = files[rel]
        lines = content.splitlines()
        if line_no - 1 >= len(lines):
            raise SystemExit(f"line out of range: {rel}:{line_no}")
        actual = lines[line_no - 1].strip()
        if old_line != actual:
            raise SystemExit(f"line mismatch {rel}:{line_no}\n expected: {old_line}\n actual:   {actual}")
        count = content.count(old_line)
        if count != expected:
            raise SystemExit(f"occurrence {count} for {old_line!r} at {rel}:{line_no} (expected {expected})")
        word = re.search(r'(Added|Increased|More|Base) "', old_line).group(1)
        prefix_zh = {"Base": "基础", "Added": "额外", "Increased": "提高", "More": "更多"}[word] + " "
        patches.append(make_patch(rel, line_no, old_line, new_line,
                                  sha256_file(src_path).upper(), expected,
                                  word, prefix_zh))
    return patches


def main():
    stats_path = ROOT / "04_recovered/Globals/StatsInfo.gd"
    tags_path = ROOT / "04_recovered/Globals/SkillTags.gd"
    escape_path = ROOT / "04_recovered/Scenes/Popups/EscapeMenu.gd"

    stats_content = stats_path.read_text(encoding="utf-8")
    tags_content = tags_path.read_text(encoding="utf-8")
    escape_content = escape_path.read_text(encoding="utf-8")
    files = {
        "Globals/StatsInfo.gd": stats_content,
        "Globals/SkillTags.gd": tags_content,
        "Scenes/Popups/EscapeMenu.gd": escape_content,
    }

    stat_pattern = re.compile(r'^"([^"]+)": "([^"]*)"(,?)$')
    tag_pattern = re.compile(r'^(Tags\.[A-Z_]+): "([^"]*)"(,?)$')

    patches = []
    patches += build_dict_patches(stats_path, "var stat_name = {", stat_pattern,
                                  STAT_NAME_TRANSLATIONS, True, stats_content,
                                  stats_content.splitlines())
    patches += build_dict_patches(tags_path, "var TagNames = {", tag_pattern,
                                  TAG_NAME_TRANSLATIONS, False, tags_content,
                                  tags_content.splitlines())
    patches += build_prefix_patches(files, PREFIX_ENTRIES)

    unit_ids = [p["unit_id"] for p in patches]
    if len(set(unit_ids)) != len(unit_ids):
        raise SystemExit("duplicate unit_id in patches")

    per_file_preimage = {
        "Globals/StatsInfo.gd": sha256_file(stats_path).upper(),
        "Globals/SkillTags.gd": sha256_file(tags_path).upper(),
        "Scenes/Popups/EscapeMenu.gd": sha256_file(escape_path).upper(),
    }
    for p in patches:
        if p["preimage_sha256"] != per_file_preimage[p["path"]]:
            raise SystemExit(f"preimage mismatch for {p['unit_id']}")

    manifest = {
        "id": "c5-l12-stats-tags-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": TARGET_ORIGINAL_SHA256,
        "dependencies": [],
        "conflicts": [],
        "scope": "ALL 149 stat display names (StatsInfo.gd stat_name) + ALL 24 skill tag names (SkillTags.gd TagNames) + runtime prefixes Base/Added/Increased/More in StatsInfo.gd render functions and EscapeMenu.gd stat breakdown; stat keys/IDs untouched; CODE_PATCH on plaintext sources in 04_recovered",
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

    loaded = json.loads(OUT.read_text(encoding="utf-8"))
    if loaded["id"] != "c5-l12-stats-tags-zhcn":
        raise SystemExit("manifest id mismatch after write")
    if len(loaded["patches"]) != len(patches):
        raise SystemExit("patch count mismatch after write")
    if loaded["target_original_sha256"] != TARGET_ORIGINAL_SHA256:
        raise SystemExit("target_original_sha256 mismatch after write")

    n_stats = len(STAT_NAME_TRANSLATIONS)
    n_tags = len(TAG_NAME_TRANSLATIONS)
    n_prefix = len(PREFIX_ENTRIES)
    print(f"manifest written: {OUT}")
    print(f"total patches: {len(patches)} (stat_name={n_stats}, TagNames={n_tags}, prefixes={n_prefix})")
    print(f"preimages: StatsInfo={per_file_preimage['Globals/StatsInfo.gd']}")
    print(f"           SkillTags={per_file_preimage['Globals/SkillTags.gd']}")
    print(f"           EscapeMenu={per_file_preimage['Scenes/Popups/EscapeMenu.gd']}")
    print("VERIFY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
