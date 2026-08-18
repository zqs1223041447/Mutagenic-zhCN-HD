extends BaseEffect

onready var target_stats = get_parent().get_parent()

var bleed_damage_per_rate = {}

var hit_damage = 0.0
var accumulated = 0.0
var penetration = 0.0

const BLEED_RATE = 60.0

func on_apply():
				var applier_stats = applier_stats_weakref.get_ref()
				if applier_stats:
								
								var ailment_effect = get_physical_ailment_effect()

								
								var time_warp_multi = 1.0
								if applier_stats.keystones.has("TREE_TIME_WARP"):
												time_warp_multi = 1.4

								var dot_multi = applier_stats.gs("dot_damage")
								var sp = skill_parent_weakref.get_ref()
								if sp:
												dot_multi = sp.get_dot_damage()
												lifetime *= sp.get_ailment_duration()
								else:
												lifetime *= applier_stats.gs("ailment_duration")
								lifetime /= time_warp_multi
								if applier_stats.keystones.has("TREE_MAGMATIC_BLOOD"):
												bleed_damage_per_rate = {
																"damage": {SkillTags.Tags.FIRE: time_warp_multi * 0.1 * hit_damage * ailment_effect * dot_multi / BLEED_RATE}, 
												}
								else:
												bleed_damage_per_rate = {
																"damage": {SkillTags.Tags.PHYSICAL: time_warp_multi * 0.1 * hit_damage * ailment_effect * dot_multi / BLEED_RATE}, 
												}

								var amount = 0
								for tag in bleed_damage_per_rate.damage:
												amount += bleed_damage_per_rate.damage[tag]
								update_tracked_skill_amount(skill_parent_weakref.get_ref(), amount)

				else:
								remove_effect()

func on_tick(delta):
				var sp = skill_parent_weakref.get_ref()
				if sp:
								var info = target_stats.apply_damage(bleed_damage_per_rate, Color.white, applier_stats_weakref.get_ref(), false, true, sp, false)
								for skill in ramped_damage_for_applying_skill:
												if is_instance_valid(skill) and total_applying_damage > 0:
																var skill_amount = {
																				"did_kill": false, 
																				"damage": info.damage * ramped_damage_for_applying_skill[skill] / total_applying_damage
																}
																skill.track_hit(skill_amount)

func get_status_flags():
				return [Constants.StatusFlags.RUPTURED]

func get_remaining_bleed_damage():
				var effective_remaining = bleed_damage_per_rate.duplicate()
				for k in effective_remaining.damage:
								effective_remaining.damage[k] *= (lifetime - lifetime_expired) * BLEED_RATE
				return effective_remaining

func get_damage():
				return bleed_damage_per_rate.damage

func merge_damage(other_bleed):
				var other_damage = other_bleed.get_damage()
				var inc_damage = 0.0
				for tag in other_damage:
								var dmg_to_transfer = other_damage[tag] * (other_bleed.lifetime - other_bleed.lifetime_expired) / (lifetime - lifetime_expired)
								if bleed_damage_per_rate.damage.has(tag):
												bleed_damage_per_rate.damage[tag] += dmg_to_transfer
								else:
												bleed_damage_per_rate.damage[tag] = dmg_to_transfer
								inc_damage += dmg_to_transfer
				var incoming_skill = other_bleed.skill_parent_weakref.get_ref()
				if incoming_skill:
								update_tracked_skill_amount(incoming_skill, inc_damage)
				n_applications += 1
