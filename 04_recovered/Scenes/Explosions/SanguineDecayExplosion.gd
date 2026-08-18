extends Node2D

var blood = preload("res://Scenes/Explosions/TexturedExplosions/BloodExplosion.tscn")
var splash_applier = preload("res://Scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.tscn")

var stats
var attacker_stats
var damage
var radius


func _ready() -> void :
				var ground_layer = GameState.get_global("ground")
				var blood_explosion = blood.instance()
				blood_explosion.radius = radius
				blood_explosion.global_position = global_position
				ground_layer.call_deferred("add_child", blood_explosion)

				var splash_applier_instance = splash_applier.instance()
				splash_applier_instance.damage_bundle = damage
				splash_applier_instance.radius = radius
				splash_applier_instance.target_group = stats.allies_group
				splash_applier_instance.global_position = global_position
				ground_layer.call_deferred("add_child", splash_applier_instance)
				queue_free()

