extends Node
## P3-D probe driver: E6 loot loop (drop spawns -> ground entity -> player
## pickup -> queryable inventory).
##
## Chain under test (production scenes, no shortcuts):
##   GenePickup.tscn (restored product/scenes/Pickups chain, the same scene
##   Mob._on_death instantiates) is spawned onto a ground layer
##   -> Pickup (Area2D, monitoring mask 1) overlaps the player-side Area2D
##   -> auto_pickup -> do_pickup -> Genes.pickup_gene()
##   -> GameState.get_active_stats().genes[id] becomes queryable.
##
## Player stub mirrors the real Player.tscn interface that Pickups and
## GeneGenerator rely on: a body in group "player" owning an Area2D collider
## (layer 1, monitorable) and exposing stats.keystones (read by
## GeneGenerator.generate_random_gene for TREE_TRANSMOGRIFICATION).
##
## Results are printed as one JSON line wrapped in P3D_RESULT_JSON<<< >>>
## and parsed by scripts/validate/run_p3_d_loot.py.
## The user save file is backed up before any mutation and restored on exit.

const CHAR_NAME: String = "P3DProbeChar"
const CHAR_CLASS: String = "MAGE"
const MARKER: String = "P3D_RESULT_JSON<<<"
const PICKUP_SCENE_PATH: String = "res://scenes/Pickups/Gene/GenePickup.tscn"
const ORB_SCENE_PATH: String = "res://scenes/Pickups/Orb/OrbPickup.tscn"
const PORTAL_SCENE_PATH: String = "res://scenes/Pickups/Portal/PortalPickup.tscn"
const PICKUP_TIMEOUT_FRAMES: int = 600
const WATCHDOG_SECONDS: float = 120.0

var results: Dictionary = {"task": "P3-D", "e6": {}}
var backup_text: String = ""
var had_backup: bool = false


class PlayerStub:
	extends Node2D
	## Minimal stand-in for scenes/Player/Player.tscn: group tag + the
	## stats.keystones dictionary GeneGenerator reads.
	var stats = {"keystones": {}}


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
	results["all_pass"] = false
	results["finished"] = true
	print(MARKER, JSON.stringify(results), ">>>")
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
	return bool(pred.call())


