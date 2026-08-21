extends PopupBase

var passive_node_scene = preload("res://scenes/Popups/Dialogs/PassiveTree/PassiveNode.tscn")
var edge_scene = preload("res://scenes/Popups/Dialogs/PassiveTree/Edge.tscn")

var text_input_dialog = preload("res://scenes/Popups/Dialogs/TextInputDialog.tscn")
var load_dialog = preload("res://scenes/Popups/Dialogs/TreeSelector/TreeSelector.tscn")

@onready var passive_container = $PassiveTree/PassiveTreeContainer
@onready var selector = $PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/MarginContainer/SelectorContainer/Selector
@onready var selector_container = $PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/MarginContainer/SelectorContainer
@onready var node_container = $PassiveTree/PassiveTreeContainer/Nodes
@onready var edge_container = $PassiveTree/PassiveTreeContainer/Edges
@onready var stat_container = $PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/StatPanel/VBoxContainer/StatScrollContainer/EffectiveStatContainer
@onready var stat_scroller = $PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/StatPanel/VBoxContainer/StatScrollContainer
@onready var searcher = $PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer2/HBoxContainer3/SearchInput

var node_for_id = {}

var cn

const SHRINK = 3.0
const small_offset = Vector2(8.0, 8.0)
const large_offset = Vector2(12.0, 12.0)
const keystone_offset = Vector2(16.0, 16.0)


func _ready() -> void :
				cn = GameState.get_current_specialization_tree(). class 
				GameState.connect("passives_changed", Callable(self, "resync"))
				GameState.connect("changed", Callable(self, "_on_settings_change"))
				GameState.connect("settings_changed", Callable(self, "_on_settings_change"))
				GameState.connect("tree_changed", Callable(self, "_on_tree_changed"))
				rebuild()
				_on_settings_change()
				_on_tree_changed()

				auto_pop = false

				$PassiveTree/PassiveTreeContainer.selector_container = selector_container
				$PassiveTree/PassiveTreeContainer.selector = selector

				$CanvasLayer/ColorRect.color = Colors.color_passive_tree


				Globals.update_search("")

func _process(delta: float) -> void :
				if Input.is_action_just_pressed("ui_cancel"):
								if passive_container.can_scroll and Globals.use_controllers:
												passive_container.can_scroll = false
												$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/BackButton.grab_focus()
								else:
												if PopupManager.is_popup_focused(self):
																PopupManager.pop_popup()

				if Input.is_action_pressed("gamepad_scroll_down"):
								stat_scroller.scroll_vertical += 3.0

				if Input.is_action_pressed("gamepad_scroll_up"):
								stat_scroller.scroll_vertical -= 3.0

				if Input.is_key_pressed(KEY_F):
								if Input.is_key_pressed(KEY_CONTROL):
												searcher.grab_focus()
												searcher.select_all()

func rebuild():
				for child in edge_container.get_children():
								child.queue_free()
				for child in node_container.get_children():
								child.queue_free()

				for node in PassiveTreeData.tree_data.nodes:
								node_for_id[node.id] = node
				if cn:
								for node in SpecializationData.loaded_data[cn].nodes:
												node_for_id[node.id] = node

				create_edges()
				create_nodes()
				render_effective_stats()
				resync()

func _on_tree_changed():
				$PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/MarginContainer/MessageBlocker.visible = false
				passive_container.can_scroll = true
				var focus_owner = $PassiveTreeGUI/MarginContainer.get_focus_owner()
				if GameState.get_allocated_count() > 0:
								$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/HBoxContainer/RefundButton.visible = true
				else:
								$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/HBoxContainer/RefundButton.visible = false

func resync():
				
				render_effective_stats()
				$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/VBOX/HBoxContainer/PointsAvailableLevel.text = str(GameState.get_available_passives())
				$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/VBOX/HBoxContainer2/SpecializationLabel.text = str(GameState.get_available_specialization_passives())
				$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/HBoxContainer/RefundButton.visible = false
				if GameState.get_allocated_count() + GameState.get_allocated_specialization_count() > 0:
									$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/HBoxContainer/RefundButton.visible = true

