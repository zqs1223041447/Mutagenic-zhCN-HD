extends GenericSkill

var slash_effect = preload("res://Scenes/ShaderExplosions/SlashEffect/SlashEffect.tscn")
var splash_applier = preload("res://Scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.tscn")

const SLASH_WIDTH = PI / 2.0

var attack_count = 0

var closest = null
var dist = INF

func can_cast():
				var all_enemies = get_visible_enemies(true)
				dist = INF
				closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy
				var radius = get_radius()
				return closest != null and dist <= radius

func cast():
				var radius = get_radius()
				if closest != null and dist <= radius:
								attack_count += 1
								var damage_bundle = get_damage_bundle()

								if attack_count == 3:
												attack_count = 0
												damage_bundle.crit.chance = 1.0
								var base_angle = global_position.direction_to(closest.global_position)
								
								consume_boons()

								var tint_color = Color.white
								var max_dmg = 0.0
								for tag in damage_bundle.damage:
												if damage_bundle.damage[tag] > max_dmg:
																max_dmg = damage_bundle.damage[tag]
																tint_color = Colors.color_for_skill_tag[tag]

								
								var slash = slash_effect.instance()
								slash.radius = radius
								slash.global_position = global_position
								slash.apply_in_arc = true
								slash.arc_angle = PI + global_position.angle_to_point(closest.global_position)
								slash.arc_width = SLASH_WIDTH
								slash.tint = tint_color
								ground_effect_level.add_child(slash)

								var splash_applier_instance = splash_applier.instance()
								splash_applier_instance.global_position = global_position
								splash_applier_instance.target_group = stats.target_group
								splash_applier_instance.damage_bundle = damage_bundle
								splash_applier_instance.radius = radius
								splash_applier_instance.skill_parent = self
								splash_applier_instance.only_apply_in_arc = true
								splash_applier_instance.arc_direction_vector = global_position.direction_to(closest.global_position)
								splash_applier_instance.arc_width = SLASH_WIDTH
								ground_effect_level.call_deferred("add_child", splash_applier_instance)

								play_sound()

func get_damage_bundle(apply = true, use_cache = true, apply_as = null):
				if apply:
								var options = [SkillTags.Tags.LIGHTNING, SkillTags.Tags.COLD, SkillTags.Tags.FIRE]
								var chosen = options[randi() % len(options)]
								var dmg = .get_damage_bundle(apply, false, chosen).duplicate(true)
								return dmg
				else:
								return .get_damage_bundle(apply, false)
