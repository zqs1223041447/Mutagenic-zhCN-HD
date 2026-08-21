extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_more_all_spell", 
												"stat": "all_damage", 
												"tags": [SkillTags.Tags.SPELL], 
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
												"id": "do_impl_more_physical_damage_spell", 
												"stat": "physical_damage", 
												"tags": [SkillTags.Tags.SPELL], 
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
												"id": "do_impl_more_lightning_damage_spell", 
												"stat": "lightning_damage", 
												"tags": [SkillTags.Tags.SPELL], 
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
												"id": "do_impl_more_cold_damage_spell", 
												"stat": "cold_damage", 
												"tags": [SkillTags.Tags.SPELL], 
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
												"id": "do_impl_more_fire_damage_spell", 
												"stat": "fire_damage", 
												"tags": [SkillTags.Tags.SPELL], 
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
												"id": "do_impl_more_toxic_damage_spell", 
												"stat": "physical_damage", 
												"tags": [SkillTags.Tags.SPELL], 
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
				]

				mod_option_configs.append_array(
								DropWeaponMods.mod_option_configs.duplicate(true)
				)

				compile(true)
