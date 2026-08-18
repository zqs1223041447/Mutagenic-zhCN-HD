extends HBoxContainer

signal loaded

var tree_name
var delete_enabled = true


func _ready() -> void :
				$Label.text = tree_name
				if delete_enabled:
								$DeleteButton.visible = true

func _on_LoadButton_pressed() -> void :
				GameState.load_tree(tree_name)
				emit_signal("loaded")

func _on_DeleteButton_pressed() -> void :
				GameState.delete_tree(tree_name)
				emit_signal("loaded")
