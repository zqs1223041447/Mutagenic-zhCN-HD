extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_evasion", 
												"stat": "evasion", 
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
												"id": "impl_evasion_percent", 
												"stat": "evasion", 
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
												"id": "evasion", 
												"stat": "evasion", 
												"tags": [], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 150, 
												"step": 2, 
												"stepified": 1, 
												"tiers": 5, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "evasion_percent", 
												"stat": "evasion", 
												"tags": [], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.15, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 5, 
												"weight": 250, 
												"unique": false, 
								}, 

								{
												"id": "tinkerers_keystone", 
												"keystone": "UNIQUE_BOMB_SPECIALIST", 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonPantsMods.mod_option_configs.duplicate(true)
				)
				compile()
