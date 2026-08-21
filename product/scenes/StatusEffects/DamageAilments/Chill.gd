extends BaseEffect

var damage_percentage = 0.0
var strength


func initialize():
				var effect_stats = applier_stats_weakref.get_ref()
				var ailment_effect = get_cold_ailment_effect()
				if effect_stats:
								var sp = skill_parent_weakref.get_ref()
								if sp:
												lifetime *= sp.get_ailment_duration()
								else:
												lifetime *= effect_stats.gs("ailment_duration")

				
				var base_amount = 0.05 + 0.35 * clamp(damage_percentage, 0.0, 0.3) / 0.3
				strength = clamp( - base_amount * ailment_effect, - 0.4, 0.4)

				buffs_and_nerfs = {
								"movement_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": strength, 
												"direction": - 1
								}, 
								"cast_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": strength, 
												"direction": - 1
								}
				}

func get_status_flags():
				return [Constants.StatusFlags.CHILLED, Constants.StatusFlags.REGULAR_ELEMENTAL_AILMENT]

func is_better_than(other_chill):
				return strength < other_chill.strength

func on_apply():
				var applier_stats = applier_stats_weakref.get_ref()
				if applier_stats:
								lifetime *= applier_stats.gs("ailment_duration")
								if applier_stats.keystones.has("TREE_CRYOMANCER"):
												lifetime *= 2.0

func get_effect_amount():
				return strength


