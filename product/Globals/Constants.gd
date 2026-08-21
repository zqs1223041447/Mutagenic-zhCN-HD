extends Node

enum ScalingType{
				FLAT,
				PERCENT,
				MORE,
}

enum ItemType{
				SKILL, 
				BUFF, 
				CHARACTER,
}

enum ModType{
				PREFIX, 
				SUFFIX, 
				IMPLICIT, 
				AUGMENT,
}

enum ItemRarity{
				MAGIC, 
				RARE, 
				UBER,
}

enum StatusFlags{
				
				CHILLED,
				JOLTED,
				CHARRED,
				BLEEDING,
				POISONED,
				FROZEN,
				BURNING,
				INFECTED,
				RUPTURED,
				ELECTROCUTED,
				REGULAR_ELEMENTAL_AILMENT,

				EXPOSED,
				VULNERABLE,
				RECENTLY_HIT,
				HAMSTRUNG,
				DEBILITATE,
				HINDER,
				BRITTLE,
				PROTRACT,
				SCORCH,
				BANE,
				POLARIZE,
				HYPOTHERMIA,

				CURSED,
				PLAGUED,
				PHANTOM_SHIELD,
				AURA,

				BOON,
				SWIFTNESS_BOON,
				PRECISION_BOON,
				TOUGHNESS_BOON,

				DREAD,
				TRANSFUSION,
				BLOOD_BOIL,
				VILE_DOMAIN,
				BONDED_ELECTRONS,

				ECHOING,
}

enum OrbType{
				BLUE, 
				RED, 
				GREEN, 
				GOLD, 
				CORRUPTION, 
}

const OrbName = {
				OrbType.BLUE: "Orb of Experimentation", 
				OrbType.GREEN: "Orb of Honing", 
				OrbType.RED: "Orb of Enhancement", 
				OrbType.GOLD: "Orb of Knowledge", 
				OrbType.CORRUPTION: "Corruption Shard", 
}

var USE_STEAM = false

var GAME_VERSION = "EA 0.6.2"

const KNOCKBACK_AMOUNT = 45.0
const DASH_AMOUNT = 225.0
const BASE_ATTACK_RANGE = 50.0

const AILMENT_RATE = 60.0

const ENABLE_MTX_SHOP = false

const ENABLE_TEST_ZONE = false
