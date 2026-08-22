extends GenericAura

var flame_effect = preload("res://scenes/StatusEffects/Skills/FlameTether.tscn")

func get_aura_effect():
				var effect = flame_effect.instantiate()
				effect.applier_stats_weakref = weakref(stats)
				effect.skill_parent_weakref = weakref(self)
				effect.unique_group = unique_aura_id
				effect.damage_per_second = get_damage_bundle()
				return effect
