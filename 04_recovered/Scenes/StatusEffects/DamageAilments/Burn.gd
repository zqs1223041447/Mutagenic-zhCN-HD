extends BaseEffect

onready var target_stats = get_parent().get_parent()

var burn_sfx = preload("res://Sounds/SFX/burn.wav")

var burn_damage_per_rate = {}

var hit_damage = 0.0
var ailment_modifier = 1.0
var accumulated = 0.0
var penetration = 0.0


func on_apply():
				var applier_stats = applier_stats_weakref.get_ref()
				if applier_stats:
												
								var ailment_effect = get_fire_ailment_effect()

								
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

								burn_damage_per_rate = {
												"damage": {SkillTags.Tags.FIRE: time_warp_multi * 1.0 * hit_damage * ailment_effect * dot_multi / Constants.AILMENT_RATE}, 
								}
								var amount = 0
								for tag in burn_damage_per_rate.damage:
												amount += burn_damage_per_rate.damage[tag]
								update_tracked_skill_amount(skill_parent_weakref.get_ref(), amount)
				else:
								remove_effect()

func on_tick(delta):
				var sp = skill_parent_weakref.get_ref()
				if sp:
								var info
								if sp.stats and sp.stats.keystones.has("UNIQUE_CHILL_BURN"):
												var cold_converted = burn_damage_per_rate.duplicate(true)
												cold_converted.damage[SkillTags.Tags.COLD] = cold_converted.damage[SkillTags.Tags.FIRE]
												cold_converted.damage.erase(SkillTags.Tags.FIRE)
												info = target_stats.apply_damage(cold_converted, Color.white, applier_stats_weakref.get_ref(), false, true, sp, false)
								else:
												info = target_stats.apply_damage(burn_damage_per_rate, Color.white, applier_stats_weakref.get_ref(), false, true, sp, false)
								for skill in ramped_damage_for_applying_skill:
												if is_instance_valid(skill) and total_applying_damage > 0:
																var skill_amount = {
																				"did_kill": false, 
																				"damage": info.damage * ramped_damage_for_applying_skill[skill] / total_applying_damage
																}
																skill.track_hit(skill_amount)

func get_status_flags():
				return [Constants.StatusFlags.BURNING, Constants.StatusFlags.REGULAR_ELEMENTAL_AILMENT]

func is_better_than(other_burn):
				return burn_damage_per_rate.damage[SkillTags.Tags.FIRE] > other_burn.burn_damage_per_rate.damage[SkillTags.Tags.FIRE]

func proliferate():
				var attacker_stats = applier_stats_weakref.get_ref()
				if attacker_stats:
								var enemies_to_spread = get_visible_allies(50 * sqrt(attacker_stats.gs("area_of_effect")))
								var count = 0
								for enemy in enemies_to_spread:
												if stats == enemy.stats:
																continue
												if enemy.stats.is_dead:
																continue
												
												if enemy.stats.unique_status_flags.has(Constants.StatusFlags.BURNING):
																continue

												var p = duplicate()
												p.applier_stats_weakref = weakref(attacker_stats)
												p.skill_parent_weakref = skill_parent_weakref
												p.hit_damage = hit_damage
												p.ailment_effects = ailment_effects
												p.base_lifetime = base_lifetime
												p.lifetime_expired = lifetime_expired
												p.accumulated = 0.0

												
												enemy.stats.apply_status_effect(p)
												count += 1
												if count >= 5:
																break


func get_damage():
				return burn_damage_per_rate.damage
