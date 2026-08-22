extends PopupBase

signal equip_skill(skill_name)

var option = preload("res://scenes/Popups/Dialogs/SkillSelect/SkillListOption.tscn")

@onready var grid = $MarginContainer/CenterContainer/PanelContainer/HBoxContainer/VBoxContainer2/GridContainer
@onready var content = $MarginContainer/CenterContainer/PanelContainer/HBoxContainer/VBoxContainer/ScrollContainer/StatList

func sort_skills(first, second):
				var a = Skills.config[first]
				var b = Skills.config[second]
				if a.tags.has(SkillTags.Tags.DAMAGING):
								if b.tags.has(SkillTags.Tags.DAMAGING):
												return a.name < b.name
								else:
												return true

				if b.tags.has(SkillTags.Tags.DAMAGING):
								if a.tags.has(SkillTags.Tags.DAMAGING):
												return b.name < a.name
								else:
												return false

func _ready() -> void :

				var skill_options = []
				for skill_name in Skills.config.keys():
								if Skills.config[skill_name].playable:
												skill_options.append(skill_name)

				skill_options.sort_custom(Callable(self, "sort_skills"))

				for skill_name in skill_options:
								var button = option.instantiate()
								button.skill_name = skill_name
								button.connect("focus_entered", Callable(Callable(self, "select_skill")).bind(skill_name))
								button.connect("button_down", Callable(Callable(self, "request_equip_skill")).bind(skill_name))
								grid.add_child(button)

				_grab_focus()

func _grab_focus():
				if grid.get_child_count() > 0:
								grid.get_child(0).grab_focus()

func select_skill(skill_name):
				var info = Skills.config[skill_name]
				$MarginContainer/CenterContainer/PanelContainer/HBoxContainer/VBoxContainer/NameLabel.text = info.name
				$MarginContainer/CenterContainer/PanelContainer/HBoxContainer/VBoxContainer/TagLabel.text = SkillTags.get_tag_list(skill_name)
				$MarginContainer/CenterContainer/PanelContainer/HBoxContainer/VBoxContainer/DescriptionLabel.text = info.description


				content.clear()

				var current_tier = Skills.tier_for_level(GameState.get_account_level())

				var tier_info = Skills.tiers[skill_name].tiers[current_tier]
				content.newline()
				if tier_info.has("skill"):
								content.push_color(Colors.keystone)
								content.add_text("Skill Stats")
								content.pop()
								content.newline()
								for stat in tier_info.skill:
												var effective_stat = tier_info.skill[stat]
												var stat_name = StatsInfo.stat_name[stat]

												if stat == "cooldown" and info.tags.has(SkillTags.Tags.DOT):
																continue

												if typeof(effective_stat) == TYPE_FLOAT or typeof(effective_stat) == TYPE_INT:
																if effective_stat == 0:
																				continue
																content.add_text(stat_name + ": " + StatsInfo.render_skill_stat_line(stat, effective_stat))
												elif typeof(effective_stat) == TYPE_DICTIONARY:
																content.add_text(stat_name + ": ")
																for item in effective_stat:
																				content.push_color(Colors.color_for_skill_tag[item])
																				content.add_text(" [" + str(snapped(effective_stat[item], 0.1)) + " " + SkillTags.TagNames[item] + "]")
																				content.pop()
												content.newline()

				if tier_info.has("aura"):
								content.newline()
								content.push_color(Colors.keystone)
								content.add_text("Aura Effects")
								content.pop()
								for stat in tier_info.aura:
												for item in tier_info.aura[stat]:
																content.newline()
																var stat_name = StatsInfo.stat_name[stat]

																content.add_text(StatsInfo.render_passive_stat_line(stat, {"amount": item.amount, "scaling_type": item.type}))


# Godot 4: a function may not share its name with the equip_skill signal
# (Godot 3 allowed it); renamed so the signal declaration stays authoritative.
func request_equip_skill(skill_name):
				emit_signal("equip_skill", skill_name)
				PopupManager.pop_popup()

func _on_Button_pressed() -> void :
				PopupManager.pop_popup()


func _on_ClearButton_pressed() -> void :
				request_equip_skill(null)