func create_nodes():
				for node in PassiveTreeData.tree_data.nodes:
								var passive_node = passive_node_scene.instantiate()
								passive_node.node_id = node.id
								var offset = Vector2.ZERO
								var tag = PassiveTreeData.get_tag(node.id)
								if node.id != "root" and not ("root" in tag):
												var p_type = PassiveTreeData.get_passive_type(node.id)

												if p_type == PassiveTypes.SMALL:
																offset = small_offset
												if p_type == PassiveTypes.LARGE:
																offset = large_offset
												if p_type == PassiveTypes.KEYSTONE:
																offset = keystone_offset
								passive_node.position = Vector2(node.position[0], node.position[1]) / SHRINK - offset
								passive_node.container = passive_container
								node_container.add_child(passive_node)

				if cn:
								for node in SpecializationData.loaded_data[cn].nodes:
												var passive_node = passive_node_scene.instantiate()
												passive_node.specialization_tree = cn
												passive_node.node_id = node.id
												var offset = Vector2.ZERO
												var tag = SpecializationData.get_tag(cn, node.id)
												if node.id != "root" and not ("root" in tag):
																var p_type = SpecializationData.get_passive_type(cn, node.id)
																if p_type == PassiveTypes.SMALL:
																				offset = small_offset
																if p_type == PassiveTypes.LARGE:
																				offset = large_offset
																if p_type == PassiveTypes.KEYSTONE:
																				offset = keystone_offset
												passive_node.position = Vector2(node.position[0], node.position[1]) / SHRINK - offset
												passive_node.container = passive_container
												node_container.add_child(passive_node)

func create_edges():
				for edge in PassiveTreeData.tree_data.edges:
								
								if "root" in edge[0] or "root" in edge[1]:
												continue
								var node_a = node_for_id[edge[0]]
								var node_b = node_for_id[edge[1]]
								var edge_node = edge_scene.instantiate()
								edge_node.position = Vector2.ZERO
								var offset = small_offset

								var p_type = PassiveTreeData.get_passive_type(edge[0])
								if p_type == PassiveTypes.SMALL:
												offset = small_offset
								if p_type == PassiveTypes.LARGE:
												offset = small_offset
								if p_type == PassiveTypes.KEYSTONE:
												offset = keystone_offset
								edge_node.start = Vector2(node_a.position[0], node_a.position[1]) / SHRINK

								p_type = PassiveTreeData.get_passive_type(edge[1])
								if p_type == PassiveTypes.SMALL:
												offset = small_offset
								if p_type == PassiveTypes.LARGE:
												offset = small_offset
								if p_type == PassiveTypes.KEYSTONE:
												offset = keystone_offset
								edge_node.end = Vector2(node_b.position[0], node_b.position[1]) / SHRINK

								edge_node.node_a = node_a.id
								edge_node.node_b = node_b.id
								edge_container.add_child(edge_node)

				if cn:
								for edge in SpecializationData.loaded_data[cn].edges:
												
												if "root" in edge[0] or "root" in edge[1]:
																continue
												var node_a = node_for_id[edge[0]]
												var node_b = node_for_id[edge[1]]
												var edge_node = edge_scene.instantiate()
												edge_node.specialization_tree = cn
												edge_node.position = Vector2.ZERO
												var offset = small_offset

												var p_type = SpecializationData.get_passive_type(cn, edge[0])
												if p_type == PassiveTypes.SMALL:
																offset = small_offset
												if p_type == PassiveTypes.LARGE:
																offset = small_offset
												if p_type == PassiveTypes.KEYSTONE:
																offset = keystone_offset
												edge_node.start = Vector2(node_a.position[0], node_a.position[1]) / SHRINK

												p_type = SpecializationData.get_passive_type(cn, edge[1])
												if p_type == PassiveTypes.SMALL:
																offset = small_offset
												if p_type == PassiveTypes.LARGE:
																offset = small_offset
												if p_type == PassiveTypes.KEYSTONE:
																offset = keystone_offset
												edge_node.end = Vector2(node_b.position[0], node_b.position[1]) / SHRINK

												edge_node.node_a = node_a.id
												edge_node.node_b = node_b.id
												edge_container.add_child(edge_node)


