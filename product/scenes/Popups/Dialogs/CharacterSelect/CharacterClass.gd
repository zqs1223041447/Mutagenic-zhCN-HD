extends VBoxContainer

var text_input = preload("res://scenes/Popups/Dialogs/TextInputDialog.tscn")

signal chosen(character_name, character_class)

@export var class_id = ""
@export var only_choose_class = false


func _ready() -> void :
				var description = PlayableClasses.class_descriptions[class_id]
				var cn = PlayableClasses.class_names[class_id]

				$ClassNameLabel.text = cn
				$ClassDescriptionLabel.text = description
				$Button.text = "Choose " + cn
				$TextureRect.texture = PlayableClasses.class_icons[class_id]

func _on_Button_pressed() -> void :
				if only_choose_class:
								emit_signal("chosen", null, class_id)
				else:
								var popup = text_input.instantiate()
								popup.title = "Character Name"
								popup.connect("text_entered", Callable(self, "_on_text_input"))
								PopupManager.show_popup(popup, self)

func _grab_focus():
				$Button.grab_focus()

func _on_text_input(character_name):
				emit_signal("chosen", character_name, class_id)
