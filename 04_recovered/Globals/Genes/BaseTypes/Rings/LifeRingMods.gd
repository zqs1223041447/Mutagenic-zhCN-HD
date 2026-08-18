extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_health_flat", 
												"stat": "health_max", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 25, 
												"step": 1.5, 
												"stepified": 1, 
												"tiers": 4, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "impl_health_percent", 
												"stat": "health_max", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.08, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 3, 
												"weight": 50, 
												"unique": false, 
								}, 
								{
												"id": "health_regen", 
												"stat": "health_regen", 
												"tags": [], 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 10, 
												"step": 1.6, 
												"stepified": 1, 
												"tiers": 6, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "health_regen_percent", 
												"stat": "health_regen_percent", 
												"tags": [], 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.005, 
												"step": 1.5, 
												"stepified": 0.001, 
												"tiers": 3, 
												"weight": 50, 
												"unique": false, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonRingMods.mod_option_configs.duplicate(true)
				)
				compile()
