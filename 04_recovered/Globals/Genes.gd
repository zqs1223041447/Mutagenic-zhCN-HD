extends Node

var sound_keystone = preload("res://Sounds/UI/Crafting/change_keystone.wav")
var sound_recombinate = preload("res://Sounds/UI/Crafting/recombinate.wav")
var sound_craft = preload("res://Sounds/UI/Crafting/scramble.wav")

var lesser_icon = preload("res://sprites/gui/gene_lesser.png")

var helmet_slot_icon = preload("res://sprites/gui/equipment/helmet_slot.png")
var body_slot_icon = preload("res://sprites/gui/equipment/body_slot.png")
var pant_slot_icon = preload("res://sprites/gui/equipment/pants_slot.png")
var ring_slot_icon = preload("res://sprites/gui/equipment/ring_slot.png")
var amulet_slot_icon = preload("res://sprites/gui/equipment/amulet_slot.png")
var weapon_slot_icon = preload("res://sprites/gui/equipment/weapon_slot.png")
var belt_slot_icon = preload("res://sprites/gui/equipment/belt_slot.png")
var glove_slot_icon = preload("res://sprites/gui/equipment/glove_slot.png")
var boots_slot_icon = preload("res://sprites/gui/equipment/boots_slot.png")
var minor_buff_slot_icon = preload("res://sprites/base_types/minor_buff.png")


var melee_weapon_icon = preload("res://sprites/base_types/melee_weapon.png")
var caster_weapon_icon = preload("res://sprites/base_types/caster_weapon.png")
var ranged_weapon_icon = preload("res://sprites/base_types/ranged_weapon.png")

var armor_shield_icon = preload("res://sprites/base_types/armor_shield.png")
var evasion_shield_icon = preload("res://sprites/base_types/evasion_shield.png")
var hybrid_shield_icon = preload("res://sprites/base_types/hybrid_shield.png")
var life_shield_icon = preload("res://sprites/base_types/life_shield.png")
var caster_shield_icon = preload("res://sprites/base_types/caster_shield.png")

var armor_body_icon = preload("res://sprites/base_types/armor_body.png")
var evasion_body_icon = preload("res://sprites/base_types/evasion_body.png")
var hybrid_body_icon = preload("res://sprites/base_types/hybrid_body.png")
var life_body_icon = preload("res://sprites/base_types/life_body.png")
var caster_body_icon = preload("res://sprites/base_types/caster_body.png")

var evasion_helmet_icon = preload("res://sprites/base_types/evasion_helmet.png")
var armor_helmet_icon = preload("res://sprites/base_types/armor_helmet.png")
var hybrid_helmet_icon = preload("res://sprites/base_types/hybrid_helmet.png")
var life_helmet_icon = preload("res://sprites/base_types/life_helmet.png")
var caster_helmet_icon = preload("res://sprites/base_types/caster_helmet.png")

var armor_belt_icon = preload("res://sprites/base_types/armor_belt.png")
var evasion_belt_icon = preload("res://sprites/base_types/evasion_belt.png")
var hybrid_belt_icon = preload("res://sprites/base_types/hybrid_belt.png")
var life_belt_icon = preload("res://sprites/base_types/life_belt.png")
var caster_belt_icon = preload("res://sprites/base_types/caster_belt.png")

var armor_gloves_icon = preload("res://sprites/base_types/armor_gloves.png")
var evasion_gloves_icon = preload("res://sprites/base_types/evasion_gloves.png")
var hybrid_gloves_icon = preload("res://sprites/base_types/hybrid_gloves.png")
var life_gloves_icon = preload("res://sprites/base_types/life_gloves.png")
var caster_gloves_icon = preload("res://sprites/base_types/caster_gloves.png")

var armor_boots_icon = preload("res://sprites/base_types/armor_boots.png")
var evasion_boots_icon = preload("res://sprites/base_types/evasion_boots.png")
var hybrid_boots_icon = preload("res://sprites/base_types/hybrid_boots.png")
var life_boots_icon = preload("res://sprites/base_types/life_boots.png")
var caster_boots_icon = preload("res://sprites/base_types/caster_boots.png")


var armor_pants_icon = preload("res://sprites/base_types/armor_pants.png")
var evasion_pants_icon = preload("res://sprites/base_types/evasion_pants.png")
var hybrid_pants_icon = preload("res://sprites/base_types/hybrid_pants.png")
var life_pants_icon = preload("res://sprites/base_types/life_pants.png")
var caster_pants_icon = preload("res://sprites/base_types/caster_pants.png")

var attack_ring_icon = preload("res://sprites/base_types/attack_ring.png")
var caster_ring_icon = preload("res://sprites/base_types/caster_ring.png")
var life_ring_icon = preload("res://sprites/base_types/life_ring.png")
var resistant_ring_icon = preload("res://sprites/base_types/resistant_ring.png")

var attack_amulet_icon = preload("res://sprites/base_types/attack_amulet.png")
var caster_amulet_icon = preload("res://sprites/base_types/caster_amulet.png")
var life_amulet_icon = preload("res://sprites/base_types/life_amulet.png")
var resistant_amulet_icon = preload("res://sprites/base_types/resistant_amulet.png")

var minor_buff_icon = preload("res://sprites/base_types/minor_buff.png")

signal genes_changed
signal gene_edited

var GeneSlot = {
				"WEAPON": "WEP", 
				"BODY": "BOD", 
				"HELMET": "HEL", 
				"AMULET": "AMU", 
				"RING": "RIN", 
				"BELT": "BEL", 
				"GLOVES": "GLO", 
				"BOOTS": "BOO", 
				"PANTS": "PAN", 
				"MINOR": "MIN", 
}

var BaseType = {
				"MELEE_WEAPON": "MELEE_WEAPON", 
				"CASTER_WEAPON": "CASTER_WEAPON", 
				"RANGE_WEAPON": "RANGE_WEAPON", 

				"EVASION_SHIELD": "EVASION_SHIELD", 
				"ARMOR_SHIELD": "ARMOR_SHIELD", 
				"HYBRID_SHIELD": "HYBRID_SHIELD", 
				"LIFE_SHIELD": "LIFE_SHIELD", 
				"CASTER_SHIELD": "CASTER_SHIELD", 

				"EVASION_BODY": "EVASION_BODY", 
				"ARMOR_BODY": "ARMOR_BODY", 
				"HYBRID_BODY": "HYBRID_BODY", 
				"LIFE_BODY": "LIFE_BODY", 
				"CASTER_BODY": "CASTER_BODY", 

				"EVASION_HELMET": "EVASION_HELMET", 
				"ARMOR_HELMET": "ARMOR_HELMET", 
				"HYBRID_HELMET": "HYBRID_HELMET", 
				"LIFE_HELMET": "LIFE_HELMET", 
				"CASTER_HELMET": "CASTER_HELMET", 

				"ARMOR_BELT": "ARMOR_BELT", 
				"EVASION_BELT": "EVASION_BELT", 
				"HYBRID_BELT": "HYBRID_BELT", 
				"LIFE_BELT": "LIFE_BELT", 
				"CASTER_BELT": "CASTER_BELT", 

				"ARMOR_GLOVES": "ARMOR_GLOVES", 
				"EVASION_GLOVES": "EVASION_GLOVES", 
				"HYBRID_GLOVES": "HYBRID_GLOVES", 
				"LIFE_GLOVES": "LIFE_GLOVES", 
				"CASTER_GLOVES": "CASTER_GLOVES", 

				"ARMOR_BOOTS": "ARMOR_BOOTS", 
				"EVASION_BOOTS": "EVASION_BOOTS", 
				"HYBRID_BOOTS": "HYBRID_BOOTS", 
				"LIFE_BOOTS": "LIFE_BOOTS", 
				"CASTER_BOOTS": "CASTER_BOOTS", 

				"ARMOR_PANTS": "ARMOR_PANTS", 
				"EVASION_PANTS": "EVASION_PANTS", 
				"HYBRID_PANTS": "HYBRID_PANTS", 
				"LIFE_PANTS": "LIFE_PANTS", 
				"CASTER_PANTS": "CASTER_PANTS", 

				"ATTACK_RING": "ATTACK_RING", 
				"CASTER_RING": "CASTER_RING", 
				"RESISTANT_RING": "RESISTANT_RING", 
				"LIFE_RING": "LIFE_RING", 

				"ATTACK_AMULET": "ATTACK_AMULET", 
				"CASTER_AMULET": "CASTER_AMULET", 
				"RESISTANT_AMULET": "RESISTANT_AMULET", 
				"LIFE_AMULET": "LIFE_AMULET", 

				"MINOR_BUFF": "MINOR_BUFF"
}

