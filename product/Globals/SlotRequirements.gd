extends Node

const requirements = {
				"primary": {
								"level": 1, 
								"supports": {
												"a": 1, 
												"b": 1, 
												"c": 5, 
												"d": 10, 
												"e": 15, 
												"f": 20
								}
				}, 
				"secondary": {
								"level": 1, 
								"supports": {
												"a": 1, 
												"b": 5, 
												"c": 10, 
												"d": 15, 
												"e": 20, 
												"f": 25
								}
				}, 
				"support_one": {
								"level": 10, 
								"supports": {
												"a": 15, 
												"b": 20, 
												"c": 25, 
												"d": 30, 
												"e": 35, 
												"f": 40
								}
				}, 
				"support_two": {
								"level": 15, 
								"supports": {
												"a": 20, 
												"b": 25, 
												"c": 30, 
												"d": 35, 
												"e": 40, 
												"f": 45
								}
				}, 
				"support_three": {
								"level": 20, 
								"supports": {
												"a": 25, 
												"b": 30, 
												"c": 35, 
												"d": 40, 
												"e": 45, 
												"f": 50
								}
				}, 
				"support_four": {
								"level": 25, 
								"supports": {
												"a": 30, 
												"b": 35, 
												"c": 40, 
												"d": 45, 
												"e": 50, 
												"f": 55
								}
				}
}

func get_required_level_for_support(skill_slot, support_slot):
				return requirements[skill_slot].supports[support_slot]

func get_required_level_for_skill(skill_slot):
				return requirements[skill_slot].level
