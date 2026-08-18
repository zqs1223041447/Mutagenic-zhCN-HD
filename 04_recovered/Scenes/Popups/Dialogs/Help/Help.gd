extends PopupBase

onready var tabs = $CenterContainer / PanelContainer / VBoxContainer / TabContainer


func _ready() -> void :
				$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / BackButton.grab_focus()

func _physics_process(delta: float) -> void :
				if Input.is_action_pressed("move_down"):
								tabs.get_current_tab_control().scroll_vertical += 15
				if Input.is_action_pressed("move_up"):
								tabs.get_current_tab_control().scroll_vertical -= 15

func _input(event: InputEvent) -> void :
				if event.is_action_pressed("ui_focus_next"):
								get_tree().set_input_as_handled()
								tabs.current_tab = (tabs.current_tab + 1) % tabs.get_child_count()
				if event.is_action_pressed("ui_focus_prev"):
								get_tree().set_input_as_handled()
								tabs.current_tab = (tabs.current_tab - 1 + tabs.get_child_count()) % tabs.get_child_count()

func _on_Button_pressed() -> void :
				PopupManager.pop_popup()

func _on_LineEdit_text_changed(new_text: String) -> void :
				Globals.update_search(new_text)
