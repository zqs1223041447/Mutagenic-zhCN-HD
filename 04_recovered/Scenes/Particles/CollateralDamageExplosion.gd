extends Particles2D





var radius = 1.0


func _ready() -> void :
				if GameState.is_fx_enabled():
								process_material.set("emission_sphere_radius", radius)
								amount = 0.1 * PI * radius
								emitting = true
				else:
								emitting = false

func _on_Timer_timeout() -> void :
				queue_free()
