extends Interactable

var dialog = preload("res://scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn")

func get_context_text() -> String:
				return "Cosmetic Outfits"

func on_interact():
				var popup = dialog.instantiate()
				PopupManager.show_popup(popup, self)
