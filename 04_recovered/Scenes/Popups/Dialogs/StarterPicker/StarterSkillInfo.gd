extends VBoxContainer

var item_name

func _ready() -> void :
				var skill = Skills.config[item_name]
				$SkillName.text = skill.name
				$HBoxContainer / SkillImage.texture = skill.skill_texture
				$SkillDescription.text = skill.description
