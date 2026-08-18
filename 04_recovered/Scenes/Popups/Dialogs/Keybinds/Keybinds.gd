extends PopupBase

func _ready() -> void :
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer2 / VBoxContainer / DoneButton.grab_focus()
				for child in $MarginContainer / CenterContainer / PanelContainer / VBoxContainer2 / VBoxContainer / KeybindList.get_children():
								child.connect("changed", self, "_reset_focus")

				_reset_focus()

func _on_DoneButton_pressed() -> void :
				PopupManager.pop_popup()

func _reset_focus():
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer2 / VBoxContainer / DoneButton.grab_focus()
