extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_life", 
												"stat": "health_max", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 6, 
												"step": 1.4, 
												"stepified": 1, 
												"tiers": 8, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "impl_life_percent", 
												"stat": "health_max", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.05, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 4, 
												"weight": 50, 
												"unique": false, 
								}, 
								{
												"id": "life_recover_rate", 
												"stat": "health_recovery_rate", 
												"tags": [], 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.05, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 2, 
												"weight": 50, 
												"unique": false, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonGlovesMods.mod_option_configs.duplicate(true)
				)
				compile()
