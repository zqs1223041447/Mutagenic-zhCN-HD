extends Area2D

var radius = 0.0
var target_group = "enemies"
var damage_bundle = null
var skill_parent = null
var skill_parent_weakref = null
var ignore_instance = null
var can_be_blocked = true


var only_apply_in_arc = false


var arc_direction_vector = Vector2.ZERO


var arc_width = 0.0


func _ready() -> void :
				skill_parent_weakref = weakref(skill_parent)
				$CollisionShape2D.shape.radius = radius

func _on_Timer_timeout() -> void :
				queue_free()

func _on_AreaInstanceDamageApplier_area_entered(area: Area2D) -> void :
				var p = area.get_parent()
				if p == ignore_instance:
								return
				if p.is_in_group(target_group):
								var stats = null
								var sp = skill_parent_weakref.get_ref()
								if sp:
												stats = sp.stats
								if only_apply_in_arc:
												
												var direction_to_target = global_position.direction_to(p.global_position)

												
												
												var angle_between = arc_direction_vector.angle_to(direction_to_target)
												if abs(angle_between) <= arc_width / 2.0:
																var info = p.stats.apply_damage(damage_bundle, Color.white, stats, false, false, sp, can_be_blocked)
																if sp:
																				sp.track_hit(info)
								else:
												var info = p.stats.apply_damage(damage_bundle, Color.white, stats, false, false, sp, can_be_blocked)
												if sp:
																sp.track_hit(info)
