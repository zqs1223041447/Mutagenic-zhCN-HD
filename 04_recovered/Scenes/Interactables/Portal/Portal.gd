extends Interactable

var map_select = preload("res://Scenes/Popups/Dialogs/WorldMap/WorldMapPopup.tscn")
var warning = preload("res://Scenes/Popups/Dialogs/HelpTip/NoWeaponWarning/NoWeaponWarning.tscn")

func get_context_text() -> String:
				return "Departure Portal"

func on_interact():
				if GameState.is_slot_equipped("primary"):
								show_map()
				else:
								var popup = warning.instance()
								PopupManager.show_popup(popup, self)

func show_map():
				var popup = map_select.instance()
				PopupManager.show_popup(popup, self)
