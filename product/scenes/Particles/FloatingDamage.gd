extends Node2D
## Floating combat text.
##
## P4-B F1c: two configurable rhythm tiers (normal / crit).  Each tier table
## carries duration (move+fade seconds), travel (displacement), spread,
## pop_scale/pop_duration (scale curve) and tint.  Non-crit callers keep the
## manager-driven parameters (FloatingDamageManager exports stay authoritative);
## crit hits are driven by RHYTHM_CRIT.  Defaults preserve the legacy feel:
## linear move+fade over 0.25s, crit pops 2x -> 1x over 0.4s with
## TRANS_BACK/EASE_IN and a red tint.

const RHYTHM_NORMAL := {
				"travel": Vector2(0, -8), 
				"duration": 0.25, 
				"spread": PI / 2, 
				"pop_scale": 1.0, 
				"pop_duration": 0.0, 
				"tint": null, 
}

const RHYTHM_CRIT := {
				"travel": Vector2(0, -8), 
				"duration": 0.4, 
				"spread": PI / 2, 
				"pop_scale": 2.0, 
				"pop_duration": 0.4, 
				"tint": Color(1, 0, 0), 
}


@onready var label = $Label


static func rhythm_for(crit: bool) -> Dictionary:
				return RHYTHM_CRIT if crit else RHYTHM_NORMAL


func show_value(value, travel, duration, spread, color, crit = false):
				var rhythm: Dictionary = RHYTHM_CRIT if crit else {
								"travel": travel, 
								"duration": duration, 
								"spread": spread, 
								"pop_scale": 1.0, 
								"pop_duration": 0.0, 
								"tint": null, 
				}
				_play(value, color, rhythm)


func _play(value, color, rhythm: Dictionary):
				$Label.text = value
				
				$Label.add_theme_color_override("font_color", color)
				var movement: Vector2 = rhythm.travel.rotated(randf_range( - rhythm.spread / 2, rhythm.spread / 2))
				var duration: float = rhythm.duration

				
				var tween := create_tween()
				tween.set_parallel(true)
				tween.tween_property($Label, "position", 
												$Label.position + movement, 
												duration).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)
				tween.tween_property($Label, "modulate:a", 
												0.0, duration).from(1.0).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)

				
				
				if rhythm.pop_duration > 0.0:
								if rhythm.tint != null:
												modulate = rhythm.tint
								var scale_tween := create_tween()
								scale_tween.tween_property($Label, "scale", 
																$Label.scale, 
																rhythm.pop_duration).from($Label.scale * rhythm.pop_scale).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)

				await tween.finished
				call_deferred("queue_free")
