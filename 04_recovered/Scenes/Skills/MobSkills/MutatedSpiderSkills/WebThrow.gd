extends MobSkill

var projectile_scene = preload("res://Scenes/Projectiles/MobSkills/SpiderWeb/SpiderWeb.tscn")

var rotation_extra = PI / 8.0
var rotation_count = 0

func initialize_override_mob_stats():
				override_stats.base_duration = 3.0
				override_stats.projectile_speed = 120
				override_stats.projectile_count = 4

func get_damage_tag():
				return SkillTags.Tags.PHYSICAL

func get_cooldown(apply_rand_keystones = true):
				return 1.0

func cast(damage_multiplier = 1.0, consume_boons = false):
				var all_enemies = get_visible_enemies()
				var dist = INF
				var closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy

				rotation_count += 1
				var rotation_offset = rotation_count * rotation_extra

				if closest != null:
								var dmg = get_damage_bundle()
								var duration = get_duration()
								var hits = 1 + get_extra_hits()
								var force = get_force()
								var chains = get_chains()
								var base_angle = Vector2.DOWN
								var n_proj = get_projectiles()
								var rotation_step = 2.0 * PI / n_proj
								for i in range(get_projectiles()):
												var proj = projectile_scene.instance()
												proj.skill_parent = self
												proj.target_group = target_group
												proj.global_position = global_position
												proj.damage = dmg
												proj.lifetime = duration
												proj.hits = hits
												proj.chains = chains
												projectile_layer.call_deferred("add_child", proj)
												var direction = base_angle.rotated(rotation_step * i + rotation_offset)
												proj.linear_velocity = direction * force * (0.9 + randf() * 0.2)
								play_sound()