var weapon_type_list = [
				BaseType.MELEE_WEAPON, 
				BaseType.CASTER_WEAPON, 
				BaseType.RANGE_WEAPON
]

func random_weapon_base_type():
				return weapon_type_list[randi() % len(weapon_type_list)]

var name_for_base_type = {
				BaseType.MELEE_WEAPON: "Melee Weapon", 
				BaseType.CASTER_WEAPON: "Caster Weapon", 
				BaseType.RANGE_WEAPON: "Range Weapon", 

				BaseType.EVASION_SHIELD: "Evasion Shield", 
				BaseType.ARMOR_SHIELD: "Armor Shield", 
				BaseType.HYBRID_SHIELD: "Hybrid Shield", 
				BaseType.LIFE_SHIELD: "Life Shield", 
				BaseType.CASTER_SHIELD: "Offensive Shield", 

				BaseType.EVASION_BODY: "Evasion Body", 
				BaseType.ARMOR_BODY: "Armor Body", 
				BaseType.HYBRID_BODY: "Hybrid Body", 
				BaseType.LIFE_BODY: "Life Body", 
				BaseType.CASTER_BODY: "Offensive Body", 

				BaseType.EVASION_HELMET: "Evasion Helmet", 
				BaseType.ARMOR_HELMET: "Armor Helmet", 
				BaseType.HYBRID_HELMET: "Hybrid Helmet", 
				BaseType.LIFE_HELMET: "Life Helmet", 
				BaseType.CASTER_HELMET: "Offensive Helmet", 

				BaseType.ARMOR_BELT: "Armor Belt", 
				BaseType.EVASION_BELT: "Evasion Belt", 
				BaseType.HYBRID_BELT: "Hybrid Belt", 
				BaseType.LIFE_BELT: "Life Belt", 
				BaseType.CASTER_BELT: "Offensive Belt", 

				BaseType.ARMOR_GLOVES: "Armor Gloves", 
				BaseType.EVASION_GLOVES: "Evasion Gloves", 
				BaseType.HYBRID_GLOVES: "Hybrid Gloves", 
				BaseType.LIFE_GLOVES: "Life Gloves", 
				BaseType.CASTER_GLOVES: "Offensive Gloves", 

				BaseType.ARMOR_BOOTS: "Armor Boots", 
				BaseType.EVASION_BOOTS: "Evasion Boots", 
				BaseType.HYBRID_BOOTS: "Hybrid Boots", 
				BaseType.LIFE_BOOTS: "Life Boots", 
				BaseType.CASTER_BOOTS: "Offensive Boots", 

				BaseType.ARMOR_PANTS: "Armor Pants", 
				BaseType.EVASION_PANTS: "Evasion Pants", 
				BaseType.HYBRID_PANTS: "Hybrid Pants", 
				BaseType.LIFE_PANTS: "Life Pants", 
				BaseType.CASTER_PANTS: "Offensive Pants", 

				BaseType.ATTACK_RING: "Attack Ring", 
				BaseType.CASTER_RING: "Offensive Ring", 
				BaseType.RESISTANT_RING: "Resistant Ring", 
				BaseType.LIFE_RING: "Life Ring", 

				BaseType.ATTACK_AMULET: "Attack Amulet", 
				BaseType.CASTER_AMULET: "Offensive Amulet", 
				BaseType.RESISTANT_AMULET: "Resistant Amulet", 
				BaseType.LIFE_AMULET: "Life Amulet", 

				BaseType.MINOR_BUFF: "Utility Buff"
}

var _implicit_count_for_base_type = {
				BaseType.MELEE_WEAPON: 1, 
				BaseType.CASTER_WEAPON: 1, 
				BaseType.RANGE_WEAPON: 1, 

				BaseType.EVASION_SHIELD: 1, 
				BaseType.ARMOR_SHIELD: 1, 
				BaseType.HYBRID_SHIELD: 1, 
				BaseType.LIFE_SHIELD: 1, 
				BaseType.CASTER_SHIELD: 1, 

				BaseType.EVASION_BODY: 1, 
				BaseType.ARMOR_BODY: 1, 
				BaseType.HYBRID_BODY: 2, 
				BaseType.LIFE_BODY: 1, 
				BaseType.CASTER_BODY: 1, 

				BaseType.EVASION_HELMET: 1, 
				BaseType.ARMOR_HELMET: 1, 
				BaseType.HYBRID_HELMET: 2, 
				BaseType.LIFE_HELMET: 1, 
				BaseType.CASTER_HELMET: 1, 

				BaseType.ARMOR_BELT: 1, 
				BaseType.EVASION_BELT: 1, 
				BaseType.HYBRID_BELT: 2, 
				BaseType.LIFE_BELT: 1, 
				BaseType.CASTER_BELT: 1, 

				BaseType.ARMOR_GLOVES: 1, 
				BaseType.EVASION_GLOVES: 1, 
				BaseType.HYBRID_GLOVES: 2, 
				BaseType.LIFE_GLOVES: 1, 
				BaseType.CASTER_GLOVES: 1, 

				BaseType.ARMOR_BOOTS: 1, 
				BaseType.EVASION_BOOTS: 1, 
				BaseType.HYBRID_BOOTS: 2, 
				BaseType.LIFE_BOOTS: 1, 
				BaseType.CASTER_BOOTS: 1, 

				BaseType.ARMOR_PANTS: 1, 
				BaseType.EVASION_PANTS: 1, 
				BaseType.HYBRID_PANTS: 2, 
				BaseType.LIFE_PANTS: 1, 
				BaseType.CASTER_PANTS: 1, 

				BaseType.ATTACK_RING: 1, 
				BaseType.CASTER_RING: 1, 
				BaseType.RESISTANT_RING: 1, 
				BaseType.LIFE_RING: 1, 

				BaseType.ATTACK_AMULET: 1, 
				BaseType.CASTER_AMULET: 1, 
				BaseType.RESISTANT_AMULET: 1, 
				BaseType.LIFE_AMULET: 1, 

				BaseType.MINOR_BUFF: 0
}

var _texture_for_base_type = {
				BaseType.MELEE_WEAPON: melee_weapon_icon, 
				BaseType.CASTER_WEAPON: caster_weapon_icon, 
				BaseType.RANGE_WEAPON: ranged_weapon_icon, 

				BaseType.EVASION_SHIELD: evasion_shield_icon, 
				BaseType.ARMOR_SHIELD: armor_shield_icon, 
				BaseType.HYBRID_SHIELD: hybrid_shield_icon, 
				BaseType.LIFE_SHIELD: life_shield_icon, 
				BaseType.CASTER_SHIELD: caster_shield_icon, 

				BaseType.EVASION_BODY: evasion_body_icon, 
				BaseType.ARMOR_BODY: armor_body_icon, 
				BaseType.HYBRID_BODY: hybrid_body_icon, 
				BaseType.LIFE_BODY: life_body_icon, 
				BaseType.CASTER_BODY: caster_body_icon, 

				BaseType.EVASION_HELMET: evasion_helmet_icon, 
				BaseType.ARMOR_HELMET: armor_helmet_icon, 
				BaseType.HYBRID_HELMET: hybrid_helmet_icon, 
				BaseType.LIFE_HELMET: life_helmet_icon, 
				BaseType.CASTER_HELMET: caster_helmet_icon, 

				BaseType.ARMOR_BELT: armor_belt_icon, 
				BaseType.EVASION_BELT: evasion_belt_icon, 
				BaseType.HYBRID_BELT: hybrid_belt_icon, 
				BaseType.LIFE_BELT: life_belt_icon, 
				BaseType.CASTER_BELT: caster_belt_icon, 

				BaseType.ARMOR_GLOVES: armor_gloves_icon, 
				BaseType.EVASION_GLOVES: evasion_gloves_icon, 
				BaseType.HYBRID_GLOVES: hybrid_gloves_icon, 
				BaseType.LIFE_GLOVES: life_gloves_icon, 
				BaseType.CASTER_GLOVES: caster_gloves_icon, 

				BaseType.ARMOR_BOOTS: armor_boots_icon, 
				BaseType.EVASION_BOOTS: evasion_boots_icon, 
				BaseType.HYBRID_BOOTS: hybrid_boots_icon, 
				BaseType.LIFE_BOOTS: life_boots_icon, 
				BaseType.CASTER_BOOTS: caster_boots_icon, 

				BaseType.ARMOR_PANTS: armor_pants_icon, 
				BaseType.EVASION_PANTS: evasion_pants_icon, 
				BaseType.HYBRID_PANTS: hybrid_pants_icon, 
				BaseType.LIFE_PANTS: life_pants_icon, 
				BaseType.CASTER_PANTS: caster_pants_icon, 

				BaseType.ATTACK_RING: attack_ring_icon, 
				BaseType.CASTER_RING: caster_ring_icon, 
				BaseType.RESISTANT_RING: resistant_ring_icon, 
				BaseType.LIFE_RING: life_ring_icon, 

				BaseType.ATTACK_AMULET: attack_amulet_icon, 
				BaseType.CASTER_AMULET: caster_amulet_icon, 
				BaseType.RESISTANT_AMULET: resistant_amulet_icon, 
				BaseType.LIFE_AMULET: life_amulet_icon, 

				BaseType.MINOR_BUFF: minor_buff_icon, 
}

