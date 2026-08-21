extends Interactable

var dialog = preload("res://scenes/Popups/Dialogs/SkillSelect/SkillSelect.tscn")
@onready var notice = $Notice

func _ready() -> void :
				if GameState.is_help_tip_read("weapon_intro"):
								notice.queue_free()
				else:
								GameState.connect("help_tips_changed", Callable(self, "_check"))

func get_context_text() -> String:
				return "Weapons and Abilities"

func on_interact():
				var popup = dialog.instantiate()
				PopupManager.show_popup(popup, self)

func _check():
				if GameState.is_help_tip_read("weapon_intro") and is_instance_valid(notice):
								notice.queue_free()
