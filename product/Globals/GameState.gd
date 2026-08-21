extends Node

var notification_message = preload("res://scenes/GUI/NotificationMessage.tscn")

var help_tip = preload("res://scenes/Popups/Dialogs/HelpTip/LevelupTip/LevelupTip.tscn")

signal changed
signal genes_changed
signal stored_mods_changed
signal characters_changed
signal passives_changed
signal gene_loadout_changed
signal skill_loadout_changed
signal tree_changed
signal settings_changed
signal mutation_tier_increased
signal account_xp_changed
signal skills_changed
signal marked_genes_changed
signal stage_completion_changed(stage_id)
signal outfit_changed
signal keybinds_changed
signal help_tips_changed
signal specialization_changed(spec)
signal class_changed(spec)
signal seen_items_changed

var quitting = false

var keystone_cache = {}
var globals_cache = {}

const HASH_VALUES = {
				"UNMODDED": "UNMODDED", 
				"MODDED": "MODDED", 
}


var global_configuration = {
				"save_version": 1, 
				"settings": {
								"enable_music": true, 
								"enable_sfx": true, 
								"enable_drops": true, 
								"enable_floating_damage": true, 
								"enable_fullscreen": true, 
								"enable_fx": true, 
								"enable_status_bars": true, 
								"enable_vsync": true, 
								"enable_stats_panel": true, 
								"enable_health_globe": true, 
								"enable_floating_xp": true, 
								"show_advanced_mods": true, 
								"hide_low_level": false, 
								"volume": {
												"music": 100, 
												"sfx": 100, 
												"drops": 100, 
								}
				}, 
				"shared_stash": {}, 
				"keybind_overrides": {}, 
				"characters": {}, 
				"completed_achievements": [], 
				"timestamp": 0, 
				"checksum": null, 
				"stamp": null
}


var initial_configuration = {
				"character_name": "default", 
				"account_level": 1, 
				"account_xp": 0, 
				"account_xp_next": 50, 
				"next_gene_id": 0, 
				"needs_starter": true, 
				"orbs": {
								"blue": 0, 
								"green": 0, 
								"red": 0, 
								"gold": 0, 
								"freeze": 0, 
								"corruption": 0, 
								"tear": 0, 
								"moon_shard": 0, 
								"sun_shard": 0
				}, 
				"recent_stage": null, 
				"completed_stages": {"root": true}, 
				"outfit": {
								"helmet": null, 
								"head": null, 
								"feet": null, 
								"hands": null, 
								"pants": null, 
								"back": null
				}, 
				"help_tips": {}, 
				"new_item_ids": {}, 
				"new_item_types": {}, 
				"tutorial_events": {}, 
				"mutation_tree_loadout": {"class": null, "passives": []}, 
				"specialization_loadout": {"class": null, "passives": ["root"]}, 
				"skill_loadout": {}, 
				"gene_loadout": {}, 
				"genes": {}, 
				"stored_mods": {}, 
				"filters": {}
}


var saved_stats = {}

var needs_save = false
var last_save = 0.0

func _ready():
				print("GameState getting ready...")
				randomize()
				reset_saved_state()

				if Constants.USE_STEAM:
								Steam.connect("file_read_async_complete", Callable(self, "_on_load"))
								Steam.connect("file_write_async_complete", Callable(self, "_on_save"))

				connect("changed", self, "_on_change")
				connect("settings_changed", self, "_on_change")
				connect("gene_loadout_changed", self, "save_game")
				connect("keybinds_changed", self, "update_ui_keybinds")


func _physics_process(delta: float) -> void :
				last_save -= delta
				if needs_save and last_save <= 0.0:
								last_save = 5.0
								needs_save = false
								print("Doing actual save from debounce")
								do_save_game()

func get_save_name():
				if Constants.USE_STEAM:
								
								return str(Steam.getSteamID()) + "_0_6_0.dat"
								
								
				return "user://_0_6_0.dat"

func quit():
				print("QUITTING")
				quitting = true
				save_game()

func has_save_been_modded(stats, time):
				var test = (str(time) + "/" + HASH_VALUES.UNMODDED).sha256_text()
				return stats.checksum != test and stats.checksum != null

func compute_checksum(stats, old_time):
				if has_save_been_modded(stats, old_time):
								return (str(stats.timestamp) + "/" + HASH_VALUES.MODDED).sha256_text()
				return (str(stats.timestamp) + "/" + HASH_VALUES.UNMODDED).sha256_text()

func mark_modified(stats):
				stats.checksum = (str(stats.timestamp) + "/" + HASH_VALUES.MODDED).sha256_text()

func compute_stamp(stats):
				var to_hash = stats.duplicate(true)
				var timestamp = stats.timestamp
				
				to_hash.erase("timestamp")
				to_hash.erase("stamp")
				var stamp = (str(timestamp) + "/" + JSON.stringify(to_hash, "", true)).sha256_text()
				return stamp

func verify_stamp(stats):
				var correct_stamp = compute_stamp(stats)
				return correct_stamp == stats.stamp

func get_active_stats():
				if saved_stats.characters.has(Globals.selected_character_name):
								return saved_stats.characters[Globals.selected_character_name]
				print("No character found:", Globals.selected_character_name)
				get_tree().quit()

func get_active_spec_name():
				var stats = get_active_stats()
				var spec = stats.specialization_loadout. class 
				if spec:
								return PlayableClasses.specialization_name[spec]
				else:
								
								var cls = stats.mutation_tree_loadout. class 
								return PlayableClasses.class_names[cls]

				return "?"

func save_game(debounce = true):
				if debounce:
								last_save = 5.0
								needs_save = true
				else:
								do_save_game()

func do_save_game():


				var old_time = saved_stats.timestamp
				saved_stats.timestamp = Time.get_unix_time_from_system()
				
				saved_stats.checksum = compute_checksum(saved_stats, old_time)
				
				saved_stats.stamp = compute_stamp(saved_stats)
				var serialized = JSON.stringify(saved_stats, "", true)
				var save_file = get_save_name()
				var data_to_write = serialized.to_utf8()
				if Constants.USE_STEAM:
								Steam.fileWriteAsync(save_file, data_to_write, len(data_to_write))
				else:
								var f = FileAccess.open(save_file, FileAccess.WRITE)
								f.store_string(serialized)
								f.close()
								_on_save(1)

