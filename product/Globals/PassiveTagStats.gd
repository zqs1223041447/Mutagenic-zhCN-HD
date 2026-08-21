extends Node

var life_tex = load("res://sprites/gui/passives/life.png")

var damage_tex = load("res://sprites/gui/passives/damage.png")
var physical_damage_tex = load("res://sprites/gui/passives/physical_damage.png")
var lightning_damage_tex = load("res://sprites/gui/passives/lightning_damage.png")
var cold_damage_tex = load("res://sprites/gui/passives/cold_damage.png")
var fire_damage_tex = load("res://sprites/gui/passives/fire_damage.png")
var toxic_damage_tex = load("res://sprites/gui/passives/toxic_damage.png")
var movement_tex = load("res://sprites/gui/passives/movement.png")
var armor_tex = load("res://sprites/gui/passives/armor.png")
var evasion_tex = load("res://sprites/gui/passives/evasion.png")

var resistance_tex = load("res://sprites/gui/passives/resistance.png")
var penetration_tex = load("res://sprites/gui/passives/penetration.png")
var curse_tex = load("res://sprites/gui/passives/curse.png")
var haste_tex = load("res://sprites/gui/passives/haste.png")
var pierce_tex = load("res://sprites/gui/passives/pierce.png")
var chain_tex = load("res://sprites/gui/passives/chain.png")
var aoe_tex = load("res://sprites/gui/passives/aoe.png")
var projectile_speed_tex = load("res://sprites/gui/passives/projectile_speed.png")
var duration_tex = load("res://sprites/gui/passives/duration.png")

var strength_tex = load("res://sprites/gui/passives/strength.png")
var agility_tex = load("res://sprites/gui/passives/agility.png")
var constitution_tex = load("res://sprites/gui/passives/constitution.png")
var finesse_tex = load("res://sprites/gui/passives/finesse.png")
var wisdom_tex = load("res://sprites/gui/passives/wisdom.png")

var conductive_tex = preload("res://sprites/buff_icons/conductive.png")
var burnt_tex = preload("res://sprites/buff_icons/burnt.png")


var bleed_tex = preload("res://sprites/status_effects/bleeding.png")
var rupture_tex = preload("res://sprites/status_effects/ruptured.png")

var jolt_tex = preload("res://sprites/status_effects/jolt.png")
var electrocute_tex = preload("res://sprites/status_effects/electrocuted.png")

var chill_tex = preload("res://sprites/status_effects/chilled.png")
var frozen_tex = preload("res://sprites/status_effects/frozen.png")

var burn_tex = preload("res://sprites/status_effects/burning.png")
var char_tex = preload("res://sprites/status_effects/charred.png")

var poisoned_tex = preload("res://sprites/status_effects/poison.png")
var infected_tex = preload("res://sprites/status_effects/infection.png")

var crit_tex = load("res://sprites/gui/passives/crit.png")
var bomb_tex = load("res://sprites/gui/passives/bomb.png")
var dot_tex = load("res://sprites/gui/passives/dot.png")
var block_tex = load("res://sprites/gui/passives/block.png")


var thunderstorm_tex = load("res://sprites/gui/passives/thunderstorm.png")
var goliath_tex = load("res://sprites/gui/passives/goliath.png")
var hit_attunement_tex = load("res://sprites/gui/passives/hit_attunement.png")
var ailment_tex = load("res://sprites/gui/passives/ailment.png")
var ailment_mastery_tex = load("res://sprites/gui/passives/ailment_mastery.png")

var swiftness_boon_tex = preload("res://sprites/status_effects/swiftness_boon.png")
var toughness_boon_tex = preload("res://sprites/status_effects/toughness_boon.png")
var precision_boon_tex = preload("res://sprites/status_effects/precision_boon.png")

var vulnerable_tex = preload("res://sprites/buff_icons/vulnerable.png")

var bonded_electrons_tex = preload("res://sprites/status_effects_new/bonded_electrons.png")

