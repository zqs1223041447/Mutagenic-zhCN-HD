extends Node2D

var sfx = load("res://Sounds/UI/passive_allocate.wav")
var sfx_large = load("res://Sounds/UI/passive_allocate.wav")

signal selected_node(node_id)
signal focus_changed

var small_passive_frames = load("res://sprites/gui/small_passive.aseprite")
var large_passive_frames = load("res://sprites/gui/large_passive.aseprite")
var keystone_passive_frames = load("res://sprites/gui/keystone_passive.aseprite")

var frames
var focused
var passive_type = PassiveTypes.SMALL
var node_id
var node_tag
var active
var node_config
var searchable_string = ""
var sound
var container
var has_loaded = false
var specialization_tree = null

const SMALL_OFFSET = Vector2(8.0, 8.0)
const LARGE_OFFSET = Vector2(12.0, 12.0)
const KEYSTONE_OFFSET = Vector2(16.0, 16.0)


func _ready() -> void :
				
				if specialization_tree:
								node_tag = SpecializationData.get_tag(specialization_tree, node_id)
				else:
								node_tag = PassiveTreeData.get_tag(node_id)

				if "root" in node_id:
								visible = false
								return

				node_config = PassiveTagStats.get("stats")[node_tag]

				searchable_string += node_config.name + " "

				for item in node_config.stats:
								var label = Label.new()
								var stat = item.stat
								label.text = StatsInfo.render_passive_stat_line(stat, item)
								searchable_string += label.text + " "
								$PassiveButton/StatInfoContainer/VBoxContainer/StatList.add_child(label)

				if node_config.has("keystones"):
								for item in node_config.keystones:
												var label = Label.new()
												var keystone = Keystones.keystones[item]
												label.text = keystone.description
												searchable_string += label.text + " "
												label.autowrap = true
												label.custom_minimum_size = Vector2(320, 16)
												$PassiveButton/StatInfoContainer/VBoxContainer/StatList.add_child(label)

				searchable_string = searchable_string.to_lower()

				if node_config.has("passive_texture"):
								$PassiveButton/Sprite.texture = node_config.passive_texture

				$PassiveButton/StatInfoContainer/VBoxContainer/NodeNameLabel.text = node_config.name

				if node_config.passive_type == PassiveTypes.SMALL:
								frames = small_passive_frames
								$PassiveButton/Sprite.offset = SMALL_OFFSET
								$Glow.offset = SMALL_OFFSET / 2.0
								$Glow.scale = Vector2.ONE * 2.0
								$PassiveButton.size = Vector2(16.0, 16.0)
								sound = sfx
				if node_config.passive_type == PassiveTypes.LARGE:
								frames = large_passive_frames
								$PassiveButton/Sprite.offset = LARGE_OFFSET
								$Glow.offset = LARGE_OFFSET / 4.0
								$Glow.scale = Vector2.ONE * 4.0
								$PassiveButton.size = Vector2(24.0, 24.0)
								sound = sfx_large
				if node_config.passive_type == PassiveTypes.KEYSTONE:
								frames = keystone_passive_frames
								$PassiveButton/Sprite.offset = KEYSTONE_OFFSET
								$Glow.offset = KEYSTONE_OFFSET / 4.0
								$Glow.scale = Vector2.ONE * 4.0
								$PassiveButton.size = Vector2(32.0, 32.0)
								sound = sfx_large

				$PassiveButton.connect("mouse_entered", Callable($PassiveButton, "grab_focus"))
				$PassiveButton.connect("mouse_exited", Callable($PassiveButton, "release_focus"))
				$PassiveButton.connect("focus_entered", Callable(self, "show_hover"))
				$PassiveButton.connect("focus_exited", Callable(self, "hide_hover"))
				$PassiveButton/StatInfoContainer/VBoxContainer/NodeNameLabel.modulate = Colors.buffed
				connect("focus_changed", Callable(self, "reset_focus_sprite"))
				GameState.connect("passives_changed", Callable(self, "_resync"))
				Globals.connect("search_changed", Callable(self, "_on_search_change"))
				_on_search_change(Globals.search_string)
				_resync()

