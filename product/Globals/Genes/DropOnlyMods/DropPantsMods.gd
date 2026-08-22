extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_toughness_boon", 
												"stat": "toughness_boon", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 1, 
												"step": 2, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_life", 
												"stat": "health_max", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
				]

				mod_option_configs.append_array(
								DropCommonArmorMods.mod_option_configs.duplicate(true)
				)

				compile(true)
