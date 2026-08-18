extends Node

var life_tex = preload("res://sprites/gui/passives/life.png")

var damage_tex = preload("res://sprites/gui/passives/damage.png")
var physical_damage_tex = preload("res://sprites/gui/passives/physical_damage.png")
var lightning_damage_tex = preload("res://sprites/gui/passives/lightning_damage.png")
var cold_damage_tex = preload("res://sprites/gui/passives/cold_damage.png")
var fire_damage_tex = preload("res://sprites/gui/passives/fire_damage.png")
var toxic_damage_tex = preload("res://sprites/gui/passives/toxic_damage.png")
var movement_tex = preload("res://sprites/gui/passives/movement.png")
var armor_tex = preload("res://sprites/gui/passives/armor.png")
var evasion_tex = preload("res://sprites/gui/passives/evasion.png")

var resistance_tex = preload("res://sprites/gui/passives/resistance.png")
var penetration_tex = preload("res://sprites/gui/passives/penetration.png")
var curse_tex = preload("res://sprites/gui/passives/curse.png")
var haste_tex = preload("res://sprites/gui/passives/haste.png")
var pierce_tex = preload("res://sprites/gui/passives/pierce.png")
var chain_tex = preload("res://sprites/gui/passives/chain.png")
var aoe_tex = preload("res://sprites/gui/passives/aoe.png")
var projectile_speed_tex = preload("res://sprites/gui/passives/projectile_speed.png")
var duration_tex = preload("res://sprites/gui/passives/duration.png")

var strength_tex = preload("res://sprites/gui/passives/strength.png")
var agility_tex = preload("res://sprites/gui/passives/agility.png")
var constitution_tex = preload("res://sprites/gui/passives/constitution.png")
var finesse_tex = preload("res://sprites/gui/passives/finesse.png")
var wisdom_tex = preload("res://sprites/gui/passives/wisdom.png")

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

var crit_tex = preload("res://sprites/gui/passives/crit.png")
var bomb_tex = preload("res://sprites/gui/passives/bomb.png")
var dot_tex = preload("res://sprites/gui/passives/dot.png")
var block_tex = preload("res://sprites/gui/passives/block.png")


var thunderstorm_tex = preload("res://sprites/gui/passives/thunderstorm.png")
var goliath_tex = preload("res://sprites/gui/passives/goliath.png")
var hit_attunement_tex = preload("res://sprites/gui/passives/hit_attunement.png")
var ailment_tex = preload("res://sprites/gui/passives/ailment.png")
var ailment_mastery_tex = preload("res://sprites/gui/passives/ailment_mastery.png")

var swiftness_boon_tex = preload("res://sprites/status_effects/swiftness_boon.png")
var toughness_boon_tex = preload("res://sprites/status_effects/toughness_boon.png")
var precision_boon_tex = preload("res://sprites/status_effects/precision_boon.png")

