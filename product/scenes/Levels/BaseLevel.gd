extends Node2D
class_name BaseLevel

signal status_changed(message)
signal map_done
signal portal_spawned(location)

var spawn_location_scene = preload("res://scenes/Levels/SpawnLocation.tscn")

@onready var player = GameState.get_global("player")
@onready var level = GameState.get_global("level_layer")
@onready var ground_layer = GameState.get_global("ground")
@onready var navmesh = $NavMesh
@onready var tiles = $TileMap
@onready var minimap = $Minimap

@export var min_distance_from_player = 300.0
@export var max_distance_from_player = 600.0
@export var min_tiles_from_player = 8
@export var max_spawns = 100
@export var mobs_per_spawn = 3
@export var spawn_mobs = true

var level_duration = 0.0
var spawnable_tiles = {}
var potential_tiles = {}
var nav_tiles = {}
var cached_spawnable_tiles = []
var cached_away_from_origin = []
var cached_nav_tiles = null
var spawnables = []
var spawn_load_counter = 0
var mobs_out_of_tree = []
var mobs_to_re_add = []
var layout


func connect_points(start: Vector2, target: Vector2, hollow: bool, expansion: int, square: bool = false):
				var x0 = start.x
				var y0 = start.y
				var dx = abs(target.x - start.x)
				var dy = - abs(target.y - start.y)
				var sx = - 1
				if target.x > start.x:
								sx = 1
				var sy = - 1
				if target.y > start.y:
								sy = 1
				var error = dx + dy
				var cell_movement_count = 0
				var needed_expansion = expansion
				expand_cell(start, expansion, hollow, square)
				if not square:
								
								while true:
												if cell_movement_count == needed_expansion:
																needed_expansion = expand_cell(Vector2(x0, y0), expansion, hollow, square)
																cell_movement_count = 0
												else:
																cell_movement_count += 1
												if x0 == target.x and y0 == target.y:
																break
												var e2 = 2 * error
												if e2 >= dy:
																if x0 == target.x:
																				break
																error += dy
																x0 += sx
												if e2 <= dx:
																if y0 == target.y:
																				break
																error += dx
																y0 += sy
				else:
								
								while x0 != target.x:
												expand_cell(Vector2(x0, y0), expansion, hollow, square)
												x0 += sx
								while y0 != target.y:
												expand_cell(Vector2(x0, y0), expansion, hollow, square)
												y0 += sy
				if not square:
								expand_cell(target, expansion, hollow, square)

func expand_cell(cell: Vector2, variance: int, hollow: bool, square: bool):
				var expansion = max(4, variance / 2) + randi() % (variance - 1)
				for i in range( - expansion, expansion + 1):
								for j in range( - expansion, expansion + 1):
												if ((cell + Vector2(i, j)).distance_squared_to(cell) <= expansion * expansion) or square:
																set_potential_tile(cell.x + i, cell.y + j, true)

				if expansion > 6 and hollow:
								
								for i in range( - expansion / 3, expansion / 3 + 1):
												for j in range( - expansion / 3, expansion / 3 + 1):
																if ((cell + Vector2(i, j)).distance_squared_to(cell) <= expansion) or square:
																				set_potential_tile(cell.x + i, cell.y + j, false)

				return max(1, expansion / 3)

func has_potential_tile(x, y):
				if potential_tiles.has(x):
								if potential_tiles[x].has(y):
												return potential_tiles[x][y]
				return false

func set_potential_tile(x, y, used = true):
				if potential_tiles.has(x):
								potential_tiles[x][y] = used
				else:
								potential_tiles[x] = {y: used}

func get_potential_neighbor_count_all(x, y):
				var neighbor_count = 0

				for i in [ - 1, 0, 1]:
								for j in [ - 1, 0, 1]:
												if i == 0 and j == 0:
																continue
												if has_potential_tile(x + i, y + j):
																neighbor_count += 1

				return neighbor_count

func get_potential_neighbor_count(x, y):
				var neighbor_count = 0

				for i in [ - 1, 1]:
								if has_potential_tile(x + i, y):
												neighbor_count += 1

				for j in [ - 1, 1]:
								if has_potential_tile(x, y + j):
												neighbor_count += 1

				return neighbor_count

