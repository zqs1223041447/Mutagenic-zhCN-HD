extends ShaderExplosion

var sound_effect = preload("res://Sounds/Skills/Shots/doom_explosion.wav")

func _ready() -> void :
				Globals.play_sound_effect(sound_effect)

