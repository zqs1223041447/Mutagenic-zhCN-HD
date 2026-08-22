extends PopupBase

var load_dialog = preload("res://scenes/Popups/Dialogs/SkillLoadoutSelector/SkillLoadoutSelector.tscn")
var text_input_dialog = preload("res://scenes/Popups/Dialogs/TextInputDialog.tscn")
var skill_tip = preload("res://scenes/Popups/Dialogs/HelpTip/WeaponIntro/WeaponIntro.tscn")

func _ready() -> void :
				_grab_focus()

				if not GameState.is_help_tip_read("weapon_intro"):
								GameState.mark_help_tip_read("weapon_intro")
								var popup = skill_tip.instantiate()
								popup.connect("destroy", Callable(self, "_grab_focus"))
								PopupManager.show_popup(popup, self)

func _grab_focus():
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/VBoxContainer/HBoxContainer/HBoxContainer/PrimaryButton.select()

func _on_Button_pressed() -> void :
				PopupManager.pop_popup()

func _on_NewLoadoutButton_pressed():
				var popup = text_input_dialog.instantiate()
				popup.title = "Create New Skill Loadout"
				popup.label = "Loadout Name:"
				popup.connect("text_entered", Callable(self, "_create_skill_loadout"))
				popup.connect("destroy", Callable(self, "_grab_focus"))
				PopupManager.show_popup(popup, self)


func _on_ChangeLoadoutButton_pressed():
				var popup = load_dialog.instantiate()
				PopupManager.show_popup(popup, self)


func _on_RenameLoadoutButton_pressed():
				print("RENAME")
				var popup = text_input_dialog.instantiate()
				popup.title = "Rename \"" + GameState.get_active_stats().selected_skill_loadout + "\""
				popup.label = "Skill Loadout Name"
				popup.prefill = GameState.get_active_stats().selected_skill_loadout
				popup.connect("text_entered", Callable(self, "_rename_loadout"))
				PopupManager.show_popup(popup, self)

func _rename_loadout(new_loadout_name):
				GameState.rename_skill_loadout(GameState.get_active_stats().selected_skill_loadout, new_loadout_name)
