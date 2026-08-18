extends Node

enum Tags{
				PHYSICAL, 
				LIGHTNING, 
				COLD, 
				FIRE, 
				TOXIC, 
				DAMAGE, 
				PROJECTILE, 
				DEFENCE, 
				CRITICAL, 
				RESISTANCE, 
				LIFE, 
				SPEED, 
				CURSE, 
				DURATION, 
				AILMENT, 
				ATTRIBUTE, 
				BOON, 
}

var tag_name = {
				Tags.PHYSICAL: "Physical", 
				Tags.LIGHTNING: "Lightning", 
				Tags.COLD: "Cold", 
				Tags.FIRE: "Fire", 
				Tags.TOXIC: "Toxic", 
				Tags.DAMAGE: "Damage", 
				Tags.DEFENCE: "Defence", 
				Tags.CRITICAL: "Critical", 
				Tags.RESISTANCE: "Resistance", 
				Tags.LIFE: "Life", 
				Tags.SPEED: "Speed", 
				Tags.DURATION: "Duration", 
				Tags.AILMENT: "Ailment", 
}

var valid_stat_cache = {}

func skill_sorter(a, b):
				return skill_sort_list.find(a) < skill_sort_list.find(b)

var character_sheet_list = [
				"health_max", 
				"health_regen", 
				"movement_speed", 

				"mitigation", 
				"evasion", 
				
				"physical_resistance", 
				"lightning_resistance", 
				"cold_resistance", 
				"fire_resistance", 
				"toxic_resistance", 
				"crit_resistance", 
				"curse_resistance", 
				"ailment_avoidance", 
				"block_chance", 
				"life_gain_on_block", 

				
				"constitution", 
				"strength", 
				"agility", 
				"wisdom", 
				"finesse", 

				
				"swiftness_boon", 
				"precision_boon", 
				"toughness_boon", 
				"boon_duration", 
				"self_duration", 
				"incoming_damage", 
]

var all_skill_list = [
				"skill_effectiveness", 
				"cast_speed", 
				"physical_ailment_chance", 
				"lightning_ailment_chance", 
				"cold_ailment_chance", 
				"fire_ailment_chance", 
				"toxic_ailment_chance", 
				"amplify_ailment_chance", 
				"physical_penetration", 
				"lightning_penetration", 
				"cold_penetration", 
				"fire_penetration", 
				"toxic_penetration", 
				"vulnerable_chance", 
				"vulnerable_effect", 
				"exposure_chance", 
				"exposure_effect", 
				"infection_count", 
				"life_gain_on_hit", 
]

var damage_list = [
				"physical_damage", 
				"lightning_damage", 
				"cold_damage", 
				"fire_damage", 
				"toxic_damage"
]

var skill_sort_list = [
				"damage", 
				"skill_effectiveness", 
				"damage_effectiveness", 
				"cast_speed", 
				"cooldown", 
				"radius", 
				"crit_chance", 
				"crit_multi", 
				"projectile_count", 
				"area_of_effect", 
				"skill_pierce", 
				"skill_chain", 

				"projectile_speed", 

				
				"physical_penetration", 
				"lightning_penetration", 
				"cold_penetration", 
				"fire_penetration", 
				"toxic_penetration", 

				"physical_ailment_chance", 
				"physical_ailment_effect", 

				"lightning_ailment_chance", 
				"lightning_ailment_effect", 

				"cold_ailment_chance", 
				"cold_ailment_effect", 

				"fire_ailment_chance", 
				"fire_ailment_effect", 

				"toxic_ailment_chance", 
				"toxic_ailment_effect", 

				"ailment_duration", 
				"amplify_ailment_chance", 

				"vulnerable_chance", 
				"vulnerable_effect", 

				"exposure_chance", 
				"exposure_effect", 

				
				"infection_count", 

				"life_gain_on_hit", 

				"swiftness_boon_on_hit_chance", 
				"toughness_boon_on_hit_chance", 


				"precision_boon_on_crit_chance", 
				"toughness_boon_on_get_hit_chance", 

				"swiftness_boon_on_kill_chance", 
				"precision_boon_on_kill_chance", 
				"toughness_boon_on_kill_chance", 

				"curse_effect", 
				"aura_effect", 
				"base_duration", 
				"increased_duration"
]

