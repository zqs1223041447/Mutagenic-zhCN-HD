extends Node2D
# P4-B C1 real loot chain probe driver, headless.
#
# Replaces the P3-D drop STUB with the restored real scenes and re-verifies
# the E6 loot loop end to end:
#   1. REAL OrbPickup.tscn (scenes/Pickups/Orb): touch -> vacuum chase ->
#      do_pickup -> Stats.add_orb credit -> orb_pickup signal -> queue_free.
#   2. REAL Mob elite drop branch: an is_elite mob killed through the real
#      Stats.apply_damage pipeline drops an OrbPickup via Mob._on_death into
#      the ground layer (non-ladder map config, so the drop table runs).
#   3. REAL PortalPickup.tscn (scenes/Pickups/Portal): persistent, pickup
#      opens the confirmation dialog, confirming queues the DeathScreen popup
#      through PopupManager.
#
# A minimal "World/FloatingDamageTexts" container is created under the root
# so production FloatingDamageManager code resolves its layer exactly like it
# does under the real World scene.
#
# Machine-readable result line:  P3_PROBE_RESULT:{...}
# Exit codes: 0 = PASS, 2 = FAIL.

const PROBE_ID := "p4_b_loot_real_probe"

const ORB_SCENE_PATH := "res://scenes/Pickups/Orb/OrbPickup.tscn"
const PORTAL_SCENE_PATH := "res://scenes/Pickups/Portal/PortalPickup.tscn"
const GENE_SCENE_PATH := "res://scenes/Pickups/Gene/GenePickup.tscn"
const MOB_SCENE_PATH := "res://scenes/Mobs/Mob.tscn"
const STATS_SCENE_PATH := "res://scenes/Stats.tscn"

const ORB_METRIC_KEYS := {
	Constants.OrbType.BLUE: "blue",
	Constants.OrbType.RED: "red",
	Constants.OrbType.GREEN: "green",
	Constants.OrbType.GOLD: "gold",
	Constants.OrbType.CORRUPTION: "corruption",
}

var _result := {}


class ProbeStatsStub extends RefCounted:
	func add_kills(_amount, _elite = false, _boss = false) -> void:
		pass

	func add_xp(_amount) -> void:
		pass


class ProbePlayerEntity extends Node2D:
	var stats = null
	var gear = null

	func _init() -> void:
		add_to_group("player")


func _ready() -> void :
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


func _make_world_stub() -> void:
	
	var world := Node2D.new()
	world.name = "World"
	var texts := Node2D.new()
	texts.name = "FloatingDamageTexts"
	world.add_child(texts)
	get_tree().root.add_child.call_deferred(world)


func _make_player_entity() -> ProbePlayerEntity:
	var entity := ProbePlayerEntity.new()
	entity.name = "ProbePlayer"

	var gear := Node2D.new()
	gear.name = "Gear"
	entity.add_child(gear)
	entity.gear = gear

	var stats_scene = load(STATS_SCENE_PATH)
	var stats = stats_scene.instantiate()
	stats.name = "Stats"
	entity.stats = stats
	entity.add_child(stats)

	var area := Area2D.new()
	area.monitorable = true
	area.monitoring = true
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 24.0
	shape.shape = circle
	area.add_child(shape)
	entity.add_child(area)
	return entity


func _run() -> void :
	_result = {
		"probe_id": PROBE_ID,
		"orb_drop": {},
		"elite_drop_chain": {},
		"portal": {},
		"errors": [],
	}
	seed(20260822)
	Globals.zone_level = 1

	_make_world_stub()
	_seed_character("probe")
	Globals.selected_character_name = "probe"
	GameState.mark_tutorial_event_done("first_gene")

	
	Levels.config["p4b_loot"] = {"map_type": Levels.MAP_TYPE.MAP}
	Globals.selected_level = "p4b_loot"

	var level_layer := Node2D.new()
	level_layer.name = "ProbeLevelLayer"
	var ground := Node2D.new()
	ground.name = "ProbeGround"
	add_child(level_layer)
	add_child(ground)
	GameState.set_global("level_layer", level_layer)
	GameState.set_global("ground", ground)

	await _check_real_orb_pickup()
	await _check_elite_drop_chain()
	await _check_portal_pickup()


