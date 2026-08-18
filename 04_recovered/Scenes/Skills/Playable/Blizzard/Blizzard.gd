extends GenericSkill

var blizzard = preload("res://Scenes/GroundDegens/Skills/Blizzard/BlizzardDegen.tscn")

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
								play_sound()
								var inst = blizzard.instance()
								inst.skill_parent = self
								inst.lifetime = get_duration()
								inst.damage_bundle = get_damage_bundle()
								inst.radius = get_radius()
								inst.global_position = closest.global_position
								consume_boons()
								sky_layer.call_deferred("add_child", inst)

