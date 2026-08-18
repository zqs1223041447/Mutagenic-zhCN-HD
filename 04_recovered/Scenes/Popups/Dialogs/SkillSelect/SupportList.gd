extends PopupBase

signal equip_support(support_name, slot)

var option = preload("res://Scenes/Popups/Dialogs/SkillSelect/SupportListOption.tscn")
var skill_slot = "primary"

onready var grid = $MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer2 / GridContainer
onready var statlist = $MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / StatList

func _ready() -> void :
				
				for support in SkillSupports.supports:


								if not GameState.is_support_allowed(skill_slot, support):
												continue

								var button = option.instance()
								button.support_name = support
								button.connect("focus_entered", self, "select_support", [support])
								button.connect("button_down", self, "equip_support", [support])
								if GameState.is_support_equipped(skill_slot, support):
												button.disabled = true
								grid.add_child(button)

				_grab_focus()

func _grab_focus():
				if grid.get_child_count() > 0:
								grid.get_child(0).grab_focus()

func select_support(support):
				var info = SkillSupports.supports[support]
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / NameLabel.text = info.name
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / DescriptionLabel.text = info.description
				
				for child in statlist.get_children():
								child.queue_free()

				if info.has("keystones"):
								for keystone in info.keystones:
												var keystone_info = Keystones.keystones[keystone]
												var label = Label.new()
												label.text = keystone_info.description
												label.autowrap = true
												statlist.add_child(label)

				for stat in info.stats:
								var label = Label.new()
								label.text = StatsInfo.render_passive_stat_line(stat.stat, stat)
								label.autowrap = true
								statlist.add_child(label)

func equip_support(support):
				emit_signal("equip_support", support)
				PopupManager.pop_popup()

func _on_CancelButton_pressed() -> void :
				PopupManager.pop_popup()

func _on_ClearButton_pressed() -> void :
				equip_support(null)

func _on_LineEdit_text_changed(new_text):
				var lowered = new_text.to_lower()
				for child in grid.get_children():
								child.set_filter(lowered)