var vulnerable_tex = preload("res://sprites/buff_icons/vulnerable.png")

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
				"minor_life_flat": {
								"name": "Minor Life", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 10, 
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
																"amount": 0.08, 
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
				"damage_from_health": {
								"name": "Goliath", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": goliath_tex, 
								"stats": [
								], 
								"keystones": ["TREE_GOLIATH"]
				}, 

				
				"minor_elemental_resistances": {
								"name": "Minor Elemental Resistances", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}, 
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}, 
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}, 
								]
				}, 
				"minor_physical_resistance": {
								"name": "Minor Physical Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
								]
				}, 
				"minor_lightning_resistance": {
								"name": "Minor Lightning Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
								]
				}, 
				"minor_cold_resistance": {
								"name": "Minor Cold Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
								]
				}, 
				"minor_fire_resistance": {
								"name": "Minor Fire Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
								]
				}, 
				"minor_toxic_resistance": {
								"name": "Minor Toxic Resistance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
								]
				}, 
				"major_physical_resistance": {
								"name": "Major Physical Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
								]
				}, 
				"major_lightning_resistance": {
								"name": "Major Lightning Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
								]
				}, 
				"major_cold_resistance": {
								"name": "Major Cold Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
								]
				}, 
				"major_fire_resistance": {
								"name": "Major Fire Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
								]
				}, 
				"major_toxic_resistance": {
								"name": "Major Toxic Resistance", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
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
																"amount": 0.16, 
												}, 
								]
				}, 
				"physical_ailment_surgeon": {
								"name": "Surgeon", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "physical_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03, 
												}, 
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
																"amount": 0.16, 
												}, 
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
																"amount": 0.16, 
												}, 
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
																"amount": 0.16, 
												}, 
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
																"amount": 0.16, 
												}, 
								]
				}, 

				"major_physical_damage": {
								"name": "Heavy Hitter", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
												{
																"stat": "physical_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 
				"major_lightning_damage": {
								"name": "Charged Strikes", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 
				"major_cold_damage": {
								"name": "Cold Heart", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 
				"major_more_cold_damage": {
								"name": "Yeti", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.8, 
												}, 
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "cold_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
								]
				}, 
				"major_fire_damage": {
								"name": "Searing Touches", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.6, 
												}, 
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}, 

								]
				}, 
				"major_toxic_damage": {
								"name": "Necrosis", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toxic_damage_tex, 
								"stats": [
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
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
																"amount": 0.16, 
												}, 
								]
				}, 
				"minor_area_damage": {
								"name": "Minor Area Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "area_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
												}, 
								]
				}, 
				"minor_dot_damage": {
								"name": "Minor Damage over Time", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": dot_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
												}, 
								]
				}, 

				"minor_fire_ailment_damage": {
								"name": "Flame Proficiency", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.06, 
												}, 
								]
				}, 

				"major_fire_ailment_damage": {
								"name": "Fire Wizard", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}, 
								]
				}, 

				"major_fire_hit_damage": {
								"name": "Scalding Hit", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.HIT]
												}, 
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}, 
								]
				}, 

				"minor_bleed_damage": {
								"name": "Minor Blood Loss", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.06, 
												}, 
								]
				}, 
				"minor_poison_damage": {
								"name": "Minor Sickness", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.06, 
												}, 
												{
																"stat": "toxic_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}, 
								]
				}, 
				"major_poison_effect": {
								"name": "Ailing Sickness", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								]
				}, 
				"rapid_decay": {
								"name": "Rapid Decay", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": infected_tex, 
								"stats": [
								], 
								"keystones": ["TREE_RAPID_DECAY"]
				}, 
				"minor_poison_chance": {
								"name": "Infectious", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
								]
				}, 
				"minor_hit_damage": {
								"name": "Minor Hit Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.16, 
												}, 
								]
				}, 

				"major_projectile_damage": {
								"name": "Massive Projectiles", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"major_area_damage": {
								"name": "Bellow", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "area_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"major_dot_damage": {
								"name": "Decay", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": dot_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
								]
				}, 
				"major_bleed_damage": {
								"name": "Hemorrhage", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
								]
				}, 
				"major_poison_damage": {
								"name": "Potent Toxins", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": infected_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
								]
				}, 
				"major_hit_damage": {
								"name": "Denting Blows", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": damage_tex, 
								"stats": [
												{
																"stat": "hit_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}, 
								]
				}, 

				
				"minor_physical_penetration": {
								"name": "Minor Physical Penetration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "physical_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 
				"minor_lightning_penetration": {
								"name": "Minor Lightning Penetration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 
				"minor_cold_penetration": {
								"name": "Minor Cold Penetration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 
				"minor_fire_penetration": {
								"name": "Minor Fire Penetration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "fire_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 
				"minor_toxic_penetration": {
								"name": "Minor Toxic Penetration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "toxic_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								]
				}, 

				"major_penetration": {
								"name": "Giant Breaker", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": penetration_tex, 
								"stats": [
												{
																"stat": "physical_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "lightning_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "cold_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "fire_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "toxic_penetration", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
								]
				}, 

				
				"curse_effect": {
								"name": "Curse Potency", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.03, 
												}, 
								]
				}, 
				"major_curse_effect": {
								"name": "Witch Doctor", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}, 
								]
				}, 

				
				"haste": {
								"name": "Agility", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.03, 
												}, 
								]
				}, 
				"minor_movement_speed": {
								"name": "Quick Feet", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 2, 
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
																"amount": 0.05, 
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
				"minor_cast_speed_attack": {
								"name": "Attack Speed", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.ATTACK]
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
																"amount": 0.03, 
												}
								]
				}, 
				"major_cast_speed": {
								"name": "Arcanist", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}
								]
				}, 

				
				"minor_aoe": {
								"name": "Minor Area Increase", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}
								]
				}, 
				"major_aoe": {
								"name": "Amplified Influence", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": aoe_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}
								]
				}, 

				
				"minor_duration": {
								"name": "Lingering Effects", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": duration_tex, 
								"stats": [
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}
								]
				}, 
				"major_duration": {
								"name": "Warped Time", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": duration_tex, 
								"stats": [
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}
								]
				}, 

				"minor_projectile_speed": {
								"name": "Faster Projectiles", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}
								]
				}, 

				"major_projectile_speed": {
								"name": "Faster Projectiles", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}
								]
				}, 

				
				"extra_pierce": {
								"name": "Pierce", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": pierce_tex, 
								"stats": [
												{
																"stat": "skill_pierce", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}
								]
				}, 
				"extra_chain": {
								"name": "Chain", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": chain_tex, 
								"stats": [
												{
																"stat": "skill_chain", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1, 
												}
								]
				}, 


				"physical_cast_speed_minor": {
								"name": "Rock Slinger", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.03, 
																"tags": [SkillTags.Tags.PHYSICAL]
												}
								], 
				}, 
				"fire_cast_speed_minor": {
								"name": "Flame Slinger", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.FIRE]
												}
								], 
				}, 
				"lightning_cast_speed_minor": {
								"name": "Spark Slinger", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.LIGHTNING]
												}
								], 
				}, 
				"cold_cast_speed_minor": {
								"name": "Snow Slinger", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.COLD]
												}
								], 
				}, 
				"toxic_cast_speed_minor": {
								"name": "Caustic Slinger", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.TOXIC]
												}
								], 
				}, 
				"physical_cast_speed_more": {
								"name": "Gym Rat", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.PHYSICAL]
												}
								], 
				}, 
				"fire_cast_speed_more": {
								"name": "Volcanic", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.FIRE]
												}
								], 
				}, 
				"lightning_cast_speed_more": {
								"name": "Electric", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.LIGHTNING]
												}
								], 
				}, 
				"cold_cast_speed_more": {
								"name": "Slippery", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.COLD]
												}
								], 
				}, 
				"toxic_cast_speed_more": {
								"name": "Mad Scientist", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": haste_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.TOXIC]
												}
								], 
				}, 
				"fire_cold_duration_greater": {
								"name": "Thermomemer", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": duration_tex, 
								"stats": [
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.FIRE, SkillTags.Tags.COLD]
												}
								], 
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

				

				"minor_physical_ailment_chance": {
								"name": "Sharp Cuts", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								], 
				}, 
				"minor_lightning_ailment_chance": {
								"name": "Jolting Blows", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								], 
				}, 
				"minor_cold_ailment_chance": {
								"name": "Frosted Tip", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": chill_tex, 
								"stats": [
												{
																"stat": "cold_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								], 
				}, 
				"minor_fire_ailment_chance": {
								"name": "Smoldering Tissue", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								], 
				}, 
				"minor_toxic_ailment_chance": {
								"name": "Dirty Claws", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05, 
												}
								], 
				}, 
				"major_physical_ailment_chance": {
								"name": "Deep Cuts", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": rupture_tex, 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
								], 
				}, 

				"major_lightning_ailment_chance": {
								"name": "Shock Therapy", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": electrocute_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
								], 
				}, 
				"major_cold_ailment_chance": {
								"name": "Cold Heart", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": frozen_tex, 
								"stats": [
												{
																"stat": "cold_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
								], 
				}, 
				"major_fire_ailment_chance": {
								"name": "Lavaborn", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": char_tex, 
								"stats": [
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
								], 
				}, 
				"major_toxic_ailment_chance": {
								"name": "Spiderling", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": infected_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}, 
								], 
				}, 

				"minor_physical_ailment_effect": {
								"name": "Platelet Inhibitor", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.06, 
												}
								], 
				}, 
				"major_physical_ailment_effect": {
								"name": "Serrated Cut", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bleed_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								], 
				}, 
				"major_cold_ailment_effect": {
								"name": "Deep Chill", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "cold_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
												}, 
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.05, 
												}
								], 
				}, 

				"projectile_speed_damage": {
								"name": "Impact Speed", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_PROJECTILE_SPEED_DAMAGE"]
				}, 

				"volcanic_keystone": {
								"name": "Magamatic", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": burnt_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
								], 
								"keystones": []
				}, 

				"snowstorm_keystone": {
								"name": "Snowstorm", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "area_of_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.COLD]
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
																"tags": [SkillTags.Tags.COLD]
												}, 
								], 
								"keystones": []
				}, 

				"minor_fire_crit": {
								"name": "Targeted Flames", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.FIRE]
												}
								], 
				}, 
				"major_fire_crit": {
								"name": "Searing Locus", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
												}
								], 
				}, 

				"minor_crit": {
								"name": "Precision", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}
								], 
				}, 
				"minor_crit_multi": {
								"name": "Precision", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
												}
								], 
				}, 
				"major_crit": {
								"name": "Surgical Attack", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
												}
								], 
				}, 
				"major_crit_multi": {
								"name": "Lead Blade", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.32, 
												}
								], 
				}, 
				"spicy": {
								"name": "Spicy", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": fire_damage_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
								], 
				}, 
				"popsicle": {
								"name": "Popsicle", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
																"tags": [SkillTags.Tags.COLD]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.04, 
																"tags": [SkillTags.Tags.COLD]
												}, 
								], 
				}, 

				"icicle": {
								"name": "Sharp Icicle", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.005, 
																"tags": [SkillTags.Tags.COLD]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.COLD]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.COLD]
												}, 
								], 
				}, 

				
				"minor_resistance_movespeed": {
								"name": "Resilience", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.01, 
												}, 
								], 
				}, 
				"bulwark": {
								"name": "Bulwark", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": resistance_tex, 
								"stats": [
												{
																"stat": "maximum_fire_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "maximum_cold_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "maximum_lightning_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "maximum_toxic_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "maximum_physical_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}, 
								], 
				}, 

				
				"curse_cast_speed": {
								"name": "Fast Hexing", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.CURSE]
												}, 
								], 
				}, 
				"curse_duration": {
								"name": "Lasting Hexes", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "increased_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.CURSE]
												}, 
								], 
				}, 
				"curse_potency": {
								"name": "Doom Cursing", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": curse_tex, 
								"stats": [
												{
																"stat": "curse_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2
												}, 
								], 
				}, 
				"minor_block_chance": {
								"name": "Minor Blocking", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.03
												}, 
								], 
				}, 
				"block_and_gain": {
								"name": "Sturdy", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05
												}, 
												{
																"stat": "life_gain_on_block", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 60.0
												}, 
								], 
				}, 
				"inspirational_hits": {
								"name": "Inspirational Hits", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "life_gain_on_block", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 250.0
												}, 
								], 
				}, 

				"minor_armor": {
								"name": "Thick Skin", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": armor_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 80.0
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08
												}, 
								], 
				}, 
				"major_armor": {
								"name": "Troll Hide", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": armor_tex, 
								"stats": [
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.13
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 400.0
												}, 
								], 
				}, 

				

				"major_lightning_ailment_chance_effect": {
								"name": "Thunderstorm", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": thunderstorm_tex, 
								"stats": [
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.8
												}, 
												{
																"stat": "lightning_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.LIGHTNING]
												}, 
								], 
				}, 

				
				"volrog": {
								"name": "Volrog", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": burn_tex, 
								"stats": [
												{
																"stat": "fire_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.7
												}, 
												{
																"stat": "fire_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.FIRE]
												}, 
								], 
				}, 

				"reaper": {
								"name": "Reaper", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": rupture_tex, 
								"stats": [
												{
																"stat": "physical_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.4
												}, 
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
																"tags": [SkillTags.Tags.PHYSICAL]
												}, 
								], 
				}, 

				"athleticism": {
								"name": "Athleticism", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": movement_tex, 
								"stats": [
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 15.0
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
												}, 
								], 
				}, 

				"elemental_crit_chance": {
								"name": "Elemental Honing", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.ELEMENTAL]
												}
								], 
				}, 
				"elemental_crit_multi": {
								"name": "Elemental Amplification", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.ELEMENTAL]
												}
								], 
				}, 
				"elemental_crit_mastery": {
								"name": "Elemental Affinity", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.ELEMENTAL]
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.015, 
																"tags": [SkillTags.Tags.ELEMENTAL]
												}
								], 
				}, 

				
				"minor_percent_health_regen": {
								"name": "Regeneration", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.005, 
												}, 
								], 
				}, 
				"major_percent_health_regen": {
								"name": "Lizard Flesh", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_max", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "health_regen_percent", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
								], 
				}, 

				"ailment_master": {
								"name": "Ailment Mastery", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": ailment_mastery_tex, 
								"stats": [
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1, 
												}, 
												{
																"stat": "amplify_ailment_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.5, 
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
								"passive_type": PassiveTypes.SMALL, 
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
					"demolitionist": {
								"name": "Precise Explosives", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.45, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.01, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 

				"minor_bomb_cast_speed": {
								"name": "Fast Saboteur", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 
				"major_bomb_cast_speed": {
								"name": "Explosives Expert", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
								], 
				}, 

				"minor_bomb_damage": {
								"name": "Packed Charges", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.BOMB]
												}
								], 
				}, 

				"major_bomb_damage": {
								"name": "Packed Charges", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": bomb_tex, 
								"stats": [
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.35, 
																"tags": [SkillTags.Tags.BOMB]
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.BOMB]
												}
								], 
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

				"minor_lightning_ailment_effect": {
								"name": "Zapping Blows", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": jolt_tex, 
								"stats": [
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "lightning_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
								], 
				}, 

				"minor_toxic_ailment_effect": {
								"name": "Strong Poisons", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": poisoned_tex, 
								"stats": [
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.06, 
												}, 
								], 
				}, 

				"minor_physical_projectile_damage": {
								"name": "Lead Bullets", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": physical_damage_tex, 
								"stats": [
												{
																"stat": "physical_damage", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}, 
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": - 0.1, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}, 
								], 
				}, 
				"minor_projectile_crit": {
								"name": "Pointy Bullets", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}
								], 
				}, 
				"major_projectile_crit": {
								"name": "Lethal Ammo", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 1.0, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}
								], 
				}, 

				"minor_block_chance_armor": {
								"name": "Resiliece Training", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.02, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
												}
								], 
				}, 
				"tank": {
								"name": "Tank", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": block_tex, 
								"stats": [
												{
																"stat": "block_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.08, 
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.3, 
												}
								], 
				}, 

				"ranger": {
								"name": "Ranger", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
												{
																"stat": "projectile_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
												}, 
												{
																"stat": "movement_speed", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12, 
												}, 
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.PROJECTILE]
												}
								], 
				}, 

				"minor_ailment_duration": {
								"name": "Lasting Ailments", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": duration_tex, 
								"stats": [
												{
																"stat": "ailment_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08, 
												}
								], 
				}, 
				"major_ailment_effect": {
								"name": "Strong Ailments", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": ailment_tex, 
								"stats": [
												{
																"stat": "physical_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "lightning_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "cold_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "fire_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
												{
																"stat": "toxic_ailment_effect", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.15, 
												}, 
								], 
				}, 

				"hit_attunement": {
								"name": "Hit Attunement", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": hit_attunement_tex, 
								"stats": [
												{
																"stat": "dot_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": - 1.0, 
												}, 
												{
																"stat": "cast_speed", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.HIT]
												}, 
												{
																"stat": "all_damage", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.HIT]
												}, 
								], 
				}, 

				"minor_hit_crit": {
								"name": "Precision Hits", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15, 
																"tags": [SkillTags.Tags.HIT]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1, 
																"tags": [SkillTags.Tags.HIT]
												}, 
								], 
				}, 
				"minor_hit_crit_multi": {
								"name": "Hit Specialist", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.18, 
																"tags": [SkillTags.Tags.HIT]
												}, 
								], 
				}, 
				"major_hit_crit": {
								"name": "Hit Mastery", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_chance", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.4, 
																"tags": [SkillTags.Tags.HIT]
												}, 
												{
																"stat": "crit_multi", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.3, 
																"tags": [SkillTags.Tags.HIT]
												}, 
								], 
				}, 
				"minor_evasion": {
								"name": "Minor Evasion", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 80.0
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.08
												}, 
								], 
				}, 
				"major_evasion": {
								"name": "Fast Reflexes", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.13
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 400.0
												}, 
								], 
				}, 
				"martial_training": {
								"name": "Martial Training", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": evasion_tex, 
								"stats": [
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2
												}, 
												{
																"stat": "evasion", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 500.0
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2
												}, 
												{
																"stat": "mitigation", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 500.0
												}, 
								], 
				}, 

				"minor_lightning_to_cold": {
								"name": "Chilled Lightning", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": lightning_damage_tex, 
								"stats": [
												{
																"stat": "conversion_lightning_to_cold", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"minor_cold_to_fire": {
								"name": "Heated Ice", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": cold_damage_tex, 
								"stats": [
												{
																"stat": "conversion_cold_to_fire", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"minor_vulnerable_effect": {
								"name": "Cowardly", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": vulnerable_tex, 
								"stats": [
												{
																"stat": "vulnerable_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"major_vulnerable_effect": {
								"name": "Fearmonger", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": vulnerable_tex, 
								"stats": [
												{
																"stat": "vulnerable_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1
												}, 
												{
																"stat": "vulnerable_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"minor_exposure_effect": {
								"name": "Minor Exposure", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": vulnerable_tex, 
								"stats": [
												{
																"stat": "exposure_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.15
												}, 
								], 
				}, 

				"major_exposure_effect": {
								"name": "Elemental Dread", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": vulnerable_tex, 
								"stats": [
												{
																"stat": "exposure_effect", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25
												}, 
												{
																"stat": "exposure_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1
												}, 
								], 
				}, 

				

				"swiftness_boon": {
								"name": "Maximum Swiftness Boon", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": swiftness_boon_tex, 
								"stats": [
												{
																"stat": "swiftness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1
												}, 
								], 
				}, 

				"precision_boon": {
								"name": "Maximum Precision Boon", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": precision_boon_tex, 
								"stats": [
												{
																"stat": "precision_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1
												}, 
								], 
				}, 

				"toughness_boon": {
								"name": "Maximum Toughness Boon", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "toughness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1
												}, 
								], 
				}, 

				"swiftness_boon_on_hit": {
								"name": "Learned Instincts", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": swiftness_boon_tex, 
								"stats": [
												{
																"stat": "swiftness_boon_on_hit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.05
												}, 
								], 
				}, 

				"toughness_boon_on_kill": {
								"name": "Resilience Sapper", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "toughness_boon_on_kill_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"toughness_boon_when_hit": {
								"name": "Learned Instincts", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "toughness_boon_on_get_hit_chance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.2
												}, 
								], 
				}, 

				"toughness_boon_regen": {
								"name": "Regenerative Boons", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "health_regen_percent_toughness_boon", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.007
												}, 
								], 
				}, 

				
				"major_strength": {
								"name": "Major Strength", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": strength_tex, 
								"stats": [
												{
																"stat": "strength", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 40
												}, 
												{
																"stat": "strength", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"major_wisdom": {
								"name": "Major Wisdom", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": wisdom_tex, 
								"stats": [
												{
																"stat": "wisdom", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 40
												}, 
												{
																"stat": "wisdom", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"major_constitution": {
								"name": "Major Constitution", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": constitution_tex, 
								"stats": [
												{
																"stat": "constitution", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 40
												}, 
												{
																"stat": "constitution", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"major_finesse": {
								"name": "Major Finesse", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": finesse_tex, 
								"stats": [
												{
																"stat": "finesse", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 40
												}, 
												{
																"stat": "finesse", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"major_agility": {
								"name": "Major Agility", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": agility_tex, 
								"stats": [
												{
																"stat": "agility", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 40
												}, 
												{
																"stat": "agility", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.1
												}, 
								], 
				}, 

				"damage_per_swiftness": {
								"name": "Swift Damage", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": swiftness_boon_tex, 
								"stats": [
												{
																"stat": "damage_per_swiftness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12
												}, 
								], 
				}, 

				"armor_per_toughness": {
								"name": "Resilient Boons", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": toughness_boon_tex, 
								"stats": [
												{
																"stat": "armor_per_toughness", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.12
												}, 
								], 
				}, 

				"crit_per_precision": {
								"name": "Honed Precision", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": precision_boon_tex, 
								"stats": [
												{
																"stat": "crit_multi_per_precision", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.12
												}, 
								], 
				}, 

				"minor_boon_duration": {
								"name": "Fresh Boons", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": precision_boon_tex, 
								"stats": [
												{
																"stat": "boon_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.25
												}, 
								], 
				}, 

				"major_boon_duration": {
								"name": "Greater Boons", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": precision_boon_tex, 
								"stats": [
												{
																"stat": "boon_duration", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.5
												}, 
								], 
				}, 

				"minor_crit_resistance": {
								"name": "Critical Invariance", 
								"passive_type": PassiveTypes.SMALL, 
								"passive_texture": crit_tex, 
								"stats": [
												{
																"stat": "crit_resistance", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 0.07
												}, 
								], 
				}, 

				

				"keystone_golem_blood": {
								"name": "Golem Blood", 
								"passive_type": PassiveTypes.LARGE, 
								"passive_texture": life_tex, 
								"stats": [
												{
																"stat": "health_recovery_rate", 
																"scaling_type": Constants.ScalingType.PERCENT, 
																"amount": 0.2
												}, 
								], 
				}, 

				"keystone_phantom_shield": {
								"name": "Phantom Shielding", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_PHANTOM_SHIELD"]
				}, 

				"keystone_regenerative_flesh": {
								"name": "Regenerative Flesh", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_REGENERATIVE_FLESH"]
				}, 

				"keystone_vampiric_skin": {
								"name": "Vampiric Skin", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_VAMPIRIC_SKIN"]
				}, 

				"keystone_crocodile_skin": {
								"name": "Crocodile Skin", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_CROCODILE_SKIN"]
				}, 

				"keystone_hardened_flesh": {
								"name": "Hardened Flesh", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_HARDENED_FLESH"]
				}, 

				"keystone_spike_armor": {
								"name": "Spiked Carapace", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_SPIKE_ARMOR"]
				}, 

				"keystone_deflecting_armor": {
								"name": "Deflecting Armor", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_DEFLECTING_ARMOR"]
				}, 

				"keystone_adrenaline": {
								"name": "Adrenaline", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": movement_tex, 
								"stats": [
								], 
								"keystones": ["TREE_ADRENALINE"]
				}, 

				"keystone_endurance": {
								"name": "Endurance", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_ENDURANCE"]
				}, 

				"keystone_toxicologist": {
								"name": "Toxicologist", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": duration_tex, 
								"stats": [
								], 
								"keystones": ["TREE_TOXICOLOGIST"]
				}, 

				"keystone_brick": {
								"name": "Brick", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": armor_tex, 
								"stats": [
								], 
								"keystones": ["TREE_BRICK"]
				}, 

				"keystone_leecher": {
								"name": "Leecher", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": life_tex, 
								"stats": [
								], 
								"keystones": ["TREE_LEECHER"]
				}, 

				"keystone_potential_energy": {
								"name": "Damage Capacitor", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": duration_tex, 
								"stats": [
								], 
								"keystones": ["TREE_POTENTIAL_ENERGY"]
				}, 

				"keystone_infectious_malignancy": {
								"name": "Infectious Malignancy", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": curse_tex, 
								"stats": [
								], 
								"keystones": ["TREE_INFECTIOUS_MALIGNANCY"]
				}, 

				"keystone_curse_fragility": {
								"name": "Curse Fragility", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": curse_tex, 
								"stats": [
								], 
								"keystones": ["TREE_FRAGILE_CURSES"]
				}, 

				"keystone_impending_death": {
								"name": "Marked for Death", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": curse_tex, 
								"stats": [
								], 
								"keystones": ["TREE_IMPENDING_DEATH"]
				}, 

				"keystone_prolonged_depression": {
								"name": "Prolonged Depression", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": curse_tex, 
								"stats": [
								], 
								"keystones": ["TREE_CURSE_DURATION"]
				}, 

				"keystone_repeater": {
								"name": "Repeater", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_REPEATER"]
				}, 

				"keystone_ranger": {
								"name": "Way of the Ranger", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_RANGER"]
				}, 

				"keystone_magus": {
								"name": "Way of the Magus", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": aoe_tex, 
								"stats": [
								], 
								"keystones": ["TREE_MAGUS"]
				}, 

				"keystone_piercing_truth": {
								"name": "Piercing Truth", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": pierce_tex, 
								"stats": [
								], 
								"keystones": ["TREE_PIERCING_TRUTH"]
				}, 

				"keystone_cyclic_destruction": {
								"name": "Cyclic Destruction", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": aoe_tex, 
								"stats": [
								], 
								"keystones": ["TREE_CYCLE"]
				}, 

				"keystone_growing_pain": {
								"name": "Growing Pain", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": aoe_tex, 
								"stats": [
								], 
								"keystones": ["TREE_GROWING_PAIN"]
				}, 

				"keystone_quick_getaway": {
								"name": "Quick Getaway", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": movement_tex, 
								"stats": [
								], 
								"keystones": ["TREE_QUICK_GETAWAY"]
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

				"keystone_glass_cannon": {
								"name": "Glass Cannon", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": damage_tex, 
								"stats": [
								], 
								"keystones": ["TREE_GLASS_CANNON"]
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

				"keystone_precision_strikes": {
								"name": "Precision Strikes", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": vulnerable_tex, 
								"stats": [
												{
																"stat": "vulnerable_effect", 
																"scaling_type": Constants.ScalingType.MORE, 
																"amount": 0.2, 
												}, 
								], 
								"keystones": []
				}, 

				"keystone_temperature_delta": {
								"name": "Temperature Delta", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": chill_tex, 
								"stats": [
								], 
								"keystones": ["TREE_TEMPERATURE_DELTAS"]
				}, 

				"keystone_impending_contagion": {
								"name": "Contagious Infections", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": infected_tex, 
								"stats": [
													{
																"stat": "infection_count", 
																"scaling_type": Constants.ScalingType.FLAT, 
																"amount": 1.0
												}, 
								], 
								"keystones": []
				}, 

				"keystone_sanguine_decay": {
								"name": "Sanguine Decay", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": bleed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_SANGUINE_DECAY"]
				}, 

				"keystone_ricochet": {
								"name": "Ricochet", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": chain_tex, 
								"stats": [
								], 
								"keystones": ["TREE_RICOCHET"]
				}, 

				"keystone_saboteur": {
								"name": "Saboteur", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": bomb_tex, 
								"stats": [
								], 
								"keystones": ["TREE_SABOTEUR"]
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

				"keystone_siphoner": {
								"name": "Siphoner of Life", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": life_tex, 
								"stats": [
								], 
								"keystones": ["TREE_SIPHONER"]
				}, 

				"keystone_overloaded_shells": {
								"name": "Overloaded Shells", 
								"passive_type": PassiveTypes.KEYSTONE, 
								"passive_texture": projectile_speed_tex, 
								"stats": [
								], 
								"keystones": ["TREE_OVERLOADED_SHELLS"]
				}, 
}


func get_passive_config(passive_tag):
				if stats.has(passive_tag):
								return stats[passive_tag]

				return {}
