extends Projectile

var projectile_scene = preload("res://Scenes/Projectiles/Skills/ShardOrbProjectile.tscn")

var n_proj = 1
var force = 0.0
var n_pulse = 0.0

func on_pulse(delta):
				var sp = skill_parent_weakref.get_ref()
				n_pulse += 1
				if sp:
								var rotate_per_proj = (2 * PI) / n_proj
								var offset = PI / 5
								for i in range(n_proj):
												var proj = projectile_scene.instance()
												proj.skill_parent = skill_parent_weakref.get_ref()
												proj.target_group = target_group
												proj.global_position = global_position
												proj.damage = damage
												proj.hits = 1
												proj.lifetime = 0.25
												var speed = force
												var multiplier = 1.0
												proj.lifetime /= multiplier
												proj.radius = radius
												sp.projectile_layer.call_deferred("add_child", proj)
												var angle = rotate_per_proj * i + offset * n_pulse
												var direction = Vector2.RIGHT.rotated(angle)
												proj.linear_velocity = direction * force
				else:
								call_deferred("destroy_projectile")
