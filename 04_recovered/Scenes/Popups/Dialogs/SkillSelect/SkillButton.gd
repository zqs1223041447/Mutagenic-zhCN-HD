extends VBoxContainer

var equip_sound = preload("res://Sounds/Misc/equip.wav")
var skill_list = preload("res://Scenes/Popups/Dialogs/SkillSelect/SkillList.tscn")

export var slot = "primary"

func _ready() -> void :
				GameState.connect("skills_changed", self, "update_skill")
				GameState.connect("skill_loadout_changed", self, "update_skill")
				update_skill()

func select():
				$SkillButton / SkillButton.grab_focus()

func update_skill():
				var eq = GameState.get_equipped_skills()
				if eq.has(slot):
								var equipped_skill = eq[slot].skill
								if equipped_skill != null:
												render_skill(equipped_skill)
								else:
												$SkillButton / SkillButton / MarginContainer / TextureRect.texture = null
												render_skill(equipped_skill)
				else:
								print("Equipment doesn't have slot:", eq, slot)

func render_skill(skill):
				if SlotRequirements.get_required_level_for_skill(slot) > GameState.get_account_level():
								$SkillButton / SkillButton.disabled = true
								$SkillButton / VBoxContainer / NameLabel.text = "Unlocks at level " + str(SlotRequirements.get_required_level_for_skill(slot))
								$SkillButton / VBoxContainer / NameLabel.set("custom_colors/font_color", Colors.nerfed)
				else:
								$SkillButton / SkillButton.disabled = false
								$SkillButton / VBoxContainer / NameLabel.set("custom_colors/font_color", Color.white)
								if skill == null:
												$SkillButton / SkillButton / MarginContainer / TextureRect.texture = null
												$SkillButton / VBoxContainer / NameLabel.visible = false
								else:
												var info = Skills.config[skill]
												$SkillButton / SkillButton / MarginContainer / TextureRect.texture = info.skill_texture
												$SkillButton / VBoxContainer / NameLabel.visible = true
												$SkillButton / VBoxContainer / NameLabel.text = info.name

func _on_SkillButton_pressed() -> void :
				var popup = skill_list.instance()
				popup.connect("equip_skill", self, "_equip_skill")
				PopupManager.show_popup(popup, self)

func _equip_skill(skill_name):
				GameState.equip_skill(skill_name, slot)
				Globals.play_sound_effect(equip_sound)
