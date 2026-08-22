extends Node
## P3-B probe driver: E2 (real world entry with player + tile pipeline)
## + E3 (movement via input actions + dash state/displacement).
##
## Entry strategy (recorded in results as world_entry_mode):
##   1. "world_scene"      — production path: change_scene_to_file(World.tscn),
##                           World.switch_levels spawns Player + TestLevel.
##   2. "manual_assembly"  — fallback used ONLY when World.tscn itself cannot
##                           load (e.g. parse errors in files owned by other
##                           lanes). Faithfully replicates the core of
##                           World.switch_levels(reset=true) so the substance
##                           under test — Player spawn, TestLevel._ready with
##                           player != null -> read_tiles -> process_tiles ->
##                           set_cells_terrain_connect + initialize_navmesh,
##                           then input-driven movement/dash — is still
##                           exercised end to end.
##
## Results printed as one JSON line wrapped in P3B_RESULT_JSON<<< >>> and
## parsed by scripts/validate/run_p3_b_world_movement.py.
## The user save file is backed up before any mutation and restored on exit.

const CHAR_NAME: String = "P3BProbeChar"
const CHAR_CLASS: String = "MAGE"
const MARKER: String = "P3_PROBE_RESULT:"
const WORLD_TIMEOUT_FRAMES: int = 900
const PLAYER_TIMEOUT_FRAMES: int = 900
const MAPDONE_TIMEOUT_FRAMES: int = 1500
const WALK_FRAMES: int = 45
const WATCHDOG_SECONDS: float = 300.0

var results: Dictionary = {"task": "P3-B", "e2": {}, "e3": {}}
var backup_text: String = ""
var had_backup: bool = false


class WorldStub extends Node2D:
	signal portal_spawned(location)
	signal level_changed


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_backup_save()
	var watchdog := get_tree().create_timer(WATCHDOG_SECONDS)
	watchdog.timeout.connect(_on_watchdog)
	_orchestrate()


func _on_watchdog() -> void:
	if bool(results.get("finished", false)):
		return
	results["watchdog_timeout"] = true
	results["pass"] = false
	results["finished"] = true
	print(MARKER + JSON.stringify(results))
	get_tree().quit(3)


func _collect_failed_checks(phase: Dictionary, prefix: String, skip: Array = []) -> Array:
	var failed: Array = []
	for k in phase.keys():
		if skip.has(str(k)):
			continue
		if phase[k] is bool and not phase[k]:
			failed.append(prefix + "." + str(k))
	return failed


func _backup_save() -> void:
	var p: String = GameState.get_save_name()
	had_backup = FileAccess.file_exists(p)
	if had_backup:
		var f := FileAccess.open(p, FileAccess.READ)
		if f:
			backup_text = f.get_as_text()


func _restore_save() -> void:
	GameState.needs_save = false
	var p: String = GameState.get_save_name()
	if had_backup:
		var f := FileAccess.open(p, FileAccess.WRITE)
		if f:
			f.store_string(backup_text)
			f.close()
	elif FileAccess.file_exists(p):
		DirAccess.remove_absolute(p)


func _until(pred: Callable, frames: int) -> bool:
	for i in range(frames):
		if pred.call():
			return true
		await get_tree().process_frame
	return pred.call() == true


func _physics_frames(n: int) -> void:
	for i in range(n):
		await get_tree().physics_frame


