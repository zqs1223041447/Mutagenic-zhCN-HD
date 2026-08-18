extends Projectile

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var damage_amp = 1.0
				var outgoing_damage = damage.duplicate(true)
				var should_consume = false
				if target.stats.status_flags.has(Constants.StatusFlags.JOLTED):
								
								var jolt_effect = target.stats.status_flag_amounts[Constants.StatusFlags.JOLTED]
								if jolt_effect > 0:
												damage_amp += jolt_effect
												for type in outgoing_damage.damage:
																outgoing_damage.damage[type] *= damage_amp
												should_consume = true

				var info = target.stats.apply_damage(outgoing_damage, Color.white, stats, true, false, sp)
				track_hit(info)
				if should_consume:
								target.stats.consume_all_effects(Constants.StatusFlags.JOLTED)


