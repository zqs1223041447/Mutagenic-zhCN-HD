extends Node

var extra_munitions_icon = preload("res://sprites/gui/skill_supports/extra_munitions.png")
var collateral_damage_icon = preload("res://sprites/gui/skill_supports/support_collateral_damage.png")
var sniper_icon = preload("res://sprites/gui/skill_supports/support_sniper.png")
var pierce_icon = preload("res://sprites/gui/skill_supports/support_pierce.png")
var projectile_speed_icon = preload("res://sprites/gui/skill_supports/support_projectile_speed.png")
var focus_icon = preload("res://sprites/gui/skill_supports/support_focus.png")


var cast_on_crit_icon = preload("res://sprites/gui/skill_supports/support_cast_on_crit.png")
var cast_on_kill_icon = preload("res://sprites/gui/skill_supports/support_cast_on_kill.png")
var volatility_icon = preload("res://sprites/gui/skill_supports/support_volatility.png")

var fire_icon = preload("res://sprites/gui/skill_supports/support_fire.png")
var chain_icon = preload("res://sprites/gui/skill_supports/support_chain.png")
var cold_icon = preload("res://sprites/gui/skill_supports/support_cold.png")
var toxic_icon = preload("res://sprites/gui/skill_supports/support_toxic.png")
var lightning_icon = preload("res://sprites/gui/skill_supports/support_lightning.png")
var physical_icon = preload("res://sprites/gui/skill_supports/support_physical.png")
var crit_icon = preload("res://sprites/gui/skill_supports/support_crit.png")
var ailment_icon = preload("res://sprites/gui/skill_supports/support_ailment.png")
var duration_icon = preload("res://sprites/gui/skill_supports/support_duration.png")
var cast_speed_icon = preload("res://sprites/gui/skill_supports/support_cast_speed.png")
var doom_icon = preload("res://sprites/gui/skill_supports/support_doom.png")
var aoe_icon = preload("res://sprites/gui/skill_supports/support_aoe.png")
var vulnerable_icon = preload("res://sprites/buff_icons/vulnerable.png")
var exposure_icon = preload("res://sprites/buff_icons/exposed.png")
var dot_icon = preload("res://sprites/gui/passives/dot.png")
var hamstrung_icon = preload("res://sprites/status_effects_new/hamstrung.png")
var proliferate_icon = preload("res://sprites/gui/skill_supports/support_proliferate.png")
var sacrifice_icon = preload("res://sprites/gui/skill_supports/support_sacrifice.png")

enum TRIGGER_FLAGS{
				CAST_ON_CRIT,
				CAST_ON_KILL,
				VOLATILE_CASTING,
}

