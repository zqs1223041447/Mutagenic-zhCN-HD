extends Node2D

@onready var label = $Label

func show_value(value, travel, duration, spread, color, crit = false):
				$Label.text = value
				$Label.set("custom_colors/font_color", color)
				var movement = travel.rotated(randf_range( - spread / 2, spread / 2))

				# P3-H3b: Godot 4 tween rewrite of the legacy Tween-node
				# animation calls (that API was removed in 4.0).
				var tween := create_tween()
				tween.set_parallel(true)
				tween.tween_property($Label, "position", 
												$Label.position + movement, 
												duration).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)
				tween.tween_property($Label, "modulate:a", 
												0.0, duration).from(1.0).set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)

				if crit:
								modulate = Color(1, 0, 0)
								var scale_tween := create_tween()
								scale_tween.tween_property($Label, "scale", 
																$Label.scale, 
																0.4).from($Label.scale * 2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)

				await tween.finished
				call_deferred("queue_free")
