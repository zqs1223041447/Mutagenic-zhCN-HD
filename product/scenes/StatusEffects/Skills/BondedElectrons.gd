extends BaseEffect

func get_lightning_override():
				var applier_stats = applier_stats_weakref.get_ref()
				if applier_stats:
								return applier_stats.gs("lightning_resistance")

				return 0

func get_status_flags():
				return [Constants.StatusFlags.BONDED_ELECTRONS]
