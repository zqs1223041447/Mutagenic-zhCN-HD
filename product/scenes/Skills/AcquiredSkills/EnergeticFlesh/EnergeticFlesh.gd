extends AcquiredAura

var flesh_effect = preload("res://scenes/StatusEffects/Skills/EnergeticFlesh.tscn")



func get_radius(apply = true):
				return 100.0

func get_base_damage(apply_rand_keystones = true):
				return ceil(stats.gs("health_max") * 3.0 * stats.gs("lightning_ailment_effect"))

func get_tiers():
				return [{
								"skill": {
												"damage": 0, 
												"radius": 50, 
												"damage_effectiveness": 1.0, 
								}, 
				}]

func get_aura_effect():
				var effect = flesh_effect.instantiate()
				effect.applier_stats_weakref = weakref(stats)
				effect.skill_parent_weakref = weakref(self)
				effect.unique_group = unique_aura_id
				effect.damage_per_second = get_damage_bundle()
				return effect
