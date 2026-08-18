extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_physical_damage", 
												"stat": "physical_damage", 
												"tags": [SkillTags.Tags.ATTACK], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 2, 
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
												"tiers": 3, 
												"weight": 250, 
												"unique": false, 
								}, 

								{
												"id": "frozen_sludge_keystone", 
												"keystone": "UNIQUE_FROZEN_SLUDGE", 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonRingMods.mod_option_configs.duplicate(true)
				)
				compile()