var stat_list = [
				"health_max", 
				"health_regen", 
				"health_regen_percent", 
				"health_recovery_rate", 

				"boon_duration", 
				"movement_speed", 
				"projectile_speed", 
				"projectile_count", 
				"area_of_effect", 
				"skill_pierce", 
				"skill_chain", 
				"crit_chance", 
				"crit_multi", 
				"cast_speed", 
				"constitution", 
				"strength", 
				"agility", 
				"wisdom", 
				"finesse", 
				"swiftness_boon", 
				"precision_boon", 
				"toughness_boon", 

				
				"all_damage", 
				"damage_per_boon", 
				"damage_per_25_attributes", 

				
				"projectile_damage", 
				"area_damage", 
				"dot_damage", 
				"hit_damage", 

				
				"physical_damage", 
				"lightning_damage", 
				"cold_damage", 
				"fire_damage", 
				"toxic_damage", 

				
				"physical_resistance", 
				"lightning_resistance", 
				"cold_resistance", 
				"fire_resistance", 
				"toxic_resistance", 
				"maximum_physical_resistance", 
				"maximum_lightning_resistance", 
				"maximum_cold_resistance", 
				"maximum_fire_resistance", 
				"maximum_toxic_resistance", 
				"curse_resistance", 
				"mitigation", 
				"evasion", 
				"block_chance", 
				"life_gain_on_block", 
				"life_gain_on_hit", 
				"ailment_avoidance", 
				"crit_resistance", 

				
				"physical_penetration", 
				"lightning_penetration", 
				"cold_penetration", 
				"fire_penetration", 
				"toxic_penetration", 

				"physical_ailment_effect", 
				"lightning_ailment_effect", 
				"cold_ailment_effect", 
				"fire_ailment_effect", 
				"toxic_ailment_effect", 

				"physical_ailment_chance", 
				"lightning_ailment_chance", 
				"cold_ailment_chance", 
				"fire_ailment_chance", 
				"toxic_ailment_chance", 

				"ailment_duration", 
				"amplify_ailment_chance", 

				
				"vulnerable_chance", 
				"vulnerable_effect", 

				"exposure_chance", 
				"exposure_effect", 

				
				"infection_count", 

				"swiftness_boon_on_hit_chance", 
				"toughness_boon_on_hit_chance", 
				"precision_boon_on_crit_chance", 
				"toughness_boon_on_get_hit_chance", 

				"swiftness_boon_on_kill_chance", 
				"precision_boon_on_kill_chance", 
				"toughness_boon_on_kill_chance", 

				"physical_per_25_strength", 
				"lightning_per_25_agility", 
				"fire_per_25_constitution", 
				"cold_per_25_wisdom", 
				"toxic_per_25_finesse", 

				"life_regen_per_wisdom", 

				"cold_per_precision", 
				"lightning_per_swiftness", 
				"fire_per_toughness", 

				"damage_per_swiftness", 
				"damage_per_precision", 
				"damage_per_toughness", 

				"dot_damage_per_precision", 
				"projectile_speed_per_swiftness", 

				"extra_physical_as_lightning_per_swiftness", 
				"extra_physical_as_cold_per_precision", 
				"extra_physical_as_fire_per_toughness", 

				"aoe_per_precision", 
				"aoe_per_swiftness", 
				"aoe_per_toughness", 

				"crit_multi_per_precision", 
				"armor_per_toughness", 
				"health_regen_percent_toughness_boon", 

				
				"increased_duration", 
				"self_duration", 
				"incoming_damage", 
				"curse_effect", 
				"aura_effect", 
				"radius", 

				
				"conversion_physical_to_lightning", 
				"conversion_physical_to_cold", 
				"conversion_physical_to_fire", 
				"conversion_physical_to_toxic", 
				"conversion_lightning_to_cold", 
				"conversion_lightning_to_fire", 
				"conversion_lightning_to_toxic", 
				"conversion_cold_to_fire", 
				"conversion_cold_to_toxic", 
				"conversion_fire_to_toxic", 

				
				"extra_physical_as_lightning", 
				"extra_physical_as_cold", 
				"extra_physical_as_fire", 
				"extra_physical_as_toxic", 
				"extra_lightning_as_cold", 
				"extra_lightning_as_fire", 
				"extra_lightning_as_toxic", 
				"extra_cold_as_fire", 
				"extra_cold_as_toxic", 
				"extra_fire_as_toxic", 

				"extra_cold_as_fire_against_frozen", 
				"extra_cold_as_fire_against_chilled", 
				"extra_lightning_as_cold_against_electrocuted", 


				
				"physical_taken_as_lightning", 
				"physical_taken_as_cold", 
				"physical_taken_as_fire", 
				"physical_taken_as_toxic", 
				"lightning_taken_as_cold", 
				"lightning_taken_as_fire", 
				"lightning_taken_as_toxic", 
				"cold_taken_as_fire", 
				"cold_taken_as_toxic", 
				"fire_taken_as_toxic", 






]

var taken_as_list = [
				"physical_taken_as_lightning", 
				"physical_taken_as_cold", 
				"physical_taken_as_fire", 
				"physical_taken_as_toxic", 
				"lightning_taken_as_cold", 
				"lightning_taken_as_fire", 
				"lightning_taken_as_toxic", 
				"cold_taken_as_fire", 
				"cold_taken_as_toxic", 
				"fire_taken_as_toxic"
]

var attribute_list = [
				"constitution", 
				"strength", 
				"agility", 
				"wisdom", 
				"finesse", 
				"damage_per_25_attributes", 
				"physical_per_25_strength", 
				"lightning_per_25_agility", 
				"fire_per_25_constitution", 
				"cold_per_25_wisdom", 
				"toxic_per_25_finesse", 
				"life_regen_per_wisdom"
]

var boon_list = [
				"health_regen_percent_toughness_boon", 
				"damage_per_boon", 
]

