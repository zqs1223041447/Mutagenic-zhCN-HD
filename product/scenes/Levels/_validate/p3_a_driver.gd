extends Node
## P3-A probe driver: E1 (LoadGame -> character selectable/selected)
## + E8 (do_save_game -> read back -> load_game roundtrip).
##
## Launched as a positional scene so autoloads register exactly like a normal
## boot. The driver immediately swaps itself out of the current_scene slot
## (dummy anchor) so the real LoadGame -> Menu transitions cannot free it.
## Results are printed as one JSON line wrapped in P3A_RESULT_JSON<<< >>> and
## parsed by scripts/validate/run_p3_a_character_save.py.
##
## The user save file is backed up before any mutation and restored on exit.

const CHAR_NAME: String = "P3ProbeChar"
const CHAR_CLASS: String = "MAGE"
const MARKER: String = "P3_PROBE_RESULT:"
const MENU_TIMEOUT_FRAMES: int = 1800
const POPUP_TIMEOUT_FRAMES: int = 300
const WATCHDOG_SECONDS: float = 240.0

var results: Dictionary = {"task": "P3-A", "e1": {}, "e8": {}}
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
	results["pass"] = false
	results["finished"] = true
	print(MARKER + JSON.stringify(results))
	get_tree().quit(3)


func _collect_failed_checks(phase: Dictionary, prefix: String) -> Array:
	var failed: Array = []
	for k in phase.keys():
		if phase[k] is bool and not phase[k]:
			failed.append(prefix + "." + str(k))
	return failed


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


func _is_menu() -> bool:
	var cs := get_tree().current_scene
	return cs != null and cs.scene_file_path.ends_with("Menu.tscn")


func _class_of(stats: Dictionary) -> String:
	var mt: Variant = stats.get("mutation_tree_loadout", {})
	if typeof(mt) == TYPE_DICTIONARY:
		return str(mt.get("class", ""))
	return ""


func _orchestrate() -> void:
	# --- bootstrap the real boot chain: LoadGame becomes current_scene ---
	# Wait one frame first: adding children to root during initial scene
	# setup fails with "parent busy"; after a frame it is safe, and doing it
	# synchronously lets us claim the current_scene slot before load_game()'s
	# deferred scene change fires.
	await get_tree().process_frame
	var lg: Node = (load("res://scenes/LoadGame.tscn") as PackedScene).instantiate()
	get_tree().root.add_child(lg)
	get_tree().current_scene = lg

	var e1: Dictionary = await _phase_e1()
	results["e1"] = e1
	var e8: Dictionary = await _phase_e8(e1)
	results["e8"] = e8
	results["pass"] = bool(e1.get("pass")) and bool(e8.get("pass"))
	results["errors"] = _collect_failed_checks(e1, "e1") + _collect_failed_checks(e8, "e8")
	results["finished"] = true
	_restore_save()
	print(MARKER + JSON.stringify(results))
	await get_tree().process_frame
	get_tree().quit(0 if bool(results["pass"]) else 2)


func _phase_e1() -> Dictionary:
	var e1: Dictionary = {}
	e1["menu_arrived"] = await _until(_is_menu, MENU_TIMEOUT_FRAMES)
	if not bool(e1["menu_arrived"]):
		e1["pass"] = false
		return e1

	var menu: Node = get_tree().current_scene
	var btn: BaseButton = menu.get_node_or_null("CenterContainer/VBoxContainer/CenterContainer/VBoxContainer/StartButton") as BaseButton
	e1["start_button_present"] = btn != null
	if btn == null:
		e1["pass"] = false
		return e1

	btn.pressed.emit()
	e1["popup_opened"] = await _until(func() -> bool: return PopupManager.open_popups.size() > 0, POPUP_TIMEOUT_FRAMES)
	if not bool(e1["popup_opened"]):
		e1["pass"] = false
		return e1

	var popup: Node = PopupManager.open_popups.back()[0]
	var popup_script: Script = popup.get_script()
	var popup_path: String = popup_script.resource_path if popup_script else ""
	e1["popup_is_character_select"] = popup_path.contains("CharacterSelect")

	e1["preexisting_character_count"] = GameState.saved_stats.characters.keys().size()
	if not GameState.saved_stats.characters.has(CHAR_NAME):
		GameState.create_new_character(CHAR_NAME, CHAR_CLASS)
		await _until(func() -> bool: return GameState.saved_stats.characters.has(CHAR_NAME), 120)
	e1["probe_character_created"] = GameState.saved_stats.characters.has(CHAR_NAME)

	var list: Node = popup.get_node_or_null("MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CharacterList")
	e1["slot_count_after_create"] = list.get_child_count() if list else -1

	Globals.selected_character_name = CHAR_NAME
	e1["selected"] = GameState.saved_stats.characters.has(Globals.selected_character_name)
	if bool(e1["selected"]):
		var st: Dictionary = GameState.get_active_stats()
		e1["active_identity_matches"] = str(st.get("character_name", "")) == CHAR_NAME
		e1["active_class"] = _class_of(st)

	e1["pass"] = bool(e1["start_button_present"]) \
			and bool(e1["popup_opened"]) \
			and bool(e1["popup_is_character_select"]) \
			and bool(e1["probe_character_created"]) \
			and bool(e1["selected"]) \
			and bool(e1.get("active_identity_matches", false))
	return e1


