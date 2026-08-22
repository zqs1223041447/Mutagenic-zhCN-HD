extends Node2D
# P4-B F1 VFX-rhythm probe driver, headless.
#
# Machine-verifiable structural assertions for the three F1 feedback points:
#   1. HitBurst (scenes/Particles/HitBurst.tscn): element->color configuration
#      resolves through override -> per-instance table -> shared defaults;
#      one-shot lifecycle frees itself; Mob wiring spawns bursts on health
#      loss through the REAL Stats.apply_damage path, throttled by the
#      per-mob cooldown.
#   2. Death dissolve rhythm (scenes/Mobs/DissolveMob.tscn): configurable
#      duration/delay drive both the shader ramp and the removal timer.
#   3. FloatingDamage rhythm tiers (scenes/Particles/FloatingDamage.tscn):
#      normal/crit tables differ and are honored (tint, pop, lifetime).
#
# Subjective feel is explicitly out of scope; everything asserted here is
# machine-checkable structure/timing.
#
# Machine-readable result line:  P3_PROBE_RESULT:{...}
# Exit codes: 0 = PASS, 2 = FAIL.

const PROBE_ID := "p4_b_vfx_probe"

const HIT_BURST_SCRIPT = preload("res://scenes/Particles/HitBurst.gd")
const HIT_BURST_SCENE = preload("res://scenes/Particles/HitBurst.tscn")
const DISSOLVE_SCENE = preload("res://scenes/Mobs/DissolveMob.tscn")
const FLOATING_DAMAGE_SCRIPT = preload("res://scenes/Particles/FloatingDamage.gd")
const FLOATING_DAMAGE_SCENE = preload("res://scenes/Particles/FloatingDamage.tscn")
const MOB_SCENE_PATH := "res://scenes/Mobs/Mob.tscn"

const ELEMENTS := {
	"fire": 11,        # SkillTags.Tags.FIRE
	"cold": 12,        # SkillTags.Tags.COLD
	"lightning": 13,   # SkillTags.Tags.LIGHTNING
	"physical": 14,    # SkillTags.Tags.PHYSICAL
	"toxic": 15,       # SkillTags.Tags.TOXIC
}

var _result := {}


class ProbeStatsStub extends RefCounted:
	func add_kills(_amount, _elite = false, _boss = false) -> void:
		pass

	func add_xp(_amount) -> void:
		pass


class ProbePlayerStub extends Node2D:
	var stats = ProbeStatsStub.new()

	func _init() -> void:
		add_to_group("player")
		position = Vector2(1000000, 1000000)


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


func _setup_world_stubs() -> void:
	seed(20260822)
	Globals.zone_level = 1
	GameState.saved_stats.settings.enable_fx = true

	
	var world := Node2D.new()
	world.name = "World"
	var texts := Node2D.new()
	texts.name = "FloatingDamageTexts"
	world.add_child(texts)
	get_tree().root.add_child.call_deferred(world)

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

	
	Levels.config["p4b_vfx"] = {"map_type": Levels.MAP_TYPE.LADDER}
	Globals.selected_level = "p4b_vfx"


func _run() -> void :
	_result = {
		"probe_id": PROBE_ID,
		"fx_enabled": null,
		"hit_burst": {},
		"mob_hit_wiring": {},
		"death_dissolve": {},
		"floating_damage": {},
		"errors": [],
	}
	_setup_world_stubs()
	_result.fx_enabled = GameState.is_fx_enabled()

	await _check_hit_burst_config()
	await _check_mob_hit_wiring()
	await _check_death_dissolve()
	await _check_floating_damage()


# --- 1a: HitBurst element-color configuration + lifecycle --------------------