var tags_for_stat = {
				"health_max": [Tags.LIFE, Tags.DEFENCE], 
				"health_regen": [Tags.LIFE, Tags.DEFENCE], 
				"health_regen_percent": [Tags.LIFE, Tags.DEFENCE], 
				"health_recovery_rate": [Tags.LIFE, Tags.DEFENCE], 
				"constitution": [Tags.ATTRIBUTE], 
				"strength": [Tags.ATTRIBUTE], 
				"agility": [Tags.ATTRIBUTE], 
				"wisdom": [Tags.ATTRIBUTE], 
				"finesse": [Tags.ATTRIBUTE], 
				"swiftness_boon": [Tags.BOON], 
				"precision_boon": [Tags.BOON], 
				"toughness_boon": [Tags.BOON], 
				"movement_speed": [Tags.SPEED], 
				"projectile_speed": [Tags.SPEED, Tags.PROJECTILE], 
				"projectile_count": [Tags.PROJECTILE], 
				"area_of_effect": [], 
				"skill_pierce": [], 
				"skill_chain": [], 
				"crit_chance": [Tags.CRITICAL], 
				"crit_multi": [Tags.CRITICAL], 
				"cast_speed": [Tags.SPEED], 

				
				"all_damage": [Tags.DAMAGE], 

				
				"projectile_damage": [Tags.DAMAGE, Tags.PROJECTILE], 
				"area_damage": [Tags.DAMAGE], 
				"dot_damage": [Tags.DAMAGE], 
				"hit_damage": [Tags.DAMAGE], 

				
				"physical_damage": [Tags.DAMAGE, Tags.PHYSICAL], 
				"lightning_damage": [Tags.DAMAGE, Tags.LIGHTNING], 
				"cold_damage": [Tags.DAMAGE, Tags.COLD], 
				"fire_damage": [Tags.DAMAGE, Tags.FIRE], 
				"toxic_damage": [Tags.DAMAGE, Tags.TOXIC], 

				
				"physical_resistance": [Tags.RESISTANCE, Tags.PHYSICAL], 
				"lightning_resistance": [Tags.RESISTANCE, Tags.LIGHTNING], 
				"cold_resistance": [Tags.RESISTANCE, Tags.COLD], 
				"fire_resistance": [Tags.RESISTANCE, Tags.FIRE], 
				"toxic_resistance": [Tags.RESISTANCE, Tags.TOXIC], 
				"maximum_physical_resistance": [Tags.RESISTANCE, Tags.PHYSICAL], 
				"maximum_lightning_resistance": [Tags.RESISTANCE, Tags.LIGHTNING], 
				"maximum_cold_resistance": [Tags.RESISTANCE, Tags.COLD], 
				"maximum_fire_resistance": [Tags.RESISTANCE, Tags.FIRE], 
				"maximum_toxic_resistance": [Tags.RESISTANCE, Tags.TOXIC], 
				"curse_resistance": [Tags.RESISTANCE, Tags.AILMENT], 
				"mitigation": [Tags.DEFENCE], 
				"evasion": [Tags.DEFENCE], 
				"block_chance": [Tags.DEFENCE], 
				"life_gain_on_block": [Tags.DEFENCE, Tags.LIFE], 
				"life_gain_on_hit": [Tags.LIFE], 
				"ailment_avoidance": [Tags.DEFENCE, Tags.AILMENT], 

				
				"physical_penetration": [Tags.PHYSICAL], 
				"lightning_penetration": [Tags.LIGHTNING], 
				"cold_penetration": [Tags.COLD], 
				"fire_penetration": [Tags.FIRE], 
				"toxic_penetration": [Tags.TOXIC], 

				"physical_ailment_effect": [Tags.PHYSICAL, Tags.AILMENT], 
				"lightning_ailment_effect": [Tags.LIGHTNING, Tags.AILMENT], 
				"cold_ailment_effect": [Tags.COLD, Tags.AILMENT], 
				"fire_ailment_effect": [Tags.FIRE, Tags.AILMENT], 
				"toxic_ailment_effect": [Tags.TOXIC, Tags.AILMENT], 

				"physical_ailment_chance": [Tags.PHYSICAL, Tags.AILMENT], 
				"lightning_ailment_chance": [Tags.LIGHTNING, Tags.AILMENT], 
				"cold_ailment_chance": [Tags.COLD, Tags.AILMENT], 
				"fire_ailment_chance": [Tags.FIRE, Tags.AILMENT], 
				"toxic_ailment_chance": [Tags.TOXIC, Tags.AILMENT], 

				"ailment_duration": [Tags.DURATION, Tags.AILMENT], 
				"amplify_ailment_chance": [Tags.AILMENT], 

				
				"increased_duration": [Tags.DURATION], 
				"self_duration": [Tags.DURATION], 
				"incoming_damage": [Tags.DAMAGE], 
				"curse_effect": [Tags.AILMENT], 
}

var effect_for_chance = {
				"physical_ailment_chance": "physical_ailment_effect", 
				"lightning_ailment_chance": "lightning_ailment_effect", 
				"cold_ailment_chance": "cold_ailment_effect", 
				"fire_ailment_chance": "fire_ailment_effect", 
				"toxic_ailment_chance": "toxic_ailment_effect", 
}


var type_for_chance = {
				"physical_ailment_chance": SkillTags.Tags.PHYSICAL, 
				"lightning_ailment_chance": SkillTags.Tags.LIGHTNING, 
				"cold_ailment_chance": SkillTags.Tags.COLD, 
				"fire_ailment_chance": SkillTags.Tags.FIRE, 
				"toxic_ailment_chance": SkillTags.Tags.TOXIC, 
}

var type_for_penetration = {
				"physical_penetration": SkillTags.Tags.PHYSICAL, 
				"lightning_penetration": SkillTags.Tags.LIGHTNING, 
				"cold_penetration": SkillTags.Tags.COLD, 
				"fire_penetration": SkillTags.Tags.FIRE, 
				"toxic_penetration": SkillTags.Tags.TOXIC, 
}

