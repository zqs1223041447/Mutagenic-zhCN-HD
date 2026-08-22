extends Projectile

var explosion = preload("res://scenes/Explosions/TexturedExplosions/FlameExplosion.tscn")
var dmg_bundle = null
var aoe = 0.0
var target_position = Vector2.ZERO

func on_destroy():
				var sp = skill_parent_weakref.get_ref()
				if sp:
								
								var explosion_instance = explosion.instantiate()
								explosion_instance.radius = radius
								explosion_instance.global_position = global_position
								sp.ground_effect_level.add_child(explosion_instance)

								
								var splash_applier_instance = splash_applier.instantiate()
								splash_applier_instance.global_position = global_position
								splash_applier_instance.damage_bundle = dmg_bundle
								splash_applier_instance.radius = radius
								splash_applier_instance.skill_parent = sp
								GameState.get_global("ground").call_deferred("add_child", splash_applier_instance)


