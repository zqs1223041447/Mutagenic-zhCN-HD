extends Particles2D

var shatter_sound = preload("res://Sounds/Skills/Explosions/shatter.wav")

func _ready() -> void :
				Globals.play_sound_effect(shatter_sound)

func _on_Timer_timeout() -> void :
				queue_free()
