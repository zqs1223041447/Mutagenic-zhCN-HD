extends GenericSkill

var projectile_scene = preload("res://Scenes/Projectiles/Skills/ShockOrbProjectile.tscn")

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
								var rotation = 2.0 * PI / n_proj
								var dmg = get_damage_bundle()
								var hits = 1 + get_pierces()
								var chains = get_chains()
								var force = get_force()
								var base_angle = global_position.direction_to(closest.global_position)
								consume_boons()
								for i in range(n_proj):
												var proj = projectile_scene.instance()
												proj.skill_parent = self
												proj.target_group = target_group
												proj.global_position = global_position
												proj.damage = dmg
												proj.hits = hits
												projectile_layer.call_deferred("add_child", proj)
												var direction = base_angle.rotated( - PI / 4 + randf() * PI / 2)
												proj.linear_velocity = direction * get_force() * (0.95 + randf() * 0.1)
								play_sound()

