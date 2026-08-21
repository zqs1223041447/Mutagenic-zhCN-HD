extends HBoxContainer

signal changed

@export var label_text = ""
@export var action_name = ""

var is_setting = false

func _ready() -> void :
				$Label.text = label_text
				if InputMap.has_action(action_name):
								print("Action found:", action_name)
				else:
								print("Invalid action name:", action_name)
								get_tree().quit()

				GameState.connect("keybinds_changed", Callable(self, "_update"))
				_update()

func _update():
				$Button.text = GameState.get_keybind(action_name)

func _on_Button_pressed() -> void :
				is_setting = true

func _unhandled_key_input(event: InputEventKey) -> void :
				if not is_setting:
								return
				if event is InputEventKey:
								is_setting = false
								if event.is_action("ui_cancel"):
												return
								GameState.set_keybind(action_name, event)
								emit_signal("changed")
