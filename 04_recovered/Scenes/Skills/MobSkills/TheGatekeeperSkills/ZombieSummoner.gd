extends MobSkill

func get_damage_tag():
				return SkillTags.Tags.TOXIC

var zombie_scene = preload("res://Scenes/Mobs/Basic/Creatures/Zombie.tscn")

func cast():
				var enemy_count = get_tree().get_nodes_in_group("enemies")
				if len(enemy_count) < 6:
								var enemy = zombie_scene.instance()
								enemy.global_position = global_position
								level.add_child(enemy)

