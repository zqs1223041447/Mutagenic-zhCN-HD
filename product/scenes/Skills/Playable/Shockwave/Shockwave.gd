extends GenericSkill

var projectile = preload("res://scenes/Projectiles/MeleeSkills/ShockwaveProjectile.tscn")

var closest = null
var dist = INF

func get_cast_range(apply = true):
				return 150

func get_force(apply_rand_keystones = true):
				
				return get_stat("projectile_speed")

func can_cast():
				var all_enemies = get_visible_enemies(true)
				dist = get_cast_range()
				closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy
				return closest != null

func cast():
				if closest != null:
								var radius = get_radius()
								var force = get_force()
								var dmg = get_damage_bundle()
								consume_boons()
								var base_angle = global_position.direction_to(closest.global_position)
								var proj = projectile.instantiate()
								proj.global_position = global_position
								proj.target_group = stats.target_group
								proj.damage = get_damage_bundle()
								proj.radius = radius
								proj.skill_parent = self
								proj.max_distance_travelled = get_cast_range()
								projectile_layer.call_deferred("add_child", proj)
								proj.linear_velocity = base_angle * force
								play_sound()




