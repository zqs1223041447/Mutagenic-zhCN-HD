extends HBoxContainer

var texture
var effect
var effect_weakref
var buff_count = 0


func _ready() -> void :
				effect_weakref = weakref(effect)
				$VBoxContainer/Buff/BuffIcon.texture = texture
				# P4-WIRE: G3 hint_tooltip renamed tooltip_text in Godot 4
				$VBoxContainer/Buff.tooltip_text = effect.description
				if effect.permanent:
								$VBoxContainer/DurationLabel.text = ""
				else:
								$VBoxContainer/DurationLabel.text = str(ceil(effect.lifetime - effect.lifetime_expired))


func _on_Timer_timeout() -> void :
				var e = effect_weakref.get_ref()
				if e:
								if not e.permanent:
												$VBoxContainer/DurationLabel.text = str(ceil(e.lifetime - e.lifetime_expired))
				else:
								queue_free()

func update_count():
				if buff_count > 0:
								$VBoxContainer/CountLabel.text = str(buff_count)
				else:
								$VBoxContainer/CountLabel.text = ""
