extends PopupBase

var slot = preload("res://Scenes/Popups/Dialogs/CharacterSelect/CharacterSlot.tscn")

var class_select = preload("res://Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn")

onready var character_list = $MarginContainer / CenterContainer / PanelContainer / VBoxContainer2 / CharacterList

func _ready() -> void :
				GameState.connect("characters_changed", self, "render")
				render()

func render():
				for child in character_list.get_children():
								child.queue_free()
				var characters = GameState.saved_stats.characters.keys()
				characters.sort()
				var first = null
				for c in characters:
								var c_slot = slot.instance()
								c_slot.character_name = c
								character_list.add_child(c_slot)

								if not first:
												first = c_slot
				if first:
								first.focus()

func _on_Button2_pressed() -> void :
				PopupManager.pop_popup()

func _on_CharacterCreateButton_pressed() -> void :
				var popup = class_select.instance()
				popup.connect("character_created", self, "_create_character")
				popup.connect("destroy", self, "_refocus_new")
				PopupManager.show_popup(popup, self)

func _refocus_new():
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer2 / HBoxContainer / CharacterCreateButton.grab_focus()

func _create_character(character_name, character_class):
				GameState.create_new_character(character_name, character_class)
