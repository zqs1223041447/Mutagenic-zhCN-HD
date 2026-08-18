extends Interactable

var passive_tree = preload("res://Scenes/Popups/Dialogs/PassiveTree/PassiveTreePopup.tscn")

func get_context_text() -> String:
				return "Passive Upgrades"

func on_interact():
				var popup = passive_tree.instance()
				PopupManager.show_popup(popup, self)
