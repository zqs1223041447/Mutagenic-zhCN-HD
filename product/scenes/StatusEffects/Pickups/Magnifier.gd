extends BaseEffect

func initialize():
				buffs_and_nerfs = {
								"projectile_count": {
												"type": Constants.ScalingType.FLAT, 
												"amount": 2, 
												"direction": 1
								}, 
								"area_of_effect": {
												"type": Constants.ScalingType.MORE, 
												"amount": 0.5, 
												"direction": 1
								}, 
				}
