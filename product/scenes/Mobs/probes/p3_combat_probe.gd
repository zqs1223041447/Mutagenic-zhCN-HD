extends Node
# P3-C combat probe driver (Exit Criteria E4/E5), headless.
#
# E4: instantiate >=1 real skill node and >=1 real mob; a skill damage bundle
#     produced by the skill reduces the mob's HP.
# E5: driving that bundle through Stats.apply_damage until zero triggers the
#     died signal, Mob._on_death, and removal of the mob from the tree.
#
# No game source is modified at runtime beyond test-scoped autoload state
# (globals/containers seeded the way BaseLevel would seed them).  The ladder
# map stub makes Mob._on_death skip its drop table so the kill path is
# deterministic without the (still missing) product/scenes/Pickups scenes.
#
# Machine-readable result line:  P3_PROBE_RESULT:{...}
# Exit codes: 0 = PASS, 2 = FAIL.

const PROBE_ID := "p3_combat_probe"
const MAX_HIT_ATTEMPTS := 50

var _result := {}


class ProbeStatsStub extends RefCounted:
	# Mob._on_death credits kills/xp on target.stats; melee exchanges would
	# call apply_damage.  The stub keeps those calls harmless.
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
		position = Vector2(1000000, 1000000)  # out of every attack range


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	await _run()
	_report()


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


func _run() -> void:
	_result = {
		"probe_id": PROBE_ID,
		"skill_instantiated": false,
		"skill_is_generic_skill": false,
		"mob_instantiated": false,
		"victim_type": "",
		"hp_before": null,
		"hp_after_first_hit": null,
		"first_hit_damage": 0.0,
		"hit_attempts": 0,
		"did_kill": false,
		"died_signal_received": false,
		"removed_from_tree": false,
		"script_errors_during_probe": 0,
		"errors": [],
	}
	seed(20260822)
	Globals.zone_level = 1

	var level_layer := Node2D.new()
	level_layer.name = "ProbeLevelLayer"
	var ground := Node2D.new()
	ground.name = "ProbeGround"
	add_child(level_layer)
	add_child(ground)
	GameState.set_global("level_layer", level_layer)
	GameState.set_global("ground", ground)

	var player := ProbePlayerStub.new()
	add_child(player)
	GameState.set_global("player", player)

	_seed_character("probe")
	Globals.selected_character_name = "probe"
	GameState.mark_tutorial_event_done("first_gene")

	# Ladder stub => Mob._on_death skips the drop table (Pickups scenes are
	# still absent from product/) => deterministic kill path.
	Levels.config["p3_probe"] = {"map_type": Levels.MAP_TYPE.LADDER}
	Globals.selected_level = "p3_probe"

	var mob_scene = load("res://scenes/Mobs/Mob.tscn")
	if mob_scene == null:
		_result.errors.append("failed to load res://scenes/Mobs/Mob.tscn")
		return

	var attacker = mob_scene.instantiate()
	attacker.type = MonsterTypes.MonsterType.TRAINING_DUMMY
	attacker.position = Vector2(-200, 0)
	add_child(attacker)

	var victim = mob_scene.instantiate()
	victim.type = MonsterTypes.MonsterType.SKELETON_ARCHER
	victim.position = Vector2(200, 0)
	add_child(victim)
	_result.mob_instantiated = victim.is_inside_tree()
	_result.victim_type = str(victim.type)

	await get_tree().process_frame
	await get_tree().process_frame

	var skill = attacker.get_node_or_null("Gear/BasicAttack")
	_result.skill_instantiated = skill != null
	if skill == null:
		_result.errors.append("attacker Gear/BasicAttack skill node missing")
		return
	_result.skill_is_generic_skill = skill is GenericSkill

	var stats = victim.get_node_or_null("Stats")
	if stats == null:
		_result.errors.append("victim Stats node missing")
		return

	stats.connect("died", Callable(self, "_on_victim_died"))

	var hp_before: float = stats.health
	_result.hp_before = hp_before
	if hp_before <= 0.0:
		_result.errors.append("victim spawned with non-positive hp: %s" % hp_before)
		return

	var bundle: Dictionary = skill.get_damage_bundle(false, false)
	if not bundle.has("damage") or bundle.damage.is_empty():
		_result.errors.append("skill produced an empty damage bundle")
		return

	var did_kill := false
	for attempt in range(1, MAX_HIT_ATTEMPTS + 1):
		_result.hit_attempts = attempt
		var res: Dictionary = stats.apply_damage(bundle, Color.WHITE, attacker.stats, false)
		if res.damage > 0.0 and _result.first_hit_damage == 0.0:
			_result.first_hit_damage = res.damage
			_result.hp_after_first_hit = stats.health
		did_kill = res.did_kill
		if did_kill:
			break

	_result.did_kill = did_kill

	# died is emitted deferred; give the tree a few frames to run
	# Mob._on_death (drop-skip ladder path, death animation, queue_free).
	for i in range(6):
		await get_tree().process_frame

	_result.removed_from_tree = not is_instance_valid(victim) or not victim.is_inside_tree()


func _on_victim_died() -> void:
	_result.died_signal_received = true


func _report() -> void:
	var e4_pass: bool = _result.skill_instantiated and _result.skill_is_generic_skill \
			and _result.mob_instantiated and _result.first_hit_damage > 0.0 \
			and _result.hp_after_first_hit != null \
			and _result.hp_after_first_hit < _result.hp_before
	var e5_pass: bool = _result.did_kill and _result.died_signal_received \
			and _result.removed_from_tree
	_result["e4_pass"] = e4_pass
	_result["e5_pass"] = e5_pass
	_result["pass"] = e4_pass and e5_pass and _result.errors.is_empty()
	print("P3_PROBE_RESULT:" + JSON.stringify(_result))
	get_tree().quit(0 if _result.pass else 2)
