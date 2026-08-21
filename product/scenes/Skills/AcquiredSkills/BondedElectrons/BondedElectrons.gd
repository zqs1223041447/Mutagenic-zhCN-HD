extends AcquiredAura

var bonded_electron_effect = preload("res://scenes/StatusEffects/Skills/BondedElectrons.tscn")

func get_tiers():
				return [{
								"skill": {
												"radius": 50, 
								}, 
				}]

func get_radius(apply = true):
				return 100.0

func get_aura_effect():
				var effect = bonded_electron_effect.instantiate()
				effect.applier_stats_weakref = weakref(stats)
				effect.skill_parent_weakref = weakref(self)
				effect.unique_group = unique_aura_id
				return effect
