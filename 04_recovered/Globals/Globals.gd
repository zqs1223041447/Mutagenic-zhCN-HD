extends Node

signal change_input(is_mouse)
signal search_changed(value)
signal run_time_expired
signal context_changed(text)
signal context_entity_changed(entity)
signal show_notification(child)
signal show_message(text)

var sound_effect = preload("res://Scenes/SoundEffect.tscn")
var rare_orb_sfx = preload("res://Sounds/Pickups/rare_orb.wav")

var selected_character_name = "default"
var selected_level = null
var zone_level = 1
var waves_completed = 0
var last_wave_time = 0.0
var elapsed_time = 0.0
var time_until_last_clear = 0.0
var kill_count = 0
var navmesh = null
var use_controllers = false
var needs_unpause = false

var search_string = ""
var pause_count = 0


var current_context_instance = null
var current_context_text = ""
var current_context_entity = null


var current_stage = 0
var stage_times = []
var stage_kills = 0
var stage_iiq = 0.0
var stage_iir = 0.0

var STEAM_USERNAME

func _ready():
				randomize()
				pause_mode = Node.PAUSE_MODE_PROCESS

				if Constants.USE_STEAM:
								_initialize_Steam()
								Steam.connect("overlay_toggled", self, "_on_overlay")

func request_pause():
				pause_count += 1
				if pause_count > 0:
								get_tree().paused = true

func release_pause():
				pause_count -= 1
				if pause_count <= 0:
								pause_count = 0
								get_tree().paused = false

func _on_overlay(toggled, _other, _other2):
				if toggled:
								request_pause()
				else:
								release_pause()

func _process(delta: float) -> void :
				if Constants.USE_STEAM:
								Steam.run_callbacks()

				if Input.is_action_just_pressed("ui_screenshot"):
								print("Taking screenshot")
								var image = get_viewport().get_texture().get_data()
								image.flip_y()
								image.save_png("user://mutagenic_screenshot_%d.png" % OS.get_ticks_msec())

				if pause_count <= 0:
								elapsed_time += delta

func _input(event: InputEvent) -> void :
				if event is InputEventMouseButton:
								use_controllers = false
								Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
								emit_signal("change_input", true)
				if event is InputEventMouseMotion:
								use_controllers = false
								Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
								emit_signal("change_input", true)
				if event is InputEventJoypadButton:
								use_controllers = true
								Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)
								emit_signal("change_input", false)
				if event is InputEventJoypadMotion:
								use_controllers = true
								Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)
								emit_signal("change_input", false)

func _initialize_Steam():
				var INIT: Dictionary = Steam.steamInit()
				print("Did Steam initialize?: " + str(INIT))
				if INIT["status"] != 1:
								print("Failed to initialize Steam. " + str(INIT["verbal"]) + " Shutting down...")
								

				var IS_ONLINE: bool = Steam.loggedOn()
				var STEAM_ID: int = Steam.getSteamID()
				var IS_OWNED: bool = Steam.isSubscribed()
				STEAM_USERNAME = Steam.getPersonaName()

				if IS_OWNED == false:
							print("User does not own this game")
							

				Achievements.initialize()
				Leaderboard.initialize()
				MtxManager.initialize()
				yield(Leaderboard, "loaded")
				print("Steam initialized!")

func _on_upload(success, score, changed, new_rank, old_rank):
				print("UPLOADED -----------------------")

func is_using_controller():
				return use_controllers

func _notification(what: int) -> void :
				if what == MainLoop.NOTIFICATION_WM_QUIT_REQUEST:
								if Constants.USE_STEAM:
												print("Shutting down Steam")
												if use_controllers:
																Steam.inputShutdown()
								print("Quit received")
								get_tree().quit()
				if what == MainLoop.NOTIFICATION_CRASH:
								print("CRASHED")

func reset():
				current_stage = 0
				stage_times = []
				elapsed_time = 0.0
				last_wave_time = 0.0
				waves_completed = 0
				stage_iiq = 0.0
				stage_iir = 0.0

func reset_pause():
				pause_count = 0
				get_tree().paused = false

func compute_score():
				return max(0, floor(10000 * Globals.waves_completed - Globals.last_wave_time))

func get_zone_level():
				return zone_level

func get_zone_scaled_xp():
				return ZoneScaling.get_xp_scaler(zone_level)

func get_elapsed_time():
				return Utils.render_time(elapsed_time)

func play_sound_effect(stream, bus = "SFX"):
				if bus == "SFX":
								if GameState.saved_stats.settings.enable_sfx:
												var sfx = sound_effect.instance()
												sfx.stream = stream
												sfx.bus = bus
												get_tree().get_root().add_child(sfx)
				if bus == "Drops":
								if GameState.saved_stats.settings.enable_drops:
												var sfx = sound_effect.instance()
												sfx.stream = stream
												sfx.bus = bus
												get_tree().get_root().add_child(sfx)

func update_search(text):
				search_string = text.to_lower()
				emit_signal("search_changed", search_string)

func set_context(instance, value):
				current_context_instance = instance
				current_context_text = value
				emit_signal("context_changed", value)

func remove_context(instance):
				if current_context_instance == instance:
								current_context_instance = null
								current_context_text = ""
								emit_signal("context_changed", "")

func clear_context():
				current_context_instance = null
				current_context_text = ""
				emit_signal("context_changed", "")

func set_context_entity(entity):
				current_context_entity = entity
				emit_signal("context_entity_changed", entity)

func remove_context_entity(entity):
				if current_context_entity == entity:
								current_context_entity = null
								emit_signal("context_entity_changed", null)

func clear_context_entity():
				current_context_entity = null
				emit_signal("context_entity_changed", null)

func show_notification(child):
				emit_signal("show_notification", child)

func show_message(text):
				emit_signal("show_message", text)

func play_orb_sound(orb_type):
				if orb_type == Constants.OrbType.GOLD or orb_type == Constants.OrbType.CORRUPTION:
								Globals.play_sound_effect(rare_orb_sfx)


func set_rich_presence_zone(zone_level):
				if Constants.USE_STEAM:
								
								Steam.setRichPresence("steam_display", "#Status_InZone")
								Steam.setRichPresence("player_level", str(GameState.get_active_stats().account_level))
								Steam.setRichPresence("player_class", str(GameState.get_active_spec_name()))
								Steam.setRichPresence("zone_level", str(zone_level))

func set_rich_presence_hideout():
				if Constants.USE_STEAM:
								
								Steam.setRichPresence("steam_display", "#Status_InHideout")

func set_rich_presence_ladder():
				if Constants.USE_STEAM:
								
								Steam.setRichPresence("steam_display", "#Status_ChallengeLadder")

func set_rich_presence_menu():
				if Constants.USE_STEAM:
								
								Steam.setRichPresence("steam_display", "#Status_InMenu")
