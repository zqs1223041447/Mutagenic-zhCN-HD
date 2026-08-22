extends Node

var nodes_in_path = []
var _cached_node = {}

const LEVELS_PER_DISTANCE = 5

func get_distance_to_root(start):
				var queue = [{
								"node": start, 
								"path": [start], 
				}]
				var seen = {}
				seen[start] = true

				while len(queue) > 0:
								var info = queue.pop_front()
								var node = info.node
								var path = info.path

								seen[node] = true

								var neighbors = WorldMapData.get_neighbors(node)

								for n in neighbors:
												
												if seen.has(n):
																continue

												
												var n_path = path.duplicate()
												if not is_node_level_fixed(n):
																n_path.append(n)

												if n == "root":
																return len(n_path)

												
												queue.append({
																"node": n, 
																"path": n_path, 
												})

				return 0

func edge_in_path(a, b):
				return _cached_node.has(a) and _cached_node.has(b)

func is_node_level_fixed(node_id):
				if node_id == "root":
								return false
				var map_name = WorldMapData.get_map_name(node_id)
				return Levels.is_map_fixed_level(map_name)

func get_stage_level(node_id):
				if node_id == "root":
								return 1
				if not WorldMapData.is_node_valid(node_id):
								return 1

				
				var map_name = WorldMapData.get_map_name(node_id)

				if Levels.is_map_fixed_level(map_name):
								return Levels.get_map_zone_level(map_name)

				return max(1, LEVELS_PER_DISTANCE * (WorldMapUtils.get_distance_to_root(node_id) - 2))