var stat_name = {
				"health_max": "Maximum Life", 
				"health_regen": "Life Regeneration", 
				"health_regen_percent": "Maximum Life Regeneration", 
				"health_recovery_rate": "Life Regeneration Rate", 
				"constitution": "Constitution", 
				"strength": "Strength", 
				"agility": "Agility", 
				"wisdom": "Wisdom", 
				"finesse": "Finesse", 
				"swiftness_boon": "Max Swiftness Boons", 
				"precision_boon": "Max Precision Boons", 
				"toughness_boon": "Max Toughness Boons", 
				"boon_duration": "Boon Duration", 
				"projectile_count": "Projectiles", 
				"movement_speed": "Movement Speed", 
				"projectile_speed": "Projectile Speed", 
				"cast_speed": "Cast Speed", 
				"mitigation": "Armor", 
				"evasion": "Evasion", 

				"crit_chance": "Critical Strike Chance", 
				"crit_multi": "Critical Strike Damage Multiplier", 

				
				"physical_resistance": "Physical Resistance", 
				"lightning_resistance": "Lightning Resistance", 
				"cold_resistance": "Cold Resistance", 
				"fire_resistance": "Fire Resistance", 
				"toxic_resistance": "Toxic Resistance", 

				"maximum_physical_resistance": "Maximum Physical Resistance", 
				"maximum_lightning_resistance": "Maximum Lightning Resistance", 
				"maximum_cold_resistance": "Maximum Cold Resistance", 
				"maximum_fire_resistance": "Maximum Fire Resistance", 
				"maximum_toxic_resistance": "Maximum Toxic Resistance", 

				"curse_resistance": "Curse Resistance", 
				"block_chance": "Block Chance", 
				"life_gain_on_block": "Life Gain On Block", 
				"life_gain_on_hit": "Life Gain On Hit", 
				"ailment_avoidance": "Ailment Avoidance", 
				"crit_resistance": "Critical Resistance", 

				
				"all_damage": "Damage", 
				"damage_per_boon": "Damage Per Boon", 
				"damage_per_25_attributes": "Damage per 25 Total Attributes", 
				"projectile_damage": "Projectile Damage", 
				"area_damage": "Area Damage", 
				"dot_damage": "Damage Over Time Multiplier", 
				"hit_damage": "Hit Damage", 

				"physical_damage": "Physical Damage", 
				"lightning_damage": "Lightning Damage", 
				"cold_damage": "Cold Damage", 
				"fire_damage": "Fire Damage", 
				"toxic_damage": "Toxic Damage", 

				
				"physical_penetration": "Physical Penetration", 
				"lightning_penetration": "Lightning Penetration", 
				"cold_penetration": "Cold Penetration", 
				"fire_penetration": "Fire Penetration", 
				"toxic_penetration": "Toxic Penetration", 
				"elemental_penetration": "Elemental Penetration", 

				

				"physical_ailment_effect": "Physical Ailment Effect", 
				"lightning_ailment_effect": "Lightning Ailment Effect", 
				"cold_ailment_effect": "Cold Ailment Effect", 
				"fire_ailment_effect": "Fire Ailment Effect", 
				"toxic_ailment_effect": "Toxic Ailment Effect", 

				"physical_ailment_chance": "Physical Ailment Chance", 
				"lightning_ailment_chance": "Lightning Ailment Chance", 
				"cold_ailment_chance": "Cold Ailment Chance", 
				"fire_ailment_chance": "Fire Ailment Chance", 
				"toxic_ailment_chance": "Toxic Ailment Chance", 

				"ailment_duration": "Ailment Duration", 
				"amplify_ailment_chance": "Enhanced Ailment Chance", 

				"vulnerable_chance": "Chance to apply Vulnerable on Hit", 
				"vulnerable_effect": "Vulnerable Effect", 

				"exposure_chance": "Chance to apply Exposure on Hit", 
				"exposure_effect": "Exposure Effect", 

				
				"infection_count": "Infection Spread Count", 

				"swiftness_boon_on_hit_chance": "Chance to gain Swiftness Boon on Hit", 
				"toughness_boon_on_hit_chance": "Chance to gain Toughness Boon on Hit", 

				"precision_boon_on_crit_chance": "Chance to gain Precision Boon on Crit", 
				"toughness_boon_on_get_hit_chance": "Chance to gain Toughness Boon when Hit", 

				"swiftness_boon_on_kill_chance": "Chance to gain Swiftness Boon on Kill", 
				"precision_boon_on_kill_chance": "Chance to gain Precision Boon on Kill", 
				"toughness_boon_on_kill_chance": "Chance to gain Toughness Boon on Kill", 

				"extra_physical_as_lightning_per_swiftness": "Physical Damage as Extra Added Lightning Damage per Swiftness Boon", 
				"extra_physical_as_cold_per_precision": "Physical Damage as Extra Added Cold Damage per Precision Boon", 
				"extra_physical_as_fire_per_toughness": "Physical Damage as Extra Added Fire Damage per Toughness Boon", 

				"aoe_per_precision": "Increased Area of Effect per Precision Boon", 
				"aoe_per_swiftness": "Increased Area of Effect per Swiftness Boon", 
				"aoe_per_toughtness": "Increased Area of Effect per Toughness Boon", 

				"physical_per_25_strength": "Physical Damage per 25 Strength", 
				"lightning_per_25_agility": "Lightning Damage per 25 Agility", 
				"fire_per_25_constitution": "Fire Damage per 25 Constitution", 
				"cold_per_25_wisdom": "Cold Damage per 25 Wisdom", 
				"toxic_per_25_finesse": "Toxic Damage per 25 Finesse", 
				"life_regen_per_wisdom": "Life Regeneration per second Per Wisdom", 

				"cold_per_precision": "Cold Damage per Precision Boon", 
				"lightning_per_swiftness": "Lightning Damage per Swiftness Boon", 
				"fire_per_toughness": "Fire Damage per Toughness Boon", 

				"damage_per_swiftness": "Damage per Swiftness Boon", 
				"damage_per_precision": "Damage per Precision Boon", 
				"damage_per_toughness": "Damage per Toughness Boon", 
				"crit_multi_per_precision": "Critical Strike Multiplier per Precision Boon", 
				"dot_damage_per_precision": "Damage Over Time Multiplier per Precision Boon", 
				"projectile_speed_per_swiftness": "Projectile Speed per Swiftness Boon", 
				"armor_per_toughness": "Armor per Toughness Boon", 
				"health_regen_percent_toughness_boon": "Maximum Health Regenerated Per Second Per Toughness Boon", 

				"damage": "Damage", 
				"skill_effectiveness": "Skill Damage Effectiveness", 
				"damage_effectiveness": "Added Damage Effectiveness", 
				"skill_pierce": "Pierce", 
				"skill_chain": "Chain", 
				"base_duration": "Skill Duration", 
				"cooldown": "Skill Cooldown", 
				"increased_duration": "Skill Duration", 
				"area_of_effect": "Area of Effect", 
				"self_duration": "Buff Duration", 
				"incoming_damage": "Damage Received", 
				"radius": "Skill Radius", 
				"curse_effect": "Curse Effect", 
				"aura_effect": "Aura Effect", 

				"conversion_physical_to_lightning": "Physical Damage Converted to Lightning Damage", 
				"conversion_physical_to_cold": "Physical Damage Converted to Cold Damage", 
				"conversion_physical_to_fire": "Physical Damage Converted to Fire Damage", 
				"conversion_physical_to_toxic": "Physical Damage Converted to Toxic Damage", 
				"conversion_lightning_to_cold": "Lightning Damage Converted to Cold Damage", 
				"conversion_lightning_to_fire": "Lightning Damage Converted to Fire Damage", 
				"conversion_lightning_to_toxic": "Lightning Damage Converted to Toxic Damage", 
				"conversion_cold_to_fire": "Cold Damage Converted to Fire Damage", 
				"conversion_cold_to_toxic": "Cold Damage Converted to Toxic Damage", 
				"conversion_fire_to_toxic": "Fire Damage Converted to Toxic Damage", 

				"extra_physical_as_lightning": "Physical Damage as Extra Added Lightning Damage", 
				"extra_physical_as_cold": "Physical Damage as Extra Added Cold Damage", 
				"extra_physical_as_fire": "Physical Damage as Extra Added Fire Damage", 
				"extra_physical_as_toxic": "Physical Damage as Extra Added Toxic Damage", 
				"extra_lightning_as_cold": "Lightning Damage as Extra Added Cold Damage", 
				"extra_lightning_as_fire": "Lightning Damage as Extra Added Fire Damage", 
				"extra_lightning_as_toxic": "Lightning Damage as Extra Added Toxic Damage", 
				"extra_cold_as_fire": "Cold Damage as Extra Added Fire Damage", 
				"extra_cold_as_toxic": "Cold Damage as Extra Added Toxic Damage", 
				"extra_fire_as_toxic": "Fire Damage as Extra Added Toxic Damage", 

				"physical_taken_as_lightning": "Physical Damage taken as Lightning Damage", 
				"physical_taken_as_cold": "Physical Damage taken as Cold Damage", 
				"physical_taken_as_fire": "Physical Damage taken as Fire Damage", 
				"physical_taken_as_toxic": "Physical Damage taken as Toxic Damage", 
				"lightning_taken_as_cold": "Lightning Damage taken as Cold Damage", 
				"lightning_taken_as_fire": "Lightning Damage taken as Fire Damage", 
				"lightning_taken_as_toxic": "Lightning Damage taken as Toxic Damage", 
				"cold_taken_as_fire": "Cold Damage taken as Fire Damage", 
				"cold_taken_as_toxic": "Cold Damage taken as Toxic Damage", 
				"fire_taken_as_toxic": "Fire Damage taken as Toxic Damage", 

				"extra_cold_as_fire_against_frozen": "Cold Damage as Extra Added Fire Damage against Frozen Enemies", 
				"extra_cold_as_fire_against_chilled": "Cold Damage as Extra Added Fire Damage against Chilled Enemies", 
				"extra_lightning_as_cold_against_electrocuted": "Lightning Damage as Extra Added Cold Damage against Electrocuted Enemies", 
}

