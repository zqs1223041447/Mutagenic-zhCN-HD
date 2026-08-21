extends Node

signal loaded
signal uploaded(new_rank)
signal downloaded(results)

var Steam = Engine.get_singleton("Steam") if Engine.has_singleton("Steam") else null

var result = {
				"handle": 0, 
				"found": 0, 
}

var upload_result = null

var LEADERBOARD_HANDLES = {}
var LEADERBOARD_DATA = {}

func initialize():
				if Constants.USE_STEAM:
								Steam.connect("leaderboard_find_result", Callable(self, "_on_leaderboard_find_result"))
								Steam.connect("leaderboard_score_uploaded", Callable(self, "_on_leaderboard_score_uploaded"))
								Steam.connect("leaderboard_scores_downloaded", Callable(self, "_on_leaderboard_scores_downloaded"))
								Steam.setLeaderboardDetailsMax(16)
								load_leaderboard_handles()

func load_leaderboard_handles():
				for level in Levels.config:
								var info = Levels.config[level]
								if info.has("leaderboard"):
												var leaderboard = info.leaderboard
												if not leaderboard:
																print("Could not find leaderboard for: ", level)
																continue
												Steam.findLeaderboard(leaderboard)
												await Steam.leaderboard_find_result
												if result.found == 1:
																LEADERBOARD_HANDLES[leaderboard] = result.handle
				emit_signal("loaded")
				reload_leaderboards()

func reload_leaderboards():
				for handle in LEADERBOARD_HANDLES:
								Steam.downloadLeaderboardEntries(1, 25, 0, LEADERBOARD_HANDLES[handle])
								await Steam.leaderboard_scores_downloaded

func _on_leaderboard_find_result(handle, found):
				result.handle = handle
				result.found = found

func _on_leaderboard_score_uploaded(success, handle, score_info):
				print("Got leaderboard result for: ", handle, score_info)
				if success == 1:
								upload_result = {
												"score": score_info.score, 
												"changed": score_info.score_changed, 
												"new_rank": score_info.global_rank_new, 
												"old_rank": score_info.global_rank_prev, 
								}
				else:
								print("Failed to upload score")
								upload_result = null

func _on_leaderboard_scores_downloaded(message, handle, entries):
				var copied_result = entries.duplicate(true)
				for entry in copied_result:
								entry["name"] = Steam.getFriendPersonaName(entry["steam_id"])
				LEADERBOARD_DATA[handle] = copied_result

func upload_score(leaderboard_name, score):
				var active_stats = GameState.get_active_stats()
				var active_level = active_stats.account_level
				var active_class = active_stats.specialization_loadout. class 
				var extra_details = [active_level, PlayableClasses.get_playable_spec_id(active_class)]






				if score == 0:
								emit_signal("uploaded", - 3, 0)
								return

				if LEADERBOARD_HANDLES.has(leaderboard_name):
								var handle = LEADERBOARD_HANDLES[leaderboard_name]
								print("Found handle:", handle)
								Steam.uploadLeaderboardScore(score, true, extra_details, handle)
								await Steam.leaderboard_score_uploaded
								if upload_result:
												if upload_result.changed == 1:
																emit_signal("uploaded", upload_result.new_rank, upload_result.score)
												else:
																emit_signal("uploaded", upload_result.old_rank, upload_result.score)
												return
								else:
												print("No upload result found")
												emit_signal("uploaded", - 1, 0)
												return
				else:
								print("No leaderboard handle found")
								emit_signal("uploaded", - 1, 0)

func get_entries(leaderboard_name):
				if LEADERBOARD_HANDLES.has(leaderboard_name):
								var handle = LEADERBOARD_HANDLES[leaderboard_name]
								if LEADERBOARD_DATA.has(handle):
												var entries = LEADERBOARD_DATA[handle]
												return entries

				return []