func is_potential_tile_valid(x, y):
				
				var has_hor_neighbor = false
				for i in [ - 1, 1]:
								if has_potential_tile(x + i, y):
												has_hor_neighbor = true

				var has_vert_neighbor = false
				for i in [ - 1, 1]:
								if has_potential_tile(x, y + i):
												has_vert_neighbor = true

				if not has_vert_neighbor or not has_hor_neighbor:
								return false

				var n_count = get_potential_neighbor_count(x, y)
				if n_count <= 1:
								return false

				for i in [ - 1, 1]:
								if get_potential_neighbor_count(x + i, y) == 4:
												if n_count >= 2:
																return true

				for j in [ - 1, 1]:
								if get_potential_neighbor_count(x, y + j) == 4:
												if n_count >= 2:
																return true
				return false

func get_all_potential_tiles():
				var t = []
				for x in potential_tiles:
								for y in potential_tiles[x]:
												if potential_tiles[x][y] == true:
																t.append([x, y])

				return t

func clean_potential_tiles():
				var clean_tiles_added = 0
				for i in range(1):
								var tiles_to_enable = get_all_potential_tiles()
								var tiles_to_remove = []
								for tile in tiles_to_enable:
												if not is_potential_tile_valid(tile[0], tile[1]):
																tiles_to_remove.append(tile)
								for tile in tiles_to_remove:
												for j in [ - 1, 1]:
																if not has_potential_tile(tile[0] + j, tile[1]):
																				if get_potential_neighbor_count(tile[0] + j, tile[1]) > 1:
																								set_potential_tile(tile[0] + j, tile[1], true)
																								clean_tiles_added += 1
																if not has_potential_tile(tile[0], tile[1] + j):
																				if get_potential_neighbor_count(tile[0], tile[1] + j) > 1:
																								set_potential_tile(tile[0], tile[1] + j, true)
																								clean_tiles_added += 1

				print("Clean tiles added: ", clean_tiles_added)

func set_spawnable_tile(x, y, used = true):
				if spawnable_tiles.has(x):
								spawnable_tiles[x][y] = used
				else:
								spawnable_tiles[x] = {y: used}

func is_spawnable_tile(x, y):
				if spawnable_tiles.has(x):
								if spawnable_tiles[x].has(y):
												return spawnable_tiles[x][y]
				return false

func set_nav_tile(x, y, used = true):
				if nav_tiles.has(x):
								nav_tiles[x][y] = used
				else:
								nav_tiles[x] = {y: used}

func is_nav_tile(x, y):
				if nav_tiles.has(x):
								if nav_tiles[x].has(y):
												return nav_tiles[x][y]
				return false

func is_border_tile(x, y):
				return has_potential_tile(x, y) and not is_spawnable_tile(x, y) and get_potential_neighbor_count(x, y) > 0

func get_bounds():
				var min_x = INF
				var min_y = INF
				var max_x = - INF
				var max_y = - INF
				var all_tiles = get_all_potential_tiles()
				for tile in all_tiles:
								if is_border_tile(tile[0], tile[1]):
												min_x = min(min_x, tile[0])
												min_y = min(min_y, tile[1])
												max_x = max(max_x, tile[0])
												max_y = max(max_y, tile[1])

				return [min_x, min_y, max_x, max_y]

func get_spawnable_neighbor_count(x, y):
				var neighbor_count = 0

				for i in [ - 1, 1]:
								if is_spawnable_tile(x + i, y):
												neighbor_count += 1

				for j in [ - 1, 1]:
								if is_spawnable_tile(x, y + j):
												neighbor_count += 1

				return neighbor_count

func get_spawnable_neighbor_count_for_nav(x, y):
				var neighbor_count = 0

				for i in [ - 1, 0, 1]:
								for j in [ - 1, 0, 1]:
												if is_spawnable_tile(x + i, y + j):
																neighbor_count += 1

				return neighbor_count

func get_all_spawnable_tiles():
				if len(cached_spawnable_tiles) > 0:
								return cached_spawnable_tiles
				var t = []
				for x in spawnable_tiles:
								for y in spawnable_tiles[x]:
												t.append([x, y])
				cached_spawnable_tiles = t
				return t

func get_spawnable_away_from_origin():
				if len(cached_away_from_origin) > 0:
								return cached_away_from_origin
				var tiles = get_all_spawnable_tiles()
				var filtered = []
				for t in tiles:
								if Vector2(t[0], t[1]).length() > min_tiles_from_player:
												filtered.append(t)

				cached_away_from_origin = filtered

				return filtered

