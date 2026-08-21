extends GPUParticles2D

var radius = 0

func _ready() -> void :
				process_material.emission_sphere_radius = radius
				amount = radius * radius * 0.1
				emitting = true

func _on_Timer_timeout() -> void :
				queue_free()
