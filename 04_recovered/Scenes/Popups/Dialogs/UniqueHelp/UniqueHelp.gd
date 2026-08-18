extends PopupBase

var unique_item_scene = preload("res://Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.tscn")

onready var content_container = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / TabContainer
onready var content = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / TabContainer / ModContent
onready var tree = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer2 / ModTree


func _ready() -> void :
				$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / BackButton.grab_focus()

				var root = tree.create_item()
				tree.hide_root = true

				for slot_type in Genes.base_types_for_slot.keys():
								var slot_root = tree.create_item(root)
								slot_root.set_text(0, Genes.name_for_gene_type[slot_type])
								slot_root.set_metadata(0, slot_type)
								slot_root.collapsed = true

				tree.connect("item_selected", self, "_on_item_selected")

				tree.get_root().get_children().select(0)


func _on_item_selected():
				var item_selected = tree.get_selected()
				var slot = item_selected.get_metadata(0)
				if slot:
								render_items(slot)
				else:
								item_selected.collapsed = false

func _physics_process(delta: float) -> void :
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
								if not tree.has_focus():
												content_container.scroll_vertical += 15
				if Input.is_action_pressed("move_up"):
								if not tree.has_focus():
												content_container.scroll_vertical -= 15

func _on_Button_pressed() -> void :
				PopupManager.pop_popup()

func render_items(slot):
				for child in content.get_children():
								child.queue_free()
				
				var unique_ids = UniqueGenes.get_unique_ids_for_slot(slot)
				for id in unique_ids:
								var item = unique_item_scene.instance()
								item.unique_id = id
								content.add_child(item)

func _on_LineEdit_text_changed(new_text: String) -> void :
				Globals.update_search(new_text)
