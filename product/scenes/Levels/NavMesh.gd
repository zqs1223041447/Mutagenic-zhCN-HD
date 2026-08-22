extends Node2D
class_name NavMesh

var seen
var points
var navmesh
var cell_size

func test_seen(tile):
				if seen.has(tile[0]):
								if seen[tile[0]].has(tile[1]):
												return seen[tile[0]][tile[1]]
				return false

func mark_seen(tile):
				if seen.has(tile[0]):
								seen[tile[0]][tile[1]] = true
				else:
								seen[tile[0]] = {tile[1]: true}

func get_point(tile):
				if points.has(tile[0]):
								if points[tile[0]].has(tile[1]):
												return points[tile[0]][tile[1]]
				return null

func create_point(tile):
				var point_id = navmesh.get_available_point_id()
				navmesh.add_point(point_id, Vector2(tile[0], tile[1]))
				if points.has(tile[0]):
								points[tile[0]][tile[1]] = point_id
				else:
								points[tile[0]] = {tile[1]: point_id}

func build_navmesh(tiles, cell_size):
				self.cell_size = cell_size
				navmesh = AStar2D.new()
				if len(tiles) == 0:
								# Godot 4 迁移守卫：空瓦片集直接返回，避免 tiles[0] 越界中断 _ready 链。
								print("Building navmesh skipped: no tiles")
								return
				if len(tiles) > 64:
								navmesh.reserve_space(len(tiles))

				seen = {}
				points = {}
				

				
				for tile in tiles:
								create_point(tile)

				var queue = [tiles[0]]
				print("Building navmesh started...")
				
				while not queue.is_empty():
								var tile = queue.pop_front()
								mark_seen(tile)
								var point_id = get_point(tile)
								for i in [ - 1, 1]:
												
												var target_tile = [tile[0] + i, tile[1]]
												var target_point_id = get_point(target_tile)
												if target_point_id != null:
																navmesh.connect_points(point_id, target_point_id)
																if not test_seen(target_tile):
																				mark_seen(target_tile)
																				queue.push_back(target_tile)

												
												target_tile = [tile[0], tile[1] + i]
												target_point_id = get_point(target_tile)
												if target_point_id != null:
																navmesh.connect_points(point_id, target_point_id)
																if not test_seen(target_tile):
																				mark_seen(target_tile)
																				queue.push_back(target_tile)
				print("Building navmesh finished.")


func get_shortest_path_target(start, end):
				
				
				var start_x = floor(start.x / cell_size.x)
				var start_y = floor(start.y / cell_size.y)

				var start_point_id = navmesh.get_closest_point(Vector2(start_x, start_y))

				var end_x = floor(end.x / cell_size.x)
				var end_y = floor(end.y / cell_size.y)

				var end_point_id = navmesh.get_closest_point(Vector2(end_x, end_y))

				var point_path = navmesh.get_point_path(start_point_id, end_point_id)

				
				
				var space_state = get_world_2d().direct_space_state
				for i in range(len(point_path)):
								var node_position = point_path[len(point_path) - i - 1]

								var node_position_in_world = Vector2(node_position.x * cell_size.x, node_position.y * cell_size.y)

								
								var result = space_state.intersect_ray(PhysicsRayQueryParameters2D.create(start, node_position_in_world, 256))

								if not result:
												
												return Vector2(node_position.x * cell_size.x + cell_size.x / 2.0, node_position.y * cell_size.y + cell_size.y / 2.0)

				return null

func get_shortest_path(start, end):
				
				
				var start_x = floor(start.x / cell_size.x)
				var start_y = floor(start.y / cell_size.y)

				var start_point_id = navmesh.get_closest_point(Vector2(start_x, start_y))

				var end_x = floor(end.x / cell_size.x)
				var end_y = floor(end.y / cell_size.y)

				var end_point_id = navmesh.get_closest_point(Vector2(end_x, end_y))

				var point_path = navmesh.get_point_path(start_point_id, end_point_id)

				var world_points = []
				for point in point_path:
								world_points.append(Vector2(point.x * cell_size.x, point.y * cell_size.y))

				return world_points

