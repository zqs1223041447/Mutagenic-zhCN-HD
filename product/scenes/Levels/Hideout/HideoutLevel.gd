extends BaseLevel

var starter_popup = load("res://scenes/Popups/Dialogs/StarterPicker/StarterPicker.tscn")

func get_spawnables():
				return spawnables

func _ready():
				Globals.reset()
				player.global_position = Vector2.ZERO
				read_tiles()
				apply_saved_player_position()
				await FrameTimer.idle_frame(self).timeout
				emit_signal("map_done")
				call_deferred("check_for_starter_build")

				Globals.set_rich_presence_hideout()

func _input(event: InputEvent) -> void :
				if event is InputEventKey:
								if event.is_action_pressed("goto_test_level") and Constants.ENABLE_TEST_ZONE:
												GameState.get_global("world").switch_levels("test_level", true, 1)


func check_for_starter_build():
				if GameState.needs_starter():
								var popup = starter_popup.instantiate()
								PopupManager.show_popup(popup, self)
