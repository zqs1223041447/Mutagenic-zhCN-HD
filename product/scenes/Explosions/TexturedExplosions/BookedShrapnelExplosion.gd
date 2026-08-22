extends FlipbookExplosion

@onready var bomb_sound = preload("res://Sounds/Skills/Shots/bomb.wav")

func _ready() -> void :
				emitting = true
				if radius:
								# P4-WIRE: G3 float scale -> scale_min/scale_max (Godot 4)
								process_material.scale_min = radius / 64.0
								process_material.scale_max = radius / 64.0
				if override_scale != 0:
								process_material.scale_min = override_scale
								process_material.scale_max = override_scale

				modulate = modulation

				Globals.play_sound_effect(bomb_sound)


func _on_Timer_timeout() -> void :
				queue_free()
