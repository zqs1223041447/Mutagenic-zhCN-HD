extends Particles2D








func _ready() -> void :
				if GameState.is_fx_enabled():
								emitting = true
				else:
								emitting = false
								$TextureRect.visible = false
								$TextureRect2.visible = false

func _on_Timer_timeout() -> void :
				queue_free()
