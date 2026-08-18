extends BaseEffect

var chain_lightning = load("res://Scenes/StatusEffects/Skills/ChainLightning.tscn")
var chain_lightning_effect = preload("res://Scenes/Particles/ChainLightning.tscn")

var damage_bundle = {}
var chains = 0
onready var ground_effect_level = GameState.get_global("ground")
onready var target_stats = get_parent().get_parent()

func get_status_flags():
				return []

func _exit_tree() -> void :
				remove_effect()

func on_expire():
				var attacker_stats = applier_stats_weakref.get_ref()
				var info = target_stats.apply_damage(damage_bundle, Color.blueviolet, attacker_stats, false, false, skill_parent_weakref.get_ref())

				var sp = skill_parent_weakref.get_ref()
				if sp:
								sp.track_hit(info)

				if chains > 0:
								var potential_targets = get_visible_allies(80)
								var dist = INF
								var closest = null
								for enemy in potential_targets:
												var dist_to_enemy = enemy.global_position.distance_to(target_stats.global_position)
												if dist_to_enemy < dist and enemy.stats != target_stats:
																dist = dist_to_enemy
																closest = enemy

								if closest:
												var target = closest
												
												var effect = chain_lightning.instance()
												effect.skill_parent_weakref = skill_parent_weakref
												effect.applier_stats_weakref = applier_stats_weakref
												effect.damage_bundle = damage_bundle
												effect.chains = chains - 1

												target.stats.apply_status_effect(effect)

												
												var inst = chain_lightning_effect.instance()
												inst.source_target = target_stats
												inst.dest_target = target.stats
												ground_effect_level.call_deferred("add_child", inst)

												
												if chains > 0:
																var chained_to = 0
																for enemy in potential_targets:
																				if enemy == target:
																								continue
																				effect = chain_lightning.instance()
																				effect.skill_parent_weakref = skill_parent_weakref
																				effect.applier_stats_weakref = applier_stats_weakref
																				effect.damage_bundle = damage_bundle
																				effect.chains = 0

																				enemy.stats.apply_status_effect(effect)

																				
																				inst = chain_lightning_effect.instance()
																				inst.source_target = target_stats
																				inst.dest_target = enemy.stats
																				ground_effect_level.call_deferred("add_child", inst)

																				chained_to += 1
																				if chained_to >= chains:
																								break


