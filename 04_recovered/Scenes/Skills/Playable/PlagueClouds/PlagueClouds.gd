extends GenericSkill

var plague_cloud = preload("res://Scenes/Projectiles/Skills/PlagueCloudsProjectile.tscn")

func cast():
				var inst = plague_cloud.instance()
				inst.skill_parent = self
				inst.target_group = target_group
				inst.lifetime = get_duration()
				inst.damage = get_damage_bundle()
				inst.radius = get_radius()
				inst.particle_multiplier = get_aoe()
				inst.global_position = global_position
				inst.pulse_cooldown = 0.25
				ground_effect_level.add_child(inst)

func get_cooldown(apply_rand_keystones = true):
				return get_stat("cooldown", 1.0)