var defaults = {
				"health_max": 100, 
				"health_regen": 0.0, 
				"health_regen_percent": 0.0, 
				"health_recovery_rate": 1.0, 
				"constitution": 0, 
				"strength": 0, 
				"agility": 0, 
				"wisdom": 0, 
				"finesse": 0, 
				"swiftness_boon": 3, 
				"precision_boon": 3, 
				"toughness_boon": 3, 
				"boon_duration": 1.0, 
				"health_regen_percent_toughness_boon": 0.0, 
				"damage_per_boon": 0.0, 
				"projectile_count": 0, 
				"movement_speed": 90.0, 
				"crit_chance": 0, 
				"crit_multi": 1.5, 
				"projectile_speed": 1.0, 
				"cast_speed": 1.0, 
				"physical_resistance": 0.0, 
				"lightning_resistance": 0.0, 
				"cold_resistance": 0.0, 
				"fire_resistance": 0.0, 
				"toxic_resistance": 0.0, 
				"maximum_physical_resistance": 0.75, 
				"maximum_lightning_resistance": 0.75, 
				"maximum_cold_resistance": 0.75, 
				"maximum_fire_resistance": 0.75, 
				"maximum_toxic_resistance": 0.75, 
				"curse_resistance": 0.0, 
				"crit_resistance": 0.0, 
				"physical_penetration": 0.0, 
				"lightning_penetration": 0.0, 
				"cold_penetration": 0.0, 
				"fire_penetration": 0.0, 
				"toxic_penetration": 0.0, 
				"elemental_penetration": 0.0, 
				"mitigation": 0, 
				"evasion": 0, 
				"skill_pierce": 0, 
				"skill_chain": 0, 
				"all_damage": 1.0, 
				"physical_damage": 1.0, 
				"lightning_damage": 1.0, 
				"cold_damage": 1.0, 
				"fire_damage": 1.0, 
				"toxic_damage": 1.0, 
				"projectile_damage": 1.0, 
				"area_damage": 1.0, 
				"dot_damage": 1.0, 
				"hit_damage": 1.0, 
				"physical_ailment_effect": 1.0, 
				"lightning_ailment_effect": 1.0, 
				"cold_ailment_effect": 1.0, 
				"fire_ailment_effect": 1.0, 
				"toxic_ailment_effect": 1.0, 
				"physical_ailment_chance": 0.0, 
				"lightning_ailment_chance": 0.0, 
				"cold_ailment_chance": 0.0, 
				"fire_ailment_chance": 0.0, 
				"toxic_ailment_chance": 0.0, 
				"ailment_duration": 1.0, 
				"amplify_ailment_chance": 0.0, 
				"vulnerable_chance": 0.0, 
				"vulnerable_effect": 1.0, 
				"exposure_chance": 0.0, 
				"exposure_effect": 1.0, 
				"infection_count": 1, 
				"swiftness_boon_on_hit_chance": 0.0, 
				"toughness_boon_on_hit_chance": 0.0, 
				"precision_boon_on_crit_chance": 0.0, 
				"toughness_boon_on_get_hit_chance": 0.0, 
				"swiftness_boon_on_kill_chance": 0.0, 
				"precision_boon_on_kill_chance": 0.0, 
				"toughness_boon_on_kill_chance": 0.0, 
				"physical_per_25_strength": 0.0, 
				"lightning_per_25_agility": 0.0, 
				"fire_per_25_constitution": 0.0, 
				"cold_per_25_wisdom": 0.0, 
				"toxic_per_25_finesse": 0.0, 
				"life_regen_per_wisdom": 0.0, 
				"damage_per_25_attributes": 0.0, 
				"cold_per_precision": 0.0, 
				"lightning_per_swiftness": 0.0, 
				"fire_per_toughness": 0.0, 
				"damage_per_swiftness": 0.0, 
				"damage_per_precision": 0.0, 
				"damage_per_toughness": 0.0, 
				"extra_physical_as_lightning_per_swiftness": 0.0, 
				"extra_physical_as_cold_per_precision": 0.0, 
				"extra_physical_as_fire_per_toughness": 0.0, 
				"aoe_per_precision": 0.0, 
				"aoe_per_swiftness": 0.0, 
				"aoe_per_toughness": 0.0, 
				"crit_multi_per_precision": 0.0, 
				"dot_damage_per_precision": 0.0, 
				"projectile_speed_per_swiftness": 0.0, 
				"armor_per_toughness": 0.0, 
				"block_chance": 0.0, 
				"life_gain_on_block": 0.0, 
				"life_gain_on_hit": 0.0, 
				"ailment_avoidance": 0.0, 
				"duration": 1.0, 
				"increased_duration": 0.0, 
				"area_of_effect": 1.0, 
				"radius": 0.0, 
				"self_duration": 1.0, 
				"incoming_damage": 1.0, 
				"curse_effect": 0.0, 
				"aura_effect": 1.0, 
				"conversion_physical_to_lightning": 0.0, 
				"conversion_physical_to_cold": 0.0, 
				"conversion_physical_to_fire": 0.0, 
				"conversion_physical_to_toxic": 0.0, 
				"conversion_lightning_to_cold": 0.0, 
				"conversion_lightning_to_fire": 0.0, 
				"conversion_lightning_to_toxic": 0.0, 
				"conversion_cold_to_fire": 0.0, 
				"conversion_cold_to_toxic": 0.0, 
				"conversion_fire_to_toxic": 0.0, 

				
				"extra_physical_as_lightning": 0.0, 
				"extra_physical_as_cold": 0.0, 
				"extra_physical_as_fire": 0.0, 
				"extra_physical_as_toxic": 0.0, 
				"extra_lightning_as_cold": 0.0, 
				"extra_lightning_as_fire": 0.0, 
				"extra_lightning_as_toxic": 0.0, 
				"extra_cold_as_fire": 0.0, 
				"extra_cold_as_toxic": 0.0, 
				"extra_fire_as_toxic": 0.0, 

				"physical_taken_as_lightning": 0.0, 
				"physical_taken_as_cold": 0.0, 
				"physical_taken_as_fire": 0.0, 
				"physical_taken_as_toxic": 0.0, 
				"lightning_taken_as_cold": 0.0, 
				"lightning_taken_as_fire": 0.0, 
				"lightning_taken_as_toxic": 0.0, 
				"cold_taken_as_fire": 0.0, 
				"cold_taken_as_toxic": 0.0, 
				"fire_taken_as_toxic": 0.0, 

				"extra_cold_as_fire_against_frozen": 0.0, 
				"extra_cold_as_fire_against_chilled": 0.0, 
				"extra_lightning_as_cold_against_electrocuted": 0.0, 
}

