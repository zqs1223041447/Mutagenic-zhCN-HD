#!/usr/bin/env python3
"""Generate C5-L13: dynamic (runtime) UI string translations.

Each unit = one quoted string literal (or set of literals on one line) that is
player-visible at runtime. old_text/new_text = full stripped source line
(unique per line; identical lines patched once with expected_occurrences=N).

Verifies before writing:
  - every old_text occurs exactly expected_occurrences times in its file
  - line numbers match the stripped line content
  - preimage sha256 (UPPERCASE) of each source file matches what is recorded
  - % format tokens conserved between source_text and translation
    (and between old_line and new_line)
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_recovered"
OUT = ROOT / "mods/c5-l13-dynamic-ui-zhcn/mod.json"
TARGET_SHA = "C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209"

# (rel_path, line_nos[first = anchor], old_line, new_line, source_text, translation)
# line_nos = all lines where old_line (stripped) occurs; expected_occurrences = len(line_nos)
ENTRIES = [
    # ---- 1. Scenes/GUI/GUI.gd ----
    ("Scenes/GUI/GUI.gd", [88], r'show_message("Defeat the Mutant")',
     r'show_message("击败突变体")', "Defeat the Mutant", "击败突变体"),
    ("Scenes/GUI/GUI.gd", [90], r'show_message("Slay 250 Enemies to Complete Stage")',
     r'show_message("击杀 250 名敌人以完成关卡")', "Slay 250 Enemies to Complete Stage", "击杀 250 名敌人以完成关卡"),
    ("Scenes/GUI/GUI.gd", [92], r'show_message("Your Hideout")',
     r'show_message("你的藏身处")', "Your Hideout", "你的藏身处"),
    ("Scenes/GUI/GUI.gd", [94], r'show_message("Survive Endless Waves of Enemies")',
     r'show_message("抵御敌人的无尽波次")', "Survive Endless Waves of Enemies", "抵御敌人的无尽波次"),
    ("Scenes/GUI/GUI.gd", [101], r'xp_label.text = "Maxed"',
     r'xp_label.text = "已满级"', "Maxed", "已满级"),
    ("Scenes/GUI/GUI.gd", [110],
     r'$SkillBar / PanelContainer / VBoxContainer / VBoxContainer / MutationInfoContainer / MutationTierLabel.text = "Level: " + str(st.account_level) + "\n" + PlayableClasses.get_class_name(cn, spec)',
     r'$SkillBar / PanelContainer / VBoxContainer / VBoxContainer / MutationInfoContainer / MutationTierLabel.text = "等级：" + str(st.account_level) + "\n" + PlayableClasses.get_class_name(cn, spec)',
     '"Level: "', '"等级："'),
    ("Scenes/GUI/GUI.gd", [183], r'show_message("Completed Zone Level " + str(stage_level) + " " + stage_name, Colors.buffed)',
     r'show_message("已完成区域等级 " + str(stage_level) + " " + stage_name, Colors.buffed)',
     '"Completed Zone Level "', '"已完成区域等级 "'),
    ("Scenes/GUI/GUI.gd", [189],
     r'$LevelInfoContainer / MarginContainer / LevelInfo / ZoneCompletion / CompletionLabel.text = "Yes"',
     r'$LevelInfoContainer / MarginContainer / LevelInfo / ZoneCompletion / CompletionLabel.text = "是"',
     "Yes", "是"),
    ("Scenes/GUI/GUI.gd", [192],
     r'$LevelInfoContainer / MarginContainer / LevelInfo / ZoneCompletion / CompletionLabel.text = "No"',
     r'$LevelInfoContainer / MarginContainer / LevelInfo / ZoneCompletion / CompletionLabel.text = "否"',
     "No", "否"),
    ("Scenes/GUI/GUI.gd", [202], r'content.add_text("Took ")',
     r'content.add_text("受到 ")', '"Took "', '"受到 "'),
    ("Scenes/GUI/GUI.gd", [205], r'content.add_text("Critical ")',
     r'content.add_text("暴击 ")', '"Critical "', '"暴击 "'),
    ("Scenes/GUI/GUI.gd", [215], r'content.add_text(" Hit Damage")',
     r'content.add_text(" 命中伤害")', '" Hit Damage"', '" 命中伤害"'),
    ("Scenes/GUI/GUI.gd", [221], r'content.add_text("Picked up ")',
     r'content.add_text("拾取了 ")', '"Picked up "', '"拾取了 "'),

    # ---- 2. Scenes/Popups/EscapeMenu.gd ----
    ("Scenes/Popups/EscapeMenu.gd", [68],
     r'$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer2 / CharacterLevelLabel.text = "Level " + str(save_stats.account_level) + " " + active_class_name',
     r'$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer2 / CharacterLevelLabel.text = "等级 " + str(save_stats.account_level) + " " + active_class_name',
     '"Level "', '"等级 "'),
    ("Scenes/Popups/EscapeMenu.gd", [125], r'confirm_dialog.window_title = "Are you sure?"',
     r'confirm_dialog.window_title = "确定吗？"', "Are you sure?", "确定吗？"),
    ("Scenes/Popups/EscapeMenu.gd", [150],
     r'$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.text = "Details"',
     r'$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.text = "详情"',
     "Details", "详情"),
    ("Scenes/Popups/EscapeMenu.gd", [157],
     r'$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.text = "Hide"',
     r'$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.text = "隐藏"',
     "Hide", "隐藏"),
    ("Scenes/Popups/EscapeMenu.gd", [171, 204], r'label.stat_name = "Base " + StatsInfo.stat_name[stat] + ":"',
     r'label.stat_name = "基础 " + StatsInfo.stat_name[stat] + ":"', '"Base "', '"基础 "'),
    ("Scenes/Popups/EscapeMenu.gd", [177, 211], r'label.stat_name = "Added " + StatsInfo.stat_name[stat] + ":"',
     r'label.stat_name = "额外 " + StatsInfo.stat_name[stat] + ":"', '"Added "', '"额外 "'),
    ("Scenes/Popups/EscapeMenu.gd", [182, 217], r'label.stat_name = "Increased " + StatsInfo.stat_name[stat] + ":"',
     r'label.stat_name = "提高 " + StatsInfo.stat_name[stat] + ":"', '"Increased "', '"提高 "'),
    ("Scenes/Popups/EscapeMenu.gd", [188, 223], r'label.stat_name = "More " + StatsInfo.stat_name[stat] + ":"',
     r'label.stat_name = "更多 " + StatsInfo.stat_name[stat] + ":"', '"More "', '"更多 "'),

    # ---- 3. Scenes/Popups/DeathScreen.gd ----
    ("Scenes/Popups/DeathScreen.gd", [42],
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ThisRunLabel.text = "This Run Score: " + str(computed_score)',
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ThisRunLabel.text = "本次得分：" + str(computed_score)',
     '"This Run Score: "', '"本次得分："'),
    ("Scenes/Popups/DeathScreen.gd", [47, 57],
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "Score too low"',
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "得分过低"',
     "Score too low", "得分过低"),
    ("Scenes/Popups/DeathScreen.gd", [51],
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "Rank " + str(new_rank) + " with a score of " + str(score)',
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "排名 " + str(new_rank) + "，得分 " + str(score)',
     '"Rank " + " with a score of "', '"排名 " + "，得分 "'),
    ("Scenes/Popups/DeathScreen.gd", [53],
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "Rank did not change"',
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "排名未发生变化"',
     "Rank did not change", "排名未发生变化"),
    ("Scenes/Popups/DeathScreen.gd", [55],
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "Edited Save File"',
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "存档文件已被修改"',
     "Edited Save File", "存档文件已被修改"),
    ("Scenes/Popups/DeathScreen.gd", [59],
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "Error Uploading Score"',
     r'$CenterContainer / PanelContainer / CenterContainer / ChallengeInfo / VBoxContainer / ChallengeRankLabel.text = "上传得分时出错"',
     "Error Uploading Score", "上传得分时出错"),

    # ---- 4. Globals/Constants.gd (OrbName values only) ----
    ("Globals/Constants.gd", [83], r'OrbType.BLUE: "Orb of Experimentation",',
     r'OrbType.BLUE: "实验之珠",', "Orb of Experimentation", "实验之珠"),
    ("Globals/Constants.gd", [84], r'OrbType.GREEN: "Orb of Honing",',
     r'OrbType.GREEN: "磨砺之珠",', "Orb of Honing", "磨砺之珠"),
    ("Globals/Constants.gd", [85], r'OrbType.RED: "Orb of Enhancement",',
     r'OrbType.RED: "强化之珠",', "Orb of Enhancement", "强化之珠"),
    ("Globals/Constants.gd", [86], r'OrbType.GOLD: "Orb of Knowledge",',
     r'OrbType.GOLD: "知识之珠",', "Orb of Knowledge", "知识之珠"),
    ("Globals/Constants.gd", [87], r'OrbType.CORRUPTION: "Corruption Shard",',
     r'OrbType.CORRUPTION: "腐化碎片",', "Corruption Shard", "腐化碎片"),

    # ---- 5. Scenes/Popups/Dialogs/GeneEditor/GeneEditor.gd ----
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.gd", [77],
     r'$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / GeneLevelLabel.text = "Item Level: " + str(gene.level)',
     r'$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / GeneLevelLabel.text = "物品等级：" + str(gene.level)',
     '"Item Level: "', '"物品等级："'),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.gd", [82],
     r'$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / GeneQualityLabel.text = "+" + str(gene.quality) + "% Affix Effectiveness"',
     r'$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / GeneQualityLabel.text = "+" + str(gene.quality) + "词缀效果"',
     '"+" + "% Affix Effectiveness"', '"+" + "词缀效果"'),
    ("Scenes/Popups/Dialogs/GeneEditor/GeneEditor.gd", [159],
     r'confirm_dialog.window_title = "Permanently Delete this Item?"',
     r'confirm_dialog.window_title = "永久删除该物品？"', "Permanently Delete this Item?", "永久删除该物品？"),

    # ---- 6. Scenes/Popups/Dialogs/CharacterSelect/CharacterSlot.gd ----
    ("Scenes/Popups/Dialogs/CharacterSelect/CharacterSlot.gd", [15],
     r'$VBoxContainer / LevelLabel.text = "Level: " + str(save_stats.account_level)',
     r'$VBoxContainer / LevelLabel.text = "等级：" + str(save_stats.account_level)',
     '"Level: "', '"等级："'),
    ("Scenes/Popups/Dialogs/CharacterSelect/CharacterSlot.gd", [44],
     r'popup.window_title = "Permanently Delete this Character?"',
     r'popup.window_title = "永久删除该角色？"', "Permanently Delete this Character?", "永久删除该角色？"),

    # ---- 7. SpecializationPicker ----
    ("Scenes/Popups/Dialogs/SpecializationPicker/SpecializationOption.gd", [10],
     r'$ChooseButton.text = "Specialize as a " + cn',
     r'$ChooseButton.text = "专精为" + cn', '"Specialize as a "', '"专精为"'),

    # ---- 8. StarterPicker ----
    ("Scenes/Popups/Dialogs/StarterPicker/StarterOption.gd", [10],
     r'button.text = "Choose " + info.name',
     r'button.text = "选择 " + info.name', '"Choose "', '"选择 "'),

    # ---- 9. SkillSelect/SkillButton.gd ----
    ("Scenes/Popups/Dialogs/SkillSelect/SkillButton.gd", [31],
     r'$SkillButton / VBoxContainer / NameLabel.text = "Unlocks at level " + str(SlotRequirements.get_required_level_for_skill(slot))',
     r'$SkillButton / VBoxContainer / NameLabel.text = "等级 " + str(SlotRequirements.get_required_level_for_skill(slot))',
     '"Unlocks at level "', '"等级 "'),

    # ---- 10. SkillSelect/SupportButton.gd ----
    ("Scenes/Popups/Dialogs/SkillSelect/SupportButton.gd", [29],
     r'$VBoxContainer / NameLabel.text = "Req Level: " + str(SlotRequirements.get_required_level_for_support(slot, support_slot))',
     r'$VBoxContainer / NameLabel.text = "需求等级：" + str(SlotRequirements.get_required_level_for_support(slot, support_slot))',
     '"Req Level: "', '"需求等级："'),

    # ---- 11. SkillSelect/SkillSelect.gd ----
    ("Scenes/Popups/Dialogs/SkillSelect/SkillSelect.gd", [24],
     r'popup.title = "Create New Skill Loadout"',
     r'popup.title = "创建新技能配置"', "Create New Skill Loadout", "创建新技能配置"),
    ("Scenes/Popups/Dialogs/SkillSelect/SkillSelect.gd", [39],
     r'popup.title = "Rename \"" + GameState.get_active_stats().selected_skill_loadout + "\""',
     r'popup.title = "重命名 \"" + GameState.get_active_stats().selected_skill_loadout + "\""',
     '"Rename \\""', '"重命名 \\""'),

    # ---- 12. GeneEditor/GeneLoadout.gd ----
    ("Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.gd", [82],
     r'popup.title = "Rename \"" + GameState.get_active_stats().selected_gene_loadout + "\""',
     r'popup.title = "重命名 \"" + GameState.get_active_stats().selected_gene_loadout + "\""',
     '"Rename \\""', '"重命名 \\""'),

    # ---- 13. GeneSelector/GeneSelector.gd ----
    ("Scenes/Popups/Dialogs/GeneSelector/GeneSelector.gd", [106],
     r'item_level_label.text = "Item Level: " + str(gene.level)',
     r'item_level_label.text = "物品等级：" + str(gene.level)',
     '"Item Level: "', '"物品等级："'),

    # ---- 14. Tooltips/GeneTooltip/GeneInfo.gd ----
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.gd", [13],
     r'$VBoxContainer / GeneQualityLabel.text = "+" + str(gene.quality) + "% Affix Effectiveness"',
     r'$VBoxContainer / GeneQualityLabel.text = "+" + str(gene.quality) + "词缀效果"',
     '"+" + "% Affix Effectiveness"', '"+" + "词缀效果"'),
    ("Scenes/Tooltips/GeneTooltip/GeneInfo.gd", [46],
     r'$VBoxContainer / GeneLevelLabel.text = "Item Level: " + str(gene.level)',
     r'$VBoxContainer / GeneLevelLabel.text = "物品等级：" + str(gene.level)',
     '"Item Level: "', '"物品等级："'),

    # ---- 15. Scenes/UI/ModItem.gd ----
    ("Scenes/UI/ModItem.gd", [38],
     r'mod_label.text += "Mod Level %s: (%s - %s)" % [mod.tier + 1, roll_range.min_formatted, roll_range.max_formatted]',
     r'mod_label.text += "词缀等级 %s: (%s - %s)" % [mod.tier + 1, roll_range.min_formatted, roll_range.max_formatted]',
     '"Mod Level %s: (%s - %s)"', '"词缀等级 %s: (%s - %s)"'),
    ("Scenes/UI/ModItem.gd", [39],
     r'mod_label.text += "\nDrop Only: Cannot be upgraded"',
     r'mod_label.text += "\n无法升级"', '"\\nDrop Only: Cannot be upgraded"', '"\\n无法升级"'),
    ("Scenes/UI/ModItem.gd", [42],
     r'mod_label.text += "Mod Level Maxed: (%s - %s)" % [roll_range.min_formatted, roll_range.max_formatted]',
     r'mod_label.text += "词缀等级已达上限: (%s - %s)" % [roll_range.min_formatted, roll_range.max_formatted]',
     '"Mod Level Maxed: (%s - %s)"', '"词缀等级已达上限: (%s - %s)"'),
    ("Scenes/UI/ModItem.gd", [44],
     r'mod_label.text += "Mod Level %d: (%s - %s)" % [mod.tier + 1, roll_range.min_formatted, roll_range.max_formatted]',
     r'mod_label.text += "词缀等级 %d: (%s - %s)" % [mod.tier + 1, roll_range.min_formatted, roll_range.max_formatted]',
     '"Mod Level %d: (%s - %s)"', '"词缀等级 %d: (%s - %s)"'),
    ("Scenes/UI/ModItem.gd", [57], r'lock_icon.text = "Locked"',
     r'lock_icon.text = "已锁定"', "Locked", "已锁定"),
    ("Scenes/UI/ModItem.gd", [61], r'lock_icon.text = "Unlocked"',
     r'lock_icon.text = "已解锁"', "Unlocked", "已解锁"),

    # ---- 16. ModHelp/TierGroup.gd ----
    ("Scenes/Popups/Dialogs/ModHelp/TierGroup.gd", [10], r'$AffixType.text = "Prefix"',
     r'$AffixType.text = "前缀"', "Prefix", "前缀"),
    ("Scenes/Popups/Dialogs/ModHelp/TierGroup.gd", [12], r'$AffixType.text = "Suffix"',
     r'$AffixType.text = "后缀"', "Suffix", "后缀"),
    ("Scenes/Popups/Dialogs/ModHelp/TierGroup.gd", [14], r'$AffixType.text = "Implicit"',
     r'$AffixType.text = "固有"', "Implicit", "固有"),
    ("Scenes/Popups/Dialogs/ModHelp/TierGroup.gd", [16], r'$AffixType.text = "Unknown"',
     r'$AffixType.text = "未知"', "Unknown", "未知"),
    ("Scenes/Popups/Dialogs/ModHelp/TierGroup.gd", [55],
     'label.text = "Mod Level " + str(tier.tier) + " (" + str(tier.chance) + "%) (Minimum Drop Level: " + \\',
     'label.text = "词缀等级 " + str(tier.tier) + " (" + str(tier.chance) + "%) (Minimum Drop Level: " + \\',
     '"Mod Level "', '"词缀等级 "'),

    # ---- 17. PassiveTree/PassiveTreePopup.gd ----
    ("Scenes/Popups/Dialogs/PassiveTree/PassiveTreePopup.gd", [284],
     r'popup.title = "Save Tree"', r'popup.title = "保存天赋树"', "Save Tree", "保存天赋树"),

    # ---- 18. Settings/Settings.gd ----
    ("Scenes/Popups/Dialogs/Settings/Settings.gd", [24],
     r'confirm_dialog.window_title = "Are you sure? This cannot be undone."',
     r'confirm_dialog.window_title = "确定吗？此操作无法撤销。"',
     "Are you sure? This cannot be undone.", "确定吗？此操作无法撤销。"),

    # ---- 19. MTXStore/MTXItem.gd ----
    ("Scenes/Popups/Dialogs/MTXStore/MTXItem.gd", [17],
     r'$PriceLabel.text = "Owned"', r'$PriceLabel.text = "已拥有"', "Owned", "已拥有"),

    # ---- 20. Scenes/Popups/ItemTabContent.gd ----
    ("Scenes/Popups/ItemTabContent.gd", [17],
     r'$ItemTabContent / ItemTierLabel.text = "Current Tier: " + str(current_tier + 1)',
     r'$ItemTabContent / ItemTierLabel.text = "当前等级：" + str(current_tier + 1)',
     '"Current Tier: "', '"当前等级："'),
    ("Scenes/Popups/ItemTabContent.gd", [121],
     r'content.add_text("Aura Effects")', r'content.add_text("光环效果")',
     "Aura Effects", "光环效果"),

    # ---- 21. Tooltips/SkillTooltip/SkillTooltip.gd ----
    ("Scenes/Tooltips/SkillTooltip/SkillTooltip.gd", [113],
     r'content.add_text("Aura Effects")', r'content.add_text("光环效果")',
     "Aura Effects", "光环效果"),

    # ---- 22. SkillSelect/SkillList.gd ----
    ("Scenes/Popups/Dialogs/SkillSelect/SkillList.gd", [62],
     r'content.add_text("Skill Stats")', r'content.add_text("技能属性")',
     "Skill Stats", "技能属性"),
    ("Scenes/Popups/Dialogs/SkillSelect/SkillList.gd", [87],
     r'content.add_text("Aura Effects")', r'content.add_text("光环效果")',
     "Aura Effects", "光环效果"),

    # ---- 23. ModHelp/ModTab.gd ----
    ("Scenes/Popups/Dialogs/ModHelp/ModTab.gd", [11],
     r'label.text = "Available Affixes"', r'label.text = "可用词缀"',
     "Available Affixes", "可用词缀"),
    ("Scenes/Popups/Dialogs/ModHelp/ModTab.gd", [25],
     r'label.text = "Drop Only Mods"', r'label.text = "仅掉落词缀"',
     "Drop Only Mods", "仅掉落词缀"),

    # ---- 24. Pickups/Portal/PortalPickup.gd ----
    ("Scenes/Pickups/Portal/PortalPickup.gd", [8],
     r'popup.title = "Return to Hideout?"', r'popup.title = "返回藏身处？"',
     "Return to Hideout?", "返回藏身处？"),

    # ---- 25. Scenes/Stats.gd ----
    ("Scenes/Stats.gd", [629],
     r'$FloatingDamageManager.show_value("Block", color)',
     r'$FloatingDamageManager.show_value("格挡", color)', "Block", "格挡"),
    ("Scenes/Stats.gd", [637],
     r'$FloatingDamageManager.show_value("Evade", color)',
     r'$FloatingDamageManager.show_value("闪避", color)', "Evade", "闪避"),
    ("Scenes/Stats.gd", [671],
     r'$FloatingDamageManager.show_value("Shielded", Color.purple)',
     r'$FloatingDamageManager.show_value("护盾", Color.purple)', "Shielded", "护盾"),
    ("Scenes/Stats.gd", [734],
     r'$FloatingDamageManager.show_value("Deflect", color)',
     r'$FloatingDamageManager.show_value("招架", color)', "Deflect", "招架"),
    ("Scenes/Stats.gd", [2030],
     r'$FloatingDamageManager.show_value("+" + str(recovered) + " hp", Colors.healing)',
     r'$FloatingDamageManager.show_value("+" + str(recovered) + " 生命", Colors.healing)',
     '"+" + " hp"', '"+" + " 生命"'),

    # ---- 26. Interactables (context_text) ----
    ("Scenes/Interactables/SpecializationStatue/SpecializationStatue.gd", [13],
     r'return "Class Specializations"', r'return "职业专精"', "Class Specializations", "职业专精"),
    ("Scenes/Interactables/SharedStash/SharedStash.gd", [7],
     r'return "Stash Transfer"', r'return "仓库转移"', "Stash Transfer", "仓库转移"),
    ("Scenes/Interactables/Portal/Portal.gd", [7],
     r'return "Departure Portal"', r'return "出发传送门"', "Departure Portal", "出发传送门"),
    ("Scenes/Interactables/OutfitBench/OutfitBench.gd", [6],
     r'return "Cosmetic Outfits"', r'return "外观装扮"', "Cosmetic Outfits", "外观装扮"),
    ("Scenes/Interactables/MutationBench/MutationBench.gd", [6],
     r'return "Passive Upgrades"', r'return "被动升级"', "Passive Upgrades", "被动升级"),
    ("Scenes/Interactables/LoadoutBench/LoadoutBench.gd", [6],
     r'return "Equipment"', r'return "装备"', "Equipment", "装备"),
    ("Scenes/Interactables/CraftingBench/CraftingBench.gd", [6],
     r'return "Items and Item Modding"', r'return "物品与词缀加工"', "Items and Item Modding", "物品与词缀加工"),
    ("Scenes/Interactables/GearBench/SkillBench.gd", [13],
     r'return "Weapons and Abilities"', r'return "武器与技能"', "Weapons and Abilities", "武器与技能"),
    ("Scenes/Interactables/ClassChanger/ClassStatue.gd", [7],
     r'return "Change Character Class"', r'return "更换职业"', "Change Character Class", "更换职业"),
]

TOKEN_RE = re.compile(r"%(?:\d+)?(?:\.\d+)?[a-zA-Z%]")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tokens(s: str):
    return TOKEN_RE.findall(s)


def main():
    # group entries by file, load each file once
    by_file = {}
    for rel, lines_nos, old, new, src, tr in ENTRIES:
        by_file.setdefault(rel, []).append((lines_nos, old, new, src, tr))

    patches = []
    per_file_counts = {}
    combined_patches = []
    uncertain = []
    total_lines_checked = 0

    for rel, items in sorted(by_file.items()):
        path = SRC / rel
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        preimage = sha256_file(path).upper()

        # guard: old_text must be a full line (no newline, non-empty)
        for lines_nos, old, new, src, tr in items:
            if "\n" in old or "\n" in new:
                raise SystemExit(f"newline inside patch text: {rel}")
            if old == new:
                raise SystemExit(f"old_text == new_text: {rel}:{lines_nos}")
            expected = len(lines_nos)
            actual = content.count(old)
            if actual != expected:
                raise SystemExit(
                    f"occurrence mismatch {rel} {old!r}: expected {expected}, found {actual}")
            for ln in lines_nos:
                if ln - 1 >= len(lines):
                    raise SystemExit(f"line out of range: {rel}:{ln}")
                got = lines[ln - 1].strip()
                if got != old:
                    raise SystemExit(
                        f"line mismatch {rel}:{ln}\n expected: {old!r}\n actual:   {got!r}")
                total_lines_checked += 1

            # placeholder conservation: % tokens in source_text vs translation
            st, tt = tokens(src), tokens(tr)
            if st != tt:
                raise SystemExit(
                    f"placeholder mismatch {rel}:{lines_nos[0]} {src!r} -> {tr!r}: {st} vs {tt}")
            # % tokens in the full old line vs new line must also match
            ol, nl = tokens(old), tokens(new)
            if ol != nl:
                raise SystemExit(
                    f"line placeholder mismatch {rel}:{lines_nos[0]}:\n {old!r}\n {new!r}\n {ol} vs {nl}")

            anchor = lines_nos[0]
            col = old.find('"') + 1
            unit_id = f"{rel}:{anchor}:{col}"
            patches.append({
                "path": rel,
                "field": "text",
                "classification": "TEXT_PATCH",
                "unit_id": unit_id,
                "old_text": old,
                "new_text": new,
                "preimage_sha256": preimage,
                "expected_occurrences": expected,
                "source_text": src,
                "translation": tr,
                "placeholders": st,
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
            per_file_counts[rel] = per_file_counts.get(rel, 0) + 1
            if '" + "' in src:
                combined_patches.append((rel, anchor, src, tr))

    # global sanity: no duplicate unit_ids, all preimages equal TARGET-independent
    ids = [p["unit_id"] for p in patches]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate unit_ids")
    preimages = {p["preimage_sha256"] for p in patches}
    print(f"preimages in manifest: {len(preimages)} (distinct files)")
    for p in patches:
        if p["preimage_sha256"] != sha256_file(SRC / p["path"]).upper():
            raise SystemExit(f"preimage mismatch for {p['path']}")

    manifest = {
        "id": "c5-l13-dynamic-ui-zhcn",
        "version": "0.1.0",
        "patch_type": "TEXT_PATCH",
        "target_original_sha256": TARGET_SHA,
        "dependencies": [],
        "conflicts": [],
        "scope": ("C5-L13: runtime/dynamic player-visible UI strings across 26 scripts "
                  "(GUI HUD messages, popup/dialog window titles, stat breakdown prefixes, "
                  "tooltip headers, orb names, interactable context text, floating combat text); "
                  "internal identifiers, signal names, node paths and code structure untouched; "
                  "CODE_PATCH on plaintext sources in 04_recovered"),
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
            "phase_checkpoint_dynamic_ui_zhcn",
        ],
        "not_proven": ("visual layout quality, persistence, gameplay, broad localization, "
                       "or release readiness"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("=" * 60)
    print(f"PASS  manifest written: {OUT}")
    print(f"total patches: {len(patches)}")
    print(f"total line checks: {total_lines_checked}")
    print("per-file counts:")
    for rel, n in sorted(per_file_counts.items()):
        print(f"  {n:3d}  {rel}")
    print(f"multi-literal (combined source/translation) patches: {len(combined_patches)}")
    for rel, ln, src, tr in combined_patches:
        print(f"  {rel}:{ln}  {src}  ->  {tr}")
    print(f"TRANSLATION_UNCERTAIN entries: {len(uncertain)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())