func _check_hit_burst_config() -> void :
	var section: Dictionary = _result.hit_burst
	var defaults: Dictionary = HIT_BURST_SCRIPT.default_element_colors()

	var colors_match := {}
	for key in ELEMENTS:
		var element: int = ELEMENTS[key]
		var burst = HIT_BURST_SCRIPT.new()
		burst.element = element
		colors_match[key] = burst.burst_color() == defaults[element]
		burst.free()
	section.element_colors_match = colors_match

	var override = HIT_BURST_SCRIPT.new()
	override.color_override = Color(1, 0, 1, 1)
	override.element = ELEMENTS.fire
	section.override_wins = override.burst_color() == Color(1, 0, 1, 1)
	override.free()

	var unknown = HIT_BURST_SCRIPT.new()
	unknown.element = 999
	section.unknown_falls_back_white = unknown.burst_color() == Color.WHITE
	unknown.free()

	
	var live = HIT_BURST_SCENE.instantiate()
	live.burst_lifetime = 0.2
	add_child(live)
	section.emitting_on_ready = live.emitting
	
	await get_tree().create_timer(0.2 + 0.5).timeout
	section.freed_after_lifetime = not is_instance_valid(live) \
			or live.is_queued_for_deletion()

	section.pass = _all_true(colors_match.values()) and section.override_wins \
			and section.unknown_falls_back_white and section.emitting_on_ready \
			and section.freed_after_lifetime


# --- 1a: Mob wiring through the real damage path -----------------------------

func _check_mob_hit_wiring() -> void :
	var section: Dictionary = _result.mob_hit_wiring
	var mob_scene = load(MOB_SCENE_PATH)
	if mob_scene == null:
		_result.errors.append("failed to load %s" % MOB_SCENE_PATH)
		section.pass = false
		return

	var mob = mob_scene.instantiate()
	mob.type = MonsterTypes.MonsterType.SKELETON_ARCHER
	mob.position = Vector2(200, 0)
	add_child(mob)

	for i in range(4):
		await get_tree().process_frame

	var stats = mob.get_node_or_null("Stats")
	if stats == null:
		_result.errors.append("mob Stats node missing")
		section.pass = false
		return

	
	var ground = GameState.get_global("ground")
	var spawns := {"total": 0}
	ground.child_entered_tree.connect(func(node):
		if node.get_script() == HIT_BURST_SCRIPT:
			spawns.total += 1)

	var bundle: Dictionary = {"damage": {SkillTags.Tags.PHYSICAL: 1.0}}
	var hp_before: float = stats.health
	var damage_applied := false
	for attempt in range(10):
		if stats.health <= 1.5:
			break
		
		var res: Dictionary = stats.apply_damage(bundle, Color.WHITE, null, false)
		if res.damage > 0.0:
			damage_applied = true
			break
	section.damage_applied = damage_applied
	section.hp_before = hp_before
	section.mob_alive = is_instance_valid(mob) and stats.health > 1.0
	if not damage_applied:
		_result.errors.append("apply_damage never landed on the mob")
		section.pass = false
		return

	
	var seen_first := false
	for i in range(40):
		await get_tree().physics_frame
		if spawns.total > 0:
			seen_first = true
			break
	section.burst_spawned_on_hit = seen_first
	if not seen_first:
		_result.errors.append("no HitBurst spawned after mob health loss")
		section.pass = false
		return

	
	var after_first: int = spawns.total
	stats.apply_damage(bundle, Color.WHITE, null, false)
	for i in range(20):
		await get_tree().physics_frame
	section.cooldown_throttles = spawns.total == after_first

	
	await get_tree().create_timer(mob.hit_burst_min_interval + 0.3).timeout
	stats.apply_damage(bundle, Color.WHITE, null, false)
	var reached_two := false
	for i in range(40):
		await get_tree().physics_frame
		if spawns.total >= after_first + 1:
			reached_two = true
			break
	section.second_burst_after_interval = reached_two
	section.bursts_total = spawns.total

	section.pass = section.damage_applied and section.mob_alive \
			and section.burst_spawned_on_hit \
			and section.cooldown_throttles and section.second_burst_after_interval


# --- 1b: death -> dissolve -> removal pacing ---------------------------------

