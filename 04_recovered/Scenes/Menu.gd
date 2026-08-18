extends PanelContainer

var click = preload("res://Sounds/UI/button_click.wav")
var settings = preload("res://Scenes/Popups/Dialogs/Settings/Settings.tscn")
var help = preload("res://Scenes/Popups/Dialogs/Help/Help.tscn")
var mod_help = preload("res://Scenes/Popups/Dialogs/ModHelp/ModHelp.tscn")
var unique_help = preload("res://Scenes/Popups/Dialogs/UniqueHelp/UniqueHelp.tscn")
var character_select = preload("res://Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn")

func _ready() -> void :
				GameState.connect("changed", self, "render")
				render()

				PopupManager.reset()

				Globals.set_rich_presence_menu()

func render():
				$CenterContainer / VBoxContainer / CenterContainer / VBoxContainer / StartButton.grab_focus()
				$CenterContainer / VBoxContainer / HBoxContainer2 / HBoxContainer / VersionLabel.text = Constants.GAME_VERSION

				if GameState.saved_stats.settings.enable_music:
								$AudioStreamPlayer.playing = true

func _on_StartButton_pressed() -> void :
				var popup = character_select.instance()
				PopupManager.show_popup(popup, self)

func _on_QuitButton_pressed() -> void :
				GameState.quit()

func _on_UpgradeButton_pressed() -> void :
				Globals.play_sound_effect(click)
				get_tree().change_scene("res://Scenes/PassiveTree/PassiveTree.tscn")

func _on_SettingsButton_pressed() -> void :
				var popup = settings.instance()
				popup.show_reset = true
				popup.connect("destroy", self, "_focus_settings")
				PopupManager.show_popup(popup, self)

func _focus_settings():
				$CenterContainer / VBoxContainer / CenterContainer / VBoxContainer / SettingsButton.grab_focus()

func _on_LinkButton_pressed() -> void :
				Globals.play_sound_effect(click)
				OS.shell_open("https://discord.gg/TzF3aRWnhZ")

func _on_HelpButton_pressed() -> void :
				Globals.play_sound_effect(click)
				var popup = help.instance()
				PopupManager.show_popup(popup, self)

func _on_GeneButton_pressed() -> void :
				Globals.play_sound_effect(click)
				get_tree().change_scene("res://Scenes/GeneEditor/GeneLoadout.tscn")

func _on_CRISPRButton_pressed() -> void :
				Globals.play_sound_effect(click)
				get_tree().change_scene("res://Scenes/GeneEditor/GeneInventory.tscn")


func _on_HelpButton2_pressed() -> void :
				Globals.play_sound_effect(click)
				var popup = mod_help.instance()
				PopupManager.show_popup(popup, self)


func _on_UniqueItems_pressed():
				Globals.play_sound_effect(click)
				var popup = unique_help.instance()
				PopupManager.show_popup(popup, self)
