extends Node2D
# P4-B F2 performance-baseline probe driver, headless.
#
# Spawns --count real Mob.tscn instances (mixed types, ~10% elites) around a
# player-group stub, lets them chase/attack-cycle, then samples per-process-
# frame wall times and reports ms percentiles (p50/p95/p99/max) plus FPS.
# First measurement establishes a BASELINE on this machine; it is explicitly
# NOT a PASS/FAIL performance gate.
#
# Headless notes: the process loop runs uncapped, so per-frame deltas measure
# real CPU frame cost (simulation + physics-step frames included); there is
# no GPU rendering in this mode.  Repeatable: seeded RNG, parameterized via
#   godot ... res://scenes/Mobs/_validate/p4_b_perf_probe.tscn -- --count=100 --frames=600
#
# Machine-readable result line:  P3_PROBE_RESULT:{...}
# Exit codes: 0 = PASS (baseline captured), 2 = FAIL (sanity checks failed).

const PROBE_ID := "p4_b_perf_probe"
const MOB_SCENE_PATH := "res://scenes/Mobs/Mob.tscn"
const WARMUP_FRAMES := 60

# Runtime-evaluated (autoload enum access is not a constant expression).
var _mob_types := [
	MonsterTypes.MonsterType.TRAINING_DUMMY,
	MonsterTypes.MonsterType.SKELETON_ARCHER,
	MonsterTypes.MonsterType.ZOMBIE,
]

var _engine_version := ""

var _result := {}


class ProbeStatsStub extends RefCounted:
	func add_kills(_amount, _elite = false, _boss = false) -> void:
		pass

	func add_xp(_amount) -> void:
		pass

	func apply_damage(_bundle, _color = Color.WHITE, _attacker_stats = null,
			_show_damage = false, _is_dot = false, _skill_parent = null,
			_can_block = true) -> Dictionary:
		return {"did_kill": false, "damage": 0}


class ProbePlayerStub extends Node2D:
	var stats = ProbeStatsStub.new()

	func _init() -> void:
		add_to_group("player")


func _read_args() -> Dictionary:
	var args := {"count": 50, "frames": 600}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--count="):
			args.count = max(1, int(arg.get_slice("=", 1)))
		elif arg.begins_with("--frames="):
			args.frames = max(60, int(arg.get_slice("=", 1)))
	return args


func _seed_character(name: String) -> void:
	GameState.saved_stats.characters[name] = {
		"character_name": name,
		"account_level": 1,
		"account_xp": 0,
		"account_xp_next": 50,
		"next_gene_id": 0,
		"needs_starter": false,
		"orbs": {"blue": 0, "green": 0, "red": 0, "gold": 0, "freeze": 0,
				"corruption": 0, "tear": 0, "moon_shard": 0, "sun_shard": 0},
		"recent_stage": null,
		"completed_stages": {},
		"outfit": {"helmet": null, "head": null, "feet": null, "hands": null,
				"pants": null, "back": null},
		"help_tips": {},
		"new_item_ids": {},
		"new_item_types": {},
		"tutorial_events": {},
		"mutation_tree_loadout": {"class": "WARRIOR", "passives": ["root_warrior"]},
		"specialization_loadout": {"class": null, "passives": ["root"]},
		"skill_loadout": {},
		"gene_loadout": {},
		"genes": {},
		"stored_mods": {},
		"filters": {},
	}


func _percentile(sorted_samples: Array, q: float) -> float:
	if sorted_samples.is_empty():
		return 0.0
	var index: int = clampi(int(round(q * (sorted_samples.size() - 1))), 0, sorted_samples.size() - 1)
	return sorted_samples[index]


func _ready() -> void :
	process_mode = Node.PROCESS_MODE_ALWAYS
	var vi := Engine.get_version_info()
	_engine_version = "%d.%d.%d-%s" % [
			vi.get("major", 0), vi.get("minor", 0),
			vi.get("patch", 0), vi.get("status", "")]
	await _run()
	_report()


func _run() -> void :
	var args := _read_args()
	_result = {
		"probe_id": PROBE_ID,
		"requested_count": args.count,
		"sample_frames": args.frames,
		"warmup_frames": WARMUP_FRAMES,
		"spawned": 0,
		"samples_taken": 0,
		"frame_ms": {},
		"fps": {},
		"env": {
			"mode": "headless",
			"engine_version": _engine_version,
			"os_name": OS.get_name(),
			"processor_name": OS.get_processor_name(),
			"processor_count": OS.get_processor_count(),
		},
		"errors": [],
	}

	seed(20260822)
	Globals.zone_level = 1
	GameState.saved_stats.settings.enable_fx = true

	var level_layer := Node2D.new()
	level_layer.name = "ProbeLevelLayer"
	var ground := Node2D.new()
	ground.name = "ProbeGround"
	add_child(level_layer)
	add_child(ground)
	GameState.set_global("level_layer", level_layer)
	GameState.set_global("ground", ground)

	var player := ProbePlayerStub.new()
	player.position = Vector2.ZERO
	add_child(player)
	GameState.set_global("player", player)

	_seed_character("probe")
	Globals.selected_character_name = "probe"
	GameState.mark_tutorial_event_done("first_gene")

	
	Levels.config["p4b_perf"] = {"map_type": Levels.MAP_TYPE.LADDER}
	Globals.selected_level = "p4b_perf"

	var mob_scene = load(MOB_SCENE_PATH)
	if mob_scene == null:
		_result.errors.append("failed to load %s" % MOB_SCENE_PATH)
		return

	for i in range(args.count):
		var mob = mob_scene.instantiate()
		mob.type = _mob_types[i % _mob_types.size()]
		mob.is_elite = i % 10 == 0
		var angle := TAU * float(i) / float(args.count)
		var radius := 120.0 + 28.0 * float(i % 6)
		mob.position = Vector2(cos(angle), sin(angle)) * radius
		level_layer.add_child(mob)

	
	for i in range(10):
		await get_tree().process_frame
	_result.spawned = get_tree().get_nodes_in_group("enemies").size()

	
	for i in range(WARMUP_FRAMES):
		await get_tree().process_frame

	
	var samples := PackedFloat64Array()
	samples.resize(args.frames)
	var previous := Time.get_ticks_usec()
	for i in range(args.frames):
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		samples[i] = float(now - previous) / 1000.0
		previous = now

	var sorted := Array(samples)
	sorted.sort()
	var total := 0.0
	for s in samples:
		total += s
	var mean := total / float(samples.size())

	_result.samples_taken = samples.size()
	_result.frame_ms = {
		"min": sorted[0],
		"p50": _percentile(sorted, 0.50),
		"p95": _percentile(sorted, 0.95),
		"p99": _percentile(sorted, 0.99),
		"max": sorted[sorted.size() - 1],
		"mean": mean,
	}
	_result.fps = {
		"avg_from_mean_ms": 1000.0 / mean if mean > 0.0 else 0.0,
		"engine_reported": Engine.get_frames_per_second(),
	}


func _report() -> void :
	var sane: bool = _result.spawned == _result.requested_count \
			and _result.samples_taken == _result.sample_frames \
			and _result.frame_ms.get("mean", 0.0) > 0.0
	if not sane:
		if _result.errors.is_empty():
			_result.errors.append("sanity check failed: spawned=%s samples=%s"
					% [_result.spawned, _result.samples_taken])
	_result["baseline_captured"] = sane
	_result["pass"] = sane
	print("P3_PROBE_RESULT:" + JSON.stringify(_result))
	get_tree().quit(0 if _result.pass else 2)
