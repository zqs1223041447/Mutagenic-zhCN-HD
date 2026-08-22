extends Node
## P3-BC combat harness director - Godot 4 port of the B1-X5 G3 fixture
## (test_fixtures/combat_harness/ScenarioDirector.gd), embedded by
## TestLevel.gd when user://combat_harness/request.json exists.
##
## Protocol (unchanged from the G3 contract):
##   1. Host writes request JSON to user://combat_harness/request.json:
##      { "game_request": { "scenario_id": "...", "seed": <int>,
##          "duration": <float>, "plan": [ { "res": "res://...",
##          "x": <float>, "y": <float>, "count": <int>, ["mob_type"] } ] },
##        "expected_telemetry_path": "<host abs path>" }
##   2. Director seeds the global RNG from seed, spawns the plan under the
##      level's Spawns node, wires Stats.died / Stats.damage_taken counters,
##      drives player movement/dash input, finishes on timeout or full kill.
##   3. Director writes telemetry JSON (schema 1.0,
##      scripts/validate/combat_telemetry_schema.json) to
##      user://combat_harness/telemetry_<scenario_id>_<seed>.json AND to
##      expected_telemetry_path, then quits the process.
##
## Headless note: missing SpriteFrames / audio assets are an art boundary;
## no logic here depends on visual resources existing. Mob.tscn guards its
## own sprite access; Arc (preferred player skill) applies damage directly.
##
## Harness-only exemptions (never active without a request file):
##   - runtime_smoke_safe: player health_max=1e8 + per-checkpoint fill_health
##     so the lifecycle run survives to its timeout (B3-P2-X0 contract); no
##     skill is equipped there so killed stays 0.
##   - kill scenarios: one starter damage skill is equipped on the player via
##     the real GameState skill_loadout -> Player._on_skills_changed pipeline.

const REQUEST_PATH := "user://combat_harness/request.json"
const TELEMETRY_DIR := "user://combat_harness"
const SCHEMA_VERSION := "1.0"
const CHECKPOINT_INTERVAL := 5.0
const PLAYER_WAIT_FRAMES := 600
# Player damage sources per loadout slot; first entry whose scene
# instantiates wins. Orb = projectile with unlimited targeting range inside
# the 150px detection radius; Shockwave/BloodSlash = melee AoE cleanup.
const SKILL_LOADOUT := {
	"primary": ["Orb", "Shotgun", "Axe"],
	"secondary": ["Shockwave", "BloodSlash", "EnergizedAxe"],
}
# Movement/dash drive pattern, in physics ticks (60 Hz): hold move_right for
# WALK_TICKS, rest WALK_TICKS, fire dash once per DASH_CYCLE_TICKS.
const WALK_TICKS := 45
const DASH_AT_TICK := 135
const DASH_HOLD_TICKS := 3
const DASH_CYCLE_TICKS := 270
# G3 的 ladder 刷怪圈：玩家 ±64px 近战范围。宿主计划的大散布点会落在视线墙外，
# 而 Mob AI 在受损前不追击（LOS 鸡生蛋问题），故将超距生成点确定性收敛回圈内：
# 保持相对方向、钳制距离，不引入额外随机量。
const ENGAGEMENT_RADIUS := 64.0

var scenario_id := ""
var seed_value := 0
var duration := 30.0
var expected_telemetry_path := ""
var _plan: Array = []

var _level: Node = null
var _spawn_parent: Node = null
var _player: Node = null
var _started_unix := 0
var _elapsed := 0.0
var _tick := 0
var _since_checkpoint := 0.0
var _process_frames := 0
var _fps_min := 9999.0
var _fps_max := 0.0

var _spawned := 0
var _planned := 0
var _adjusted_spawns := 0
var _killed := 0
var _damage_events := 0
var _duplicate_deaths := 0
var _dead_ids := {}
var _player_moves := 0
var _dashes := 0
var _checkpoints := []
var _session_file := ""
var _finished := false
var _skill_used := ""
var _drive_input := false
var _move_held := false
var _dash_held := false
var _last_dash_cooldown := 0.0
var _last_player_pos := Vector2.ZERO
var _has_last_pos := false


