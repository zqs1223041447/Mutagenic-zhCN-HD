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
												"id": "ogre_talisman_health_damage", 
												"keystone": "UNIQUE_OGRE_TALISMAN", 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "ogre_talisman_fire_damage", 
												"stat": "fire_damage", 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.3, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 

								
								{
												"id": "strength_from_strength_conversion", 
												"keystone": "UNIQUE_STRENGTH_FROM_STRENGTH", 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "strength_from_strength_life", 
												"stat": "health_max", 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": - 0.3, 
												"step": 1.8, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonAmuletMods.mod_option_configs.duplicate(true)
				)
				compile()
