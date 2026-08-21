extends PanelContainer

var gene_selector = preload("res://scenes/Popups/Dialogs/GeneSelector/GeneSelector.tscn")

@onready var tooltip = $GeneTooltip

@export var gene_type = ""
@export var slot_id = ""

var gene_id = null

func _ready() -> void :
				GameState.connect("gene_loadout_changed", Callable(self, "render"))
				GameState.connect("seen_items_changed", Callable(self, "update_seen_label"))
				render()
				update_seen_label()

func update_seen_label():
				if GameState.is_gene_type_new(gene_type):
								$Control/NewLabel.visible = true
				else:
								$Control/NewLabel.visible = false


func render():
				$Button/PanelContainer/TextureRect.texture = Genes.icon_for_gene_slot[gene_type]
				var current_gene_loadout = GameState.get_current_gene_loadout()
				if current_gene_loadout:
								visible = true
								if current_gene_loadout[gene_type][slot_id] == null:
												
												$Button.modulate = Color(1.0, 1.0, 1.0, 0.3)
												gene_id = null
								else:
												$Button.modulate = Color.WHITE
												gene_id = current_gene_loadout[gene_type][slot_id]
												var icon = Genes.get_icon(gene_id)
												$Button/PanelContainer/TextureRect.texture = icon
				else:
								gene_id = null
								visible = false

func _on_Button_pressed() -> void :
				GameState.mark_gene_type_seen(gene_type)
				var selector = gene_selector.instantiate()
				selector.gene_loadout_slot = slot_id
				selector.gene_loadout_type = gene_type
				selector.connect("destroy", Callable(self, "_select"))
				PopupManager.show_popup(selector, self)

func _select():
				$Button.grab_focus()

func _on_Button_focus_entered() -> void :
				tooltip.render(gene_id, rect_global_position, rect_size)

func _on_Button_focus_exited() -> void :
				$GeneTooltip.visible = false

func _on_Button_mouse_exited() -> void :
				$GeneTooltip.visible = false
				$Button.release_focus()

func _on_Button_mouse_entered() -> void :
				if not $Button.has_focus():
								$Button.grab_focus()