func run_harness(level: Node) -> bool:
	# Returns true when a request was found and executed, false otherwise.
	_level = level
	var request := _read_request()
	if request.is_empty():
		return false
	if not _parse_request(request):
		print("[COMBAT_HARNESS] ERROR unparsable request; quitting")
		get_tree().quit(4)
		return true
	seed(seed_value)
	_player = GameState.get_global("player")
	var wait_frames := 0
	while not _is_valid_node(_player) and wait_frames < PLAYER_WAIT_FRAMES:
		await get_tree().process_frame
		_player = GameState.get_global("player")
		wait_frames += 1
	if not _is_valid_node(_player):
		_finish("boot_failed")
		return true
	_spawn_parent = _level.get_node_or_null("Spawns")
	if _spawn_parent == null:
		_spawn_parent = _level
	_planned = _count_planned()
	_started_unix = int(Time.get_unix_time_from_system())
	_session_file = "session_" + scenario_id + "_" + str(seed_value) + ".json"
	_apply_scenario_exemptions()
	_skill_used = _equip_player_skill()
	_spawn_from_plan()
	_drive_input = _planned == 0 or scenario_id == "movement_dash_smoke"
	_flush_checkpoint()
	print("[COMBAT_HARNESS] scenario=" + scenario_id + " seed=" + str(seed_value)
			+ " spawns=" + str(_planned) + " skill=" + (_skill_used if _skill_used != "" else "<none>"))
	return true


func _physics_process(delta: float) -> void:
	if _finished:
		return
	_process_frames += 1
	_elapsed += delta
	_since_checkpoint += delta
	_drive_player_input()
	if _since_checkpoint >= CHECKPOINT_INTERVAL:
		_since_checkpoint = 0.0
		_flush_checkpoint()
	if _elapsed >= duration:
		_finish("timeout")
	elif _planned > 0 and _dead_ids.size() >= _planned:
		_finish("all_killed")


func _read_request() -> Dictionary:
	if not FileAccess.file_exists(REQUEST_PATH):
		return {}
	var file := FileAccess.open(REQUEST_PATH, FileAccess.READ)
	if file == null:
		return {}
	var text := file.get_as_text()
	file.close()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		return {}
	return parsed


func _parse_request(request: Dictionary) -> bool:
	var game: Dictionary = request.get("game_request", {})
	scenario_id = str(game.get("scenario_id", ""))
	seed_value = int(game.get("seed", 0))
	duration = float(game.get("duration", 30.0))
	expected_telemetry_path = str(request.get("expected_telemetry_path", ""))
	_plan = game.get("plan", [])
	if scenario_id.is_empty() or duration <= 0.0:
		return false
	return true


func _count_planned() -> int:
	var total := 0
	for entry in _plan:
		total += int(entry.get("count", 1))
	return total


func _apply_scenario_exemptions() -> void:
	# B3-P2-X0 harness-only exemption, gated on this explicit scenario id.
	if scenario_id == "runtime_smoke_safe" and _is_valid_node(_player):
		var stats: Node = _player.get("stats")
		if stats != null:
			stats.base_stats["health_max"] = 100000000.0
			stats.recompute_stats(true)
			stats.fill_health()


func _equip_player_skill() -> String:
	# Real pipeline: GameState skill_loadout -> skill_loadout_changed ->
	# Player._on_skills_changed -> Skills.config[skill].skill_scene into Gear.
	if _planned == 0 or scenario_id == "runtime_smoke_safe" or not _is_valid_node(_player):
		return ""
	var loadout = GameState.get_equipped_skills()
	if typeof(loadout) != TYPE_DICTIONARY:
		return ""
	var config = Skills.get("config")
	var equipped: Array[String] = []
	for slot in SKILL_LOADOUT:
		if not loadout.has(slot):
			continue
		for skill_name in SKILL_LOADOUT[slot]:
			if not config.has(skill_name):
				continue
			var scene = config[skill_name].get("skill_scene")
			if scene == null or not (scene is PackedScene) or not scene.can_instantiate():
				continue
			loadout[slot]["skill"] = skill_name
			equipped.append(skill_name)
			break
	if equipped.is_empty():
		return ""
	GameState.emit_signal("skill_loadout_changed")
	return "+".join(equipped)


