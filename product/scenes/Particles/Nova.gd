extends Node2D

@onready var nova_sound = preload("res://Sounds/SFX/nova.wav")
var radius = 1.0
func _ready() -> void :
				Globals.play_sound_effect(nova_sound)
				$GPUParticles2D.process_material.set("initial_velocity", radius * 2.0)

func _on_Timer_timeout() -> void :
				queue_free()
