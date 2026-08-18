extends HBoxContainer

signal select_gene_type

var confirm_dialog = preload("res://Scenes/Popups/Dialogs/TintedConfirmationDialog.tscn")

var quit_icon = preload("res://sprites/gui/quit.png")
var keep_icon = preload("res://sprites/gui/active.png")

var text_popup = preload("res://Scenes/Popups/Dialogs/TextInputDialog.tscn")
var editor = preload("res://Scenes/Popups/Dialogs/GeneEditor/GeneEditor.tscn")

onready var tooltip = $GeneButton / GeneTooltip
onready var button = $GeneButton

var gene_id
var is_in_shared = false
var action_transfer = false
var focused
var popup_parent = null
var search_string = ""


func _ready() -> void :
				_update_name()
				GameState.connect("settings_changed", self, "_check_visibility")
				GameState.connect("seen_items_changed", self, "update_seen_label")
				Globals.connect("search_changed", self, "_check_search")

				search_string = SearchUtils.get_search_string(gene_id)

				_check_visibility()


				if not is_in_shared:
								if GameState.is_gene_equipped(gene_id):
												$GeneButton / EquippedIcon.visible = true

				update_seen_label()

func update_seen_label():
				if not is_in_shared:
								if GameState.is_gene_new(gene_id):
												$GeneButton / NewLabel.visible = true
								else:
												$GeneButton / NewLabel.visible = false

func _check_visibility():
				if is_in_shared:
								pass
				else:
								var item = GameState.get_active_stats().genes[gene_id]
								if Filters.should_hide_item(item) and not GameState.is_gene_equipped(gene_id):
												visible = false
								else:
												visible = true

								

func _check_search(ss):
				_check_visibility()
				modulate = Color.white
				if ss and len(ss) > 2:
								if not (ss in search_string):
												modulate = Color(1, 1, 1, 0.1)

func _update_name():
				if is_in_shared:
								var gene = GameState.saved_stats.shared_stash[gene_id]
								if gene:
												var icon_tex = Genes.get_icon(gene_id, true)
												button.icon = icon_tex
												button.set("custom_colors/font_color", Colors.unequipped)
				else:
								var gene = GameState.get_active_stats().genes[gene_id]
								if gene:
												var icon_tex = Genes.get_icon(gene_id)
												button.icon = icon_tex
												if GameState.is_gene_equipped(gene_id):
																button.set("custom_colors/font_color", Colors.equipped)
												else:
																button.set("custom_colors/font_color", Colors.unequipped)

func _on_GeneButton_pressed() -> void :
				if action_transfer:
								if is_in_shared:
												GameState.move_to_local_stash(gene_id)
								else:
												
												GameState.move_to_shared_stash(gene_id)
				else:
								var popup = editor.instance()
								popup.gene_id = gene_id
								popup.connect("destroy", self, "_select")
								if popup_parent:
												PopupManager.show_popup(popup, popup_parent)
								else:
												PopupManager.show_popup(popup, self)

func _select():
				if Genes.is_gene_valid(gene_id):
								button.grab_focus()
								tooltip.visible = false
				else:
								
								emit_signal("select_gene_type")


func _on_GeneButton_focus_entered() -> void :
				if not is_in_shared:
								GameState.mark_gene_seen(gene_id)
				tooltip.render(gene_id, rect_global_position, rect_size, is_in_shared)

func _on_GeneButton_focus_exited() -> void :
				tooltip.visible = false

func _on_GeneButton_mouse_entered() -> void :
				button.grab_focus()

func _on_GeneButton_mouse_exited() -> void :
				tooltip.visible = false
				button.release_focus()

func _on_GeneButton_gui_input(event: InputEvent) -> void :
				if is_in_shared:
								return
				if event is InputEventMouseButton and event.is_pressed():
								match event.button_index:
												BUTTON_RIGHT:
																var gene = GameState.get_active_stats().genes[gene_id]
																if gene and not gene.unique:
																				quick_delete()

func quick_delete():
				var gene = GameState.get_active_stats().genes[gene_id]
				if gene:
								var popup = confirm_dialog.instance()
								popup.window_title = "Permanently Delete this Item?"
								popup.connect("confirmed", self, "_on_delete_gene")
								add_child(popup)
								popup.popup_centered()

func _on_delete_gene():
				Genes.delete_gene(gene_id)
