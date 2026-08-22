extends VBoxContainer

var equip_sound = preload("res://Sounds/Misc/equip.wav")
var support_list = preload("res://scenes/Popups/Dialogs/SkillSelect/SupportList.tscn")

@export var slot = "primary"
@export var support_slot = "a"

func _ready() -> void :
				GameState.connect("skills_changed", Callable(self, "update_support"))
				GameState.connect("skill_loadout_changed", Callable(self, "update_support"))
				update_support()

func select():
				$HBoxContainer/SupportButton.grab_focus()

func update_support():
				var equipped_skills = GameState.get_equipped_skills()
				var equipped_support = equipped_skills[slot].supports[support_slot]
				if equipped_support != null:
								render_support(equipped_support)
				else:
								$HBoxContainer/SupportButton/MarginContainer/TextureRect.texture = null
								render_support(equipped_support)

func render_support(equipped_support):
				if SlotRequirements.get_required_level_for_support(slot, support_slot) > GameState.get_account_level():
								$HBoxContainer/SupportButton.disabled = true
								$VBoxContainer/NameLabel.text = "Req Level: " + str(SlotRequirements.get_required_level_for_support(slot, support_slot))
								$VBoxContainer/NameLabel.visible = true
								$VBoxContainer/NameLabel.set("theme_override_colors/font_color", Colors.nerfed)
				else:
								$HBoxContainer/SupportButton.disabled = false
								$VBoxContainer/NameLabel.visible = false
								$VBoxContainer/NameLabel.set("theme_override_colors/font_color", Color.WHITE)
								if equipped_support == null:
												$HBoxContainer/SupportButton/MarginContainer/TextureRect.texture = null
												$VBoxContainer/NameLabel.visible = false
								else:
												var info = SkillSupports.supports[equipped_support]
												$HBoxContainer/SupportButton/MarginContainer/TextureRect.texture = info.icon
												$VBoxContainer/NameLabel.visible = true
												$VBoxContainer/NameLabel.text = info.name


func _equip_support(support_name):
				GameState.equip_support(slot, support_slot, support_name)
				Globals.play_sound_effect(equip_sound)


func _on_SupportButton_pressed() -> void :
				var popup = support_list.instantiate()
				popup.skill_slot = slot
				popup.connect("equip_support", Callable(self, "_equip_support"))
				PopupManager.show_popup(popup, self)
