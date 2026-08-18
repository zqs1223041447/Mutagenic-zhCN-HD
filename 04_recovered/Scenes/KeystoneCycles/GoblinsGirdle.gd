extends Node

var stats

func _ready() -> void :
				trigger()

func _on_SwitchTimer_timeout() -> void :
				trigger()

func trigger():
				
				stats.call_deferred("add_toughness_boon", 1)
