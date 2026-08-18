extends Node

var queued_popups = []
var open_popups = []

func _ready() -> void :
				pause_mode = Node.PAUSE_MODE_PROCESS

func show_popup(popup, node):
				queued_popups.append([popup, node])

func reset():
				for popup in open_popups:
								if popup[0]:
												popup[0].queue_free()
				queued_popups = []
				open_popups = []

func _process(delta: float) -> void :
				if Input.is_action_just_pressed("ui_cancel"):
								call_deferred("maybe_pop")

				if len(queued_popups) > 0:
								var popup_data = queued_popups.pop_front()
								var popup = popup_data[0]
								var node = popup_data[1]
								if is_instance_valid(popup) and is_instance_valid(node):
												popup.connect("destroy", self, "_on_destroy", [popup])
												popup.layer = get_next_layer()
												node.add_child(popup)
												push_popup(popup)


func maybe_pop():
				if should_pop():
								pop_popup()

func pop_popup():
				if len(open_popups) > 0:
								var latest = open_popups.pop_back()[0]
								if len(open_popups) > 0:
												var next = open_popups.back()
												if is_instance_valid(next[0]):
																next[0].pause_mode = next[1]
																next[0]._grab_focus()
								latest.queue_free()



func push_popup(popup):
				if len(open_popups) > 0:
								var next = open_popups.back()
								next[0].pause_mode = PAUSE_MODE_STOP
				open_popups.append([popup, popup.pause_mode])
				popup.pause_mode = PAUSE_MODE_PROCESS

func should_pop():
				if len(open_popups) > 0:
								var next = open_popups.back()[0]
								if is_instance_valid(next):
												return next.auto_pop
				return true

func is_popup_focused(popup):
				if len(open_popups) > 0:
								return open_popups.back()[0] == popup
				return false

func get_next_layer():
				if len(open_popups) > 0:
								var highest = open_popups.back()[0]
								if highest:
												return highest.layer + 1
				return 10

func _on_destroy(popup):
				if len(open_popups) > 0:
								if open_popups.back()[0] == popup:
													pop_popup()

func is_free():
				return len(open_popups) == 0
