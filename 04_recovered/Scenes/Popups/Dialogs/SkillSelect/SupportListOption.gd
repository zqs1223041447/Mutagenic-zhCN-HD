extends Button

var support_name
var filter
var filter_string

func _ready():
				var info = SkillSupports.supports[support_name]
				$MarginContainer / TextureRect.texture = info.icon

				filter_string = SkillSupports.get_filter_string(support_name)

				if disabled:
								modulate = Colors.disabled

func _on_SkillListOption_mouse_entered() -> void :
				grab_focus()

func set_filter(_filter):
				filter = _filter
				if filter in filter_string or not filter or len(filter) == 0:
								modulate = Color.white
				else:
								modulate = Color(1, 1, 1, 0.1)
