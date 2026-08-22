extends BaseEffect

var strength = 0.0
var vulnerable_effect = 1.0


func initialize():
				strength = 0.25 * vulnerable_effect
				buffs_and_nerfs = {
								"incoming_damage": {
												"type": Constants.ScalingType.MORE, 
												"amount": strength, 
												"direction": 1
								}
				}

func is_better_than(other):
				return strength >= other.strength

func get_status_flags():
				return [Constants.StatusFlags.VULNERABLE]

func get_effect_amount():
				return strength
