extends Projectile

var start_velocity = Vector2.ZERO

func _ready() -> void :
				start_velocity = linear_velocity

func _physics_process(delta: float) -> void :
				linear_velocity = linear_velocity.rotated(linear_velocity.length() / 60.0 * delta * PI / 2)

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var info = target.stats.apply_damage(damage, Color.white, stats, true, false, sp)
				track_hit(info)

