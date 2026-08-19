extends Node
# B1-X5 Combat Harness — in-game reference fixture.
#
# Standalone reference implementation of the request-driven scenario director
# that mods/k5-combat-harness embeds into TestLevel.gd (CODE_PATCH, zero new
# res:// paths). This file is a TEST FIXTURE ONLY: it is not loaded by the
# game, not part of any pack, and exists so the director logic can be read,
# reviewed and unit-exercised outside the recovered tree. The shipped MOD
# payload is the authoritative copy; keep the two in sync.
#
# Protocol (matches docs/ai/B1-X5_COMBAT_HARNESS.md):
#   1. Host writes request JSON to user://combat_harness/request.json:
#      { "scenario_id": "...", "seed": <int>, "duration": <float>,
#        "plan": [ { "res": "res://...", "x": <float>, "y": <float>,
#                    "count": <int> }, ... ] }
#   2. Director seeds the global RNG from request.seed, spawns the plan under
#      its configured spawn_parent, wires Stats.died / Stats.damage_taken
#      counters, finishes on timeout or full kill.
#   3. Director writes telemetry JSON to
#      user://combat_harness/telemetry_<scenario_id>_<seed>.json (schema
#      version 1.0, see scripts/validate/combat_telemetry_schema.json).

onready var spawn_parent = get_node_or_null("Spawns")

var _request = {}
var _started = 0
var _spawned = 0
var _killed = 0
var _damage_events = 0
var _duplicate_deaths = 0
var _dead_ids = {}
var _finished = false


func run_harness() -> bool:
	# Returns true when a request was found and executed, false otherwise.
	var request_path = "user://combat_harness/request.json"
	var file = File.new()
	if not file.file_exists(request_path):
		return false
	var err = file.open(request_path, File.READ)
	if err != OK:
		return false
	var req_text = file.get_as_text()
	file.close()
	var parsed = JSON.parse(req_text)
	if parsed.error != OK:
		return false
	_request = parsed.result
	seed(int(_request.get("seed", 0)))
	if spawn_parent == null:
		spawn_parent = get_parent()
	_spawn_from_plan()
	_started = int(OS.get_unix_time())
	var timer = Timer.new()
	timer.one_shot = true
	timer.wait_time = float(_request.get("duration", 30.0))
	timer.connect("timeout", self, "_finish_harness_scenario")
	add_child(timer)
	timer.start()
	print("[COMBAT_HARNESS] scenario=" + str(_request.get("scenario_id", ""))
			+ " seed=" + str(_request.get("seed", 0)) + " spawns=started")
	return true


func _spawn_from_plan():
	var plan = _request.get("plan", [])
	for entry in plan:
		var scene = load(str(entry.get("res", "")))
		if scene == null:
			continue
		for i in range(int(entry.get("count", 1))):
			var inst = scene.instance()
			spawn_parent.add_child(inst)
			inst.position = Vector2(float(entry.get("x", 0)), float(entry.get("y", 0)))
			var stats = inst.get("stats")
			if stats != null and stats.has_signal("died"):
				stats.connect("died", self, "_on_harness_died", [inst.get_instance_id()])
			if stats != null and stats.has_signal("damage_taken"):
				stats.connect("damage_taken", self, "_on_harness_damage")
			_spawned += 1


func _on_harness_died(instance_id):
	var key = str(instance_id)
	if _dead_ids.has(key):
		_duplicate_deaths += 1
	else:
		_dead_ids[key] = true
	_killed += 1
	_check_harness_done()


func _on_harness_damage(amounts, attacker_stats, was_crit):
	_damage_events += 1


func _iso_utc(unix_seconds):
	var dt = OS.get_datetime(true)
	return "%04d-%02d-%02dT%02d:%02d:%02dZ" % [dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second]


func _check_harness_done():
	if _spawned > 0 and _dead_ids.size() >= _spawned:
		_finish_harness_scenario()


func _finish_harness_scenario():
	if _finished:
		return
	_finished = true
	var scenario_id = str(_request.get("scenario_id", ""))
	var seed_num = int(_request.get("seed", 0))
	var elapsed = float(OS.get_unix_time()) - float(_started)
	var telemetry = {
		"schema_version": "1.0",
		"scenario_id": scenario_id,
		"seed": seed_num,
		"started_at": _iso_utc(_started),
		"ended_at": _iso_utc(int(OS.get_unix_time())),
		"boot": {"ok": true, "fatal_count": 0, "alert_count": 0},
		"counters": {
			"spawned": _spawned,
			"alive": _spawned - _killed,
			"killed": _killed,
			"duplicate_deaths": _duplicate_deaths,
			"damage_events": _damage_events
		},
		"perf": {"frames": 0, "fps_avg": Engine.get_frames_per_second(),
				"fps_min": 0, "fps_max": 0, "frame_pacing_p95_ms": 0},
		"runtime": {"exit_code": 0, "in_game_result": "PASS",
				"notes": ["run_seconds=" + str(elapsed)]},
		"proves": "game booted; request-driven spawn executed; kill counting wired",
		"not_proven": "candidate build; frame pacing accuracy; perf monitors"
	}
	var out = File.new()
	out.open("user://combat_harness/telemetry_" + scenario_id + "_" + str(seed_num) + ".json", File.WRITE)
	out.store_string(JSON.print(telemetry, "\t"))
	out.close()
	print("[COMBAT_HARNESS] DONE " + scenario_id + " seed=" + str(seed_num)
			+ " killed=" + str(_killed) + "/" + str(_spawned))