# --- 1: real OrbPickup touch -> vacuum -> inventory credit -------------------

func _check_real_orb_pickup() -> void :
	var section: Dictionary = _result.orb_drop
	var orb_scene = load(ORB_SCENE_PATH)
	if orb_scene == null:
		_result.errors.append("failed to load %s" % ORB_SCENE_PATH)
		section.pass = false
		return

	var player := _make_player_entity()
	add_child(player)
	GameState.set_global("player", player)
	var stats = player.stats

	var credited := {"seen": false, "type": null, "amount": 0}
	stats.connect("orb_pickup", Callable(self, "_on_probe_orb_pickup").bind(credited))

	var orbs_before: Dictionary = {
		"blue": stats.metrics.orbs.blue,
		"red": stats.metrics.orbs.red,
		"green": stats.metrics.orbs.green,
		"gold": stats.metrics.orbs.gold,
		"corruption": stats.metrics.orbs.corruption,
	}

	var drop = orb_scene.instantiate()
	drop.zone_level = 1
	drop.quantity_multiplier = 1.0
	add_child(drop)
	drop.global_position = Vector2(240, 0)
	player.global_position = Vector2(100, 0)

	
	await get_tree().process_frame
	section.drop_spawned = is_instance_valid(drop) and drop.is_inside_tree()
	section.does_vaccuum = drop.does_vaccuum
	section.rolled_orb_type = drop.orb_type
	section.rolled_amount = drop.amount
	section.button_text = drop.button.text

	
	
	player.global_position = Vector2(160, 0)

	var vacuum_seen: bool = is_instance_valid(drop) and drop.is_vaccuuming
	var collected: bool = is_instance_valid(drop) and drop.picked_up
	for i in range(360):
		await get_tree().physics_frame
		if is_instance_valid(drop):
			vacuum_seen = vacuum_seen or drop.is_vaccuuming
			collected = collected or drop.picked_up
		if not is_instance_valid(drop) or drop.is_queued_for_deletion():
			break

	await get_tree().process_frame
	section.vacuum_engaged = vacuum_seen
	section.collected = collected
	section.removed_from_tree = not is_instance_valid(drop) \
			or drop.is_queued_for_deletion()
	section.orb_pickup_signal_seen = credited.seen

	var key: String = ORB_METRIC_KEYS.get(section.rolled_orb_type, "")
	if key != "":
		var after: int = stats.metrics.orbs.get(key)
		section.metric_key = key
		section.counter_before = orbs_before[key]
		section.counter_after = after
		section.counter_credited = after - orbs_before[key]
		section.counter_matches_amount = section.counter_credited == section.rolled_amount
	else:
		section.counter_matches_amount = false

	section.pass = section.drop_spawned and section.does_vaccuum \
			and section.collected and section.removed_from_tree \
			and section.orb_pickup_signal_seen and section.counter_matches_amount


func _on_probe_orb_pickup(orb_type, amount, credited) -> void:
	credited.seen = true
	credited.type = orb_type
	credited.amount += amount


# --- 2: real Mob elite death drops an OrbPickup ------------------------------

func _count_scripts_under(node: Node, script_path: String) -> int:
	var target = load(script_path)
	var count := 0
	for child in node.get_children():
		if child.get_script() == target:
			count += 1
	return count


