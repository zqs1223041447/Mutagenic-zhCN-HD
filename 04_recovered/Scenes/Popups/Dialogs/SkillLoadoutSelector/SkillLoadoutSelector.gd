extends PopupBase

var option = preload("res://Scenes/Popups/Dialogs/SkillLoadoutSelector/LoadOption.tscn")
onready var loadoptions = $MarginContainer / CenterContainer / PanelContainer / VBoxContainer / LoadOptions

export var delete_enabled = true

func _ready() -> void :
				if not GameState.has_saved_skill_loadouts():
								$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / NoneLabel.visible = true
				else:
								for loadout_name in GameState.get_saved_skill_loadouts():
												var o = option.instance()
												o.loadout_name = loadout_name
												o.delete_enabled = delete_enabled
												o.connect("loaded", self, "queue_free")
												loadoptions.add_child(o)

				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer3 / CloseButton.grab_focus()

func _on_CloseButton_pressed() -> void :
				PopupManager.pop_popup()
