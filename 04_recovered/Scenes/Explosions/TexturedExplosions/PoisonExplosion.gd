extends FlipbookExplosion

onready var nova_sound = preload("res://Sounds/Mobskills/nova.wav")

func _ready() -> void :
				emitting = true
				if radius:
								process_material.scale = radius / 64.0
				if override_scale != 0:
								process_material.scale = override_scale

				modulate = modulation

				Globals.play_sound_effect(nova_sound)

func _on_Timer_timeout() -> void :
				queue_free()
