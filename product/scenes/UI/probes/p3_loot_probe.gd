extends Node2D
# P3-D loot probe driver (Exit Criteria E6), headless.
#
# Spawns a drop stub that uses the REAL collision pickup contract
# (Area2D overlap with an entity in the "player" group) and credits the REAL
# inventory API (Stats.add_orb -> metrics.orbs.* + orb_pickup signal).
#
# NOTE: product/scenes/Pickups/** (OrbPickup/GenePickup/PortalPickup) is still
# missing from product/ and restoring it is outside this lane's write domain,
# so the drop itself is a test stub by necessity.  Everything downstream of
# the collision moment - the inventory credit and its queryable state - is
# real production code.
#
# Machine-readable result line:  P3_PROBE_RESULT:{...}
# Exit codes: 0 = PASS, 2 = FAIL.

const PROBE_ID := "p3_loot_probe"
const CREDIT_AMOUNT := 3

var _result := {}


class ProbePlayerEntity extends Node2D:
	# Minimal player entity: group membership drives Pickup-style collision;
	# `gear` and `stats` are required by Stats._recache_gear/_ready.
	var stats = null
	var gear = null

	func _init() -> void:
		add_to_group("player")


class DropStub extends Area2D:
	# Mirrors the Pickup.gd contract: area_entered -> player check -> credit.
	signal credited(orb_type, amount)

	var orb_type = null
	var amount := CREDIT_AMOUNT
	var collected := false

	func _ready() -> void:
		monitoring = true
		monitorable = true
		var shape := CollisionShape2D.new()
		var circle := CircleShape2D.new()
		circle.radius = 16.0
		shape.shape = circle
		add_child(shape)
		area_entered.connect(_on_area_entered)

	func _on_area_entered(area: Area2D) -> void:
		if collected:
			return
		var entity = area.get_parent()
		if entity != null and entity.is_in_group("player"):
			collected = true
			entity.stats.add_orb(orb_type, amount)
			emit_signal("credited", orb_type, amount)


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


func _make_player_entity() -> ProbePlayerEntity:
	var entity := ProbePlayerEntity.new()
	entity.name = "ProbePlayer"

	var gear := Node2D.new()
	gear.name = "Gear"
	entity.add_child(gear)
	entity.gear = gear

	var stats_scene = load("res://scenes/Stats.tscn")
	if stats_scene == null:
		return entity
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


func _run() -> void:
	var result := {
		"probe_id": PROBE_ID,
		"drop_spawned": false,
		"collision_pickup_fired": false,
		"orb_pickup_signal_seen": false,
		"orbs_blue_before": null,
		"orbs_blue_after": null,
		"credited_amount": 0,
		"errors": [],
	}
	seed(20260822)
	Globals.zone_level = 1

	_seed_character("probe")
	Globals.selected_character_name = "probe"

	var player := _make_player_entity()
	add_child(player)
	var stats = player.stats
	if stats == null or not stats.is_inside_tree():
		result.errors.append("failed to instantiate res://scenes/Stats.tscn under the probe player entity")
		_result = result
		return

	result.orbs_blue_before = stats.metrics.orbs.blue
	stats.connect("orb_pickup", Callable(self, "_on_orb_pickup").bind(result))

	var drop := DropStub.new()
	drop.orb_type = Constants.OrbType.BLUE
	drop.position = Vector2(100, 0)
	add_child(drop)
	result.drop_spawned = drop.is_inside_tree()

	player.position = Vector2(100, 0)

	for i in range(12):
		await get_tree().physics_frame
		if drop.collected:
			break

	for i in range(2):
		await get_tree().process_frame

	result.collision_pickup_fired = drop.collected
	result.orbs_blue_after = stats.metrics.orbs.blue
	_result = result


func _on_orb_pickup(_orb_type, _amount, result) -> void:
	result.orb_pickup_signal_seen = true
	result.credited_amount += _amount


func _report() -> void:
	var e6_pass: bool = _result.drop_spawned and _result.collision_pickup_fired \
			and _result.orb_pickup_signal_seen \
			and _result.orbs_blue_before == 0 \
			and _result.orbs_blue_after == CREDIT_AMOUNT
	_result["e6_pass"] = e6_pass
	_result["pass"] = e6_pass and _result.errors.is_empty()
	print("P3_PROBE_RESULT:" + JSON.stringify(_result))
	get_tree().quit(0 if _result.pass else 2)
