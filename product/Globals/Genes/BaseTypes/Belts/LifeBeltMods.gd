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

								
								{
												"id": "balanced_oppression_penetration", 
												"affix_type": Constants.ModType.SUFFIX, 
												"keystone": "UNIQUE_BALANCED_OPPRESSION", 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "balanced_oppression_fire_resistance", 
												"stat": "fire_resistance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.2, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "balanced_oppression_cold_resistance", 
												"stat": "cold_resistance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.2, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 

				]

				
				mod_option_configs.append_array(
								CommonBeltMods.mod_option_configs.duplicate(true)
				)
				compile()
