extends GPUParticles2D
class_name FlipbookExplosion

@export var override_scale = 0.0
@export var modulation = Color.WHITE
var radius

func _ready() -> void :
				emitting = true
				if radius:
								# P4-WIRE: G3 float `scale` split into scale_min/scale_max in
								# Godot 4; setting both keeps the old deterministic size.
								process_material.scale_min = radius / 64.0
								process_material.scale_max = radius / 64.0
				if override_scale != 0:
								process_material.scale_min = override_scale
								process_material.scale_max = override_scale

				modulate = modulation

func _on_Timer_timeout() -> void :
				queue_free()
