extends Particles2D
class_name FlipbookExplosion

export var override_scale = 0.0
export var modulation = Color.white
var radius

func _ready() -> void :
				emitting = true
				if radius:
								process_material.scale = radius / 64.0
				if override_scale != 0:
								process_material.scale = override_scale

				modulate = modulation

func _on_Timer_timeout() -> void :
				queue_free()
