extends Interactable

var dialog = preload("res://Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.tscn")
onready var notice = $Notice

func get_context_text() -> String:
				return "Stash Transfer"

func on_interact():
				var popup = dialog.instance()
				PopupManager.show_popup(popup, self)
