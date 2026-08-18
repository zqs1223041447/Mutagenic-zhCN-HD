extends BaseEffect

func get_status_flags():
				return [Constants.StatusFlags.BLOOD_BOIL]

func initialize():
				buffs_and_nerfs = {
								"incoming_damage": {
												"type": Constants.ScalingType.PERCENT, 
												"amount": - 0.15, 
												"direction": 1
								}, 
								"health_recovery_rate": {
												"type": Constants.ScalingType.PERCENT, 
												"amount": 0.2, 
												"direction": 1
								}
				}
