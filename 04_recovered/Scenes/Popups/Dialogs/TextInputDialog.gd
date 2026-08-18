extends PopupBase

signal text_entered(text)

var title = ""
var label = ""
var prefill

func _ready() -> void :
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / HBoxContainer / InputLabel.text = label
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / TitleLabel.text = title
				if prefill:
								$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / HBoxContainer / LineEdit.text = prefill

				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / HBoxContainer / LineEdit.grab_focus()

func _process(_delta) -> void :
				if Input.is_action_just_pressed("ui_enter"):
								submit()

func _on_AcceptButton_pressed() -> void :
				submit()

func _on_CloseButton_pressed() -> void :
				PopupManager.pop_popup()

func submit():
				var text = $MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / HBoxContainer / LineEdit.text
				emit_signal("text_entered", text)
				PopupManager.pop_popup()
