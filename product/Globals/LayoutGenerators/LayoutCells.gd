extends LayoutGenerator

func generate(level):
				var start_y = 0
				var start_x = 0
				var target_x
				var target_y
				
				var player_x = (start_x) * level.tiles.cell_size.x
				var player_y = (start_y) * level.tiles.cell_size.y
				
				level.player.global_position = Vector2(player_x, player_y)
				
				var forks = 8
				var target_rotation = 0
				for k in range(forks):
								target_rotation = k * 2 * PI / forks + randf() * 2 * PI / forks
								
								target_x = round(start_x + 30 * cos(target_rotation))
								target_y = round(start_y + 30 * sin(target_rotation))

								level.connect_points(Vector2(start_x, start_y), Vector2(target_x, target_y), false, 3, true)
												
								start_x = target_x
								start_y = target_y
								
								if Vector2(start_x, start_y).length() < 5:
												break
								
				level.connect_points(Vector2(start_x, start_y), Vector2(0, 0), false, 3, true)
