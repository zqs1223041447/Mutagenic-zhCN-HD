extends GenericSkill

var projectile_scene = preload("res://scenes/DelayedSkill/ClusterBombs/ClusterBombs.tscn")

var DURATION = 0.6

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
								var count = get_projectiles()
								if stats.keystones.has("TREE_SABOTEUR") and randf() <= 0.5:
												count += 1
								if stats.keystones.has("UNIQUE_BOMB_SPECIALIST"):
												count *= 2
								var dmg = get_damage_bundle()
								consume_boons()
								for i in range(count):
												var outgoing_velocity = dist / DURATION
												var proj = projectile_scene.instantiate()
												proj.skill_parent = self
												proj.lifetime = DURATION
												proj.target_group = target_group
												proj.global_position = global_position
												proj.damage = dmg
												
												proj.radius = get_radius()
												ground_effect_level.add_child(proj)
												var angle = 0
												if count > 1:
																angle = ( - 5 * count + randf() * (2 * count * 5)) * PI / 180.0
												var direction = global_position.direction_to(closest.global_position).rotated(angle)
												proj.linear_velocity = direction * outgoing_velocity



