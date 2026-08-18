extends PopupBase

signal character_created(character_name, character_class)

onready var class_list = $MarginContainer / CenterContainer / PanelContainer / VBoxContainer2 / ClassList


func _ready() -> void :
				for child in class_list.get_children():
								child.connect("chosen", self, "_on_class_chosen")

func _on_class_chosen(character_name, character_class):
				emit_signal("character_created", character_name, character_class)
				PopupManager.pop_popup()

func _on_CancelButton_pressed() -> void :
				PopupManager.pop_popup()
