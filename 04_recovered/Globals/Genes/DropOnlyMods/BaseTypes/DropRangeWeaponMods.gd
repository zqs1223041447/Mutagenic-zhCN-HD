extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_more_physical_damage_range", 
												"stat": "physical_damage", 
												"tags": [SkillTags.Tags.PROJECTILE], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_lightning_damage_range", 
												"stat": "lightning_damage", 
												"tags": [SkillTags.Tags.PROJECTILE], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_cold_damage_range", 
												"stat": "cold_damage", 
												"tags": [SkillTags.Tags.PROJECTILE], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_fire_damage_range", 
												"stat": "fire_damage", 
												"tags": [SkillTags.Tags.PROJECTILE], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_more_toxic_damage_range", 
												"stat": "physical_damage", 
												"tags": [SkillTags.Tags.PROJECTILE], 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.MORE, 
												"min_value": 0.1, 
												"step": 1.5, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_projectiles", 
												"stat": "projectile_count", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 1, 
												"step": 1.4, 
												"stepified": 1, 
												"tiers": 2, 
												"weight": 100, 
												"unique": false, 
												"drop_only": true
								}, 
				]

				mod_option_configs.append_array(
								DropWeaponMods.mod_option_configs.duplicate(true)
				)

				compile(true)
