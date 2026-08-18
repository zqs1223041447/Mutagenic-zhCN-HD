extends BaseEffect

var flame_chain = preload("res://Scenes/Particles/FlameTether.tscn")

export var damage_per_second = {}
var cached_dps = {}
var accumulated = 0.0
onready var target_stats = get_parent().get_parent()

var tether

func initialize():
				
				buffs_and_nerfs = {
								"all_damage": {
												"type": Constants.ScalingType.MORE, 
												"amount": - 0.25, 
												"direction": 1
								}
				}

func on_apply():
				cached_dps = {"damage": {}}
				if damage_per_second.has("penetrations"):
								cached_dps["penetrations"] = damage_per_second.penetrations
				for k in damage_per_second["damage"]:
								cached_dps["damage"][k] = damage_per_second["damage"][k] / Constants.AILMENT_RATE

				var source = applier_stats_weakref.get_ref()
				if source:
								var target = get_parent().get_parent()
								tether = flame_chain.instance()
								tether.source_target = source
								tether.dest_target = target
								ground_layer.call_deferred("add_child", tether)


func on_tick(delta):
				accumulated += delta
				if accumulated >= 1.0 / Constants.AILMENT_RATE:
								var attacker_stats = applier_stats_weakref.get_ref()
								var info = target_stats.apply_damage(cached_dps, Color.blueviolet, attacker_stats, false, true)
								track_hit(info)
								accumulated -= 1.0 / Constants.AILMENT_RATE

func on_expire():
				
				if tether:
								tether.queue_free()

func get_status_flags():
				return []
