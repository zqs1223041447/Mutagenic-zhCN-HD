extends CanvasLayer
class_name TooltipBase

func confine_to_window(element: PanelContainer, position, position_offset = Vector2.ZERO):
				var centered_position = Vector2(position.x, position.y)
				if element:
								var viewport_size = get_viewport().size
								var max_x = max(0, viewport_size.x - element.size.x)
								var max_y = max(0, viewport_size.y - element.size.y)
								if centered_position.x > viewport_size.x / 2:
												centered_position.x -= element.size.x + position_offset.x / 2.0 + 16.0
								else:
												centered_position.x += position_offset.x
								if centered_position.y > viewport_size.y / 2:
												centered_position.y -= element.size.y + position_offset.y / 2.0 + 16.0
								else:
												centered_position.x += position_offset.y
								element.position = Vector2(min(max_x, max(0, centered_position.x)), min(max_y, max(0, centered_position.y)))

