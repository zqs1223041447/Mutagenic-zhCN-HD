extends HBoxContainer

var stat_name
var stat_value
var highlight = false


func _ready() -> void :
				$Name.text = stat_name
				$Value.text = stat_value
				
				if highlight:
								modulate = Colors.buffed
