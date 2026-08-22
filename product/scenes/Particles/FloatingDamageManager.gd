extends Node2D

var FCT = preload("res://scenes/Particles/FloatingDamage.tscn")

@onready var floating_damage_layer = get_tree().get_root().get_node("World/FloatingDamageTexts")

@export var travel = Vector2(0, - 8)
@export var duration = 0.25
@export var spread = PI / 2

func show_value(value, color, crit = false):
				var fct = FCT.instantiate()
				floating_damage_layer.add_child(fct)
				fct.global_position = global_position - fct.label.size / 2
				fct.global_position.y -= 8
				if typeof(value) == TYPE_FLOAT:
								value = Utils.render_suffix_number(value)
				fct.show_value(value, travel, duration, spread, color, crit)

func show_damage(value, color, crit = false):
				var fct = FCT.instantiate()
				floating_damage_layer.add_child(fct)
				fct.global_position = global_position - fct.label.size / 2
				fct.global_position.y -= 8
				if typeof(value) == TYPE_FLOAT:
								value = Utils.render_suffix_number(value)
				fct.show_value(value, travel, duration, spread, color, crit)

func show_xp(value, color, crit = false):
				var fct = FCT.instantiate()
				floating_damage_layer.add_child(fct)
				fct.global_position = global_position - fct.label.size / 2
				fct.global_position.y -= 20
				if typeof(value) == TYPE_FLOAT:
								value = Utils.render_suffix_number(value)
				value = "+" + value + " XP"
				fct.show_value(value, travel, duration, spread, color, crit)
