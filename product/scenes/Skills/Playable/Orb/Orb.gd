extends GenericSkill

var projectile_scene = preload("res://scenes/Projectiles/Skills/OrbProjectile.tscn")

var closest = null
var dist = INF

func can_cast():
				var all_enemies = get_visible_enemies(true)
				dist = INF
				closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy
				return closest != null

func cast():
				if closest != null:
								var n_proj = get_projectiles()
								var variance = get_projectile_spread(n_proj)
								var tick = 1
								if n_proj > 1:
												tick = (n_proj - 1)
								var dmg = get_damage_bundle()
								var hits = 1 + get_extra_hits()
								var force = get_force()
								var chains = get_chains()
								var base_angle = global_position.direction_to(closest.global_position)
								consume_boons()
								for i in range(n_proj):
												var proj = projectile_scene.instantiate()
												proj.skill_parent = self
												proj.target_group = target_group
												proj.global_position = global_position
												proj.damage = dmg
												proj.hits = hits
												proj.chains = chains
												projectile_layer.call_deferred("add_child", proj)
												var angle = - variance / 2.0 + i * variance / tick
												var direction = base_angle.rotated(angle)
												proj.linear_velocity = direction * force * (0.8 + 0.4 * randf())
								play_sound()

