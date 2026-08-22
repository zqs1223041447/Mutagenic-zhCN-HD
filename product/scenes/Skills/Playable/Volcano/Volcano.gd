extends GenericSkill

var volcano = preload("res://scenes/Projectiles/Skills/VolcanoProjectile.tscn")

var potential_targets = []
var closest_enemy = null

func can_cast():
				var all_enemies = get_visible_enemies(true)
				var effect_radius = get_radius()
				potential_targets = []
				var closest = INF
				closest_enemy = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < closest:
												closest = dist_to_enemy
												closest_enemy = enemy
												potential_targets.append(enemy)
				return len(potential_targets) > 0

func cast():
				if len(potential_targets) > 0:
								var count = 1
								if stats.keystones.has("TREE_SABOTEUR") and randf() <= 0.5:
												count = 2
								if stats.keystones.has("UNIQUE_BOMB_SPECIALIST"):
												count *= 2
								for i in range(count):
												var target = potential_targets[randi() % len(potential_targets)]
												if i == 0:
																target = closest_enemy
												var inst = volcano.instantiate()
												inst.skill_parent = self
												inst.global_position = target.global_position + Vector2(randf() * 16, randf() * 16)
												inst.lifetime = get_duration()
												inst.pulse_cooldown = super.get_cooldown()
												projectile_layer.call_deferred("add_child", inst)
								play_sound()

func get_cooldown(apply_rand_keystones = true):
				return 2.0
