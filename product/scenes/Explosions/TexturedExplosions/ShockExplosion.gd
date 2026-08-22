extends FlipbookExplosion

var explosion_sound = preload("res://Sounds/Skills/Explosions/cluster_bombs.wav")

func _ready() -> void :
				Globals.play_sound_effect(explosion_sound)
