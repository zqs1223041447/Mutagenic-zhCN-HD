extends Node2D

var stream
var bus = "SFX"


func _ready() -> void :
				if stream == null:
								queue_free()
								return
				$Audio.stream = stream
				$Audio.bus = bus
				$Audio.connect("finished", self, "queue_free")
				$Audio.play()
