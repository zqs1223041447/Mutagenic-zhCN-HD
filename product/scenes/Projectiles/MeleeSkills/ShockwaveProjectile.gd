extends Projectile

var parts = preload("res://scenes/Particles/ShockwaveBurst.tscn")

func _ready():
				$CollisionShape2D.shape.radius = radius

func _on_Timer_timeout() -> void :
				var inst = parts.instantiate()
				inst.global_position = global_position
				inst.radius = radius
				GameState.get_global("ground").call_deferred("add_child", inst)

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var info = target.stats.apply_damage(damage, Color.WHITE, stats, true, false, sp)
				track_hit(info)
