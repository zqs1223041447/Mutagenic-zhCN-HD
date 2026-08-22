extends Node2D

var source_target = null
var dest_target = null
var elapsed = 0.0
var invalid = false
var timer_length = 1.0
@onready var tex = $TextureRect


func _ready() -> void :
				timer_length = $Timer.wait_time
				_update_position()
				if invalid:
								visible = false


func _process(delta: float) -> void :
				_update_position()
				elapsed += delta
				tex.material.set_shader_param("elapsed", - 1.0 + 2.0 * (elapsed / timer_length))

func _update_position():
				if invalid:
								return
				if not is_instance_valid(dest_target):
								invalid = true
								return
				if not is_instance_valid(source_target):
								invalid = true
								return

				var source_position = source_target.global_position
				var dest_position = dest_target.global_position
				global_position = dest_position

				var tex_size = tex.rect_size

				var chain_distance = source_position.distance_to(dest_position)
				var chain_scale = chain_distance / tex_size.y

				tex.rect_scale = Vector2(1.0, chain_scale)
				tex.rect_pivot_offset = Vector2(tex_size.x / 2.0, 0.0)
				tex.rect_rotation = 90 + 180.0 * dest_position.angle_to_point(source_position) / PI

func _on_Timer_timeout() -> void :
				queue_free()
