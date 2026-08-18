extends GenericSkill

var projectile_scene = preload("res://Scenes/Projectiles/Skills/BladeShieldProjectile.tscn")

var closest = null

func can_cast():
				var all_enemies = get_visible_enemies(true)
				var dist = INF
				closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy
				return closest != null

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
								proj.lifetime = get_duration()
								call_deferred("add_child", proj)
								proj.linear_velocity = force * Vector2.RIGHT
								play_sound()

func get_cooldown(apply = true):
				return 2.0 / get_projectiles(apply)
