extends BaseLevel

var death_screen = preload("res://scenes/Popups/DeathScreen.tscn")

@onready var spawn_parent = $Spawns
@onready var time_label = $CanvasLayer/MarginContainer/VBoxContainer/HBoxContainer/TimeLabel

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
				await FrameTimer.idle_frame(self).timeout
				emit_signal("map_done")
				Globals.reset()
				spawn_cluster_in_ladder(0, 0, 300, current_wave)