func _check_death_dissolve() -> void :
	var section: Dictionary = _result.death_dissolve

	var configured = DISSOLVE_SCENE.instantiate()
	configured.dissolve_duration = 0.4
	configured.dissolve_delay = 0.1
	add_child(configured)

	var vanilla = DISSOLVE_SCENE.instantiate()
	add_child(vanilla)

	
	await get_tree().create_timer(0.05).timeout
	section.hold_progress_zero = configured.dissolve_progress() == 0.0
	section.default_progressing = vanilla.dissolve_progress() > 0.0

	
	await get_tree().create_timer(0.38).timeout
	section.progress_near_full_before_free = configured.dissolve_progress() >= 0.8

	
	await get_tree().create_timer(0.12).timeout
	
	section.configured_freed_after_total = not is_instance_valid(configured) \
			or configured.is_queued_for_deletion()
	section.default_freed_after_duration = not is_instance_valid(vanilla) \
			or vanilla.is_queued_for_deletion()

	section.pass = section.hold_progress_zero and section.default_progressing \
			and section.progress_near_full_before_free \
			and section.configured_freed_after_total \
			and section.default_freed_after_duration


# --- 1c: floating damage normal/crit rhythm tiers ----------------------------

func _wait_freed(node: Node, timeout_s := 2.0) -> float:
	var started := Time.get_ticks_msec()
	while is_instance_valid(node) and not node.is_queued_for_deletion():
		if Time.get_ticks_msec() - started > timeout_s * 1000.0:
			return -1.0
		await get_tree().process_frame
	return (Time.get_ticks_msec() - started) / 1000.0


func _check_floating_damage() -> void :
	var section: Dictionary = _result.floating_damage

	var normal_table: Dictionary = FLOATING_DAMAGE_SCRIPT.rhythm_for(false)
	var crit_table: Dictionary = FLOATING_DAMAGE_SCRIPT.rhythm_for(true)
	section.rhythm_tables_differ = normal_table.duration != crit_table.duration \
			and crit_table.pop_duration > 0.0 and crit_table.tint != null

	
	var normal = FLOATING_DAMAGE_SCENE.instantiate()
	add_child(normal)
	var base_scale: Vector2 = normal.label.scale
	normal.show_value("12", Vector2(0, -8), 0.25, PI / 2, Color.WHITE, false)
	await get_tree().process_frame
	section.normal_no_pop = normal.label.scale == base_scale \
			and normal.modulate == Color.WHITE
	section.font_color_override_applied = \
			normal.label.get_theme_color("font_color") == Color.WHITE
	var normal_life := await _wait_freed(normal)
	section.normal_lifetime_s = normal_life

	
	var crit = FLOATING_DAMAGE_SCENE.instantiate()
	add_child(crit)
	crit.show_value("99", Vector2(0, -8), 0.25, PI / 2, Color.WHITE, true)
	await get_tree().process_frame
	section.crit_tint_applied = crit.modulate == Color(1, 0, 0)
	section.crit_pop_visible = crit.label.scale.x > base_scale.x * 1.2
	var crit_life := await _wait_freed(crit)
	section.crit_lifetime_s = crit_life

	section.crit_lives_longer_than_normal = crit_life > normal_life \
			and normal_life > 0.0 and crit_life > 0.0

	section.pass = section.rhythm_tables_differ and section.crit_tint_applied \
			and section.crit_pop_visible and section.normal_no_pop \
			and section.font_color_override_applied \
			and section.crit_lives_longer_than_normal


func _all_true(values) -> bool:
	for v in values:
		if v != true:
			return false
	return true


func _report() -> void :
	var overall: bool = _result.hit_burst.get("pass", false) \
			and _result.mob_hit_wiring.get("pass", false) \
			and _result.death_dissolve.get("pass", false) \
			and _result.floating_damage.get("pass", false) \
			and _result.errors.is_empty()
	_result["f1_pass"] = overall
	_result["pass"] = overall
	print("P3_PROBE_RESULT:" + JSON.stringify(_result))
	get_tree().quit(0 if _result.pass else 2)
