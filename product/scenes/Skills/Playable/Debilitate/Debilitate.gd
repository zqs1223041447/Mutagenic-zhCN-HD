extends GenericSkill

var debilitate_projectile = preload("res://scenes/Projectiles/Skills/DebilitateProjectile.tscn")

func cast():
				var all_enemies = get_visible_enemies(true)
				var dist = INF
				var target = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												target = enemy
				if target:
								var inst = debilitate_projectile.instantiate()
								inst.skill_parent = self
								inst.curse_duration = get_duration()
								inst.curse_effect = get_curse_effect()
								inst.damage = get_damage_bundle()
								inst.radius = get_radius()
								inst.particle_multiplier = get_aoe()
								inst.global_position = target.global_position
								inst.target_group = target_group
								consume_boons()
								level.call_deferred("add_child", inst)