func load_game():
				await FrameTimer.idle_frame(self).timeout
				var save_file = get_save_name()
				if Constants.USE_STEAM:
								if Steam.fileExists(save_file):
												var file_size = Steam.getFileSize(save_file)
												Steam.fileReadAsync(save_file, 0, file_size)
								else:
												print("No save file found")
												get_tree().change_scene_to_file("res://scenes/Menu.tscn")
				else:
								var f = FileAccess.open(save_file, FileAccess.READ)
								if FileAccess.file_exists(save_file):
												var data = f.get_as_text()
												var json = JSON.parse_string(data)
												if json != null and typeof(json) == TYPE_DICTIONARY:
																var modded = false
																if not verify_stamp(json):
																				modded = true
																migrate(saved_stats, json)
																clean_saved_data()
																print("LOADED AND MERGED", JSON.stringify(saved_stats))
																if modded:
																				mark_modified(saved_stats)
												else:
																print("failed to load:", json)
								load_keybinds()
								set_volume_levels()
								get_tree().change_scene_to_file("res://scenes/Menu.tscn")

func _on_load(result):
				if result.result == 1:
								var byte_pool_array = result.buffer
								var as_string = byte_pool_array.get_string_from_utf8()
								var json = JSON.parse_string(as_string)
								if json != null and typeof(json) == TYPE_DICTIONARY:
												var modded = false
												if not verify_stamp(json):
																modded = true
												migrate(saved_stats, json)
												clean_saved_data()
												if modded:
																mark_modified(saved_stats)

												OS.window_fullscreen = saved_stats.settings.enable_fullscreen
												OS.window_maximized = saved_stats.settings.enable_fullscreen
												set_vsync(saved_stats.settings.enable_vsync)
								else:
												print("failed to load:", json)
				else:
								print("File load result:", result)
				load_keybinds()
				set_volume_levels()
				print("Going to menu")
				get_tree().change_scene_to_file("res://scenes/Menu.tscn")

func _on_save(result):
				if result == 1:
								print("Game saved!")
				else:
								print("Failed to save: ", result)

				if quitting:
								print("QUIT")
								get_tree().notification(MainLoop.NOTIFICATION_WM_QUIT_REQUEST)

func reset_saved_state():
				
				saved_stats = global_configuration.duplicate(true)
				set_volume_levels()

func create_new_character(character_name, chosen_class):
				
				if saved_stats.characters.has(character_name):
								return
				add_character(character_name)
				Globals.selected_character_name = character_name
				create_new_gene_loadout()
				create_new_tree(chosen_class)
				create_new_skill_loadout()
				save_game()
				emit_signal("characters_changed")

func create_new_tree(chosen_class):
				var stats = get_active_stats()
				var class_root = PlayableClasses.get_root_node(chosen_class)
				stats.mutation_tree_loadout = {"class": chosen_class, "passives": [class_root]}
				emit_signal("tree_changed")

func delete_character(character_name):
				saved_stats.characters.erase(character_name)
				emit_signal("characters_changed")

func add_character(character_name):
				saved_stats.characters[character_name] = initial_configuration.duplicate(true)
				saved_stats.characters[character_name].character_name = character_name

func reset_game_state():
				var saved_game = get_save_name()
				if Constants.USE_STEAM:
								if Steam.fileExists(saved_game):
												Steam.fileDelete(saved_game)
				else:
								var d = Directory.new()
								d.remove(saved_game)

				
				reset_saved_state()
				load_keybinds()
				get_tree().change_scene_to_file("res://scenes/Menu.tscn")

func set_music_enabled(enabled):
				saved_stats.settings.enable_music = enabled
				emit_signal("settings_changed")

func set_sfx_enabled(enabled):
				saved_stats.settings.enable_sfx = enabled
				emit_signal("settings_changed")

func set_drops_enabled(enabled):
				saved_stats.settings.enable_drops = enabled
				emit_signal("settings_changed")

func set_floating_damage_enabled(enabled):
				saved_stats.settings.enable_floating_damage = enabled
				emit_signal("settings_changed")

func set_floating_xp_enabled(enabled):
				saved_stats.settings.enable_floating_xp = enabled
				emit_signal("settings_changed")

func set_fullscreen(enabled):
				saved_stats.settings.enable_fullscreen = enabled
				OS.window_maximized = enabled
				OS.window_fullscreen = enabled
				emit_signal("settings_changed")

func set_vsync(enabled):
				saved_stats.settings.enable_vsync = enabled
				OS.vsync_enabled = enabled
				if not enabled:
								var refresh_rate = OS.get_screen_refresh_rate()
								if refresh_rate < 0:
												print("Failed to find refresh rate. Setting to 60 fps target")
												refresh_rate = 60.0
								print("Setting refresh rate to ", refresh_rate, " fps")
								Engine.set_target_fps(60)
				emit_signal("settings_changed")

func set_fx(enabled):
				saved_stats.settings.enable_fx = enabled
				emit_signal("settings_changed")

func set_status_bars(enabled):
				saved_stats.settings.enable_status_bars = enabled
				emit_signal("settings_changed")

func set_globes(enabled):
				saved_stats.settings.enable_health_globe = enabled
				emit_signal("settings_changed")

func set_stats_panel(enabled):
				saved_stats.settings.enable_stats_panel = enabled
				emit_signal("settings_changed")

func set_advanced_mods(enabled):
				saved_stats.settings.show_advanced_mods = enabled
				emit_signal("settings_changed")

func set_hide_low_level(enabled):
				saved_stats.settings.hide_low_level = enabled
				emit_signal("settings_changed")

func apply_settings_to_music():
				set_volume_levels()

func _on_change():
				apply_settings_to_music()

func needs_starter():
				var stats = get_active_stats()
				return stats.account_xp == 0 and stats.account_level == 1 and stats.needs_starter

func set_starter_build(template_id):
				var stats = get_active_stats()
				var template = StarterBuilds.templates[template_id]
				stats.skill_loadout = template.loadout.duplicate(true)
				stats.needs_starter = false
				emit_signal("skill_loadout_changed")

