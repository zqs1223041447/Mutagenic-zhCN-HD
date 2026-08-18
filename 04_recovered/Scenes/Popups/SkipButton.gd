extends Button

signal focused







func _ready() -> void :
				pass


func _on_SkipButton_mouse_entered() -> void :
				grab_focus()


func _on_SkipButton_focus_entered() -> void :
				emit_signal("focused")
