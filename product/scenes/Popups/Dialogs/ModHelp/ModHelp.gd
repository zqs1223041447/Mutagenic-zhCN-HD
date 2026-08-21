extends PopupBase

var mod_tab = preload("res://scenes/Popups/Dialogs/ModHelp/ModTab.tscn")

@onready var content_container = $CenterContainer/PanelContainer/VBoxContainer/HBoxContainer2/TabContainer
@onready var content = $CenterContainer/PanelContainer/VBoxContainer/HBoxContainer2/TabContainer/ModContent
@onready var tree = $CenterContainer/PanelContainer/VBoxContainer/HBoxContainer2/ModTree
@onready var searcher = $CenterContainer/PanelContainer/VBoxContainer/HBoxContainer/HBoxContainer/Searcher


func _ready() -> void :
				$CenterContainer/PanelContainer/VBoxContainer/HBoxContainer/BackButton.grab_focus()

				var root = tree.create_item()
				tree.hide_root = true
				for slot_type in Genes.base_types_for_slot.keys():
								var slot_root = tree.create_item(root)
								slot_root.set_text(0, Genes.name_for_gene_type[slot_type])
								for base_type in Genes.base_types_for_slot[slot_type]:
												var base_item = tree.create_item(slot_root)
												base_item.set_text(0, Genes.name_for_base_type[base_type])
												base_item.set_metadata(0, base_type)
								slot_root.collapsed = true

				tree.connect("item_selected", Callable(self, "_on_item_selected"))

				tree.get_root().get_children().select(0)
				tree.get_selected().get_children().select(0)


func _on_item_selected():
				var item_selected = tree.get_selected()
				var base_type = item_selected.get_metadata(0)
				if base_type:
								render_mods(base_type)
				else:
								item_selected.collapsed = false

func _physics_process(delta: float) -> void :
				if not searcher.has_focus():
								if Input.is_action_just_pressed("move_down"):
												if tree.has_focus():
																var next = tree.get_selected()
																if next:
																				if next.get_children():
																								next.get_children().select(0)
																				elif next and next.get_next():
																								next.get_next().select(0)
																				else:
																								var parent = next.get_parent()
																								if parent and parent.get_next():
																												parent.get_next().select(0)
																else:
																				tree.get_root().select(0)
								if Input.is_action_just_pressed("move_up"):
												if tree.has_focus():
																var next = tree.get_selected()
																if next and next.get_prev():
																				next.get_prev().select(0)
																else:
																				var parent = next.get_parent()
																				if parent and parent != tree.get_root():
																								parent.select(0)

								if Input.is_action_pressed("move_down"):
												if not tree.has_focus() and not searcher.has_focus():
																content_container.scroll_vertical += 15
								if Input.is_action_pressed("move_up"):
												if not tree.has_focus() and not searcher.has_focus():
																content_container.scroll_vertical -= 15

				if Input.is_key_pressed(KEY_F):
								if Input.is_key_pressed(KEY_CTRL):
												searcher.grab_focus()
												searcher.select_all()

func _on_Button_pressed() -> void :
				PopupManager.pop_popup()

func render_mods(base_type):
				for child in content.get_children():
								child.queue_free()
				var tab = mod_tab.instantiate()
				tab.base_type = base_type
				content.add_child(tab)

func _on_LineEdit_text_changed(new_text: String) -> void :
				Globals.update_search(new_text)
