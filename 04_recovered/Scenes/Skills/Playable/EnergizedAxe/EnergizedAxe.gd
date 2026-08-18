extends GenericSkill

var projectile_scene = preload("res://Scenes/Projectiles/Skills/EnergizedAxeProjectile.tscn")

var closest = null

func get_cast_range(apply_random_keystones = true):
				return get_radius(apply_random_keystones) * 2.0

func can_cast():
				var all_enemies = get_visible_enemies(true)
				var dist = get_cast_range()
				closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy
				return closest != null

func get_duration(apply = true):
				return max(0.1, get_cooldown(apply) / 2.0)

func cast():
				if closest != null:
								var dmg = get_damage_bundle()
								var force = get_force()
								consume_boons()
								var proj = projectile_scene.instance()
								proj.skill_parent = self
								proj.target_group = target_group
								proj.global_position = global_position
								proj.damage = dmg
								proj.radius = get_radius()
								proj.target_angle = closest.global_position.angle_to_point(global_position)
								proj.lifetime = get_duration()
								call_deferred("add_child", proj)
								play_sound()