func _on_RefundButton_pressed() -> void :
				GameState.reset_passives()
				if Globals.use_controllers:
								$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/EditButton.grab_focus()
				else:
								$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/BackButton.grab_focus()

func render_effective_stats():
				print("render stats..")
				for child in stat_container.get_children():
								child.queue_free()
				var applied_stats = GameState.collect_passive_tree_buffs()

				for keystone in applied_stats.keystones:
								var label = Label.new()
								label.autowrap = true
								label.align = HORIZONTAL_ALIGNMENT_CENTER
								label.text = Keystones.keystones[keystone].description
								stat_container.add_child(label)

				for stat in StatsInfo.stat_list:
								if applied_stats.stats.has(stat):
												var stat_config = applied_stats.stats[stat]
												for scaling_type in stat_config:
																var label = Label.new()
																label.autowrap = true
																label.align = HORIZONTAL_ALIGNMENT_CENTER
																label.text = StatsInfo.render_passive_stat_line(stat, {
																				"scaling_type": scaling_type, 
																				"amount": stat_config[scaling_type]
																})
																stat_container.add_child(label)

				for stat in StatsInfo.stat_list:
								var tagged_stats = applied_stats.conditional_stats
								for damage_type in tagged_stats:
												var stats_for_type = tagged_stats[damage_type]
												if stats_for_type.has(stat):
																var stat_config = stats_for_type[stat]
																for scaling_type in stat_config:
																				var label = Label.new()
																				label.autowrap = true
																				label.align = HORIZONTAL_ALIGNMENT_CENTER
																				label.text = StatsInfo.render_passive_stat_line(stat, {
																								"scaling_type": scaling_type, 
																								"amount": stat_config[scaling_type], 
																								"tags": [damage_type]
																				})
																				stat_container.add_child(label)

func _on_StatScrollContainer_mouse_entered() -> void :
				passive_container.disable_zoom = true

func _on_StatScrollContainer_mouse_exited() -> void :
				passive_container.disable_zoom = false

func _on_SearchInput_focus_entered() -> void :
				passive_container.disable_zoom = true

func _on_SearchInput_focus_exited() -> void :
				passive_container.disable_zoom = false

func _on_SearchInput_mouse_exited() -> void :
				searcher.release_focus()

func _on_SearchInput_text_changed(new_text: String) -> void :
				Globals.update_search(new_text)

func _on_LoadButton_pressed() -> void :
				var popup = load_dialog.instantiate()
				popup.connect("destroy", Callable(self, "_refocus_back"))
				PopupManager.show_popup(popup, self)

func _on_NewButton_pressed() -> void :
				var popup = text_input_dialog.instantiate()
				popup.title = "Save Tree"
				popup.label = "Tree Name:"
				popup.connect("text_entered", Callable(self, "_create_tree"))
				popup.connect("destroy", Callable(self, "_refocus_new"))
				PopupManager.show_popup(popup, self)

func _refocus_back():
				if Globals.use_controllers:
								passive_container.can_scroll = true
								$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/BackButton.grab_focus()

func _refocus_new():
				if Globals.use_controllers:
								passive_container.can_scroll = true
								$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/HBoxContainer/NewButton.grab_focus()

func _on_ShowButton_pressed():
				GameState.set_stats_panel(true)
				$PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/StatPanel/VBoxContainer/HBoxContainer/HideButton.grab_focus()

func _on_HideButton_pressed():
				GameState.set_stats_panel(false)
				$PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/ShowContainer/ShowButton.grab_focus()

func _on_settings_change():
				var show_panel = GameState.saved_stats.settings.enable_stats_panel
				$PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/StatPanel.visible = show_panel
				$PassiveTreeGUI/MarginContainer/VBoxContainer/HBoxContainer/ShowContainer.visible = not show_panel

func _on_BackButton_pressed() -> void :
				PopupManager.pop_popup()

func _on_EditButton_pressed() -> void :
				passive_container.can_scroll = true
				$PassiveTreeGUI/MarginContainer/VBoxContainer/MarginContainer/PanelContainer/HBoxContainer2/HBoxContainer/EditButton.release_focus()