func get_spawnable_tiles_near_position(pos, max_dist = INF):
				var x_step = tiles.cell_size.x
				var y_step = tiles.cell_size.y

				var current_x = round(pos.x / x_step)
				var current_y = round(pos.y / y_step)
				var seen = {}
				var queue = [[[current_x, current_y], 0]]
				var tile_options = []

				seen[str(current_x) + "-" + str(current_y)] = true

				while not queue.empty():
								var next = queue.pop_front()
								var current_tile = next[0]
								var current_distance = next[1]

								if current_distance >= max_dist:
												continue

								if current_distance < max_dist and is_spawnable_tile(current_tile[0], current_tile[1]):
												
												tile_options.append(current_tile)

								for i in [ - 1, 1]:
												var x_key = str(current_tile[0] + i) + "-" + str(current_tile[1])
												var y_key = str(current_tile[0]) + "-" + str(current_tile[1] + i)
												if not seen.has(x_key) and is_spawnable_tile(current_tile[0] + i, current_tile[1]):
																seen[x_key] = true
																queue.append([[current_tile[0] + i, current_tile[1]], current_distance + 1])

												if not seen.has(y_key) and is_spawnable_tile(current_tile[0], current_tile[1] + i):
																seen[y_key] = true
																queue.append([[current_tile[0], current_tile[1] + i], current_distance + 1])

				return tile_options

func get_random_spawn_location_in_tile(tile_x, tile_y):
				var x_step = tiles.cell_size.x
				var y_step = tiles.cell_size.y

				return [tile_x * x_step + randf() * x_step, tile_y * y_step + randf() * y_step]

func initialize_navmesh():
				navmesh.build_navmesh(get_all_spawnable_tiles(), Vector2(tiles.cell_size.x, tiles.cell_size.y))
				Globals.navmesh = navmesh

func process_tiles():
				emit_signal("status_changed", "Cleaning Level...")

				clean_potential_tiles()

				emit_signal("status_changed", "Computing Spawns...")
				var final_tiles = get_all_potential_tiles()
				var tile_to_set = tiles.tile_set.get_tiles_ids()[0]
				for tile in final_tiles:
								tiles.set_cell(tile[0], tile[1], tile_to_set)
				tiles.update_bitmask_region()

				
				for tile in final_tiles:
								if get_potential_neighbor_count_all(tile[0], tile[1]) == 8:
												set_spawnable_tile(tile[0], tile[1])

				emit_signal("status_changed", "Computing Navigation System...")
				initialize_navmesh()
				emit_signal("status_changed", "Spawning Genes...")

func read_tiles():
				var tiles_existing = tiles.get_used_cells()
				for tile in tiles_existing:
								set_potential_tile(tile.x, tile.y, true)
				process_tiles()

func _ready():
				Globals.navmesh = navmesh
				PopupManager.reset()
				Globals.reset()

				$TileMap.tile_set.tile_set_texture(0, Levels.get("config")[Globals.selected_level].tileset)

				if GameState.saved_stats.settings.enable_music:
								$AudioStreamPlayer.playing = true

				await FrameTimer.idle_frame(self).timeout

				emit_signal("status_changed", "Spawning Monsters...")

				await FrameTimer.idle_frame(self).timeout
				if spawn_mobs and not Levels.is_current_level_ladder():
								create_spawn_locations()

func get_layout_generator():
				var stage_id = GameState.get_global("active_stage_id")
				return Levels.get_layout_for_stage_id(stage_id)

func _exit_tree() -> void :
				for child in mobs_out_of_tree:
								if child.get_ref():
												child.get_ref().queue_free()

func _physics_process(delta: float) -> void :
				level_duration += delta

				if len(mobs_to_re_add) > 0:
								var last = mobs_to_re_add.pop_back()
								level.call_deferred("add_child", last)

func create_spawn_locations():
				
				var to_spawn = max_spawns
				var tile_options = get_spawnable_away_from_origin()
				var max_options = len(tile_options)
				for i in range(min(max_options, to_spawn)):
								var location = randi() % len(tile_options)
								var tile = tile_options[location]
								create_spawn_location(tile)
								tile_options.remove(location)
								if i % 4 == 0:
												await FrameTimer.idle_frame(self).timeout
				print("Done")

func create_spawn_location(tile):
				var spawn_location = spawn_location_scene.instantiate()
				spawn_location.mobs_to_spawn = min(7, floor(mobs_per_spawn + Globals.zone_level / 50))
				var spawn_position = get_random_spawn_location_in_tile(tile[0], tile[1])

				spawn_location.connect("computed_spawn", Callable(self, "increment_load"))

				level.add_child(spawn_location)
				spawn_location.global_position.x = round(spawn_position[0])
				spawn_location.global_position.y = round(spawn_position[1])

