extends PopupBase

var option = preload("res://scenes/Popups/Dialogs/SpecializationPicker/SpecializationOption.tscn")
var help_tip = preload("res://scenes/Popups/Dialogs/HelpTip/SpecializationTip/SpecializationTip.tscn")

func _ready() -> void :
				var st = GameState.get_active_stats()
				if st.account_level >= 30:
								$MarginContainer/CenterContainer/PanelContainer/Available.visible = true
								var active_class = st.mutation_tree_loadout. class 
								if active_class:
												var available_specializations = PlayableClasses.specializations_for_class[active_class]
												for spec in available_specializations:
																var op = option.instantiate()
																op.specialization_class = spec
																$MarginContainer/CenterContainer/PanelContainer/Available/SpecializationOptions.add_child(op)
								else:
												print("No mutation tree class found. Error!")
								if not GameState.is_help_tip_read("specialization_intro"):
												GameState.mark_help_tip_read("specialization_intro")
												var popup = help_tip.instantiate()
												PopupManager.show_popup(popup, self)
				else:
								$MarginContainer/CenterContainer/PanelContainer/Unavailable.visible = true
