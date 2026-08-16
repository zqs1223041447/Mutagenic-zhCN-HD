#!/usr/bin/env python3
"""Generate C5-L11: FULL passive tree zh_CN localization manifest.

Covers:
  - Globals/PassiveTagStats.gd      : 326 passive node display names
  - Globals/Keystones/TreeKeystones.gd   : 65 keystone names+descriptions
  - Globals/Keystones/SupportKeystones.gd:  9 keystone names+descriptions
  - Globals/Keystones/UniqueKeystones.gd : 14 keystone names+descriptions

Translations follow docs/zh_CN_glossary.md (Damage=伤害, Life=生命, Physical=物理,
Lightning=闪电, Cold=寒冷, Fire=火焰, Toxic=毒素, Ailment=异常状态, Boon=恩惠,
Curse=诅咒, Armor=护甲, Evasion=闪避, Critical Strike=暴击, Resistance=抗性,
More=更多, Increased=增加, Projectile=投射物, Area=范围, Duration=持续时间 ...).

Notes on disambiguation:
  4 pairs of passive nodes share byte-identical "name" lines
  (Critical Strikes x2, Critical Multiplier x2, Minor Curse Effect x2,
   Maximum Toxic Resistance x2). For those 8 units old_text/new_text span
  the neighbouring raw line (next or previous) so the patch target stays
  unique in the file.

TRANSLATION_UNCERTAIN entries (kept in scope field with evidence):
  - critical_thinking            pun "Critical Thinking" -> 批判性思维
  - major_physical_damage        "Physician" pun -> 物理学者
  - maximum_all_resistances      source repeats name "Maximum Toxic Resistance"
  - major_toxic_ailment_effect   source typo "Poison Intesity"
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"G:\opencode-Mutageni")
OUT = ROOT / "mods/c5-l11-passive-tree-zhcn/mod.json"
EXTRACT_PASSIVES = ROOT / "10_logs/full_passive_text_extract.json"
EXTRACT_KEYSTONES = ROOT / "10_logs/keystones_extract.json"

MANIFEST_TESTS = [
    "locked_units_and_preimages",
    "exact_unit_application",
    "resource_contract",
    "declared_delta",
    "compiled_script_load",
    "pck_checksum",
    "exe_structure",
    "pck_roundtrip",
    "boot",
    "phase_checkpoint_passive_tree_zhcn",
]

PATCH_TESTS = [
    "unit_id_exact_match",
    "placeholder_conservation",
    "token_conservation",
    "resource_contract",
    "declared_delta",
    "compiled_script_load",
]

# ---------------------------------------------------------------------------
# Passive node names: node key -> zh_CN display name (326 entries)
# ---------------------------------------------------------------------------
PASSIVE_TR = {
    "starter_node": "入门者",
    "minor_strength": "次级力量",
    "major_strength": "高级力量",
    "minor_constitution": "次级体质",
    "major_constitution": "高级体质",
    "minor_agility": "次级敏捷",
    "major_agility": "高级敏捷",
    "minor_wisdom": "次级智慧",
    "major_wisdom": "高级智慧",
    "minor_finesse": "次级灵巧",
    "major_finesse": "高级灵巧",
    "swiftness_on_hit": "命中获得迅捷",
    "toughness_boon_when_hit": "命中获得坚韧",
    "max_precision_boons": "精准恩惠",
    "max_swiftness_boons": "迅捷恩惠",
    "max_toughness_boons": "坚韧恩惠",
    "minor_damage_per_boon": "恩惠伤害",
    "major_damage_per_boon": "恩惠专精",
    "damage_per_swiftness": "迅捷伤害",
    "damage_per_precision": "精准伤害",
    "damage_per_toughness": "坚韧伤害",
    "multi_per_precision": "精准倍率",
    "armor_per_toughness": "坚韧护甲",
    "health_regen_per_toughness": "再生恩惠",
    "minor_damage": "次级伤害",
    "minor_health": "次级生命",
    "medium_health": "强化生命",
    "minor_life_regen": "次级生命回复",
    "minor_lgoh": "次级吸取",
    "major_lgoh": "高级吸取",
    "major_life": "健壮",
    "major_life_regen": "再生组织",
    "ogre_blood": "食人魔之血",
    "zombie_blood": "僵尸之血",
    "chilled_blood": "寒冰之血",
    "ancient_blood": "远古之血",
    "minor_projectile_damage": "次级投射物伤害",
    "minor_projectile_speed": "次级投射物速度",
    "major_projectile_speed": "远程精通",
    "major_projectile_damage": "投射物专精",
    "extra_attack_projectiles": "额外弹药",
    "extra_spell_projectiles": "重复施法",
    "minor_dot_damage": "持续伤害",
    "major_dot_damage": "侵蚀伤害",
    "uber_dot_damage": "邪恶虹吸",
    "minor_fire_dot_damage": "余烬",
    "major_fire_dot_damage": "熔岩之脉",
    "minor_physical_dot_damage": "轻度出血",
    "major_physical_dot_damage": "重度出血",
    "minor_physical_resistances": "物理抗性",
    "major_physical_resistances": "高级物理抗性",
    "minor_lightning_resistances": "闪电抗性",
    "major_lightning_resistances": "高级闪电抗性",
    "minor_cold_resistances": "寒冷抗性",
    "major_cold_resistances": "高级寒冷抗性",
    "minor_fire_resistances": "火焰抗性",
    "major_fire_resistances": "高级火焰抗性",
    "minor_toxic_resistances": "毒素抗性",
    "major_toxic_resistances": "高级毒素抗性",
    "maximum_physical_resistance": "物理抗性上限",
    "maximum_lightning_resistance": "闪电抗性上限",
    "maximum_cold_resistance": "寒冷抗性上限",
    "maximum_fire_resistance": "火焰抗性上限",
    "maximum_toxic_resistance": "毒素抗性上限",
    "maximum_all_resistances": "毒素抗性上限",
    "minor_curse_resistance": "次级诅咒抗性",
    "major_curse_resistance": "恶魔抗性",
    "minor_block_chance": "次级格挡几率",
    "minor_block_chance_armor": "稳固格挡几率",
    "major_block_chance": "盾卫大师",
    "minor_block_recovery": "次级格挡回复",
    "major_block_recovery": "高级格挡回复",
    "minor_ailment_avoidance": "次级异常回避",
    "major_ailment_avoidance": "异常回避",
    "major_ailment_avoidance_evasion": "技巧回避",
    "minor_ailment_avoidance_life": "次级元素韧性",
    "major_ailment_avoidance_life": "元素韧性",
    "minor_crit_resistance": "次级暴击抗性",
    "major_crit_resistance": "高级暴击抗性",
    "minor_movement_speed": "疾足",
    "minor_all_speed": "灵动",
    "major_movement_speed": "疾跑者",
    "major_all_speed": "迅捷",
    "minor_movement_speed_evasion": "盗贼之步",
    "major_movement_speed_evasion": "移动大师",
    "minor_cast_speed_melee": "近战速度",
    "major_cast_speed_melee": "熟练打击",
    "minor_cast_speed_attack": "攻击速度",
    "major_cast_speed_attack": "攻击精通",
    "major_cast_speed_spell": "施法精通",
    "minor_cast_speed_spell": "施法速度",
    "minor_cast_speed": "灵巧双手",
    "minor_spell_damage": "次级法术伤害",
    "minor_attack_damage": "次级攻击伤害",
    "medium_spell_damage": "法术伤害",
    "medium_attack_damage": "攻击伤害",
    "major_spell_damage": "强力法术伤害",
    "major_attack_damage": "强力攻击伤害",
    "minor_physical_damage": "次级物理伤害",
    "medium_physical_damage": "物理伤害",
    "major_physical_damage": "物理学者",
    "major_physical_damage_crit": "物理亲和",
    "minor_spell_physical_damage": "次级物理法术伤害",
    "minor_attack_physical_damage": "次级物理攻击伤害",
    "medium_spell_physical_damage": "物理法术伤害",
    "medium_attack_physical_damage": "物理攻击伤害",
    "major_spell_physical_damage": "强力物理法术伤害",
    "major_attack_physical_damage": "强力物理攻击伤害",
    "minor_lightning_damage": "次级闪电伤害",
    "major_lightning_damage_conduit": "闪电导管",
    "minor_spell_lightning_damage": "次级闪电法术伤害",
    "minor_attack_lightning_damage": "次级闪电攻击伤害",
    "medium_spell_lightning_damage": "闪电法术伤害",
    "medium_attack_lightning_damage": "闪电攻击伤害",
    "major_spell_lightning_damage": "强力闪电法术伤害",
    "major_attack_lightning_damage": "强力闪电攻击伤害",
    "minor_cold_damage": "次级寒冷伤害",
    "major_cold_damage": "雪人",
    "minor_spell_cold_damage": "次级寒冷法术伤害",
    "minor_attack_cold_damage": "次级寒冷攻击伤害",
    "medium_spell_cold_damage": "寒冷法术伤害",
    "medium_attack_cold_damage": "寒冷攻击伤害",
    "major_spell_cold_damage": "强力寒冷法术伤害",
    "major_attack_cold_damage": "强力寒冷攻击伤害",
    "minor_fire_damage": "次级火焰伤害",
    "major_fire_damage": "纵火者",
    "major_fire_damage_ailement_effect": "火焰伤害大师",
    "minor_spell_fire_damage": "次级火焰法术伤害",
    "minor_attack_fire_damage": "次级火焰攻击伤害",
    "medium_spell_fire_damage": "火焰法术伤害",
    "medium_attack_fire_damage": "火焰攻击伤害",
    "major_spell_fire_damage": "强力火焰法术伤害",
    "major_attack_fire_damage": "强力火焰攻击伤害",
    "minor_toxic_damage": "次级毒素伤害",
    "major_toxic_damage": "瘟疫使者",
    "minor_spell_toxic_damage": "次级毒素法术伤害",
    "minor_attack_toxic_damage": "次级毒素攻击伤害",
    "medium_spell_toxic_damage": "毒素法术伤害",
    "medium_attack_toxic_damage": "毒素攻击伤害",
    "major_spell_toxic_damage": "强力毒素法术伤害",
    "major_attack_toxic_damage": "强力毒素攻击伤害",
    "minor_hit_damage": "重创打击",
    "minor_hit_damage_cast_speed": "快速连击",
    "major_hit_damage": "粉碎重击",
    "major_hit_damage_cast_speed": "急速粉碎",
    "massive_hit_damage": "即时生效",
    "minor_armor": "次级护甲",
    "major_armor": "高级护甲",
    "minor_evasion": "次级闪避",
    "major_evasion": "高级闪避",
    "minor_hybrid": "次级防御",
    "major_hybrid": "高级防御",
    "minor_armor_life": "护甲生命",
    "major_armor_life": "凝血之血",
    "minor_evasion_life": "闪避者",
    "major_evasion_life": "潜行者",
    "minor_health_regen": "次级再生",
    "medium_health_regen": "再生",
    "major_health_regen": "蝾螈之血",
    "minor_health_regen_armor": "再生护甲",
    "major_health_regen_armor": "蜥蜴之皮",
    "attack_fire_damage_and_penetration": "红外之刃",
    "spell_fire_damage_and_penetration": "熔岩迸溅",
    "attack_cold_damage_and_penetration": "寒冰重击",
    "spell_cold_damage_and_penetration": "碎裂施法",
    "attack_lightning_damage_and_penetration": "充能之锤",
    "spell_lightning_damage_and_penetration": "电击之手",
    "attack_penetration": "元素攻击穿透",
    "minor_enhanced_ailment_chance": "异常研习",
    "major_enhanced_ailment_chance": "强化异常",
    "minor_physical_ailment_chance": "流血几率",
    "major_physical_ailment_chance": "强化流血几率",
    "minor_lightning_ailment_chance": "电击几率",
    "major_lightning_ailment_chance": "强化电击几率",
    "minor_cold_ailment_chance": "寒冷几率",
    "major_cold_ailment_chance": "强化寒冷几率",
    "minor_fire_ailment_chance": "灼烧几率",
    "major_fire_ailment_chance": "强化灼烧几率",
    "minor_toxic_ailment_chance": "中毒几率",
    "major_toxic_ailment_chance": "强化中毒几率",
    "minor_physical_ailment_effect": "流血效果",
    "major_physical_ailment_effect": "流血强度",
    "minor_lightning_ailment_effect": "电击增幅器",
    "major_lightning_ailment_effect": "圣艾尔摩之火",
    "uber_lightning_ailment_effect": "特斯拉线圈",
    "minor_cold_ailment_effect": "寒冷效果",
    "minor_fire_ailment_effect": "灼烧效果",
    "major_fire_ailment_effect": "灼烧强度",
    "uber_fire_ailment_effect": "熔岩之子",
    "minor_toxic_ailment_effect": "中毒效果",
    "medium_toxic_ailment_effect": "强化毒素",
    "major_toxic_ailment_effect": "毒素强度",
    "uber_toxic_ailment_effect": "剧毒收集者",
    "minor_skill_duration": "次级技能持续时间",
    "major_skill_duration": "持久技能",
    "minor_ailment_duration": "次级异常持续时间",
    "minor_ailment_effect": "次级异常效果",
    "major_ailment_effect": "异常增幅器",
    "major_ailment_duration": "异常持续时间",
    "toxicologist": "毒理学家",
    "minor_area_of_effect": "范围效果",
    "major_area_of_effect": "延伸范围",
    "minor_physical_area_of_effect": "物理范围效果",
    "major_physical_area_of_effect": "钢铁延伸",
    "minor_lightning_area_of_effect": "闪电范围效果",
    "major_lightning_area_of_effect": "弧光延伸",
    "minor_cold_area_of_effect": "寒冷范围效果",
    "major_cold_area_of_effect": "严寒延伸",
    "uber_cold_area_of_effect": "冬日风暴",
    "minor_fire_area_of_effect": "火焰范围效果",
    "major_fire_area_of_effect": "烈焰延伸",
    "minor_toxic_area_of_effect": "毒素范围效果",
    "major_toxic_area_of_effect": "剧毒延伸",
    "minor_crit_chance": "暴击",
    "major_crit_chance": "暴击",
    "minor_crit_multi": "暴击倍率",
    "major_crit_multi": "暴击倍率",
    "minor_crit_chance_projectiles": "投射物暴击",
    "major_crit_chance_projectiles": "投射物暴击亲和",
    "minor_attack_crit_chance": "次级攻击暴击",
    "major_attack_crit_chance": "攻击暴击",
    "minor_attack_crit_multi": "次级攻击暴击倍率",
    "major_attack_crit_multi": "攻击暴击倍率",
    "minor_spell_crit_chance": "法术暴击",
    "major_spell_crit_chance": "华丽法术暴击",
    "minor_spell_crit_multi": "法术暴击倍率",
    "major_spell_crit_multi": "华丽法术暴击倍率",
    "minor_spell_crit_chance_cast_speed": "次级巫术",
    "major_spell_crit_chance_cast_speed": "巫术",
    "minor_spell_crit_multi_cast_speed": "弱魔法师",
    "major_spell_crit_multi_cast_speed": "魔法师",
    "stable_strikes": "稳定打击",
    "volatile_strikes": "易爆打击",
    "minor_curse_effect": "次级诅咒效果",
    "major_curse_effect": "高级诅咒效果",
    "minor_curse_effect_cast_speed": "次级诅咒效果",
    "major_curse_effect_cast_speed": "诅咒术士",
    "minor_curse_aoe": "诅咒影响",
    "major_curse_aoe": "高级诅咒影响",
    "minor_aura_effect": "次级光环效果",
    "major_aura_effect": "高级光环效果",
    "bomb_area_minor": "炸弹匠人",
    "bomb_area_major": "爆破专家",
    "minor_bomb_crit_chance": "不稳定炸药",
    "minor_bomb_crit_multi": "强力炸药",
    "major_bomb_crit": "强化冲击波",
    "impact_speed_keystone": "冲击速度",
    "keystone_brick": "铁砖",
    "keystone_impending_death": "死亡标记",
    "keystone_sanguine_decay": "血红衰败",
    "keystone_saboteur": "破坏者",
    "keystone_cyclic_destruction": "循环毁灭",
    "keystone_cryomancer": "寒冰法师",
    "keystone_charged_field": "充能领域",
    "keystone_kinetic_projectiles": "动能投射物",
    "keystone_time_warp": "时间扭曲",
    "keystone_raging_momentum": "狂暴动量",
    "keystone_temperature_delta": "温差",
    "keystone_volley": "不稳定齐射",
    "keystone_unleash": "解放",
    "keystone_overloaded_shells": "过载弹壳",
    "empty": "测试节点",
    "attuned_decay": "亲和衰败",
    "hysteria": "歇斯底里",
    "dread": "恐惧",
    "paranoia": "偏执",
    "transmogrify": "变形",
    "bewitching_whispers": "魅惑低语",
    "monster_study": "怪物研习",
    "affliction_study": "苦痛研习",
    "battle_hardened": "身经百战",
    "fury": "狂怒",
    "spirited_resilience": "不屈韧性",
    "youthful_recklessness": "年少轻狂",
    "hoplite": "重装步兵",
    "swordsman": "剑士",
    "thors_apprentice": "雷神学徒",
    "warriors_spirit": "战士之魂",
    "leeching_presence": "吸血光环",
    "retaliatory_mark": "复仇印记",
    "blood_armor": "血之护甲",
    "magmatic_blood": "岩浆之血",
    "blood_price": "血之代价",
    "veil_of_night": "夜幕之纱",
    "caustics": "腐蚀",
    "effect_of_the_horde": "兽群之力",
    "thieves_agility": "盗贼敏捷",
    "volatile_casting": "易爆施法",
    "chain_gang": "锁链帮",
    "warped_time": "事件视界",
    "bloody_mess": "血腥盛宴",
    "shocking_moves": "电击步伐",
    "fortified_artillery": "强化炮火",
    "hand_to_hand_combat": "近身格斗专家",
    "forest_bathing": "森林浴",
    "arctic_breath": "极寒吐息",
    "impactful_strikes": "强力打击",
    "frozen_domain": "污秽领域",
    "viridian_sage": "翠绿贤者",
    "oak_aegis": "橡木神盾",
    "mountain_born": "山岳之子",
    "stifled_cursing": "窒息诅咒",
    "energetic_flesh": "能量之躯",
    "chaotic_resonance": "混沌共振",
    "one_with_lightning": "与雷合一",
    "bonded_electrons": "附近敌人的闪电抗性等同于你的闪电抗性。",
    "reverence": "崇敬",
    "scorn": "蔑视",
    "derision": "嘲讽",
    "ire": "导电之怒",
    "weapon_dexterity": "武器灵巧",
    "strengthened_wisdom": "强化智慧",
    "flame_resonance": "烈焰共振",
    "critical_thinking": "批判性思维",
    "elemental_shelling": "元素炮击",
    "heated_resonance": "炽热共振",
    "elemental_piercing": "元素穿透",
    "overcooked": "过熟",
    "titanic_resilience": "泰坦韧性",
    "capable_combatant": "能征善战",
    "coated_blades": "涂层之刃",
    "serrated_blades": "锯齿之刃",
    "sabotank": "破坏坦克",
    "slippery_titan": "滑溜泰坦",
    "ailment_reaver": "异常掠夺者",
    "vitality_surge": "活力奔涌",
}

# ---------------------------------------------------------------------------
# Keystone translations: (filename, key) -> (zh name, zh description)
# ---------------------------------------------------------------------------
KEYSTONE_TR = {
    # ---------------- TreeKeystones.gd (65) ----------------
    ("TreeKeystones.gd", "TREE_DETERIORATION"): (
        "腐朽",
        "技能命中时有 10% 几率施加暴露。"),
    ("TreeKeystones.gd", "TREE_RAPID_DECAY"): (
        "急速衰败",
        "中毒与感染的伤害结算速度提高 20%。"),
    ("TreeKeystones.gd", "TREE_PROJECTILE_SPEED_DAMAGE"): (
        "冲击速度",
        "投射物速度增加值的 12% 同时转化为投射物伤害的更多加成"),
    ("TreeKeystones.gd", "TREE_GOLIATH"): (
        "歌利亚",
        "最大生命增加值的 10% 同时转化为范围伤害的更多加成"),
    ("TreeKeystones.gd", "TREE_PHANTOM_SHIELD"): (
        "幻影面纱",
        "每 3 秒获得 1 层幻影护盾（最多 1 层）。即将受到攻击时，改为消耗幻影护盾避免这次攻击。幻影护盾无法阻挡持续伤害。"),
    ("TreeKeystones.gd", "TREE_REGENERATIVE_FLESH"): (
        "再生血肉",
        "每 10 秒获得持续 1 秒的每秒 20% 最大生命回复。"),
    ("TreeKeystones.gd", "TREE_VAMPIRIC_SKIN"): (
        "吸血鬼之皮",
        "若在过去 5 秒内受到伤害，则每秒生命回复提高 100%（更多）"),
    ("TreeKeystones.gd", "TREE_CROCODILE_SKIN"): (
        "鳄鱼之皮",
        "若在过去 5 秒内未受到攻击，则受到的攻击伤害降低 90%。"),
    ("TreeKeystones.gd", "TREE_HARDENED_FLESH"): (
        "硬化血肉",
        "若在过去 5 秒内受到攻击，则受到的伤害降低 10%。"),
    ("TreeKeystones.gd", "TREE_SPIKE_ARMOR"): (
        "尖刺甲壳",
        "若在过去 5 秒内受到攻击，则造成 20% 更多伤害"),
    ("TreeKeystones.gd", "TREE_DEFLECTING_ARMOR"): (
        "偏转护甲",
        "有 20% 几率完全避免受到的攻击伤害"),
    ("TreeKeystones.gd", "TREE_ADRENALINE"): (
        "肾上腺素",
        "受到攻击时，获得持续 5 秒的 25% 更多移动速度"),
    ("TreeKeystones.gd", "TREE_ENDURANCE"): (
        "耐力",
        "若在过去 5 秒内受到攻击，则获得 30% 更多护甲"),
    ("TreeKeystones.gd", "TREE_TOXICOLOGIST"): (
        "毒理学家",
        "受到的持续伤害降低 35%"),
    ("TreeKeystones.gd", "TREE_BRICK"): (
        "铁砖",
        "受到的攻击伤害降低 15%"),
    ("TreeKeystones.gd", "TREE_LEECHER"): (
        "吸血者",
        "击杀敌人时回复 1% 最大生命。"),
    ("TreeKeystones.gd", "TREE_POTENTIAL_ENERGY"): (
        "伤害电容器",
        "持续伤害不再直接造成伤害，而是以势能的形式存储在敌人身上。敌人被击杀时，将存储伤害的 15% 以物理伤害的形式在敌人周围引发大规模爆炸。"),
    ("TreeKeystones.gd", "TREE_INFECTIOUS_MALIGNANCY"): (
        "传染性恶变",
        "诅咒效果降低 10%。敌人被击杀时，其身上的诅咒会传播给附近敌人"),
    ("TreeKeystones.gd", "TREE_FRAGILE_CURSES"): (
        "脆弱诅咒",
        "诅咒持续时间降低 50%，但诅咒效果提高 30%"),
    ("TreeKeystones.gd", "TREE_IMPENDING_DEATH"): (
        "死亡标记",
        "敌人身上的每个诅咒使其受到 10% 更多伤害"),
    ("TreeKeystones.gd", "TREE_CURSE_DURATION"): (
        "延长抑郁",
        "诅咒持续时间提高 50%"),
    ("TreeKeystones.gd", "TREE_REPEATER"): (
        "连发器",
        "技能施法速度提高 15%。持续时间类技能的持续时间降低 30%"),
    ("TreeKeystones.gd", "TREE_RANGER"): (
        "游侠之道",
        "技能投射物速度提高 30%"),
    ("TreeKeystones.gd", "TREE_MAGUS"): (
        "法师之道",
        "技能范围效果提高 30%"),
    ("TreeKeystones.gd", "TREE_PIERCING_TRUTH"): (
        "贯穿真理",
        "技能可穿透的敌人数量翻倍"),
    ("TreeKeystones.gd", "TREE_CYCLE"): (
        "循环毁灭",
        "每 5 秒在\u201c造成 20% 更多范围伤害\u201d与\u201c范围效果提高 40%\u201d之间切换"),
    ("TreeKeystones.gd", "TREE_GROWING_PAIN"): (
        "成长的阵痛",
        "若在过去 5 秒内有击杀，则范围效果提高 30%"),
    ("TreeKeystones.gd", "TREE_QUICK_GETAWAY"): (
        "快速脱身",
        "受到攻击时，获得持续 1 秒的 25% 移动速度加成"),
    ("TreeKeystones.gd", "TREE_CRYOMANCER"): (
        "寒冰法师",
        "寒冷持续时间提高 100%"),
    ("TreeKeystones.gd", "TREE_CHARGED_FIELD"): (
        "充能领域",
        "附近敌人受到 30% 更多伤害"),
    ("TreeKeystones.gd", "TREE_KINETIC_PROJECTILES"): (
        "动能投射物",
        "投射物造成 30% 更多伤害。投射物始终以基础速度飞行"),
    ("TreeKeystones.gd", "TREE_GLASS_CANNON"): (
        "玻璃大炮",
        "最大生命降低 65%，施法速度提高 10%，伤害提高 25%"),
    ("TreeKeystones.gd", "TREE_TIME_WARP"): (
        "时间扭曲",
        "持续伤害的结算速度提高 40%"),
    ("TreeKeystones.gd", "TREE_RAGING_MOMENTUM"): (
        "狂暴动量",
        "若在过去 5 秒内有击杀，则造成 15% 更多伤害"),
    ("TreeKeystones.gd", "TREE_PRECISION_STRIKES"): (
        "精准打击",
        "对受易伤影响的敌人造成 25% 更多伤害"),
    ("TreeKeystones.gd", "TREE_TEMPERATURE_DELTAS"): (
        "温差",
        "受寒冷影响的敌人受到 15% 更多伤害"),
    ("TreeKeystones.gd", "TREE_IMPENDING_CONTAGION"): (
        "传染性感染",
        "感染额外传播至 1 名敌人。"),
    ("TreeKeystones.gd", "TREE_SANGUINE_DECAY"): (
        "血红衰败",
        "流血或撕裂的敌人在死亡时爆炸，将其身上剩余的流血与撕裂总伤害的 50% 施加给附近敌人。"),
    ("TreeKeystones.gd", "TREE_RICOCHET"): (
        "弹射",
        "投射物每次连锁时造成 30% 更多伤害"),
    ("TreeKeystones.gd", "TREE_SABOTEUR"): (
        "破坏者",
        "有 50% 几率额外施放一枚炸弹"),
    ("TreeKeystones.gd", "TREE_VOLLEY"): (
        "不稳定齐射",
        "技能有 10% 几率发射双倍投射物"),
    ("TreeKeystones.gd", "TREE_UNLEASH"): (
        "解放",
        "每 10 秒获得持续 4 秒的 30% 更多施法速度"),
    ("TreeKeystones.gd", "TREE_SIPHONER"): (
        "生命虹吸者",
        "以持续伤害击杀敌人时，回复 2% 最大生命。"),
    ("TreeKeystones.gd", "TREE_OVERLOADED_SHELLS"): (
        "过载弹壳",
        "投射物造成 10% 更多伤害"),
    ("TreeKeystones.gd", "TREE_HYSTERIA"): (
        "歇斯底里",
        "被击杀的敌人有 30% 几率爆炸，以自身最大生命 10% 的毒素伤害伤害附近敌人"),
    ("TreeKeystones.gd", "TREE_PARANOIA"): (
        "偏执",
        "中毒的敌人受到 20% 更多伤害"),
    ("TreeKeystones.gd", "TREE_DREAD"): (
        "恐惧",
        "附近敌人受到恐惧诅咒。敌人身上的每种未强化的元素异常状态，都会使其受到 25% 更多伤害。"),
    ("TreeKeystones.gd", "TREE_TRANSMOGRIFICATION"): (
        "变形",
        "所有掉落的武器均为施法者武器。"),
    ("TreeKeystones.gd", "TREE_FURY"): (
        "狂怒",
        "当你拥有满额恩惠时，造成 40% 更多伤害"),
    ("TreeKeystones.gd", "TREE_TRANSFUSION"): (
        "复仇印记",
        "攻击你的敌人会被施加输血标记。被输血标记的敌人受到 50% 更多持续伤害。"),
    ("TreeKeystones.gd", "TREE_BLOOD_ARMOR"): (
        "血之护甲",
        "受到攻击时获得 1 层持续 4 秒的血沸。每层血沸使生命回复提高 20%，受到的伤害降低 15%。达到 5 层血沸时，释放一次强力鲜血爆发。"),
    ("TreeKeystones.gd", "TREE_MAGMATIC_BLOOD"): (
        "岩浆之血",
        "流血与撕裂以火焰伤害结算。流血的敌人物理与火焰抗性降低 25%。"),
    ("TreeKeystones.gd", "TREE_VILE_DOMAIN"): (
        "污秽领域",
        "附近敌人被视为中毒状态。附近敌人造成 20% 更少伤害。"),
    ("TreeKeystones.gd", "TREE_ENERGETIC_FLESH"): (
        "能量之躯",
        "附近受电击影响的敌人每秒受到你最大生命 300% 的闪电伤害。造成等同于你闪电异常效果的更多伤害。"),
    ("TreeKeystones.gd", "TREE_CHAOTIC_RESONANCE"): (
        "混沌共振",
        "你的闪电伤害可以造成毒素异常状态。"),
    ("TreeKeystones.gd", "TREE_BONDED_ELECTRONS"): (
        "电子结合",
        "附近敌人的闪电抗性等同于你的闪电抗性。"),
    ("TreeKeystones.gd", "TREE_WEAPON_DEXTERITY"): (
        "武器灵巧",
        "攻击技能同时视为法术技能。法术技能同时视为攻击技能。"),
    ("TreeKeystones.gd", "TREE_OVERCOOK"): (
        "过熟",
        "焦黑的敌人受到 40% 更多火焰伤害。"),
    ("TreeKeystones.gd", "TREE_CAPABLE_COMBATANT"): (
        "能征善战",
        "格挡几率上限同时转化为更多伤害。"),
    ("TreeKeystones.gd", "TREE_COATED_BLADES"): (
        "涂层之刃",
        "物理伤害可以造成毒素异常状态。"),
    ("TreeKeystones.gd", "TREE_VIRIDIAN_SAGE"): (
        "翠绿贤者",
        "每 30 点智慧使受到的伤害降低 1%，最多降低 30%。"),
    ("TreeKeystones.gd", "TREE_STIFLED_CURSING"): (
        "窒息诅咒",
        "受到被诅咒敌人的伤害降低 20%。"),
    ("TreeKeystones.gd", "TREE_SHOCKING_MOVES"): (
        "电击步伐",
        "每 200 点总闪避使闪电伤害提高 1%，最多提高 5000%"),
    ("TreeKeystones.gd", "TREE_HOPLITE"): (
        "重装步兵",
        "同时装备近战武器与任意盾牌时，造成 60% 更多伤害。"),
    ("TreeKeystones.gd", "TREE_SWORDSMAN"): (
        "剑士",
        "装备两把近战武器时，施法速度提高 30%，造成 20% 更多伤害，受到的伤害降低 20%。"),
    # ---------------- SupportKeystones.gd (9) ----------------
    ("SupportKeystones.gd", "SUPPORT_SNIPER"): (
        "狙击手",
        "投射物无散射"),
    ("SupportKeystones.gd", "SUPPORT_COLLATERAL_DAMAGE"): (
        "附带伤害",
        "投射物命中时有 10% 几率对目标与附近敌人额外造成其 300% 的伤害。"),
    ("SupportKeystones.gd", "SUPPORT_CAST_ON_CRIT"): (
        "暴击时施放",
        "当其他技能造成暴击时施放此技能。此技能不会自动施放，也无法触发其他技能。"),
    ("SupportKeystones.gd", "SUPPORT_CAST_ON_KILL"): (
        "击杀时施放",
        "当其他技能造成击杀时，此技能有 10% 几率施放。此技能不会自动施放，也无法触发其他技能。"),
    ("SupportKeystones.gd", "SUPPORT_VOLATILITY"): (
        "易变",
        "用任何非触发技能命中敌人时施放此技能。此技能消耗全部恩惠，每消耗一个恩惠造成 20% 更多伤害。此技能不会自动施放，也无法触发其他技能。"),
    ("SupportKeystones.gd", "SUPPORT_HAMSTRING"): (
        "断筋",
        "技能命中时使敌人断筋 4 秒，移动速度降低 15%"),
    ("SupportKeystones.gd", "SUPPORT_PROLIFERATE"): (
        "扩散",
        "此技能造成的元素异常状态同样作用于附近敌人。"),
    ("SupportKeystones.gd", "SUPPORT_SACRIFICE"): (
        "牺牲",
        "技能每次施放消耗 10% 最大生命，并获得其一半作为额外物理伤害。若生命不足以支付消耗，被辅助的技能无法施放。"),
    ("SupportKeystones.gd", "SUPPORT_STATIC_ELECTRICITY"): (
        "静电",
        "命中受电击影响的敌人时，有 50% 几率引发闪电，劈向最多 3 名附近敌人并消耗电击效果。闪电造成的伤害等同于初始命中伤害乘以原敌人身上电击效果的 200%。闪电可以暴击，但无法造成异常状态。"),
    # ---------------- UniqueKeystones.gd (14) ----------------
    ("UniqueKeystones.gd", "UNIQUE_BALANCED_OPPRESSION"): (
        "平衡压迫",
        "对受寒冷影响的敌人，伤害穿透其 25% 火焰抗性"),
    ("UniqueKeystones.gd", "UNIQUE_CROWN_OF_ICE"): (
        "寒冰之冠",
        "所有伤害均以寒冷伤害结算。不再造成任何非寒冷伤害。"),
    ("UniqueKeystones.gd", "UNIQUE_STRENGTH_FROM_STRENGTH"): (
        "强者恒强",
        "每 250 点总护甲使物理伤害提高 1%，最多提高 5000%。"),
    ("UniqueKeystones.gd", "UNIQUE_GLADIATORS_RESOLVE"): (
        "角斗士的决意",
        "所有闪避转化为护甲"),
    ("UniqueKeystones.gd", "UNIQUE_MERCURIAL_VENOM"): (
        "水银剧毒",
        "敌人身上的每种异常状态使伤害穿透其 1% 闪电抗性"),
    ("UniqueKeystones.gd", "UNIQUE_SPREADING_FLAMES"): (
        "蔓延烈焰",
        "燃烧的敌人死亡时，其灼烧效果会蔓延至最多 5 名附近未燃烧的敌人。"),
    ("UniqueKeystones.gd", "UNIQUE_OGRE_TALISMAN"): (
        "食人魔护符",
        "获得最大生命 5% 的额外火焰伤害"),
    ("UniqueKeystones.gd", "UNIQUE_BOMB_SPECIALIST"): (
        "工匠的玩具",
        "无法使用非炸弹类伤害技能。炸弹技能发射双倍炸弹。"),
    ("UniqueKeystones.gd", "UNIQUE_FROZEN_SLUDGE"): (
        "冻结泥浆",
        "中毒的敌人始终拥有 -100% 寒冷抗性。"),
    ("UniqueKeystones.gd", "UNIQUE_GOBLINS_GIRDLE"): (
        "地精腰带",
        "每 3 秒获得一个坚韧恩惠。"),
    ("UniqueKeystones.gd", "UNIQUE_CHILL_BURN"): (
        "寒炎",
        "灼烧以寒冷伤害结算。"),
    ("UniqueKeystones.gd", "UNIQUE_CHEETAHS"): (
        "猎豹之速",
        "移动速度加成的 50% 同时转化为施法速度加成"),
    ("UniqueKeystones.gd", "UNIQUE_ECHOING_FURY"): (
        "回响之怒",
        "命中时有 10% 几率使敌人回响 250ms。造成回响后，附近敌人会受到该次命中伤害 140% 的伤害。回响造成的伤害可以再次造成回响。受回响影响的敌人无法被再次施加回响。"),
    ("UniqueKeystones.gd", "UNIQUE_BALANCE_OF_POWER"): (
        "力量平衡",
        "失去精准恩惠时，获得一个迅捷恩惠。"),
}

UNCERTAIN = {
    "critical_thinking": "passive 'Critical Thinking' is a crit pun; chose 批判性思维 (critic/pun) over 暴击思考",
    "major_physical_damage": "passive 'Physician' pun on Physical; chose 物理学者",
    "maximum_all_resistances": "source repeats 'Maximum Toxic Resistance' as its display name (node key maximum_all_resistances); translated verbatim to match source",
    "major_toxic_ailment_effect": "source typo 'Poison Intesity'; translated as 毒素强度",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def make_unit(src_path: Path, raw: str, raw_lines, line_no: int,
              src_value: str, tr_value: str, expect_line_text: str):
    if line_no - 1 >= len(raw_lines):
        raise SystemExit(f"line out of range: {src_path}:{line_no}")
    stripped = raw_lines[line_no - 1].strip()
    if stripped != expect_line_text:
        raise SystemExit(
            f"extract/text mismatch {src_path}:{line_no}\n"
            f" expected: {expect_line_text}\n actual:   {stripped}")
    old = stripped
    kind = "single"
    if raw.count(old) != 1:
        name_raw = raw_lines[line_no - 1]
        nxt_raw = raw_lines[line_no] if line_no < len(raw_lines) else None
        nxt_cand = (name_raw + "\n" + nxt_raw) if nxt_raw is not None else None
        if nxt_cand is not None and raw.count(nxt_cand) == 1:
            old = nxt_cand
            kind = "name+next"
        else:
            prev_raw = raw_lines[line_no - 2]
            cand = prev_raw + "\n" + name_raw
            if raw.count(cand) != 1:
                raise SystemExit(
                    f"cannot disambiguate {src_path}:{line_no} ({src_value!r}) "
                    f"count={raw.count(old)}")
            old = cand
            kind = "prev+name"
    if raw.count(old) != 1:
        raise SystemExit(f"occurrence {raw.count(old)} for {old!r} at {src_path}:{line_no}")
    quoted = '"' + src_value + '"'
    new = old.replace(quoted, '"' + tr_value + '"')
    if new == old:
        raise SystemExit(f"no-op translation at {src_path}:{line_no}")
    col = stripped.find('"') + 1
    rel = src_path.relative_to(ROOT / "04_recovered").as_posix()
    return {
        "path": rel,
        "field": "text",
        "classification": "TEXT_PATCH",
        "unit_id": f"{rel}:{line_no}:{col}",
        "old_text": old,
        "new_text": new,
        "preimage_sha256": sha256_file(src_path).upper(),
        "expected_occurrences": 1,
        "source_text": src_value,
        "translation": tr_value,
        "placeholders": [],
        "format_tokens": [],
        "tests": list(PATCH_TESTS),
        "_kind": kind,
    }


def main() -> int:
    # ---- load extracts ----
    pex = json.loads(EXTRACT_PASSIVES.read_text(encoding="utf-8"))
    kex = json.loads(EXTRACT_KEYSTONES.read_text(encoding="utf-8"))

    patches: list[dict] = []
    multi = []

    # ---- passives ----
    src = ROOT / "04_recovered/Globals/PassiveTagStats.gd"
    raw = src.read_text(encoding="utf-8")
    raw_lines = raw.split("\n")
    nodes = pex["PassiveTagStats"]["nodes"]
    if len(nodes) != 326:
        raise SystemExit(f"expected 326 passive nodes, got {len(nodes)}")
    if set(PASSIVE_TR) != {n["key"] for n in nodes}:
        raise SystemExit("PASSIVE_TR key set mismatch vs extract")
    for n in nodes:
        key, ln, lt, val = n["key"], n["name"]["line"], n["name"]["line_text"], n["name"]["value"]
        tr = PASSIVE_TR[key]
        p = make_unit(src, raw, raw_lines, ln, val, tr, lt)
        if p["_kind"] != "single":
            multi.append((p["unit_id"], p["_kind"], val))
        del p["_kind"]
        patches.append(p)

    # ---- keystones ----
    for fname, entries in kex.items():
        src = ROOT / "04_recovered/Globals/Keystones" / fname
        raw = src.read_text(encoding="utf-8")
        raw_lines = raw.split("\n")
        for e in entries:
            key, nval, nlt, nline = e["key"], e["name"]["value"], e["name"]["line_text"], e["name"]["line"]
            dval, dlt, dline = e["description"]["value"], e["description"]["line_text"], e["description"]["line"]
            t = KEYSTONE_TR.get((fname, key))
            if t is None:
                raise SystemExit(f"missing keystone translation: {fname} {key}")
            tname, tdesc = t
            patches.append(make_unit(src, raw, raw_lines, nline, nval, tname, nlt))
            patches.append(make_unit(src, raw, raw_lines, dline, dval, tdesc, dlt))

    # ---- manifest ----
    scope = (
        "ALL 326 passive node display names (PassiveTagStats.gd) and ALL 88 keystone "
        "names+descriptions (TreeKeystones.gd 65, SupportKeystones.gd 9, "
        "UniqueKeystones.gd 14); internal dict keys, stats, passive_type and texture "
        "fields untouched; 8 units use 2-line old_text (4 byte-identical duplicate name "
        "pairs disambiguated by neighbour line: " +
        "; ".join(f"{u} [{k}]" for u, k, _ in multi) +
        "); CODE_PATCH on plaintext sources in 04_recovered. "
        "TRANSLATION_UNCERTAIN: " +
        "; ".join(f"{k}: {v}" for k, v in UNCERTAIN.items())
    )
    manifest = {
        "id": "c5-l11-passive-tree-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209",
        "dependencies": [],
        "conflicts": [],
        "scope": scope,
        "entities": [
            {"kind": "localization_unit", "id": p["unit_id"],
             "classification": "DISPLAY_SAFE", "confidence": "INFERENCE_HIGH",
             "expected_runtime_effect": f"displays {p['translation']}"}
            for p in patches
        ],
        "patches": patches,
        "asset_overlays": [],
        "tests": list(MANIFEST_TESTS),
        "not_proven": "visual layout quality, persistence, gameplay, broad localization, or release readiness",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest written: {OUT}")
    print(f"units: {len(patches)}  (passives 326, tree 130, support 18, unique 28)")
    print(f"multi-line context units: {len(multi)}")
    for u, k, v in multi:
        print(f"   {u} [{k}] {v!r}")
    print("TRANSLATION_UNCERTAIN:")
    for k, v in UNCERTAIN.items():
        print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
