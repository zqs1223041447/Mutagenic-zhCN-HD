extends PopupBase

@onready var class_list = $MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/ClassList


func _ready() -> void :
				for child in class_list.get_children():
								child.connect("chosen", Callable(self, "_on_class_chosen"))

func _on_class_chosen(_name, character_class):
				print("TODO: Change class to ", character_class)
				GameState.change_class(character_class)
				PopupManager.pop_popup()

func _on_CancelButton_pressed() -> void :
				PopupManager.pop_popup()
