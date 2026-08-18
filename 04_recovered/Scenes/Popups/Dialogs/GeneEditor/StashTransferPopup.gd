extends PopupBase

onready var gene_list = $GeneInventory / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer / ScrollContainer2 / Items
onready var shared_list = $GeneInventory / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / VBoxContainer2 / ScrollContainer2 / Items
onready var backbutton = $GeneInventory / CenterContainer / PanelContainer / VBoxContainer / Controls / BackButton

var item_list = preload("res://Scenes/Popups/Dialogs/GeneEditor/ItemList.tscn")

func _ready():
				render_genes()
				Genes.connect("genes_changed", self, "render_genes")
				GameState.connect("genes_changed", self, "render_genes")
				backbutton.grab_focus()
				$GeneInventory / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer3 / HideLowLevelToggle.pressed = GameState.saved_stats.settings.hide_low_level


func _process(delta: float) -> void :
				if Input.is_action_just_pressed("ui_cancel"):
								PopupManager.pop_popup()

func _on_BackButton_pressed() -> void :
				PopupManager.pop_popup()

func render_genes():
				for child in gene_list.get_children():
								child.queue_free()
				for child in shared_list.get_children():
								child.queue_free()

				for slot in Genes.GeneSlot.values():
								var itemlist = item_list.instance()
								itemlist.slot = slot
								itemlist.is_shared = false
								itemlist.action_transfer = true
								gene_list.add_child(itemlist)

				for slot in Genes.GeneSlot.values():
								var itemlist = item_list.instance()
								itemlist.slot = slot
								itemlist.is_shared = true
								itemlist.action_transfer = true
								shared_list.add_child(itemlist)

func select_button(button):
				button.grab_focus()

func _on_HideLowLevelToggle_toggled(button_pressed: bool) -> void :
				GameState.set_hide_low_level(button_pressed)
