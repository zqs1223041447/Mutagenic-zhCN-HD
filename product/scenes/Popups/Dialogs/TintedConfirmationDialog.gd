extends ConfirmationDialog

var window_theme = preload("res://Themes/MainTheme.tres")


func _enter_tree() -> void :
				set_as_minsize()
				theme = window_theme
				get_close_button().visible = false

func _ready():
				var parent_offset = rect_size / 2.0
				var actual_rect = get_viewport().get_visible_rect()
				$Node/ColorRect.rect_size = actual_rect.size
				$Node/ColorRect.rect_global_position = - $Node/ColorRect.rect_size / 2.0 + parent_offset
