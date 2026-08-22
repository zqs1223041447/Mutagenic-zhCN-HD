extends BaseEffect

func initialize():
				buffs_and_nerfs = {
								"movement_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": 0.3, 
												"direction": 1
								}, 
								"cast_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": 0.3, 
												"direction": 1
								}, 
								"projectile_speed": {
												"type": Constants.ScalingType.MORE, 
												"amount": 0.3, 
												"direction": 1
								}
				}

