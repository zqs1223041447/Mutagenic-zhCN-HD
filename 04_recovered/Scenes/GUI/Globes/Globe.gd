extends Control

func update_progress(amount, amount_max):
				var percent = amount / amount_max
				$TextureProgress.value = 100.0 * percent
				$HBoxContainer / HealthLabel.text = str(round(amount)) + " / " + str(round(amount_max))
