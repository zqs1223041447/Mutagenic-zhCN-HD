
extends Node

var tree_data
var node_data = {}
var edge_data = {}

func _load_json_data():
				var datafile = "res://passive_tree_data/passive_tree_gen.json"
				var f = FileAccess.open(datafile, FileAccess.READ)
				if FileAccess.file_exists(datafile):
								var data = f.get_as_text()
								var json = JSON.parse_string(data)
								if json != null and typeof(json) == TYPE_DICTIONARY:
												tree_data = json
								else:
												print("Invalid tree data")
												get_tree().quit()

func _ready():
				_load_json_data()
				extract_nodes()
				integrity_check()

func extract_nodes():
				for node in tree_data.nodes:
								node_data[node.id] = node
								if not edge_data.has(node.id):
												edge_data[node.id] = {}

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

				print("Passive tree integrity passed.")

func quit(msg):
				print("Quit Message:", msg)
				get_tree().quit()

func get_tag(node_id):
				return node_data[node_id].passive_tag

func get_node_config(node_id):
				var tag = get_tag(node_id)
				var passive_config = PassiveTagStats.get_passive_config(tag)
				return passive_config

func get_passive_type(node_id):
				var passive_config = get_node_config(node_id)
				if not passive_config:
								print("NO NODE:", get_tag(node_id))
				return passive_config.passive_type

func is_connected_to_root(node_id):
				if edge_data.has("root"):
								if edge_data["root"].has(node_id):
												return true

				return false

func is_connected_to_class_root(node_id, class_root):
				if edge_data.has(class_root):
								if edge_data[class_root].has(node_id):
												return true

				return false