var supports = {
				"extra_projectiles": {
								"name": "Extra Munitions", 
								"description": "Skill fires extra projectiles, each dealing less damage.", 
								"icon": extra_munitions_icon, 
								"tags": [SkillTags.Tags.PROJECTILE], 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.3, 
												}, 
												{
																"stat": "projectile_count", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}
								]
				}, 
				"snipe": {
								"name": "Sniper", 
								"description": "Projectiles fire with no spread.", 
								"icon": sniper_icon, 
								"tags": [SkillTags.Tags.PROJECTILE], 
								"stats": [
								], 
								"keystones": ["SUPPORT_SNIPER"]
				}, 
				"collateral_damage": {
								"name": "Collateral Damage", 
								"description": "Projectiles deal damage to nearby enemies on hit.", 
								"icon": collateral_damage_icon, 
								"tags": [SkillTags.Tags.PROJECTILE], 
								"stats": [
								], 
								"keystones": ["SUPPORT_COLLATERAL_DAMAGE"]
				}, 
				"extra_pierce": {
								"name": "Puncturing Shots", 
								"description": "Projectiles pierce enemies.", 
								"icon": pierce_icon, 
								"tags": [SkillTags.Tags.PROJECTILE], 
								"stats": [
												{
																"stat": "skill_pierce", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 3, 
												}
								]
				}, 
				"extra_chain": {
								"name": "Ricocheting Shots", 
								"description": "Projectiles that can chain to nearby enemies.", 
								"icon": chain_icon, 
								"tags": [SkillTags.Tags.CHAINING], 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.3, 
												}, 
												{
																"stat": "skill_chain", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}
								]
				}, 
				"quicker_projectiles": {
								"name": "Quicker Projectiles", 
								"description": "Projectiles travel with increased speed.", 
								"icon": projectile_speed_icon, 
								"tags": [SkillTags.Tags.PROJECTILE], 
								"stats": [
												{
																"stat": "projectile_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.3, 
												}
								]
				}, 
				"focus": {
								"name": "Focus", 
								"description": "Skill never deals Critical Strikes, but deals More Damage.", 
								"icon": focus_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 1.0, 
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.5, 
												}
								]
				}, 
				"proliferate": {
								"name": "Proliferation", 
								"description": "Elemental Ailments inflicted by this Skill also apply to 10 random nearby enemies.", 
								"icon": proliferate_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"keystones": ["SUPPORT_PROLIFERATE"], 
								"stats": []
				}, 
				"static_electricity": {
								"name": "Capacitor Discharging", 
								"description": "Inflict Lightning to nearby enemies when hitting Jolted enemies.", 
								"icon": lightning_icon, 
								"tags": [SkillTags.Tags.HIT, SkillTags.Tags.MELEE], 
								"keystones": ["SUPPORT_STATIC_ELECTRICITY"], 
								"stats": [
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"hamstring": {
								"name": "Hamstring", 
								"description": "Deal more Physical Damage with Melee Attacks, and inflicts Hamstrung for 4 seconds on hit.", 
								"icon": hamstrung_icon, 
								"keystones": ["SUPPORT_HAMSTRING"], 
								"tags": [SkillTags.Tags.HIT, SkillTags.Tags.MELEE], 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"increased_crit": {
								"name": "Critical Honing", 
								"description": "Skill has a higher chance to deal critical strikes.", 
								"icon": crit_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 1.25, 
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.015, 
												}
								]
				}, 
				"increased_crit_multi": {
								"name": "Critical Mass", 
								"description": "Skill deals more damage with critical strikes.", 
								"icon": crit_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1.0, 
												}, 
								]
				}, 
				"sacrifice": {
								"name": "Sacrifice", 
								"description": "Sacrifices Life to gain Added Physical Damage.", 
								"icon": sacrifice_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"keystones": ["SUPPORT_SACRIFICE"], 
								"stats": []
				}, 
				"physical_ailment": {
								"name": "Bloody", 
								"description": "Skill deals more damage with Bleeds and Ruptures, and has a higher chance to inflict Bleeds.", 
								"icon": physical_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"fire_ailment": {
								"name": "Ignition", 
								"description": "Skill deals more damage with Burns, and has a higher chance to inflict Burn.", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"cold_ailment": {
								"name": "Chilling", 
								"description": "Chills and Freezes inflicted have more effect.", 
								"icon": cold_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "cold_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"lightning_ailment": {
								"name": "Charged", 
								"description": "Jolts and Electrocutions inflicted have more effect.", 
								"icon": lightning_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"toxic_ailment": {
								"name": "Poison", 
								"description": "Skill deals more damage with Poisons and Infections, and has a higher chance to inflict Poisons.", 
								"icon": toxic_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "toxic_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"fast_hands": {
								"name": "Wizardry", 
								"description": "Skill is cast at a faster rate", 
								"icon": cast_speed_icon, 
								"tags": [SkillTags.Tags.CASTABLE], 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"physical_to_cold": {
								"name": "Cold Attuned", 
								"description": "Skill converts some Physical damage into Cold Damage", 
								"icon": cold_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "conversion_physical_to_cold", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"physical_to_lightning": {
								"name": "Shock Attuned", 
								"description": "Skill converts some Physical damage into Lightning Damage", 
								"icon": lightning_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "conversion_physical_to_lightning", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"physical_to_fire": {
								"name": "Fire Attuned", 
								"description": "Skill converts some Physical damage into Fire Damage", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "conversion_physical_to_fire", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"area_mastery": {
								"name": "Expansive", 
								"description": "Skill affects a larger area, and will deal more area damage", 
								"icon": aoe_icon, 
								"tags": [SkillTags.Tags.AREA], 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.AREA]
												}, 
								]
				}, 
				"more_physical_damage": {
								"name": "Physical Damage", 
								"description": "Skill deals more Physical Damage", 
								"icon": physical_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"more_lightning_damage": {
								"name": "Lightning Damage", 
								"description": "Skill deals more Lightning Damage", 
								"icon": lightning_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"more_cold_damage": {
								"name": "Cold Damage", 
								"description": "Skill deals more Cold Damage", 
								"icon": cold_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"more_fire_damage": {
								"name": "Fire Damage", 
								"description": "Skill deals more Fire Damage", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"more_toxic_damage": {
								"name": "Toxic Damage", 
								"description": "Skill deals more Toxic Damage", 
								"icon": toxic_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"physical_penetration": {
								"name": "Physical Penetration", 
								"description": "Physical Damage with skill penetrates Physical Resistance on enemies.", 
								"icon": physical_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "physical_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"lightning_penetration": {
								"name": "Lightning Penetration", 
								"description": "Lightning Damage with skill penetrates Lightning Resistance on enemies.", 
								"icon": lightning_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"cold_penetration": {
								"name": "Cold Penetration", 
								"description": "Cold Damage with skill penetrates Cold Resistance on enemies.", 
								"icon": cold_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"fire_penetration": {
								"name": "Fire Penetration", 
								"description": "Fire Damage with skill penetrates Fire Resistance on enemies.", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "fire_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"toxic_penetration": {
								"name": "Toxic Penetration", 
								"description": "Toxic Damage with skill penetrates Toxic Resistance on enemies.", 
								"icon": toxic_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "toxic_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"convert_lightning_to_cold": {
								"name": "Frigid Static", 
								"description": "Convert a portion of Lightning Damage into Cold Damage.", 
								"icon": cold_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "conversion_lightning_to_cold", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"gain_phys_as_fire": {
								"name": "Extra Fire", 
								"description": "Extra Fire Damage from Physical", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "extra_physical_as_fire", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.35, 
												}, 
								]
				}, 
				"convert_lightning_to_fire": {
								"name": "Burning Static", 
								"description": "Convert a portion of Lightning Damage into Fire Damage.", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "conversion_lightning_to_fire", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"convert_lightning_to_toxic": {
								"name": "Vile Static", 
								"description": "Convert a portion of Lightning Damage into Toxic Damage", 
								"icon": toxic_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "conversion_lightning_to_toxic", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"ailment_duration": {
								"name": "Ailment Duration", 
								"description": "Ailments inflicted by this skill last longer.", 
								"icon": ailment_icon, 
								"tags": [SkillTags.Tags.DAMAGING, SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"enhanced_ailments": {
								"name": "Enhanced Ailments", 
								"description": "Ailments inflicted by this skill have a chance to inflicted the enhanced version as well.", 
								"icon": ailment_icon, 
								"tags": [SkillTags.Tags.DAMAGING, SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"increased_duration": {
								"name": "Increased Duration", 
								"description": "Skill lasts longer.", 
								"icon": duration_icon, 
								"tags": [SkillTags.Tags.DURATION], 
								"stats": [
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.6, 
												}, 
								]
				}, 
				"damage_over_time": {
								"name": "Potent Suppression", 
								"description": "Damage over Time inflicted by this skill deal more damage.", 
								"icon": dot_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.3, 
												}, 
								]
				}, 
				"vulnerable": {
								"name": "Vulnerability", 
								"description": "Skill has a chance to inflict Vulnerable on hit, with increased effect.", 
								"icon": vulnerable_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "vulnerable_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "vulnerable_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"exposure": {
								"name": "Weakness", 
								"description": "Skill has a chance to inflict Exposure on hit, with increased effect.", 
								"icon": exposure_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "exposure_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "exposure_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
								]
				}, 

				
				"curse_effect": {
								"name": "Doomed", 
								"description": "Skill has more effect of curses.", 
								"icon": doom_icon, 
								"tags": [SkillTags.Tags.CURSE], 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.2, 
												}, 
								]
				}, 
				"curse_area": {
								"name": "Large Curses", 
								"description": "Skill has a larger area of effect of curses", 
								"icon": doom_icon, 
								"tags": [SkillTags.Tags.CURSE], 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								]
				}, 

				"physical_ailment_effect": {
								"name": "Lacerating", 
								"description": "Bleeds and Ruptures inflicted by this skill have increased effect.", 
								"icon": physical_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"fire_ailment_effect": {
								"name": "Scorched", 
								"description": "Burns and Chars inflicted by this skill have increased effect.", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"cold_ailment_effect": {
								"name": "Frigid", 
								"description": "Chills and Freezes inflicted by this skill have increased effect.", 
								"icon": cold_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"lightning_ailment_effect": {
								"name": "Stunner", 
								"description": "Jolts and Electrocutions inflicted by this skill have increased effect.", 
								"icon": lightning_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"toxic_ailment_effect": {
								"name": "Venom", 
								"description": "Poisons and Infections inflicted by this skill have increased effect.", 
								"icon": toxic_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								]
				}, 
				"strength_training": {
								"name": "Weightlifting", 
								"description": "Strength provides Added Physical Damage.", 
								"icon": physical_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "physical_per_25_strength", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
								]
				}, 
				"constitution_training": {
								"name": "Igni Study", 
								"description": "Constitution provides Added Fire Damage.", 
								"icon": fire_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "fire_per_25_constitution", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
								]
				}, 
				"wisdom_training": {
								"name": "Cryo Study", 
								"description": "Widsom provides Added Cold Damage.", 
								"icon": cold_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "cold_per_25_wisdom", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
								]
				}, 
				"arc_training": {
								"name": "Conductive Movement", 
								"description": "Agility provides Added Lightning Damage.", 
								"icon": lightning_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "lightning_per_25_agility", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
								]
				}, 
				"finesse_training": {
								"name": "Finessed Toxins", 
								"description": "Finesse provides Added Toxic Damage.", 
								"icon": toxic_icon, 
								"tags": [SkillTags.Tags.DAMAGING], 
								"stats": [
												{
																"stat": "toxic_per_25_finesse", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
								]
				}, 
				"infectious": {
								"name": "Infection", 
								"description": "Infections inflicted by this skill spread to more nearby enemies.", 
								"icon": toxic_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "infection_count", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}, 
								]
				}, 
				"cast_on_crit": {
								"name": "Cast on Crit", 
								"description": "Skill is cast when another skill inflicts a critical strike. Skill does not auto cast, and cannot trigger other skills. All Triggered skills have a 100ms cooldown.", 
								"icon": cast_on_crit_icon, 
								"tags": [SkillTags.Tags.TRIGGERABLE], 
								"keystones": ["SUPPORT_CAST_ON_CRIT"], 
								"is_triggered": true, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.2, 
												}, 
								]
				}, 
				"cast_on_kill": {
								"name": "Cast on Kill", 
								"description": "Skill has a 30% chance to cast when another skill inflicts a killing blow. Skill does not auto cast, and cannot trigger other skills. All Triggered skills have a 100ms cooldown.", 
								"icon": cast_on_kill_icon, 
								"tags": [SkillTags.Tags.TRIGGERABLE], 
								"keystones": ["SUPPORT_CAST_ON_KILL"], 
								"is_triggered": true, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 2.5, 
												}, 
								]
				}, 
				"volatility": {
								"name": "Volatility", 
								"description": "Skill is cast when hitting an enemy with any non-triggered skill. Skill consumes a random number of Boons to deal 20% more damage for each consumed Boon. Must have at least one active boon to cast. Skill does not auto cast, and cannot trigger other skills. All Triggered skills have a 100ms cooldown.", 
								"icon": volatility_icon, 
								"tags": [SkillTags.Tags.TRIGGERABLE], 
								"keystones": ["SUPPORT_VOLATILITY"], 
								"is_triggered": true, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"precision_boon_on_crit": {
								"name": "Precision Boon on Critical Strike", 
								"description": "Skill has a chance to grant a Precision Boon on crit.", 
								"icon": crit_icon, 
								"tags": [SkillTags.Tags.HIT], 
								"stats": [
												{
																"stat": "precision_boon_on_crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.75, 
												}, 
								]
				}, 
}


func get_filter_string(support):
				var string = ""
				var info = supports[support]
				string += info.name + " " + info.description + " "
				for tag in info.tags:
								string += SkillTags.TagNames[tag] + " "
				for stat in info.stats:
								var stat_info = StatsInfo.render_passive_stat_line(stat.stat, stat)
								string += " " + stat_info

				return string.to_lower()
