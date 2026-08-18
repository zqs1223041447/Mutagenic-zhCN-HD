extends Interactable

var cb = preload("res://Scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.tscn")

func get_context_text() -> String:
				return "Items and Item Modding"

func on_interact():
				var popup = cb.instance()
				PopupManager.show_popup(popup, self)