func _resync():
				reset_focus_sprite()
				reset_modulate()
				var stats = GameState.get_active_stats()
				var cls = stats.mutation_tree_loadout. class 
				var cls_root = PlayableClasses.get_root_node(cls)
				if not has_loaded and not specialization_tree:
								has_loaded = true
								if GameState.can_allocate_passive(node_id) and PassiveTreeData.is_connected_to_class_root(node_id, cls_root):
												container.center_on(position)

				if not specialization_tree:
								if GameState.can_allocate_passive(node_id) and GameState.get_allocated_count() == 0:
												$StartingGlow.visible = true
								else:
												$StartingGlow.visible = false

func reset_focus_sprite():
				if specialization_tree:
								if GameState.is_specialization_passive_allocated(node_id):
												$PassiveButton.texture_normal = frames.get_frame("default", 0)
								else:
												$PassiveButton.texture_normal = frames.get_frame("default", 1)
												if GameState.can_allocate_specialization_passive(node_id):
																$PassiveButton.texture_normal = frames.get_frame("default", 2)
								if focused:
												$PassiveButton.texture_normal = frames.get_frame("default", 3)
				else:
								if GameState.is_passive_allocated(node_id):
												$PassiveButton.texture_normal = frames.get_frame("default", 0)
								else:
												$PassiveButton.texture_normal = frames.get_frame("default", 1)
												if GameState.can_allocate_passive(node_id):
																$PassiveButton.texture_normal = frames.get_frame("default", 2)

								if focused:
												$PassiveButton.texture_normal = frames.get_frame("default", 3)

				reset_modulate()

func reset_modulate():
				if specialization_tree:
								if GameState.is_specialization_passive_allocated(node_id):
												$PassiveButton.self_modulate = Colors.buffed
								else:
												$PassiveButton.self_modulate = Color.WHITE
				else:
								if GameState.is_passive_allocated(node_id):
												$PassiveButton.self_modulate = Colors.buffed
								else:
												$PassiveButton.self_modulate = Color.WHITE

func toggle():
				if specialization_tree:
								if not GameState.is_specialization_passive_allocated(node_id):
												if GameState.allocate_specialization_path():
																Globals.play_sound_effect(sound)
												else:
																print("Failed to allocated node id", node_id)
								else:
												if GameState.disconnect_specialization_path_at(node_id):
																Globals.play_sound_effect(sound)
												else:
																print("Failed to remove node id", node_id)
				else:
								if not GameState.is_passive_allocated(node_id):
												if GameState.allocate_path():
																Globals.play_sound_effect(sound)
												else:
																print("Failed to allocated node id", node_id)
								else:
												if GameState.disconnect_path_at(node_id):
																Globals.play_sound_effect(sound)
												else:
																print("Failed to remove node id", node_id)


func show_hover() -> void :
				z_index = 5
				if specialization_tree:
								SpecializationTreeUtils.compute_shortest_allocation_path(specialization_tree, node_id)
				else:
								
								PassiveTreeUtils.compute_shortest_allocation_path(node_id)


func hide_hover() -> void :
				z_index = 1
				if specialization_tree:
								SpecializationTreeUtils.clear_shortest_allocation_path()
				else:
								
								PassiveTreeUtils.clear_shortest_allocation_path()

func _on_PassiveButton_focus_entered() -> void :
				focused = true
				$PassiveButton/StatInfoContainer.visible = true
				emit_signal("focus_changed")

func _on_PassiveButton_focus_exited() -> void :
				focused = false
				$PassiveButton/StatInfoContainer.visible = false
				emit_signal("focus_changed")

func grab_focus():
				if focused:
								return
				$PassiveButton.grab_focus()

func release_focus():
				$PassiveButton.release_focus()

func _on_search_change(text):
				if len(text) > 2:
								if text in searchable_string:
												$PassiveButton.modulate = Color.WHITE
												$Glow.visible = true
								else:
												$PassiveButton.modulate = Color(1, 1, 1, 0.156863)
												$Glow.visible = false
				else:
								$PassiveButton.modulate = Color.WHITE
								$Glow.visible = false


func set_zoom(zoom):
				$PassiveButton/StatInfoContainer.scale = Vector2(1.0 / zoom, 1.0 / zoom)
