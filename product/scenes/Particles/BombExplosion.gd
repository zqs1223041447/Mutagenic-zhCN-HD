extends GPUParticles2D

var sound = preload("res://Sounds/Skills/Explosions/shrapnel_explosion.wav")

var radius
var particle_multiplier = 1.0

func _ready() -> void :
				if GameState.is_fx_enabled():
								emitting = true
				else:
								emitting = false

				var d_scale = radius / 64.0

				process_material.scale = d_scale

				Globals.play_sound_effect(sound)

func _on_Timer_timeout() -> void :
				queue_free()
