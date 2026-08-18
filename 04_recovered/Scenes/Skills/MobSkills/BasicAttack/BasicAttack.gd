extends MobSkill

func get_damage_tag():
				return get_parent().get_parent().damage_type
