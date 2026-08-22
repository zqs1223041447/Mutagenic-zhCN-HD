extends AcquiredSkill

var sanguine_effect = preload("res://scenes/Explosions/TexturedExplosions/FlameNovaExplosion.tscn")
var splash_applier = preload("res://scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.tscn")

func get_base_damage(apply_rand_keystones = true):
				return stats.gs("health_max") * 2.5

func get_tiers():
				return [{
								"skill": {
												"damage": 0, 
												"radius": 50, 
												"crit_chance": 0.0, 
												"crit_multi": 0.0, 
												"fire_ailment_chance": 1.0, 
												"fire_ailment_effect": 0.0, 
												"damage_effectiveness": 1.0, 
								}, 
				}]

func get_damage_tag():
				return SkillTags.Tags.FIRE

func cast():
				var radius = get_radius()

				var effect = sanguine_effect.instantiate()
				effect.radius = radius
				effect.global_position = global_position
				ground_effect_level.call_deferred("add_child", effect)

				var splash_applier_instance = splash_applier.instantiate()
				splash_applier_instance.global_position = global_position
				splash_applier_instance.target_group = stats.target_group
				splash_applier_instance.damage_bundle = get_damage_bundle()
				splash_applier_instance.radius = radius
				splash_applier_instance.skill_parent = self
				GameState.get_global("ground").call_deferred("add_child", splash_applier_instance)