var _slot_for_base = {
				BaseType.MELEE_WEAPON: GeneSlot.WEAPON, 
				BaseType.RANGE_WEAPON: GeneSlot.WEAPON, 
				BaseType.CASTER_WEAPON: GeneSlot.WEAPON, 

				BaseType.EVASION_SHIELD: GeneSlot.WEAPON, 
				BaseType.ARMOR_SHIELD: GeneSlot.WEAPON, 
				BaseType.HYBRID_SHIELD: GeneSlot.WEAPON, 
				BaseType.LIFE_SHIELD: GeneSlot.WEAPON, 
				BaseType.CASTER_SHIELD: GeneSlot.WEAPON, 

				BaseType.EVASION_BODY: GeneSlot.BODY, 
				BaseType.ARMOR_BODY: GeneSlot.BODY, 
				BaseType.HYBRID_BODY: GeneSlot.BODY, 
				BaseType.LIFE_BODY: GeneSlot.BODY, 
				BaseType.CASTER_BODY: GeneSlot.BODY, 

				BaseType.EVASION_HELMET: GeneSlot.HELMET, 
				BaseType.ARMOR_HELMET: GeneSlot.HELMET, 
				BaseType.HYBRID_HELMET: GeneSlot.HELMET, 
				BaseType.LIFE_HELMET: GeneSlot.HELMET, 
				BaseType.CASTER_HELMET: GeneSlot.HELMET, 

				BaseType.ARMOR_BELT: GeneSlot.BELT, 
				BaseType.EVASION_BELT: GeneSlot.BELT, 
				BaseType.HYBRID_BELT: GeneSlot.BELT, 
				BaseType.LIFE_BELT: GeneSlot.BELT, 
				BaseType.CASTER_BELT: GeneSlot.BELT, 

				BaseType.ARMOR_GLOVES: GeneSlot.GLOVES, 
				BaseType.EVASION_GLOVES: GeneSlot.GLOVES, 
				BaseType.HYBRID_GLOVES: GeneSlot.GLOVES, 
				BaseType.LIFE_GLOVES: GeneSlot.GLOVES, 
				BaseType.CASTER_GLOVES: GeneSlot.GLOVES, 

				BaseType.ARMOR_BOOTS: GeneSlot.BOOTS, 
				BaseType.EVASION_BOOTS: GeneSlot.BOOTS, 
				BaseType.HYBRID_BOOTS: GeneSlot.BOOTS, 
				BaseType.LIFE_BOOTS: GeneSlot.BOOTS, 
				BaseType.CASTER_BOOTS: GeneSlot.BOOTS, 

				BaseType.ARMOR_PANTS: GeneSlot.PANTS, 
				BaseType.EVASION_PANTS: GeneSlot.PANTS, 
				BaseType.HYBRID_PANTS: GeneSlot.PANTS, 
				BaseType.LIFE_PANTS: GeneSlot.PANTS, 
				BaseType.CASTER_PANTS: GeneSlot.PANTS, 

				BaseType.ATTACK_RING: GeneSlot.RING, 
				BaseType.CASTER_RING: GeneSlot.RING, 
				BaseType.RESISTANT_RING: GeneSlot.RING, 
				BaseType.LIFE_RING: GeneSlot.RING, 

				BaseType.ATTACK_AMULET: GeneSlot.AMULET, 
				BaseType.CASTER_AMULET: GeneSlot.AMULET, 
				BaseType.RESISTANT_AMULET: GeneSlot.AMULET, 
				BaseType.LIFE_AMULET: GeneSlot.AMULET, 

				BaseType.MINOR_BUFF: GeneSlot.MINOR, 
}

onready var _mods_for_base_type = {
				BaseType.MELEE_WEAPON: MeleeWeaponMods, 
				BaseType.RANGE_WEAPON: RangeWeaponMods, 
				BaseType.CASTER_WEAPON: CasterWeaponMods, 

				BaseType.EVASION_SHIELD: EvasionShieldMods, 
				BaseType.ARMOR_SHIELD: ArmorShieldMods, 
				BaseType.HYBRID_SHIELD: HybridShieldMods, 
				BaseType.LIFE_SHIELD: LifeShieldMods, 
				BaseType.CASTER_SHIELD: CasterShieldMods, 

				BaseType.EVASION_BODY: EvasionBodyMods, 
				BaseType.ARMOR_BODY: ArmorBodyMods, 
				BaseType.HYBRID_BODY: HybridBodyMods, 
				BaseType.LIFE_BODY: LifeBodyMods, 
				BaseType.CASTER_BODY: CasterBodyMods, 

				BaseType.EVASION_HELMET: EvasionHelmetMods, 
				BaseType.ARMOR_HELMET: ArmorHelmetMods, 
				BaseType.HYBRID_HELMET: HybridHelmetMods, 
				BaseType.LIFE_HELMET: LifeHelmetMods, 
				BaseType.CASTER_HELMET: CasterHelmetMods, 

				BaseType.ARMOR_BELT: ArmorBeltMods, 
				BaseType.EVASION_BELT: EvasionBeltMods, 
				BaseType.HYBRID_BELT: HybridBeltMods, 
				BaseType.LIFE_BELT: LifeBeltMods, 
				BaseType.CASTER_BELT: CasterBeltMods, 

				BaseType.ARMOR_GLOVES: ArmorGlovesMods, 
				BaseType.EVASION_GLOVES: EvasionGlovesMods, 
				BaseType.HYBRID_GLOVES: HybridGlovesMods, 
				BaseType.LIFE_GLOVES: LifeGlovesMods, 
				BaseType.CASTER_GLOVES: CasterGlovesMods, 

				BaseType.ARMOR_BOOTS: ArmorBootsMods, 
				BaseType.EVASION_BOOTS: EvasionBootsMods, 
				BaseType.HYBRID_BOOTS: HybridBootsMods, 
				BaseType.LIFE_BOOTS: LifeBootsMods, 
				BaseType.CASTER_BOOTS: CasterBootsMods, 

				BaseType.ARMOR_PANTS: ArmorPantsMods, 
				BaseType.EVASION_PANTS: EvasionPantsMods, 
				BaseType.HYBRID_PANTS: HybridPantsMods, 
				BaseType.LIFE_PANTS: LifePantsMods, 
				BaseType.CASTER_PANTS: CasterPantsMods, 

				BaseType.ATTACK_RING: AttackRingMods, 
				BaseType.CASTER_RING: CasterRingMods, 
				BaseType.RESISTANT_RING: ResistantRingMods, 
				BaseType.LIFE_RING: LifeRingMods, 

				BaseType.ATTACK_AMULET: AttackAmuletMods, 
				BaseType.CASTER_AMULET: CasterAmuletMods, 
				BaseType.RESISTANT_AMULET: ResistantAmuletMods, 
				BaseType.LIFE_AMULET: LifeAmuletMods, 

				BaseType.MINOR_BUFF: MinorMods, 
}

