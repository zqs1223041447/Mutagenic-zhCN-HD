extends Node
## P4-A C2 driver: saved-position application on world re-entry.
##
## 1. enter World.tscn (production chain), wait map ready
## 2. teleport player to a navmesh-verified open spot, do_save_game()
##    -> assert characters[char].position == {x,y,level="test_level"}
## 3. re-enter World.tscn -> assert player spawned AT the saved position
##    (C2 apply runs after the default ZERO spawn)
## 4. absence branch: erase position in memory, re-enter again
##    -> assert default spawn at Vector2.ZERO (behaviour unchanged)

const CHAR_NAME: String = "P4APosProbeChar"
const CHAR_CLASS: String = "MAGE"
const MARKER: String = "P3_PROBE_RESULT:"
const WATCHDOG_SECONDS: float = 300.0

var results: Dictionary = {"task": "P4-A-C2", "apply": {}, "absence": {}}
var backup_text: String = ""
var had_backup: bool = false


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


func _enter_world() -> Dictionary:
	var out := {"entered": false, "player": null}
	Globals.selected_level = "test_level"
	if get_tree().change_scene_to_file("res://scenes/World.tscn") != OK:
		return out
	var is_world := func() -> bool:
		var cs := get_tree().current_scene
		return cs != null and cs.scene_file_path.ends_with("World.tscn")
	if not await _until(is_world, 900):
		return out
	out["entered"] = true
	var has_player := func() -> bool:
		var p: Variant = GameState.get_global("player")
		return p != null and is_instance_valid(p) and p.is_inside_tree()
	await _until(has_player, 900)
	out["player"] = GameState.get_global("player")
	var map_ready := func() -> bool:
		var nm: Variant = Globals.navmesh
		if nm == null or not is_instance_valid(nm):
			return false
		var astar: Variant = nm.get("navmesh")
		return astar != null and is_instance_valid(astar) and astar.get_point_count() > 0
	await _until(map_ready, 1500)
	return out


func _orchestrate() -> void:
	var apply: Dictionary = {}
	var absence: Dictionary = {}

	if not GameState.saved_stats.characters.has(CHAR_NAME):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
		await _until(func() -> bool: return GameState.saved_stats.characters.has(CHAR_NAME), 120)
	Globals.selected_character_name = CHAR_NAME

	var anchor := Node.new()
	get_tree().root.add_child.call_deferred(anchor)
	await get_tree().process_frame
	get_tree().current_scene = anchor

	# ---------- phase 1: save at a known open spot ----------
	var entry: Dictionary = await _enter_world()
	apply["world_entered"] = entry["entered"]
	var player: Node = entry["player"]
	var spot := Vector2.ZERO
	if player != null:
		var nm: Variant = Globals.navmesh
		var astar: Variant = nm.get("navmesh") if nm != null and is_instance_valid(nm) else null
		if astar != null and is_instance_valid(astar) and astar.get_point_count() > 0:
			spot = astar.get_point_position(0) * Vector2(32, 32) + Vector2(16, 16)
		player.global_position = spot
		player.linear_velocity = Vector2.ZERO
	apply["teleport_target"] = {"x": snappedf(spot.x, 0.01), "y": snappedf(spot.y, 0.01)}
	GameState.do_save_game()
	var pos: Variant = GameState.saved_stats.get("characters", {}).get(CHAR_NAME, {}).get("position")
	apply["saved_position_field"] = pos
	apply["save_records_position"] = typeof(pos) == TYPE_DICTIONARY \
			and absf(float(pos.get("x", 99999.0)) - spot.x) < 0.5 \
			and absf(float(pos.get("y", 99999.0)) - spot.y) < 0.5 \
			and str(pos.get("level", "")) == "test_level"

	# ---------- phase 2: re-enter, expect C2 to restore the spot ----------
	var reentry: Dictionary = await _enter_world()
	apply["reentered"] = reentry["entered"]
	var p2: Node = reentry["player"]
	if p2 != null:
		apply["respawn_position"] = {
			"x": snappedf(p2.global_position.x, 0.01),
			"y": snappedf(p2.global_position.y, 0.01),
		}
		apply["position_applied"] = p2.global_position.distance_to(spot) < 16.0
	else:
		apply["position_applied"] = false

	# ---------- phase 3: absence keeps default spawn ----------
	GameState.saved_stats.get("characters", {}).get(CHAR_NAME, {}).erase("position")
	var third: Dictionary = await _enter_world()
	absence["reentered_without_position"] = third["entered"]
	var p3: Node = third["player"]
	if p3 != null:
		absence["default_spawn_position"] = {
			"x": snappedf(p3.global_position.x, 0.01),
			"y": snappedf(p3.global_position.y, 0.01),
		}
		absence["default_spawn_kept"] = absf(p3.global_position.x) < 8.0 and absf(p3.global_position.y) < 40.0
	else:
		absence["default_spawn_kept"] = false

	apply["pass"] = bool(apply.get("world_entered")) and bool(apply.get("save_records_position")) \
			and bool(apply.get("reentered")) and bool(apply.get("position_applied"))
	absence["pass"] = bool(absence.get("reentered_without_position")) and bool(absence.get("default_spawn_kept"))

	results["apply"] = apply
	results["absence"] = absence
	results["pass"] = bool(apply["pass"]) and bool(absence["pass"])
	results["errors"] = _collect_failed(apply, "apply") + _collect_failed(absence, "absence")
	results["finished"] = true
	_restore_save()
	print(MARKER + JSON.stringify(results))
	await get_tree().process_frame
	get_tree().quit(0 if bool(results["pass"]) else 2)


func _collect_failed(phase: Dictionary, prefix: String) -> Array:
	var failed: Array = []
	for k in phase.keys():
		if phase[k] is bool and not phase[k]:
			failed.append(prefix + "." + str(k))
	return failed
