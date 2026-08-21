extends BaseEffect

func initialize():
				buffs_and_nerfs = {
								"movement_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": - 0.25, 
												"direction": 1
								}, 
				}

func is_better_than(other):
				return lifetime_expired < other.lifetime_expired

func get_status_flags():
				return [Constants.StatusFlags.HAMSTRUNG]

func get_effect_amount():
				return - 0.25
