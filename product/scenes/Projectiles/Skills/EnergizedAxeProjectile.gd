extends Projectile

var ANGLE_ARC = PI / 2.0
var rotations_per_second = 0.0
var target_angle = 0.0

func _ready():
				$CollisionShape2D.shape.radius = radius
				$Sprite.scale.y = radius / 16.0
				var swing_progress = lifetime_expired / lifetime
				var current_angle = target_angle + ANGLE_ARC / 2.0 - ANGLE_ARC * swing_progress
				position = Vector2.RIGHT.rotated(current_angle) * radius
				rotation = current_angle + PI / 2.0

func _physics_process(delta: float) -> void :
				var swing_progress = lifetime_expired / lifetime
				var current_angle = target_angle + ANGLE_ARC / 2.0 - ANGLE_ARC * swing_progress
				position = Vector2.RIGHT.rotated(current_angle) * radius
				rotation = current_angle + PI / 2.0
				if not visible:
								visible = true


func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var info = target.stats.apply_damage(damage, Color.WHITE, stats, true, false, sp)
				track_hit(info)