func increment_load():
				spawn_load_counter += 1
				emit_signal("status_changed", "Generating Level: " + str(round((float(spawn_load_counter) / max_spawns) * 100.0)) + "%")
				if spawn_load_counter == max_spawns:
								emit_signal("map_done")

func spawn_cluster(tile_options, amount):
				var spawnables = get_spawnables()
				var mob_to_spawn = spawnables[randi() % len(spawnables)]

				if typeof(mob_to_spawn) == TYPE_ARRAY:
								
								mob_to_spawn = mob_to_spawn[randi() % len(mob_to_spawn)]

				var make_elite = randf() < ZoneScaling.get_rare_monster_chance(Globals.zone_level)
				var make_magic = randf() < 0.2 and not make_elite
				var monster_mods = []
				if make_magic:
								monster_mods = MonsterMods.choose(1)
				elif make_elite:
								
								monster_mods = MonsterMods.choose(3)
				for i in range(amount):
								spawn(tile_options, mob_to_spawn, i == 0 and make_elite, make_magic, monster_mods)
								await FrameTimer.idle_frame(self).timeout

func spawn(tile_options, mob_to_spawn, make_elite = false, make_magic = false, monster_mods = []):
				if len(tile_options) == 0:
								return

				var tile_to_spawn = tile_options[randi() % len(tile_options)]
				var spawned_mob = mob_to_spawn.instantiate()

				if make_elite:
								
								spawned_mob.is_elite = true
								spawned_mob.monster_mods = monster_mods
				if make_magic:
								spawned_mob.is_magic = true
								spawned_mob.monster_mods = monster_mods

				var spawn_position = get_random_spawn_location_in_tile(tile_to_spawn[0], tile_to_spawn[1])
				level.add_child(spawned_mob)
				spawned_mob.global_position.x = round(spawn_position[0])
				spawned_mob.global_position.y = round(spawn_position[1])


func spawn_cluster_in_ladder(x, y, amount, wave = 1):
				var spawnables = get_spawnables()
				var mob_to_spawn = spawnables[randi() % len(spawnables)]

				if typeof(mob_to_spawn) == TYPE_ARRAY:
								
								mob_to_spawn = mob_to_spawn[randi() % len(mob_to_spawn)]

				var make_elite = randf() < 0.05
				var make_magic = randf() < 0.1 and not make_elite
				var monster_mods = []
				if make_magic:
								monster_mods = MonsterMods.choose(1)
				elif make_elite:
								
								monster_mods = MonsterMods.choose(3)
				for i in range(amount):
								spawn_in_ladder(x, y, mob_to_spawn, i == 0 and make_elite, make_magic, monster_mods, wave)

func spawn_in_ladder(x, y, mob_to_spawn, make_elite = false, make_magic = false, monster_mods = [], wave = 1):
				var spawned_mob = mob_to_spawn.instantiate()

				if make_elite:
								
								spawned_mob.is_elite = true
								spawned_mob.monster_mods = monster_mods
				if make_magic:
								spawned_mob.is_magic = true
								spawned_mob.monster_mods = monster_mods

				spawned_mob.wave = wave
				level.add_child(spawned_mob)
				spawned_mob.global_position.x = x - 64 + randf() * 128
				spawned_mob.global_position.y = y - 64 + randf() * 128


func get_spawnables():
				return []

func recompute_cached_tiles() -> void :
				cached_spawnable_tiles = get_all_spawnable_tiles()

func _on_MobDisabler_timeout() -> void :
				recompute_far_mobs()

func recompute_far_mobs():
				
				var mobs_to_keep_disabled = []

				for mob in level.get_children():
								if not mob.is_in_group("enemies"):
												continue
								
								if mob.global_position.distance_to(player.global_position) > 1500:
												mobs_to_keep_disabled.append(weakref(mob))
												mob.last_global_position = mob.global_position
												level.call_deferred("remove_child", mob)

				
				for mobref in mobs_out_of_tree:
								
								if mobref.get_ref():
												if mobref.get_ref().last_global_position.distance_to(player.global_position) < 1200:
																mobs_to_re_add.append(mobref.get_ref())
												else:
																mobs_to_keep_disabled.append(mobref)
								else:
												print("REFERENCE DEAD")

				
				mobs_out_of_tree = mobs_to_keep_disabled

