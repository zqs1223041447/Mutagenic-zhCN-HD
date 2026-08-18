extends Pickup

var death_screen = preload("res://Scenes/Popups/DeathScreen.tscn")
var confirm = preload("res://Scenes/Popups/Dialogs/ConfirmWindow/ConfirmWindow.tscn")

func on_pickup():
				var popup = confirm.instance()
				popup.title = "Return to Hideout?"
				popup.connect("confirmed", self, "_on_confirm")
				PopupManager.show_popup(popup, self)

func _on_confirm():
				var instance = death_screen.instance()
				PopupManager.show_popup(instance, get_tree().get_root().get_node("World"))
