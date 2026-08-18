extends BaseEffect

func on_apply():
				if stats:
								lifetime *= stats.gs("boon_duration")

func get_status_flags():
				return [Constants.StatusFlags.TOUGHNESS_BOON, Constants.StatusFlags.BOON]
