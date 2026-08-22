extends BaseEffect

var damage_percentage = 0.0
var strength = 0.0

func initialize():
				var effect_stats = applier_stats_weakref.get_ref()
				var ailment_effect = get_lightning_ailment_effect()
				if effect_stats:
								var sp = skill_parent_weakref.get_ref()
								if sp:
												lifetime *= sp.get_ailment_duration()
								else:
												lifetime *= effect_stats.gs("ailment_duration")
				var base_amount = 0.05 + 0.2 * clamp(damage_percentage, 0.0, 0.1) / 0.1
				strength = - base_amount * ailment_effect
				buffs_and_nerfs = {
								"physical_resistance": {
												"type": Constants.ScalingType.FLAT, 
												"amount": strength, 
												"direction": 1
								}, 
								"lightning_resistance": {
												"type": Constants.ScalingType.FLAT, 
												"amount": strength, 
												"direction": 1
								}, 
								"cold_resistance": {
												"type": Constants.ScalingType.FLAT, 
												"amount": strength, 
												"direction": 1
								}, 
								"fire_resistance": {
												"type": Constants.ScalingType.FLAT, 
												"amount": strength, 
												"direction": 1
								}, 
								"toxic_resistance": {
												"type": Constants.ScalingType.FLAT, 
												"amount": strength, 
												"direction": 1
								}, 
				}

func is_better_than(other_electrocution):
				return strength < other_electrocution.strength

func get_status_flags():
				return [Constants.StatusFlags.ELECTROCUTED]

func get_effect_amount():
				return strength