func _orchestrate() -> void:
	var e2: Dictionary = {}
	var e3: Dictionary = {}

	# --- ensure an active character exists (same API the UI calls) ---
	if not GameState.saved_stats.characters.has(CHAR_NAME):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
		await _until(func() -> bool: return GameState.saved_stats.characters.has(CHAR_NAME), 120)
	e2["probe_character_created"] = GameState.saved_stats.characters.has(CHAR_NAME)
	Globals.selected_character_name = CHAR_NAME

	# --- swap out of the current_scene slot so scene changes cannot free us ---
	var anchor := Node.new()
	anchor.name = "P3BSceneAnchor"
	get_tree().root.add_child.call_deferred(anchor)
	await get_tree().process_frame
	get_tree().current_scene = anchor

	var world: Node = null
	var player: Node = null
	var level: Node = null

	# --- entry attempt 1: production World.tscn path ---
	Globals.selected_level = "test_level"
	var change_err: int = get_tree().change_scene_to_file("res://scenes/World.tscn")
	e2["change_scene_ok"] = change_err == OK
	if change_err == OK:
		e2["world_entry_mode"] = "world_scene"
		var is_world := func() -> bool:
			var cs := get_tree().current_scene
			return cs != null and cs.scene_file_path.ends_with("World.tscn")
		var entered: bool = await _until(is_world, WORLD_TIMEOUT_FRAMES)
		e2["world_entered"] = entered
		world = get_tree().current_scene if entered else null

	# --- entry attempt 2: manual assembly replicating switch_levels(reset=true) ---
	if world == null:
		e2["world_entry_mode"] = "manual_assembly"
		e2["world_scene_blocked_note"] = (
			"World.tscn could not be loaded; see world_scene_blocked_by. "
			+ "Manual assembly replicates World.switch_levels(reset=true) core steps."
		)
		var assembled: Dictionary = await _assemble_world_manually()
		world = assembled.get("world")
		player = assembled.get("player")
		level = assembled.get("level")
		e2["world_entered"] = assembled.get("entered", false)

	var has_player := func() -> bool:
		var p: Variant = GameState.get_global("player")
		return p != null and is_instance_valid(p) and p.is_inside_tree()
	e2["player_spawned"] = await _until(has_player, PLAYER_TIMEOUT_FRAMES)
	if player == null and bool(e2["player_spawned"]):
		player = GameState.get_global("player")

	if level == null and world != null:
		var bg: Node = world.get_node_or_null("BackgroundContainer")
		if bg:
			for child in bg.get_children():
				var s: Script = child.get_script()
				if s != null and s.resource_path.contains("TestLevel"):
					level = child
	e2["test_level_instance_found"] = level != null and is_instance_valid(level)

	if world != null and player != null:
		var level_layer: Node = world.get_node_or_null("Level")
		if level_layer == null:
			level_layer = player.get_parent()
		# Godot 4: Node.is_a_parent_of 不存在，等价改为 is_ancestor_of。
		e2["player_parent_is_level_layer"] = level_layer != null and level_layer.is_ancestor_of(player)
	else:
		e2["player_parent_is_level_layer"] = false
	e2["active_stage_id"] = str(GameState.get_global("active_stage_id"))

	# --- wait for map_done: navmesh built is the strongest completion signal ---
	var map_ready := func() -> bool:
		var nm: Variant = Globals.navmesh
		if nm == null or not is_instance_valid(nm):
			return false
		var astar: Variant = nm.get("navmesh")
		return astar != null and is_instance_valid(astar) and astar.get_point_count() > 0
	e2["map_done"] = await _until(map_ready, MAPDONE_TIMEOUT_FRAMES)

	# --- determinize the sampling window ---
	# TestLevel._ready emits map_done BEFORE spawn_cluster_in_ladder dumps the
	# 300-mob wave, so navmesh-built alone does NOT mean the wave exists yet.
	# Wait for the wave, then cull it and let queue_free drain — otherwise mobs
	# land on the player mid-sampling and jam displacement measurements.
	var wave_seen := await _until(func() -> bool:
		return get_tree().get_nodes_in_group("enemies").size() >= 100, 600)
	e2["mob_wave_spawned"] = wave_seen
	e2["enemies_culled_early"] = _cull_enemies(level)
	await _physics_frames(8)
	e2["enemies_culled_early_second_pass"] = _cull_enemies(level)
	e2["enemies_remaining_after_cull"] = get_tree().get_nodes_in_group("enemies").size()
	if level != null and is_instance_valid(level):
		var tiles: Node = level.get_node_or_null("TileMap")
		if tiles != null:
			e2["tile_used_cells"] = tiles.get_used_cells(0).size()
		var spawnable: Array = level.get_all_spawnable_tiles()
		e2["spawnable_tile_count"] = spawnable.size()
	var nm: Variant = Globals.navmesh
	if nm != null and is_instance_valid(nm):
		var astar: Variant = nm.get("navmesh")
		if astar != null and is_instance_valid(astar):
			e2["navmesh_points"] = astar.get_point_count()
	e2["tiles_painted"] = int(e2.get("tile_used_cells", 0)) > 0
	e2["navmesh_built"] = int(e2.get("navmesh_points", 0)) > 0

	e2["pass"] = bool(e2.get("probe_character_created")) \
			and bool(e2.get("world_entered")) \
			and bool(e2.get("player_spawned")) \
			and bool(e2.get("test_level_instance_found")) \
			and bool(e2.get("player_parent_is_level_layer")) \
			and bool(e2.get("map_done")) \
			and bool(e2.get("tiles_painted")) \
			and bool(e2.get("navmesh_built"))
	results["e2"] = e2

	# --- E3 movement + dash ---
	if bool(e2.get("map_done")) and player != null and is_instance_valid(player):
		e3 = await _phase_e3(player, level)
	results["e3"] = e3

	results["pass"] = bool(e2.get("pass")) and bool(e3.get("pass"))
	var e3_skip: Array = ["player_sleeping_before", "player_freeze", "player_can_sleep",
		"walk_end_velocity_len", "dash_cd_before", "dash_cd_after_trigger"]
	var failed: Array = _collect_failed_checks(e2, "e2") \
			+ _collect_failed_checks(e3, "e3", e3_skip)
	if str(e2.get("world_entry_mode")) == "manual_assembly":
		# change_scene_ok=false is the EXPECTED trigger for the fallback path,
		# not a probe failure; drop it from the failure list.
		failed.erase("e2.change_scene_ok")
	results["errors"] = failed
	results["finished"] = true
	_restore_save()
	print(MARKER + JSON.stringify(results))
	await get_tree().process_frame
	get_tree().quit(0 if bool(results["pass"]) else 2)


