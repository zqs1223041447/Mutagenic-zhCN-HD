extends Interactable

var cb = preload("res://scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.tscn")

func get_context_text() -> String:
				return "Items and Item Modding"

func on_interact():
				var popup = cb.instantiate()
				PopupManager.show_popup(popup, self)
