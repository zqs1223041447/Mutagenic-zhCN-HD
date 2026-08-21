extends BaseEffect

var poison_chain_effect = preload("res://scenes/Particles/InfectionChain.tscn")

var hit_damage
var poison_damage_per_rate = {}
var accumulated = 0.0
var penetration = 0.0
@onready var target_stats = get_parent().get_parent()

func on_apply():
				var applier_stats = applier_stats_weakref.get_ref()
				if applier_stats:
								
								var ailment_effect = get_toxic_ailment_effect()

								
								var time_warp_multi = 1.0
								if applier_stats.keystones.has("TREE_TIME_WARP"):
												time_warp_multi *= 1.4
								if applier_stats.keystones.has("TREE_RAPID_DECAY"):
												time_warp_multi *= 1.2

								var dot_multi = applier_stats.gs("dot_damage")
								var sp = skill_parent_weakref.get_ref()
								if sp:
												dot_multi = sp.get_dot_damage()
												lifetime *= sp.get_ailment_duration()
								else:
												lifetime *= applier_stats.gs("ailment_duration")
								lifetime /= time_warp_multi

								poison_damage_per_rate = {
												"damage": {SkillTags.Tags.TOXIC: time_warp_multi * 0.05 * hit_damage * ailment_effect * dot_multi / Constants.AILMENT_RATE}, 
								}
								var amount = 0
								for tag in poison_damage_per_rate.damage:
												amount += poison_damage_per_rate.damage[tag]
								update_tracked_skill_amount(skill_parent_weakref.get_ref(), amount)
				else:
								remove_effect()

func on_tick(delta):
				var sp = skill_parent_weakref.get_ref()
				if sp:
								var info = target_stats.apply_damage(poison_damage_per_rate, Color.WHITE, applier_stats_weakref.get_ref(), false, true, sp, false)
								for skill in ramped_damage_for_applying_skill:
												if is_instance_valid(skill) and total_applying_damage > 0:
																var skill_amount = {
																				"did_kill": false, 
																				"damage": info.damage * ramped_damage_for_applying_skill[skill] / total_applying_damage
																}
																skill.track_hit(skill_amount)

func proliferate():
				var attacker_stats = applier_stats_weakref.get_ref()
				if attacker_stats:
								var effective_radius = 80 * sqrt(attacker_stats.gs("area_of_effect"))
								var enemies_to_spread = get_visible_allies(effective_radius)
								if enemies_to_spread and len(enemies_to_spread) > 0:
												enemies_to_spread.shuffle()

												

												var max_proliferations = attacker_stats.gs("infection_count")
												if skill_parent_weakref:
																var sp = skill_parent_weakref.get_ref()
																if sp:
																				max_proliferations = sp.get_infection_count()

												var n_profliferations = 0
												var did_explode = false
												for enemy in enemies_to_spread:
																if stats == enemy.stats:
																				continue
																var p = duplicate()
																p.applier_stats_weakref = weakref(attacker_stats)
																p.hit_damage = hit_damage
																p.ailment_effects = ailment_effects
																p.base_lifetime = base_lifetime
																p.lifetime_expired = lifetime_expired
																p.skill_parent_weakref = skill_parent_weakref
																p.accumulated = 0.0

																
																enemy.stats.apply_status_effect(p)

																
																n_profliferations += 1

																var explosion = poison_chain_effect.instantiate()
																explosion.source_target = stats
																explosion.dest_target = enemy.stats
																attacker_stats.ground_layer.call_deferred("add_child", explosion)

																if n_profliferations >= max_proliferations:
																				break

func get_status_flags():
				return [Constants.StatusFlags.INFECTED]

func get_damage():
				return poison_damage_per_rate.damage

func merge_damage(other_poison):
				var other_damage = other_poison.get_damage()
				var inc_damage = 0.0
				for tag in other_damage:
								var dmg_to_transfer = other_damage[tag] * (other_poison.lifetime - other_poison.lifetime_expired) / (lifetime - lifetime_expired)
								if poison_damage_per_rate.damage.has(tag):
												poison_damage_per_rate.damage[tag] += dmg_to_transfer
								else:
												poison_damage_per_rate.damage[tag] = dmg_to_transfer
								inc_damage += dmg_to_transfer
				var incoming_skill = other_poison.skill_parent_weakref.get_ref()
				if incoming_skill:
								update_tracked_skill_amount(incoming_skill, inc_damage)
				n_applications += 1

