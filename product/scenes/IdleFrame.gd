extends RefCounted
class_name FrameTimer

class FrameTimer_ extends Node:
				signal timeout

				var frames: = 1

				func _ready() -> void :
								get_tree().connect("process_frame", Callable(self, "_on_timeout"))

				func _on_timeout() -> void :
								frames -= 1
								if frames == 0:
												emit_signal("timeout")
												queue_free()

static func idle_frame(node: Node, frames: int = 1):
				var t: = FrameTimer_.new()
				t.frames = frames
				node.add_child(t)

				return t
