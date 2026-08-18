extends BaseEffect


var used = false

func consume():
				if used:
								return false
				used = true
				return true

func get_status_flags():
				return [Constants.StatusFlags.PHANTOM_SHIELD]