func migrate(current, saved):
				current.characters = saved.characters
				for c in current.characters:
								print(current.characters[c].mutation_tree_loadout)
								merge_in_saved_data(current.characters[c], initial_configuration)
								if current.characters[c].mutation_tree_loadout.has("class"):
												if current.characters[c].mutation_tree_loadout. class == null:
																current.characters.erase(c)
								if current.characters.has(c):
												if current.characters[c].specialization_loadout.has("class"):
																var spec = current.characters[c].specialization_loadout. class 
																if not PlayableClasses.PLAYABLE_SPECIALIZATIONS.keys().has(spec):
																				print("Reset class as it was not found: ", spec)
																				current.characters[c].specialization_loadout. class = null

				merge_in_saved_data(current, saved, "", "characters", true)

func merge_in_saved_data(current, new, path = "", ignore = null, override = false):
				for key in new:
								if ignore and key == ignore:
												continue
								var current_path = path + "-" + key
								if current.has(key):
												if typeof(new[key]) == TYPE_DICTIONARY and typeof(current[key]) == TYPE_DICTIONARY:
																merge_in_saved_data(current[key], new[key], current_path, ignore, override)
												elif override:
																current[key] = new[key]
								else:
												current[key] = new[key]

func clean_saved_data():
				Genes.verify()
				verify_current_trees()
				verify_current_skills()
				save_game(false)
				emit_signal("changed")

func get_account_level():
				var stats = get_active_stats()
				return stats.account_level

func get_orb_count(orb_type):
				var stats = get_active_stats()
				if orb_type == Constants.OrbType.BLUE:
								return stats.orbs.blue
				if orb_type == Constants.OrbType.RED:
								return stats.orbs.red
				if orb_type == Constants.OrbType.GREEN:
								return stats.orbs.green
				if orb_type == Constants.OrbType.GOLD:
								return stats.orbs.gold
				if orb_type == Constants.OrbType.CORRUPTION:
								return stats.orbs.corruption

				return 0

func remove_orbs(orb_type, amount):
				var stats = get_active_stats()
				if orb_type == Constants.OrbType.BLUE:
								stats.orbs.blue -= amount
				if orb_type == Constants.OrbType.RED:
								stats.orbs.red -= amount
				if orb_type == Constants.OrbType.GREEN:
								stats.orbs.green -= amount
				if orb_type == Constants.OrbType.GOLD:
								stats.orbs.gold -= amount
				if orb_type == Constants.OrbType.CORRUPTION:
								stats.orbs.corruption -= amount

				emit_signal("changed")

func is_fx_enabled():
				return saved_stats.settings.enable_fx

func is_status_bars_enabled():
				return saved_stats.settings.enable_status_bars

func get_current_tree():
				var stats = get_active_stats()
				return stats.mutation_tree_loadout

func get_current_specialization_tree():
				var stats = get_active_stats()
				return stats.specialization_loadout

func change_specialization(spec):
				var stats = get_active_stats()
				stats.specialization_loadout = {"class": spec, "passives": ["root"]}
				emit_signal("passives_changed")
				emit_signal("specialization_changed", spec)

func change_class(spec):
				var stats = get_active_stats()
				create_new_tree(spec)
				stats.specialization_loadout = {"class": null, "passives": ["root"]}
				emit_signal("passives_changed")
				emit_signal("class_changed", spec)

func reset_passives():
				var tree = get_current_tree()
				if tree:
								tree.passives = [PlayableClasses.get_root_node(tree. class )]
				var s_tree = get_current_specialization_tree()
				if s_tree:
								s_tree.passives = ["root"]

				emit_signal("passives_changed")


func is_passive_allocated(node_id):
				var tree = get_current_tree()
				if tree:
								return tree.passives.has(node_id)
				return false

func is_specialization_passive_allocated(node_id):
				var tree = get_current_specialization_tree()
				if tree:
								return tree.passives.has(node_id)
				return false

func get_allocated_count():
				var tree = get_current_tree()
				if tree:
								return len(tree.passives) - 1
				return 0

func get_allocated_specialization_count():
				var tree = get_current_specialization_tree()
				if tree:
								return len(tree.passives) - 1
				return 0

func get_max_allocated_count():
				var stats = get_active_stats()
				return stats.account_level - 1

func get_max_specialization_allocated_count():
				var stats = get_active_stats()
				return min(4, floor(stats.account_level / 30.0))

func get_available_passives():
				return get_max_allocated_count() - get_allocated_count()

func get_available_specialization_passives():
				return get_max_specialization_allocated_count() - get_allocated_specialization_count()

func can_allocate_passive(node_id):
				var tree = get_current_tree()
				if not tree:
								return false
				
				if tree.passives.has(node_id):
								return false

				
				if get_allocated_count() >= get_max_allocated_count():
								return false

				
				var nodes_found = {}
				for node in tree.passives:
								nodes_found[node] = true

				for edge in PassiveTreeData.edge_data[node_id]:
								if nodes_found.has(edge):
												return true

				
				return false

func can_allocate_specialization_passive(node_id):
				var tree = get_current_specialization_tree()
				if not tree:
								return false
				
				if tree.passives.has(node_id):
								return false

				
				if get_allocated_specialization_count() >= get_max_specialization_allocated_count():
								return false

				
				var nodes_found = {}
				for node in tree.passives:
								nodes_found[node] = true

				var edge_data = SpecializationData.tree_data[tree. class ].edges
				for edge in edge_data[node_id]:
								if nodes_found.has(edge):
												return true

				
				return false

func can_remove_passive(node_id):
				var tree = get_current_tree()
				if not tree:
								return false
				var tag = PassiveTreeData.get_tag(node_id)
				if node_id == "root" or "root" in tag:
								return false

				var edges_for_node = {}
				
				for e in PassiveTreeData.tree_data.edges:
								var a = e[0]
								var b = e[1]
								if edges_for_node.has(a):
												edges_for_node[a].append(b)
								else:
												edges_for_node[a] = [b]

								if edges_for_node.has(b):
												edges_for_node[b].append(a)
								else:
												edges_for_node[b] = [a]

				
				var allocated_nodes = {}
				for node in tree.passives:
								
								if node == node_id:
												continue
								allocated_nodes[node] = true

				
				var nodes_seen = {
								"root": true
				}

				
				var queue = ["root"]

				
				var remaining_connected_count = 0

				
				while not queue.empty():
								var next = queue.pop_back()

								
								remaining_connected_count += 1

								
								if edges_for_node.has(next):
												for node in edges_for_node[next]:
																
																if node == node_id:
																				continue
																
																if nodes_seen.has(node):
																				continue
																if not allocated_nodes.has(node):
																				continue
																nodes_seen[node] = true
																queue.append(node)

				
				return remaining_connected_count == get_allocated_count()