func _phase_e8(e1: Dictionary) -> Dictionary:
	var e8: Dictionary = {}
	if not bool(e1.get("selected")):
		e8["skipped_reason"] = "e1_not_selected"
		e8["pass"] = false
		return e8

	var snap: Dictionary = JSON.parse_string(JSON.stringify(GameState.saved_stats.characters[CHAR_NAME]))
	var save_path: String = GameState.get_save_name()
	var ts_before: float = float(GameState.saved_stats.get("timestamp", 0.0))

	GameState.do_save_game()

	var raw: String = ""
	if FileAccess.file_exists(save_path):
		var f := FileAccess.open(save_path, FileAccess.READ)
		if f:
			raw = f.get_as_text()
	var parsed: Variant = JSON.parse_string(raw) if raw != "" else null
	e8["file_nonempty"] = raw != ""
	e8["file_parses"] = typeof(parsed) == TYPE_DICTIONARY

	if typeof(parsed) == TYPE_DICTIONARY:
		var chars: Variant = parsed.get("characters", {})
		if typeof(chars) == TYPE_DICTIONARY and chars.has(CHAR_NAME):
			var c: Dictionary = chars[CHAR_NAME]
			e8["identity_written"] = str(c.get("character_name", "")) == CHAR_NAME
			e8["class_written"] = _class_of(c) == _class_of(snap)
			e8["level_written"] = int(c.get("account_level", -1)) == int(snap.get("account_level", -2))
			e8["xp_written"] = int(c.get("account_xp", -1)) == int(snap.get("account_xp", -2))
			e8["timestamp_advanced"] = float(parsed.get("timestamp", 0.0)) >= ts_before

			var pos_keys: Array = []
			for k in c.keys():
				var kl: String = str(k).to_lower()
				if kl.contains("position") or kl.contains("location") or kl == "pos":
					pos_keys.append(str(k))
			e8["position_like_keys"] = pos_keys
			e8["position_schema_note"] = "product save schema defines no player-position field; roundtrip anchored on identity/class/account_level/account_xp"

			# reload through the real load path. NOTE: current_scene is already
			# Menu here, so waiting for a Menu transition cannot work — wait for
			# the merged data itself (migrate runs before load_game's scene swap).
			GameState.reset_saved_state()
			GameState.load_game()
			e8["reloaded_character_present"] = await _until(func() -> bool:
				return GameState.saved_stats.characters.has(CHAR_NAME), MENU_TIMEOUT_FRAMES)
			e8["reload_menu_arrived"] = await _until(_is_menu, POPUP_TIMEOUT_FRAMES)
			var reloaded: Variant = GameState.saved_stats.get("characters", {}).get(CHAR_NAME)
			if typeof(reloaded) == TYPE_DICTIONARY:
				e8["roundtrip_identity"] = str(reloaded.get("character_name", "")) == CHAR_NAME
				e8["roundtrip_class"] = _class_of(reloaded) == _class_of(snap)
				e8["roundtrip_level"] = int(reloaded.get("account_level", -1)) == int(snap.get("account_level", -2))
				e8["roundtrip_xp"] = int(reloaded.get("account_xp", -1)) == int(snap.get("account_xp", -2))

	e8["pass"] = bool(e8.get("file_nonempty")) \
			and bool(e8.get("file_parses")) \
			and bool(e8.get("identity_written")) \
			and bool(e8.get("class_written")) \
			and bool(e8.get("level_written")) \
			and bool(e8.get("xp_written")) \
			and bool(e8.get("reload_menu_arrived")) \
			and bool(e8.get("reloaded_character_present")) \
			and bool(e8.get("roundtrip_identity")) \
			and bool(e8.get("roundtrip_class")) \
			and bool(e8.get("roundtrip_level")) \
			and bool(e8.get("roundtrip_xp"))
	return e8
