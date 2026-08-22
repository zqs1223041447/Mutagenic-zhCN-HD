extends Node
# P3-E UI probe driver (Exit Criteria E7), headless.
#
# Opens the skill screen (SkillSelect) and the passive tree screen
# (PassiveTreePopup) through the real PopupManager flow, verifies neither
# crashes, then closes both and verifies the popup stack drains back to zero.
#
# A seeded character is required because both popups resolve
# GameState.get_active_stats().  help_tips carries "weapon_intro": true so
# SkillSelect does not chain-open the WeaponIntro tip; the WeaponIntro scene
# itself is exercised by the boot probe after the P3 asset restore.
#
# Machine-readable result line:  P3_PROBE_RESULT:{...}
# Exit codes: 0 = PASS, 2 = FAIL.

const PROBE_ID := "p3_ui_probe"

var _result := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	await _run()
	_report()


func _seed_character(name: String) -> void:
	var empty_supports := func(n: int) -> Dictionary:
		var keys := ["a", "b", "c", "d", "e", "f"]
		var supports := {}
		for i in range(n):
			supports[keys[i]] = null
		return supports
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
		"help_tips": {"weapon_intro": true},
		"new_item_ids": {},
		"new_item_types": {},
		"tutorial_events": {},
		"mutation_tree_loadout": {"class": "WARRIOR", "passives": ["root_warrior"]},
		"specialization_loadout": {"class": null, "passives": ["root"]},
		"skill_loadout": {
			"primary": {"skill": null, "supports": empty_supports.call(6)},
			"secondary": {"skill": null, "supports": empty_supports.call(4)},
			"support_one": {"skill": null, "supports": empty_supports.call(4)},
			"support_two": {"skill": null, "supports": empty_supports.call(2)},
			"support_three": {"skill": null, "supports": empty_supports.call(1)},
			"support_four": {"skill": null, "supports": empty_supports.call(1)},
		},
		"gene_loadout": {},
		"genes": {},
		"stored_mods": {},
		"filters": {},
	}


func _await_frames(count: int) -> void:
	for i in range(count):
		await get_tree().process_frame


func _run() -> void:
	_result = {
		"probe_id": PROBE_ID,
		"skill_screen_opened": false,
		"skill_screen_closed": false,
		"passive_tree_opened": false,
		"passive_tree_nodes_built": false,
		"passive_tree_closed": false,
		"popup_stack_drained": false,
		"errors": [],
	}
	seed(20260822)
	Globals.zone_level = 1

	_seed_character("probe")
	Globals.selected_character_name = "probe"

	var popup_manager = get_node_or_null("/root/PopupManager")
	if popup_manager == null:
		_result.errors.append("PopupManager autoload missing")
		return

	# --- E7a: skill screen -------------------------------------------------
	var skill_scene = load("res://scenes/Popups/Dialogs/SkillSelect/SkillSelect.tscn")
	if skill_scene == null:
		_result.errors.append("SkillSelect.tscn failed to load")
		return
	var skill_popup = skill_scene.instantiate()
	popup_manager.show_popup(skill_popup, self)
	await _await_frames(5)

	if not is_instance_valid(skill_popup) or not skill_popup.is_inside_tree():
		_result.errors.append("SkillSelect did not enter the tree via PopupManager")
		return
	_result.skill_screen_opened = true

	popup_manager.pop_popup()
	await _await_frames(4)
	if is_instance_valid(skill_popup) and skill_popup.is_inside_tree():
		_result.errors.append("SkillSelect survived pop_popup()")
		return
	_result.skill_screen_closed = true

	# --- E7b: passive tree screen ------------------------------------------
	var tree_scene = load("res://scenes/Popups/Dialogs/PassiveTree/PassiveTreePopup.tscn")
	if tree_scene == null:
		_result.errors.append("PassiveTreePopup.tscn failed to load")
		return
	var tree_popup = tree_scene.instantiate()
	popup_manager.show_popup(tree_popup, self)
	await _await_frames(10)

	if not is_instance_valid(tree_popup) or not tree_popup.is_inside_tree():
		_result.errors.append("PassiveTreePopup did not enter the tree via PopupManager")
		return
	_result.passive_tree_opened = true

	var nodes_container = tree_popup.get_node_or_null("PassiveTree/PassiveTreeContainer/Nodes")
	if nodes_container != null and nodes_container.get_child_count() > 0:
		_result.passive_tree_nodes_built = true
	else:
		_result.errors.append("PassiveTreePopup built no passive nodes")

	popup_manager.pop_popup()
	await _await_frames(4)
	if is_instance_valid(tree_popup) and tree_popup.is_inside_tree():
		_result.errors.append("PassiveTreePopup survived pop_popup()")
		return
	_result.passive_tree_closed = true
	_result.popup_stack_drained = popup_manager.is_free()


func _report() -> void:
	var e7_pass: bool = _result.skill_screen_opened and _result.skill_screen_closed \
			and _result.passive_tree_opened and _result.passive_tree_nodes_built \
			and _result.passive_tree_closed and _result.popup_stack_drained
	_result["e7_pass"] = e7_pass
	_result["pass"] = e7_pass and _result.errors.is_empty()
	print("P3_PROBE_RESULT:" + JSON.stringify(_result))
	get_tree().quit(0 if _result.pass else 2)
