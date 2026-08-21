extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_cast_speed_percent", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.SPELL], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.08, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 3, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "impl_attack_speed_percent", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.ATTACK], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.08, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 3, 
												"weight": 250, 
												"unique": false, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonBootsMods.mod_option_configs.duplicate(true)
				)
				compile()