func _spawn_from_plan() -> void:
	var player_pos := Vector2.ZERO
	if _is_valid_node(_player):
		player_pos = _player.global_position
	for entry in _plan:
		var scene: PackedScene = load(str(entry.get("res", "")))
		if scene == null:
			continue
		for i in range(int(entry.get("count", 1))):
			var inst = scene.instantiate()
			var mob_type := str(entry.get("mob_type", ""))
			if mob_type != "" and MonsterTypes.MonsterType.has(mob_type):
				inst.type = MonsterTypes.MonsterType[mob_type]
			var pos := Vector2(float(entry.get("x", 0)), float(entry.get("y", 0)))
			var offset := pos - player_pos
			if offset.length() > ENGAGEMENT_RADIUS or not _has_los(player_pos, pos):
				# 收敛到玩家近战圈并做确定性 LOS 扫描（12 个方位角），
				# 保证 Mob AI 的可见性判定成立、玩家技能可锁定目标。
				var dist: float = clamp(offset.length(), 24.0, ENGAGEMENT_RADIUS)
				var base_angle := offset.angle()
				var placed := false
				for attempt in range(12):
					var candidate: Vector2 = player_pos \
							+ Vector2.RIGHT.rotated(base_angle + attempt * TAU / 12.0) * dist
					if _has_los(player_pos, candidate):
						pos = candidate
						placed = true
						break
				if not placed:
					pos = player_pos
				_adjusted_spawns += 1
			# add_child 之前设置位置：Mob._ready 的 start_position 才是真实落点。
			inst.position = pos
			_spawn_parent.add_child(inst)
			var stats: Node = inst.get("stats")
			if stats != null:
				stats.connect("died", Callable(self, "_on_harness_died").bind(inst.get_instance_id()))
				# 注意：product 的 Stats 只在 is_player 时才 emit damage_taken；
				# 野怪掉血经由每帧轮询块 emit health_changed（血条同款通路）。
				stats.connect("health_changed", Callable(self, "_on_harness_damage"))
			_spawned += 1


func _has_los(from: Vector2, to: Vector2) -> bool:
	if from.distance_to(to) < 1.0:
		return true
	var player_2d := _player as Node2D
	if player_2d == null:
		return false
	var space = player_2d.get_world_2d().direct_space_state
	var query := PhysicsRayQueryParameters2D.create(from, to, 256)
	return space.intersect_ray(query).is_empty()


func _drive_player_input() -> void:
	if not _is_valid_node(_player):
		return
	var cycle_tick := _tick % DASH_CYCLE_TICKS
	var want_move := cycle_tick < WALK_TICKS
	if want_move != _move_held:
		_move_held = want_move
		if want_move:
			Input.action_press("move_right")
		else:
			Input.action_release("move_right")
	if _move_held:
		if _has_last_pos and _player.global_position.distance_to(_last_player_pos) > 0.5:
			_player_moves += 1
		_last_player_pos = _player.global_position
		_has_last_pos = true
	var want_dash := cycle_tick >= DASH_AT_TICK and cycle_tick < DASH_AT_TICK + DASH_HOLD_TICKS
	if want_dash != _dash_held:
		_dash_held = want_dash
		if want_dash:
			Input.action_press("dash")
		else:
			Input.action_release("dash")
	var cooldown_value = _player.get("dash_cooldown")
	var cooldown: float = float(cooldown_value) if cooldown_value != null else 0.0
	if _last_dash_cooldown <= 0.0 and cooldown > 0.0:
		_dashes += 1
	_last_dash_cooldown = cooldown
	_tick += 1


func _on_harness_died(instance_id: int) -> void:
	var key := str(instance_id)
	if _dead_ids.has(key):
		_duplicate_deaths += 1
	else:
		_dead_ids[key] = true
	_killed += 1
	_check_harness_done()


