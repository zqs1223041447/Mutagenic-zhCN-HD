extends BaseEffect

var damage_percentage = 0.0
var strength = 0.0

func initialize():
				var effect_stats = applier_stats_weakref.get_ref()
				var ailment_effect = get_fire_ailment_effect()
				var sp = skill_parent_weakref.get_ref()
				if sp:
								lifetime *= sp.get_ailment_duration()
				elif effect_stats:
								lifetime *= effect_stats.gs("ailment_duration")

				
				var base_amount = 0.05 + 0.15 * clamp(damage_percentage, 0.0, 0.3) / 0.3
				strength = clamp( - base_amount * ailment_effect, - 0.5, 0.5)
				buffs_and_nerfs = {
								"cast_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": strength, 
												"direction": 1
								}, 
								"all_damage": {
												"type": Constants.ScalingType.MORE, 
												"amount": strength, 
												"direction": 1
								}
				}

				if effect_stats and effect_stats.keystones.has("TREE_OVERCOOK"):
								print("Applying char from overcook")
								buffs_and_nerfs["incoming_damage"] = {
												"type": Constants.ScalingType.MORE, 
												"amount": 1.4, 
												"direction": 1
								}

func is_better_than(other_char):
				return strength < other_char.strength

func get_status_flags():
				return [Constants.StatusFlags.CHARRED]

func get_effect_amount():
				return strength

