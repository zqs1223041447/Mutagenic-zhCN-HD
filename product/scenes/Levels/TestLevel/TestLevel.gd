extends BaseLevel

var death_screen = preload("res://scenes/Popups/DeathScreen.tscn")

@onready var spawn_parent = $Spawns
@onready var time_label = $CanvasLayer/MarginContainer/VBoxContainer/HBoxContainer/TimeLabel

var time_to_next_spawn = 2
var current_wave = 1
var _is_spawning = true

const TIME_PER_WAVE = 45.0

var time_remaining = TIME_PER_WAVE

func get_spawnables():
				return spawnables

func _ready():
				_seed_legacy_tiles()
				if _harness_request_present():
								await _run_combat_harness()
								return
				if player:
								player.global_position = Vector2.ZERO
								read_tiles()
				await FrameTimer.idle_frame(self).timeout
				emit_signal("map_done")
				Globals.reset()
				spawn_cluster_in_ladder(0, 0, 300, current_wave)

func _seed_legacy_tiles() -> void:
				# Godot 4 迁移补种：TestLevel.tscn 的 G3 tile_data（PackedInt32Array 三元组）
				# 在 G4 加载时是未知属性、被静默丢弃，TileMap 因此为空 -> read_tiles 无瓦片
				# -> navmesh 空崩溃。这里把解码出的 320 个格子坐标回种到 potential_tiles，
				# 由 process_tiles 的 set_cells_terrain_connect 正常铺瓦。若场景将来带上了
				# G4 tile_map_data（used_cells>0），本函数按守卫直接跳过，行为不变。
				if tiles.get_used_cells(0).size() > 0:
								return
				var file = FileAccess.open("res://scenes/Levels/TestLevel/legacy_tile_data.json", FileAccess.READ)
				if file == null:
								print("TestLevel: legacy_tile_data.json missing; TileMap stays empty")
								return
				var parsed = JSON.parse_string(file.get_as_text())
				file.close()
				if typeof(parsed) != TYPE_DICTIONARY or not parsed.has("cells"):
								print("TestLevel: legacy_tile_data.json unparsable")
								return
				for cell in parsed["cells"]:
								set_potential_tile(int(cell[0]), int(cell[1]), true)

func _harness_request_present() -> bool:
				# P3-BC combat harness gate: harness mode only when the host driver
				# planted a request file; normal gameplay path stays untouched.
				return FileAccess.file_exists("user://combat_harness/request.json")

func _run_combat_harness() -> void:
				# Same world-entry pipeline as the normal path (player repositioned,
				# read_tiles -> process_tiles -> navmesh), minus the ambient 300-mob
				# ladder dump; ScenarioDirector drives the scripted scenario and
				# quits the process when telemetry is written.
				if player:
								player.global_position = Vector2.ZERO
								read_tiles()
				await FrameTimer.idle_frame(self).timeout
				emit_signal("map_done")
				Globals.reset()
				var director_script = load("res://scenes/Levels/_validate/ScenarioDirector.gd")
				var director = director_script.new()
				add_child(director)
				director.run_harness(self)
