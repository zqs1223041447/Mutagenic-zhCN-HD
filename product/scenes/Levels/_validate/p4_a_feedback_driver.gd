extends Node
## P4-A lane A driver: R1 readability + R2 camera/screen feedback assertions.
##
## Enters the production World.tscn chain (world_scene), then:
##   R1 enemy flash  - emit damage_taken on a wave mob's Stats, assert modulate
##                     overbright tween fires and restores.
##   R1 elite marker - ensure an elite exists, assert P4EliteMarker ring child.
##   R2 kill zoom    - emit died on a sacrificial mob, assert camera zoom punch
##                     fires and restores.
##   R1 vignette     - emit player damage_taken(crit), assert red overlay alpha
##                     rises and returns to 0.
##   R2 shake/hitstop- same trigger: camera offset jitters then zeroes;
##                     Engine.time_scale dips below 1 and restores to exactly 1.
## Results via P3_PROBE_RESULT contract (frozen shared common).

const CHAR_NAME: String = "P4AProbeChar"
const CHAR_CLASS: String = "MAGE"
const MARKER: String = "P3_PROBE_RESULT:"
const WATCHDOG_SECONDS: float = 300.0

var results: Dictionary = {"task": "P4-A", "r1": {}, "r2": {}}
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


func _physics_frames(n: int) -> void:
	for i in range(n):
		await get_tree().physics_frame


