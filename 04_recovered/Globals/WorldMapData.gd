extends Node

var tree_data
var node_data = {}
var edge_data = {}

func _load_json_data():
				var f = File.new()
				var datafile = "res://world_map_data/map.json"
				f.open(datafile, File.READ)
				if f.file_exists(datafile):
								var data = f.get_as_text()
								var json = JSON.parse(data)
								if json.error == OK and typeof(json.result) == TYPE_DICTIONARY:
												tree_data = json.result
								else:
												print("Invalid map data")
												get_tree().quit()

func _ready():
				_load_json_data()
				extract_nodes()
				integrity_check()

func extract_nodes():
				for node in tree_data.nodes:
								node_data[node.id] = node

				for edge in tree_data.edges:
								if edge_data.has(edge[0]):
												edge_data[edge[0]][edge[1]] = true
								else:
												edge_data[edge[0]] = {edge[1]: true}

								if edge_data.has(edge[1]):
												edge_data[edge[1]][edge[0]] = true
								else:
												edge_data[edge[1]] = {edge[0]: true}

func get_neighbors(node_id):
				if edge_data.has(node_id):
								return edge_data[node_id].keys()
				return []

func integrity_check():
				
				var seen_nodes = []
				for node in tree_data.nodes:
								if seen_nodes.has(node.id):
												quit("Duplicate id %s:" % node.id)
								seen_nodes.append(node.id)

				var seen_node_ids_in_edges = []
				for edge in tree_data.edges:
								if seen_nodes.has(edge[0]) and seen_nodes.has(edge[1]):
												continue
								quit("Found unknown edge: %s%s" % edge)

				print("World Map integrity passed.")

func is_node_valid(node_id):
				return node_data.has(node_id)

func quit(msg):
				print("Quit Message:", msg)
				get_tree().quit()

func get_map_name(node_id):
				if node_id == "hideout":
								return "hideout"
				if node_id == "test_level":
								return "test_level"
				return node_data[node_id].passive_tag

func get_node_config(node_id):
				var tag = get_map_name(node_id)
				var map_config = Levels.config[tag]
				return map_config

func is_connected_to_root(node_id):
				if edge_data.has("root"):
								if edge_data["root"].has(node_id):
												return true

				return false

