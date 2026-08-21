extends Node

var blue_tex = preload("res://sprites/drops/blue_orb.png")
var red_tex = preload("res://sprites/drops/red_orb.png")
var green_tex = preload("res://sprites/drops/green_orb.png")
var gold_tex = preload("res://sprites/drops/gold_orb.png")
var corruption_tex = preload("res://sprites/drops/corruption.png")

var blue_animated = preload("res://sprites/drops/blue_orb.aseprite")
var red_animated = preload("res://sprites/drops/red_orb.aseprite")
var green_animated = preload("res://sprites/drops/green_orb.aseprite")
var gold_animated = preload("res://sprites/drops/gold_orb.aseprite")
var corruption_animated = preload("res://sprites/drops/corruption.aseprite")

var texture_for_orb = {
				Constants.OrbType.BLUE: blue_tex, 
				Constants.OrbType.RED: red_tex, 
				Constants.OrbType.GREEN: green_tex, 
				Constants.OrbType.GOLD: gold_tex, 
				Constants.OrbType.CORRUPTION: corruption_tex, 
}

var animation_for_orb = {
				Constants.OrbType.BLUE: blue_animated, 
				Constants.OrbType.RED: red_animated, 
				Constants.OrbType.GREEN: green_animated, 
				Constants.OrbType.GOLD: gold_animated, 
				Constants.OrbType.GOLD: gold_animated, 
				Constants.OrbType.CORRUPTION: corruption_animated, 
}
