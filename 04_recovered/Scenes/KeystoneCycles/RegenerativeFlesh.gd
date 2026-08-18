extends Node

var regen_effect = preload("res://Scenes/StatusEffects/Keystones/RegenerativeFleshEffect.tscn")

var stats

func _ready() -> void :
				trigger()

func _on_SwitchTimer_timeout() -> void :
				trigger()

func trigger():
				var buff = regen_effect.instance()
				buff.applier_stats_weakref = weakref(stats)
				stats.apply_status_effect(buff)

