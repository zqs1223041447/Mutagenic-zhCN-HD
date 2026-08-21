extends PopupBase

var dialog = preload("res://scenes/Popups/Dialogs/TintedConfirmationDialog.tscn")
var keybind_menu = preload("res://scenes/Popups/Dialogs/Keybinds/Keybinds.tscn")

var show_reset = false

func _ready() -> void :


				GameState.connect("settings_changed", Callable(self, "_on_settings_change"))

				if not show_reset:
								$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/ResetButton.visible = false

				_on_settings_change()
				_refocus()

func _refocus():
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/ReturnButton.grab_focus()

func _on_ResetButton_pressed() -> void :
				var confirm_dialog = dialog.instantiate()
				confirm_dialog.window_title = "Are you sure? This cannot be undone."
				confirm_dialog.connect("confirmed", Callable(self, "_on_confirm"))
				add_child(confirm_dialog)
				confirm_dialog.popup_centered()

func _on_confirm():
				GameState.reset_game_state()

func _on_ReturnButton_pressed() -> void :
				PopupManager.pop_popup()

func _on_settings_change():
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/MusicToggle.pressed = GameState.saved_stats.settings.enable_music
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/SFXToggle.pressed = GameState.saved_stats.settings.enable_sfx
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/DropsToggle.pressed = GameState.saved_stats.settings.enable_drops
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/FloatingDamageToggle.pressed = GameState.saved_stats.settings.enable_floating_damage
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/FloatingXPToggle.pressed = GameState.saved_stats.settings.enable_floating_xp
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/FullscreenToggle.pressed = GameState.saved_stats.settings.enable_fullscreen
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/VSyncToggle.pressed = GameState.saved_stats.settings.enable_vsync
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/EffectsToggle.pressed = GameState.saved_stats.settings.enable_fx
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/StatusToggle.pressed = GameState.saved_stats.settings.enable_status_bars
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer/GlobeToggle.pressed = GameState.saved_stats.settings.enable_health_globe
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer2/HBoxContainer/MusicSlider.value = GameState.saved_stats.settings.volume.music
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer2/HBoxContainer2/SFXSlider.value = GameState.saved_stats.settings.volume.sfx
				$MarginContainer/CenterContainer/PanelContainer/VBoxContainer2/CenterContainer/VBoxContainer2/HBoxContainer3/DropSlider.value = GameState.saved_stats.settings.volume.drops
				GameState.save_game(false)

func _on_MusicToggle_toggled(button_pressed: bool) -> void :
				GameState.set_music_enabled(button_pressed)

func _on_SFXToggle_toggled(button_pressed: bool) -> void :
				GameState.set_sfx_enabled(button_pressed)

func _on_DropsToggle_toggled(button_pressed: bool) -> void :
				GameState.set_drops_enabled(button_pressed)

func _on_FloatingDamageToggle_toggled(button_pressed: bool) -> void :
				GameState.set_floating_damage_enabled(button_pressed)

func _on_FullscreenToggle_toggled(button_pressed):
				GameState.set_fullscreen(button_pressed)

func _on_EffectsToggle_toggled(button_pressed):
				GameState.set_fx(button_pressed)

func _on_StatusToggle_toggled(button_pressed):
				GameState.set_status_bars(button_pressed)

func _on_VSyncToggle_toggled(button_pressed: bool) -> void :
				GameState.set_vsync(button_pressed)

func _on_GlobeToggle_toggled(button_pressed: bool) -> void :
				GameState.set_globes(button_pressed)

func _on_Keybindings_pressed() -> void :
				var popup = keybind_menu.instantiate()
				popup.connect("destroy", Callable(self, "_refocus"))
				PopupManager.show_popup(popup, self)

func _on_DropSlider_value_changed(value: float) -> void :
				GameState.set_drops_volume(value)

func _on_SFXSlider_value_changed(value: float) -> void :
				GameState.set_sfx_volume(value)

func _on_MusicSlider_value_changed(value: float) -> void :
				GameState.set_music_volume(value)


func _on_FloatingXPToggle_toggled(button_pressed: bool) -> void :
				GameState.set_floating_xp_enabled(button_pressed)
