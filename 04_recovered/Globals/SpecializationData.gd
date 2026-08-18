extends Node

var loaded_data = {}
var tree_data = {}

func _load_json_data(fname, tree_name):
				var f = File.new()
				var datafile = "res://passive_tree_data/specializations/" + fname + ".json"
				f.open(datafile, File.READ)
				if f.file_exists(datafile):
								var data = f.get_as_text()
								var json = JSON.parse(data)
								if json.error == OK and typeof(json.result) == TYPE_DICTIONARY:
												extract_nodes(tree_name, json.result)
												loaded_data[tree_name] = json.result
								else:
												print("Failed to load json")
												get_tree().quit()
				else:
								print("No data found for: ", fname, " : ", tree_name)

func _ready():
				for spec in PlayableClasses.PLAYABLE_SPECIALIZATIONS.keys():
								var fname = PlayableClasses.specialization_data_files[spec]
								_load_json_data(fname, spec)
				integrity_check()
				print("Done integrity check for specialization trees")

func extract_nodes(tree_name, data):
				var node_data = {}
				var edge_data = {}
				if not tree_data.has(tree_name):
								tree_data[tree_name] = {
												"nodes": node_data, 
												"edges": edge_data, 
								}

				for node in data.nodes:
								node_data[node.id] = node
								if not edge_data.has(node.id):
												edge_data[node.id] = {}

				for edge in data.edges:
								if edge_data.has(edge[0]):
												edge_data[edge[0]][edge[1]] = true
								else:
												edge_data[edge[0]] = {edge[1]: true}

								if edge_data.has(edge[1]):
												edge_data[edge[1]][edge[0]] = true
								else:
												edge_data[edge[1]] = {edge[0]: true}

func get_neighbors(tree_name, node_id):
				var edge_data = tree_data[tree_name].edges
				if edge_data.has(node_id):
								return edge_data[node_id].keys()
				return []

func integrity_check():
				
				for tree_name in tree_data.keys():
								var seen_nodes = []
								for node in loaded_data[tree_name].nodes:
												if seen_nodes.has(node.id):
																quit("Duplicate id %s:" % node.id)
												seen_nodes.append(node.id)

								var seen_node_ids_in_edges = []
								for edge in loaded_data[tree_name].edges:
												if seen_nodes.has(edge[0]) and seen_nodes.has(edge[1]):
																continue
												quit("Found unknown edge: %s%s" % edge)

				print("Passive tree integrity passed.")

func quit(msg):
				print("Quit Message:", msg)
				get_tree().quit()

func get_tag(tree_name, node_id):
				var node_data = tree_data[tree_name].nodes
				return node_data[node_id].passive_tag

func get_node_config(tree_name, node_id):
				var tag = get_tag(tree_name, node_id)
				var passive_config = PassiveTagStats.get_passive_config(tag)
				return passive_config

func get_passive_type(tree_name, node_id):
				var passive_config = get_node_config(tree_name, node_id)
				if not passive_config:
								print("NO NODE:", get_tag(tree_name, node_id))
				return passive_config.passive_type

func is_connected_to_root(tree_name, node_id):
				var edge_data = tree_data[tree_name].edges
				if edge_data.has("class_root"):
								if edge_data["class_root"].has(node_id):
												return true
				return false

