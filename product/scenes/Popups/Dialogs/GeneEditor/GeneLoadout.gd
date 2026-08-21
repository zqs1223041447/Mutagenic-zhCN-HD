extends PopupBase

var text_input_dialog = preload("res://scenes/Popups/Dialogs/TextInputDialog.tscn")
var help_tip = preload("res://scenes/Popups/Dialogs/HelpTip/LoadoutScreenTip/LoadoutScreenTip.tscn")

@onready var stat_container = $CenterContainer/PanelContainer/VBoxContainer/HBoxContainer/LoadoutStatsContainer/ScrollContainer/LoadoutStats

func _ready() -> void :
				GameState.connect("gene_loadout_changed", Callable(self, "_on_loadout_changed"))
				_on_loadout_changed()

				$CenterContainer/PanelContainer/VBoxContainer/Controls/VBoxContainer/HBoxContainer/BackButton.grab_focus()

				if not GameState.is_help_tip_read("loadout_info"):
								GameState.mark_help_tip_read("loadout_info")
								var popup = help_tip.instantiate()
								PopupManager.show_popup(popup, self)

func _on_BackButton_pressed() -> void :
				PopupManager.pop_popup()

func _refocus():
				$CenterContainer/PanelContainer/VBoxContainer/Controls/VBoxContainer/HBoxContainer/BackButton.grab_focus()

func _on_loadout_changed():
				var loadout_stats = GameState.collect_gene_loadout_buffs()
				render_loadout_stats(loadout_stats)

func clear_loadout_stats():
				for child in stat_container.get_children():
								child.queue_free()

func render_loadout_stats(applied_stats):
				clear_loadout_stats()
				for keystone in applied_stats.keystones:
								var label = Label.new()
								label.autowrap = true
								label.align = HORIZONTAL_ALIGNMENT_CENTER
								label.text = Keystones.keystones[keystone].name
								label.modulate = Colors.keystone
								stat_container.add_child(label)
								label = Label.new()
								label.autowrap = true
								label.align = HORIZONTAL_ALIGNMENT_CENTER
								label.text = Keystones.keystones[keystone].description
								label.modulate = Colors.keystone_description
								stat_container.add_child(label)

				for stat in StatsInfo.stat_list:
								if applied_stats.stats.has(stat):
												var stat_config = applied_stats.stats[stat]
												for scaling_type in stat_config:
																var label = Label.new()
																label.autowrap = true
																label.align = HORIZONTAL_ALIGNMENT_CENTER
																label.text = StatsInfo.render_passive_stat_line(stat, {
																				"scaling_type": scaling_type, 
																				"amount": stat_config[scaling_type]
																})
																stat_container.add_child(label)

				for stat in StatsInfo.stat_list:
								var tagged_stats = applied_stats.conditional_stats
								for damage_type in tagged_stats:
												var stats_for_type = tagged_stats[damage_type]
												if stats_for_type.has(stat):
																var stat_config = stats_for_type[stat]
																for scaling_type in stat_config:
																				var label = Label.new()
																				label.align = HORIZONTAL_ALIGNMENT_CENTER
																				label.autowrap = true
																				label.text = StatsInfo.render_passive_stat_line(stat, {
																								"scaling_type": scaling_type, 
																								"amount": stat_config[scaling_type], 
																								"tags": [damage_type]
																				})
																				stat_container.add_child(label)


func _on_RenameLoadoutButton_pressed() -> void :
				var popup = text_input_dialog.instantiate()
				popup.title = "Rename \"" + GameState.get_active_stats().selected_gene_loadout + "\""
				popup.label = "New Name"
				popup.prefill = GameState.get_active_stats().selected_gene_loadout
				popup.connect("text_entered", Callable(self, "_rename_loadout"))
				popup.connect("destroy", Callable(self, "_refocus_rename"))
				PopupManager.show_popup(popup, self)

func _rename_loadout(new_name):
				GameState.rename_loadout(GameState.get_active_stats().selected_gene_loadout, new_name)

func _refocus_rename():
				$CenterContainer/PanelContainer/VBoxContainer/Controls/VBoxContainer/HBoxContainer/RenameLoadoutButton.grab_focus()
