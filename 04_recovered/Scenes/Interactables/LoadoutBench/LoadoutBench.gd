extends Interactable

var loadout_selector = preload("res://Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.tscn")

func get_context_text() -> String:
				return "Equipment"

func on_interact():
				var popup = loadout_selector.instance()
				PopupManager.show_popup(popup, self)
