extends CanvasLayer

class_name PopupBase

signal destroy
signal create

@export var auto_pop = true

func _enter_tree() -> void :
				Globals.request_pause()
				emit_signal("create")

func _exit_tree() -> void :
				emit_signal("destroy")
				Globals.call_deferred("release_pause")

func _grab_focus():
				pass
