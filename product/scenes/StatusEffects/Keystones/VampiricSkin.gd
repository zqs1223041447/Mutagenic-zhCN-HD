extends BaseEffect

func initialize():
				buffs_and_nerfs = {
								"health_regen": {
												"type": Constants.ScalingType.MORE, 
												"amount": 1.0, 
												"direction": 1
								}, 
								"health_regen_percent": {
												"type": Constants.ScalingType.MORE, 
												"amount": 1.0, 
												"direction": 1
								}
				}
