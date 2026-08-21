extends MobSkill

var projectile_scene = preload("res://scenes/Projectiles/MobSkills/SotaSpear/SotaSpear.tscn")

var shooting_direction = 0.0
var cooldown_reset = false

func initialize_override_mob_stats():
				override_stats.cooldown = 0.1
				override_stats.base_duration = 3.0
				override_stats.projectile_speed = 150

func get_damage_tag():
				return SkillTags.Tags.PHYSICAL

func get_cooldown(apply_rand_keystones = true):
				if not cooldown_reset:
								return .get_cooldown(apply_rand_keystones)
				cooldown_reset = false
				return 1.5

func cast(damage_multiplier = 1.0, consume_boons = false):
				var all_enemies = get_visible_enemies()
				var dist = INF
				var closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy

				if closest != null:
								var variance = min(60, (get_projectiles() - 1) * 15) * PI / 180
								var dmg = get_damage_bundle()
								var duration = get_duration()

								var hits = 1 + get_extra_hits()
								var force = get_force()
								var chains = get_chains()
								var base_angle = Vector2.DOWN
								for i in range(get_projectiles()):
												var proj = projectile_scene.instantiate()
												proj.skill_parent = self
												proj.target_group = target_group
												proj.global_position = global_position
												proj.damage = dmg
												proj.lifetime = duration
												proj.hits = hits
												proj.chains = chains
												projectile_layer.call_deferred("add_child", proj)
												var angle = - variance / 2 + randf() * variance
												var direction = base_angle.rotated(angle + shooting_direction * PI / 4)
												proj.linear_velocity = direction * force * (0.9 + randf() * 0.2)
								shooting_direction += 1.0

								if shooting_direction == 8:
												cooldown_reset = true
												shooting_direction = 0

								play_sound()

