#!/usr/bin/env python3
"""Generate C5-L18: equipment display names (Genes.gd name_for_base_type /
name_for_gene_type / craft_name) and gene name prefix/suffix words
(ItemNameGenerator.gd).

Each unit old_text/new_text = the full stripped serialized source line.
Translations follow docs/zh_CN_glossary.md (Mod=词缀, Gene=基因, Boon=增益).
Internal identifiers (BaseType/GeneSlot/CraftType keys, variable names) stay
English; only player-visible display values are translated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")
SRC = ROOT / "04_recovered"
OUT = ROOT / "mods/c5-l18-equipment-names-zhcn/mod.json"
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
    "phase_checkpoint_equipment_names_zhcn",
]

# (rel_path, line_no, old_line, new_line, source_text, translation, occurrences)
ENTRIES = [
    # ============ Globals/Genes.gd : name_for_base_type (L165-223) ============
    ("Globals/Genes.gd", 166, 'BaseType.MELEE_WEAPON: "Melee Weapon", ', 'BaseType.MELEE_WEAPON: "近战武器", ', "Melee Weapon", "近战武器", 1),
    ("Globals/Genes.gd", 167, 'BaseType.CASTER_WEAPON: "Caster Weapon", ', 'BaseType.CASTER_WEAPON: "法术武器", ', "Caster Weapon", "法术武器", 1),
    ("Globals/Genes.gd", 168, 'BaseType.RANGE_WEAPON: "Range Weapon", ', 'BaseType.RANGE_WEAPON: "远程武器", ', "Range Weapon", "远程武器", 1),
    ("Globals/Genes.gd", 170, 'BaseType.EVASION_SHIELD: "Evasion Shield", ', 'BaseType.EVASION_SHIELD: "闪避盾", ', "Evasion Shield", "闪避盾", 1),
    ("Globals/Genes.gd", 171, 'BaseType.ARMOR_SHIELD: "Armor Shield", ', 'BaseType.ARMOR_SHIELD: "护甲盾", ', "Armor Shield", "护甲盾", 1),
    ("Globals/Genes.gd", 172, 'BaseType.HYBRID_SHIELD: "Hybrid Shield", ', 'BaseType.HYBRID_SHIELD: "混合盾", ', "Hybrid Shield", "混合盾", 1),
    ("Globals/Genes.gd", 173, 'BaseType.LIFE_SHIELD: "Life Shield", ', 'BaseType.LIFE_SHIELD: "生命盾", ', "Life Shield", "生命盾", 1),
    ("Globals/Genes.gd", 174, 'BaseType.CASTER_SHIELD: "Offensive Shield", ', 'BaseType.CASTER_SHIELD: "进攻盾", ', "Offensive Shield", "进攻盾", 1),
    ("Globals/Genes.gd", 176, 'BaseType.EVASION_BODY: "Evasion Body", ', 'BaseType.EVASION_BODY: "闪避胸甲", ', "Evasion Body", "闪避胸甲", 1),
    ("Globals/Genes.gd", 177, 'BaseType.ARMOR_BODY: "Armor Body", ', 'BaseType.ARMOR_BODY: "护甲胸甲", ', "Armor Body", "护甲胸甲", 1),
    ("Globals/Genes.gd", 178, 'BaseType.HYBRID_BODY: "Hybrid Body", ', 'BaseType.HYBRID_BODY: "混合胸甲", ', "Hybrid Body", "混合胸甲", 1),
    ("Globals/Genes.gd", 179, 'BaseType.LIFE_BODY: "Life Body", ', 'BaseType.LIFE_BODY: "生命胸甲", ', "Life Body", "生命胸甲", 1),
    ("Globals/Genes.gd", 180, 'BaseType.CASTER_BODY: "Offensive Body", ', 'BaseType.CASTER_BODY: "进攻胸甲", ', "Offensive Body", "进攻胸甲", 1),
    ("Globals/Genes.gd", 182, 'BaseType.EVASION_HELMET: "Evasion Helmet", ', 'BaseType.EVASION_HELMET: "闪避头盔", ', "Evasion Helmet", "闪避头盔", 1),
    ("Globals/Genes.gd", 183, 'BaseType.ARMOR_HELMET: "Armor Helmet", ', 'BaseType.ARMOR_HELMET: "护甲头盔", ', "Armor Helmet", "护甲头盔", 1),
    ("Globals/Genes.gd", 184, 'BaseType.HYBRID_HELMET: "Hybrid Helmet", ', 'BaseType.HYBRID_HELMET: "混合头盔", ', "Hybrid Helmet", "混合头盔", 1),
    ("Globals/Genes.gd", 185, 'BaseType.LIFE_HELMET: "Life Helmet", ', 'BaseType.LIFE_HELMET: "生命头盔", ', "Life Helmet", "生命头盔", 1),
    ("Globals/Genes.gd", 186, 'BaseType.CASTER_HELMET: "Offensive Helmet", ', 'BaseType.CASTER_HELMET: "进攻头盔", ', "Offensive Helmet", "进攻头盔", 1),
    ("Globals/Genes.gd", 188, 'BaseType.ARMOR_BELT: "Armor Belt", ', 'BaseType.ARMOR_BELT: "护甲腰带", ', "Armor Belt", "护甲腰带", 1),
    ("Globals/Genes.gd", 189, 'BaseType.EVASION_BELT: "Evasion Belt", ', 'BaseType.EVASION_BELT: "闪避腰带", ', "Evasion Belt", "闪避腰带", 1),
    ("Globals/Genes.gd", 190, 'BaseType.HYBRID_BELT: "Hybrid Belt", ', 'BaseType.HYBRID_BELT: "混合腰带", ', "Hybrid Belt", "混合腰带", 1),
    ("Globals/Genes.gd", 191, 'BaseType.LIFE_BELT: "Life Belt", ', 'BaseType.LIFE_BELT: "生命腰带", ', "Life Belt", "生命腰带", 1),
    ("Globals/Genes.gd", 192, 'BaseType.CASTER_BELT: "Offensive Belt", ', 'BaseType.CASTER_BELT: "进攻腰带", ', "Offensive Belt", "进攻腰带", 1),
    ("Globals/Genes.gd", 194, 'BaseType.ARMOR_GLOVES: "Armor Gloves", ', 'BaseType.ARMOR_GLOVES: "护甲手套", ', "Armor Gloves", "护甲手套", 1),
    ("Globals/Genes.gd", 195, 'BaseType.EVASION_GLOVES: "Evasion Gloves", ', 'BaseType.EVASION_GLOVES: "闪避手套", ', "Evasion Gloves", "闪避手套", 1),
    ("Globals/Genes.gd", 196, 'BaseType.HYBRID_GLOVES: "Hybrid Gloves", ', 'BaseType.HYBRID_GLOVES: "混合手套", ', "Hybrid Gloves", "混合手套", 1),
    ("Globals/Genes.gd", 197, 'BaseType.LIFE_GLOVES: "Life Gloves", ', 'BaseType.LIFE_GLOVES: "生命手套", ', "Life Gloves", "生命手套", 1),
    ("Globals/Genes.gd", 198, 'BaseType.CASTER_GLOVES: "Offensive Gloves", ', 'BaseType.CASTER_GLOVES: "进攻手套", ', "Offensive Gloves", "进攻手套", 1),
    ("Globals/Genes.gd", 200, 'BaseType.ARMOR_BOOTS: "Armor Boots", ', 'BaseType.ARMOR_BOOTS: "护甲靴", ', "Armor Boots", "护甲靴", 1),
    ("Globals/Genes.gd", 201, 'BaseType.EVASION_BOOTS: "Evasion Boots", ', 'BaseType.EVASION_BOOTS: "闪避靴", ', "Evasion Boots", "闪避靴", 1),
    ("Globals/Genes.gd", 202, 'BaseType.HYBRID_BOOTS: "Hybrid Boots", ', 'BaseType.HYBRID_BOOTS: "混合靴", ', "Hybrid Boots", "混合靴", 1),
    ("Globals/Genes.gd", 203, 'BaseType.LIFE_BOOTS: "Life Boots", ', 'BaseType.LIFE_BOOTS: "生命靴", ', "Life Boots", "生命靴", 1),
    ("Globals/Genes.gd", 204, 'BaseType.CASTER_BOOTS: "Offensive Boots", ', 'BaseType.CASTER_BOOTS: "进攻靴", ', "Offensive Boots", "进攻靴", 1),
    ("Globals/Genes.gd", 206, 'BaseType.ARMOR_PANTS: "Armor Pants", ', 'BaseType.ARMOR_PANTS: "护甲裤", ', "Armor Pants", "护甲裤", 1),
    ("Globals/Genes.gd", 207, 'BaseType.EVASION_PANTS: "Evasion Pants", ', 'BaseType.EVASION_PANTS: "闪避裤", ', "Evasion Pants", "闪避裤", 1),
    ("Globals/Genes.gd", 208, 'BaseType.HYBRID_PANTS: "Hybrid Pants", ', 'BaseType.HYBRID_PANTS: "混合裤", ', "Hybrid Pants", "混合裤", 1),
    ("Globals/Genes.gd", 209, 'BaseType.LIFE_PANTS: "Life Pants", ', 'BaseType.LIFE_PANTS: "生命裤", ', "Life Pants", "生命裤", 1),
    ("Globals/Genes.gd", 210, 'BaseType.CASTER_PANTS: "Offensive Pants", ', 'BaseType.CASTER_PANTS: "进攻裤", ', "Offensive Pants", "进攻裤", 1),
    ("Globals/Genes.gd", 212, 'BaseType.ATTACK_RING: "Attack Ring", ', 'BaseType.ATTACK_RING: "攻击戒指", ', "Attack Ring", "攻击戒指", 1),
    ("Globals/Genes.gd", 213, 'BaseType.CASTER_RING: "Offensive Ring", ', 'BaseType.CASTER_RING: "进攻戒指", ', "Offensive Ring", "进攻戒指", 1),
    ("Globals/Genes.gd", 214, 'BaseType.RESISTANT_RING: "Resistant Ring", ', 'BaseType.RESISTANT_RING: "抗性戒指", ', "Resistant Ring", "抗性戒指", 1),
    ("Globals/Genes.gd", 215, 'BaseType.LIFE_RING: "Life Ring", ', 'BaseType.LIFE_RING: "生命戒指", ', "Life Ring", "生命戒指", 1),
    ("Globals/Genes.gd", 217, 'BaseType.ATTACK_AMULET: "Attack Amulet", ', 'BaseType.ATTACK_AMULET: "攻击护符", ', "Attack Amulet", "攻击护符", 1),
    ("Globals/Genes.gd", 218, 'BaseType.CASTER_AMULET: "Offensive Amulet", ', 'BaseType.CASTER_AMULET: "进攻护符", ', "Offensive Amulet", "进攻护符", 1),
    ("Globals/Genes.gd", 219, 'BaseType.RESISTANT_AMULET: "Resistant Amulet", ', 'BaseType.RESISTANT_AMULET: "抗性护符", ', "Resistant Amulet", "抗性护符", 1),
    ("Globals/Genes.gd", 220, 'BaseType.LIFE_AMULET: "Life Amulet", ', 'BaseType.LIFE_AMULET: "生命护符", ', "Life Amulet", "生命护符", 1),
    ("Globals/Genes.gd", 222, 'BaseType.MINOR_BUFF: "Utility Buff"', 'BaseType.MINOR_BUFF: "辅助增益"', "Utility Buff", "辅助增益", 1),

    # ============ Globals/Genes.gd : name_for_gene_type (L539-550) ============
    ("Globals/Genes.gd", 540, 'GeneSlot.WEAPON: "Weapon/Shield", ', 'GeneSlot.WEAPON: "武器/盾牌", ', "Weapon/Shield", "武器/盾牌", 1),
    ("Globals/Genes.gd", 541, 'GeneSlot.BODY: "Chest Piece", ', 'GeneSlot.BODY: "胸甲", ', "Chest Piece", "胸甲", 1),
    ("Globals/Genes.gd", 542, 'GeneSlot.HELMET: "Helmet", ', 'GeneSlot.HELMET: "头盔", ', "Helmet", "头盔", 1),
    ("Globals/Genes.gd", 543, 'GeneSlot.AMULET: "Amulet", ', 'GeneSlot.AMULET: "护符", ', "Amulet", "护符", 1),
    ("Globals/Genes.gd", 544, 'GeneSlot.RING: "Ring", ', 'GeneSlot.RING: "戒指", ', "Ring", "戒指", 1),
    ("Globals/Genes.gd", 545, 'GeneSlot.BELT: "Belt", ', 'GeneSlot.BELT: "腰带", ', "Belt", "腰带", 1),
    ("Globals/Genes.gd", 546, 'GeneSlot.GLOVES: "Gloves", ', 'GeneSlot.GLOVES: "手套", ', "Gloves", "手套", 1),
    ("Globals/Genes.gd", 547, 'GeneSlot.BOOTS: "Boots", ', 'GeneSlot.BOOTS: "靴子", ', "Boots", "靴子", 1),
    ("Globals/Genes.gd", 548, 'GeneSlot.PANTS: "Pants", ', 'GeneSlot.PANTS: "裤子", ', "Pants", "裤子", 1),
    ("Globals/Genes.gd", 549, 'GeneSlot.MINOR: "Minor Buff", ', 'GeneSlot.MINOR: "小型增益", ', "Minor Buff", "小型增益", 1),

    # ============ Globals/Genes.gd : craft_name (L572-592) ============
    ("Globals/Genes.gd", 573, 'CraftType.CLEAR: "Clear", ', 'CraftType.CLEAR: "清除", ', "Clear", "清除", 1),
    ("Globals/Genes.gd", 574, 'CraftType.EXTRACT: "Store", ', 'CraftType.EXTRACT: "存入", ', "Store", "存入", 1),
    ("Globals/Genes.gd", 575, 'CraftType.SPLICE: "Restore", ', 'CraftType.SPLICE: "恢复", ', "Restore", "恢复", 1),
    ("Globals/Genes.gd", 578, 'CraftType.SCRAMBLE: "Scramble", ', 'CraftType.SCRAMBLE: "重组", ', "Scramble", "重组", 1),
    ("Globals/Genes.gd", 579, 'CraftType.SCRAMBLE_LUCKY: "Lucky Scramble", ', 'CraftType.SCRAMBLE_LUCKY: "幸运重组", ', "Lucky Scramble", "幸运重组", 1),
    ("Globals/Genes.gd", 580, 'CraftType.SCRAMBLE_ULTRA: "Godly Scramble", ', 'CraftType.SCRAMBLE_ULTRA: "神赐重组", ', "Godly Scramble", "神赐重组", 1),
    ("Globals/Genes.gd", 581, 'CraftType.GAMMA: "Add Random Mod", ', 'CraftType.GAMMA: "添加随机词缀", ', "Add Random Mod", "添加随机词缀", 1),
    ("Globals/Genes.gd", 582, 'CraftType.RECESSIVE: "Remove Random Mod", ', 'CraftType.RECESSIVE: "移除随机词缀", ', "Remove Random Mod", "移除随机词缀", 1),
    ("Globals/Genes.gd", 583, 'CraftType.RECOMBINATE: "Recombinate", ', 'CraftType.RECOMBINATE: "再组合", ', "Recombinate", "再组合", 1),
    ("Globals/Genes.gd", 584, 'CraftType.COSMIC: "Reroll Mod Values", ', 'CraftType.COSMIC: "重掷词缀数值", ', "Reroll Mod Values", "重掷词缀数值", 1),
    ("Globals/Genes.gd", 585, 'CraftType.LOCK_MOD: "Permanently Lock Random Mod", ', 'CraftType.LOCK_MOD: "永久锁定随机词缀", ', "Permanently Lock Random Mod", "永久锁定随机词缀", 1),
    ("Globals/Genes.gd", 586, 'CraftType.UNLOCK_MOD: "Unlock Random Mod", ', 'CraftType.UNLOCK_MOD: "解锁随机词缀", ', "Unlock Random Mod", "解锁随机词缀", 1),
    ("Globals/Genes.gd", 587, 'CraftType.SCRAMBLE_PREFIXES: "Scramble Prefixes", ', 'CraftType.SCRAMBLE_PREFIXES: "重组前缀", ', "Scramble Prefixes", "重组前缀", 1),
    ("Globals/Genes.gd", 588, 'CraftType.SCRAMBLE_SUFFIXES: "Scramble Suffixes", ', 'CraftType.SCRAMBLE_SUFFIXES: "重组后缀", ', "Scramble Suffixes", "重组后缀", 1),
    ("Globals/Genes.gd", 589, 'CraftType.UPGRADE_TIER: "Upgrade Random Mod", ', 'CraftType.UPGRADE_TIER: "升级随机词缀", ', "Upgrade Random Mod", "升级随机词缀", 1),
    ("Globals/Genes.gd", 590, 'CraftType.LOCK_SPECIFIC_MOD: "Lock Mod", ', 'CraftType.LOCK_SPECIFIC_MOD: "锁定词缀", ', "Lock Mod", "锁定词缀", 1),
    ("Globals/Genes.gd", 591, 'CraftType.UNLOCK_SPECIFIC_MOD: "Unlock Mod", ', 'CraftType.UNLOCK_SPECIFIC_MOD: "解锁词缀", ', "Unlock Mod", "解锁词缀", 1),

    # ============ Globals/ItemNameGenerator.gd : prefix_words (L4-48) ============
    ("Globals/ItemNameGenerator.gd", 5, '"Dire", ', '"凶煞", ', "Dire", "凶煞", 1),
    ("Globals/ItemNameGenerator.gd", 6, '"Blue", ', '"蓝", ', "Blue", "蓝", 1),
    ("Globals/ItemNameGenerator.gd", 7, '"Red", ', '"红", ', "Red", "红", 1),
    ("Globals/ItemNameGenerator.gd", 8, '"White", ', '"白", ', "White", "白", 1),
    ("Globals/ItemNameGenerator.gd", 9, '"Bitten", ', '"撕咬", ', "Bitten", "撕咬", 1),
    ("Globals/ItemNameGenerator.gd", 10, '"Woven", ', '"编织", ', "Woven", "编织", 1),
    ("Globals/ItemNameGenerator.gd", 11, '"Spiral", ', '"螺旋", ', "Spiral", "螺旋", 1),
    ("Globals/ItemNameGenerator.gd", 12, '"Jovial", ', '"欢快", ', "Jovial", "欢快", 1),
    ("Globals/ItemNameGenerator.gd", 13, '"Sprung", ', '"弹跃", ', "Sprung", "弹跃", 1),
    ("Globals/ItemNameGenerator.gd", 14, '"Bionic", ', '"生化", ', "Bionic", "生化", 1),
    ("Globals/ItemNameGenerator.gd", 15, '"Zomboid", ', '"丧尸", ', "Zomboid", "丧尸", 1),
    ("Globals/ItemNameGenerator.gd", 16, '"Wimpering", ', '"呜咽", ', "Wimpering", "呜咽", 1),
    ("Globals/ItemNameGenerator.gd", 17, '"Bearded", ', '"长须", ', "Bearded", "长须", 1),
    ("Globals/ItemNameGenerator.gd", 18, '"Sampled", ', '"采样", ', "Sampled", "采样", 1),
    ("Globals/ItemNameGenerator.gd", 19, '"Morbid", ', '"病态", ', "Morbid", "病态", 1),
    ("Globals/ItemNameGenerator.gd", 20, '"Scorched", ', '"灼烧", ', "Scorched", "灼烧", 1),
    ("Globals/ItemNameGenerator.gd", 21, '"Seared", ', '"炙烤", ', "Seared", "炙烤", 1),
    ("Globals/ItemNameGenerator.gd", 22, '"Flaming", ', '"烈焰", ', "Flaming", "烈焰", 1),
    ("Globals/ItemNameGenerator.gd", 23, '"Frozen", ', '"冰封", ', "Frozen", "冰封", 1),
    ("Globals/ItemNameGenerator.gd", 24, '"Chilled", ', '"寒冷", ', "Chilled", "寒冷", 1),
    ("Globals/ItemNameGenerator.gd", 25, '"Bitter", ', '"苦涩", ', "Bitter", "苦涩", 1),
    ("Globals/ItemNameGenerator.gd", 26, '"Salty", ', '"咸涩", ', "Salty", "咸涩", 1),
    ("Globals/ItemNameGenerator.gd", 27, '"Panicked", ', '"恐慌", ', "Panicked", "恐慌", 1),
    ("Globals/ItemNameGenerator.gd", 28, '"Angry", ', '"愤怒", ', "Angry", "愤怒", 1),
    ("Globals/ItemNameGenerator.gd", 29, '"Branded", ', '"烙印", ', "Branded", "烙印", 1),
    ("Globals/ItemNameGenerator.gd", 30, '"Doused", ', '"浸透", ', "Doused", "浸透", 1),
    ("Globals/ItemNameGenerator.gd", 31, '"Demonic", ', '"恶魔", ', "Demonic", "恶魔", 1),
    ("Globals/ItemNameGenerator.gd", 32, '"Glimmering", ', '"微光", ', "Glimmering", "微光", 1),
    ("Globals/ItemNameGenerator.gd", 33, '"Starry", ', '"星光", ', "Starry", "星光", 1),
    ("Globals/ItemNameGenerator.gd", 34, '"Loathe", ', '"憎恶", ', "Loathe", "憎恶", 1),
    ("Globals/ItemNameGenerator.gd", 35, '"Spiny", ', '"尖刺", ', "Spiny", "尖刺", 1),
    ("Globals/ItemNameGenerator.gd", 36, '"Chimeral", ', '"奇美拉", ', "Chimeral", "奇美拉", 1),
    ("Globals/ItemNameGenerator.gd", 37, '"Vampiric", ', '"吸血", ', "Vampiric", "吸血", 1),
    ("Globals/ItemNameGenerator.gd", 38, '"Defiled", ', '"污秽", ', "Defiled", "污秽", 1),
    ("Globals/ItemNameGenerator.gd", 39, '"Warm", ', '"温暖", ', "Warm", "温暖", 1),
    ("Globals/ItemNameGenerator.gd", 40, '"Cool", ', '"凉爽", ', "Cool", "凉爽", 1),
    ("Globals/ItemNameGenerator.gd", 41, '"Catlike", ', '"猫性", ', "Catlike", "猫性", 1),
    ("Globals/ItemNameGenerator.gd", 42, '"Venomous", ', '"剧毒", ', "Venomous", "剧毒", 1),
    ("Globals/ItemNameGenerator.gd", 43, '"Worn", ', '"破旧", ', "Worn", "破旧", 1),
    ("Globals/ItemNameGenerator.gd", 44, '"Ringed", ', '"环纹", ', "Ringed", "环纹", 1),
    ("Globals/ItemNameGenerator.gd", 45, '"Aspirant\'s", ', '"渴望者", ', "Aspirant's", "渴望者", 1),
    ("Globals/ItemNameGenerator.gd", 46, '"Ogre\'s", ', '"食人魔", ', "Ogre's", "食人魔", 1),
    ("Globals/ItemNameGenerator.gd", 47, '"Goblin\'s", ', '"哥布林", ', "Goblin's", "哥布林", 1),

    # ============ Globals/ItemNameGenerator.gd : suffix_words (L50-85) ============
    ("Globals/ItemNameGenerator.gd", 51, '"Ghoul", ', '"食尸鬼", ', "Ghoul", "食尸鬼", 1),
    ("Globals/ItemNameGenerator.gd", 52, '"Rain", ', '"雨", ', "Rain", "雨", 1),
    ("Globals/ItemNameGenerator.gd", 53, '"Snow", ', '"雪", ', "Snow", "雪", 1),
    ("Globals/ItemNameGenerator.gd", 54, '"Potato", ', '"土豆", ', "Potato", "土豆", 1),
    ("Globals/ItemNameGenerator.gd", 55, '"Germ", ', '"细菌", ', "Germ", "细菌", 1),
    ("Globals/ItemNameGenerator.gd", 56, '"Rock", ', '"岩石", ', "Rock", "岩石", 1),
    ("Globals/ItemNameGenerator.gd", 57, '"Eagle", ', '"鹰", ', "Eagle", "鹰", 1),
    ("Globals/ItemNameGenerator.gd", 58, '"Ape", ', '"猿", ', "Ape", "猿", 1),
    ("Globals/ItemNameGenerator.gd", 59, '"Eyes", ', '"眼", ', "Eyes", "眼", 1),
    ("Globals/ItemNameGenerator.gd", 60, '"Heart", ', '"心", ', "Heart", "心", 1),
    ("Globals/ItemNameGenerator.gd", 61, '"Lungs", ', '"肺", ', "Lungs", "肺", 1),
    ("Globals/ItemNameGenerator.gd", 62, '"Liver", ', '"肝", ', "Liver", "肝", 1),
    ("Globals/ItemNameGenerator.gd", 63, '"Brain", ', '"脑", ', "Brain", "脑", 1),
    ("Globals/ItemNameGenerator.gd", 64, '"Wolf", ', '"狼", ', "Wolf", "狼", 1),
    ("Globals/ItemNameGenerator.gd", 65, '"Fox", ', '"狐", ', "Fox", "狐", 1),
    ("Globals/ItemNameGenerator.gd", 66, '"Vagabond", ', '"流浪者", ', "Vagabond", "流浪者", 1),
    ("Globals/ItemNameGenerator.gd", 67, '"Thorn", ', '"荆棘", ', "Thorn", "荆棘", 1),
    ("Globals/ItemNameGenerator.gd", 68, '"Reaver", ', '"掠夺者", ', "Reaver", "掠夺者", 1),
    ("Globals/ItemNameGenerator.gd", 69, '"Flesh", ', '"血肉", ', "Flesh", "血肉", 1),
    ("Globals/ItemNameGenerator.gd", 70, '"Meat", ', '"肉", ', "Meat", "肉", 1),
    ("Globals/ItemNameGenerator.gd", 71, '"Wind", ', '"风", ', "Wind", "风", 1),
    ("Globals/ItemNameGenerator.gd", 72, '"Fear", ', '"恐惧", ', "Fear", "恐惧", 1),
    ("Globals/ItemNameGenerator.gd", 73, '"Bane", ', '"灾厄", ', "Bane", "灾厄", 1),
    ("Globals/ItemNameGenerator.gd", 74, '"Ogre", ', '"食人魔", ', "Ogre", "食人魔", 1),
    ("Globals/ItemNameGenerator.gd", 75, '"Giant", ', '"巨人", ', "Giant", "巨人", 1),
    ("Globals/ItemNameGenerator.gd", 76, '"Crux", ', '"关键", ', "Crux", "关键", 1),
    ("Globals/ItemNameGenerator.gd", 77, '"Tiara", ', '"冠冕", ', "Tiara", "冠冕", 1),
    ("Globals/ItemNameGenerator.gd", 78, '"Seal", ', '"封印", ', "Seal", "封印", 1),
    ("Globals/ItemNameGenerator.gd", 79, '"Cup", ', '"杯", ', "Cup", "杯", 1),
    ("Globals/ItemNameGenerator.gd", 80, '"Statue", ', '"雕像", ', "Statue", "雕像", 1),
    ("Globals/ItemNameGenerator.gd", 81, '"Key", ', '"钥匙", ', "Key", "钥匙", 1),
    ("Globals/ItemNameGenerator.gd", 82, '"Crown", ', '"王冠", ', "Crown", "王冠", 1),
    ("Globals/ItemNameGenerator.gd", 83, '"Mask", ', '"面具", ', "Mask", "面具", 1),
    ("Globals/ItemNameGenerator.gd", 84, '"Jar"', '"罐"', "Jar", "罐", 1),
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
        "id": "c5-l18-equipment-names-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": TARGET_SHA,
        "dependencies": [],
        "conflicts": [],
        "scope": f"C5-L18: equipment display names across {len(files)} scripts - Genes.gd name_for_base_type (48 base types), name_for_gene_type (10 slots), craft_name (17 craft actions), ItemNameGenerator.gd prefix_words (43) + suffix_words (34); internal keys (BaseType/GeneSlot/CraftType enums, dict keys) untouched",
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