func can_remove_specialization_passive(node_id):
				var tree = get_current_specialization_tree()
				if not tree:
								return false
				var tag = SpecializationData.get_tag(tree. class , node_id)
				if node_id == "root" or "root" in tag:
								return false

				var edges_for_node = {}
				
				for e in SpecializationData.loaded_data[tree. class ].edges:
								var a = e[0]
								var b = e[1]
								if edges_for_node.has(a):
												edges_for_node[a].append(b)
								else:
												edges_for_node[a] = [b]

								if edges_for_node.has(b):
												edges_for_node[b].append(a)
								else:
												edges_for_node[b] = [a]

				
				var allocated_nodes = {}
				for node in tree.passives:
								
								if node == node_id:
												continue
								allocated_nodes[node] = true

				
				var nodes_seen = {
								"root": true
				}

				
				var queue = ["root"]

				
				var remaining_connected_count = 0

				
				while not queue.empty():
								var next = queue.pop_back()

								
								remaining_connected_count += 1

								
								if edges_for_node.has(next):
												for node in edges_for_node[next]:
																
																if node == node_id:
																				continue
																
																if nodes_seen.has(node):
																				continue
																if not allocated_nodes.has(node):
																				continue
																nodes_seen[node] = true
																queue.append(node)

				
				return remaining_connected_count == get_allocated_specialization_count()

func allocate_path():
				var tree = get_current_tree()
				if not tree:
								return false
				var nodes_to_allocate = PassiveTreeUtils.nodes_in_path.duplicate()
				nodes_to_allocate.invert()
				var did_allocate = false
				for node_id in nodes_to_allocate:
								if can_allocate_passive(node_id):
												tree.passives.append(node_id)
												did_allocate = true
				if did_allocate:
								emit_signal("passives_changed")
								Achievements.queue_achievement("GROWING_STRONGER")
								return true
				return false

func allocate_specialization_path():
				var tree = get_current_specialization_tree()
				if not tree:
								return false
				var nodes_to_allocate = SpecializationTreeUtils.nodes_in_path.duplicate()
				nodes_to_allocate.invert()
				var did_allocate = false
				for node_id in nodes_to_allocate:
								if can_allocate_specialization_passive(node_id):
												tree.passives.append(node_id)
												did_allocate = true
				if did_allocate:
								emit_signal("passives_changed")
								Achievements.queue_achievement("GROWING_STRONGER")
								return true
				return false

func disconnect_path_at(node_id):
				var tree = get_current_tree()
				if not tree:
								return false
				if node_id in tree.passives:
								tree.passives.erase(node_id)
								tree.passives = get_connected_nodes()
								emit_signal("passives_changed")
								return true
				return false

func disconnect_specialization_path_at(node_id):
				var tree = get_current_specialization_tree()
				if not tree:
								return false
				if node_id in tree.passives:
								tree.passives.erase(node_id)
								tree.passives = get_connected_specialization_nodes()
								emit_signal("passives_changed")
								return true
				return false

func get_connected_nodes():
				var nodes_connected = {}
				var stats = get_active_stats()
				var class_root = stats.mutation_tree_loadout. class 
				var stack = [PlayableClasses.get_root_node(class_root)]
				var nodes_seen = {"root": true}
				nodes_seen[class_root] = true
				while len(stack) > 0:
								var node = stack.pop_back()
								if is_passive_allocated(node):
												nodes_connected[node] = true
								else:
												continue
								for n in PassiveTreeData.get_neighbors(node):
												if nodes_seen.has(n):
																continue
												nodes_seen[n] = true
												stack.append(n)

				var passives_to_keep = nodes_connected.keys()
				return passives_to_keep

func get_connected_specialization_nodes():
				var tree = get_current_specialization_tree()
				if tree and tree. class == null:
								return ["root"]
				var nodes_connected = {}
				var stats = get_active_stats()
				var stack = ["root"]
				var nodes_seen = {"root": true}
				nodes_seen["root"] = true
				while len(stack) > 0:
								var node = stack.pop_back()
								if is_specialization_passive_allocated(node):
												nodes_connected[node] = true
								else:
												continue
								for n in SpecializationData.get_neighbors(tree. class , node):
												if nodes_seen.has(n):
																continue
												nodes_seen[n] = true
												stack.append(n)

				var passives_to_keep = nodes_connected.keys()
				return passives_to_keep

func are_passives_allocated(node_a, node_b):
				var tree = get_current_tree()
				if not tree:
								return false
				
				var ps = tree.passives
				return ps.has(node_a) and ps.has(node_b)

func are_specialization_passives_allocated(node_a, node_b):
				var tree = get_current_specialization_tree()
				if not tree:
								return false
				
				var ps = tree.passives
				return ps.has(node_a) and ps.has(node_b)

