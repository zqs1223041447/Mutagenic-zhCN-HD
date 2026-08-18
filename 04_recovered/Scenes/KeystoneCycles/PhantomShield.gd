extends Node

var phantom_shield = preload("res://Scenes/StatusEffects/Keystones/PhantomShield.tscn")

var stats

func _ready() -> void :
				trigger()

func trigger():
				var buff = phantom_shield.instance()
				buff.applier_stats_weakref = weakref(stats)
				if stats.status_flags.has(Constants.StatusFlags.PHANTOM_SHIELD):
								if stats.status_flags[Constants.StatusFlags.PHANTOM_SHIELD] < 1:
												stats.apply_status_effect(buff)
				else:
								stats.apply_status_effect(buff)

func _on_AddShieldTimer_timeout() -> void :
				trigger()