func _check_elite_drop_chain() -> void :
	var section: Dictionary = _result.elite_drop_chain
	var mob_scene = load(MOB_SCENE_PATH)
	if mob_scene == null:
		_result.errors.append("failed to load %s" % MOB_SCENE_PATH)
		section.pass = false
		return

	var deaths := {"count": 0}

	var mob = mob_scene.instantiate()
	mob.type = MonsterTypes.MonsterType.SKELETON_ARCHER
	mob.is_elite = true
	mob.position = Vector2(-300, 0)

	
	var killer := ProbePlayerEntity.new()
	killer.stats = ProbeStatsStub.new()
	killer.position = Vector2(1000000, 1000000)
	add_child(killer)
	GameState.set_global("player", killer)

	add_child(mob)
	for i in range(4):
		await get_tree().process_frame

	var stats = mob.get_node_or_null("Stats")
	if stats == null:
		_result.errors.append("elite mob Stats node missing")
		section.pass = false
		return
	stats.connect("died", func(): deaths.count += 1)

	var ground = GameState.get_global("ground")
	var orbs_before := _count_scripts_under(ground, "res://scenes/Pickups/Orb/OrbPickup.gd")

	var bundle: Dictionary = {"damage": {SkillTags.Tags.PHYSICAL: 9999999.0}}
	var did_kill := false
	for attempt in range(10):
		var res: Dictionary = stats.apply_damage(bundle, Color.WHITE, null, false)
		did_kill = did_kill or res.did_kill
		if did_kill:
			break
	section.killed_through_apply_damage = did_kill

	
	for i in range(12):
		await get_tree().process_frame

	section.mob_removed = not is_instance_valid(mob) or mob.is_queued_for_deletion()
	section.death_settled_once = deaths.count == 1
	var orbs_after := _count_scripts_under(ground, "res://scenes/Pickups/Orb/OrbPickup.gd")
	section.orbs_before = orbs_before
	section.orbs_after = orbs_after
	section.elite_dropped_orb = orbs_after > orbs_before
	section.genes_dropped = _count_scripts_under(ground,
			"res://scenes/Pickups/Gene/GenePickup.gd")

	section.pass = section.killed_through_apply_damage and section.mob_removed \
			and section.death_settled_once and section.elite_dropped_orb


# --- 3: real PortalPickup confirm -> DeathScreen popup handoff ---------------

func _check_portal_pickup() -> void :
	var section: Dictionary = _result.portal
	var portal_scene = load(PORTAL_SCENE_PATH)
	if portal_scene == null:
		_result.errors.append("failed to load %s" % PORTAL_SCENE_PATH)
		section.pass = false
		return

	var portal = portal_scene.instantiate()
	add_child(portal)
	section.persistent = portal.persistent

	portal.do_pickup()
	await get_tree().process_frame

	var dialog = null
	for child in portal.get_children():
		if child is ConfirmationDialog:
			dialog = child
			break
	section.confirm_dialog_opened = dialog != null
	if dialog == null:
		_result.errors.append("portal pickup did not open a confirmation dialog")
		section.pass = false
		return
	section.dialog_title = dialog.title
	section.dialog_title_correct = dialog.title == "Return to Hideout?"

	
	var world: Node = get_tree().root.get_node_or_null("World")
	section.world_stub_present = world != null
	var queued_before: int = PopupManager.queued_popups.size()
	dialog.confirmed.emit()
	var queued_after: int = PopupManager.queued_popups.size()
	section.death_screen_queued = queued_after == queued_before + 1
	if queued_after > queued_before:
		var pending = PopupManager.queued_popups.back()[0]
		PopupManager.queued_popups.clear()
		if is_instance_valid(pending):
			pending.free()
	PopupManager.reset()

	section.pass = section.persistent and section.confirm_dialog_opened \
			and section.dialog_title_correct and section.world_stub_present \
			and section.death_screen_queued


func _report() -> void :
	var overall: bool = _result.orb_drop.get("pass", false) \
			and _result.elite_drop_chain.get("pass", false) \
			and _result.portal.get("pass", false) \
			and _result.errors.is_empty()
	_result["c1_pass"] = overall
	_result["pass"] = overall
	print("P3_PROBE_RESULT:" + JSON.stringify(_result))
	get_tree().quit(0 if _result.pass else 2)
