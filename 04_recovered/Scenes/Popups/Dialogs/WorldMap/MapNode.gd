extends Node2D

signal focus_changed

onready var scores = $MapButton / StatInfoContainer / VBoxContainer / LeaderboardInfo / Scores

var node_id
var zone_level = 1
var iiq = 0.0
var iir = 0.0


func _ready() -> void :
				
				if node_id == "root":
								visible = false
				else:
								var map_name = WorldMapData.get_map_name(node_id)
								$MapButton / StatInfoContainer / VBoxContainer / NodeNameLabel.text = Levels.config[map_name].name
								$MapButton / MapIcon.texture = Levels.config[map_name].icon
								zone_level = WorldMapUtils.get_stage_level(node_id)
								$MapButton / StatInfoContainer / VBoxContainer / ZoneLabel.text = "Zone Level: " + str(zone_level)

								
								if StageProgress.is_neighbor_completed(node_id) or WorldMapData.is_connected_to_root(node_id):
												$MapButton.disabled = false
												modulate = Color.white

								else:
												$MapButton.disabled = true
												modulate = Color(1, 1, 1, 0.2)



								if Levels.config[map_name].has("leaderboard"):
												render_leaderboard(Levels.config[map_name].leaderboard)
								else:
												iiq = ZoneScaling.get_iiq_scaler(zone_level)
												iir = ZoneScaling.get_iir_scaler(zone_level)
												if iiq > 0:
																$MapButton / StatInfoContainer / VBoxContainer / ItemQuanityLabel.visible = true
																$MapButton / StatInfoContainer / VBoxContainer / ItemQuanityLabel.text = str(stepify(iiq * 100.0, 1)) + "% Increased Quantity of Items Found"
												if iir > 0:
																$MapButton / StatInfoContainer / VBoxContainer / ItemRarityLabel.visible = true
																$MapButton / StatInfoContainer / VBoxContainer / ItemRarityLabel.text = str(stepify(iir * 100.0, 1)) + "% Increased Rarity of Items Found"

func render_leaderboard(leaderboard):
				$MapButton / StatInfoContainer / VBoxContainer / LeaderboardInfo.visible = true

				var entries = Leaderboard.get_entries(leaderboard)
				for entry in entries:
								var rank_label = Label.new()
								rank_label.align = Label.ALIGN_LEFT
								rank_label.text = str(entry.global_rank)
								scores.add_child(rank_label)
								var name_label = Label.new()
								name_label.align = Label.ALIGN_LEFT
								name_label.text = entry.name
								scores.add_child(name_label)
								var level_label = Label.new()
								level_label.align = Label.ALIGN_RIGHT
								if entry.details[0] > 0:
												level_label.text = str(entry.details[0])
								else:
												level_label.text = "?"
								scores.add_child(level_label)
								var spec_label = Label.new()
								spec_label.align = Label.ALIGN_RIGHT
								spec_label.text = str(PlayableClasses.get_spec_name_from_id(entry.details[1]))
								spec_label.modulate = PlayableClasses.get_spec_color_from_id(entry.details[1])
								scores.add_child(spec_label)
								var score_label = Label.new()
								score_label.align = Label.ALIGN_RIGHT
								score_label.text = str(entry.score)
								scores.add_child(score_label)

func set_zoom(zoom):
				$MapButton / StatInfoContainer.rect_scale = Vector2(1.0 / zoom, 1.0 / zoom)

func grab_focus():
				show_hover()

func release_focus():
				hide_hover()

func show_hover() -> void :
				z_index = 5
				$MapButton.grab_focus()

func hide_hover() -> void :
				z_index = 1
				$MapButton.release_focus()

func _on_focus() -> void :
				$MapButton / StatInfoContainer.visible = true
				$MapButton / Glow.visible = true
				$MapButton / Glow.frame = 0
				z_index = 5
				emit_signal("focus_changed")

func _on_focus_loss() -> void :
				$MapButton / StatInfoContainer.visible = false
				$MapButton / Glow.visible = false
				z_index = 1
				emit_signal("focus_changed")

func _on_MapButton_mouse_entered() -> void :
				show_hover()

func _on_MapButton_mouse_exited() -> void :
				hide_hover()

func _on_MapButton_pressed() -> void :
				GameState.save_recent_stage(node_id)
				GameState.set_global("active_stage_id", node_id)
				GameState.get_global("world").switch_levels(node_id, true, zone_level)
