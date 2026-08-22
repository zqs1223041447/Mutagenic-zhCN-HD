extends BaseEffect

var effect_is_damage

func initialize():
				if effect_is_damage:
								buffs_and_nerfs = {
												"area_damage": {
																"type": Constants.ScalingType.MORE, 
																"amount": 0.2, 
																"direction": 1
												}
								}
				else:
								buffs_and_nerfs = {
												"area_of_effect": {
																"type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
																"direction": 1
												}
								}
