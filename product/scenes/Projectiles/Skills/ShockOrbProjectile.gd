extends Projectile

var change_direction = false
var accum_distance = 0.0

func _physics_process(delta: float) -> void :
				accum_distance += linear_velocity.length() * delta
				if accum_distance > 30:
								accum_distance -= 30
								change_direction = false
								var speed = linear_velocity.length()
								linear_velocity = linear_velocity.rotated( - PI / 4 + randf() * PI / 2)

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats

				var info = target.stats.apply_damage(damage, Color.WHITE, stats, true, false, sp)
				track_hit(info)
