extends Sprite

@onready var world = GameState.get_global("world")

var target = null

func _ready() -> void :
				target = null
				world.connect("portal_spawned", Callable(self, "_set_target"))
				visible = false
				
func _set_target(pos):
				if pos != null:
								target = pos
								visible = true
				else:
								target = null
								visible = false

func _process(delta: float) -> void :
				if target != null:
								rotation = PI + global_position.angle_to_point(target)
				