func _orchestrate() -> void:
	await get_tree().process_frame
	seed(20260822)

	var e6: Dictionary = {}

	# --- active character (same API the UI calls), so inventory writes land ---
	if not GameState.saved_stats.characters.has(CHAR_NAME):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
		await _until(func() -> bool: return GameState.saved_stats.characters.has(CHAR_NAME), 120)
	e6["probe_character_created"] = GameState.saved_stats.characters.has(CHAR_NAME)
	Globals.selected_character_name = CHAR_NAME
	e6["active_identity_matches"] = str(GameState.get_active_stats().get("character_name", "")) == CHAR_NAME

	# --- minimal stage: ground layer + player stub (no level/map needed) ---
	var ground := Node2D.new()
	ground.name = "Ground"
	add_child(ground)
	GameState.set_global("ground", ground)
	GameState.set_global("level_layer", ground)

	var player := PlayerStub.new()
	player.name = "PlayerStub"
	player.add_to_group("player")
	var collider := Area2D.new()
	collider.name = "PlayerCollider"
	collider.collision_layer = 1
	collider.collision_mask = 0
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = 16.0
	shape.shape = circle
	collider.add_child(shape)
	player.add_child(collider)
	add_child(player)
	player.position = Vector2(-200, 0)
	GameState.set_global("player", player)
	e6["player_stub_ready"] = player.is_inside_tree() and collider.is_inside_tree()

	# --- s1: drop scene resolves (Mob.gd gene_pickup reference now valid) ---
	e6["drop_scene_exists"] = ResourceLoader.exists(PICKUP_SCENE_PATH)
	var pickup_scene: PackedScene = null
	if bool(e6["drop_scene_exists"]):
		pickup_scene = load(PICKUP_SCENE_PATH)
	e6["drop_scene_loaded"] = pickup_scene != null

	if pickup_scene != null:
		# --- s2: spawn the drop onto the ground layer (Mob._on_death wiring) ---
		var pickup: Node = pickup_scene.instantiate()
		pickup.zone_level = 1
		pickup.rarity_bonus = 0.0
		pickup.unique_pools = [UniquePoolGeneric.get("pool")]
		pickup.auto_pickup = true
		ground.add_child(pickup)
		pickup.global_position = Vector2(200, 0)
		e6["drop_spawned"] = pickup.is_inside_tree() and pickup.get_parent() == ground

		var gene: Variant = pickup.get("gene")
		e6["gene_generated"] = gene != null and typeof(gene) == TYPE_DICTIONARY and str(gene.get("id", "")) != ""
		if gene != null and typeof(gene) == TYPE_DICTIONARY:
			e6["gene_id"] = str(gene.get("id", ""))
			e6["gene_type"] = str(gene.get("type", ""))

		var gid: String = str(e6.get("gene_id", ""))
		var stats_before: Dictionary = GameState.get_active_stats()
		var genes_before: int = stats_before.genes.keys().size()
		e6["inventory_absent_before"] = gid != "" and not stats_before.genes.has(gid)
		e6["genes_count_before"] = genes_before

		# --- s3: player moves onto the drop -> auto-pickup fires -> entity frees ---
		var picked_flag := false
		var freed := false
		for i in range(PICKUP_TIMEOUT_FRAMES):
			if not is_instance_valid(pickup):
				freed = true
				break
			# walk the stub toward the drop until overlap (like real movement)
			player.position = player.position.move_toward(pickup.global_position, 4.0)
			if bool(pickup.get("picked_up")):
				picked_flag = true
			await get_tree().physics_frame
		if is_instance_valid(pickup):
			picked_flag = picked_flag or bool(pickup.get("picked_up"))
		else:
			freed = true
		e6["pickup_flag_observed"] = picked_flag
		e6["pickup_entity_freed"] = freed
		e6["pickup_fired"] = picked_flag or freed

		# --- s4: inventory queryable through GameState after pickup ---
		var stats_after: Dictionary = GameState.get_active_stats()
		e6["inventory_has_item"] = gid != "" and stats_after.genes.has(gid)
		if bool(e6["inventory_has_item"]):
			var entry: Variant = stats_after.genes[gid]
			e6["inventory_item_type_matches"] = typeof(entry) == TYPE_DICTIONARY \
					and str(entry.get("type", "")) == str(e6.get("gene_type", ""))
			var slot: Variant = Genes.slot_for_base(entry.get("type"))
			e6["inventory_slot_recorded"] = slot != null \
					and bool(stats_after.new_item_types.get(slot, false))
		else:
			e6["inventory_item_type_matches"] = false
			e6["inventory_slot_recorded"] = false
		e6["inventory_grew"] = stats_after.genes.keys().size() > genes_before
		e6["new_item_id_marked"] = bool(stats_after.new_item_ids.get(gid, false))

	# --- informational (non-gating): sibling drop scenes still missing ---
	e6["orb_pickup_scene_present"] = ResourceLoader.exists(ORB_SCENE_PATH)
	e6["portal_pickup_scene_present"] = ResourceLoader.exists(PORTAL_SCENE_PATH)

	e6["pass"] = bool(e6.get("probe_character_created")) \
			and bool(e6.get("active_identity_matches")) \
			and bool(e6.get("player_stub_ready")) \
			and bool(e6.get("drop_scene_exists")) \
			and bool(e6.get("drop_scene_loaded")) \
			and bool(e6.get("drop_spawned")) \
			and bool(e6.get("gene_generated")) \
			and bool(e6.get("inventory_absent_before")) \
			and bool(e6.get("pickup_fired")) \
			and bool(e6.get("pickup_entity_freed")) \
			and bool(e6.get("inventory_has_item")) \
			and bool(e6.get("inventory_item_type_matches")) \
			and bool(e6.get("inventory_slot_recorded")) \
			and bool(e6.get("inventory_grew")) \
			and bool(e6.get("new_item_id_marked"))
	results["e6"] = e6
	results["all_pass"] = bool(e6.get("pass"))
	results["finished"] = true
	_restore_save()
	print(MARKER, JSON.stringify(results), ">>>")
	await get_tree().process_frame
	get_tree().quit(0 if bool(results["all_pass"]) else 1)
