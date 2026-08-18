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
												"step": 1.3, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "health_max_percent", 
												"stat": "health_max", 
												"tags": [], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.08, 
												"step": 1.4, 
												"stepified": 0.01, 
												"tiers": 5, 
												"weight": 150, 
												"unique": false, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonShieldMods.mod_option_configs.duplicate(true)
				)
				compile()
