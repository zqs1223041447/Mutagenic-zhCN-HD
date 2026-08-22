extends ConfirmationDialog

var window_theme = preload("res://Themes/MainTheme.tres")


func _enter_tree() -> void :
				reset_size()
				theme = window_theme
				if has_method("get_close_button"):
								call("get_close_button").visible = false

func _ready():
				var parent_offset = size / 2.0
				var actual_rect = get_viewport().get_visible_rect()
				$Node/ColorRect.size = actual_rect.size
				$Node/ColorRect.global_position = - $Node/ColorRect.size / 2.0 + parent_offset
