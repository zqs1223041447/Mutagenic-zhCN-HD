extends BaseEffect

var curse_effect = 1.0
var strength = 0.0

func initialize():
				var curse_resistance = stats.cap_resistance(stats.gs("curse_resistance"), 1.0)
				strength = 0.3 * curse_effect * (1.0 - curse_resistance)
				buffs_and_nerfs = {
								"self_duration": {
												"type": Constants.ScalingType.MORE, 
												"amount": strength, 
												"direction": 1
								}
				}

func is_better_than(other):
				if strength == other.strength:
								return lifetime - lifetime_expired > other.lifetime - other.lifetime_expired
				return strength > other.strength

func get_status_flags():
				return [Constants.StatusFlags.PROTRACT, Constants.StatusFlags.CURSED]

func get_effect_amount():
				return strength

