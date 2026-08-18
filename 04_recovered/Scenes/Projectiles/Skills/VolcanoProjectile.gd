extends Projectile

var projectile_scene = preload("res://Scenes/Projectiles/Skills/VolcanoOrbProjectile.tscn")

func on_pulse(delta):
				var sp = skill_parent_weakref.get_ref()

				if sp:
								var n_proj = sp.get_projectiles()
								var variance = sp.get_projectile_spread(n_proj)
								var dmg = sp.get_damage_bundle()
								var force = sp.get_force()
								var radius = sp.get_radius()
								var aoe = sp.get_aoe()

								for i in range(n_proj):
												var proj = projectile_scene.instance()
												proj.skill_parent = skill_parent_weakref.get_ref()
												proj.target_group = target_group
												proj.global_position = global_position
												proj.dmg_bundle = dmg
												proj.aoe = aoe
												proj.lifetime = 0.1 + randf() * 0.1
												var speed = force
												var multiplier = 1.0
												proj.lifetime /= multiplier
												proj.radius = radius
												sp.level.call_deferred("add_child", proj)
												var angle_to_enemy = randf() * 2 * PI
												var direction = Vector2.RIGHT.rotated(angle_to_enemy)
												proj.linear_velocity = direction * speed * (0.9 + randf() * 0.2)
								play_sound()
				else:
								call_deferred("destroy_projectile")
