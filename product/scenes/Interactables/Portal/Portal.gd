extends Interactable

var map_select = preload("res://scenes/Popups/Dialogs/WorldMap/WorldMapPopup.tscn")
var warning = preload("res://scenes/Popups/Dialogs/HelpTip/NoWeaponWarning/NoWeaponWarning.tscn")

func get_context_text() -> String:
				return "Departure Portal"

func on_interact():
				if GameState.is_slot_equipped("primary"):
								show_map()
				else:
								var popup = warning.instantiate()
								PopupManager.show_popup(popup, self)

func show_map():
				var popup = map_select.instantiate()
				PopupManager.show_popup(popup, self)
