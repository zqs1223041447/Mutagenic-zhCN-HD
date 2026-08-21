extends Control

@onready var parent = get_parent().get_parent()
@onready var level = GameState.get_global("level_scene")
@onready var player = GameState.get_global("player")

var step_x
var step_y
var initialized = false

var zoom_scale = 6.0

func initialize():
				step_x = level.tiles.cell_size.x
				step_y = level.tiles.cell_size.y
				initialized = true
				size = Vector2(32, 32)
				scale = Vector2(zoom_scale, zoom_scale)

func _process(delta: float) -> void :
				if initialized:
								queue_redraw()

func _draw() -> void :
				if initialized:
								var p_x = player.global_position.x / step_x - parent.offset_x + parent.IMAGE_PADDING
								var p_y = player.global_position.y / step_y - parent.offset_y + parent.IMAGE_PADDING
								var pos = Vector2(p_x, p_y) - (size / 2.0)
								draw_texture_rect_region(parent.image_texture, Rect2(Vector2.ZERO, size), Rect2(pos, size))
								draw_circle(size / 2.0, 1, Color.GREEN)


