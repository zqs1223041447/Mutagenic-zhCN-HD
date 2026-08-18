extends PopupBase


var dialog = preload("res://Scenes/Popups/Dialogs/TintedConfirmationDialog.tscn")
var helptip = preload("res://Scenes/Popups/Dialogs/HelpTip/CraftingHelp/CraftingHelp.tscn")

var modline = preload("res://Scenes/UI/ModItem.tscn")

onready var name_edit = $GeneEditor / VBoxContainer / HBoxContainer / HBoxContainer / NameEdit
onready var stored_stats = $GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer / PanelContainer2 / ScrollContainer / StoredStatList
onready var gene_stats = $GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer / PanelContainer3 / ScrollContainer / GeneStatList
onready var implicit_stats = $GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / ImplicitInfo
var gene_id


func _ready() -> void :
				Genes.connect("gene_edited", self, "render")
				GameState.connect("settings_changed", self, "_on_settings_changed")
				GameState.connect("changed", self, "_update_resources")
				_on_settings_changed()

				var gene = GameState.get_active_stats().genes[gene_id]

				if gene.has("unique") and gene.unique:
								if gene.has("unique_id"):
												var unique_meta = UniqueGenes.get_unique_data(gene.unique_id)
												$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / UniqueNameLabel.visible = true
												$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / UniqueNameLabel.text = unique_meta.name
								name_edit.editable = false

				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / CenterContainer / IconTexture.texture = Genes.get_icon(gene_id)

				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / ScrambleButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / ScrambleLuckyButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / ScrambleUltraButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / ScramblePrefixesButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / ScrambleSuffixesButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / RestoreButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / ExtractButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer / RecombinateButton.set_gene_id(gene_id)


				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer3 / CosmicButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer3 / RemoveModButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer3 / AddModButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer3 / UpgradeTierButton.set_gene_id(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer3 / LockModButton.set_gene_id(gene_id)

				$GeneEditor / VBoxContainer / HBoxContainer / CancelButton.grab_focus()

				_update_resources()
				$GeneEditor / VBoxContainer / HBoxContainer / HBoxContainer / NameEdit.text = gene.name


func _process(delta: float) -> void :
				if Input.is_action_just_pressed("ui_cancel"):
								close()

func _update_resources():
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer4 / VBoxContainer / BlueOrbLabel.text = str(GameState.get_active_stats().orbs.blue)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer4 / VBoxContainer2 / RedOrbLabel.text = str(GameState.get_active_stats().orbs.red)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer4 / VBoxContainer3 / GreenOrbLabel.text = str(GameState.get_active_stats().orbs.green)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer4 / VBoxContainer4 / GoldOrbLabel.text = str(GameState.get_active_stats().orbs.gold)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer4 / VBoxContainer5 / CorruptionLabel.text = str(GameState.get_active_stats().orbs.corruption)

func close() -> void :
				queue_free()

func render():
				var gene = GameState.get_active_stats().genes[gene_id]
				if gene == null:
								print("Failed to get gene, does not exist: ", gene_id)
								get_tree().quit()

				var icon = Genes.get_icon(gene_id)
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / CenterContainer / IconTexture.texture = icon
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / GeneLevelLabel.text = "Item Level: " + str(gene.level)

				
				if gene.has("quality") and gene.quality > 0:
								$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / GeneQualityLabel.visible = true
								$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / GeneQualityLabel.text = "+" + str(gene.quality) + "% Affix Effectiveness"

				render_gene_list()
				render_stored_list()

func render_gene_list():
				var gene = GameState.get_active_stats().genes[gene_id]
				for child in implicit_stats.get_children():
								child.queue_free()
				for child in gene_stats.get_children():
								child.queue_free()
				var show_advanced = GameState.saved_stats.settings.show_advanced_mods

				for mod in gene.implicits:
								var label = modline.instance()
								label.gene_id = gene_id
								label.mod = mod
								label.show_advanced = show_advanced
								label.is_implicit = true
								implicit_stats.add_child(label)

				for mod in gene.prefixes:
								var label = modline.instance()
								label.gene_id = gene_id
								label.mod = mod
								label.show_advanced = show_advanced
								gene_stats.add_child(label)
				gene_stats.add_child(HSeparator.new())
				for mod in gene.suffixes:
								var label = modline.instance()
								label.gene_id = gene_id
								label.mod = mod
								label.show_advanced = show_advanced
								gene_stats.add_child(label)

func render_stored_list():
				var gene = GameState.get_active_stats().genes[gene_id]
				for child in stored_stats.get_children():
								child.queue_free()
				var show_advanced = GameState.saved_stats.settings.show_advanced_mods
				var stored_mods = null
				if GameState.get_active_stats().stored_mods.has(gene.type):
								stored_mods = GameState.get_active_stats().stored_mods[gene.type]

				if stored_mods:
								for mod in stored_mods.prefixes:
												var label = modline.instance()
												label.gene_id = gene_id
												label.mod = mod
												label.show_advanced = show_advanced
												stored_stats.add_child(label)
								stored_stats.add_child(HSeparator.new())
								for mod in stored_mods.suffixes:
												var label = modline.instance()
												label.gene_id = gene_id
												label.mod = mod
												label.show_advanced = show_advanced
												stored_stats.add_child(label)
				else:
								print("No stored mods: ", gene)

func _on_CancelButton_pressed() -> void :
				close()

func _on_CheckBox_toggled(button_pressed: bool) -> void :
				GameState.set_advanced_mods(button_pressed)

func _on_LineEdit_text_changed(new_text: String) -> void :
				Genes.rename_gene(gene_id, new_text)

func _on_settings_changed():
				$GeneEditor / VBoxContainer / HBoxContainer2 / VBoxContainer2 / HBoxContainer3 / AdvancedToggle.pressed = GameState.saved_stats.settings.show_advanced_mods
				render()


func _on_Button_pressed() -> void :
				var confirm_dialog = dialog.instance()
				confirm_dialog.window_title = "Permanently Delete this Item?"
				confirm_dialog.connect("confirmed", self, "_on_delete_gene")
				add_child(confirm_dialog)
				confirm_dialog.popup_centered()

func _on_delete_gene():
				Genes.delete_gene(gene_id)
				close()

func _on_CraftingHelpButton_pressed() -> void :
				var popup = helptip.instance()
				PopupManager.show_popup(popup, self)
