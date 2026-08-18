extends GenericSkill

var chain_lightning = preload("res://Scenes/Particles/ChainLightning.tscn")
var chain_lightning_effect = preload("res://Scenes/StatusEffects/Skills/ChainLightning.tscn")

var closest = null

func can_cast():
				var all_enemies = get_visible_enemies(true)
				var dist = INF
				closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy
				return closest != null

func cast(damage_multiplier = 1.0, consume_boons = false):
				if closest:
								var base_damage = get_damage_bundle()
								consume_boons()
								var target = closest
								var inst = chain_lightning.instance()
								inst.source_target = stats
								inst.dest_target = target.stats
								ground_effect_level.call_deferred("add_child", inst)

								
								var effect = chain_lightning_effect.instance()
								effect.skill_parent_weakref = weakref(self)
								effect.applier_stats_weakref = weakref(stats)
								effect.damage_bundle = base_damage
								effect.chains = get_chains()

								target.stats.apply_status_effect(effect)

								play_sound()
