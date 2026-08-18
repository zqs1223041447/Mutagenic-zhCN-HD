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
												"id": "crown_of_ice_conversion", 
												"keystone": "UNIQUE_CROWN_OF_ICE", 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "crown_of_ice_crit", 
												"stat": "crit_chance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.03, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonHelmetMods.mod_option_configs.duplicate(true)
				)
				compile()
