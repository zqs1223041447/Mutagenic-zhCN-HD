extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "impl_physical_damage", 
												"stat": "physical_damage", 
												"tags": [SkillTags.Tags.SPELL], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 2, 
												"step": 1.5, 
												"stepified": 1, 
												"tiers": 7, 
												"weight": 250, 
												"unique": false, 
								}, 
								{
												"id": "impl_cast_speed", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.SPELL], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.06, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 4, 
												"weight": 250, 
												"unique": false, 
								}, 

								
								{
												"id": "echoes_of_sin_conversion", 
												"stat": "conversion_fire_to_toxic", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.25, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "echoes_of_sin_maximum_life", 
												"stat": "health_max", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 50, 
												"step": 1.6, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "echoes_of_sin_fire_damage", 
												"stat": "fire_damage", 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.4, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "echoes_of_sin_toxic_resistance", 
												"stat": "toxic_resistance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.25, 
												"step": 1.4, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "echoes_of_sin_fire_resistance", 
												"stat": "fire_resistance", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.25, 
												"step": 1.4, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 


								
								{
												"id": "chill_burn_keystone", 
												"keystone": "UNIQUE_CHILL_BURN", 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "chill_burn_life", 
												"stat": "health_max", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 50, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 

								
								{
												"id": "ancients_charm_life", 
												"stat": "health_max", 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 250, 
												"step": 2.0, 
												"stepified": 1, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "ancients_charm_cast_speed", 
												"stat": "cast_speed", 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.3, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
								{
												"id": "ancients_charm_aoe", 
												"stat": "area_of_effect", 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.5, 
												"step": 2.0, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 0, 
												"unique": true, 
								}, 
				]

				
				mod_option_configs.append_array(
								CommonRingMods.mod_option_configs.duplicate(true)
				)
				compile()
