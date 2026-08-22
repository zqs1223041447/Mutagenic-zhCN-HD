extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_crit_multi", 
												"stat": "crit_multi", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.08, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 50, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_aura_effect", 
												"stat": "aura_effect", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.25, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 15, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_physical_damage", 
												"stat": "physical_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_cold_damage", 
												"stat": "cold_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_fire_damage", 
												"stat": "fire_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_lightning_damage", 
												"stat": "lightning_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_toxic_damage", 
												"stat": "toxic_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_dot", 
												"stat": "dot_damage", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_damage_per_attr", 
												"stat": "damage_per_25_attributes", 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.01, 
												"step": 3.0, 
												"stepified": 0.01, 
												"tiers": 2, 
												"weight": 5, 
												"unique": false, 
												"drop_only": true
								}, 

								
								{
												"id": "do_damage_per_attr", 
												"stat": "damage_per_25_attributes", 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.01, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 2, 
												"weight": 10, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_health_more", 
												"stat": "health_max", 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.05, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_mitigation_more", 
												"stat": "mitigation", 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.05, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_evasion_more", 
												"stat": "evasion", 
												"affix_type": Constants.ModType.PREFIX, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.05, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 

								
								{
												"id": "do_inc_constitution", 
												"stat": "constitution", 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.12, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_inc_str", 
												"stat": "strength", 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.12, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_inc_wisdom", 
												"stat": "wisdom", 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.12, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_inc_finesse", 
												"stat": "finesse", 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.12, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_inc_agility", 
												"stat": "agility", 
												"affix_type": Constants.ModType.SUFFIX, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.12, 
												"step": 1.5, 
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
