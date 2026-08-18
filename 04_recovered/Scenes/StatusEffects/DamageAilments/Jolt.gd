extends BaseEffect

onready var target_stats = get_parent().get_parent()

var damage_percentage = 0.0
var strength = 0.0

var sfx = preload("res://Sounds/SFX/jolt.wav")

func initialize():
				var effect_stats = applier_stats_weakref.get_ref()
				var ailment_effect = get_lightning_ailment_effect()
				if effect_stats:
								var sp = skill_parent_weakref.get_ref()
								if sp:
												lifetime *= sp.get_ailment_duration()
								else:
												lifetime *= effect_stats.gs("ailment_duration")

				
				var base_amount = 0.05 + 0.45 * clamp(damage_percentage, 0.0, 0.1) / 0.1
				strength = base_amount * ailment_effect
				buffs_and_nerfs = {
								"incoming_damage": {
												"type": Constants.ScalingType.MORE, 
												"amount": strength, 
												"direction": 1
								}
				}

func is_better_than(other_char):
				return strength > other_char.strength

func get_status_flags():
				return [Constants.StatusFlags.JOLTED, Constants.StatusFlags.REGULAR_ELEMENTAL_AILMENT]

func get_effect_amount():
				return strength

