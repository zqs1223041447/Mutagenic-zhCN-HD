extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_toughness_boon", 
												"stat": "toughness_boon", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 1, 
												"step": 1, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 10, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_cast_speed", 
												"stat": "cast_speed", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.04, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 50, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_movement_speed", 
												"stat": "movement_speed", 
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
								{
												"id": "do_impl_life_regen", 
												"stat": "health_regen_percent", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.02, 
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
