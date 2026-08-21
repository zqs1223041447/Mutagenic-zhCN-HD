extends Mob

var toxic_pool = preload("res://scenes/GroundDegens/OnDeathEffects/ToxicPoolDegen.tscn")

func _on_death():
				._on_death()

				var pool = toxic_pool.instantiate()
				pool.global_position = global_position
				pool.damage_bundle = {"damage": {SkillTags.Tags.TOXIC: damage}}
				pool.target_group = "allies"
				pool.radius = 25
				ground_layer.add_child(pool)