onready var _drop_only_mods_for_base_type = {
				BaseType.MELEE_WEAPON: DropMeleeWeaponMods, 
				BaseType.RANGE_WEAPON: DropRangeWeaponMods, 
				BaseType.CASTER_WEAPON: DropCasterWeaponMods, 

				BaseType.EVASION_SHIELD: DropShieldMods, 
				BaseType.ARMOR_SHIELD: DropShieldMods, 
				BaseType.HYBRID_SHIELD: DropShieldMods, 
				BaseType.LIFE_SHIELD: DropShieldMods, 
				BaseType.CASTER_SHIELD: DropShieldMods, 

				BaseType.EVASION_BODY: DropBodyMods, 
				BaseType.ARMOR_BODY: DropBodyMods, 
				BaseType.HYBRID_BODY: DropBodyMods, 
				BaseType.LIFE_BODY: DropBodyMods, 
				BaseType.CASTER_BODY: DropBodyMods, 

				BaseType.EVASION_HELMET: DropHelmetMods, 
				BaseType.ARMOR_HELMET: DropHelmetMods, 
				BaseType.HYBRID_HELMET: DropHelmetMods, 
				BaseType.LIFE_HELMET: DropHelmetMods, 
				BaseType.CASTER_HELMET: DropHelmetMods, 

				BaseType.ARMOR_BELT: DropBeltMods, 
				BaseType.EVASION_BELT: DropBeltMods, 
				BaseType.HYBRID_BELT: DropBeltMods, 
				BaseType.LIFE_BELT: DropBeltMods, 
				BaseType.CASTER_BELT: DropBeltMods, 

				BaseType.ARMOR_GLOVES: DropGlovesMods, 
				BaseType.EVASION_GLOVES: DropGlovesMods, 
				BaseType.HYBRID_GLOVES: DropGlovesMods, 
				BaseType.LIFE_GLOVES: DropGlovesMods, 
				BaseType.CASTER_GLOVES: DropGlovesMods, 

				BaseType.ARMOR_BOOTS: DropBootsMods, 
				BaseType.EVASION_BOOTS: DropBootsMods, 
				BaseType.HYBRID_BOOTS: DropBootsMods, 
				BaseType.LIFE_BOOTS: DropBootsMods, 
				BaseType.CASTER_BOOTS: DropBootsMods, 

				BaseType.ARMOR_PANTS: DropPantsMods, 
				BaseType.EVASION_PANTS: DropPantsMods, 
				BaseType.HYBRID_PANTS: DropPantsMods, 
				BaseType.LIFE_PANTS: DropPantsMods, 
				BaseType.CASTER_PANTS: DropPantsMods, 

				BaseType.ATTACK_RING: DropRingMods, 
				BaseType.CASTER_RING: DropRingMods, 
				BaseType.RESISTANT_RING: DropRingMods, 
				BaseType.LIFE_RING: DropRingMods, 

				BaseType.ATTACK_AMULET: DropAmuletMods, 
				BaseType.CASTER_AMULET: DropAmuletMods, 
				BaseType.RESISTANT_AMULET: DropAmuletMods, 
				BaseType.LIFE_AMULET: DropAmuletMods, 

				BaseType.MINOR_BUFF: DropMinorMods, 
}

var icon_for_gene_slot = {
				GeneSlot.WEAPON: weapon_slot_icon, 
				GeneSlot.BODY: body_slot_icon, 
				GeneSlot.HELMET: helmet_slot_icon, 
				GeneSlot.AMULET: amulet_slot_icon, 
				GeneSlot.RING: ring_slot_icon, 
				GeneSlot.BELT: belt_slot_icon, 
				GeneSlot.GLOVES: glove_slot_icon, 
				GeneSlot.BOOTS: boots_slot_icon, 
				GeneSlot.PANTS: pant_slot_icon, 
				GeneSlot.MINOR: minor_buff_slot_icon, 
}


var name_for_gene_type = {
				GeneSlot.WEAPON: "Weapon/Shield", 
				GeneSlot.BODY: "Chest Piece", 
				GeneSlot.HELMET: "Helmet", 
				GeneSlot.AMULET: "Amulet", 
				GeneSlot.RING: "Ring", 
				GeneSlot.BELT: "Belt", 
				GeneSlot.GLOVES: "Gloves", 
				GeneSlot.BOOTS: "Boots", 
				GeneSlot.PANTS: "Pants", 
				GeneSlot.MINOR: "Minor Buff", 
}

const CraftType = {
				"SCRAMBLE": "SCRAMBLE", 
				"SCRAMBLE_LUCKY": "SCRAMBLE_LUCKY", 
				"SCRAMBLE_ULTRA": "SCRAMBLE_ULTRA", 
				"CLEAR": "CLEAR", 
				"EXTRACT": "EXTRACT", 
				"SPLICE": "SPLICE", 
				"RECOMBINATE": "RECOMBINATE", 
				"GAMMA": "GAMMA", 
				"RECESSIVE": "RECESSIVE", 
				"COSMIC": "COSMIC", 
				"LOCK_MOD": "LOCK_MOD", 
				"UNLOCK_MOD": "UNLOCK_MOD", 
				"SCRAMBLE_PREFIXES": "SCRAMBLE_PREFIXES", 
				"SCRAMBLE_SUFFIXES": "SCRAMBLE_SUFFIXES", 
				"UPGRADE_TIER": "UPGRADE_TIER", 
				"LOCK_SPECIFIC_MOD": "LOCK_SPECIFIC_MOD", 
				"UNLOCK_SPECIFIC_MOD": "UNLOCK_SPECIFIC_MOD", 
}

const craft_name = {
				CraftType.CLEAR: "Clear", 
				CraftType.EXTRACT: "Store", 
				CraftType.SPLICE: "Restore", 

				
				CraftType.SCRAMBLE: "Scramble", 
				CraftType.SCRAMBLE_LUCKY: "Lucky Scramble", 
				CraftType.SCRAMBLE_ULTRA: "Godly Scramble", 
				CraftType.GAMMA: "Add Random Mod", 
				CraftType.RECESSIVE: "Remove Random Mod", 
				CraftType.RECOMBINATE: "Recombinate", 
				CraftType.COSMIC: "Reroll Mod Values", 
				CraftType.LOCK_MOD: "Permanently Lock Random Mod", 
				CraftType.UNLOCK_MOD: "Unlock Random Mod", 
				CraftType.SCRAMBLE_PREFIXES: "Scramble Prefixes", 
				CraftType.SCRAMBLE_SUFFIXES: "Scramble Suffixes", 
				CraftType.UPGRADE_TIER: "Upgrade Random Mod", 
				CraftType.LOCK_SPECIFIC_MOD: "Lock Mod", 
				CraftType.UNLOCK_SPECIFIC_MOD: "Unlock Mod", 
}

const craft_costs = {
				
				CraftType.CLEAR: [], 
				CraftType.EXTRACT: [{"orb": Constants.OrbType.BLUE, "cost": 1}], 
				CraftType.SPLICE: [{"orb": Constants.OrbType.BLUE, "cost": 1}], 

				
				CraftType.SCRAMBLE: [{"orb": Constants.OrbType.BLUE, "cost": 1}], 
				CraftType.SCRAMBLE_LUCKY: [{"orb": Constants.OrbType.BLUE, "cost": 5}], 
				CraftType.SCRAMBLE_ULTRA: [{"orb": Constants.OrbType.BLUE, "cost": 25}], 
				CraftType.GAMMA: [{"orb": Constants.OrbType.RED, "cost": 1}], 
				CraftType.RECESSIVE: [{"orb": Constants.OrbType.RED, "cost": 1}], 
				CraftType.RECOMBINATE: [{"orb": Constants.OrbType.CORRUPTION, "cost": 1}], 
				CraftType.COSMIC: [{"orb": Constants.OrbType.GREEN, "cost": 1}], 
				CraftType.LOCK_MOD: [{"orb": Constants.OrbType.GOLD, "cost": 1}], 
				CraftType.UNLOCK_MOD: [{"orb": Constants.OrbType.GOLD, "cost": 1}], 
				CraftType.SCRAMBLE_PREFIXES: [{"orb": Constants.OrbType.BLUE, "cost": 10}, {"orb": Constants.OrbType.RED, "cost": 3}], 
				CraftType.SCRAMBLE_SUFFIXES: [{"orb": Constants.OrbType.BLUE, "cost": 10}, {"orb": Constants.OrbType.RED, "cost": 3}], 
				CraftType.UPGRADE_TIER: [{"orb": Constants.OrbType.RED, "cost": 10}, {"orb": Constants.OrbType.GREEN, "cost": 20}, {"orb": Constants.OrbType.GOLD, "cost": 5}], 
				CraftType.LOCK_SPECIFIC_MOD: [], 
				CraftType.UNLOCK_SPECIFIC_MOD: [], 
}

var base_types_for_slot = {}

func mod_sorter(a, b):
				var a_key = a.has("keystone")
				var b_key = b.has("keystone")
				if a_key and b_key:
								return Keystones.keystones[a.keystone].name < Keystones.keystones[b.keystone].name
				if a_key:
								return true
				if b_key:
								return false

				return StatsInfo.skill_sort_list.find(a.stat) < StatsInfo.skill_sort_list.find(b.stat)

const PURCHASE_COST = 5

func mods_for_base_type(base_type):
				if _mods_for_base_type.has(base_type):
								return _mods_for_base_type[base_type]
				print("Invalid gene type: ", base_type)
				get_tree().quit()

func implicit_count_for_base_type(base_type):
				if _implicit_count_for_base_type.has(base_type):
								return _implicit_count_for_base_type[base_type]
				print("Invalid base type for implicit count: ", base_type)
				get_tree().quit()

func slot_for_base(base):
				if _slot_for_base.has(base):
								return _slot_for_base[base]
				print("Error: Could not find slot for base type: ", base, name_for_base_type[base])
				return null

