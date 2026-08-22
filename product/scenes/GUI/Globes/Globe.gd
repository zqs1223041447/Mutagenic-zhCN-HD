extends Control

func update_progress(amount, amount_max):
				if amount_max <= 0:
								return
				var bar = $TextureProgressBar
				var label = $HBoxContainer/HealthLabel
				if bar == null or label == null:
								return
				var percent = amount / amount_max
				bar.value = 100.0 * percent
				label.text = str(round(amount)) + " / " + str(round(amount_max))
