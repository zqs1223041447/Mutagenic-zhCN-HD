extends Particles2D






var play_sound = false


func _ready() -> void :
				if GameState.is_fx_enabled():
								emitting = true
				else:
								emitting = false

				if play_sound:
								Globals.play_sound_effect($AudioStreamPlayer.stream)

func _on_Timer_timeout() -> void :
				queue_free()