func texture_for_base_type(base):
				if _texture_for_base_type.has(base):
								return _texture_for_base_type[base]
				print("Error: Could not find texture for base type: ", base, name_for_base_type[base])
				return null

func is_shield(base_type):
				return "SHIELD" in base_type

func drop_only_mods_for_base_type(base_type):
				if _drop_only_mods_for_base_type.has(base_type):
								return _drop_only_mods_for_base_type[base_type]

				print("Invalid base type for drop only: ", base_type)
				get_tree().quit()

func _ready() -> void :
				connect("gene_edited", self, "_on_edit")
				connect("genes_changed", self, "_on_edit")

				compute_base_types_for_slot()

func compute_base_types_for_slot():
				for base_type in _slot_for_base.keys():
								var slot = _slot_for_base[base_type]
								if base_types_for_slot.has(slot):
												base_types_for_slot[slot].append(base_type)
								else:
												base_types_for_slot[slot] = [base_type]

func _on_edit():
				GameState.save_game()

func get_icon(gene_id, is_shared = false):
				var gene
				if is_shared:
								gene = GameState.saved_stats.shared_stash[gene_id]
				else:
								gene = GameState.get_active_stats().genes[gene_id]
				if gene.unique:
								var gene_info = UniqueGenes.get_unique_data(gene.unique_id)
								if gene_info.has("texture"):
												return gene_info.texture
								else:
												print("ERROR: NO unique texture found for gene id: ", gene.unique_id)
												return null
				return texture_for_base_type(gene.type)

func verify():
				for character in GameState.saved_stats.characters:
								Globals.selected_character_name = character
								print("VERIFYING GENES")
								verify_genes()
								verify_stored_mods()

func verify_genes():
				
				print("Verifying Gene Integrity")
				var genes_to_remove = []
				for gene_id in GameState.get_active_stats().genes.keys():
								var gene = GameState.get_active_stats().genes[gene_id]
								var mod_config = null
								var drop_only_mod_config = null
								if gene.has("type"):
												mod_config = mods_for_base_type(gene.type)
												drop_only_mod_config = drop_only_mods_for_base_type(gene.type)

								var remove = false
								if not gene.has("id"):
												print("Missing id", gene)
												remove = true
								if not gene.has("name"):
												print("Missing gene name", gene)
												remove = true
								if not gene.has("type"):
												print("Missing gene type", gene)
												remove = true
								if not gene.has("prefixes"):
												print("Missing prefixes", gene)
												remove = true
								if not gene.has("suffixes"):
												print("Missing suffixes", gene)
												remove = true
								if not gene.has("locked"):
												print("Missing locked", gene)
												remove = true

								
								if not gene.has("equipment_slot"):
												gene.equipment_slot = null

								if not gene.has("quality"):
												print("Setting quality on legacy gear")
												gene.quality = 0

								if gene.has("prefixes"):
												for prefix in gene.prefixes:
																
																if not prefix.has("locked"):
																				prefix.locked = false
																if not prefix.has("drop_only"):
																				prefix.drop_only = false

																var mod_config_to_use = mod_config
																if prefix.drop_only:
																				mod_config_to_use = drop_only_mod_config

																if not prefix.has("mod_id"):
																				print("Missing mod_id", prefix)
																				remove = true
																				break
																if not mod_config_to_use.mod_option_for_id.has(prefix.mod_id):
																				remove = true
																				break
																var mod = mod_config_to_use.mod_option_for_id[prefix.mod_id]
																if mod.has("keystone"):
																				if not Keystones.keystones.has(mod.keystone):
																								print("Invalid keystone: ", mod.keystone)
																								remove = true
																				continue
																if not prefix.has("tier") or prefix.tier < 0 or prefix.tier >= mod.tiers:
																				print("Invalid tier", mod, prefix)
																				remove = true
																if not prefix.has("tier_strength") or prefix.tier_strength < 0 or prefix.tier_strength > 1:
																				print("Missing tier_strength", prefix)
																				remove = true
																if prefix.has("stat"):
																				if not StatsInfo.is_stat_valid(prefix.stat):
																								print("Invalid prefix stat: ", prefix.stat)
																								remove = true

								if gene.has("suffixes"):
												for suffix in gene.suffixes:
																
																if not suffix.has("locked"):
																				suffix.locked = false
																if not suffix.has("drop_only"):
																				suffix.drop_only = false

																var mod_config_to_use = mod_config
																if suffix.drop_only:
																				mod_config_to_use = drop_only_mod_config

																if not suffix.has("mod_id"):
																				print("Missing mod_id", suffix)
																				remove = true
																				break
																if not mod_config_to_use.mod_option_for_id.has(suffix.mod_id):
																				remove = true
																				break
																var mod = mod_config_to_use.mod_option_for_id[suffix.mod_id]
																if mod.has("keystone"):
																				if not Keystones.keystones.has(mod.keystone):
																								print("Invalid keystone: ", mod.keystone)
																								remove = true
																				continue
																if not suffix.has("tier") or suffix.tier < 0 or suffix.tier >= mod.tiers:
																				print("Invalid tier", mod, suffix)
																				remove = true
																if not suffix.has("tier_strength") or suffix.tier_strength < 0 or suffix.tier_strength > 1:
																				print("Missing tier_strength", suffix)
																				remove = true

																if suffix.has("stat"):
																				if not StatsInfo.is_stat_valid(suffix.stat):
																								print("Invalid suffix stat: ", suffix.stat)
																								remove = true


								if remove:
												genes_to_remove.append(gene_id)

				
				for id in genes_to_remove:
								delete_gene(id)

func verify_stored_mods():
				
				
				print("Verifying Stored Mod Integrity")

				for base_type in Genes.BaseType.keys():
								var mods = Genes.mods_for_base_type(base_type)
								if GameState.get_active_stats().stored_mods.has(base_type):
												var modset = GameState.get_active_stats().stored_mods[base_type]
												if modset.has("prefixes"):
																var keep_mods = []
																for prefix in modset.prefixes:
																				if not prefix.has("mod_id"):
																								print("Missing tier", prefix)
																								continue
																				var mod = mods.mod_option_for_id[prefix.mod_id]
																				if not prefix.has("tier") or prefix.tier < 0 or prefix.tier >= mod.tiers:
																								print("Invalid tier", mod, prefix)
																								continue
																				if not prefix.has("tier_strength") or prefix.tier_strength < 0 or prefix.tier_strength > 1:
																								print("Missing tier_strength", prefix)
																								continue
																				
																				print("Valid prefix", prefix)
																				keep_mods.append(prefix)
																modset.prefixes = keep_mods

												if modset.has("suffixes"):
																var keep_mods = []
																for suffix in modset.suffixes:
																				if not suffix.has("mod_id"):
																								print("Missing tier", suffix)
																								continue
																				var mod = mods.mod_option_for_id[suffix.mod_id]
																				if not suffix.has("tier") or suffix.tier < 0 or suffix.tier >= mod.tiers:
																								print("Invalid tier", mod, suffix)
																								continue
																				if not suffix.has("tier_strength") or suffix.tier_strength < 0 or suffix.tier_strength > 1:
																								print("Missing tier_strength", suffix)
																								continue
																				
																				print("Valid suffix", suffix)
																				keep_mods.append(suffix)
																modset.suffixes = keep_mods
				print("Verification done")

func can_create_new_gene(type):
				if GameState.get_active_stats().orbs.gold >= PURCHASE_COST:
								return true
				return false

func get_next_id():
				
				var id = str(GameState.get_active_stats().next_gene_id)
				GameState.get_active_stats().next_gene_id += 1
				return id

func pickup_gene(gene):
				if gene != null:
								var slot = Genes.slot_for_base(gene.type)
								GameState.get_active_stats().genes[gene.id] = gene
								GameState.get_active_stats().new_item_types[slot] = true
								GameState.get_active_stats().new_item_ids[gene.id] = true
								emit_signal("genes_changed")

func create_new_gene(type, level = 1):
				var id = get_next_id()

				if not (type in GeneSlot.values()):
								print("Type", type, " is not a Gene Type")
								get_tree().quit()

				var gene = {
								"id": id, 
								"level": level, 
								"unique": false, 
								"name": "Gene " + id, 
								"type": type, 
								"implicits": [], 
								"prefixes": [], 
								"suffixes": [], 
								"locked": false
				}

				
				GameState.get_active_stats().genes[id] = gene
				GameState.get_active_stats().orbs.gold -= PURCHASE_COST
				GameState.emit_signal("changed")
				GameState.save_game(true)
				emit_signal("genes_changed")
				return id

func get_stored_mods_for_type(type):
				if GameState.get_active_stats().stored_mods.has(type):
								return GameState.get_active_stats().stored_mods[type]

				return null

