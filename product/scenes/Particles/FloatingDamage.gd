extends Node2D

@onready var label = $Label

func show_value(value, travel, duration, spread, color, crit = false):
				$Label.text = value
				$Label.set("custom_colors/font_color", color)
				var movement = travel.rotated(randf_range( - spread / 2, spread / 2))

				$Label/Tween.interpolate_property($Label, "rect_position", 
												$Label.rect_position, $Label.rect_position + movement, 
												duration, Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)
				$Label/Tween.interpolate_property($Label, "modulate:a", 
												1.0, 0.0, duration, 
												Tween.TRANS_LINEAR, Tween.EASE_IN_OUT)

				if crit:
								modulate = Color(1, 0, 0)
								$Label/Tween.interpolate_property($Label, "rect_scale", 
												$Label.rect_scale * 2, $Label.rect_scale, 
												0.4, Tween.TRANS_BACK, Tween.EASE_IN)

				$Label/Tween.start()
				await $Label/Tween.tween_all_completed
				call_deferred("queue_free")
