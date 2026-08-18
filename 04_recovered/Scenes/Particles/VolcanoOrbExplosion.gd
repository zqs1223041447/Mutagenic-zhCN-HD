extends Particles2D

var radius
var particle_multiplier = 1.0

func _ready() -> void :
				if GameState.is_fx_enabled():
								emitting = true
				else:
								emitting = false
				process_material.emission_sphere_radius = radius
				amount *= sqrt(particle_multiplier)

func _on_Timer_timeout() -> void :
				queue_free()