func collect_passive_tree_buffs():
				var result = {}
				var conditionals = {}
				var keystones = []

				
				var tree = get_current_tree()
				if tree:
								for node in tree.passives:
												if node == "root":
																continue
												if "root" in node:
																continue
												var passive_config = PassiveTreeData.get_node_config(node)
												var buffs = passive_config.stats

												
												for item in buffs:
																var stat = item.stat


																var type = item.scaling_type
																var amount = item.amount
																if item.has("tags"):
																				for tag in item.tags:
																								if not conditionals.has(tag):
																												conditionals[tag] = {}
																								if not conditionals[tag].has(stat):
																												conditionals[tag][stat] = {}

																								if conditionals[tag][stat].has(type):
																												if type == Constants.ScalingType.FLAT:
																																conditionals[tag][stat][type] += amount
																												if type == Constants.ScalingType.PERCENT:
																																conditionals[tag][stat][type] += amount
																												if type == Constants.ScalingType.MORE:
																																conditionals[tag][stat][type] *= 1.0 + amount
																								else:
																												if type == Constants.ScalingType.FLAT:
																																conditionals[tag][stat][type] = amount
																												if type == Constants.ScalingType.PERCENT:
																																conditionals[tag][stat][type] = amount
																												if type == Constants.ScalingType.MORE:
																																conditionals[tag][stat][type] = 1.0 + amount
																else:
																				if not result.has(stat):
																								result[stat] = {}
																				if result[stat].has(type):
																								if type == Constants.ScalingType.FLAT:
																												result[stat][type] += amount
																								if type == Constants.ScalingType.PERCENT:
																												result[stat][type] += amount
																								if type == Constants.ScalingType.MORE:
																												result[stat][type] *= 1.0 + amount
																				else:
																								if type == Constants.ScalingType.FLAT:
																												result[stat][type] = amount
																								if type == Constants.ScalingType.PERCENT:
																												result[stat][type] = amount
																								if type == Constants.ScalingType.MORE:
																												result[stat][type] = 1.0 + amount

												
												if passive_config.has("keystones"):
																for k in passive_config.keystones:
																				if not keystones.has(k):
																								keystones.append(k)

				var s_tree = get_current_specialization_tree()
				if s_tree:
								for node in s_tree.passives:
												if node == "root":
																continue
												if "root" in node:
																continue
												var passive_config = SpecializationData.get_node_config(s_tree. class , node)
												var buffs = passive_config.stats

												
												for item in buffs:
																var stat = item.stat
																var type = item.scaling_type
																var amount = item.amount
																if item.has("tags"):
																				for tag in item.tags:
																								if not conditionals.has(tag):
																												conditionals[tag] = {}
																								if not conditionals[tag].has(stat):
																												conditionals[tag][stat] = {}

																								if conditionals[tag][stat].has(type):
																												if type == Constants.ScalingType.FLAT:
																																conditionals[tag][stat][type] += amount
																												if type == Constants.ScalingType.PERCENT:
																																conditionals[tag][stat][type] += amount
																												if type == Constants.ScalingType.MORE:
																																conditionals[tag][stat][type] *= 1.0 + amount
																								else:
																												if type == Constants.ScalingType.FLAT:
																																conditionals[tag][stat][type] = amount
																												if type == Constants.ScalingType.PERCENT:
																																conditionals[tag][stat][type] = amount
																												if type == Constants.ScalingType.MORE:
																																conditionals[tag][stat][type] = 1.0 + amount
																else:
																				if not result.has(stat):
																								result[stat] = {}
																				if result[stat].has(type):
																								if type == Constants.ScalingType.FLAT:
																												result[stat][type] += amount
																								if type == Constants.ScalingType.PERCENT:
																												result[stat][type] += amount
																								if type == Constants.ScalingType.MORE:
																												result[stat][type] *= 1.0 + amount
																				else:
																								if type == Constants.ScalingType.FLAT:
																												result[stat][type] = amount
																								if type == Constants.ScalingType.PERCENT:
																												result[stat][type] = amount
																								if type == Constants.ScalingType.MORE:
																												result[stat][type] = 1.0 + amount

												
												if passive_config.has("keystones"):
																for k in passive_config.keystones:
																				if not keystones.has(k):
																								keystones.append(k)

				
				for stat in result:
								if result[stat].has(Constants.ScalingType.MORE):
												result[stat][Constants.ScalingType.MORE] -= 1.0

				
				for tag in conditionals:
								for stat in conditionals[tag]:
												if conditionals[tag][stat].has(Constants.ScalingType.MORE):
																conditionals[tag][stat][Constants.ScalingType.MORE] -= 1.0
				return {
								"stats": result, 
								"conditional_stats": conditionals, 
								"keystones": keystones
				}

func collect_gene_loadout_buffs():
				var result = {}
				var conditionals = {}
				var keystones = []
				var stats = get_active_stats()
				var loadout = stats.gene_loadout

				if loadout:
								for gene_type in loadout.keys():
												for slot in loadout[gene_type]:

																var gene_id = loadout[gene_type][slot]
																if not gene_id:
																				continue
																var gene = GameState.get_gene(gene_id)

																if not gene:
																				continue

																var gene_mods = Genes.mods_for_base_type(gene.type)
																var drop_only_gene_mods = Genes.drop_only_mods_for_base_type(gene.type)

																var quality_multiplier = 1.0
																if gene.has("quality"):
																				quality_multiplier = 1.0 + gene.quality / 100.0


																var all_mods = []
																for mod in gene.implicits:
																				all_mods.append(mod.duplicate(true))
																for mod in gene.prefixes:
																				all_mods.append(mod.duplicate(true))
																for mod in gene.suffixes:
																				all_mods.append(mod.duplicate(true))
																for mod in all_mods:
																				var mod_configs = gene_mods
																				if mod.drop_only:
																								mod_configs = drop_only_gene_mods
																				if mod.has("keystone"):
																								keystones.append(mod.keystone)
																								continue
																				var stat = mod.stat
																				if not result.has(stat):
																								result[stat] = {}
																				var item = mod_configs.calculate_effective_stat(mod)
																				var type = item.type
																				var amount = item.amount * quality_multiplier

																				if item.has("tags"):
																								for tag in item.tags:
																												if not conditionals.has(tag):
																																conditionals[tag] = {}
																												if not conditionals[tag].has(stat):
																																conditionals[tag][stat] = {}

																												if conditionals[tag][stat].has(type):
																																if type == Constants.ScalingType.FLAT:
																																				conditionals[tag][stat][type] += amount
																																if type == Constants.ScalingType.PERCENT:
																																				conditionals[tag][stat][type] += amount
																																if type == Constants.ScalingType.MORE:
																																				conditionals[tag][stat][type] *= 1.0 + amount
																												else:
																																if type == Constants.ScalingType.FLAT:
																																				conditionals[tag][stat][type] = amount
																																if type == Constants.ScalingType.PERCENT:
																																				conditionals[tag][stat][type] = amount
																																if type == Constants.ScalingType.MORE:
																																				conditionals[tag][stat][type] = 1.0 + amount
																				else:
																								if result[stat].has(type):
																												if type == Constants.ScalingType.FLAT:
																																result[stat][type] += amount
																												if type == Constants.ScalingType.PERCENT:
																																result[stat][type] += amount
																												if type == Constants.ScalingType.MORE:
																																result[stat][type] *= 1.0 + amount
																								else:
																												if type == Constants.ScalingType.FLAT:
																																result[stat][type] = amount
																												if type == Constants.ScalingType.PERCENT:
																																result[stat][type] = amount
																												if type == Constants.ScalingType.MORE:
																																result[stat][type] = 1.0 + amount

				
				for stat in result:
								if result[stat].has(Constants.ScalingType.MORE):
												result[stat][Constants.ScalingType.MORE] -= 1.0

				
				for tag in conditionals:
								for stat in conditionals[tag]:
												if conditionals[tag][stat].has(Constants.ScalingType.MORE):
																conditionals[tag][stat][Constants.ScalingType.MORE] -= 1.0

				var key_hash = {}
				for key in keystones:
								key_hash[key] = true
				var gene_result = {
								"stats": result, 
								"conditional_stats": conditionals, 
								"keystones": key_hash.keys()
				}

				return gene_result

