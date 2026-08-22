extends Node
## P3-H2 probe driver: player-position save persistence roundtrip.
##
## Enters a minimal world context (player node published into the globals,
## exactly the way BaseLevel publishes it), saves through the REAL
## GameState.do_save_game(), resets in-memory state, reloads through the REAL
## GameState.load_game() and asserts the position survives the roundtrip
## within tolerance.  A negative control then removes the world context and
## re-saves: the position field must be OMITTED from the written character
## dict (pre-H2 schema shape, backward compatible).
##
## Lives under Projectiles/_validate/ because Levels/_validate is outside this
## lane's write domain this round; relocated once ownership allows.
##
## Results print as one JSON line wrapped in P3_PROBE_RESULT:{...}.
## Exit codes: 0 = PASS, 2 = FAIL, 3 = watchdog timeout.

const CHAR_NAME: String = "P3ProbeChar"
const CHAR_CLASS: String = "MAGE"
const MARKER: String = "P3_PROBE_RESULT:"
const RELOAD_TIMEOUT_FRAMES: int = 1800
const WATCHDOG_SECONDS: float = 180.0
const POSITION_TOLERANCE: float = 0.01
const TARGET_POSITION := Vector2(123.5, -77.25)
const TARGET_LEVEL := "p3_h2_probe"

var results: Dictionary = {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var watchdog := get_tree().create_timer(WATCHDOG_SECONDS)
	watchdog.timeout.connect(_on_watchdog)
	# Detach from the current_scene slot: load_game() ends with
	# change_scene_to_file(Menu), which would free this driver otherwise.
	await get_tree().process_frame
	var anchor := Node.new()
	anchor.name = "P3H2Anchor"
	get_tree().root.add_child(anchor)
	get_tree().current_scene = anchor
	_orchestrate()


func _on_watchdog() -> void:
	if bool(results.get("finished", false)):
		return
	results["watchdog_timeout"] = true
	results["pass"] = false
	results["finished"] = true
	print(MARKER + JSON.stringify(results))
	get_tree().quit(3)


func _backup_save() -> Dictionary:
	var p: String = GameState.get_save_name()
	var info := {"had": FileAccess.file_exists(p), "text": ""}
	if bool(info["had"]):
		var f := FileAccess.open(p, FileAccess.READ)
		if f:
			info["text"] = f.get_as_text()
	return info


func _restore_save(backup: Dictionary) -> void:
	GameState.needs_save = false
	var p: String = GameState.get_save_name()
	if bool(backup["had"]):
		var f := FileAccess.open(p, FileAccess.WRITE)
		if f:
			f.store_string(str(backup["text"]))
			f.close()
	elif FileAccess.file_exists(p):
		DirAccess.remove_absolute(p)


func _until(pred: Callable, frames: int) -> bool:
	for i in range(frames):
		if pred.call():
			return true
		await get_tree().process_frame
	return bool(pred.call())


func _read_saved_character() -> Dictionary:
	var save_path: String = GameState.get_save_name()
	if not FileAccess.file_exists(save_path):
		return {}
	var f := FileAccess.open(save_path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	var chars: Variant = parsed.get("characters", {})
	if typeof(chars) != TYPE_DICTIONARY or not chars.has(CHAR_NAME):
		return {}
	var c: Dictionary = chars[CHAR_NAME]
	return c


func _position_matches(pos: Dictionary) -> bool:
	if typeof(pos) != TYPE_DICTIONARY:
		return false
	return absf(float(pos.get("x", 0.0)) - TARGET_POSITION.x) <= POSITION_TOLERANCE \
			and absf(float(pos.get("y", 0.0)) - TARGET_POSITION.y) <= POSITION_TOLERANCE \
			and str(pos.get("level", "")) == TARGET_LEVEL


func _enter_world_context(root: Node) -> Dictionary:
	var level_layer := Node2D.new()
	level_layer.name = "ProbeLevelLayer"
	root.add_child(level_layer)
	var ground := Node2D.new()
	ground.name = "ProbeGround"
	root.add_child(ground)
	GameState.set_global("level_layer", level_layer)
	GameState.set_global("ground", ground)

	var player := Node2D.new()
	player.name = "ProbePlayer"
	root.add_child(player)
	GameState.set_global("player", player)
	Globals.selected_level = TARGET_LEVEL
	return {"player": player}


func _orchestrate() -> void:
	seed(20260822)
	var backup := _backup_save()

	var h2: Dictionary = {}

	# create_new_character (not add_character): migrate() erases characters
	# whose mutation_tree_loadout.class is null, so the probe character needs
	# a real class to survive the reload.
	if not GameState.saved_stats.characters.has(CHAR_NAME):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
	Globals.selected_character_name = CHAR_NAME
	h2["character_ready"] = GameState.saved_stats.characters.has(CHAR_NAME)

	# --- positive path: world context -> save -> reset -> load --------------
	var world := _enter_world_context(self)
	world["player"].position = TARGET_POSITION
	await get_tree().process_frame

	GameState.do_save_game()
	var mem_pos: Variant = GameState.saved_stats.characters[CHAR_NAME].get("position")
	h2["memory_position_written"] = _position_matches(mem_pos if typeof(mem_pos) == TYPE_DICTIONARY else {})

	var written: Dictionary = _read_saved_character()
	h2["file_has_position_field"] = written.has("position")
	h2["file_position_roundtrip_shape"] = _position_matches(written.get("position", {}) if typeof(written.get("position", {})) == TYPE_DICTIONARY else {})

	GameState.reset_saved_state()
	GameState.load_game()
	h2["reloaded_character_present"] = await _until(func() -> bool:
		return GameState.saved_stats.characters.has(CHAR_NAME), RELOAD_TIMEOUT_FRAMES)

	var reloaded_pos: Variant = GameState.saved_stats.characters.get(CHAR_NAME, {}).get("position")
	h2["reloaded_position_within_tolerance"] = _position_matches(
			reloaded_pos if typeof(reloaded_pos) == TYPE_DICTIONARY else {})
	if typeof(reloaded_pos) == TYPE_DICTIONARY:
		h2["reloaded_position_values"] = reloaded_pos

	# --- negative control: no world context -> field omitted ----------------
	if is_instance_valid(world["player"]):
		world["player"].queue_free()
	GameState.set_global("player", null)
	await get_tree().process_frame

	GameState.do_save_game()
	var omitted: Dictionary = _read_saved_character()
	h2["no_world_context_omits_field"] = not omitted.has("position")

	h2["pass"] = bool(h2["character_ready"]) \
			and bool(h2["memory_position_written"]) \
			and bool(h2["file_has_position_field"]) \
			and bool(h2["file_position_roundtrip_shape"]) \
			and bool(h2["reloaded_character_present"]) \
			and bool(h2["reloaded_position_within_tolerance"]) \
			and bool(h2["no_world_context_omits_field"])
	h2["errors"] = []
	for k in h2.keys():
		if h2[k] is bool and not h2[k]:
			h2["errors"].append("h2." + str(k))

	_restore_save(backup)
	results = h2
	results["finished"] = true
	print(MARKER + JSON.stringify(results))
	await get_tree().process_frame
	get_tree().quit(0 if bool(h2["pass"]) else 2)
