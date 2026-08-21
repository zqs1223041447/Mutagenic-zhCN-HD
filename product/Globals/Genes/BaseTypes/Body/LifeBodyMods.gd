extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_life", 
												"stat": "health_max", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 7, 
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
												"tiers": 5, 
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
												"tiers": 3, 
												"weight": 50, 
												"unique": false, 
								}, 

								
								{
												"id": "echoing_fury_keystone", 
												"keystone": "UNIQUE_ECHOING_FURY", 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "echoing_fury_resistance", 
												"stat": "toxic_resistance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 1.0, 
												"step": 1, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonBodyMods.mod_option_configs.duplicate(true)
				)
				compile()
