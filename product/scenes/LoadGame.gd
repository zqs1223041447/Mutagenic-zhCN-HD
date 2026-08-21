extends PanelContainer


func _ready() -> void :
				var refresh = DisplayServer.screen_get_refresh_rate()
				if refresh <= 60:
								Engine.physics_ticks_per_second = 60
				else:
								Engine.physics_ticks_per_second = 120

				print("Physics FPS set to: ", Engine.physics_ticks_per_second)

				GameState.load_game()

