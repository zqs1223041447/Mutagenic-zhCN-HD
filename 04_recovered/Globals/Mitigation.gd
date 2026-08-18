extends Node

func get_effective_mitigation(mitigation, current_level = 0):
				return 1.0 / min(4.0, pow(2.0, mitigation / (5.0 * (current_level * current_level))))

func get_effective_evasion(mitigation, current_level = 0):
				return 1.0 - get_effective_mitigation(mitigation, current_level)
