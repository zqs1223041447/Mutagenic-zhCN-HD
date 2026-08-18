extends VBoxContainer


var description
var subtext


func _ready() -> void :
				$HBoxContainer / UnlockDescription.text = description
				$UnlockRequirement.text = subtext
