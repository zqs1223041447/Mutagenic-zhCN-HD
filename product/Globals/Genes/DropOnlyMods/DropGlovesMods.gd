extends GeneMods

func _ready() -> void :
				mod_option_configs = [
								{
												"id": "do_impl_cast_speed_attack", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.ATTACK], 
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
												"id": "do_impl_curse_effect", 
												"stat": "curse_effect", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.PERCENT, 
												"min_value": 0.25, 
												"step": 2, 
												"stepified": 0.01, 
												"tiers": 1, 
												"weight": 20, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_crit_chance", 
												"stat": "crit_chance", 
												"affix_type": Constants.ModType.IMPLICIT, 
												"type": Constants.ScalingType.FLAT, 
												"min_value": 0.01, 
												"step": 2, 
												"stepified": 0.001, 
												"tiers": 1, 
												"weight": 50, 
												"unique": false, 
												"drop_only": true
								}, 
								{
												"id": "do_impl_cast_speed_spell", 
												"stat": "cast_speed", 
												"tags": [SkillTags.Tags.SPELL], 
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
								DropCommonArmorMods.mod_option_configs.duplicate(true)
				)

				compile(true)
