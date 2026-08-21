extends Node

var harrowing_cold_texture = load("res://sprites/uniques/harrowing_cold.png")
var ogre_talisman_texture = load("res://sprites/uniques/ogre_talisman.png")
var balanced_oppression_texture = load("res://sprites/uniques/balanced_oppression.png")
var crown_of_ice_texture = load("res://sprites/uniques/crown_of_ice.png")
var echoes_of_sin_texture = load("res://sprites/uniques/echoes_of_sin.png")
var strength_from_strength_texture = load("res://sprites/uniques/strength_from_strength.png")
var gladiators_resolve_texture = load("res://sprites/uniques/gladiators_resolve.png")
var fishing_rod_texture = load("res://sprites/uniques/fishing_rod.png")
var mercurial_venom_texture = load("res://sprites/uniques/mercurial_venom.png")
var skull_crusher_texture = load("res://sprites/uniques/skull_crusher.png")
var spreading_flames_texture = load("res://sprites/uniques/spreading_flames.png")
var cheetahs_texture = load("res://sprites/uniques/cheetahs.png")
var tinkerers_toys_texture = load("res://sprites/uniques/tinkerers_toys.png")
var goblins_girdle_texture = load("res://sprites/uniques/goblins_girdle.png")
var frozen_sludge_texture = preload("res://sprites/uniques/frozen_sludge.png")
var chill_burn_texture = load("res://sprites/uniques/chill_burn.png")
var echoing_fury_texture = load("res://sprites/uniques/echoing_fury.png")
var prismatic_bow_texture = load("res://sprites/uniques/prismatic_bow.png")
var bloody_knuckle_texture = load("res://sprites/uniques/bloody_knuckle.png")
var elder_ward_texture = load("res://sprites/uniques/elder_ward.png")
var expansion_charm_texture = load("res://sprites/uniques/expansion_charm.png")
var balance_of_power_texture = load("res://sprites/uniques/balance_of_power.png")


