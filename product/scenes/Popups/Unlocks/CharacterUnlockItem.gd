extends VBoxContainer


var texture
var description
var subtext


func _ready() -> void :
				$HBoxContainer/UnlockTexture.texture = texture
				$HBoxContainer/UnlockDescription.text = description
				$UnlockRequirement.text = subtext
