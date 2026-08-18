extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_swiftness_boon", 
												"stat": "swiftness_boon", 
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
												"id": "do_impl_more_constitution", 
												"stat": "constitution", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.06, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_strength", 
												"stat": "strength", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.06, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_finesse", 
												"stat": "finesse", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.06, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_wisdom", 
												"stat": "wisdom", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.06, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_agility", 
												"stat": "agility", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.06, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
				]

				mod_option_configs.append_array(
								DropCommonJewelleryMods.mod_option_configs.duplicate(true)
				)

				compile(true)
