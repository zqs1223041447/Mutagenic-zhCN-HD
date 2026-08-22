extends Interactable

var passive_tree = preload("res://scenes/Popups/Dialogs/PassiveTree/PassiveTreePopup.tscn")

func get_context_text() -> String:
				return "Passive Upgrades"

func on_interact():
				var popup = passive_tree.instantiate()
				PopupManager.show_popup(popup, self)