var stats = {
				
				"starter_node": {
								"name": "Initiate", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 20.0, 
												}
								]
				}, 
				
				"minor_strength": {
								"name": "Minor Strength", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": strength_tex, 
								"stats": [
												{
																"stat": "strength", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 10, 
												}
								]
				}, 
				"major_strength": {
								"name": "Major Strength", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": strength_tex, 
								"stats": [
												{
																"stat": "strength", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}
								]
				}, 
				"minor_constitution": {
								"name": "Minor Constitution", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": constitution_tex, 
								"stats": [
												{
																"stat": "constitution", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 10, 
												}
								]
				}, 
				"major_constitution": {
								"name": "Major Constitution", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": constitution_tex, 
								"stats": [
												{
																"stat": "constitution", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}
								]
				}, 
				"minor_agility": {
								"name": "Minor Agility", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": agility_tex, 
								"stats": [
												{
																"stat": "agility", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 10, 
												}
								]
				}, 
				"major_agility": {
								"name": "Major Agility", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": agility_tex, 
								"stats": [
												{
																"stat": "agility", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}
								]
				}, 
				"minor_wisdom": {
								"name": "Minor Wisdom", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": wisdom_tex, 
								"stats": [
												{
																"stat": "wisdom", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 10, 
												}
								]
				}, 
				"major_wisdom": {
								"name": "Major Wisdom", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": wisdom_tex, 
								"stats": [
												{
																"stat": "wisdom", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}
								]
				}, 
				"minor_finesse": {
								"name": "Minor Finesse", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": finesse_tex, 
								"stats": [
												{
																"stat": "finesse", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 10, 
												}
								]
				}, 
				"major_finesse": {
								"name": "Major Finesse", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": finesse_tex, 
								"stats": [
												{
																"stat": "finesse", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}
								]
				}, 


				
				"swiftness_on_hit": {
								"name": "Swiftness on Hit", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": swiftness_boon_tex, 
								"stats": [
												{
																"stat": "swiftness_boon_on_hit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}
								]
				}, 
				"toughness_boon_when_hit": {
								"name": "Toughness when Hit", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "toughness_boon_on_get_hit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}
								]
				}, 
				"max_precision_boons": {
								"name": "Precision Boon", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": precision_boon_tex, 
								"stats": [
												{
																"stat": "precision_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}
								]
				}, 
				"max_swiftness_boons": {
								"name": "Swiftness Boon", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": swiftness_boon_tex, 
								"stats": [
												{
																"stat": "swiftness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}
								]
				}, 
				"max_toughness_boons": {
								"name": "Toughness Boon", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "toughness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}
								]
				}, 

				"minor_damage_per_boon": {
								"name": "Boon Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "damage_per_boon", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
												}
								]
				}, 
				"major_damage_per_boon": {
								"name": "Boon Specialist", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "damage_per_boon", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.01, 
												}
								]
				}, 

				"damage_per_swiftness": {
								"name": "Swift Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": swiftness_boon_tex, 
								"stats": [
												{
																"stat": "damage_per_swiftness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								]
				}, 

				"damage_per_precision": {
								"name": "Precise Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": precision_boon_tex, 
								"stats": [
												{
																"stat": "damage_per_precision", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								]
				}, 

				"damage_per_toughness": {
								"name": "Tough Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "damage_per_toughness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								]
				}, 

				"multi_per_precision": {
								"name": "Precision Multiplier", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": precision_boon_tex, 
								"stats": [
												{
																"stat": "crit_multi_per_precision", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								]
				}, 

				"armor_per_toughness": {
								"name": "Tough Armor", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "armor_per_toughness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}
								]
				}, 

				"health_regen_per_toughness": {
								"name": "Regenerative Boons", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "health_regen_percent_toughness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.0025, 
												}
								]
				}, 

				
				"minor_damage": {
								"name": "Minor Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}
								]
				}, 
				"minor_health": {
								"name": "Minor Life", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								]
				}, 
				"medium_health": {
								"name": "Buffed Life", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}
								]
				}, 
				"minor_life_regen": {
								"name": "Minor Life Regen", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_regen", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 5, 
												}
								]
				}, 

				"minor_lgoh": {
								"name": "Minor Leech", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "life_gain_on_hit", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}
								]
				}, 

				"major_lgoh": {
								"name": "Major Leech", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "life_gain_on_hit", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 3, 
												}
								]
				}, 

				
				"major_life": {
								"name": "Hearty", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 25, 
												}
								]
				}, 
				"major_life_regen": {
								"name": "Regenerative Tissue", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_regen", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 25.0, 
												}
								]
				}, 

				
				"ogre_blood": {
								"name": "Ogre Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 35, 
												}, 
								]
				}, 
				"zombie_blood": {
								"name": "Zombie Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.015, 
												}, 
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"chilled_blood": {
								"name": "Chilled Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.07, 
												}, 
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"ancient_blood": {
								"name": "Ancient Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.08, 
												}, 
												{
																"stat": "health_recovery_rate", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
								]
				}, 

				
				"minor_projectile_damage": {
								"name": "Minor Projectile Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}
								]
				}, 
				"minor_projectile_speed": {
								"name": "Minor Projectile Speed", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_projectile_speed": {
								"name": "Ranged Proficiency", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "projectile_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}
								]
				}, 
				"major_projectile_damage": {
								"name": "Projectile Specialist", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}, 
								]
				}, 

				
				"extra_attack_projectiles": {
								"name": "Extra Munitions", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_count", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"extra_spell_projectiles": {
								"name": "Repeated Casting", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_count", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 

				
				"minor_dot_damage": {
								"name": "Damage Over Time", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": dot_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.06, 
												}
								]
				}, 
				"major_dot_damage": {
								"name": "Draining Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": dot_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
												}
								]
				}, 
				"uber_dot_damage": {
								"name": "Wicked Siphon", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": dot_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_fire_dot_damage": {
								"name": "Lingering Flames", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.FIRE]
												}
								]
				}, 
				"major_fire_dot_damage": {
								"name": "Lava Veins", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.FIRE]
												}
								]
				}, 

				"minor_physical_dot_damage": {
								"name": "Light Hemorrhage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.PHYSICAL]
												}
								]
				}, 
				"major_physical_dot_damage": {
								"name": "Heavy Hemorrhage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.PHYSICAL]
												}
								]
				}, 

				
				"minor_physical_resistances": {
								"name": "Physical Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_physical_resistances": {
								"name": "Major Physical Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_lightning_resistances": {
								"name": "Lightning Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_lightning_resistances": {
								"name": "Major Lightning Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_cold_resistances": {
								"name": "Cold Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_cold_resistances": {
								"name": "Major Cold Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_fire_resistances": {
								"name": "Fire Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_fire_resistances": {
								"name": "Major Fire Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_toxic_resistances": {
								"name": "Toxic Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_toxic_resistances": {
								"name": "Major Toxic Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 

				"maximum_physical_resistance": {
								"name": "Maximum Physical Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "maximum_physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}
								]
				}, 
				"maximum_lightning_resistance": {
								"name": "Maximum Lightning Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "maximum_lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}
								]
				}, 
				"maximum_cold_resistance": {
								"name": "Maximum Cold Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "maximum_cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}
								]
				}, 
				"maximum_fire_resistance": {
								"name": "Maximum Fire Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "maximum_fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}
								]
				}, 
				"maximum_toxic_resistance": {
								"name": "Maximum Toxic Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "maximum_toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}
								]
				}, 

				"maximum_all_resistances": {
								"name": "Maximum Toxic Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "maximum_physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}, 
												{
																"stat": "maximum_lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}, 
												{
																"stat": "maximum_cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}, 
												{
																"stat": "maximum_fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}, 
												{
																"stat": "maximum_toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}, 
								]
				}, 

				"minor_curse_resistance": {
								"name": "Minor Curse Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_curse_resistance": {
								"name": "Demonic Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.26, 
												}
								]
				}, 

				
				"minor_block_chance": {
								"name": "Minor Block Chance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}
								]
				}, 
				"minor_block_chance_armor": {
								"name": "Sturdy Block Chance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_block_chance": {
								"name": "Expert Shieldbearer", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								]
				}, 

				"minor_block_recovery": {
								"name": "Minor Recovery on Block", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "life_gain_on_block", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 20, 
												}
								]
				}, 

				"major_block_recovery": {
								"name": "Major Recovery on Block", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "life_gain_on_block", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 120, 
												}
								]
				}, 

				
				"minor_ailment_avoidance": {
								"name": "Minor Ailment Avoidance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "ailment_avoidance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								]
				}, 
				"major_ailment_avoidance": {
								"name": "Ailment Avoidance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "ailment_avoidance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}
								]
				}, 
				"major_ailment_avoidance_evasion": {
								"name": "Skilled Avoidance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "ailment_avoidance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}
								]
				}, 

				"minor_ailment_avoidance_life": {
								"name": "Minor Elemental Resilience", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "ailment_avoidance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.04, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
												}
								]
				}, 
				"major_ailment_avoidance_life": {
								"name": "Elemental Resilience", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "ailment_avoidance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}
								]
				}, 

				"minor_crit_resistance": {
								"name": "Minor Crit Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "crit_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_crit_resistance": {
								"name": "Major Crit Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "crit_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 

				
				"minor_movement_speed": {
								"name": "Fast Feet", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								]
				}, 
				"minor_all_speed": {
								"name": "Agile", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.03, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.03, 
												}
								]
				}, 
				"major_movement_speed": {
								"name": "Sprinter", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}
								]
				}, 
				"major_all_speed": {
								"name": "Swift", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.06, 
												}
								]
				}, 
				"minor_movement_speed_evasion": {
								"name": "Thief Step", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.03, 
												}
								]
				}, 
				"major_movement_speed_evasion": {
								"name": "Mastermind of Movement", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.06, 
												}
								]
				}, 


				
				"minor_cast_speed_melee": {
								"name": "Melee Speed", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
																"tags": [SkillTags.Tags.MELEE]
												}
								]
				}, 
				"major_cast_speed_melee": {
								"name": "Proficient Strikes", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.MELEE]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.MELEE]
												}
								]
				}, 
				"minor_cast_speed_attack": {
								"name": "Attack Speed", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_cast_speed_attack": {
								"name": "Attack Proficiency", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.09, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_cast_speed_spell": {
								"name": "Spellcasting Proficiency", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.09, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_cast_speed_spell": {
								"name": "Spellcasting Speed", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_cast_speed": {
								"name": "Nimble Hands", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
												}
								]
				}, 

				
				"minor_spell_damage": {
								"name": "Minor Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_attack_damage": {
								"name": "Minor Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"medium_spell_damage": {
								"name": "Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"medium_attack_damage": {
								"name": "Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_spell_damage": {
								"name": "Heavy Spell Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"major_attack_damage": {
								"name": "Heavy Attack Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				
				"minor_physical_damage": {
								"name": "Minor Physical Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"medium_physical_damage": {
								"name": "Physical Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
												}
								]
				}, 
				"major_physical_damage": {
								"name": "Physician", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
								]
				}, 
				"major_physical_damage_crit": {
								"name": "Physically Attuned", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"minor_spell_physical_damage": {
								"name": "Minor Physical Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_attack_physical_damage": {
								"name": "Minor Physical Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"medium_spell_physical_damage": {
								"name": "Physical Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"medium_attack_physical_damage": {
								"name": "Physical Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_spell_physical_damage": {
								"name": "Heavy Physical Spell Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"major_attack_physical_damage": {
								"name": "Heavy Physical Attack Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				
				"minor_lightning_damage": {
								"name": "Minor Lightning Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_lightning_damage_conduit": {
								"name": "Lightning Conduit", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}
								]
				}, 
				"minor_spell_lightning_damage": {
								"name": "Minor Lightning Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_attack_lightning_damage": {
								"name": "Minor Lightning Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"medium_spell_lightning_damage": {
								"name": "Lightning Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"medium_attack_lightning_damage": {
								"name": "Lightning Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_spell_lightning_damage": {
								"name": "Heavy Lightning Spell Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"major_attack_lightning_damage": {
								"name": "Heavy Lightning Attack Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				
				"minor_cold_damage": {
								"name": "Minor Cold Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_cold_damage": {
								"name": "Yeti", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}
								]
				}, 
				"minor_spell_cold_damage": {
								"name": "Minor Cold Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_attack_cold_damage": {
								"name": "Minor Cold Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"medium_spell_cold_damage": {
								"name": "Cold Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"medium_attack_cold_damage": {
								"name": "Cold Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_spell_cold_damage": {
								"name": "Heavy Cold Spell Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"major_attack_cold_damage": {
								"name": "Heavy Cold Attack Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				
				"minor_fire_damage": {
								"name": "Minor Fire Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_fire_damage": {
								"name": "Pyro", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}
								]
				}, 
				"major_fire_damage_ailement_effect": {
								"name": "Fire Damage Master", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}
								]
				}, 
				"minor_spell_fire_damage": {
								"name": "Minor Fire Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_attack_fire_damage": {
								"name": "Minor Fire Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"medium_spell_fire_damage": {
								"name": "Fire Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"medium_attack_fire_damage": {
								"name": "Fire Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_spell_fire_damage": {
								"name": "Heavy Fire Spell Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"major_attack_fire_damage": {
								"name": "Heavy Fire Attack Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				
				"minor_toxic_damage": {
								"name": "Minor Toxic Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_toxic_damage": {
								"name": "Plaguebearer", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_spell_toxic_damage": {
								"name": "Minor Toxic Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"minor_attack_toxic_damage": {
								"name": "Minor Toxic Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"medium_spell_toxic_damage": {
								"name": "Toxic Spell Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"medium_attack_toxic_damage": {
								"name": "Toxic Attack Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 
				"major_spell_toxic_damage": {
								"name": "Heavy Toxic Spell Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 
				"major_attack_toxic_damage": {
								"name": "Heavy Toxic Attack Damage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				
				"minor_hit_damage": {
								"name": "Denting Blows", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.HIT]
												}
								]
				}, 
				"minor_hit_damage_cast_speed": {
								"name": "Rapid Blows", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.HIT]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.HIT]
												}
								]
				}, 
				"major_hit_damage": {
								"name": "Crushing Blows", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.HIT]
												}
								]
				}, 
				"major_hit_damage_cast_speed": {
								"name": "Rapid Crush", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
																"tags": [SkillTags.Tags.HIT]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.HIT]
												}
								]
				}, 

				"massive_hit_damage": {
								"name": "Immediate Effectiveness", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.HIT]
												}, 
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.8, 
																"tags": [SkillTags.Tags.HIT]
												}
								]
				}, 

				
				"minor_armor": {
								"name": "Minor Armor", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": armor_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 120, 
												}
								]
				}, 
				"major_armor": {
								"name": "Major Armor", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": armor_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 400, 
												}
								]
				}, 
				"minor_evasion": {
								"name": "Minor Evasion", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 120, 
												}
								]
				}, 
				"major_evasion": {
								"name": "Major Evasion", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 400, 
												}
								]
				}, 
				"minor_hybrid": {
								"name": "Minor Defenses", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								]
				}, 
				"major_hybrid": {
								"name": "Major Defenses", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
								]
				}, 
				"minor_armor_life": {
								"name": "Armored Life", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
												}
								]
				}, 
				"major_armor_life": {
								"name": "Coagulated Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"minor_evasion_life": {
								"name": "Dodgey", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
												}
								]
				}, 
				"major_evasion_life": {
								"name": "Stealthy", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 

				
				"minor_health_regen": {
								"name": "Minor Regeneration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_regen", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 5, 
												}, 
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.006, 
												}
								]
				}, 
				"medium_health_regen": {
								"name": "Regeneration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_regen", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 15, 
												}, 
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}
								]
				}, 
				"major_health_regen": {
								"name": "Salamander Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.015, 
												}, 
												{
																"stat": "health_recovery_rate", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 

				
				"minor_health_regen_armor": {
								"name": "Regenerative Armor", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": armor_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 50, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.004, 
												}
								]
				}, 
				"major_health_regen_armor": {
								"name": "Lizard Skin", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": armor_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 150, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}
								]
				}, 

				
				"attack_fire_damage_and_penetration": {
								"name": "Infrared Blade", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "fire_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				"spell_fire_damage_and_penetration": {
								"name": "Lava Sparking", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "fire_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 

				"attack_cold_damage_and_penetration": {
								"name": "Chilled Smash", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				"spell_cold_damage_and_penetration": {
								"name": "Cracking Casts", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 

				"attack_lightning_damage_and_penetration": {
								"name": "Charged Hammer", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				"spell_lightning_damage_and_penetration": {
								"name": "Zapping Hands", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.SPELL]
												}
								]
				}, 

				"attack_penetration": {
								"name": "Elemental Attack Penetration", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "fire_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.ATTACK]
												}
								]
				}, 

				
				"minor_enhanced_ailment_chance": {
								"name": "Ailment Study", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}, 
								], 
				}, 
				"major_enhanced_ailment_chance": {
								"name": "Enhanced Ailments", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
								], 
				}, 
				"minor_physical_ailment_chance": {
								"name": "Bleed Chance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_physical_ailment_chance": {
								"name": "Heightened Bleed Chance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_lightning_ailment_chance": {
								"name": "Jolt Chance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_lightning_ailment_chance": {
								"name": "Heightened Jolt Chance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_cold_ailment_chance": {
								"name": "Chill Chance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": chill_tex, 
								"stats": [
												{
																"stat": "cold_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_cold_ailment_chance": {
								"name": "Heightened Chill Chance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": chill_tex, 
								"stats": [
												{
																"stat": "cold_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_fire_ailment_chance": {
								"name": "Burn Chance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_fire_ailment_chance": {
								"name": "Heightened Burn Chance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}
								]
				}, 
				"minor_toxic_ailment_chance": {
								"name": "Poison Chance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_toxic_ailment_chance": {
								"name": "Heightened Poison Chance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								]
				}, 

				
				"minor_physical_ailment_effect": {
								"name": "Bleed Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_physical_ailment_effect": {
								"name": "Bleed Intensity", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}
								]
				}, 
				"minor_lightning_ailment_effect": {
								"name": "Jolt Amplifier", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_lightning_ailment_effect": {
								"name": "St. Elmo's Fire", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}
								]
				}, 
				"uber_lightning_ailment_effect": {
								"name": "Tesla Coil", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "skill_chain", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 
				"minor_cold_ailment_effect": {
								"name": "Chill Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": chill_tex, 
								"stats": [
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"minor_fire_ailment_effect": {
								"name": "Burn Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_fire_ailment_effect": {
								"name": "Burn Intensity", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}
								]
				}, 
				"uber_fire_ailment_effect": {
								"name": "Lavaborn", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}
								]
				}, 
				"minor_toxic_ailment_effect": {
								"name": "Poison Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								]
				}, 
				"medium_toxic_ailment_effect": {
								"name": "Extended Poison", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.TOXIC]
												}
								]
				}, 
				"major_toxic_ailment_effect": {
								"name": "Poison Intesity", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}
								]
				}, 
				"uber_toxic_ailment_effect": {
								"name": "Venom Collector", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "infection_count", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}
								]
				}, 

				
				"minor_skill_duration": {
								"name": "Minor Skill Duration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": duration_tex, 
								"stats": [
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_skill_duration": {
								"name": "Persistent Skills", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": duration_tex, 
								"stats": [
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}
								]
				}, 

				
				"minor_ailment_duration": {
								"name": "Minor Ailment Duration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"minor_ailment_effect": {
								"name": "Minor Ailment Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}
								]
				}, 
				"major_ailment_effect": {
								"name": "Ailment Amplifier", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_ailment_duration": {
								"name": "Ailment Duration", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
												}
								]
				}, 

				
				"toxicologist": {
								"name": "Toxicologist", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 1.75, 
												}, 
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.5, 
												}
								]
				}, 

				
				"minor_area_of_effect": {
								"name": "Area of Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}
								]
				}, 
				"major_area_of_effect": {
								"name": "Extended Reach", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "area_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}
								]
				}, 

				"minor_physical_area_of_effect": {
								"name": "Physical Area of Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.PHYSICAL]
												}, 
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								]
				}, 
				"major_physical_area_of_effect": {
								"name": "Iron Reach", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.PHYSICAL]
												}, 
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
								]
				}, 

				"minor_lightning_area_of_effect": {
								"name": "Lightning Area of Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.LIGHTNING]
												}, 
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								]
				}, 
				"major_lightning_area_of_effect": {
								"name": "Arcing Reach", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.LIGHTNING]
												}, 
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
								]
				}, 

				"minor_cold_area_of_effect": {
								"name": "Cold Area of Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.COLD]
												}, 
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								]
				}, 
				"major_cold_area_of_effect": {
								"name": "Frigid Reach", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.COLD]
												}, 
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
								]
				}, 
				"uber_cold_area_of_effect": {
								"name": "Winter Squall", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.COLD]
												}, 
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.COLD]
												}, 
								]
				}, 

				"minor_fire_area_of_effect": {
								"name": "Fire Area of Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								]
				}, 
				"major_fire_area_of_effect": {
								"name": "Flaming Reach", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
								]
				}, 

				"minor_toxic_area_of_effect": {
								"name": "Toxic Area of Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.TOXIC]
												}, 
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								]
				}, 
				"major_toxic_area_of_effect": {
								"name": "Venomous Reach", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.TOXIC]
												}, 
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.24, 
												}, 
								]
				}, 

				
				"minor_crit_chance": {
								"name": "Critical Strikes", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
								]
				}, 
				"major_crit_chance": {
								"name": "Critical Strikes", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.65, 
												}, 
								]
				}, 
				"minor_crit_multi": {
								"name": "Critical Multiplier", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}, 
								]
				}, 
				"major_crit_multi": {
								"name": "Critical Multiplier", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}, 
								]
				}, 

				"minor_crit_chance_projectiles": {
								"name": "Projectile Critical Strikes", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}, 
								]
				}, 
				"major_crit_chance_projectiles": {
								"name": "Projectile Critical Attunement", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.6, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}, 
								]
				}, 

				"minor_attack_crit_chance": {
								"name": "Minor Attack Critical Strikes", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
								]
				}, 
				"major_attack_crit_chance": {
								"name": "Attack Critical Strikes", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.6, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
								]
				}, 
				"minor_attack_crit_multi": {
								"name": "Minor Attack Critical Multiplier", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
								]
				}, 
				"major_attack_crit_multi": {
								"name": "Attack Critical Multiplier", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
								]
				}, 

				"minor_spell_crit_chance": {
								"name": "Spell Critical Strikes", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 
				"major_spell_crit_chance": {
								"name": "Magnificient Spell Critical Strikes", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.75, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 
				"minor_spell_crit_multi": {
								"name": "Spell Critical Multiplier", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 
				"major_spell_crit_multi": {
								"name": "Magnificient Spell Critical Multiplier", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 

				"minor_spell_crit_chance_cast_speed": {
								"name": "Minor Wizardry", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 
				"major_spell_crit_chance_cast_speed": {
								"name": "Wizardry", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 
				"minor_spell_crit_multi_cast_speed": {
								"name": "Weak Magus", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.03, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 
				"major_spell_crit_multi_cast_speed": {
								"name": "Magus", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.SPELL]
												}, 
								]
				}, 

				"stable_strikes": {
								"name": "Stable Strikes", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": hit_attunement_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 1.0, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.6, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
								]
				}, 

				"volatile_strikes": {
								"name": "Volatile Strikes", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.6, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 1.0, 
																"tags": [SkillTags.Tags.ATTACK]
												}, 
								]
				}, 

				
				"minor_curse_effect": {
								"name": "Minor Curse Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}, 
								]
				}, 
				"major_curse_effect": {
								"name": "Major Curse Effect", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"minor_curse_effect_cast_speed": {
								"name": "Minor Curse Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.CURSE]
												}, 

								]
				}, 
				"major_curse_effect_cast_speed": {
								"name": "Curse Wizard", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.09, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.CURSE]
												}, 
								]
				}, 
				"minor_curse_aoe": {
								"name": "Curse Influence", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}, 
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.CURSE]
												}, 
								]
				}, 
				"major_curse_aoe": {
								"name": "Major Curse Influence", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.CURSE]
												}, 
								]
				}, 

				
				"minor_aura_effect": {
								"name": "Minor Aura Effect", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "aura_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.06, 
												}, 
								]
				}, 
				"major_aura_effect": {
								"name": "Major Aura Effect", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "aura_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}, 
								]
				}, 

				
				"bomb_area_minor": {
								"name": "Bomb Tinkerer", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.18, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 
				"bomb_area_major": {
								"name": "Demolitionist", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.6, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 
				"minor_bomb_crit_chance": {
								"name": "Unstable Explosives", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 
				"minor_bomb_crit_multi": {
								"name": "Strong Explosives", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 
				"major_bomb_crit": {
								"name": "Amplified Shockwaves", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 

				
				"impact_speed_keystone": {
								"name": "Impact Speed", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_PROJECTILE_SPEED_DAMAGE"]
				}, 

				"keystone_brick": {
								"name": "Brick", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_BRICK"]
				}, 

				"keystone_impending_death": {
								"name": "Marked for Death", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": curse_tex, 
								"stats": [
								], 
								"keystones": ["TREE_IMPENDING_DEATH"]
				}, 

				"keystone_sanguine_decay": {
								"name": "Sanguine Decay", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": bleed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_SANGUINE_DECAY"]
				}, 
				"keystone_saboteur": {
								"name": "Saboteur", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": bomb_tex, 
								"stats": [
								], 
								"keystones": ["TREE_SABOTEUR"]
				}, 
				"keystone_cyclic_destruction": {
								"name": "Cyclic Destruction", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": aoe_tex, 
								"stats": [
								], 
								"keystones": ["TREE_CYCLE"]
				}, 
				"keystone_cryomancer": {
								"name": "Cryomancer", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
								], 
								"keystones": ["TREE_CRYOMANCER"]
				}, 
				"keystone_charged_field": {
								"name": "Charged Field", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": damage_tex, 
								"stats": [
								], 
								"keystones": ["TREE_CHARGED_FIELD"]
				}, 
				"keystone_kinetic_projectiles": {
								"name": "Kinetic Projectiles", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": damage_tex, 
								"stats": [
								], 
								"keystones": ["TREE_KINETIC_PROJECTILES"]
				}, 
				"keystone_time_warp": {
								"name": "Time Warp", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": duration_tex, 
								"stats": [
								], 
								"keystones": ["TREE_TIME_WARP"]
				}, 
				"keystone_raging_momentum": {
								"name": "Raging Momentum", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": damage_tex, 
								"stats": [
								], 
								"keystones": ["TREE_RAGING_MOMENTUM"]
				}, 
				"keystone_temperature_delta": {
								"name": "Temperature Delta", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": chill_tex, 
								"stats": [
								], 
								"keystones": ["TREE_TEMPERATURE_DELTAS"]
				}, 
				"keystone_volley": {
								"name": "Unstable Volley", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_VOLLEY"]
				}, 
				"keystone_unleash": {
								"name": "Unleashed", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": haste_tex, 
								"stats": [
								], 
								"keystones": ["TREE_UNLEASH"]
				}, 
				"keystone_overloaded_shells": {
								"name": "Overloaded Shells", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_OVERLOADED_SHELLS"]
				}, 


				
				"empty": {
								"name": "TEST NODE", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": damage_tex, 
								"stats": [
								], 
								"keystones": []
				}, 

				
				"attuned_decay": {
								"name": "Attuned Decay", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
												{
																"stat": "dot_damage_per_precision", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.04, 
												}, 
								]
				}, 
				"hysteria": {
								"name": "Hysteria", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [], 
								"keystones": ["TREE_HYSTERIA"]
				}, 
				"dread": {
								"name": "Dread", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": ailment_tex, 
								"stats": [], 
								"keystones": ["TREE_DREAD"]
				}, 
				"paranoia": {
								"name": "Paranoia", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.6, 
												}, 
								], 
								"keystones": ["TREE_PARANOIA"]
				}, 
				"transmogrify": {
								"name": "Transmogrification", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [], 
								"keystones": ["TREE_TRANSMOGRIFICATION"]
				}, 
				"bewitching_whispers": {
								"name": "Bewitching Whispers", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.35, 
												}, 
												{
																"stat": "area_of_effect", 
																"tags": [SkillTags.Tags.CURSE], 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"monster_study": {
								"name": "Monster Study", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "incoming_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.15, 
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"affliction_study": {
								"name": "Affliction Study", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": ailment_mastery_tex, 
								"stats": [
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								], 
				}, 



				
				"battle_hardened": {
								"name": "Battle Hardened", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": armor_tex, 
								"stats": [
												{
																"stat": "incoming_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.2, 
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"tags": [SkillTags.Tags.ATTACK], 
																"amount": 0.2, 
												}, 
								], 
				}, 
				"fury": {
								"name": "Fury", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.1, 
												}, 
								], 
								"keystones": ["TREE_FURY"]
				}, 
				"spirited_resilience": {
								"name": "Spirited Resilience", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "toughness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
												{
																"stat": "swiftness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
												{
																"stat": "swiftness_boon_on_hit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "toughness_boon_on_hit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								], 
				}, 
				"youthful_recklessness": {
								"name": "Youthful Recklessness", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"tags": [SkillTags.Tags.ATTACK], 
																"amount": 0.4, 
												}, 
												{
																"stat": "incoming_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
												}, 
								], 
				}, 
				"hoplite": {
								"name": "Hoplite", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.2, 
												}, 
								], 
								"keystones": ["TREE_HOPLITE"], 
				}, 
				"swordsman": {
								"name": "Swordsman", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [], 
								"keystones": ["TREE_SWORDSMAN"], 
				}, 
				"thors_apprentice": {
								"name": "Thor's Apprentice", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "conversion_physical_to_lightning", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1.0, 
												}, 
								], 
				}, 
				"warriors_spirit": {
								"name": "Warrior Spirit", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "aura_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								], 
				}, 

				
				"leeching_presence": {
								"name": "Leeching Presence", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "life_gain_on_hit", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 20, 
												}, 
								], 
				}, 
				"retaliatory_mark": {
								"name": "Retaliatory Mark", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [], 
								"keystones": ["TREE_TRANSFUSION"]
				}, 
				"blood_armor": {
								"name": "Blood Armor", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [], 
								"keystones": ["TREE_BLOOD_ARMOR"]
				}, 
				"magmatic_blood": {
								"name": "Magmatic Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": burn_tex, 
								"stats": [], 
								"keystones": ["TREE_MAGMATIC_BLOOD"]
				}, 
				"blood_price": {
								"name": "Blood Price", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 8.0, 
												}, 
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1.0, 
												}, 
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.75, 
												}, 
								], 
				}, 
				"veil_of_night": {
								"name": "Veil of Night", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 5000, 
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.3, 
												}, 
								], 
				}, 
				"caustics": {
								"name": "Caustics", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "extra_fire_as_toxic", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"effect_of_the_horde": {
								"name": "Effect of the Horde", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": swiftness_boon_tex, 
								"stats": [
												{
																"stat": "swiftness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}, 
												{
																"stat": "damage_per_swiftness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "aoe_per_swiftness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}, 
								], 
				}, 

				
				"thieves_agility": {
								"name": "Thieves Agility", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.1, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.12, 
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.015, 
												}, 
								], 
				}, 
				"volatile_casting": {
								"name": "Volatile Casting", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "swiftness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
												{
																"stat": "swiftness_boon_on_hit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}, 
								], 
				}, 
				"chain_gang": {
								"name": "Chain Gang", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "skill_chain", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}, 
												{
																"stat": "projectile_count", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
												}, 
								], 
								"keystones": ["TREE_RICOCHET"]
				}, 
				"warped_time": {
								"name": "Event Horizons", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_speed_per_swiftness", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.05, 
												}, 
												{
																"stat": "aoe_per_swiftness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
												}, 
												{
																"stat": "damage_per_swiftness", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.02, 
												}, 
								], 
				}, 
				"bloody_mess": {
								"name": "Bloody Mess", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"tags": [SkillTags.Tags.PROJECTILE], 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "physical_ailment_effect", 
																"tags": [SkillTags.Tags.PROJECTILE], 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.3, 
												}, 
								], 
				}, 
				"shocking_moves": {
								"name": "Shocking Moves", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
												{
																"stat": "extra_physical_as_lightning_per_swiftness", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}
								], 
								"keystones": ["TREE_SHOCKING_MOVES"]
				}, 
				"fortified_artillery": {
								"name": "Fortified Artillery", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "incoming_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.35, 
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.35, 
												}, 
								], 
				}, 
				"hand_to_hand_combat": {
								"name": "Hand to Hand Specialist", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"tags": [SkillTags.Tags.MELEE], 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.6, 
												}, 
												{
																"stat": "cast_speed", 
																"tags": [SkillTags.Tags.MELEE], 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.1, 
												}, 
								], 
				}, 


				
				"forest_bathing": {
								"name": "Forest Bathing", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "life_regen_per_wisdom", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}, 
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.1, 
												}, 
								], 
				}, 
				"arctic_breath": {
								"name": "Arctic Breath", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": chill_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.2, 
												}, 
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"tags": [SkillTags.Tags.COLD], 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"impactful_strikes": {
								"name": "Impactful Strikes", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 1.25, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.3, 
												}, 
								], 
				}, 
				"frozen_domain": {
								"name": "Vile Domain", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": poisoned_tex, 
								"stats": [], 
								"keystones": ["TREE_VILE_DOMAIN"]
				}, 
				"viridian_sage": {
								"name": "Viridian Sage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": armor_tex, 
								"stats": [], 
								"keystones": ["TREE_VIRIDIAN_SAGE"]
				}, 
				"oak_aegis": {
								"name": "Oak Aegis", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": - 0.3, 
												}, 
								], 
				}, 
				"mountain_born": {
								"name": "Mountain Born", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.75, 
												}, 
												{
																"stat": "maximum_cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}, 
												{
																"stat": "conversion_physical_to_cold", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"stifled_cursing": {
								"name": "Stifled Cursing", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"tags": [SkillTags.Tags.CURSE], 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
								], 
								"keystones": ["TREE_STIFLED_CURSING"]
				}, 

				
				"energetic_flesh": {
								"name": "Energetic Flesh", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": jolt_tex, 
								"stats": [], 
								"keystones": ["TREE_ENERGETIC_FLESH"]
				}, 
				"chaotic_resonance": {
								"name": "Chaotic Resonance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": poisoned_tex, 
								"stats": [], 
								"keystones": ["TREE_CHAOTIC_RESONANCE"]
				}, 
				"one_with_lightning": {
								"name": "One With Lightning", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_taken_as_cold", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "lightning_taken_as_fire", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"bonded_electrons": {
								"name": "Nearby Enemies have Lightning Resistance equal to yours.", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bonded_electrons_tex, 
								"stats": [
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								], 
								"keystones": ["TREE_BONDED_ELECTRONS"]
				}, 
				"reverence": {
								"name": "Reverence", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": - 0.25, 
												}, 
								], 
				}, 
				"scorn": {
								"name": "Scorn", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "aura_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"derision": {
								"name": "Derision", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								], 
				}, 
				"ire": {
								"name": "Conductive Ire", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"tags": [SkillTags.Tags.LIGHTNING], 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
								], 
				}, 

				
				"weapon_dexterity": {
								"name": "Weapon Dexterity", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [], 
								"keystones": ["TREE_WEAPON_DEXTERITY"]
				}, 
				"strengthened_wisdom": {
								"name": "Strengthened Wisdom", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": strength_tex, 
								"stats": [
												{
																"stat": "strength", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
												{
																"stat": "wisdom", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
								], 
				}, 
				"flame_resonance": {
								"name": "Flame Resonance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1.0, 
												}, 
												{
																"stat": "maximum_fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}, 
								], 
				}, 
				"critical_thinking": {
								"name": "Critical Thinking", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "crit_multi_per_precision", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}, 
								], 
				}, 
				"elemental_shelling": {
								"name": "Elemental Shelling", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_count", 
																"tags": [SkillTags.Tags.ELEMENTAL], 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 3, 
												}, 
								], 
				}, 
				"heated_resonance": {
								"name": "Heated Resonance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "extra_physical_as_cold", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "extra_physical_as_fire", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								], 
				}, 
				"elemental_piercing": {
								"name": "Elemental Piercing", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "fire_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								], 
				}, 
				"overcooked": {
								"name": "Overcook", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.1, 
												}, 
								], 
								"keystones": ["TREE_OVERCOOK"]
				}, 

				
				"titanic_resilience": {
								"name": "Titanic Resilience", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "ailment_avoidance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.75, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.75, 
												}, 
												{
																"stat": "incoming_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 0.1, 
												}, 
								], 
				}, 
				"capable_combatant": {
								"name": "Capable Combatant", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
								], 
								"keystones": ["TREE_CAPABLE_COMBATANT"]
				}, 
				"coated_blades": {
								"name": "Coated Blades", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_chance", 
																"tags": [SkillTags.Tags.ATTACK], 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
								], 
								"keystones": ["TREE_COATED_BLADES"]
				}, 
				"serrated_blades": {
								"name": "Serrated Blades", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"tags": [SkillTags.Tags.ATTACK], 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"tags": [SkillTags.Tags.PHYSICAL], 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "physical_ailment_effect", 
																"tags": [SkillTags.Tags.ATTACK], 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.25, 
												}, 
								], 
				}, 
				"sabotank": {
								"name": "Sabotank", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"tags": [SkillTags.Tags.BOMB], 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.4, 
												}, 
												{
																"stat": "cast_speed", 
																"tags": [SkillTags.Tags.BOMB], 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}
								], 
				}, 
				"slippery_titan": {
								"name": "Slippery Titan", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 1.0, 
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 1.0, 
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
												}, 
								], 
				}, 
				"ailment_reaver": {
								"name": "Ailment Reaver", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"tags": [SkillTags.Tags.ATTACK], 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.3, 
												}, 
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
								], 
				}, 
				"vitality_surge": {
								"name": "Vitality Surge", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_recovery_rate", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}, 
												{
																"stat": "health_regen", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 100, 
												}, 
								], 
				}, 
}


func get_passive_config(passive_tag):
				if stats.has(passive_tag):
								return stats[passive_tag]

				return {}
