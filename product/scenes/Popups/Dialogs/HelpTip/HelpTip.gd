extends PopupBase

class_name HelpTip

func _ready() -> void :
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer/HBoxContainer2/Button.grab_focus()

func _on_Button_pressed() -> void :
				PopupManager.pop_popup()
