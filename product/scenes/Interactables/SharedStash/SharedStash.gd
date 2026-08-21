extends Interactable

var dialog = preload("res://scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn")
@onready var notice = $Notice

func get_context_text() -> String:
				return "Stash Transfer"

func on_interact():
				var popup = dialog.instantiate()
				PopupManager.show_popup(popup, self)
