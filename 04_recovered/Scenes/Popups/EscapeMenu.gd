extends PopupBase

var dialog = preload("res://Scenes/Popups/Dialogs/TintedConfirmationDialog.tscn")
var settings = preload("res://Scenes/Popups/Dialogs/Settings/Settings.tscn")
var help = preload("res://Scenes/Popups/Dialogs/Help/Help.tscn")
var mod_help = preload("res://Scenes/Popups/Dialogs/ModHelp/ModHelp.tscn")
var unique_help = preload("res://Scenes/Popups/Dialogs/UniqueHelp/UniqueHelp.tscn")

onready var gear = GameState.get_global("player").get_node("Gear")
onready var stats = GameState.get_global("player").get_node("Stats")
onready var stat_container = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / StatScroll / MarginContainer / StatContainer
onready var tab_container = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / TabContainer
onready var tab_icon_container = $CenterContainer / PanelContainer / VBoxContainer / TabIconContainer

var tab_pane = preload("res://Scenes/Popups/ItemTabContent.tscn")
var death_screen = preload("res://Scenes/Popups/DeathScreen.tscn")
var stat_scene = preload("res://Scenes/Popups/EscapeMenuStat.tscn")

var showing_breakdown = false

func _ready() -> void :
				var tab_index = 0
				var items = []
				for item in gear.get_children():
								items.append(item)
				var eq = GameState.get_equipped_skills()
				for item in items:
								var tab_content = tab_pane.instance()
								tab_content.item = item
								tab_container.add_child(tab_content)

								tab_container.set_tab_icon(tab_index, item.texture)
								tab_container.set_tab_title(tab_index, "")

								var button = Button.new()
								button.icon = item.texture
								button.connect("focus_entered", self, "_select", [tab_index])
								button.connect("pressed", self, "_select", [tab_index])
								tab_icon_container.add_child(button)
								button.rect_scale = Vector2(4.0, 4.0)
								button.rect_min_size = Vector2(64, 64)
								button.expand_icon = true
								button.icon_align = Button.ALIGN_CENTER

								tab_index += 1

				tab_icon_container.connect("focus_entered", self, "_focus_tab_zero")
				_focus_tab_zero()

				update_stats()

				if Levels.is_current_level_hideout():
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / AbandonButton.visible = false
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / MarginContainer / SettingsButton.focus_neighbour_right = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / BackToMenuButton.get_path()
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / CloseButton.focus_neighbour_left = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / BackToMenuButton.get_path()
				else:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / MarginContainer / SettingsButton.focus_neighbour_right = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / AbandonButton.get_path()
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / BackToMenuButton.visible = false

				render()

func render():
				var save_stats = GameState.get_active_stats()
				var active_class = save_stats.mutation_tree_loadout. class 
				var active_spec = save_stats.specialization_loadout. class 
				var active_class_name = PlayableClasses.get_class_name(active_class, active_spec)
				$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer2 / CharacterNameLabel.text = Globals.selected_character_name
				$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer2 / CharacterLevelLabel.text = "Level " + str(save_stats.account_level) + " " + active_class_name
				var helmet = Outfits.get_helmet(save_stats)
				$Viewport / BodyParts / PantsAttachment / HeadAttachment / HelmetSprite.frames = helmet
				var head = Outfits.get_head(save_stats)
				$Viewport / BodyParts / PantsAttachment / HeadAttachment / HeadSprite.frames = head
				var pants = Outfits.get_pants(save_stats)
				$Viewport / BodyParts / PantsAttachment / PantsSprite.frames = pants
				var hands = Outfits.get_hands(save_stats)
				$Viewport / BodyParts / PantsAttachment / LeftHand / Hand.frames = hands
				$Viewport / BodyParts / PantsAttachment / RightHand / Hand.frames = hands
				var feet = Outfits.get_feet(save_stats)
				$Viewport / BodyParts / PantsAttachment / LeftFoot / Foot.frames = feet
				$Viewport / BodyParts / PantsAttachment / RightFoot / Foot.frames = feet
				var back = Outfits.get_back(save_stats)
				$Viewport / BodyParts / PantsAttachment / BackSprite.frames = back

func _focus_tab_zero():
				if tab_icon_container.get_child_count() > 0:
								tab_icon_container.get_child(0).grab_focus()

func _process(delta: float) -> void :
				if Input.is_action_just_pressed("move_up"):
								if $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.has_focus():
												$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / AbandonButton.grab_focus()
								else:
												$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / CloseButton.grab_focus()

				if Input.is_action_pressed("gamepad_scroll_down"):
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / StatScroll.scroll_vertical += 3.0
				if Input.is_action_pressed("gamepad_scroll_up"):
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / StatScroll.scroll_vertical -= 3.0

				if Input.is_action_just_pressed("move_down"):
								var should_focus = true
								for child in $CenterContainer / PanelContainer / VBoxContainer / TabIconContainer.get_children():
												if child.has_focus():
																should_focus = false
																$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.grab_focus()
																break

								if not should_focus:
												_focus_tab_zero()

				if Input.is_action_just_pressed("ui_focus_prev") or Input.is_action_just_pressed("move_left") or Input.is_action_just_pressed("zoom_out"):
								if tab_container.get_focus_owner() == null and tab_container.get_tab_count() > 0:
												var next = (tab_container.get_tab_count() + tab_container.current_tab - 1) % tab_container.get_tab_count()
												tab_container.current_tab = next
				elif Input.is_action_just_pressed("ui_focus_next") or Input.is_action_just_pressed("move_right") or Input.is_action_just_pressed("zoom_in"):
								if tab_container.get_focus_owner() == null and tab_container.get_tab_count() > 0:
												var next = (tab_container.get_tab_count() + tab_container.current_tab + 1) % tab_container.get_tab_count()
												tab_container.current_tab = next