func _assemble_world_manually() -> Dictionary:
	"""Replicate World.switch_levels(stage_id="test_level", reset=true) core.

	Only the steps required for level/player lifecycle are reproduced; the
	GUI/LoadingScreen/EscapeMenu wiring belongs to World.tscn and stays out.
	"""
	var out: Dictionary = {"entered": false, "world": null, "player": null, "level": null}

	var world_stub: WorldStub = WorldStub.new()
	world_stub.name = "P3BWorldStub"
	var level_layer := Node2D.new()
	level_layer.name = "P3BLevelLayer"
	var ground := Node2D.new()
	var projectiles := Node2D.new()
	var sky := Node2D.new()
	get_tree().root.add_child.call_deferred(world_stub)
	get_tree().root.add_child.call_deferred(level_layer)
	get_tree().root.add_child.call_deferred(ground)
	get_tree().root.add_child.call_deferred(projectiles)
	get_tree().root.add_child.call_deferred(sky)
	await get_tree().process_frame
	await get_tree().process_frame

	Globals.reset()
	GameState.reset_globals()
	Globals.selected_level = "test_level"
	Globals.zone_level = Levels.config[Globals.selected_level].zone_level

	var player: Node = (load("res://scenes/Player/Player.tscn") as PackedScene).instantiate()
	GameState.set_global("player", player)
	GameState.set_global("level_layer", level_layer)
	GameState.set_global("ground", ground)
	GameState.set_global("projectiles", projectiles)
	GameState.set_global("sky", sky)
	GameState.set_global("world", world_stub)
	GameState.set_global("active_stage_id", "test_level")

	MapMods.reroll_mods(Globals.zone_level)

	var level: Node = (Levels.config["test_level"].level_scene as PackedScene).instantiate()
	level.spawnables = MonsterLevels.monsters_in["test_level"]
	GameState.set_global("level_scene", level)

	var map_done_flag: Dictionary = {"done": false}
	level.connect("map_done", func() -> void: map_done_flag.done = true)

	level_layer.add_child(player)
	get_tree().root.add_child(level)
	# TestLevel._ready ran synchronously inside add_child and dumped the mob
	# wave; cull within the same frame so no physics tick can damage player.
	out["enemies_culled_at_spawn"] = _cull_enemies(level)
	PopupManager.reset()
	Globals.reset_pause()

	out["world"] = world_stub
	out["player"] = player
	out["level"] = level
	out["entered"] = await _until(func() -> bool: return bool(map_done_flag.done), MAPDONE_TIMEOUT_FRAMES)
	return out


