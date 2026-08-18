extends Mob

var hinder = preload("res://Scenes/Skills/Playable/Hinder/Hinder.tscn")
var bane = preload("res://Scenes/Skills/Playable/Bane/Bane.tscn")
var brittle = preload("res://Scenes/Skills/Playable/Brittle/Brittle.tscn")
var protract = preload("res://Scenes/Skills/Playable/Protract/Protract.tscn")
var debilitate = preload("res://Scenes/Skills/Playable/Debilitate/Debilitate.tscn")
var hypothermia = preload("res://Scenes/Skills/Playable/Hypothermia/Hypothermia.tscn")
var polarize = preload("res://Scenes/Skills/Playable/Polarize/Polarize.tscn")
var scorch = preload("res://Scenes/Skills/Playable/Scorch/Scorch.tscn")

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
				var gear = chosen_curse.instance()
				$Gear.add_child(gear)