var pool = {
				"expansion_charm": {
								"texture": expansion_charm_texture, 
								"min_level_requirement": 30, 
								"unique": true, 
								"name": "Expansion Charm", 
								"flavor": "Increase your reach.", 
								"type": Genes.BaseType.MINOR_BUFF, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "unique_expansion_charm_radius", 
								}], 
								"suffixes": [], 
								"weight": 10, 
								"locked": true, 
				}, 

				"harrowing_cold": {
								"texture": harrowing_cold_texture, 
								"min_level_requirement": 1, 
								"unique": true, 
								"name": "Harrowing Cold", 
								"flavor": "It's cold outside...", 
								"type": Genes.BaseType.MINOR_BUFF, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "unique_harrowing_cold_damage", 
								}], 
								"suffixes": [
								{
												"mod_id": "unique_harrowing_cold_resistance", 
								}, 
								{
												"mod_id": "unique_harrowing_cold_ailment_chance", 
								}], 
								"weight": 50, 
								"locked": true, 
				}, 

				"balanced_oppression": {
								"texture": balanced_oppression_texture, 
								"min_level_requirement": 50, 
								"unique": true, 
								"name": "Balanced Oppression", 
								"flavor": "Some love the heat, some love the cold. Why not both?", 
								"type": Genes.BaseType.LIFE_BELT, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "balanced_oppression_penetration", 
								}], 
								"suffixes": [{
												"mod_id": "balanced_oppression_fire_resistance", 
								}, 
								{
												"mod_id": "balanced_oppression_cold_resistance", 
								}], 
								"weight": 50, 
								"locked": true
				}, 

				"crown_of_ice": {
								"texture": crown_of_ice_texture, 
								"min_level_requirement": 65, 
								"unique": true, 
								"name": "Ice Crown", 
								"flavor": "From the cold comes darkness.", 
								"type": Genes.BaseType.ARMOR_HELMET, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "crown_of_ice_conversion", 
								}], 
								"suffixes": [{
												"mod_id": "crown_of_ice_crit", 
								}], 
								"weight": 50, 
								"locked": true
				}, 

				"echoes_of_sin": {
								"texture": echoes_of_sin_texture, 
								"min_level_requirement": 40, 
								"unique": true, 
								"name": "Echoes of Sin", 
								"flavor": "Fires of the past continue to burn with a malignant taste.", 
								"type": Genes.BaseType.CASTER_RING, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "echoes_of_sin_conversion", 
								}, 
								{
												"mod_id": "echoes_of_sin_maximum_life", 
								}, 
								{
												"mod_id": "echoes_of_sin_fire_damage", 
								}], 
								"suffixes": [{
												"mod_id": "echoes_of_sin_fire_resistance", 
								}, 
								{
												"mod_id": "echoes_of_sin_toxic_resistance", 
								}], 
								"weight": 50, 
								"locked": true
				}, 

				"strength_from_strength": {
								"texture": strength_from_strength_texture, 
								"min_level_requirement": 15, 
								"unique": true, 
								"name": "Strength from Strength", 
								"flavor": "The best offense is a good defense.", 
								"type": Genes.BaseType.LIFE_AMULET, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "strength_from_strength_conversion", 
								}], 
								"suffixes": [
								{
												"mod_id": "strength_from_strength_life", 
								}], 
								"weight": 20, 
								"locked": true
				}, 

				"gladiators_resolve": {
								"texture": gladiators_resolve_texture, 
								"min_level_requirement": 15, 
								"unique": true, 
								"name": "Gladiators Resolve", 
								"flavor": "Sometimes one must take a hit to make it through to the end.", 
								"type": Genes.BaseType.HYBRID_BODY, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "gladiators_resolve_conversion", 
								}, 
								{
												"mod_id": "gladiators_resolve_cast_speed_penalty", 
								}, 
								{
												"mod_id": "gladiators_resolve_movement_speed", 
								}], 
								"suffixes": [
								{
												"mod_id": "gladiators_resolve_evasion", 
								}], 
								"weight": 20, 
								"locked": true
				}, 

				"fishing_rod": {
								"texture": fishing_rod_texture, 
								"min_level_requirement": 25, 
								"unique": true, 
								"name": "Fishing Rod", 
								"flavor": "It's not much, but it'll do for now.", 
								"type": Genes.BaseType.MELEE_WEAPON, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "fishing_rod_damage", 
								}], 
								"suffixes": [
								{
												"mod_id": "fishing_rod_radius", 
								}], 
								"weight": 50, 
								"locked": true
				}, 

				"mercurial_venom": {
								"texture": mercurial_venom_texture, 
								"min_level_requirement": 25, 
								"unique": true, 
								"name": "Mercurial Venom", 
								"flavor": "The toxin had a metallic shimmer.", 
								"type": Genes.BaseType.RESISTANT_RING, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "mercurial_venom_added_lightning_damage", 
								}, 
								{
												"mod_id": "mercurial_venom_added_toxic_damage", 
								}], 
								"suffixes": [
								{
												"mod_id": "mercurial_venom_lightning_chance", 
								}, 
								{
												"mod_id": "mercurial_venom_toxic_chance", 
								}, 
								{
												"mod_id": "mercurial_venom_penetration", 
								}], 
								"weight": 20, 
								"locked": true
				}, 

				"skull_crusher": {
								"texture": skull_crusher_texture, 
								"min_level_requirement": 100, 
								"unique": true, 
								"name": "Skull Crusher", 
								"flavor": "It's big. Big and heavy.", 
								"type": Genes.BaseType.MELEE_WEAPON, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "skull_crusher_damage", 
								}], 
								"suffixes": [{
												"mod_id": "skull_crusher_multi", 
								}, 
								{
												"mod_id": "skull_crusher_cast_speed", 
								}], 
								"weight": 50, 
								"locked": true
				}, 

				"spreading_flames": {
								"texture": spreading_flames_texture, 
								"min_level_requirement": 40, 
								"unique": true, 
								"name": "Spreading Flames", 
								"flavor": "When the wind catches a small flame, a forest is needed to put it out.", 
								"type": Genes.BaseType.RESISTANT_AMULET, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "spreading_flames_damage", 
								}, 
								{
												"mod_id": "spreading_flames_proliferate", 
								}], 
								"suffixes": [{
												"mod_id": "spreading_flames_fire_ailment", 
								}, 
								{
												"mod_id": "spreading_flames_fire_resistance", 
								}], 
								"weight": 15, 
								"locked": true
				}, 

				"ogre_talisman": {
								"texture": ogre_talisman_texture, 
								"min_level_requirement": 65, 
								"unique": true, 
								"name": "Ogre Talisman", 
								"flavor": "Fire burns hotter in a bigger heart.", 
								"type": Genes.BaseType.LIFE_AMULET, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "ogre_talisman_fire_damage", 
								}], 
								"suffixes": [{
												"mod_id": "ogre_talisman_health_damage", 
								}], 
								"weight": 50, 
								"locked": true
				}, 

				"cheatahs": {
								"texture": cheetahs_texture, 
								"min_level_requirement": 1, 
								"unique": true, 
								"name": "Cheat-ahs", 
								"flavor": "A little pep in your step.", 
								"type": Genes.BaseType.EVASION_BOOTS, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "cheatahs_movement_speed", 
								}], 
								"suffixes": [{
												"mod_id": "cheetahs_keystone", 
								}], 
								"weight": 100, 
								"locked": true
				}, 

				"tinkerers_toys": {
								"texture": tinkerers_toys_texture, 
								"min_level_requirement": 1, 
								"unique": true, 
								"name": "Tinkerer's Toy", 
								"flavor": "Sometimes, just sometimes, tinkering with a bomb isn't dangerous.", 
								"type": Genes.BaseType.EVASION_PANTS, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "tinkerers_keystone", 
								}], 
								"suffixes": [], 
								"weight": 50, 
								"locked": true
				}, 

				"frozen_sludge": {
								"texture": frozen_sludge_texture, 
								"min_level_requirement": 25, 
								"unique": true, 
								"name": "Frozen Sludge", 
								"flavor": "A feverish cold comes over your foes.", 
								"type": Genes.BaseType.ATTACK_RING, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "frozen_sludge_keystone", 
								}], 
								"suffixes": [], 
								"weight": 15, 
								"locked": true
				}, 

				"goblins_girdle": {
								"texture": goblins_girdle_texture, 
								"min_level_requirement": 75, 
								"unique": true, 
								"name": "Goblin's Girdle", 
								"flavor": "A goblin is alone without a tribe. A tribe of Buff-Boons.", 
								"type": Genes.BaseType.HYBRID_BELT, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "goblins_girdle_keystone", 
								}, {
												"mod_id": "goblins_girdle_armor", 
								}], 
								"suffixes": [{
												"mod_id": "goblins_girdle_regen", 
								}], 
								"weight": 20, 
								"locked": true
				}, 

				"chill_burn": {
								"texture": chill_burn_texture, 
								"min_level_requirement": 1, 
								"unique": true, 
								"name": "Chillburn", 
								"flavor": "Burning sensations are replaced by numbness to the pain.", 
								"type": Genes.BaseType.CASTER_RING, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "chill_burn_life", 
								}], 
								"suffixes": [{
												"mod_id": "chill_burn_keystone", 
								}], 
								"weight": 50, 
								"locked": true
				}, 

				"echoing_fury": {
								"texture": echoing_fury_texture, 
								"min_level_requirement": 75, 
								"unique": true, 
								"name": "Echoing Fury", 
								"flavor": "Memories of trauma linger amongst the survivors.", 
								"type": Genes.BaseType.LIFE_BODY, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "echoing_fury_keystone", 
								}], 
								"suffixes": [{
												"mod_id": "echoing_fury_resistance", 
								}], 
								"weight": 10, 
								"locked": true
				}, 

				"prismatic_bow": {
								"texture": prismatic_bow_texture, 
								"min_level_requirement": 100, 
								"unique": true, 
								"name": "Prismatic Bow", 
								"flavor": "Elemental dread at the pull of a string.", 
								"type": Genes.BaseType.RANGE_WEAPON, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "prismatic_bow_lightning_damage", 
								}, {
												"mod_id": "prismatic_bow_cold_damage", 
								}, {
												"mod_id": "prismatic_bow_fire_damage", 
								}], 
								"suffixes": [{
												"mod_id": "prismatic_bow_lightning_penetration", 
								}, {
												"mod_id": "prismatic_bow_cold_penetration", 
								}, {
												"mod_id": "prismatic_bow_fire_penetration", 
								}], 
								"weight": 10, 
								"locked": true
				}, 

				"bloody_knuckle": {
								"texture": bloody_knuckle_texture, 
								"min_level_requirement": 1, 
								"unique": true, 
								"name": "Bloody Knuckles", 
								"flavor": "Reminders of the skill you possess.", 
								"type": Genes.BaseType.ARMOR_GLOVES, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "bloody_knuckle_cast_speed", 
								}], 
								"suffixes": [], 
								"weight": 25, 
								"locked": true
				}, 

				"elder_ward": {
								"texture": elder_ward_texture, 
								"min_level_requirement": 150, 
								"unique": true, 
								"name": "Elder Ward", 
								"flavor": "Become a stalwart defender in critical times.", 
								"type": Genes.BaseType.ARMOR_SHIELD, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "elder_ward_life", 
								}, 
								{
												"mod_id": "elder_ward_block_chance", 
								}], 
								"suffixes": [{
												"mod_id": "elder_ward_crit_resistance", 
								}, 
								{
												"mod_id": "elder_ward_lgob", 
								}], 
								"weight": 10, 
								"locked": true
				}, 

				"balance_of_power": {
								"texture": balance_of_power_texture, 
								"min_level_requirement": 80, 
								"unique": true, 
								"name": "Balance of Power", 
								"flavor": "A steady stream of rotational power.", 
								"type": Genes.BaseType.RESISTANT_AMULET, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "balance_of_power_life", 
								}], 
								"suffixes": [{
												"mod_id": "balance_of_power_keystone", 
								}], 
								"weight": 5, 
								"locked": true
				}, 
}