func _cull_enemies(_level: Node) -> int:
	# Probe-side isolation: ladder waves dump hundreds of mobs around the
	# player origin. Cull tree-wide by group — spawn_in_ladder adds mobs to the
	# level_layer container, not to the level node, so scanning the level node
	# alone finds nothing.
	var culled: int = 0
	for mob in get_tree().get_nodes_in_group("enemies"):
		mob.queue_free()
		culled += 1
	return culled


func _phase_e3(player: Node, level: Node) -> Dictionary:
	var e3: Dictionary = {}

	await _physics_frames(10)
	e3["enemies_culled"] = _cull_enemies(level)
	e3["level_child_count"] = level.get_child_count() if level != null and is_instance_valid(level) else -1
	e3["enemies_in_group"] = get_tree().get_nodes_in_group("enemies").size()
	await _physics_frames(5)
	e3["enemies_culled_second_pass"] = _cull_enemies(level)

	# --- diagnostics: why would displacement be zero? ---
	var stats_node: Node = player.get_node_or_null("Stats")
	e3["movement_speed_stat"] = stats_node.gs("movement_speed") if stats_node != null else -1.0
	e3["player_sleeping_before"] = player.sleeping
	e3["player_freeze"] = player.freeze
	e3["player_can_sleep"] = player.can_sleep
	# Probe isolation: an actively-driven player never sleeps; a body that fell
	# asleep ignores impulses and would fake a movement regression.
	player.can_sleep = false
	player.sleeping = false

	# --- movement: the spawn point can be enclosed by terrain collision, so
	# sample at navmesh-verified open spots until one yields real displacement.
	player.can_sleep = false
	player.sleeping = false
	var walk_attempts: Array = []
	var moved_ok := false
	var p0 := Vector2.ZERO
	var p1 := Vector2.ZERO
	var nm: Variant = Globals.navmesh
	var astar: Variant = nm.get("navmesh") if nm != null and is_instance_valid(nm) else null
	if astar != null and is_instance_valid(astar):
		# NavMesh stores TILE coordinates (pathfinding scales them by cell_size
		# later); convert to world space before teleporting the player, else it
		# spawns embedded inside terrain and cannot move.
		var tile_size := Vector2(32, 32)
		if level != null and is_instance_valid(level):
			var tmap: Node = level.get_node_or_null("TileMap")
			if tmap != null and tmap.tile_set != null:
				tile_size = Vector2(tmap.tile_set.tile_size)
		for pi in range(astar.get_point_count()):
			if walk_attempts.size() >= 6:
				break
			var spot: Vector2 = astar.get_point_position(pi) * tile_size + tile_size * 0.5
			player.global_position = spot
			player.linear_velocity = Vector2.ZERO
			await _physics_frames(5)
			p0 = player.global_position
			Input.action_press("move_right")
			await _physics_frames(20)
			Input.action_release("move_right")
			p1 = player.global_position
			var ddx: float = p1.x - p0.x
			walk_attempts.append({
				"point_index": pi,
				"spot_x": snappedf(spot.x, 0.1),
				"dx": snappedf(ddx, 0.01),
			})
			if ddx > 15.0:
				moved_ok = true
				break
	e3["walk_attempts"] = walk_attempts
	e3["moved"] = moved_ok

	# --- dash while moving right (at the last sampled spot) ---
	Input.action_press("move_right")
	await _physics_frames(10)
	var d0: Vector2 = player.global_position
	var cd_before: float = float(player.dash_cooldown)
	Input.action_press("dash")
	await _physics_frames(3)
	Input.action_release("dash")
	var fired: bool = float(player.dash_cooldown) > 0.0
	e3["dash_cd_before"] = cd_before
	e3["dash_cd_after_trigger"] = snappedf(float(player.dash_cooldown), 0.001)
	await _physics_frames(15)
	Input.action_release("move_right")
	var d1: Vector2 = player.global_position
	e3["dash_burst_px"] = snappedf((d1 - d0).length(), 0.01)
	e3["dash_fired_state"] = fired
	e3["dash_pass"] = fired

	e3["pass"] = bool(e3.get("moved")) and bool(e3.get("dash_pass"))
	return e3
