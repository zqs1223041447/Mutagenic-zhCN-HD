extends Interactable

var dialog = preload("res://Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.tscn")

func get_context_text() -> String:
				return "Cosmetic Outfits"

func on_interact():
				var popup = dialog.instance()
				PopupManager.show_popup(popup, self)
