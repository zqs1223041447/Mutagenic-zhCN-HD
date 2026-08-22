extends Node2D

signal portal_spawned
signal level_changed

var player_scene = preload("res://scenes/Player/Player.tscn")
var escape_menu = preload("res://scenes/Popups/EscapeMenu.tscn")
var loadout_menu = preload("res://scenes/Popups/Dialogs/GeneEditor/GeneLoadout.tscn")


var player
var level
var is_switching = false

func _enter_tree() -> void :
				switch_levels(Globals.selected_level, true)

func _ready() -> void :
				Input.connect("joy_connection_changed", Callable(self, "_on_unplug"))
				$GUI.connect("show_info", Callable(self, "_on_show_info"))

func _process(delta: float) -> void :
				if Input.is_action_just_pressed("ui_open_menu"):
								if PopupManager.is_free():
												var menu = escape_menu.instantiate()
												PopupManager.show_popup(menu, self)
				if Input.is_action_just_pressed("ui_open_inventory"):
								if PopupManager.is_free():
												
												var menu = loadout_menu.instantiate()
												PopupManager.show_popup(menu, self)


func _on_show_info():
				var menu = escape_menu.instantiate()
				PopupManager.show_popup(menu, self)

func _on_unplug(device, connected):
				if not connected:
								var menu = escape_menu.instantiate()
								PopupManager.show_popup(menu, self)
								PopupManager.show_popup(menu, self)

func _render_map_mods():
				print(MapMods.get_map_mods())

func switch_levels(stage_id, reset = false, zone_level_override = null):
				var destination = WorldMapData.get_map_name(stage_id)
				
				emit_signal("portal_spawned", null)
				Globals.request_pause()
				if is_switching:
								print("Already switching...")
								return
				
				Globals.stage_kills = 0
				Globals.selected_level = destination
				Globals.zone_level = Levels.config[destination].zone_level


				if zone_level_override != null:
								Globals.zone_level = zone_level_override
				if stage_id == "hideout":
								print("GOING TO HIDEOUT")
								Globals.zone_level = GameState.get_highest_level_completed()

				
				is_switching = true
				print("Switching levels...")

				
				var destination_scene = Levels.config[destination].level_scene

				if destination_scene:
								print("Destination found:", destination)
								$LoadingScreen.visible = true
								if reset:
												print("Resetting World")
												if player:
																print("Freeing existing player")
																player.queue_free()
												Globals.reset()
												GameState.reset_globals()
												player = player_scene.instantiate()
												GameState.set_global("player", player)
												GameState.set_global("level_layer", $Level)
												GameState.set_global("ground", $GroundEffects)
												GameState.set_global("projectiles", $ProjectileLayer)
												GameState.set_global("sky", $SkyLayer)
												GameState.set_global("world", self)
												GameState.set_global("active_stage_id", stage_id)

								Globals.stage_iiq = ZoneScaling.get_iiq_scaler(Globals.zone_level)
								Globals.stage_iir = ZoneScaling.get_iir_scaler(Globals.zone_level)
								print("Removing player")
								
								# Godot 4：Node.is_a_parent_of 已更名 is_ancestor_of
								if $Level.is_ancestor_of(player):
												$Level.remove_child(player)

								print("Clearing Ground")
								
								for child in $GroundEffects.get_children():
												child.queue_free()
								print("Clearing BGC")
								for child in $BackgroundContainer.get_children():
												child.queue_free()
								for child in $ProjectileLayer.get_children():
												child.queue_free()
								print("Clearing Level")
								for child in $Level.get_children():
												child.queue_free()
								print("Clearing FDT")
								for child in $FloatingDamageTexts.get_children():
												child.queue_free()
								for child in $SkyLayer.get_children():
												child.queue_free()

								
								MapMods.reroll_mods(Globals.zone_level)

								level = destination_scene.instantiate()

								
								if destination != "hideout" and level.spawn_mobs:
												var spawnables = MonsterLevels.monsters_in[destination]
												level.spawnables = spawnables
								else:
												level.spawnables = []

								
								GameState.set_global("level_scene", level)

								
								level.connect("status_changed", Callable($LoadingScreen, "on_status_change"))
								level.connect("map_done", Callable(self, "_on_map_loaded"))
								level.connect("map_done", Callable($GUI, "_refresh_on_new_map"))

								$Level.add_child(player)
								$BackgroundContainer.add_child(level)
								$GUI.call_deferred("_on_level_changed")
								emit_signal("level_changed")
								PopupManager.reset()
								Globals.reset_pause()
								Globals.call_deferred("clear_context")
				else:
								print("Failed with no destination scene")
								get_tree().quit()

func _on_map_loaded():
				Globals.release_pause()
				$LoadingScreen.visible = false
				is_switching = false