func _select(tab_index):
				tab_container.current_tab = tab_index

func _on_AbandonButton_pressed() -> void :
				var confirm_dialog = dialog.instance()
				confirm_dialog.window_title = "Are you sure?"
				confirm_dialog.connect("confirmed", self, "_on_confirm_abandon")
				add_child(confirm_dialog)
				confirm_dialog.popup_centered()

func _on_confirm_abandon():
				PopupManager.pop_popup()
				var instance = death_screen.instance()
				PopupManager.show_popup(instance, get_tree().get_root().get_node("World"))

func _on_CloseButton_pressed() -> void :
				PopupManager.pop_popup()

func _on_Button_pressed() -> void :
				var popup = settings.instance()
				PopupManager.show_popup(popup, self)

func _on_BreakdownButton_pressed() -> void :
				showing_breakdown = not showing_breakdown
				update_stats()

func update_stats():
				for c in stat_container.get_children():
								c.queue_free()
				if not showing_breakdown:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.text = "Details"
								for stat in StatsInfo.character_sheet_list:
												var label = stat_scene.instance()
												label.stat_name = StatsInfo.stat_name[stat] + ":"
												label.stat_value = StatsInfo.render_character_stat_line(stat, stats.gs(stat), stats)
												stat_container.add_child(label)
				else:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / HBoxContainer / BreakdownButton.text = "Hide"
								for stat in StatsInfo.character_sheet_list:
												var label
												if stat in StatsInfo.damage_list:

																var effective_multiplier = stats.base_stats[stat] * (1.0 + stats.gi(stat)) * (stats.gm(stat))

																if effective_multiplier != 1.0:
																				label = stat_scene.instance()
																				label.highlight = true
																				label.stat_name = StatsInfo.stat_name[stat] + ":"
																				label.stat_value = StatsInfo.render_character_stat_line(stat, effective_multiplier, stats, false)
																				stat_container.add_child(label)
																				label = stat_scene.instance()
																				label.stat_name = "Base " + StatsInfo.stat_name[stat] + ":"
																				label.stat_value = StatsInfo.render_character_stat_line(stat, stats.base_stats[stat], stats, false)
																				stat_container.add_child(label)
																				if stats.ga(stat) != 0.0:
																								
																								label = stat_scene.instance()
																								label.stat_name = "Added " + StatsInfo.stat_name[stat] + ":"
																								label.stat_value = str(stepify(stats.ga(stat), 0.1))
																								stat_container.add_child(label)
																				if stats.gi(stat) != 0.0:
																								label = stat_scene.instance()
																								label.stat_name = "Increased " + StatsInfo.stat_name[stat] + ":"
																								label.stat_value = str(stats.gi(stat) * 100.0) + "%"
																								stat_container.add_child(label)

																				if stats.gm(stat) != 1.0:
																								label = stat_scene.instance()
																								label.stat_name = "More " + StatsInfo.stat_name[stat] + ":"
																								label.stat_value = str((stats.gm(stat) - 1.0) * 100.0) + "%"
																								stat_container.add_child(label)

																				stat_container.add_child(HSeparator.new())
												else:
																if stats.gs(stat) == StatsInfo.defaults[stat]:
																				continue

																label = stat_scene.instance()
																label.highlight = true
																label.stat_name = StatsInfo.stat_name[stat] + ":"
																label.stat_value = StatsInfo.render_character_stat_line(stat, stats.gs(stat), stats)
																stat_container.add_child(label)

																label = stat_scene.instance()
																label.stat_name = "Base " + StatsInfo.stat_name[stat] + ":"
																label.stat_value = StatsInfo.render_character_stat_line(stat, stats.base_stats[stat], stats, false)
																stat_container.add_child(label)
																if stats.base_stats[stat] != stats.gs(stat):
																				if stats.ga(stat) != 0.0:
																								
																								label = stat_scene.instance()
																								label.stat_name = "Added " + StatsInfo.stat_name[stat] + ":"
																								label.stat_value = StatsInfo.render_character_stat_line(stat, stats.ga(stat), stats, false)
																								stat_container.add_child(label)

																				if stats.gi(stat) != 0.0:
																								label = stat_scene.instance()
																								label.stat_name = "Increased " + StatsInfo.stat_name[stat] + ":"
																								label.stat_value = str(stats.gi(stat) * 100.0) + "%"
																								stat_container.add_child(label)

																				if stats.gm(stat) != 1.0:
																								label = stat_scene.instance()
																								label.stat_name = "More " + StatsInfo.stat_name[stat] + ":"
																								label.stat_value = str((stats.gm(stat) - 1.0) * 100.0) + "%"
																								stat_container.add_child(label)

																stat_container.add_child(HSeparator.new())


func _on_BackToMenuButton_pressed() -> void :
				get_tree().change_scene("res://Scenes/Menu.tscn")


func _on_Button2_pressed() -> void :
				var popup = help.instance()
				PopupManager.show_popup(popup, self)


func _on_Button3_pressed() -> void :
				var popup = mod_help.instance()
				PopupManager.show_popup(popup, self)


func _on_Button4_pressed() -> void :
				var popup = unique_help.instance()
				PopupManager.show_popup(popup, self)
