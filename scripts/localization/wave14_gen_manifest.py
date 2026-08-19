#!/usr/bin/env python3
"""Generate C5-L14: remaining static .tscn scene text localization manifest.

Each unit old_text/new_text = the exact full stripped serialized line from
03_raw/Scenes/**.tscn (e.g. `text = "Close"`). Runtime-overwritten
placeholders/debug strings (verified against 04_recovered .gd scripts) are
SKIPPED and reported. Translations follow docs/zh_CN_glossary.md.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "03_raw"
OUT = ROOT / "mods/c5-l14-static-scenes-zhcn/mod.json"

# ---- translation table: (relpath, line_no, old_line, new_line, source_text, translation, occurrences) ----
T = [
    # Scenes/Levels/Ladder/Ladder.tscn
    ("Scenes/Levels/Ladder/Ladder.tscn", 421, 'text = "Time Remaining:"', 'text = "剩余时间："', "Time Remaining:", "剩余时间：", 1),
    # Scenes/Levels/TestLevel/TestLevel.tscn
    ("Scenes/Levels/TestLevel/TestLevel.tscn", 396, 'text = "Time Remaining:"', 'text = "剩余时间："', "Time Remaining:", "剩余时间：", 1),
    # Scenes/Popups/Dialogs/GeneEditor/CraftButton.tscn
    ("Scenes/Popups/Dialogs/GeneEditor/CraftButton.tscn", 23, 'text = "Cost:"', 'text = "消耗："', "Cost:", "消耗：", 1),
    # Scenes/Popups/Dialogs/GeneEditor/GeneButton.tscn
    ("Scenes/Popups/Dialogs/GeneEditor/GeneButton.tscn", 52, 'text = "NEW"', 'text = "新"', "NEW", "新", 1),
    # Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 57, 'text = "Gene Name"', 'text = "基因名称"', "Gene Name", "基因名称", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 78, 'text = "Crafting Help"', 'text = "制作帮助"', "Crafting Help", "制作帮助", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 85, 'text = "Done"', 'text = "完成"', "Done", "完成", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 376, 'text = "Delete Item"', 'text = "删除物品"', "Delete Item", "删除物品", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 382, 'text = "Show Advanced Mods"', 'text = "显示高级词缀"', "Show Advanced Mods", "显示高级词缀", 1),
    # Scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.tscn
    ("Scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.tscn", 54, 'text = "Equipment Stash"', 'text = "装备仓库"', "Equipment Stash", "装备仓库", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.tscn", 61, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.tscn", 85, 'text = "Hide Low Level Items"', 'text = "隐藏低等级物品"', "Hide Low Level Items", "隐藏低等级物品", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.tscn", 98, 'text = "Search"', 'text = "搜索"', "Search", "搜索", 1),
    # Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.tscn
    ("Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.tscn", 64, 'text = "Equipped Gear"', 'text = "已装备物品"', "Equipped Gear", "已装备物品", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.tscn", 71, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.tscn", 336, 'text = "Equipment Stats"', 'text = "装备属性"', "Equipment Stats", "装备属性", 1),
    # Scenes/Popups/Dialogs/GeneEditor/LoadoutSlot.tscn
    ("Scenes/Popups/Dialogs/GeneEditor/LoadoutSlot.tscn", 77, 'text = "NEW"', 'text = "新"', "NEW", "新", 1),
    # Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn
    ("Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn", 53, 'text = "Item Transfer"', 'text = "物品转移"', "Item Transfer", "物品转移", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn", 60, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn", 76, 'text = "Your Stash"', 'text = "你的仓库"', "Your Stash", "你的仓库", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn", 102, 'text = "Shared Stash"', 'text = "共享仓库"', "Shared Stash", "共享仓库", 1),
    ("Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn", 127, 'text = "Hide Low Level Items"', 'text = "隐藏低等级物品"', "Hide Low Level Items", "隐藏低等级物品", 1),
    # Scenes/Popups/Dialogs/GeneSelector/GeneOption.tscn
    ("Scenes/Popups/Dialogs/GeneSelector/GeneOption.tscn", 20, 'text = "NEW"', 'text = "新"', "NEW", "新", 1),
    # Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn", 45, 'text = "Unequip Item"', 'text = "卸下物品"', "Unequip Item", "卸下物品", 1),
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn", 51, 'text = "Cancel"', 'text = "取消"', "Cancel", "取消", 1),
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn", 71, 'text = "Equipped Item"', 'text = "已装备物品"', "Equipped Item", "已装备物品", 1),
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn", 83, 'text = "Available Items"', 'text = "可用物品"', "Available Items", "可用物品", 1),
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn", 106, 'text = "Item Stats"', 'text = "物品属性"', "Item Stats", "物品属性", 1),
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn", 130, 'text = "Hide Low Level Items"', 'text = "隐藏低等级物品"', "Hide Low Level Items", "隐藏低等级物品", 1),
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn", 143, 'text = "Search: "', 'text = "搜索： "', "Search: ", "搜索： ", 1),
    # Scenes/Popups/Dialogs/Help/Help.tscn
    ("Scenes/Popups/Dialogs/Help/Help.tscn", 43, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    # Scenes/Popups/Dialogs/HelpTip/CraftingHelp/CraftingHelp.tscn
    ("Scenes/Popups/Dialogs/HelpTip/CraftingHelp/CraftingHelp.tscn", 27, 'text = "Crafting Help"', 'text = "制作帮助"', "Crafting Help", "制作帮助", 1),
    # Scenes/Popups/Dialogs/HelpTip/HelpTip.tscn
    ("Scenes/Popups/Dialogs/HelpTip/HelpTip.tscn", 47, 'text = "Helpful Tip"', 'text = "实用提示"', "Helpful Tip", "实用提示", 1),
    ("Scenes/Popups/Dialogs/HelpTip/HelpTip.tscn", 70, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    # Scenes/Popups/Dialogs/ModHelp/ModHelp.tscn
    ("Scenes/Popups/Dialogs/ModHelp/ModHelp.tscn", 33, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    ("Scenes/Popups/Dialogs/ModHelp/ModHelp.tscn", 47, 'text = "Mod Search "', 'text = "词缀搜索 "', "Mod Search ", "词缀搜索 ", 1),
    # Scenes/Popups/Dialogs/ModHelp/TierGroup.tscn
    ("Scenes/Popups/Dialogs/ModHelp/TierGroup.tscn", 29, 'text = "Mod Weight: "', 'text = "词缀权重： "', "Mod Weight: ", "词缀权重： ", 1),
    # Scenes/Popups/Dialogs/MTXStore/MTXItem.tscn
    ("Scenes/Popups/Dialogs/MTXStore/MTXItem.tscn", 66, 'text = "Purchase"', 'text = "购买"', "Purchase", "购买", 1),
    # Scenes/Popups/Dialogs/MTXStore/MTXStore.tscn
    ("Scenes/Popups/Dialogs/MTXStore/MTXStore.tscn", 46, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    ("Scenes/Popups/Dialogs/MTXStore/MTXStore.tscn", 70, 'text = "Cosmetics do not affect gameplay."', 'text = "外观不影响游戏玩法。"', "Cosmetics do not affect gameplay.", "外观不影响游戏玩法。", 1),
    # Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 51, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 57, 'text = "Choose Outfit"', 'text = "选择外观"', "Choose Outfit", "选择外观", 1),
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 185, 'text = "Helmets"', 'text = "头盔"', "Helmets", "头盔", 1),
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 218, 'text = "Face"', 'text = "面部"', "Face", "面部", 1),
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 250, 'text = "Gloves"', 'text = "手套"', "Gloves", "手套", 1),
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 282, 'text = "Body"', 'text = "身体"', "Body", "身体", 1),
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 314, 'text = "Boots"', 'text = "靴子"', "Boots", "靴子", 1),
    ("Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn", 346, 'text = "Back"', 'text = "背部"', "Back", "背部", 1),
    # Scenes/Popups/Dialogs/SkillLoadoutSelector/LoadOption.tscn
    ("Scenes/Popups/Dialogs/SkillLoadoutSelector/LoadOption.tscn", 25, 'text = "Delete"', 'text = "删除"', "Delete", "删除", 1),
    ("Scenes/Popups/Dialogs/SkillLoadoutSelector/LoadOption.tscn", 32, 'text = "Select"', 'text = "选择"', "Select", "选择", 1),
    # Scenes/Popups/Dialogs/SkillLoadoutSelector/SkillLoadoutSelector.tscn
    ("Scenes/Popups/Dialogs/SkillLoadoutSelector/SkillLoadoutSelector.tscn", 50, 'text = "Load Tree"', 'text = "加载天赋树"', "Load Tree", "加载天赋树", 1),
    ("Scenes/Popups/Dialogs/SkillLoadoutSelector/SkillLoadoutSelector.tscn", 57, 'text = "No Trees Saved"', 'text = "未保存的天赋树"', "No Trees Saved", "未保存的天赋树", 1),
    ("Scenes/Popups/Dialogs/SkillLoadoutSelector/SkillLoadoutSelector.tscn", 77, 'text = "Cancel"', 'text = "取消"', "Cancel", "取消", 1),
    # Scenes/Popups/Dialogs/SpecializationPicker/SpecializationPicker.tscn
    ("Scenes/Popups/Dialogs/SpecializationPicker/SpecializationPicker.tscn", 59, 'text = "Class Specializations are available starting at Level 30."', 'text = "职业专精在 30 级起可用。"', "Class Specializations are available starting at Level 30.", "职业专精在 30 级起可用。", 1),
    # Scenes/Popups/Dialogs/StarterPicker/StarterPicker.tscn
    ("Scenes/Popups/Dialogs/StarterPicker/StarterPicker.tscn", 40, 'text = "Choose a Starting Build"', 'text = "选择初始配置"', "Choose a Starting Build", "选择初始配置", 1),
    ("Scenes/Popups/Dialogs/StarterPicker/StarterPicker.tscn", 59, 'text = "You can change your skills at any time for free at the Skills and Weapons found in your hideout."', 'text = "你可以随时在藏身处中的技能与武器处免费更换技能。"', "You can change your skills at any time for free at the Skills and Weapons found in your hideout.", "你可以随时在藏身处中的技能与武器处免费更换技能。", 1),
    # Scenes/Popups/Dialogs/TextInputDialog.tscn (text = "Save" occurs on lines 50 and 93)
    ("Scenes/Popups/Dialogs/TextInputDialog.tscn", 50, 'text = "Save"', 'text = "保存"', "Save", "保存", 2),
    ("Scenes/Popups/Dialogs/TextInputDialog.tscn", 66, 'text = "Name:"', 'text = "名称："', "Name:", "名称：", 1),
    ("Scenes/Popups/Dialogs/TextInputDialog.tscn", 86, 'text = "Cancel"', 'text = "取消"', "Cancel", "取消", 1),
    # Scenes/Popups/Dialogs/TreeSelector/LoadOption.tscn
    ("Scenes/Popups/Dialogs/TreeSelector/LoadOption.tscn", 25, 'text = "Delete"', 'text = "删除"', "Delete", "删除", 1),
    ("Scenes/Popups/Dialogs/TreeSelector/LoadOption.tscn", 32, 'text = "Select"', 'text = "选择"', "Select", "选择", 1),
    # Scenes/Popups/Dialogs/TreeSelector/TreeSelector.tscn
    ("Scenes/Popups/Dialogs/TreeSelector/TreeSelector.tscn", 50, 'text = "Load Tree"', 'text = "加载天赋树"', "Load Tree", "加载天赋树", 1),
    ("Scenes/Popups/Dialogs/TreeSelector/TreeSelector.tscn", 57, 'text = "No Trees Saved"', 'text = "未保存的天赋树"', "No Trees Saved", "未保存的天赋树", 1),
    ("Scenes/Popups/Dialogs/TreeSelector/TreeSelector.tscn", 77, 'text = "Cancel"', 'text = "取消"', "Cancel", "取消", 1),
    # Scenes/Popups/Dialogs/UniqueHelp/UniqueHelp.tscn
    ("Scenes/Popups/Dialogs/UniqueHelp/UniqueHelp.tscn", 33, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    # Scenes/Popups/Dialogs/WorldMap/MapNode.tscn
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 90, 'text = "Rank"', 'text = "排名"', "Rank", "排名", 1),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 96, 'text = "Player"', 'text = "玩家"', "Player", "玩家", 1),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 104, 'text = "Level"', 'text = "等级"', "Level", "等级", 1),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 112, 'text = "Specialization"', 'text = "专精"', "Specialization", "专精", 1),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 120, 'text = "Score"', 'text = "分数"', "Score", "分数", 1),
    # Scenes/Popups/Dialogs/WorldMap/WorldMapPopup.tscn
    ("Scenes/Popups/Dialogs/WorldMap/WorldMapPopup.tscn", 64, 'text = "Choose a Zone"', 'text = "选择区域"', "Choose a Zone", "选择区域", 1),
    ("Scenes/Popups/Dialogs/WorldMap/WorldMapPopup.tscn", 71, 'text = "Close"', 'text = "关闭"', "Close", "关闭", 1),
    # Scenes/Popups/ItemTabContent.tscn
    ("Scenes/Popups/ItemTabContent.tscn", 58, 'text = "Base Damage:"', 'text = "基础伤害："', "Base Damage:", "基础伤害：", 1),
    # Scenes/UI/ModItem.tscn
    ("Scenes/UI/ModItem.tscn", 48, 'text = "Lock"', 'text = "锁定"', "Lock", "锁定", 1),
]

# ---- skipped (runtime-overwritten / debug placeholders, verified vs 04_recovered .gd) ----
SKIPPED = [
    # (relpath, line, line_text, reason)
    ("Scenes/Levels/Ladder/Ladder.tscn", 430, 'text = "30s"', "TimeLabel overwritten every 0.1s by Ladder.gd _on_TimeUpdater_timeout (str(remaining)+'s'); numeric"),
    ("Scenes/Levels/TestLevel/TestLevel.tscn", 405, 'text = "30s"', "TimeLabel runtime countdown value; numeric"),
    ("Scenes/Particles/FloatingDamage.tscn", 14, 'text = "test"', "debug placeholder; text set at runtime by script on spawn"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 173, 'text = "5"', "BlueOrbLabel overwritten in GeneEditor.gd _ready (str(orbs.blue)); numeric"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 193, 'text = "5"', "RedOrbLabel overwritten in GeneEditor.gd _ready (str(orbs.red)); numeric"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 213, 'text = "5"', "GreenOrbLabel overwritten in GeneEditor.gd _ready (str(orbs.green)); numeric"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 233, 'text = "5"', "GoldOrbLabel overwritten in GeneEditor.gd _ready (str(orbs.gold)); numeric"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 253, 'text = "5"', "CorruptionLabel overwritten in GeneEditor.gd _ready (str(orbs.corruption)); numeric"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 275, 'text = "UNIQUE NAME"', "UniqueNameLabel hidden (visible=false) and set to unique_meta.name in GeneEditor.gd"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 298, 'text = "UNIQUE NAME"', "GeneLevelLabel set to 'Item Level: '+str(gene.level) in GeneEditor.gd"),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn", 306, 'text = "UNIQUE NAME"', "GeneQualityLabel hidden and set to quality text in GeneEditor.gd"),
    ("Scenes/Popups/Dialogs/GeneSelector/GeneOption.tscn", 9, 'text = "Gene 1"', "overwritten in GeneOption.gd _ready (text = gene.name)"),
    ("Scenes/Popups/Dialogs/SpecializationPicker/SpecializationOption.tscn", 24, 'text = "asfasdfasdf"', "debug placeholder; overwritten in SpecializationOption.gd _ready"),
    ("Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.tscn", 15, 'text = "Frozen Sludge"', "sample data; Name label set to data.name in UniqueItem.gd _ready"),
    ("Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.tscn", 22, 'text = "Frozen Sludge"', "sample data; Basename set to base type name in UniqueItem.gd _ready"),
    ("Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.tscn", 30, 'text = "Frozen Sludge"', "sample data; Description set to data.flavor in UniqueItem.gd _ready"),
    ("Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.tscn", 37, 'text = "Frozen Sludge"', "sample data; DropLevel set to 'Minimum Drop Level: '+str in UniqueItem.gd _ready"),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 50, 'text = "Abandoned Cave"', "NodeNameLabel set to zone name in MapNode.gd _ready"),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 56, 'text = "Zone Level: 10"', "ZoneLabel set to 'Zone Level: '+str(zone_level) in MapNode.gd _ready"),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 63, 'text = "Zone Level: 10"', "ItemQuanityLabel hidden and set in MapNode.gd _ready"),
    ("Scenes/Popups/Dialogs/WorldMap/MapNode.tscn", 70, 'text = "Zone Level: 10"', "ItemRarityLabel hidden and set in MapNode.gd _ready"),
    ("Scenes/Popups/ItemTabContent.tscn", 23, 'text = "Item Name goes here"', "ItemNameLabel set in ItemTabContent.gd _ready (Skills.config[item.name].name)"),
    ("Scenes/Popups/ItemTabContent.tscn", 31, 'text = "Item Name goes here"', "ItemTagsLabel set in ItemTabContent.gd _ready (render_tag_list)"),
    ("Scenes/Popups/ItemTabContent.tscn", 39, 'text = "Item Supports go here."', "ItemSupportLabel set in ItemTabContent.gd _ready (render_supports)"),
    ("Scenes/Popups/ItemTabContent.tscn", 47, 'text = "Item Name goes here"', "ItemTierLabel set in ItemTabContent.gd _ready ('Current Tier: '+str)"),
    ("Scenes/Popups/ItemTabContent.tscn", 64, 'text = "0"', "DamageTypeLabel set in ItemTabContent.gd _ready; numeric"),
    ("Scenes/Popups/ItemTabContent.tscn", 70, 'text = "Item Description goes here"', "ItemDescriptionLabel set in ItemTabContent.gd _ready (description)"),
    ("Scenes/Popups/Dialogs/MTXStore/MTXItem.tscn", 28, 'text = "Cosmetic Name"', "NameLabel set in MTXItem.gd _ready (MtxManager.MTX_DEFINITIONS[item_id].name)"),
    ("Scenes/Popups/Dialogs/MTXStore/MTXItem.tscn", 58, 'text = "Price Here"', "PriceLabel set in MTXItem.gd _ready (price / 'Owned')"),
    ("Scenes/Popups/Unlocks/CharacterUnlockItem.tscn", 29, 'text = "Vesta has been unlocked!"', "UnlockDescription set in CharacterUnlockItem.gd _ready (description var)"),
    ("Scenes/Popups/Unlocks/CharacterUnlockItem.tscn", 35, 'text = "Requirements uncertain"', "UnlockRequirement set in CharacterUnlockItem.gd _ready (subtext var)"),
    ("Scenes/Popups/Unlocks/LevelUnlockItem.tscn", 19, 'text = "Vesta has been unlocked!"', "UnlockDescription set in LevelUnlockItem.gd _ready (description var)"),
    ("Scenes/Popups/Unlocks/LevelUnlockItem.tscn", 26, 'text = "Requirements uncertain"', "UnlockRequirement set in LevelUnlockItem.gd _ready (subtext var)"),
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.tscn", 22, 'text = "Gene Name"', "GeneNameLabel set in GeneInfo.gd render (gene.name)"),
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.tscn", 29, 'text = "Offensive Gene"', "GeneTypeLabel set in GeneInfo.gd render (name_for_base_type)"),
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.tscn", 37, 'text = "Offensive Gene"', "GeneSlotLabel hidden (visible=false) and set in GeneInfo.gd render"),
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.tscn", 44, 'text = "Gene Level: 32"', "GeneLevelLabel set to 'Item Level: '+str(gene.level) in GeneInfo.gd render"),
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.tscn", 53, 'text = "Gene Level: 32"', "GeneQualityLabel hidden and set in GeneInfo.gd render"),
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.tscn", 61, 'text = "flavor"', "debug placeholder; GeneFlavor hidden until set to unique_info.flavor"),
    ("Scenes/UI/ModItem.tscn", 23, 'text = "test"', "ModName hidden (visible=false) and set in ModItem.gd _ready"),
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
        src_path = RAW / rel
        content = src_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        if line_no - 1 >= len(lines):
            raise SystemExit(f"line out of range: {rel}:{line_no}")
        actual = lines[line_no - 1].strip()
        if old != actual:
            raise SystemExit(f"line mismatch {rel}:{line_no}\n expected: {old}\n actual:   {actual}")
        count = content.count(old)
        if count != occurrences:
            raise SystemExit(f"occurrence {count} != {occurrences} for {old!r} at {rel}:{line_no}")
        preimage = sha256_file(src_path).upper()
        col = actual.find('"') + 2  # 1-based column of first value character (matches c5-l6 scene text precedent)
        unit_id = f"{rel}:{line_no}:{col}"
        patches.append({
            "path": rel,
            "field": "text",
            "classification": "TEXT_PATCH",
            "unit_id": unit_id,
            "old_text": old,
            "new_text": new,
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
    patches = build_patches(T)

    files = sorted({p["path"] for p in patches})
    manifest = {
        "id": "c5-l14-static-scenes-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209",
        "dependencies": [],
        "conflicts": [],
        "scope": f"remaining static player-visible text= lines in {len(files)} runtime .tscn scenes (ladder/test-level HUD, gene editor family, gene selector, help/help-tip/crafting help, mod help + tier groups, MTX store, outfit selector, skill/tree loadout selectors, specialization/starter pickers, text input dialog, unique help, world map + leaderboard headers, item tab content, mod item lock button); runtime-overwritten placeholder/debug strings excluded (see SKIPPED in generator)",
        "entities": [
            {"kind": "localization_unit", "id": p["unit_id"], "classification": "DISPLAY_SAFE",
             "confidence": "INFERENCE_HIGH",
             "expected_runtime_effect": f"displays {p['translation']}"}
            for p in patches
        ],
        "patches": patches,
        "asset_overlays": [],
        "tests": [
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
        ],
        "not_proven": "visual layout quality, persistence, gameplay, broad localization, or release readiness",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest written: {OUT}")
    print(f"patches: {len(patches)}")
    print(f"files: {len(files)}")
    print(f"skipped: {len(SKIPPED)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
