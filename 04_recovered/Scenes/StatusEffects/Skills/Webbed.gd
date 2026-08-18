extends BaseEffect

var damage_percentage = 0.0
var strength

func initialize():
				buffs_and_nerfs = {
								"movement_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": - 0.5, 
												"direction": - 1
								}, 
				}

func get_status_flags():
				return []

func is_better_than(other):
				return lifetime > other.lifetime

func get_effect_amount():
				return strength


