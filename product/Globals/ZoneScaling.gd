extends Node


const LEVEL_100_MULTIPLIER = 1000000.0
const LIFE_EXPONENT = 1.105
const XP_EXPONENT = 1.048
const DAMAGE_EXPONENT = 1.062118

func get_map_mod_count(zone_level):
				return 0

func get_damage_scaler(zone_level):
				return pow(DAMAGE_EXPONENT, min(125, zone_level - 1))

func get_health_scaler(zone_level):
				
				return pow(LIFE_EXPONENT, zone_level - 1)

func get_xp_scaler(zone_level):



				return pow(XP_EXPONENT, zone_level)

func get_iiq_scaler(zone_level):
				return max(0.0, zone_level / 80.0 - 1.0)

func get_iir_scaler(zone_level):
				return 6.0 * max(0.0, zone_level / 100.0 - 1.0)

func get_rare_monster_chance(zone_level):
				return 0.05 + 0.1 * (zone_level / 200.0)
