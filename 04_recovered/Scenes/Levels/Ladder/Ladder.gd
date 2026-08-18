extends BaseLevel

var death_screen = preload("res://Scenes/Popups/DeathScreen.tscn")

onready var spawn_parent = $Spawns
onready var time_label = $CanvasLayer / MarginContainer / VBoxContainer / HBoxContainer / TimeLabel

var time_to_next_spawn = 2
var current_wave = 1
var _is_spawning = true

const TIME_PER_WAVE = 45.0

var time_remaining = TIME_PER_WAVE

func get_spawnables():
				return spawnables

func _ready():
				player.global_position = Vector2.ZERO
				read_tiles()
				yield(FrameTimer.idle_frame(self), "timeout")
				emit_signal("map_done")
				Globals.reset()
				Globals.set_rich_presence_ladder()

func _physics_process(delta: float) -> void :
				if _is_spawning:
								time_to_next_spawn -= delta
								if time_to_next_spawn <= 0:
												time_to_next_spawn = 2.0
												spawn_next_wave()

				time_remaining -= delta
				if _is_spawning:
								time_remaining = TIME_PER_WAVE
				if time_remaining <= 0:
								
								var all_enemies = get_tree().get_nodes_in_group("enemies")
								if len(all_enemies) == 0:
												attempt_spawn()
								else:
												
												var popup = death_screen.instance()
												popup.out_of_time = true
												PopupManager.show_popup(popup, self)

func spawn_next_wave():
				_is_spawning = false

				
				for child in spawn_parent.get_children():
								spawn_cluster_in_ladder(child.position.x, child.position.y, 6, current_wave)

				current_wave += 1
				Globals.last_wave_time = Globals.elapsed_time
				Globals.waves_completed = current_wave - 2
				time_remaining = TIME_PER_WAVE

func _on_Timer_timeout() -> void :
				attempt_spawn()

func attempt_spawn():
				if _is_spawning:
								return
				
				var all_enemies = get_tree().get_nodes_in_group("enemies")

				if len(all_enemies) == 0:
								
								trigger_spawn_countdown()

func trigger_spawn_countdown():
				_is_spawning = true
				Globals.show_message("Wave " + str(current_wave) + " Spawning Shortly...")

func _on_TimeUpdater_timeout() -> void :
				time_label.text = str(stepify(floor(time_remaining), 0.1)) + "s"
