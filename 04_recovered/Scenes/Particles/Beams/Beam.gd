extends Node2D

export var length = 100.0
export var width = 16.0
var source_target = null
var invalid = false
onready var tex = $TextureRect


func _ready() -> void :
				_update_position()

func _process(delta: float) -> void :
				_update_position()

func _update_position():
				if is_instance_valid(source_target):
								global_position = source_target.global_position

				var tex_size = tex.rect_size
				var chain_distance = length
				var chain_scale = chain_distance / tex_size.y
				var width_scale = 1.0 / (tex_size.x / width)
				tex.rect_scale = Vector2(width_scale, chain_scale)
				tex.rect_pivot_offset = Vector2(tex_size.x / 2.0, 0.0)
