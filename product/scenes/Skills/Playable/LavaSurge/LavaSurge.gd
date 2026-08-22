extends GenericSkill

@onready var surge = $LavaSurge

var ROTATION_SPEED = 2.0 * PI
var current_target
var needs_angle_reset = false

func _ready() -> void :
				call_deferred("setup")

func setup():
				surge.damage_bundle = get_damage_bundle()
				surge.beam_width = get_radius()
				surge.skill_parent_weakref = weakref(self)
				surge.update_beam()

func _handle_stat_change():
				surge.damage_bundle = get_damage_bundle()
				surge.beam_width = get_radius()
				surge.update_beam()

func _physics_process(delta: float) -> void :
				if current_target != null:
								var t = current_target.get_ref()
								if t:
												var angle_dest = global_position.angle_to_point(t.global_position) + PI / 2.0
												if needs_angle_reset:
																surge.rotation = angle_dest
																needs_angle_reset = false
												else:
																surge.rotation = lerp_angle(surge.rotation, angle_dest, 0.1)

func _on_Timer_timeout() -> void :
				
				var all_enemies = get_visible_enemies(true)
				var dist = INF
				var closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist and dist_to_enemy <= 100:
												dist = dist_to_enemy
												closest = enemy

				if closest:
								if stats.keystones.has("UNIQUE_BOMB_SPECIALIST"):
												
												if cached_tags.has(SkillTags.Tags.DAMAGING) and not cached_tags.has(SkillTags.Tags.BOMB):
																return
								current_target = weakref(closest)
								var angle_dest = global_position.angle_to_point(closest.global_position) + PI / 2.0
								if needs_angle_reset:
												surge.rotation = angle_dest
												needs_angle_reset = false
								surge.enable()
				else:
								current_target = null
								needs_angle_reset = true
								surge.disable()