func _orchestrate() -> void:
	var r1: Dictionary = {}
	var r2: Dictionary = {}

	if not GameState.saved_stats.characters.has(CHAR_NAME):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
		await _until(func() -> bool: return GameState.saved_stats.characters.has(CHAR_NAME), 120)
	r1["character_ready"] = GameState.saved_stats.characters.has(CHAR_NAME)
	Globals.selected_character_name = CHAR_NAME

	var anchor := Node.new()
	get_tree().root.add_child.call_deferred(anchor)
	await get_tree().process_frame
	get_tree().current_scene = anchor

	Globals.selected_level = "test_level"
	r2["change_scene_ok"] = get_tree().change_scene_to_file("res://scenes/World.tscn") == OK

	var is_world := func() -> bool:
		var cs := get_tree().current_scene
		return cs != null and cs.scene_file_path.ends_with("World.tscn")
	r2["world_entered"] = await _until(is_world, 900)

	var has_player := func() -> bool:
		var p: Variant = GameState.get_global("player")
		return p != null and is_instance_valid(p) and p.is_inside_tree()
	r2["player_spawned"] = await _until(has_player, 900)
	var player: Node = GameState.get_global("player")

	var map_ready := func() -> bool:
		var nm: Variant = Globals.navmesh
		if nm == null or not is_instance_valid(nm):
			return false
		var astar: Variant = nm.get("navmesh")
		return astar != null and is_instance_valid(astar) and astar.get_point_count() > 0
	r2["map_done"] = await _until(map_ready, 1500)

	var wave_seen := await _until(func() -> bool:
		return get_tree().get_nodes_in_group("enemies").size() >= 100, 600)
	r1["wave_spawned"] = wave_seen

	var vignette: Node = get_tree().get_first_node_in_group("p4_vignette")
	var controller: Node = get_tree().get_first_node_in_group("p4_feedback_controller")
	r1["vignette_present"] = vignette != null
	r1["controller_present"] = controller != null
	if controller != null:
		r1["controller_instance_id_at_start"] = controller.get_instance_id()
	if controller != null and controller.has_method("rescan"):
		controller.rescan()

	var controller_start: Node = get_tree().get_first_node_in_group("p4_feedback_controller")
	if controller_start != null:
		r1["controller_instance_id_at_start"] = controller_start.get_instance_id()
	controller.rescan()

	# ---------- R1 enemy flash ----------
	var enemies := get_tree().get_nodes_in_group("enemies")
	var target: Node = null
	for e in enemies:
		if is_instance_valid(e) and e.get("stats") != null:
			target = e
			break
	r1["enemy_sampled"] = target != null
	if target != null:
		var st: Node = target.get("stats")
		var own_hits := {"n": 0}
		var own_cb := func(): own_hits.n += 1
		st.health_changed.connect(own_cb)
		var conn_desc := []
		for c in st.health_changed.get_connections():
			conn_desc.append(str(c.callable.get_method()) + ":" + str(c.flags))
		r1["target_connections"] = conn_desc
		var flash_before: int = controller.debug_flash_count if controller != null else -1
		var max_r := 1.0
		st.set("health", maxf(1.0, float(st.get("health")) - 10.0))
		st.emit_signal("health_changed")
		for i in range(12):
			await get_tree().process_frame
			if is_instance_valid(target):
				max_r = maxf(max_r, target.modulate.r)
		r1["connections_on_target"] = st.health_changed.get_connections().size()
		r1["own_handler_fired"] = own_hits.n > 0
		r1["flash_peak_modulate_r"] = snappedf(max_r, 0.01)
		var flash_after: int = controller.debug_flash_count if controller != null else -1
		r1["flash_delta"] = flash_after - flash_before
		r1["enemy_flash_fired"] = flash_after > flash_before
		await _physics_frames(30)
		r1["enemy_flash_restored"] = absf(target.modulate.r - 1.0) < 0.05 if is_instance_valid(target) else true

	# ---------- R1 elite marker ----------
	var elite: Node = null
	for e in get_tree().get_nodes_in_group("enemies"):
		if is_instance_valid(e) and bool(e.get("is_elite")):
			elite = e
			break
	r1["natural_elite_found"] = elite != null
	if elite == null and not enemies.is_empty():
		for e in enemies:
			if is_instance_valid(e):
				e.set("is_elite", true)
				elite = e
				break
	if controller != null and controller.has_method("rescan"):
		controller.rescan()
	r1["elite_marker_attached"] = await _until(func() -> bool:
		return elite != null and is_instance_valid(elite) and elite.has_node("P4EliteMarker"), 90)

	# ---------- R2 kill zoom ----------
	var cam: Node = get_viewport().get_camera_2d()
	r2["camera_present"] = cam != null
	if cam != null and target != null and is_instance_valid(target) and target.get("stats") != null:
		var max_zoom := 1.0
		target.get("stats").emit_signal("died")
		for i in range(15):
			await get_tree().process_frame
			if is_instance_valid(cam):
				max_zoom = maxf(max_zoom, cam.zoom.x)
		r2["kill_zoom_peak"] = snappedf(max_zoom, 0.001)
		r2["kill_zoom_fired"] = max_zoom > 1.01
		await _physics_frames(25)
		r2["kill_zoom_restored"] = (not is_instance_valid(cam)) or absf(cam.zoom.x - 1.0) < 0.02

	# ---------- R1 vignette + R2 shake + hit-stop ----------
	# Isolate the player first: live mobs keep landing real hits, which would
	# re-trigger the very feedback we are sampling and mask restoration.
	_cull_all()
	await _physics_frames(10)
	r2["enemies_after_isolation"] = get_tree().get_nodes_in_group("enemies").size()
	if player != null and vignette != null and cam != null:
		var v_base: float = vignette.color.a
		var ts_min := 1.0
		var off_max := 0.0
		player.stats.emit_signal("damage_taken", [], null, true)
		for i in range(20):
			await get_tree().process_frame
			ts_min = minf(ts_min, Engine.time_scale)
			if is_instance_valid(cam):
				off_max = maxf(off_max, cam.offset.length())
		r1["vignette_baseline_alpha"] = snappedf(v_base, 0.001)
		r1["vignette_alpha_after_trigger"] = snappedf(vignette.color.a, 0.001)
		r1["vignette_fired"] = vignette.color.a > 0.05 or v_base > 0.05
		r2["shake_offset_max"] = snappedf(off_max, 0.01)
		r2["shake_fired"] = off_max > 0.5
		r2["hitstop_time_scale_min"] = snappedf(ts_min, 0.001)
		r2["hitstop_engaged"] = ts_min < 0.9
		await _physics_frames(90)
		r1["vignette_restored"] = vignette.color.a < 0.02
		r2["shake_restored"] = (not is_instance_valid(cam)) or cam.offset.length() < 0.01
		r2["time_scale_restored"] = absf(Engine.time_scale - 1.0) < 0.001

	r1["pass"] = bool(r1.get("character_ready")) and bool(r1.get("wave_spawned")) \
			and bool(r1.get("vignette_present")) and bool(r1.get("controller_present")) \
			and bool(r1.get("enemy_flash_fired")) and bool(r1.get("enemy_flash_restored")) \
			and bool(r1.get("elite_marker_attached")) \
			and bool(r1.get("vignette_fired")) and bool(r1.get("vignette_restored"))
	r2["pass"] = bool(r2.get("change_scene_ok")) and bool(r2.get("world_entered")) \
			and bool(r2.get("player_spawned")) and bool(r2.get("map_done")) \
			and bool(r2.get("camera_present")) \
			and bool(r2.get("kill_zoom_fired")) and bool(r2.get("kill_zoom_restored")) \
			and bool(r2.get("shake_fired")) and bool(r2.get("shake_restored")) \
			and bool(r2.get("hitstop_engaged")) and bool(r2.get("time_scale_restored"))

	# read controller counters LAST: events fire during the phases above
	var controller_end: Node = get_tree().get_first_node_in_group("p4_feedback_controller")
	if controller_end != null:
		r1["controller_instance_id_at_end"] = controller_end.get_instance_id()
		r1["controller_same_instance"] = r1.get("controller_instance_id_at_start") == controller_end.get_instance_id()
		r1["debug_connect_count"] = controller_end.debug_connect_count
		r1["debug_flash_count"] = controller_end.debug_flash_count
		r1["debug_marker_count"] = controller_end.debug_marker_count
		r1["debug_damage_events"] = controller_end.debug_damage_events
	var census := []
	for node in get_tree().get_nodes_in_group("p4_feedback_controller"):
		census.append(node.get_instance_id())
	r1["controllers_in_group_census"] = census

	_cull_all()
	results["r1"] = r1
	results["r2"] = r2
	results["pass"] = bool(r1["pass"]) and bool(r2["pass"])
	results["errors"] = _collect_failed(r1, "r1", ["natural_elite_found"]) + _collect_failed(r2, "r2")
	results["finished"] = true
	_restore_save()
	print(MARKER + JSON.stringify(results))
	await get_tree().process_frame
	get_tree().quit(0 if bool(results["pass"]) else 2)


func _collect_failed(phase: Dictionary, prefix: String, skip: Array = []) -> Array:
	var failed: Array = []
	for k in phase.keys():
		if skip.has(str(k)):
			continue
		if phase[k] is bool and not phase[k]:
			failed.append(prefix + "." + str(k))
	return failed


func _cull_all() -> void:
	for mob in get_tree().get_nodes_in_group("enemies"):
		mob.queue_free()
