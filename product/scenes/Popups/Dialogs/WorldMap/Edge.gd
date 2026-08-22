extends Node2D

var start
var end
var node_a
var node_b

func _ready() -> void :
				if StageProgress.is_stage_completed(node_a) or StageProgress.is_stage_completed(node_b):
								modulate = Color.WHITE
				else:
								modulate = Color(1, 1, 1, 0.2)

func _draw() -> void :
				var c = Colors.path
				var dash_length = 2.0
				var width = 3.0
				var cap_end = true
				var length = (end - start).length()
				var normal = (end - start).normalized()
				var dash_step = normal * dash_length

				if length < dash_length:
								draw_line(start, end, c, width)
								return

				else:
								var draw_flag = true
								var segment_start = start
								var steps = length / dash_length
								for start_length in range(0, steps + 1):
												var segment_end = segment_start + dash_step
												if draw_flag:
																draw_line(segment_start, segment_end, c, width)

												segment_start = segment_end
												draw_flag = not draw_flag

								if cap_end:
												draw_line(segment_start, end, c, width)
