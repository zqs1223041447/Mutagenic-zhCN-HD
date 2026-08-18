extends Node2D
class_name AreaSkillEffect

signal expired

onready var shader_material = $InnerCircle.material

var lifetime = 10.0
var time_elapsed = 0.0
var radius = 15.0
export var started = false

func _ready() -> void :
				_update_radius()

func _update_radius():
				
				var r = radius
				$OuterCircle.rect_size = Vector2(r * 2.0, r * 2.0)
				$OuterCircle.rect_position = Vector2( - r, - r)
				$InnerCircle.rect_size = Vector2(r * 2.0, r * 2.0)
				$InnerCircle.rect_position = Vector2( - r, - r)

func start():
				started = true
				$OuterCircle.visible = true
				$InnerCircle.visible = true

func _physics_process(delta: float) -> void :
				if started:
								time_elapsed += delta

								var percent_done = time_elapsed / lifetime

								shader_material.set_shader_param("percent_done", percent_done)

								if time_elapsed >= lifetime:
												call_deferred("emit_signal", "expired")

func expired():
				pass
