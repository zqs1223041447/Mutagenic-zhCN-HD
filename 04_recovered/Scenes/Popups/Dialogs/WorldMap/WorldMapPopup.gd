extends PopupBase

var map_scene = preload("res://Scenes/Popups/Dialogs/WorldMap/MapNode.tscn")
var edge_scene = preload("res://Scenes/Popups/Dialogs/WorldMap/Edge.tscn")

var text_input_dialog = preload("res://Scenes/Popups/Dialogs/TextInputDialog.tscn")
var load_dialog = preload("res://Scenes/Popups/Dialogs/TreeSelector/TreeSelector.tscn")

var node_for_id = {}

const SHRINK = 2.0
const small_offset = Vector2(8.0, 8.0)

onready var map_container = $WorldMap / WorldMapContainer
onready var edge_container = $WorldMap / WorldMapContainer / Edges
onready var node_container = $WorldMap / WorldMapContainer / Nodes
onready var selector_container = $WorldMapGUI / MarginContainer / VBoxContainer / HBoxContainer / MarginContainer / SelectorContainer
onready var selector = $WorldMapGUI / MarginContainer / VBoxContainer / HBoxContainer / MarginContainer / SelectorContainer / Selector


func _ready() -> void :
				map_container.selector_container = selector_container
				map_container.selector = selector
				map_container.can_scroll = true
				rebuild()

func _process(delta: float) -> void :
				if Input.is_action_just_pressed("ui_cancel"):
								if map_container.can_scroll and Globals.use_controllers:
												map_container.can_scroll = false
								else:
												if PopupManager.is_popup_focused(self):
																PopupManager.pop_popup()

func rebuild():
				for child in edge_container.get_children():
								child.queue_free()
				for child in node_container.get_children():
								child.queue_free()

				for node in WorldMapData.tree_data.nodes:
								node_for_id[node.id] = node

				create_edges()
				create_nodes()


func create_nodes():
				for node in WorldMapData.tree_data.nodes:
								var passive_node = map_scene.instance()
								passive_node.node_id = node.id
								node_container.add_child(passive_node)
								var _offset = small_offset
								passive_node.position = Vector2(node.position[0], node.position[1]) / SHRINK - _offset
								passive_node.set_zoom(map_container.get_zoom())

								if passive_node.node_id == GameState.get_active_stats().recent_stage:
												
												map_container.center_on(passive_node.global_position + small_offset)

func create_edges():
				for edge in WorldMapData.tree_data.edges:
								if edge[0] == "root" or edge[1] == "root":
												continue
								var node_a = node_for_id[edge[0]]
								var node_b = node_for_id[edge[1]]
								var edge_node = edge_scene.instance()
								edge_node.position = Vector2.ZERO
								var offset = small_offset
								edge_node.start = Vector2(node_a.position[0], node_a.position[1]) / SHRINK
								edge_node.end = Vector2(node_b.position[0], node_b.position[1]) / SHRINK

								edge_node.node_a = node_a.id
								edge_node.node_b = node_b.id
								edge_container.add_child(edge_node)


func _on_Button_pressed() -> void :
				PopupManager.pop_popup()
