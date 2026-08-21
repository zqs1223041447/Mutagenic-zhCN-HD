extends GPUParticles2D

var radius

var sound = preload("res://Sounds/SFX/blood_explosion.wav")

func _ready() -> void :
				if GameState.is_fx_enabled():
								emitting = true
				else:
								emitting = false
				process_material.set("initial_velocity", radius / 0.2)

				Globals.play_sound_effect(sound)

func _on_Timer_timeout() -> void :
				queue_free()
