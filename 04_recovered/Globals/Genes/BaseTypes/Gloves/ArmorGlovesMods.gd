extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_armor", 
												"stat": "mitigation", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 50, 
												"step": 2, 
												"stepified": 1, 
												"tiers": 4, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "impl_armor_percent", 
												"stat": "mitigation", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.15, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 4, 
												"weight": 250, 
												"unique": false, 
								}, 

								{
												"id": "armor", 
												"stat": "mitigation", 
												"tags": [], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 150, 
												"step": 2, 
												"stepified": 1, 
												"tiers": 4, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "armor_percent", 
												"stat": "mitigation", 
												"tags": [], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.15, 
												"step": 1.4, 
												"stepified": 0.01, 
												"tiers": 4, 
												"weight": 250, 
												"unique": false, 
								}, 

								
								{
												"id": "bloody_knuckle_cast_speed", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.MELEE], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.5, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonGlovesMods.mod_option_configs.duplicate(true)
				)
				compile()
