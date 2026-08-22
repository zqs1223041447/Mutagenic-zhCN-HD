extends Node
## P3-E probe driver: E7 skill-select UI + passive-tree UI open/close roundtrip.
##
## Production entry points under test (no shortcuts):
##   SkillBench.on_interact / MutationBench.on_interact:
##     PopupManager.show_popup(scene.instantiate(), parent)
##   close path: PopupManager.pop_popup() (same as Back/Close buttons).
##   Nested real-data probe: SkillButton "pressed" -> SkillList grid filled
##   from Skills.config (skill name list non-empty).
##
## Assertions use node existence/counts only (headless has no pixels):
##   - popup enters tree via PopupManager queue
##   - SkillSelect: primary button + name label present, playable skill
##     count > 0, SkillList grid lists >= 1 real skill name
##   - PassiveTreePopup: Nodes/Edges containers populated, points label text
##   - after both roundtrips: PopupManager open+queued empty, no residual
##     dialog nodes, pause counter balanced, process still alive.
##
## Results printed as one JSON line wrapped in P3E_RESULT_JSON<<< >>>
## and parsed by scripts/validate/run_p3_e_ui.py.
## The user save file is backed up before any mutation and restored on exit.

const CHAR_NAME: String = "P3EProbeChar"
const CHAR_CLASS: String = "MAGE"
const MARKER: String = "P3E_RESULT_JSON<<<"
const POPUP_TIMEOUT_FRAMES: int = 300
const WATCHDOG_SECONDS: float = 240.0

const SKILL_SELECT_SCENE: String = "res://scenes/Popups/Dialogs/SkillSelect/SkillSelect.tscn"
const PASSIVE_TREE_SCENE: String = "res://scenes/Popups/Dialogs/PassiveTree/PassiveTreePopup.tscn"

const PRIMARY_BUTTON_PATH: String = "MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/VBoxContainer/HBoxContainer/HBoxContainer/PrimaryButton"
const SKILL_LIST_GRID_PATH: String = "MarginContainer/CenterContainer/PanelContainer/HBoxContainer/VBoxContainer2/GridContainer"
const NODES_PATH: String = "PassiveTree/PassiveTreeContainer/Nodes"
const EDGES_PATH: String = "PassiveTree/PassiveTreeContainer/Edges"
const POINTS_LABEL_PATH: String = "PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/VBOX/HBoxContainer/PointsAvailableLevel"
const SPEC_LABEL_PATH: String = "PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/VBOX/HBoxContainer2/SpecializationLabel"

var results: Dictionary = {"task": "P3-E", "skill_select": {}, "passive_tree": {}, "cleanup": {}}
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


func _top_popup_script_path() -> String:
	if PopupManager.open_popups.is_empty():
		return ""
	var n: Node = PopupManager.open_popups.back()[0]
	if n == null or not is_instance_valid(n):
		return ""
	var s: Script = n.get_script()
	return s.resource_path if s != null else ""


func _ensure_character() -> Dictionary:
	var info: Dictionary = {}
	info["character_preexisting"] = GameState.saved_stats.characters.has(CHAR_NAME)
	if not bool(info["character_preexisting"]):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
		await _until(func() -> bool: return GameState.saved_stats.characters.has(CHAR_NAME), 120)
	info["character_ready"] = GameState.saved_stats.characters.has(CHAR_NAME)
	Globals.selected_character_name = CHAR_NAME
	# Simulate a returning player so SkillSelect does not stack WeaponIntro;
	# keeps the popup stack single-level for exact leak assertions.
	GameState.mark_help_tip_read("weapon_intro")
	info["weapon_intro_marked_read"] = GameState.is_help_tip_read("weapon_intro")
	return info


func _orchestrate() -> void:
	await get_tree().process_frame
	results["setup"] = await _ensure_character()

	var ss: Dictionary = await _phase_skill_select()
	results["skill_select"] = ss
	var pt: Dictionary = await _phase_passive_tree()
	results["passive_tree"] = pt
	var cl: Dictionary = _phase_cleanup()
	results["cleanup"] = cl

	results["all_pass"] = bool(ss.get("pass")) and bool(pt.get("pass")) and bool(cl.get("pass"))
	results["finished"] = true
	_restore_save()
	print(MARKER, JSON.stringify(results), ">>>")
	await get_tree().process_frame
	get_tree().quit(0 if bool(results["all_pass"]) else 1)


