extends Node2D
class_name PathingController

var target
var offset
onready var pathing_target = global_position

var _is_target_visible = false
var _is_offset_visible = false


var _needs_check = true

func _ready():
				
				$RecomputePathTimer.wait_time = 2.0 + 2.0 * randf()

func _physics_process(delta: float):
				if _needs_check:
								var space_state = get_world_2d().direct_space_state
								var result = space_state.intersect_ray(global_position, target.global_position, [self], 256)
								var offset_result = space_state.intersect_ray(global_position, target.global_position + offset, [self], 256)
								if not result:
												_is_target_visible = true
								else:
												_is_target_visible = false

								if not offset_result:
												_is_offset_visible = true
								else:
												_is_offset_visible = false

								_needs_check = false

func _on_RecomputePathTimer_timeout() -> void :
				_needs_check = true

func is_target_visible():
				return _is_target_visible

func is_offset_visible():
				return _is_offset_visible

func recompute_pathing_target():
				var _pathing_target = Globals.navmesh.get_shortest_path_target(global_position, target.global_position)

				if _pathing_target != null:
								pathing_target = _pathing_target
				else:
								pathing_target = target.global_position
