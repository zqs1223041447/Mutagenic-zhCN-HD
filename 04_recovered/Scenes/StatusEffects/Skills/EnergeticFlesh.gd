extends BaseEffect

export var damage_per_second = {}
var cached_dps = {}
var accumulated = 0.0
onready var target_stats = get_parent().get_parent()

func on_apply():
				cached_dps = {"damage": {}}
				if damage_per_second.has("penetrations"):
								cached_dps["penetrations"] = damage_per_second.penetrations
				for k in damage_per_second["damage"]:
								cached_dps["damage"][k] = damage_per_second["damage"][k] / Constants.AILMENT_RATE

func on_tick(delta):
				accumulated += delta
				if accumulated >= 1.0 / Constants.AILMENT_RATE:
								var attacker_stats = applier_stats_weakref.get_ref()
								if target_stats.status_flags.has(Constants.StatusFlags.JOLTED):
												var info = target_stats.apply_damage(cached_dps, Color.blueviolet, attacker_stats, false, true)
												track_hit(info)
								accumulated -= 1.0 / Constants.AILMENT_RATE

func get_status_flags():
				return []