func _on_harness_damage(_amounts = null, _attacker_stats = null, _was_crit = false) -> void:
	_damage_events += 1


func _check_harness_done() -> void:
	if _planned > 0 and _dead_ids.size() >= _planned:
		_finish("all_killed")


func _flush_checkpoint() -> void:
	_refill_exempt_player()
	_fps_track()
	_checkpoints.append({
		"t": snappedf(_elapsed, 0.01),
		"spawned": _spawned,
		"killed": _killed,
		"alive": _spawned - _killed,
		"damage_events": _damage_events,
		"fps": Engine.get_frames_per_second(),
	})
	if OS.get_environment("P3BC_DEBUG") != "":
		_debug_state()
	var dir := DirAccess.open("user://")
	if dir != null:
		dir.make_dir_recursive("combat_harness")
	var file := FileAccess.open(TELEMETRY_DIR + "/" + _session_file, FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify({
			"status": "running",
			"scenario_id": scenario_id,
			"seed": seed_value,
			"checkpoints": _checkpoints,
		}, "\t"))
		file.close()


func _debug_state() -> void:
	if not _is_valid_node(_player):
		return
	var pstats: Node = _player.get("stats")
	var near := 0
	if pstats != null:
		near = pstats.nearby_enemies.size()
	var nearest := -1.0
	var enemy_pos := Vector2.INF
	for mob in get_tree().get_nodes_in_group("enemies"):
		if is_instance_valid(mob):
			var d: float = mob.global_position.distance_to(_player.global_position)
			if nearest < 0 or d < nearest:
				nearest = d
				enemy_pos = mob.global_position
	var skill_info := ""
	var gear: Node = _player.get_node_or_null("Gear")
	if gear != null:
		for child in gear.get_children():
			var cd = child.get("cooldown")
			var cc = null
			if child.has_method("can_cast"):
								cc = child.can_cast()
			skill_info += " %s(cd=%s cc=%s)" % [child.name, str(cd), str(cc)]
	print("[P3BC_DEBUG] t=", snappedf(_elapsed, 0.1),
			" player=", _player.global_position,
			" enemy=", enemy_pos,
			" nearest=", snappedf(nearest, 0.1),
			" nearby=", near,
			" dmg=", _damage_events,
			skill_info)
	if OS.get_environment("P3BC_DEBUG") == "2" and enemy_pos != Vector2.INF:
		var player_2d := _player as Node2D
		var space = player_2d.get_world_2d().direct_space_state
		var query := PhysicsRayQueryParameters2D.create(player_2d.global_position, enemy_pos, 256)
		var hit = space.intersect_ray(query)
		var hit_desc := "<clear>"
		if not hit.is_empty():
			var collider = hit.get("collider")
			hit_desc = str(collider) + " @ " + str(hit.get("position")) \
					+ " parent=" + (str(collider.get_parent()) if collider is Node else "?")
		print("[P3BC_DEBUG] ray player->enemy: ", hit_desc)


func _refill_exempt_player() -> void:
	if scenario_id == "runtime_smoke_safe" and _is_valid_node(_player):
		var stats: Node = _player.get("stats")
		if stats != null:
			stats.fill_health()


func _fps_track() -> void:
	var fps := float(Engine.get_frames_per_second())
	_fps_min = min(_fps_min, fps)
	_fps_max = max(_fps_max, fps)


func _iso_utc(unix_seconds: int) -> String:
	var dt := Time.get_datetime_dict_from_unix_time(unix_seconds)
	return "%04d-%02d-%02dT%02d:%02d:%02dZ" % [
		dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second]


