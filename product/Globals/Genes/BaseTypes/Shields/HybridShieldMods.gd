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
												"id": "evasion", 
												"stat": "evasion", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 100, 
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
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.15, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 5, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "armor", 
												"stat": "mitigation", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 100, 
												"step": 2, 
												"stepified": 1, 
												"tiers": 5, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "armor_percent", 
												"stat": "mitigation", 
												"tags": [], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.15, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 5, 
												"weight": 250, 
												"unique": false, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonShieldMods.mod_option_configs.duplicate(true)
				)
				compile()
