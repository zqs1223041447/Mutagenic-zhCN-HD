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
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 1, 
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
												"tiers": 6, 
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
												"tiers": 6, 
												"weight": 250, 
												"unique": false, 
								}, 

								
								{
												"id": "elder_ward_life", 
												"stat": "health_max", 
												"tags": [], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 150, 
												"step": 1.2, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "elder_ward_block_chance", 
												"stat": "block_chance", 
												"tags": [], 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.25, 
												"step": 1.2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "elder_ward_crit_resistance", 
												"stat": "crit_resistance", 
												"tags": [], 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 1.0, 
												"step": 1.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "elder_ward_lgob", 
												"stat": "life_gain_on_block", 
												"tags": [], 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 500, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonShieldMods.mod_option_configs.duplicate(true)
				)
				compile()
