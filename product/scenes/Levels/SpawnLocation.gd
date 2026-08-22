extends Node2D

signal computed_spawn
@onready var player = GameState.get_global("player")
@onready var level = GameState.get_global("level_scene")
@export var mobs_to_spawn = 10

var spawnable_tiles = []
var spawning = false
var thread


func _ready() -> void :
				await FrameTimer.idle_frame(self).timeout
				thread = Thread.new()
				thread.start(Callable(self, "_load_tiles"))
				thread.wait_to_finish()
				emit_signal("computed_spawn")
				try_to_spawn()


func _load_tiles():
				spawnable_tiles = level.get_spawnable_tiles_near_position(global_position, 3)

func _on_Timer_timeout() -> void :
				try_to_spawn()

func try_to_spawn():
				if spawning:
								print("ALREADY SPAWNING")
								return
				if player.global_position.distance_to(global_position) < 600:
								spawning = true
								level.spawn_cluster(spawnable_tiles, mobs_to_spawn)
								queue_free()
