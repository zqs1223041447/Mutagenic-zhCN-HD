extends VBoxContainer

var skill_info = preload("res://Scenes/Popups/Dialogs/StarterPicker/StarterSkillInfo.tscn")

onready var button = $ChooseButton
var template_id

func _ready() -> void :
				var info = StarterBuilds.templates[template_id]
				button.text = "Choose " + info.name
				for slot in info.loadout:
								var skill = info.loadout[slot].skill
								if skill:
												var skill_child = skill_info.instance()
												skill_child.item_name = skill
												$SkillList.add_child(skill_child)

func _on_ChooseButton_pressed() -> void :
				GameState.set_starter_build(template_id)
				PopupManager.pop_popup()
