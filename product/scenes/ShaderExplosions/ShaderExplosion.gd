extends Node2D
class_name ShaderExplosion

var radius = 0
var duration_expired = 0.0
var duration_target = 0.0
var percent_done = 0.0
var arc_width = 0.0
var arc_angle = 0.0
var apply_in_arc = false
var tint = null

func _ready() -> void :
				$ColorRect.size = 2.0 * Vector2(radius, radius)
				$ColorRect.position = - $ColorRect.size / 2.0
				duration_target = $Timer.wait_time

				if apply_in_arc:
								$ColorRect.material.set("shader_param/arc_angle", arc_width)
								$ColorRect.material.set("shader_param/only_arc", true)
								rotation = arc_angle

				if tint:
								modulate = tint

func _process(delta: float) -> void :
				if duration_target <= 0:
								return
				duration_expired += delta
				percent_done = duration_expired / duration_target
				$ColorRect.material.set_shader_param("pct_done", percent_done)
				if duration_expired > 1.0:
								duration_expired -= 1.0

func _on_Timer_timeout() -> void :
				queue_free()
