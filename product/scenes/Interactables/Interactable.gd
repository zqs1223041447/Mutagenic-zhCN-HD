extends Node2D
class_name Interactable

var mouse_hover = false

func _ready() -> void :
				$Area2D.connect("mouse_entered", Callable(self, "_on_mouse_entered"))
				$Area2D.connect("mouse_exited", Callable(self, "_on_mouse_exited"))

				$Node2D/VBoxContainer/HBoxContainer/Label.text = get_context_text()

func get_context_text() -> String:
				return ""

func _on_mouse_entered() -> void :
				if Globals.is_using_controller():
								return
				mouse_hover = true
				set_context()

func _on_mouse_exited() -> void :
				mouse_hover = false
				remove_context()

func _physics_process(delta: float) -> void :
				if Input.is_action_just_pressed("click"):
								if mouse_hover:
												on_interact()
				elif Input.is_action_just_pressed("interact"):
								if Globals.current_context_instance == self:
												on_interact()

func on_interact():
				pass

func _on_Area2D_area_entered(area: Area2D) -> void :
				if area.get_parent().is_in_group("player"):
								print("PLAYER FOUND")
								set_context()

func set_context():
				Globals.set_context(self, get_context_text())

func remove_context():
				Globals.remove_context(self)


func _on_Area2D_area_exited(area: Area2D) -> void :
				if area.get_parent().is_in_group("player"):
								print("PLAYER FOUND")
								if not mouse_hover:
												remove_context()
