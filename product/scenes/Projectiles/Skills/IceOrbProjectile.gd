extends Projectile

var chill = preload("res://scenes/StatusEffects/DamageAilments/Chill.tscn")
var cold_explosion_effect = preload("res://scenes/Explosions/TexturedExplosions/IceExplosion.tscn")

func on_hit(target):
				
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats

				if not stats:
								return

				var effective_radius = radius

				
				var explosion = cold_explosion_effect.instantiate()
				explosion.global_position = global_position
				explosion.radius = effective_radius
				stats.level_scene.call_deferred("add_child", explosion)


				var dmg = damage.duplicate(true)
				var dmg_mult = 1.0

				for k in dmg.damage:
								dmg.damage[k] *= dmg_mult

				var info = target.stats.apply_damage(dmg, Color.AQUA, stats, true, false, sp)
				track_hit(info)

				for k in dmg.damage:
								dmg.damage[k] *= 0.25

				var splash_applier_instance = splash_applier.instantiate()
				splash_applier_instance.damage_bundle = dmg
				splash_applier_instance.ignore_instance = target
				splash_applier_instance.radius = radius
				splash_applier_instance.target_group = stats.target_group
				splash_applier_instance.global_position = target.global_position
				GameState.get_global("ground").call_deferred("add_child", splash_applier_instance)




