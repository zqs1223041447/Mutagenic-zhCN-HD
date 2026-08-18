extends PanelContainer


func _ready() -> void :
				var refresh = OS.get_screen_refresh_rate()
				if refresh <= 60:
								Engine.iterations_per_second = 60
				else:
								Engine.iterations_per_second = 120

				print("Physics FPS set to: ", Engine.iterations_per_second)

				GameState.load_game()

