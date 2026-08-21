extends Mob

var hinder = preload("res://scenes/Skills/Playable/Hinder/Hinder.tscn")
var bane = preload("res://scenes/Skills/Playable/Bane/Bane.tscn")
var brittle = preload("res://scenes/Skills/Playable/Brittle/Brittle.tscn")
var protract = preload("res://scenes/Skills/Playable/Protract/Protract.tscn")
var debilitate = preload("res://scenes/Skills/Playable/Debilitate/Debilitate.tscn")
var hypothermia = preload("res://scenes/Skills/Playable/Hypothermia/Hypothermia.tscn")
var polarize = preload("res://scenes/Skills/Playable/Polarize/Polarize.tscn")
var scorch = preload("res://scenes/Skills/Playable/Scorch/Scorch.tscn")

var curse_options = [
				hinder, 
				bane, 
				brittle, 
				protract, 
				debilitate, 
				hypothermia, 
				polarize, 
				scorch
]

func _ready() -> void :
				var chosen_curse = curse_options[randi() % len(curse_options)]
				var gear = chosen_curse.instantiate()
				$Gear.add_child(gear)
