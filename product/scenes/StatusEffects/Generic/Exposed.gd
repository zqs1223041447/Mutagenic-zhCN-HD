extends BaseEffect

var exposure_effect = 1.0
var strength = 0.0

func initialize():
				strength = - 0.1 * exposure_effect
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

func is_better_than(other):
				return strength <= other.strength

func get_status_flags():
				return [Constants.StatusFlags.EXPOSED]

func get_effect_amount():
				return strength
