extends BaseEffect

func initialize():
				
				buffs_and_nerfs = {
								"all_damage": {
												"type": Constants.ScalingType.MORE, 
												"amount": - 0.2, 
												"direction": 1
								}
				}

func get_status_flags():
				return [Constants.StatusFlags.POISONED]
