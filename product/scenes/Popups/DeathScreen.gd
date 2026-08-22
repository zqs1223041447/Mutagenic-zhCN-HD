extends PopupBase

var character_unlock_item = preload("res://scenes/Popups/Unlocks/CharacterUnlockItem.tscn")
var level_unlock_item = preload("res://scenes/Popups/Unlocks/LevelUnlockItem.tscn")

@onready var gear = GameState.get_global("player").get_node("Gear")
@onready var stats = GameState.get_global("player").get_node("Stats")
@onready var world = GameState.get_global("world")

var out_of_time = false


func _ready() -> void :
				$CenterContainer/PanelContainer/CenterContainer/ReturnButton.grab_focus()

				GameState.get_active_stats().orbs.blue += stats.metrics.orbs.blue
				GameState.get_active_stats().orbs.red += stats.metrics.orbs.red
				GameState.get_active_stats().orbs.green += stats.metrics.orbs.green
				GameState.get_active_stats().orbs.gold += stats.metrics.orbs.gold
				GameState.get_active_stats().orbs.corruption += stats.metrics.orbs.corruption
				GameState.save_game(false)

				if Levels.is_current_level_ladder():
								upload_score_and_show_result()
				else:
								$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo.visible = false

				if out_of_time:
								$CenterContainer/PanelContainer/CenterContainer/HBoxContainer/ItemSummary/OutOfTime.visible = true

func _exit_tree() -> void :
				world.switch_levels("hideout", true)

func _on_Button_pressed() -> void :
				PopupManager.pop_popup()

func upload_score_and_show_result():
				if not Levels.get_current_leaderboard_name():
								return
				Leaderboard.connect("uploaded", Callable(self, "_on_upload"))
				var computed_score = Globals.compute_score()
				$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo/VBoxContainer/ThisRunLabel.text = "This Run Score: " + str(computed_score)
				print("Score: ", computed_score, " waves ", Globals.waves_completed, " time ", Globals.last_wave_time)
				if computed_score >= 0:
								Leaderboard.upload_score(Levels.get_current_leaderboard_name(), computed_score)
				else:
								$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo/VBoxContainer/ChallengeRankLabel.text = "Score too low"

func _on_upload(new_rank, score):
				if new_rank > 0:
								$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo/VBoxContainer/ChallengeRankLabel.text = "Rank " + str(new_rank) + " with a score of " + str(score)
				elif new_rank == 0:
								$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo/VBoxContainer/ChallengeRankLabel.text = "Rank did not change"
				elif new_rank == - 2:
								$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo/VBoxContainer/ChallengeRankLabel.text = "Edited Save File"
				elif new_rank == - 3:
								$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo/VBoxContainer/ChallengeRankLabel.text = "Score too low"
				elif new_rank == - 1:
								$CenterContainer/PanelContainer/CenterContainer/ChallengeInfo/VBoxContainer/ChallengeRankLabel.text = "Error Uploading Score"


				
				Leaderboard.reload_leaderboards()
