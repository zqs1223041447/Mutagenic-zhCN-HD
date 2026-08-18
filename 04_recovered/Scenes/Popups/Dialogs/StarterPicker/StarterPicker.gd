extends PopupBase

var starter_option = preload("res://Scenes/Popups/Dialogs/StarterPicker/StarterOption.tscn")

func _ready() -> void :

				var starter_options = StarterBuilds.get_starters_for_class(
								GameState.get_active_stats().mutation_tree_loadout. class 
				)

				for option in starter_options:
								var inst = starter_option.instance()
								inst.template_id = option
								$MarginContainer / CenterContainer / PanelContainer / VBoxContainer2 / VBoxContainer / StarterOptions.add_child(inst)
