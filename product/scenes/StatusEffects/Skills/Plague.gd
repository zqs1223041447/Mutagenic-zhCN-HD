extends BaseEffect

@export var damage_per_second = {}
var cached_dps = {}
var accumulated = 0.0
@onready var target_stats = get_parent().get_parent()

const PLAGUE_RATE = 60.0

func on_apply():
				cached_dps = {"damage": {}}
				if damage_per_second.has("penetrations"):
								cached_dps["penetrations"] = damage_per_second.penetrations
				for k in damage_per_second["damage"]:
								cached_dps["damage"][k] = damage_per_second["damage"][k] / PLAGUE_RATE
								if applier_stats_weakref.get_ref():
												var stats = applier_stats_weakref.get_ref()
												cached_dps["damage"][k] *= stats.gs("toxic_ailment_effect")

func on_tick(delta):
				accumulated += delta
				if accumulated >= 1.0 / PLAGUE_RATE:
								var attacker_stats = applier_stats_weakref.get_ref()
								var info = target_stats.apply_damage(cached_dps, Color.blueviolet, attacker_stats, false, true)
								track_hit(info)
								accumulated -= 1.0 / PLAGUE_RATE

func get_status_flags():
				return [Constants.StatusFlags.PLAGUED]
