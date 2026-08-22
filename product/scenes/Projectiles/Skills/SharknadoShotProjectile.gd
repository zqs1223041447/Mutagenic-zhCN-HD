extends Projectile

var projectile_scene = preload("res://scenes/Projectiles/Skills/SharknadoShardProjectile.tscn")

var n_proj = 4
var force = 0.0
var initial_hits = 0

func _ready():
				# P3-H3a: Godot 4 no longer auto-chains parent _ready(); run
				# Projectile._ready() first (weakref/collision/damage snapshot).
				super._ready()
				initial_hits = hits

func on_hit(target):
				destroy_projectile()

func on_destroy():
				var sp = skill_parent_weakref.get_ref()
				if sp:
								var rotate_per_proj = (2 * PI) / n_proj
								var offset = PI / 5
								for i in range(n_proj):
												var proj = projectile_scene.instantiate()
												proj.skill_parent = skill_parent_weakref.get_ref()
												proj.target_group = target_group
												proj.global_position = global_position
												proj.damage = damage
												proj.hits = initial_hits
												proj.lifetime = 1.0
												var speed = force
												var multiplier = 1.0
												proj.lifetime /= multiplier
												proj.radius = radius
												sp.projectile_layer.call_deferred("add_child", proj)
												var angle = rotate_per_proj * i
												var direction = Vector2.RIGHT.rotated(angle)
												proj.linear_velocity = direction * force
				else:
								call_deferred("destroy_projectile")
