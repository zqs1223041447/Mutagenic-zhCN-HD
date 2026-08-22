extends Node


func should_hide_item(item):
				if GameState.saved_stats.settings.hide_low_level:
								return item.level < GameState.get_active_stats().account_level - 20 and item.level < 80 and not item.unique
				return false
