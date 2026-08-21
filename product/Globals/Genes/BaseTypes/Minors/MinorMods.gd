extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								
								{
												"id": "unique_harrowing_cold_damage", 
												"stat": "cold_damage", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 8, 
												"step": 1.5, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "unique_harrowing_cold_resistance", 
												"stat": "cold_resistance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.25, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "unique_harrowing_cold_ailment_chance", 
												"stat": "cold_ailment_chance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.1, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 

								{
												"id": "unique_expansion_charm_radius", 
												"stat": "radius", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 2.0, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonMinorMods.mod_option_configs.duplicate(true)
				)
				compile()
