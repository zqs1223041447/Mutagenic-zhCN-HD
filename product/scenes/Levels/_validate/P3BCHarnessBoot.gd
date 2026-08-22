extends Node
## P3-BC combat harness boot: headless entry that reaches TestLevel through
## the production path (Globals.selected_level -> World.switch_levels spawns
## Player + TestLevel), so the harness exercises the real world-entry chain.
##
## Entry strategy mirrors P3BDriver:
##   1. "world_scene"     - change_scene_to_file(World.tscn).
##   2. "manual_assembly" - fallback used ONLY when World.tscn cannot load
##                          (parse errors in files owned by concurrent lanes);
##                          replicates World.switch_levels(reset=true) core.
##
## TestLevel.gd detects user://combat_harness/request.json (written by the
## host driver / p3_bc_launch_godot.py BEFORE this scene launches) and hands
## control to ScenarioDirector.gd, which quits the process when done.
## This boot only seeds the character, waits for the player to exist and
## guards the run with a watchdog. Save file is backed up and restored.

const CHAR_NAME := "P3BCHarnessChar"
const CHAR_CLASS := "MAGE"
const PLAYER_WAIT_FRAMES := 900
const WORLD_WAIT_FRAMES := 300
const WATCHDOG_SECONDS := 300.0

var backup_text := ""
var had_backup := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_backup_save()
	var watchdog := get_tree().create_timer(WATCHDOG_SECONDS)
	watchdog.timeout.connect(_on_watchdog)
	_orchestrate()


func _on_watchdog() -> void:
	print("[COMBAT_HARNESS_BOOT] watchdog timeout; quitting rc=3")
	get_tree().quit(3)


func _backup_save() -> void:
	var path: String = GameState.get_save_name()
	had_backup = FileAccess.file_exists(path)
	if had_backup:
		var file := FileAccess.open(path, FileAccess.READ)
		if file:
			backup_text = file.get_as_text()


func _restore_save() -> void:
	GameState.needs_save = false
	var path: String = GameState.get_save_name()
	if had_backup:
		var file := FileAccess.open(path, FileAccess.WRITE)
		if file:
			file.store_string(backup_text)
			file.close()
	elif FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)


func _orchestrate() -> void:
	if not GameState.saved_stats.characters.has(CHAR_NAME):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
	Globals.selected_character_name = CHAR_NAME

	# Swap out of the current_scene slot so scene changes cannot free us.
	var anchor := Node.new()
	anchor.name = "P3BCHarnessAnchor"
	get_tree().root.add_child(anchor)
	get_tree().current_scene = anchor

	Globals.selected_level = "test_level"
	var err := get_tree().change_scene_to_file("res://scenes/World.tscn")
	print("[COMBAT_HARNESS_BOOT] change_scene_to_file(World) -> ", err)

	var world_ready := func() -> bool:
		var player = GameState.get_global("player")
		return player != null and is_instance_valid(player) and player.is_inside_tree()
	var entered := false
	for i in range(WORLD_WAIT_FRAMES):
		if world_ready.call():
			entered = true
			break
		await get_tree().process_frame

	if not entered:
		print("[COMBAT_HARNESS_BOOT] World.tscn path failed; manual assembly fallback")
		entered = await _assemble_world_manually()

	var wait_frames := 0
	while not world_ready.call() and wait_frames < PLAYER_WAIT_FRAMES:
		await get_tree().process_frame
		wait_frames += 1
	if not world_ready.call():
		print("[COMBAT_HARNESS_BOOT] ERROR player never spawned; quitting rc=2")
		get_tree().quit(2)
		return
	print("[COMBAT_HARNESS_BOOT] player ready; ScenarioDirector drives the rest")


func _assemble_world_manually() -> bool:
	# Replicate World.switch_levels(stage_id="test_level", reset=true) core.
	Globals.reset()
	GameState.reset_globals()
	Globals.selected_level = "test_level"
	Globals.zone_level = Levels.config[Globals.selected_level].zone_level

	var level_layer := Node2D.new()
	level_layer.name = "HarnessLevelLayer"
	var ground := Node2D.new()
	var projectiles := Node2D.new()
	var sky := Node2D.new()
	add_child(level_layer)
	add_child(ground)
	add_child(projectiles)
	add_child(sky)

	var player: Node = (load("res://scenes/Player/Player.tscn") as PackedScene).instantiate()
	GameState.set_global("player", player)
	GameState.set_global("level_layer", level_layer)
	GameState.set_global("ground", ground)
	GameState.set_global("projectiles", projectiles)
	GameState.set_global("sky", sky)
	GameState.set_global("world", self)
	GameState.set_global("active_stage_id", "test_level")

	MapMods.reroll_mods(Globals.zone_level)

	var level: Node = (Levels.config["test_level"].level_scene as PackedScene).instantiate()
	level.spawnables = MonsterLevels.monsters_in["test_level"]
	GameState.set_global("level_scene", level)

	level.connect("map_done", Callable(self, "_on_harness_map_done"))
	level_layer.add_child(player)
	add_child(level)
	PopupManager.reset()
	Globals.reset_pause()

	for i in range(PLAYER_WAIT_FRAMES):
		if _map_done_flag:
			return true
		await get_tree().process_frame
	return _map_done_flag


var _map_done_flag := false


func _on_harness_map_done() -> void:
	_map_done_flag = true


func _exit_tree() -> void:
	_restore_save()
