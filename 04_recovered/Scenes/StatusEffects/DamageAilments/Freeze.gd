extends BaseEffect

var damage_percentage = 0.0
var strength = 0.0

func on_apply():
				var applier_stats = applier_stats_weakref.get_ref()

				if applier_stats:
								var effect = get_cold_ailment_effect()
								var sp = skill_parent_weakref.get_ref()
								if sp:
												lifetime *= sp.get_ailment_duration()
								else:
												lifetime *= applier_stats.gs("ailment_duration")
								lifetime *= effect

								strength = lifetime

func is_better_than(other):
				return lifetime >= other.lifetime

func get_status_flags():
				return [Constants.StatusFlags.FROZEN]

