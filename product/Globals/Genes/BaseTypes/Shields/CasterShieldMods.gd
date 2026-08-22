extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_block_chance", 
												"stat": "block_chance", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.15, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "cast_speed_attacks", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.ATTACK], 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.08, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 4, 
												"weight": 50, 
												"unique": false, 
												"group_id": "cast_speed"
								}, 
								{
												"id": "cast_speed_spells", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.SPELL], 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.08, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 4, 
												"weight": 50, 
												"unique": false, 
												"group_id": "cast_speed"
								}, 
				]

				
				mod_option_configs.append_array(
								CommonShieldMods.mod_option_configs.duplicate(true)
				)
				compile()
