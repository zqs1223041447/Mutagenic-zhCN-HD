extends Node

signal allocation_path_changed

var current_target_node_id
var nodes_in_path = []
var _cached_node = {}

func compute_shortest_allocation_path(node_id):
				if current_target_node_id == node_id:
								return
				current_target_node_id = node_id
				nodes_in_path = find_nodes_in_path(node_id)
				_cached_node = {}
				for n in nodes_in_path:
								_cached_node[n] = true
				emit_signal("allocation_path_changed")

func find_nodes_in_path(start):
				var nodes_in_path = bfs(start)
				return nodes_in_path

func bfs(start):
				var queue = [{
								"node": start, 
								"path": [start], 
				}]
				var seen = {}
				seen[start] = true
				seen["root"] = true

				while len(queue) > 0:
								var info = queue.pop_front()
								var node = info.node
								var path = info.path

								seen[node] = true

								var neighbors = PassiveTreeData.get_neighbors(node)

								for n in neighbors:
												
												if seen.has(n):
																continue

												
												var n_path = path.duplicate()
												n_path.append(n)

												
												if GameState.is_passive_allocated(n):
																return n_path

												
												queue.append({
																"node": n, 
																"path": n_path, 
												})

				return []

func clear_shortest_allocation_path():
				current_target_node_id = null
				nodes_in_path = []
				_cached_node = {}
				emit_signal("allocation_path_changed")

func edge_in_path(a, b):
				return _cached_node.has(a) and _cached_node.has(b)
