extends Interactable

var dialog = preload("res://scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.tscn")
@onready var notice = $Notice

func get_context_text() -> String:
				return "Change Character Class"

func on_interact():
				var popup = dialog.instantiate()
				PopupManager.show_popup(popup, self)
