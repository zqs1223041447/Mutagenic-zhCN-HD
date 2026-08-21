extends VBoxContainer

var gene_button = preload("res://scenes/Popups/Dialogs/GeneEditor/GeneButton.tscn")

var slot
var is_shared = false
var action_transfer = false

func gene_sorter(a, b):
				var gene_a = GameState.get_active_stats().genes[a]
				var gene_b = GameState.get_active_stats().genes[b]
				var slot_a = Genes.slot_for_base(gene_a.type)
				var slot_b = Genes.slot_for_base(gene_b.type)
				var unique_a = gene_a.unique
				var unique_b = gene_b.unique

				if slot_a == slot_b:
								if unique_a > unique_b:
												return true
								if unique_b > unique_a:
												return false
								return gene_a.level > gene_b.level

				return slot_a < slot_b

func shared_gene_sorter(a, b):
				var gene_a = GameState.saved_stats.shared_stash[a]
				var gene_b = GameState.saved_stats.shared_stash[b]
				var slot_a = Genes.slot_for_base(gene_a.type)
				var slot_b = Genes.slot_for_base(gene_b.type)
				var unique_a = gene_a.unique
				var unique_b = gene_b.unique

				if slot_a == slot_b:
								if unique_a > unique_b:
												return true
								if unique_b > unique_a:
												return false
								return gene_a.level > gene_b.level

				return slot_a < slot_b



func _ready():
				if is_shared:
								$Label.text = Genes.name_for_gene_type[slot]
								var all_genes = GameState.get_shared_genes_of_slot(slot)
								all_genes.sort_custom(self, "shared_gene_sorter")
								for id in all_genes:
												var button = gene_button.instantiate()
												button.gene_id = id
												button.is_in_shared = true
												button.action_transfer = action_transfer
												$Items.add_child(button)

								if len(all_genes) == 0:
												visible = false
				else:
								$Label.text = Genes.name_for_gene_type[slot]
								var all_genes = GameState.get_genes_of_slot(slot)
								all_genes.sort_custom(self, "gene_sorter")
								for id in all_genes:
												var button = gene_button.instantiate()
												button.gene_id = id
												button.is_in_shared = false
												button.action_transfer = action_transfer
												$Items.add_child(button)
								if len(all_genes) == 0:
												visible = false

