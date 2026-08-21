extends PopupBase

var gene_option = preload("res://scenes/Popups/Dialogs/GeneSelector/GeneOption.tscn")
var modline = preload("res://scenes/UI/ModItem.tscn")

@onready var genelist = $CenterContainer/GeneEditor/VBoxContainer/HBoxContainer/Vbox/ScrollContainer/GeneList
@onready var genestats = $CenterContainer/GeneEditor/VBoxContainer/HBoxContainer/VBoxContainer2/ScrollContainer/GeneStats
@onready var equipped_container = $CenterContainer/GeneEditor/VBoxContainer/HBoxContainer/Vbox/EquippedContainer
@onready var equipped_list = $CenterContainer/GeneEditor/VBoxContainer/HBoxContainer/Vbox/EquippedContainer/EquippedList



@export var gene_loadout_name = ""
@export var gene_loadout_slot = 0
@export var gene_loadout_type = ""

func _ready():
				GameState.connect("settings_changed", Callable(self, "render"))
				
				$CenterContainer/GeneEditor/VBoxContainer/HBoxContainer2/CancelButton.grab_focus()
				render()

func render():
				
				
				var loadout = GameState.get_current_gene_loadout()

				var all_available_genes = GameState.get_genes_of_slot(gene_loadout_type).duplicate()
				var existing_genes_of_type = loadout[gene_loadout_type].values()

				var filtered = []
				var in_use = []
				for id in all_available_genes:
								if id in existing_genes_of_type:
												in_use.append(id)
												continue

								if GameState.saved_stats.settings.hide_low_level:
												var item = GameState.get_active_stats().genes[id]
												var item_level = item.level
												if Filters.should_hide_item(item):
																continue
								filtered.append(id)

				render_in_use(in_use)
				render_available_genes(filtered)
				$CenterContainer/GeneEditor/VBoxContainer/HBoxContainer3/HideLowLevelToggle.pressed = GameState.saved_stats.settings.hide_low_level

				if loadout[gene_loadout_type][gene_loadout_slot] != null:
								$CenterContainer/GeneEditor/VBoxContainer/HBoxContainer2/HBoxContainer/RemoveButton.visible = true
				else:
								$CenterContainer/GeneEditor/VBoxContainer/HBoxContainer2/HBoxContainer/RemoveButton.visible = false


func close():
				call_deferred("queue_free")

func _process(_delta) -> void :
				if Input.is_action_just_pressed("ui_cancel"):
								close()

func _sort_genes(a, b):
				var lvla = GameState.get_active_stats().genes[a]
				var lvlb = GameState.get_active_stats().genes[b]
				return lvla.level > lvlb.level

func render_available_genes(ids: Array):
				for child in genelist.get_children():
								child.queue_free()

				ids.sort_custom(self, "_sort_genes")
				for id in ids:
								var opt = gene_option.instantiate()
								opt.gene_id = id
								opt.connect("selected", Callable(self, "_on_select"))
								opt.connect("focused", Callable(self, "_render_gene_stats"))
								$CenterContainer/GeneEditor/VBoxContainer/HBoxContainer/Vbox/ScrollContainer/GeneList.add_child(opt)

func render_in_use(ids):
				if len(ids) == 0:
								equipped_container.visible = false
				for child in equipped_list.get_children():
								child.queue_free()
				for id in ids:
								var opt = gene_option.instantiate()
								opt.gene_id = id
								opt.disabled = true
								opt.connect("focused", Callable(self, "_render_gene_stats"))
								equipped_list.add_child(opt)

func _on_select(gene_id):
				GameState.equip_gene(gene_loadout_type, gene_loadout_slot, gene_id)
				close()

func _render_gene_stats(gene_id):
				for child in genestats.get_children():
								child.queue_free()

				if gene_id == null:
								return

				var gene = GameState.get_active_stats().genes[gene_id]

				var item_level_label = Label.new()
				item_level_label.align = Label.ALIGN_CENTER
				item_level_label.text = "Item Level: " + str(gene.level)
				genestats.add_child(item_level_label)

				
				var mod_config_type = Genes.mods_for_base_type(gene.type)
				var drop_only_mod_config_type = Genes.drop_only_mods_for_base_type(gene.type)
				for mod in gene.implicits:
								var label = modline.instantiate()
								label.gene = gene
								label.mod = mod
								label.show_advanced = false
								label.is_implicit = true
								genestats.add_child(label)
								if len(gene.implicits) > 0:
												genestats.add_child(HSeparator.new())
				for mod in gene.prefixes:
								var label = modline.instantiate()
								label.gene = gene
								label.mod = mod
								label.show_advanced = false
								genestats.add_child(label)
				for mod in gene.suffixes:
								var label = modline.instantiate()
								label.gene = gene
								label.mod = mod
								label.show_advanced = false
								genestats.add_child(label)

func _on_CancelButton_pressed() -> void :
				close()

func _on_RemoveButton_pressed() -> void :
				GameState.unequip_gene(gene_loadout_type, gene_loadout_slot)
				close()

func _on_CancelButton_focus_entered() -> void :
				_render_gene_stats(null)

func _on_CancelButton_mouse_entered() -> void :
				$CenterContainer/GeneEditor/VBoxContainer/HBoxContainer2/CancelButton.grab_focus()

func _unhandled_key_input(event: InputEventKey) -> void :
				if event.scancode == KEY_F:
								if Input.is_key_pressed(KEY_SHIFT):
												$CenterContainer/GeneEditor/VBoxContainer/HBoxContainer3/LineEdit.grab_focus()

func _on_LineEdit_text_changed(new_text: String) -> void :
				
				if new_text == "" or not new_text or len(new_text) == 0:
								for child in genelist.get_children():
												child.clear_search_string()
				else:
								var regex = RegEx.new()
								regex.compile(new_text)
								for child in genelist.get_children():
												child.set_search_regex(regex)

func _on_HideLowLevelToggle_toggled(button_pressed: bool) -> void :
				GameState.set_hide_low_level(button_pressed)