func get_unlocked_prefix_count(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var count = 0
				for mod in gene.prefixes:
								if not mod.locked:
												count += 1

				return count


func get_locked_prefix_count(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var count = 0
				for mod in gene.prefixes:
								if mod.locked:
												count += 1

				return count

func get_upgradeable_prefix_count(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var count = 0
				for mod in gene.prefixes:
								if not mod.locked and not is_mod_maxed(gene_id, mod) and not mod.drop_only:
												count += 1

				return count

func get_unlocked_suffix_count(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var count = 0
				for mod in gene.suffixes:
								if not mod.locked:
												count += 1

				return count

func get_locked_suffix_count(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var count = 0
				for mod in gene.suffixes:
								if mod.locked:
												count += 1

				return count

func get_upgradeable_suffix_count(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var count = 0
				for mod in gene.suffixes:
								if not mod.locked and not is_mod_maxed(gene_id, mod) and not mod.drop_only:
												count += 1

				return count


func remove_random_mod(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]

				var unlocked_prefix_count = get_unlocked_prefix_count(gene_id)
				var unlocked_suffix_count = get_unlocked_suffix_count(gene_id)

				if unlocked_prefix_count > 0 and unlocked_suffix_count > 0:
								if randf() < 0.5:
												return remove_prefix(gene_id)
								else:
												return remove_suffix(gene_id)

				if unlocked_prefix_count > 0:
								return remove_prefix(gene_id)
				elif unlocked_suffix_count > 0:
								return remove_suffix(gene_id)

				return false

func lock_random_mod(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]

				var unlocked_prefix_count = get_unlocked_prefix_count(gene_id)
				var unlocked_suffix_count = get_unlocked_suffix_count(gene_id)

				if unlocked_prefix_count > 0 and unlocked_suffix_count > 0:
								if randf() < 0.5:
												return lock_random_prefix(gene_id)
								else:
												return lock_random_suffix(gene_id)

				if unlocked_prefix_count > 0:
								return lock_random_prefix(gene_id)
				elif unlocked_suffix_count > 0:
								return lock_random_suffix(gene_id)

				return false

func lock_specific_mod(gene_id, mod_id):
				var gene = GameState.get_active_stats().genes[gene_id]

				var found_mod = null
				for mod in gene.prefixes:
								if mod.mod_id == mod_id:
												found_mod = mod
												break
				for mod in gene.suffixes:
								if mod.mod_id == mod_id:
												found_mod = mod
												break

				if found_mod:
								found_mod.locked = true
								return true

				return false

func unlock_specific_mod(gene_id, mod_id):
				var gene = GameState.get_active_stats().genes[gene_id]

				var found_mod = null
				for mod in gene.prefixes:
								if mod.mod_id == mod_id:
												found_mod = mod
												break
				for mod in gene.suffixes:
								if mod.mod_id == mod_id:
												found_mod = mod
												break

				if found_mod:
								found_mod.locked = false
								return true

				return false

func upgrade_random_mod(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				print("Upgrading gene: ", JSON.print(gene, " "))

				var upgradeable_prefix_count = get_upgradeable_prefix_count(gene_id)
				var upgradeable_suffix_count = get_upgradeable_suffix_count(gene_id)

				if upgradeable_prefix_count > 0 and upgradeable_suffix_count > 0:
								if randf() < 0.5:
												return upgrade_random_prefix(gene_id)
								else:
												return upgrade_random_suffix(gene_id)

				if upgradeable_prefix_count > 0:
								return upgrade_random_prefix(gene_id)
				elif upgradeable_suffix_count > 0:
								return upgrade_random_suffix(gene_id)

				return false

func upgrade_random_prefix(gene_id):
				print("Upgrading random prefix")
				var gene = GameState.get_active_stats().genes[gene_id]
				var options = []
				for mod in gene.prefixes:
								if not mod.locked and not is_mod_maxed(gene_id, mod) and not mod.drop_only:
												options.append(mod)

				print("Options:", options)

				if len(options) > 0:
								var chosen = randi() % len(options)
								var mod_to_change = options[chosen]
								print("Modifying: ", mod_to_change)
								mod_to_change.tier += 1
								return true
				return false

func upgrade_random_suffix(gene_id):
				print("Upgrading random suffix")
				var gene = GameState.get_active_stats().genes[gene_id]
				var options = []
				for mod in gene.suffixes:
								if not mod.locked and not is_mod_maxed(gene_id, mod) and not mod.drop_only:
												options.append(mod)

				print("Options:", options)

				if len(options) > 0:
								var chosen = randi() % len(options)
								var mod_to_change = options[chosen]
								print("Modifying: ", mod_to_change)
								mod_to_change.tier += 1
								return true
				return false

func get_max_tier(gene_id, mod):
				var gene = GameState.get_active_stats().genes[gene_id]
				var mod_options = mods_for_base_type(gene.type)
				if mod.drop_only:
								mod_options = drop_only_mods_for_base_type(gene.type)

				var mod_config = mod_options.mod_option_for_id[mod.mod_id]
				var n_tiers = mod_config.tiers
				var max_tier = 0
				for i in range(n_tiers):
								if gene.level >= mod_options.get_level_requirement(i, n_tiers, mod_config.min_level):
												max_tier = i
				return max_tier

func is_mod_maxed(gene_id, mod):
				if mod.has("keystone"):
								return true
				return mod.tier >= get_max_tier(gene_id, mod)

func unlock_random_mod(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]

				var locked_prefix_count = get_locked_prefix_count(gene_id)
				var locked_suffix_count = get_locked_suffix_count(gene_id)

				if locked_prefix_count > 0 and locked_suffix_count > 0:
								if randf() < 0.5:
												return unlock_random_prefix(gene_id)
								else:
												return unlock_random_suffix(gene_id)

				if locked_prefix_count > 0:
								return unlock_random_prefix(gene_id)
				elif locked_suffix_count > 0:
								return unlock_random_suffix(gene_id)

				return false

func lock_random_prefix(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var options = []
				for mod in gene.prefixes:
								if not mod.locked:
												options.append(mod)

				if len(options) > 0:
								options[randi() % len(options)].locked = true

func unlock_random_prefix(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var options = []
				for mod in gene.prefixes:
								if mod.locked:
												options.append(mod)

				if len(options) > 0:
								options[randi() % len(options)].locked = false

func lock_random_suffix(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var options = []
				for mod in gene.suffixes:
								if not mod.locked:
												options.append(mod)

				if len(options) > 0:
								options[randi() % len(options)].locked = true

func unlock_random_suffix(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var options = []
				for mod in gene.suffixes:
								if mod.locked:
												options.append(mod)

				if len(options) > 0:
								options[randi() % len(options)].locked = false

func add_random_mod(gene_id):
				add_mod(gene_id)

func roll_tier_strength():
					return randf()

func remove_unlocked_prefixes(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var keepers = []
				for mod in gene.prefixes:
								if mod.locked:
												keepers.append(mod)
				gene.prefixes = keepers

func remove_unlocked_suffixes(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var keepers = []
				for mod in gene.suffixes:
								if mod.locked:
												keepers.append(mod)
				gene.suffixes = keepers

func remove_all_mods(gene_id):
				remove_unlocked_prefixes(gene_id)
				remove_unlocked_suffixes(gene_id)

func reroll_suffix_mod_values(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				for mod in gene.suffixes:
								if not mod.locked and not mod.drop_only:
												mod.tier_strength = roll_tier_strength()

func reroll_prefix_mod_values(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				for mod in gene.prefixes:
								if not mod.locked and not mod.drop_only:
												mod.tier_strength = roll_tier_strength()

func reroll_all_mod_values(gene_id):
				reroll_prefix_mod_values(gene_id)
				reroll_suffix_mod_values(gene_id)

func roll_prefix(gene_id, mods, n_rolls = 1):
				var gene = GameState.get_active_stats().genes[gene_id]
				var prefix_ids = []
				var group_ids = []
				for prefix in gene.prefixes:
								prefix_ids.append(prefix.mod_id)
								if prefix.has("group_id"):
												group_ids.append(prefix.group_id)
				while true:
								var potential_prefix = mods.roll_prefix(gene.level, mods.sample_prefix(gene.level), false, n_rolls)
								if potential_prefix.mod_id in prefix_ids:
												continue
								if potential_prefix.has("group_id"):
												if potential_prefix.group_id in group_ids:
																continue
								return potential_prefix

func roll_suffix(gene_id, mods, n_rolls = 1):
				var gene = GameState.get_active_stats().genes[gene_id]
				var suffix_ids = []
				var group_ids = []
				for suffix in gene.suffixes:
								suffix_ids.append(suffix.mod_id)
								if suffix.has("group_id"):
												group_ids.append(suffix.group_id)
				while true:
								var potential_suffix = mods.roll_suffix(gene.level, mods.sample_suffix(gene.level), false, n_rolls)
								if potential_suffix.mod_id in suffix_ids:
												continue
								if potential_suffix.has("group_id"):
												if potential_suffix.group_id in group_ids:
																continue
								return potential_suffix

func add_prefix(gene_id, n_rolls = 1):
				var gene = GameState.get_active_stats().genes[gene_id]
				var mods = mods_for_base_type(gene.type)
				var mod = roll_prefix(gene_id, mods, n_rolls)
				gene.prefixes.append(mod)

func add_suffix(gene_id, n_rolls = 1):
				var gene = GameState.get_active_stats().genes[gene_id]
				var mods = mods_for_base_type(gene.type)
				var mod = roll_suffix(gene_id, mods, n_rolls)
				gene.suffixes.append(mod)

func add_mod(gene_id, n_rolls = 1):
				var gene = GameState.get_active_stats().genes[gene_id]

				var prefix_count = len(gene.prefixes)
				var suffix_count = len(gene.suffixes)

				var can_add_prefix = prefix_count < 2
				var can_add_suffix = suffix_count < 2

				if can_add_prefix and can_add_suffix:
								if randf() < 0.5:
												return add_prefix(gene_id, n_rolls)
								else:
												return add_suffix(gene_id, n_rolls)
				elif can_add_prefix:
								return add_prefix(gene_id, n_rolls)
				elif can_add_suffix:
								return add_suffix(gene_id, n_rolls)

func remove_prefix(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var removable_prefixes = 0
				for mod in gene.prefixes:
								if not mod.locked:
												removable_prefixes += 1

				if removable_prefixes > 0:
								var to_remove = randi() % len(gene.prefixes)
								while gene.prefixes[to_remove].locked:
												to_remove = randi() % len(gene.prefixes)

								var keepers = []
								for i in range(len(gene.prefixes)):
												if i == to_remove:
																continue
												keepers.append(gene.prefixes[i])
								gene.prefixes = keepers
								return true

				return false

func remove_suffix(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var removable_suffixes = 0
				for mod in gene.suffixes:
								if not mod.locked:
												removable_suffixes += 1

				if removable_suffixes > 0:
								var to_remove = randi() % len(gene.suffixes)
								while gene.suffixes[to_remove].locked:
												to_remove = randi() % len(gene.suffixes)

								var keepers = []
								for i in range(len(gene.suffixes)):
												if i == to_remove:
																continue
												keepers.append(gene.suffixes[i])
								gene.suffixes = keepers
								return true

				return false

func craft_scramble(gene_id):
				print("Scrambling")
				remove_all_mods(gene_id)
				var n_mods = 3 + randi() % 2
				for i in range(n_mods):
								add_mod(gene_id)
				sort_mods(gene_id)

func craft_scramble_lucky(gene_id):
				print("Scrambling Lucky")
				remove_all_mods(gene_id)
				var n_mods = 3 + randi() % 2
				for i in range(n_mods):
								add_mod(gene_id, 2)
				sort_mods(gene_id)

func craft_scramble_ultra(gene_id):
				print("Scrambling Ultra")
				remove_all_mods(gene_id)
				var n_mods = 3 + randi() % 2
				for i in range(n_mods):
								add_mod(gene_id, 10)
				sort_mods(gene_id)

func craft_scramble_prefixes(gene_id):
				print("Scrambling Prefixes")
				var gene = GameState.get_active_stats().genes[gene_id]
				remove_unlocked_prefixes(gene_id)
				var max_affix_per_side = 2
				var n_mods = 1 + randi() % max_affix_per_side
				for i in range(n_mods):
								if len(gene.prefixes) >= max_affix_per_side:
												continue
								add_prefix(gene_id)

func craft_scramble_suffixes(gene_id):
				print("Scrambling Suffixes")
				var gene = GameState.get_active_stats().genes[gene_id]
				remove_unlocked_suffixes(gene_id)
				var max_affix_per_side = 2
				var n_mods = 1 + randi() % max_affix_per_side
				for i in range(n_mods):
								if len(gene.suffixes) >= max_affix_per_side:
												continue
								add_suffix(gene_id)

func craft_unlock(gene_id):
				unlock_random_mod(gene_id)

func craft_clear(gene_id):
				remove_all_mods(gene_id)

func craft_splice(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var type = gene.type
				if GameState.get_active_stats().stored_mods.has(type):
								var modset = GameState.get_active_stats().stored_mods[type]
								if len(modset.prefixes) > 0 or len(modset.suffixes) > 0:
												gene.prefixes = modset.prefixes.duplicate(true)
												modset.prefixes = []
												gene.suffixes = modset.suffixes.duplicate(true)
												modset.suffixes = []

func craft_extract(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]

				if len(gene.prefixes) == 0 and len(gene.suffixes) == 0:
								
								return

				var type = gene.type
				if GameState.get_active_stats().stored_mods.has(type):
								var modset = GameState.get_active_stats().stored_mods[type]
								modset.prefixes = gene.prefixes.duplicate(true)
								modset.suffixes = gene.suffixes.duplicate(true)
				else:
								var modset = {
												"prefixes": gene.prefixes.duplicate(true), 
												"suffixes": gene.suffixes.duplicate(true)
								}
								GameState.get_active_stats().stored_mods[type] = modset

				gene.suffixes = []
				gene.prefixes = []

func craft_gamma(gene_id):
				add_mod(gene_id)

func craft_recessive(gene_id):
				remove_random_mod(gene_id)

func craft_lock(gene_id):
				lock_random_mod(gene_id)

func craft_lock_specific_mod(gene_id, mod_id):
				lock_specific_mod(gene_id, mod_id)

func craft_unlock_specific_mod(gene_id, mod_id):
				unlock_specific_mod(gene_id, mod_id)

func craft_upgrade_tier(gene_id):
				return upgrade_random_mod(gene_id)

func craft_cosmic(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]

				for prefix in gene.prefixes:
								if not prefix.has("keystone") and not prefix.locked:
												prefix.tier_strength = roll_tier_strength()
				for suffix in gene.suffixes:
								if not suffix.has("keystone") and not suffix.locked:
												suffix.tier_strength = roll_tier_strength()

func craft_recombinate(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				var type = gene.type
				var stored_mods = get_stored_mods_for_type(gene.type)

				var final_prefixes = []
				var final_suffixes = []
				if stored_mods:
								if len(stored_mods.prefixes) > 0 and len(gene.prefixes) > 0 and \
								len(stored_mods.suffixes) > 0 and len(gene.suffixes) > 0:
												
												var combined_prefixes = {}
												for p in stored_mods.prefixes:
																if combined_prefixes.has(p.mod_id):
																				if randf() < 0.5:
																								combined_prefixes[p.mod_id] = p.duplicate(true)
																else:
																				combined_prefixes[p.mod_id] = p.duplicate(true)
												for p in gene.prefixes:
																if combined_prefixes.has(p.mod_id):
																				if randf() < 0.5:
																								combined_prefixes[p.mod_id] = p.duplicate(true)
																else:
																				combined_prefixes[p.mod_id] = p.duplicate(true)

												var combined_suffixes = {}
												for p in stored_mods.suffixes:
																if combined_suffixes.has(p.mod_id):
																				if randf() < 0.5:
																								combined_suffixes[p.mod_id] = p.duplicate(true)
																else:
																				combined_suffixes[p.mod_id] = p.duplicate(true)
												for p in gene.suffixes:
																if combined_suffixes.has(p.mod_id):
																				if randf() < 0.5:
																								combined_suffixes[p.mod_id] = p.duplicate(true)
																else:
																				combined_suffixes[p.mod_id] = p.duplicate(true)

												var n_prefix = len(combined_prefixes.keys())
												var n_suffix = len(combined_suffixes.keys())
												var max_affix_per_side = 2
												if n_prefix >= 2 and n_suffix >= 2:
																for i in range(min(max_affix_per_side, n_prefix)):
																				var keys = combined_prefixes.keys()
																				var rolled_index = randi() % len(keys)
																				var rolled_key = keys[rolled_index]
																				final_prefixes.append(combined_prefixes[rolled_key])
																				combined_prefixes.erase(rolled_key)
																for i in range(min(max_affix_per_side, n_suffix)):
																				var keys = combined_suffixes.keys()
																				var rolled_index = randi() % len(keys)
																				var rolled_key = keys[rolled_index]
																				final_suffixes.append(combined_suffixes[rolled_key])
																				combined_suffixes.erase(rolled_key)

																gene.prefixes = final_prefixes
																gene.suffixes = final_suffixes
																stored_mods.prefixes = []
																stored_mods.suffixes = []

func sort_mods(gene_id):
				var gene = GameState.get_active_stats().genes[gene_id]
				gene.prefixes.sort_custom(self, "mod_sorter")
				gene.suffixes.sort_custom(self, "mod_sorter")

func delete_gene(gene_id, emit = true):
				GameState.get_active_stats().genes.erase(gene_id)
				GameState.mark_gene_seen(gene_id)
				
				for type in GameState.get_active_stats().gene_loadout:
								var genes_for_type = GameState.get_active_stats().gene_loadout[type]
								for slot_id in genes_for_type:
												if genes_for_type[slot_id] == gene_id:
																genes_for_type[slot_id] = null
				if emit:
								emit_signal("genes_changed")

func is_gene_valid(gene_id):
				return GameState.get_active_stats().genes.has(gene_id)

func can_afford_craft(craft_type):
				
				var costs = craft_costs[craft_type]
				for cost in costs:
								if GameState.get_orb_count(cost.orb) < cost.cost:
												return false
				return true

func purchase_craft(gene_id, craft_type, mod_id = null):
				if can_afford_craft(craft_type) and can_perform_craft(gene_id, craft_type, mod_id):
								var costs = craft_costs[craft_type]
								for cost in costs:
												GameState.remove_orbs(cost.orb, cost.cost)

								
								if craft_type == CraftType.CLEAR:
												craft_clear(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.EXTRACT:
												craft_extract(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.SPLICE:
												craft_splice(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.RECOMBINATE:
												craft_recombinate(gene_id)
												Globals.play_sound_effect(sound_recombinate)
								if craft_type == CraftType.RECESSIVE:
												craft_recessive(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.SCRAMBLE:
												craft_scramble(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.SCRAMBLE_LUCKY:
												craft_scramble_lucky(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.SCRAMBLE_ULTRA:
												craft_scramble_ultra(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.GAMMA:
												craft_gamma(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.COSMIC:
												craft_cosmic(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.LOCK_MOD:
												craft_lock(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.UNLOCK_MOD:
												craft_unlock(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.SCRAMBLE_PREFIXES:
												craft_scramble_prefixes(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.SCRAMBLE_SUFFIXES:
												craft_scramble_suffixes(gene_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.LOCK_SPECIFIC_MOD:
												craft_lock_specific_mod(gene_id, mod_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.UNLOCK_SPECIFIC_MOD:
												craft_unlock_specific_mod(gene_id, mod_id)
												Globals.play_sound_effect(sound_craft)
								if craft_type == CraftType.UPGRADE_TIER:
												craft_upgrade_tier(gene_id)
												Globals.play_sound_effect(sound_craft)
								sort_mods(gene_id)
								emit_signal("gene_edited")


func can_perform_craft(gene_id, craft_type, mod_id = null):
				
				var gene = GameState.get_active_stats().genes[gene_id]

				
				if gene.has("unique") and gene.unique:
								return false

				if craft_type == CraftType.SPLICE:
								
								var stored_mods = get_stored_mods_for_type(gene.type)
								if not stored_mods:
												return false
								return len(stored_mods.prefixes) + len(stored_mods.suffixes) > 0

				if craft_type == CraftType.CLEAR:
								return len(gene.prefixes) + len(gene.suffixes) > 0

				if craft_type == CraftType.SCRAMBLE:
								if get_unlocked_prefix_count(gene_id) + get_unlocked_suffix_count(gene_id) > 0:
												return true
								if len(gene.prefixes) + len(gene.suffixes) < 4:
												return true

								return false

				if craft_type == CraftType.SCRAMBLE_LUCKY:
								if get_unlocked_prefix_count(gene_id) + get_unlocked_suffix_count(gene_id) > 0:
												return true
								if len(gene.prefixes) + len(gene.suffixes) < 4:
												return true

								return false

				if craft_type == CraftType.SCRAMBLE_ULTRA:
								if get_unlocked_prefix_count(gene_id) + get_unlocked_suffix_count(gene_id) > 0:
												return true
								if len(gene.prefixes) + len(gene.suffixes) < 4:
												return true

								return false

				if craft_type == CraftType.SCRAMBLE_PREFIXES:
								if get_unlocked_prefix_count(gene_id) > 0:
												return true

								if len(gene.prefixes) < 2:
												return true

								return false

				if craft_type == CraftType.SCRAMBLE_SUFFIXES:
								if get_unlocked_suffix_count(gene_id) > 0:
												return true

								if len(gene.suffixes) < 2:
													return true

								return false

				if craft_type == CraftType.EXTRACT:
								return len(gene.prefixes) + len(gene.suffixes) > 0

				if craft_type == CraftType.RECESSIVE:
								
								var removable_count = 0
								for mod in gene.prefixes:
												if not mod.locked:
																removable_count += 1
								for mod in gene.suffixes:
												if not mod.locked:
																removable_count += 1
								return removable_count > 0

				if craft_type == CraftType.COSMIC:
								return get_unlocked_prefix_count(gene_id) + get_unlocked_suffix_count(gene_id) > 0

				if craft_type == CraftType.GAMMA:
								if Genes.slot_for_base(gene.type) == GeneSlot.MINOR:
												return len(gene.prefixes) + len(gene.suffixes) < 4
								else:
												return len(gene.prefixes) + len(gene.suffixes) < 6

				if craft_type == CraftType.RECOMBINATE:
								var type = gene.type
								var stored_mods = get_stored_mods_for_type(type)
								if stored_mods:
												if len(stored_mods.prefixes) >= 2 and len(gene.prefixes) >= 2 and \
												len(stored_mods.suffixes) >= 2 and len(gene.suffixes) >= 2:
																
																var combined_prefixes = {}
																for p in stored_mods.prefixes:
																				if combined_prefixes.has(p.mod_id):
																								if randf() < 0.5:
																												combined_prefixes[p.mod_id] = p.duplicate(true)
																				else:
																								combined_prefixes[p.mod_id] = p.duplicate(true)
																for p in gene.prefixes:
																				if combined_prefixes.has(p.mod_id):
																								if randf() < 0.5:
																												combined_prefixes[p.mod_id] = p.duplicate(true)
																				else:
																								combined_prefixes[p.mod_id] = p.duplicate(true)

																var combined_suffixes = {}
																for p in stored_mods.suffixes:
																				if combined_suffixes.has(p.mod_id):
																								if randf() < 0.5:
																												combined_suffixes[p.mod_id] = p.duplicate(true)
																				else:
																								combined_suffixes[p.mod_id] = p.duplicate(true)
																for p in gene.suffixes:
																				if combined_suffixes.has(p.mod_id):
																								if randf() < 0.5:
																												combined_suffixes[p.mod_id] = p.duplicate(true)
																				else:
																								combined_suffixes[p.mod_id] = p.duplicate(true)

																var n_prefix = len(combined_prefixes.keys())
																var n_suffix = len(combined_suffixes.keys())
																var max_affix_per_side = 2

																if n_prefix >= 2 and n_suffix >= 2:
																				return true
								return false

				
				if craft_type == CraftType.LOCK_MOD:
								var enough_affixes = len(gene.prefixes) + len(gene.suffixes) > 3
								
								for mod in gene.prefixes:
												if mod.locked:
																return false
								for mod in gene.suffixes:
												if mod.locked:
																return false

								return enough_affixes

				if craft_type == CraftType.UNLOCK_MOD:
								var locked_mods = 0
								
								for mod in gene.prefixes:
												if mod.locked:
																locked_mods += 1
								for mod in gene.suffixes:
												if mod.locked:
																locked_mods += 1

								return locked_mods > 0

				if craft_type == CraftType.LOCK_SPECIFIC_MOD:
								if mod_id == null:
												return false

								for mod in gene.prefixes:
												if not mod.locked and mod_id == mod.mod_id:
																return true
								for mod in gene.suffixes:
												if not mod.locked and mod_id == mod.mod_id:
																return true

								return false

				if craft_type == CraftType.UNLOCK_SPECIFIC_MOD:
								if mod_id == null:
												return false

								for mod in gene.prefixes:
												if mod.locked and mod_id == mod.mod_id:
																return true
								for mod in gene.suffixes:
												if mod.locked and mod_id == mod.mod_id:
																return true

								return false

				if craft_type == CraftType.UPGRADE_TIER:
								for mod in gene.prefixes:
												if not mod.locked and not is_mod_maxed(gene_id, mod) and not mod.drop_only:
																return true
								for mod in gene.suffixes:
												if not mod.locked and not is_mod_maxed(gene_id, mod) and not mod.drop_only:
																return true

								return false

				return true

func rename_gene(gene_id, text):
				if GameState.get_active_stats().genes.has(gene_id):
								GameState.get_active_stats().genes[gene_id].name = text.substr(0, 20)
								emit_signal("gene_edited")
