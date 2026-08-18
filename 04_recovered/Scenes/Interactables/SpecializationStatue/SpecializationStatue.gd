extends Interactable

var dialog = preload("res://Scenes/Popups/Dialogs/SpecializationPicker/SpecializationPicker.tscn")
onready var notice = $Notice

func _ready() -> void :
				if GameState.is_help_tip_read("specialization_intro") or GameState.get_active_stats().account_level < 30:
								notice.queue_free()
				else:
								GameState.connect("help_tips_changed", self, "_check")

func get_context_text() -> String:
				return "Class Specializations"

func on_interact():
				var popup = dialog.instance()
				PopupManager.show_popup(popup, self)


func _check():
				if GameState.is_help_tip_read("specialization_intro") and is_instance_valid(notice):
								notice.queue_free()
