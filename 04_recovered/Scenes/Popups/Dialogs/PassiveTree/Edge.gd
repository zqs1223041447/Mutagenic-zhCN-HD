extends Node2D

var in_allocation_path
var specialization_tree
var start
var end
var node_a
var node_b

func _ready() -> void :
				in_allocation_path = false

				if specialization_tree:
								SpecializationTreeUtils.connect("allocation_path_changed", self, "_update_edge")
				else:
								PassiveTreeUtils.connect("allocation_path_changed", self, "_update_edge")

func _update_edge():
				if specialization_tree:
								if SpecializationTreeUtils.edge_in_path(node_a, node_b):
												in_allocation_path = true
								else:
												in_allocation_path = false
				else:
								if PassiveTreeUtils.edge_in_path(node_a, node_b):
												in_allocation_path = true
								else:
												in_allocation_path = false
				update()

func _process(_d) -> void :
				update()

func _draw() -> void :
				var c = Colors.edge_locked
				var width = 2.0
				if specialization_tree:
								if GameState.are_specialization_passives_allocated(node_a, node_b):
												c = Colors.edge_unlocked
								if in_allocation_path:
												c = Colors.edge_in_path
				else:
								if GameState.are_passives_allocated(node_a, node_b):
												c = Colors.edge_unlocked
												width = 4.0
								if in_allocation_path:
												c = Colors.edge_in_path
												width = 4.0

				draw_line(start, end, c, width)