func compute_xp_for_stage(next_level):
				var req = 50
				for i in range(next_level):
								req = req * 1.12 + 15
				return floor(req)

func add_account_xp(amount):
				var stats = get_active_stats()
				if stats.account_level >= 150:
								return stats.account_level
				stats.account_xp += amount
				var did_level_up = false
				while stats.account_xp >= stats.account_xp_next and stats.account_level < 150:
								stats.account_xp -= stats.account_xp_next
								stats.account_xp_next = compute_xp_for_stage(stats.account_level + 1)
								stats.account_level += 1
								did_level_up = true
								emit_signal("mutation_tier_increased")
				emit_signal("account_xp_changed")
				if did_level_up:
								if not GameState.is_help_tip_read("level_up"):
												GameState.mark_help_tip_read("level_up")
												var popup = help_tip.instantiate()
												PopupManager.show_popup(popup, get_tree().get_root().get_node("World"))

								if stats.account_level >= 10:
												Achievements.queue_achievement("LEVEL_10")
								if stats.account_level >= 20:
												Achievements.queue_achievement("LEVEL_20")
								if stats.account_level >= 30:
												Achievements.queue_achievement("LEVEL_30")
								if stats.account_level >= 40:
												Achievements.queue_achievement("LEVEL_40")
								if stats.account_level >= 50:
												Achievements.queue_achievement("LEVEL_50")
								if stats.account_level >= 60:
												Achievements.queue_achievement("LEVEL_60")
								if stats.account_level >= 70:
												Achievements.queue_achievement("LEVEL_70")
								if stats.account_level >= 80:
												Achievements.queue_achievement("LEVEL_80")
								if stats.account_level >= 90:
												Achievements.queue_achievement("LEVEL_90")
								if stats.account_level >= 100:
												Achievements.queue_achievement("LEVEL_100")
								if stats.account_level >= 110:
												Achievements.queue_achievement("LEVEL_110")
								if stats.account_level >= 120:
												Achievements.queue_achievement("LEVEL_120")
								if stats.account_level >= 130:
												Achievements.queue_achievement("LEVEL_130")
								if stats.account_level >= 140:
												Achievements.queue_achievement("LEVEL_140")
								if stats.account_level >= 150:
												Achievements.queue_achievement("LEVEL_150")

				return stats.account_level


func reset_globals():
				globals_cache = {}

func set_global(key, item):
				globals_cache[key] = item

func get_global(key, default = null):
				if key in globals_cache:
								return globals_cache[key]
				return default

func verify_passives(passives):
				var stats = get_active_stats()
				
				
				if len(passives) > stats.account_level:
								print("too many", len(passives), stats.account_level)
								return false

				
				var seen = {}
				var passive_lookup = {}

				for node in passives:
								seen[node] = false
								passive_lookup[node] = true




				var queue = ["root"]
				seen["root"] = true
				while not queue.empty():
								var node = queue.pop_back()


								
								for n in PassiveTreeData.get_neighbors(node):
												
												if seen.has(n) and seen[n] == true:
																continue
												
												if not passive_lookup.has(n):
																continue

												seen[n] = true
												queue.append(n)

				
				for node in seen:
								if not seen[node]:
												false

				
				return true

func verify_current_trees():
				for character in saved_stats.characters:
								print("Verifying trees for character:", character)
								Globals.selected_character_name = character
								var stats = get_active_stats()
								var tree = stats.mutation_tree_loadout
								tree.passives = get_connected_nodes()
								tree = stats.specialization_loadout
								tree.passives = get_connected_specialization_nodes()
								print("DONE Verify")

func verify_current_skills():
				for character in saved_stats.characters:
								print("Verifying trees for character:", character)
								Globals.selected_character_name = character
								var stats = get_active_stats()
								var template = generate_new_skill_loadout()
								var active_skills = stats.skill_loadout
								
								for slot_name in template.keys():
												if active_skills.has(slot_name):
																
																print("Slot found:", slot_name, " Check Supports")
																
																for support_name in active_skills[slot_name].supports.keys():
																				if template[slot_name].supports.has(support_name):
																								continue
																				print("Erasing", support_name)
																				active_skills[slot_name].supports.erase(support_name)

																
																for support_name in template[slot_name].supports.keys():
																				if active_skills[slot_name].supports.has(support_name):
																								continue
																				print("Adding missing: ", support_name)
																				active_skills[slot_name].supports[support_name] = template[slot_name].supports[support_name]
												else:
																print("Adding missing skill slot", slot_name)
																active_skills[slot_name] = template[slot_name].duplicate(true)
								for slot_name in active_skills.keys():
												if template.has(slot_name):
																continue
												active_skills.erase(slot_name)
								print("Done skill merge")

