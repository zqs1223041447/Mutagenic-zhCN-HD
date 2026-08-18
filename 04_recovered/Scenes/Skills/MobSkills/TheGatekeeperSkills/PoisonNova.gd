extends MobSkill

var shooting_direction = 0.0

func initialize_override_mob_stats():
				override_stats.cooldown = 1.0
				override_stats.radius = 80.0
				override_stats.damage = 35.0

func get_damage_tag():
				return SkillTags.Tags.TOXIC

var nova_scene = preload("res://Scenes/Explosions/TexturedExplosions/PoisonExplosion.tscn")

func cast():
				var all_enemies = get_visible_enemies()
				var dist = INF
				var closest = null
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < dist:
												dist = dist_to_enemy
												closest = enemy

				if closest != null:
								var dmg = get_damage_bundle()
								for enemy in all_enemies:
												enemy.stats.apply_damage(dmg, Color.white, stats, true, false, self)

								var nova = nova_scene.instance()
								nova.global_position = global_position
								nova.radius = get_radius()
								GameState.get_global("ground").call_deferred("add_child", nova)