var flat_stat_renders_regex = [
				"health", 
				"constitution", 
				"strength", 
				"agility", 
				"wisdom", 
				"finesse", 
				"mitigation", 
				"evasion", 
				"pierce", 
				"chain", 
				"boon", 
				"movement", 
				"radius", 
				"projectile_count", 
				"life_gain_on_block", 
				"life_gain_on_hit", 
]

var percent_render_regex = [
				"skill_effectiveness", 
				"damage_effectiveness", 
				"health_regen_percent", 
				"health_recovery_rate", 
				"health_regen_percent_toughness_boon", 
				"damage_per_swiftness", 
				"damage_per_precision", 
				"damage_per_toughness", 
				"cast_speed", 
				"resistance", 
				"chance", 
				"crit_multi", 
				"effect", 
				"penetration", 
				"avoidance", 
				"boon_duration", 
				"taken_as", 
]

var duration_regex = [
				"duration", 
				"cooldown"
]

func _ready() -> void :
				for stat in stat_list:
								valid_stat_cache[stat] = true

func is_stat_valid(stat):
				return valid_stat_cache.has(stat)

func render_skill_stat_line(stat, amount):
				for s in percent_render_regex:
								if s in stat:
												if s == "chance":
																return str(stepify(amount * 100.0, 0.01)) + "%"
												else:
																return str(round(amount * 100.0)) + "%"
				for s in duration_regex:
								if s in stat:
												return str(stepify(amount, 0.01)) + "s"
				return str(stepify(amount, 0.1))


