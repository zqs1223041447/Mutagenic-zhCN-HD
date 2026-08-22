extends Node2D
## Death dissolve overlay spawned by Mob.spawn_death_animation().
##
## P4-B F1b: the death -> dissolve -> removal rhythm is configurable.
## `dissolve_duration` drives both the shader ramp rate and the removal timer
## so they stay locked in step; `dissolve_delay` holds the corpse before the
## dissolve starts (total lifetime = delay + duration).  Defaults reproduce
## the legacy behavior exactly (0.25s ramp, no hold).

@export var dissolve_duration := 0.25
@export var dissolve_delay := 0.0

@onready var sprite = $DissolveSprite

var dissolved = 0.0
var _rate = 4.0
var _held = 0.0


func _ready() -> void :
				_rate = 1.0 / max(dissolve_duration, 0.01)
				var timer: Timer = $Timer
				timer.wait_time = max(dissolve_duration + dissolve_delay, 0.01)
				timer.start()


func _on_Timer_timeout() -> void :
				queue_free()


func _process(delta: float) -> void :
				if _held < dissolve_delay:
								_held += delta
								return
				dissolved += delta * _rate
				sprite.material.set_shader_parameter("dissolveAmount", min(dissolved, 1.0))


func dissolve_progress() -> float:
				return min(dissolved, 1.0)
