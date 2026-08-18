

extends HBoxContainer

signal loaded

var loadout_name
var delete_enabled = true


func _ready() -> void :
				$Label.text = loadout_name
				if delete_enabled:
								$DeleteButton.visible = true

func _on_LoadButton_pressed() -> void :
				GameState.load_skill_loadout(loadout_name)
				emit_signal("loaded")

func _on_DeleteButton_pressed() -> void :
				GameState.delete_skill_loadout(loadout_name)
				emit_signal("loaded")
