extends Node

var cycle_effect = preload("res://Scenes/StatusEffects/Keystones/CycleOfDestructionEffect.tscn")

var stats
var effect_is_damage = true

func _ready() -> void :
				trigger()

func _on_SwitchTimer_timeout() -> void :
				trigger()

func trigger():
				var buff = cycle_effect.instance()
				buff.applier_stats_weakref = weakref(stats)
				buff.effect_is_damage = effect_is_damage
				stats.apply_status_effect(buff)

				
				effect_is_damage = not effect_is_damage
