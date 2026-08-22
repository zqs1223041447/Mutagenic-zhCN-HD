extends Node

var blue_tex = preload("res://sprites/drops/blue_orb.png")
var red_tex = preload("res://sprites/drops/red_orb.png")
var green_tex = preload("res://sprites/drops/green_orb.png")
var gold_tex = preload("res://sprites/drops/gold_orb.png")
var corruption_tex = preload("res://sprites/drops/corruption.png")

var blue_animated = load("res://sprites/_acquired/generated_spriteframes/items/blue_orb.spriteframes.tres")
var red_animated = load("res://sprites/_acquired/generated_spriteframes/items/red_orb.spriteframes.tres")
var green_animated = load("res://sprites/_acquired/generated_spriteframes/items/green_orb.spriteframes.tres")
var gold_animated = load("res://sprites/_acquired/generated_spriteframes/items/gold_orb.spriteframes.tres")
var corruption_animated = load("res://sprites/_acquired/generated_spriteframes/items/corruption.spriteframes.tres")

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
				Constants.OrbType.CORRUPTION: corruption_animated, 
}
