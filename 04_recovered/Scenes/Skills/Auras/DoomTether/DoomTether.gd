extends GenericAura

var doom_effect = preload("res://Scenes/StatusEffects/Skills/DoomTether.tscn")

func get_aura_effect():
				var effect = doom_effect.instance()
				effect.applier_stats_weakref = weakref(stats)
				effect.skill_parent_weakref = weakref(self)
				effect.unique_group = unique_aura_id
				return effect
