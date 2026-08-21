extends Node2D

@onready var sprite = $NoticeSprite
var elapsed = 0.0

func _process(delta: float) -> void :
				elapsed += delta
				sprite.global_position = global_position + Vector2.DOWN * sin(elapsed * 4.0) * 2.0
