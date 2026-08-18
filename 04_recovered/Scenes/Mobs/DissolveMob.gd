extends Node2D

onready var sprite = $DissolveSprite

var dissolved = 0

func _on_Timer_timeout() -> void :
				queue_free()

func _process(delta: float) -> void :
				dissolved += delta * 4.0
				sprite.material.set_shader_param("dissolveAmount", min(dissolved, 1.0))
