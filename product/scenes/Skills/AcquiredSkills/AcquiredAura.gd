extends GenericAura
class_name AcquiredAura

var override_stats = {
				"damage_effectiveness": 1.0, 
}

func _ready() -> void :
				initialize_override_stats()

func initialize_override_stats():
				pass

func get_effective_tier():
				return 0

func get_tiers():
				return [{
								"skill": {}, 
				}]


func get_stat(stat, default = 0):
				if override_stats.has(stat):
								return override_stats[stat]
				return super.get_stat(stat, default)
