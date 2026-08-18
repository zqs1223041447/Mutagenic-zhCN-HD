extends Button

var equip_sound = preload("res://Sounds/Misc/equip.wav")

signal focused
signal selected

var gene_id
var search_string = ""


func _ready() -> void :
				var gene = GameState.get_active_stats().genes[gene_id]
				icon = Genes.get_icon(gene_id)
				text = gene.name

				
				search_string = SearchUtils.get_search_string(gene_id)

				GameState.connect("seen_items_changed", self, "update_new_label")
				update_new_label()

func update_new_label():
				if GameState.is_gene_new(gene_id):
								$NewLabel.visible = true
				else:
								$NewLabel.visible = false

func _on_GeneOption_pressed() -> void :
				emit_signal("selected", gene_id)
				Globals.play_sound_effect(equip_sound)

func _on_GeneOption_mouse_entered() -> void :
				GameState.mark_gene_seen(gene_id)
				grab_focus()

func _on_GeneOption_focus_entered() -> void :
				GameState.mark_gene_seen(gene_id)
				emit_signal("focused", gene_id)

func set_search_regex(regex):
				if regex.search(search_string):
								visible = true
				else:
								visible = false

func clear_search_string():
				visible = true