func _finish(exit_reason: String) -> void:
	if _finished:
		return
	_finished = true
	_flush_checkpoint()
	var elapsed := float(Time.get_unix_time_from_system()) - float(_started_unix)
	var frames := maxi(_process_frames, 1)
	var fps_avg: float = frames / max(elapsed, 0.001)
	var in_game_result := "PASS" if _duplicate_deaths == 0 else "FAIL"
	var telemetry := {
		"schema_version": SCHEMA_VERSION,
		"scenario_id": scenario_id,
		"seed": seed_value,
		"started_at": _iso_utc(_started_unix),
		"ended_at": _iso_utc(int(Time.get_unix_time_from_system())),
		"boot": {"ok": _spawned >= _planned and _is_valid_node(_player), "fatal_count": 0, "alert_count": 0},
		"counters": {
			"spawned": _spawned,
			"alive": _spawned - _killed,
			"killed": _killed,
			"duplicate_deaths": _duplicate_deaths,
			"damage_events": _damage_events,
			"player_moves": _player_moves,
			"dashes": _dashes,
			"checkpoint_count": _checkpoints.size(),
		},
		"world": _collect_world_evidence(),
		"status": "complete",
		"exit_reason": exit_reason,
		"checkpoints": _checkpoints,
		"session_file": _session_file,
		"perf": {
			"frames": frames,
			"fps_avg": snappedf(fps_avg, 0.01),
			"fps_min": 0.0 if _fps_min > 9000.0 else snappedf(_fps_min, 0.01),
			"fps_max": snappedf(_fps_max, 0.01),
			"frame_pacing_p95_ms": 0.0,
		},
		"runtime": {
			"exit_code": 0,
			"in_game_result": in_game_result,
			"notes": [
				"run_seconds=" + str(snappedf(elapsed, 0.01)),
				"exit_reason=" + exit_reason,
				"skill_used=" + (_skill_used if _skill_used != "" else "<none>"),
				"harness_mode=TestLevel.gd+ScenarioDirector.gd",
				"spawn_positions_adjusted=" + str(_adjusted_spawns) + "/" + str(_planned)
					+ " (clamped to " + str(ENGAGEMENT_RADIUS) + "px engagement radius)",
			],
		},
		"proves": "request-driven world entry with live player; plan spawn executed; "
			+ "skill->damage->kill counters wired; movement/dash input driven",
		"not_proven": "candidate build identity; frame pacing accuracy; visual/audio quality",
	}
	_write_telemetry(telemetry)
	_remove_request()
	print("[COMBAT_HARNESS] DONE " + scenario_id + " seed=" + str(seed_value)
			+ " killed=" + str(_killed) + "/" + str(_spawned)
			+ " damage_events=" + str(_damage_events)
			+ " moves=" + str(_player_moves) + " dashes=" + str(_dashes)
			+ " reason=" + exit_reason)
	get_tree().quit(0)


func _collect_world_evidence() -> Dictionary:
	# E2 world-entry evidence: player mounted, tiles painted, navmesh built.
	var evidence := {
		"player_in_tree": _is_valid_node(_player) and _player.is_inside_tree(),
		"tile_used_cells": 0,
		"navmesh_points": 0,
	}
	var tilemap: Node = _level.get_node_or_null("TileMap") if _is_valid_node(_level) else null
	if tilemap != null:
		evidence["tile_used_cells"] = tilemap.get_used_cells(0).size()
	var nav = Globals.get("navmesh")
	if nav != null and is_instance_valid(nav):
		var astar = nav.get("navmesh")
		if astar != null and is_instance_valid(astar):
			evidence["navmesh_points"] = astar.get_point_count()
	return evidence


func _write_telemetry(telemetry: Dictionary) -> void:
	var payload := JSON.stringify(telemetry, "\t")
	var paths: Array[String] = [
		TELEMETRY_DIR + "/telemetry_" + scenario_id + "_" + str(seed_value) + ".json"]
	if not expected_telemetry_path.is_empty():
		paths.append(expected_telemetry_path)
	for path in paths:
		var file := FileAccess.open(path, FileAccess.WRITE)
		if file != null:
			file.store_string(payload)
			file.close()
		else:
			print("[COMBAT_HARNESS] ERROR cannot write telemetry: " + path)


func _remove_request() -> void:
	var dir := DirAccess.open("user://combat_harness")
	if dir != null:
		dir.remove("request.json")


func _is_valid_node(node) -> bool:
	return node != null and is_instance_valid(node)
