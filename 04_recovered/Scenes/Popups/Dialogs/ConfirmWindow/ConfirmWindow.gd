extends PopupBase

var confirm_dialog = preload("res://Scenes/Popups/Dialogs/TintedConfirmationDialog.tscn")

signal confirmed

var title

func _ready() -> void :
				var popup = confirm_dialog.instance()
				popup.window_title = title
				popup.connect("confirmed", self, "_on_confirm")
				popup.get_cancel().connect("pressed", self, "_on_cancel")
				add_child(popup)
				popup.popup_centered()

func _on_confirm():
				print("Confirmed")
				emit_signal("confirmed")

func _on_cancel():
				print("Cancelling")
				PopupManager.pop_popup()