func _phase_skill_select() -> Dictionary:
	var ss: Dictionary = {}
	var packed: PackedScene = load(SKILL_SELECT_SCENE)
	ss["scene_loaded"] = packed != null
	if packed == null:
		ss["pass"] = false
		return ss

	# production entry: instantiate + PopupManager.show_popup (SkillBench path)
	var popup: Node = packed.instantiate()
	PopupManager.show_popup(popup, self)
	ss["opened"] = await _until(func() -> bool:
		return PopupManager.open_popups.size() == 1 \
				and is_instance_valid(popup) and popup.is_inside_tree(), POPUP_TIMEOUT_FRAMES)
	if not bool(ss["opened"]):
		ss["pass"] = false
		return ss

	var primary: Node = popup.get_node_or_null(PRIMARY_BUTTON_PATH)
	ss["primary_button_present"] = primary != null
	var name_label: Node = primary.get_node_or_null("SkillButton/VBoxContainer/NameLabel") if primary != null else null
	ss["name_label_present"] = name_label != null

	# real data behind the UI: playable skills exist and slots are wired
	var playable: int = 0
	for sk in Skills.config.keys():
		var cfg: Variant = Skills.config[sk]
		if cfg is Dictionary:
			if bool(cfg.get("playable", false)):
				playable += 1
		elif cfg != null and "playable" in cfg:
			if bool(cfg.playable):
				playable += 1
	ss["playable_skill_count"] = playable
	ss["equipped_slot_count"] = GameState.get_equipped_skills().keys().size()

	# nested roundtrip through the real button connection -> SkillList grid
	if primary != null:
		var inner: BaseButton = primary.get_node_or_null("SkillButton/SkillButton") as BaseButton
		ss["inner_button_present"] = inner != null
		if inner != null:
			inner.pressed.emit()
	ss["skill_list_opened"] = await _until(func() -> bool:
		return PopupManager.open_popups.size() == 2 \
				and _top_popup_script_path().ends_with("SkillList.gd"), POPUP_TIMEOUT_FRAMES)
	if bool(ss["skill_list_opened"]):
		var top: Node = PopupManager.open_popups.back()[0]
		var grid: Node = top.get_node_or_null(SKILL_LIST_GRID_PATH)
		var names: Array = []
		if grid != null:
			for opt in grid.get_children():
				var n: Variant = opt.get("skill_name")
				if n != null and str(n) != "":
					names.append(str(n))
		ss["skill_name_list_size"] = names.size()
		ss["skill_names_sample"] = names.slice(0, 8)
	else:
		ss["skill_name_list_size"] = 0

	# close SkillList (Back button path) -> back to SkillSelect only
	PopupManager.pop_popup()
	ss["skill_list_closed"] = await _until(func() -> bool:
		return PopupManager.open_popups.size() == 1 \
				and _top_popup_script_path().ends_with("SkillSelect.gd"), POPUP_TIMEOUT_FRAMES)

	# close SkillSelect itself
	PopupManager.pop_popup()
	ss["closed"] = await _until(func() -> bool:
		return PopupManager.open_popups.is_empty() and not is_instance_valid(popup), POPUP_TIMEOUT_FRAMES)

	ss["pass"] = bool(ss["opened"]) \
			and bool(ss["primary_button_present"]) \
			and bool(ss["name_label_present"]) \
			and int(ss["playable_skill_count"]) > 0 \
			and int(ss["equipped_slot_count"]) > 0 \
			and bool(ss.get("inner_button_present", false)) \
			and bool(ss["skill_list_opened"]) \
			and int(ss["skill_name_list_size"]) > 0 \
			and bool(ss["skill_list_closed"]) \
			and bool(ss["closed"])
	return ss


func _phase_passive_tree() -> Dictionary:
	var pt: Dictionary = {}
	var packed: PackedScene = load(PASSIVE_TREE_SCENE)
	pt["scene_loaded"] = packed != null
	if packed == null:
		pt["pass"] = false
		return pt

	# production entry: instantiate + PopupManager.show_popup (MutationBench path)
	var popup: Node = packed.instantiate()
	PopupManager.show_popup(popup, self)
	pt["opened"] = await _until(func() -> bool:
		return PopupManager.open_popups.size() == 1 \
				and is_instance_valid(popup) and popup.is_inside_tree(), POPUP_TIMEOUT_FRAMES)
	if not bool(pt["opened"]):
		pt["pass"] = false
		return pt

	var nodes_container: Node = popup.get_node_or_null(NODES_PATH)
	var edges_container: Node = popup.get_node_or_null(EDGES_PATH)
	pt["node_count"] = nodes_container.get_child_count() if nodes_container != null else -1
	pt["edge_count"] = edges_container.get_child_count() if edges_container != null else -1
	var pts_label: Node = popup.get_node_or_null(POINTS_LABEL_PATH)
	pt["points_label_text"] = str(pts_label.text) if pts_label != null else ""
	var spec_label: Node = popup.get_node_or_null(SPEC_LABEL_PATH)
	pt["spec_label_text"] = str(spec_label.text) if spec_label != null else ""

	# close via Back button path
	PopupManager.pop_popup()
	pt["closed"] = await _until(func() -> bool:
		return PopupManager.open_popups.is_empty() and not is_instance_valid(popup), POPUP_TIMEOUT_FRAMES)

	pt["pass"] = bool(pt["opened"]) \
			and int(pt["node_count"]) > 0 \
			and int(pt["edge_count"]) > 0 \
			and pt["points_label_text"] != "" \
			and pt["spec_label_text"] != "" \
			and bool(pt["closed"])
	return pt


func _count_residual_dialogs(root: Node) -> int:
	# NOTE: popups are parented to this driver, so its own subtree must be
	# scanned too — do not skip self.
	var found: int = 0
	for child in root.get_children():
		if is_instance_valid(child):
			var s: Script = child.get_script()
			if s != null and s.resource_path.contains("/Popups/"):
				found += 1
			found += _count_residual_dialogs(child)
	return found


func _phase_cleanup() -> Dictionary:
	var cl: Dictionary = {}
	cl["open_popups_empty"] = PopupManager.open_popups.is_empty()
	cl["queued_popups_empty"] = PopupManager.queued_popups.is_empty()
	cl["driver_children_zero"] = get_child_count() == 0
	cl["pause_balanced"] = (not get_tree().paused) and Globals.pause_count == 0
	cl["residual_dialog_nodes"] = _count_residual_dialogs(get_tree().root)
	cl["no_residual_dialogs"] = int(cl["residual_dialog_nodes"]) == 0
	cl["process_alive"] = is_inside_tree() and Time.get_ticks_msec() > 0
	cl["pass"] = bool(cl["open_popups_empty"]) \
			and bool(cl["queued_popups_empty"]) \
			and bool(cl["driver_children_zero"]) \
			and bool(cl["pause_balanced"]) \
			and bool(cl["no_residual_dialogs"]) \
			and bool(cl["process_alive"])
	return cl