func render_stat_name(stat, type, tags = null):
				var tag_postfix = ""
				if tags:
								tag_postfix = render_tag_mods(tags)
				if type == Constants.ScalingType.FLAT:
								if "resistance" in stat or "penetration" in stat or "ailment_effect" in stat or "crit_multi" in stat or "percent" in stat or "avoidance" in stat or "conversion" in stat or "extra" in stat or "taken_as" in stat:
												return stat_name[stat] + tag_postfix
								elif "chance" in stat:
												return stat_name[stat] + tag_postfix
								elif "damage" in stat:
												return "Added " + stat_name[stat] + tag_postfix
								else:
												return stat_name[stat] + tag_postfix
				if type == Constants.ScalingType.PERCENT:
								return "Increased " + stat_name[stat] + tag_postfix
				if type == Constants.ScalingType.MORE:
								return "More " + stat_name[stat] + tag_postfix

func render_passive_stat_line(stat, mod):
				var type = mod.scaling_type
				var amount = mod.amount
				var stepified = 0.1
				if mod.has(stepified):
								stepified = mod.stepified
				var tag_postfix = ""
				if mod.has("tags") and len(mod.tags) > 0:
								tag_postfix = render_tag_mods(mod.tags)
				if type == Constants.ScalingType.FLAT:
								if ("resistance" in stat or "penetration" in stat or "ailment_effect" in stat or "crit_multi" in stat or "percent" in stat or "avoidance" in stat or "conversion" in stat or "extra" in stat) and not ("maximum" in stat) or "taken_as" in stat:
												return str(stepify(amount * 100, stepified)) + "% " + stat_name[stat] + tag_postfix
								elif "chance" in stat or "maximum" in stat:
												if amount >= 0:
																return "+" + str(stepify(amount * 100, stepified)) + "% " + stat_name[stat] + tag_postfix
												else:
																return str(stepify(amount * 100, stepified)) + "% " + stat_name[stat] + tag_postfix
								elif "radius" in stat:
												if amount >= 0:
																return "+" + str(stepify(amount, stepified)) + " " + stat_name[stat] + tag_postfix
												else:
																return str(stepify(amount, stepified)) + " " + stat_name[stat] + tag_postfix
								elif "damage" in stat:
												return str(stepify(amount, stepified)) + " Added " + stat_name[stat] + tag_postfix
								else:
												return "+" + str(stepify(amount, 1)) + " " + stat_name[stat] + tag_postfix
				if type == Constants.ScalingType.PERCENT:
								if amount >= 0:
												return str(round(amount * 100)) + "% Increased " + stat_name[stat] + tag_postfix
								else:
												return str(abs(round(amount * 100))) + "% Reduced " + stat_name[stat] + tag_postfix
				if type == Constants.ScalingType.MORE:
								if amount >= 0:
												return str(round(amount * 100)) + "% More " + stat_name[stat] + tag_postfix
								else:
												return str(abs(round(amount * 100))) + "% Less " + stat_name[stat] + tag_postfix

func render_formatted_number(amount, stat, type):
				if type == Constants.ScalingType.FLAT:
								if "resistance" in stat or "penetration" in stat or "ailment_effect" in stat or "crit_multi" in stat or "percent" in stat or "avoidance" in stat or "conversion" in stat or "extra" in stat or "taken_as" in stat:
												return str(stepify(amount * 100, 0.1)) + "%"
								elif "chance" in stat:
												return str(stepify(amount * 100, 0.1)) + "%"
								else:
												return str(amount)
				if type == Constants.ScalingType.PERCENT:
								if amount >= 0:
												return str(round(amount * 100)) + "%"
								else:
												return "-" + str(abs(round(amount * 100))) + "%"
				if type == Constants.ScalingType.MORE:
								if amount >= 0:
												return str(round(amount * 100)) + "%"
								else:
												return "-" + str(abs(round(amount * 100))) + "%"