func create_new_gene_loadout():
				var stats = get_active_stats()
				stats.gene_loadout = {
								Genes.GeneSlot.WEAPON: {"slot_1": null, "slot_2": null}, 
								Genes.GeneSlot.BODY: {"slot_1": null}, 
								Genes.GeneSlot.HELMET: {"slot_1": null}, 
								Genes.GeneSlot.PANTS: {"slot_1": null}, 
								Genes.GeneSlot.GLOVES: {"slot_1": null}, 
								Genes.GeneSlot.BOOTS: {"slot_1": null}, 
								Genes.GeneSlot.BELT: {"slot_1": null}, 
								Genes.GeneSlot.AMULET: {"slot_1": null}, 
								Genes.GeneSlot.RING: {"slot_1": null, "slot_2": null}, 
								Genes.GeneSlot.MINOR: {"slot_1": null, "slot_2": null, "slot_3": null, "slot_4": null, "slot_5": null, "slot_6": null, "slot_7": null, "slot_8": null}, 
				}
				emit_signal("gene_loadout_changed")

func get_gene(gene_id):
				var stats = get_active_stats()
				if stats.genes.has(gene_id):
								return stats.genes[gene_id]
				return null

func get_genes_of_slot(slot_type):
				var stats = get_active_stats()
				var ids = []
				for id in stats.genes.keys():
								if Genes.slot_for_base(stats.genes[id].type) == slot_type:
												ids.append(id)
				return ids

func get_shared_genes_of_slot(slot_type):
				var ids = []
				for id in saved_stats.shared_stash.keys():
								if Genes.slot_for_base(saved_stats.shared_stash[id].type) == slot_type:
												ids.append(id)
				return ids

func get_genes_of_type(type):
				var stats = get_active_stats()
				var ids = []
				for id in stats.genes.keys():
								if stats.genes[id].type == type:
												ids.append(id)
				return ids

func get_all_gene_ids():
				return get_active_stats().genes.keys()

func equip_gene(slot_type, slot_name, gene_id):
				var stats = get_active_stats()
				if not stats.genes.has(gene_id):
								return false
				var gene = stats.genes[gene_id]
				if Genes.slot_for_base(gene.type) != slot_type:
								return false
				var loadout = stats.gene_loadout
				if not loadout.has(slot_type):
								return false
				if not loadout[slot_type].has(slot_name):
								return false

				
				loadout[slot_type][slot_name] = gene_id
				emit_signal("gene_loadout_changed")

func is_gene_equipped(gene_id):
				var stats = get_active_stats()
				if not stats.genes.has(gene_id):
								return false

				var loadout = stats.gene_loadout
				if not loadout:
								return false

				for type in loadout:
								for slot in loadout[type]:
												if loadout[type][slot] == gene_id:
																return true

				return false

func is_gene_new(gene_id):
				var stats = get_active_stats()
				return stats.new_item_ids.has(gene_id)

func is_gene_type_new(type):
				var stats = get_active_stats()
				return stats.new_item_types.has(type)

func mark_gene_seen(gene_id):
				var stats = get_active_stats()
				stats.new_item_ids.erase(gene_id)
				emit_signal("seen_items_changed")

func mark_gene_type_seen(type):
				var stats = get_active_stats()
				stats.new_item_types.erase(type)
				emit_signal("seen_items_changed")

func unequip_gene(slot_type, slot_name):
				var stats = get_active_stats()
				var loadout = stats.gene_loadout
				if not loadout.has(slot_type):
								return false
				if not loadout[slot_type].has(slot_name):
								return false
				print("Gene unequipped!")
				
				loadout[slot_type][slot_name] = null
				emit_signal("gene_loadout_changed")

func equip_skill(skill, slot):
				var eq = get_equipped_skills()
				if not is_skill_equipped(skill):
								eq[slot].skill = skill
								clear_supports(slot)
								emit_signal("skills_changed")
								save_game()
				else:
								
								var existing_slot = get_slot_with_skill(skill)
								eq[existing_slot].skill = null
								eq[slot].skill = skill
								clear_supports(slot)
								clear_supports(existing_slot)
								emit_signal("skills_changed")
								save_game()

func get_slot_with_skill(skill):
				if skill == null:
								return null
				var eq = get_equipped_skills()
				for slot in eq:
								if eq[slot].skill == skill:
												return slot
				return null

func is_skill_equipped(skill):
				if skill == null:
								return false
				var eq = get_equipped_skills()
				for slot in eq:
								if eq[slot].skill == skill:
												return true
				return false

func is_slot_equipped(slot):
				var eq = get_equipped_skills()
				return eq[slot].skill != null

func equip_support(skill_slot, support_slot, support):
				var eq = get_equipped_skills()
				eq[skill_slot].supports[support_slot] = support
				emit_signal("skills_changed")
				save_game()

func clear_supports(skill_slot):
				var eq = get_equipped_skills()
				for slot in eq[skill_slot].supports:
								eq[skill_slot].supports[slot] = null

func is_support_equipped(skill_slot, support):
				if skill_slot == null:
								return false
				if support == null:
								return false
				var eq = get_equipped_skills()
				for slot in eq[skill_slot].supports:
								if eq[skill_slot].supports[slot] == support:
												return true
				return false

func is_support_allowed(skill_slot, support):
				
				
				
				var eq = get_equipped_skills()
				var skill = eq[skill_slot].skill
				if skill:
								
								var tags = Skills.config[skill].tags
								var support_info = SkillSupports.supports[support]
								if support_info.has("tags"):
												var support_tags = support_info.tags
												
												for tag in support_tags:
																if not tags.has(tag):
																				return false
												return true
								else:
												
												return true

				
				print("skill not found -- error:", skill_slot, support)
				return false

func is_support_slot_equipped(skill_slot, support_slot):
				var stats = get_active_stats()
				return stats.skill_loadout[skill_slot].supports[support_slot] != null

func complete_stage(stage_id):
				var stats = get_active_stats()
				if not stats.completed_stages.has(stage_id):
								stats.completed_stages[stage_id] = true
								emit_signal("stage_completion_changed", stage_id)

func remove_outfit(slot):
				var stats = get_active_stats()
				stats.outfit[slot] = null
				save_game()
				emit_signal("outfit_changed")

func is_outfit_equipped(slot, item):
				var stats = get_active_stats()
				return stats.outfit[slot] == item

