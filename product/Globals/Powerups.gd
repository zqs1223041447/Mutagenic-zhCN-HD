extends Node

@onready var powerups = []

func create_random_powerup():
				if len(powerups) > 0:
								return powerups[randi() % len(powerups)].instantiate()
				return null
