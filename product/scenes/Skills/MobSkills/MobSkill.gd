extends GenericSkill
class_name MobSkill

var override_stats = {
				"cooldown": 1.0, 
				"duration": 5.0, 
				"base_duration": 5.0, 
				"projectile_speed": 100.0, 
				"projectile_count": 1, 
				"damage_effectiveness": 1.0, 
				"damage": 5, 
}

@export var tags = []

func _ready() -> void :
				# Godot 4 no longer auto-chains parent _ready(); without this call
				# GenericSkill._ready never runs for mob skills (no damage_tag,
				# no cooldown init -> empty damage bundles).
				super._ready()
				initialize_override_mob_stats()

func initialize_override_mob_stats():
				pass

func get_tags():
				return tags

func get_damage_tag():
				return damage_tag


func get_stat(stat, default = 0):
				if override_stats.has(stat):
								return override_stats[stat]

				return super.get_stat(stat, default)