func equip_outfit(slot, item):
				var stats = get_active_stats()
				stats.outfit[slot] = item
				save_game()
				emit_signal("outfit_changed")

func save_recent_stage(stage_id):
				var stats = get_active_stats()
				stats.recent_stage = stage_id

func mark_help_tip_read(tip_id):
				var stats = get_active_stats()
				stats.help_tips[tip_id] = true
				emit_signal("help_tips_changed")

func is_help_tip_read(tip_id):
				var stats = get_active_stats()
				return stats.help_tips.has(tip_id)

func mark_tutorial_event_done(event_id):
				var stats = get_active_stats()
				stats.tutorial_events[event_id] = true

func is_tutorial_event_done(event_id):
				var stats = get_active_stats()
				return stats.tutorial_events.has(event_id)

func generate_new_skill_loadout():
				return {
								"primary": {
												"skill": null, 
												"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
								}, 
								"secondary": {
												"skill": null, 
												"supports": {"a": null, "b": null, "c": null, "d": null}, 
								}, 
								"support_one": {
												"skill": null, 
												"supports": {"a": null, "b": null, "c": null, "d": null}, 
								}, 
								"support_two": {
												"skill": null, 
												"supports": {"a": null, "b": null}, 
								}, 
								"support_three": {
												"skill": null, 
												"supports": {"a": null}, 
								}, 
								"support_four": {
												"skill": null, 
												"supports": {"a": null}, 
								}, 
				}

func create_new_skill_loadout():
				var stats = get_active_stats()
				stats.skill_loadout = generate_new_skill_loadout()

				emit_signal("skill_loadout_changed")

func get_current_gene_loadout():
				return get_active_stats().gene_loadout

func get_equipped_skills():
				var stats = get_active_stats()
				return stats.skill_loadout

func set_keybind(action, event):
				saved_stats.keybind_overrides[action] = event.physical_scancode
				for ev in InputMap.get_action_list(action):
								if ev is InputEventKey:
												InputMap.action_erase_event(action, ev)
				var new_event = InputEventKey.new()
				new_event.physical_scancode = event.physical_scancode
				InputMap.action_add_event(action, new_event)
				emit_signal("keybinds_changed")

func get_keybind(action):
				if saved_stats.keybind_overrides.has(action):
								return OS.get_scancode_string(saved_stats.keybind_overrides[action])
				return "Unassigned"

func load_keybinds():
				for action in Keybindings.configurable_actions:
								if saved_stats.keybind_overrides.has(action):
												if typeof(saved_stats.keybind_overrides[action]) != TYPE_REAL:
																saved_stats.keybind_overrides.erase(action)
				for action in Keybindings.configurable_actions:
								if saved_stats.keybind_overrides.has(action):
												
												for event in InputMap.get_action_list(action):
																if event is InputEventKey:
																				InputMap.action_erase_event(action, event)
												
												var new_event = InputEventKey.new()
												if saved_stats.keybind_overrides[action]:
																new_event.physical_scancode = saved_stats.keybind_overrides[action]
																InputMap.action_add_event(action, new_event)
								else:
												var events = InputMap.get_action_list(action)
												for event in events:
																if event is InputEventKey:
																				saved_stats.keybind_overrides[action] = event.physical_scancode
				emit_signal("keybinds_changed")

func update_ui_keybinds():
				for ui_action in Keybindings.ui_map:
								InputMap.action_erase_events(ui_action)
								for event in InputMap.get_action_list(Keybindings.ui_map[ui_action]):
												InputMap.action_add_event(ui_action, event)
				save_game()

func set_sfx_volume(amount):
				saved_stats.settings.volume.sfx = amount
				set_volume_levels()

func set_music_volume(amount):
				saved_stats.settings.volume.music = amount
				set_volume_levels()

func set_drops_volume(amount):
				saved_stats.settings.volume.drops = amount
				set_volume_levels()

func set_volume_levels():
				if saved_stats.settings.volume.music == 0:
								AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"), true)
				elif saved_stats.settings.enable_music:
								AudioServer.set_bus_mute(AudioServer.get_bus_index("Music"), false)

				if saved_stats.settings.volume.sfx == 0:
								AudioServer.set_bus_mute(AudioServer.get_bus_index("SFX"), true)
				elif saved_stats.settings.enable_sfx:
								AudioServer.set_bus_mute(AudioServer.get_bus_index("SFX"), false)

				if saved_stats.settings.volume.drops == 0:
								AudioServer.set_bus_mute(AudioServer.get_bus_index("Drops"), true)
				elif saved_stats.settings.enable_drops:
								AudioServer.set_bus_mute(AudioServer.get_bus_index("Drops"), false)

				AudioServer.set_bus_volume_db(AudioServer.get_bus_index("SFX"), - 18.0 + 18.0 * saved_stats.settings.volume.sfx / 100.0)
				AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), - 18.0 + 18.0 * saved_stats.settings.volume.music / 100.0)
				AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Drops"), - 18.0 + 18.0 * saved_stats.settings.volume.drops / 100.0)



func move_to_shared_stash(gene_id):
				
				var active_stats = get_active_stats()
				if active_stats.genes.has(gene_id):
								var cloned_gene = active_stats.genes[gene_id]
								Genes.delete_gene(gene_id, false)
								var all_ids = saved_stats.shared_stash.keys()
								var highest_id = - 1
								for key in all_ids:
												highest_id = max(highest_id, float(key))
								var new_shared_id = highest_id + 1
								cloned_gene.id = new_shared_id
								saved_stats.shared_stash[new_shared_id] = cloned_gene
								emit_signal("genes_changed")

func move_to_local_stash(gene_id):
				
				if saved_stats.shared_stash.has(gene_id):
								var cloned_gene = saved_stats.shared_stash[gene_id]
								saved_stats.shared_stash.erase(gene_id)
								var next_id = Genes.get_next_id()
								cloned_gene.id = next_id
								var active_stats = get_active_stats()
								active_stats.genes[next_id] = cloned_gene
								emit_signal("genes_changed")

func get_highest_level_completed():
				var highest = 0
				for node_id in get_active_stats().completed_stages.keys():
								var zone_level = WorldMapUtils.get_stage_level(node_id)
								highest = max(highest, zone_level)
				return highest

