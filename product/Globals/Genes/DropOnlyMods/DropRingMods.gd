extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_crit_multi", 
												"stat": "crit_multi", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.5, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_aura_effect", 
												"stat": "aura_effect", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.15, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 20, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_flat_physical_damage", 
												"stat": "physical_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 70, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_flat_lightning_damage", 
												"stat": "lightning_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 70, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_flat_cold_damage", 
												"stat": "cold_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 70, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_flat_fire_damage", 
												"stat": "fire_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 70, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_flat_toxic_damage", 
												"stat": "toxic_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 70, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_crit_chance", 
												"stat": "crit_chance", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.01, 
												"step": 1.5, 
												"stepified": 0.001, 
												"tiers": 1, 
												"weight": 50, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_swiftness_boon", 
												"stat": "swiftness_boon", 
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
												"id": "do_impl_precision_boon", 
												"stat": "precision_boon", 
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
				]

				mod_option_configs.append_array(
								DropCommonJewelleryMods.mod_option_configs.duplicate(true)
				)

				compile(true)
