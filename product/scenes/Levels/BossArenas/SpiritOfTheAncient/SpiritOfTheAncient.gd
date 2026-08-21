extends BaseLevel

func _ready():
				player.global_position = Vector2.ZERO
				read_tiles()

				
				var boss_scene = Levels.config[Globals.selected_level].boss_scene
				var boss = boss_scene.instantiate()
				boss.global_position = $BossSpawner.global_position
				add_child(boss)
				await FrameTimer.idle_frame(self).timeout
				emit_signal("map_done")
