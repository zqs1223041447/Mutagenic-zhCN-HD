extends BaseEffect

var hit_damage = 0.0
var poison_damage_per_rate = {}
var accumulated = 0.0
var penetration = 0.0

onready var target_stats = get_parent().get_parent()

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
								var info = target_stats.apply_damage(poison_damage_per_rate, Color.white, applier_stats_weakref.get_ref(), false, true, sp, false)
								for skill in ramped_damage_for_applying_skill:
												if is_instance_valid(skill) and total_applying_damage > 0:
																var skill_amount = {
																				"did_kill": false, 
																				"damage": info.damage * ramped_damage_for_applying_skill[skill] / total_applying_damage
																}
																skill.track_hit(skill_amount)

func get_status_flags():
				return [Constants.StatusFlags.POISONED]

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
