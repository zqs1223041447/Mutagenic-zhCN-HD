extends Projectile

var curse = preload("res://Scenes/StatusEffects/Curses/Bane.tscn")

var curse_nova = preload("res://Scenes/Explosions/TexturedExplosions/CurseExplosion.tscn")

var particle_multiplier = 1.0
var curse_effect = 1.0
var curse_duration = 0.0


func _ready() -> void :
				lifetime = 0.25

				var stats
				if skill_parent_weakref.get_ref():
								stats = skill_parent_weakref.get_ref().stats

				var targets = get_tree().get_nodes_in_group(target_group)
				if len(targets) > 0:
								var explosion = curse_nova.instance()
								explosion.global_position = global_position
								explosion.radius = radius
								explosion.modulation = Color("cd93d7")
								GameState.get_global("ground").call_deferred("add_child", explosion)

								for target in targets:
												if target.global_position.distance_to(global_position) < radius:
																var ailment = curse.instance()
																ailment.applier_stats_weakref = weakref(stats)
																ailment.base_lifetime = curse_duration
																ailment.curse_effect = curse_effect
																target.stats.apply_status_effect(ailment)


