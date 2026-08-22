extends VBoxContainer

var flag = null
var amount = 0


func _ready() -> void :
				var info = StatusEffects.status_effects[flag]
				$TextureRect.texture = info.texture
				if amount != 0:
								var text = str(amount)
								if info.type == Constants.ScalingType.PERCENT:
												text = str(floor(amount * 100.0)) + "%"
								$Label.text = text
				else:
								$Label.text = ""
