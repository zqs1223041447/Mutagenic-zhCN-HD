extends Button

var skill_name

func _ready():
				var info = Skills.config[skill_name]
				$MarginContainer / TextureRect.texture = info.skill_texture

func _on_SkillListOption_mouse_entered() -> void :
				grab_focus()
