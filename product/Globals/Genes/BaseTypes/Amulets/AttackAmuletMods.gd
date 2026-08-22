extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								
								{
												"id": "impl_physical_damage", 
												"stat": "physical_damage", 
												"tags": [SkillTags.Tags.ATTACK], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 1, 
												"step": 1.5, 
												"stepified": 1, 
												"tiers": 8, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "impl_attack_speed", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.ATTACK], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.06, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 4, 
												"weight": 250, 
												"unique": false, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonAmuletMods.mod_option_configs.duplicate(true)
				)
				compile()
