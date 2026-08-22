extends Projectile

const ROTATION_RADIUS = 25.0

var rotations_per_second = 0.0
var current_angle = 0.0

func _ready():
				# P3-H3a: Godot 4 no longer auto-chains parent _ready(); run
				# Projectile._ready() first (weakref/collision/damage snapshot).
				super._ready()
				current_angle = randf() * 2.0 * PI * 0.25
				var one_rotation_distance = 2.0 * PI * ROTATION_RADIUS
				rotations_per_second = linear_velocity.length() / one_rotation_distance

func _physics_process(delta: float) -> void :
				current_angle += delta * rotations_per_second * 2.0 * PI
				position = Vector2.RIGHT.rotated(current_angle) * ROTATION_RADIUS

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var info = target.stats.apply_damage(damage, Color.WHITE, stats, true, false, sp)
				track_hit(info)

