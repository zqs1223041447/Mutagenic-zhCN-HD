extends Node2D

signal show_edit_button

var panning = false
var disable_zoom = false
@onready var node_container = $Nodes
var selector
var selector_container
var show_selector = true
var can_scroll = false

var max_zoom = 4.0
var min_zoom = 0.25

func _ready() -> void :
				
				Globals.connect("change_input", Callable(self, "_on_input_changed"))

				await FrameTimer.idle_frame(self).timeout
				position += get_center()

func center_on(dst):
				await FrameTimer.idle_frame(self).timeout
				var center = get_center() - dst / get_zoom()
				position = get_center() - dst
				_zoom_at_point(4.0, get_center())
				await FrameTimer.idle_frame(self).timeout
				select_node_in_center()

func _input(event: InputEvent) -> void :
				if not can_scroll:
								return
				if event is InputEventMouseButton:
								if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
												panning = true
								elif event.button_index == MOUSE_BUTTON_LEFT:
												panning = false

								if not disable_zoom:
												if event.button_index == MOUSE_BUTTON_WHEEL_UP:
																if get_zoom() < max_zoom:
																				_zoom_at_point(1.05, get_global_mouse_position())

												if event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
																if get_zoom() > min_zoom:
																				_zoom_at_point(0.95, get_global_mouse_position())

				if event is InputEventMouseMotion and not disable_zoom:
								if panning:
												position += event.relative

func _on_input_changed(is_mouse):
				if is_mouse:
								show_selector = false
								selector.visible = false
				else:
								show_selector = true

				
				emit_signal("show_edit_button", not is_mouse and GameState.get_current_tree())

func _process(delta: float) -> void :
				var motion = Input.get_vector("move_left", "move_right", "move_up", "move_down")

				if not can_scroll:
								return

				if not disable_zoom:
								position -= 3.0 * motion

				if not disable_zoom:
								if Input.is_action_pressed("zoom_in"):
												if get_zoom() < max_zoom:
																_zoom_at_point(1.02, get_center())

								if Input.is_action_pressed("zoom_out"):
												if get_zoom() > min_zoom:
																_zoom_at_point(0.98, get_center())

				if motion != Vector2.ZERO and not disable_zoom:
								select_node_in_center()

func _zoom_at_point(zoom_change, mouse_position):
				var old_zoom = scale.x
				scale.x = clamp(scale.x * zoom_change, min_zoom, max_zoom)
				scale.y = clamp(scale.y * zoom_change, min_zoom, max_zoom)

				var actual_change = scale.x / old_zoom
				if old_zoom != scale.x:
								var delta_x = (mouse_position.x - position.x) * (actual_change - 1)
								var delta_y = (mouse_position.y - position.y) * (actual_change - 1)
								position.x = position.x - delta_x
								position.y = position.y - delta_y

								_handle_zoom_change()

func get_zoom():
				return scale.x

func get_center():
				var sz = selector_container.size
				var screen_center = Vector2(sz.x, sz.y) / 2.0 + selector_container.global_position
				return screen_center

func select_node_in_center():
				var all_children = node_container.get_children()

				var smallest_distance = INF
				var screen_center = get_center()
				var center = (screen_center - position) / get_zoom()
				var closest = null
				for child in all_children:
								if child.node_id == "root":
												continue
								var d = (child.position).distance_to(center)
								if d < smallest_distance and d < 28.0:
												smallest_distance = d
												closest = child

				if closest != null:
								closest.grab_focus()
								selector.visible = false
				else:
								for child in all_children:
												child.release_focus()
								if show_selector:
												selector.visible = true
								else:
												selector.visible = false


func _handle_zoom_change():
				var zoom = get_zoom()
				for node in node_container.get_children():
								node.set_zoom(zoom)