func render_item_stat_line(stat, mod, quality = 1.0):
				var type = mod.type
				var amount = mod.amount * quality
				var stepified = 0.1
				if mod.has(stepified):
								stepified = mod.stepified
				var tag_postfix = ""
				if mod.has("tags") and len(mod.tags) > 0:
								tag_postfix = render_tag_mods(mod.tags)
				if type == Constants.ScalingType.FLAT:
								if "resistance" in stat or "penetration" in stat or "ailment_effect" in stat or "crit_multi" in stat or "percent" in stat or "avoidance" in stat or "conversion" in stat or "extra" in stat:
												return str(stepify(amount * 100, stepified)) + "% " + stat_name[stat] + tag_postfix
								elif "chance" in stat:
												if amount >= 0:
																return "+" + str(stepify(amount * 100, stepified)) + "% " + stat_name[stat] + tag_postfix
												else:
																	return str(stepify(amount * 100, stepified)) + "% " + stat_name[stat] + tag_postfix
								elif "radius" in stat:
												if amount >= 0:
																return "+" + str(stepify(amount, stepified)) + " " + stat_name[stat] + tag_postfix
												else:
																	return str(stepify(amount, stepified)) + " " + stat_name[stat] + tag_postfix
								elif "damage" in stat:
												return str(stepify(amount, stepified)) + " Added " + stat_name[stat] + tag_postfix
								else:
												if amount >= 0:
																return str(amount) + " " + stat_name[stat] + tag_postfix
												else:
																return str(amount) + " " + stat_name[stat] + tag_postfix
				if type == Constants.ScalingType.PERCENT:
								if amount >= 0:
												return str(amount * 100) + "% Increased " + stat_name[stat] + tag_postfix
								else:
												return str(abs(amount) * 100) + "% Reduced " + stat_name[stat] + tag_postfix
				if type == Constants.ScalingType.MORE:
								if amount >= 0:
												return str(amount * 100) + "% More " + stat_name[stat] + tag_postfix
								else:
												return str(abs(amount) * 100) + "% Less " + stat_name[stat] + tag_postfix

func render_range_into_rtl(stat, mod, tier, control: RichTextLabel):
				var type = mod.type
				var active_tier = mod.tiers[tier]
				var min_string = active_tier.range.min_formatted
				var max_string = active_tier.range.max_formatted
				var tag_postfix = ""
				if mod.has("tags") and len(mod.tags) > 0:
								tag_postfix = render_tag_mods(mod.tags)
				if type == Constants.ScalingType.FLAT:
								if "resistance" in stat or "penetration" in stat or "ailment_effect" in stat or "crit_multi" in stat or "percent" in stat or "avoidance" in stat or "conversion" in stat or "extra" in stat:
												control.add_text(min_max(min_string, max_string) + " " + stat_name[stat] + tag_postfix)
								elif "chance" in stat:
												control.add_text(min_max(min_string, max_string) + " " + stat_name[stat] + tag_postfix)
								elif "radius" in stat:
												control.add_text(min_max(min_string, max_string) + " " + stat_name[stat] + tag_postfix)
								elif "damage" in stat:
												control.add_text(min_max(min_string, max_string) + " Added " + stat_name[stat] + tag_postfix)
								else:
												control.add_text(min_max(min_string, max_string) + " " + stat_name[stat] + tag_postfix)
				if type == Constants.ScalingType.PERCENT:
								control.add_text(min_max(min_string, max_string) + " Increased " + stat_name[stat] + tag_postfix)
				if type == Constants.ScalingType.MORE:
								control.add_text(min_max(min_string, max_string) + " More " + stat_name[stat] + tag_postfix)

func render_character_stat_line(stat, amount, stats, show_capped = true):
				if show_capped:
								if stat == "mitigation":
												return str(round(amount)) + " (" + str(round(100.0 * (1.0 - Mitigation.get_effective_mitigation(amount, GameState.get_account_level())))) + "%)"
								if stat == "evasion":
												return str(round(amount)) + " (" + str(round(100.0 * Mitigation.get_effective_evasion(amount, GameState.get_account_level()))) + "%)"

								
								if "resistance" in stat or "block_chance" in stat or "avoidance" in stat:
												var capped = stats.gs(stat)
												if "resistance" in stat or "avoidance" in stat:
																if "curse" in stat or "maximum" in stat or "crit" in stat or "avoidance" in stat:
																				capped = stats.cap_resistance(capped, 1.0)
																else:
																				capped = stats.cap_resistance(capped, stats.gs("maximum_" + stat))
												if "block_chance" in stat:
																capped = stats.cap_block(capped)
												var result = str(round(capped * 100.0)) + "%"
												if amount > capped:
																result += " (" + str(round(amount * 100.0)) + "%)"
												return result


				for s in percent_render_regex:
								if s in stat:
												return str(stepify(amount * 100.0, 0.1)) + "%"
				for s in flat_stat_renders_regex:
								if s in stat:
												return str(round(amount))



				return str(round(amount * 100.0)) + "%"

func render_character_select(stat, amount):
				for s in flat_stat_renders_regex:
								if s in stat:
												return str(round(amount))
				return str(round(amount * 100.0)) + "%"

func render_tag_mods(tags = null):
				if tags == null:
								return ""
				var result = " with " + SkillTags.tags_to_string(tags) + " Skills"
				return result

func min_max(mn, mx):
				if mn == mx:
								return mn
				return "(" + mn + " to " + mx + ")"
