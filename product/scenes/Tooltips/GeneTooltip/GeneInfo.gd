extends PanelContainer

@onready var gene_stats = $VBoxContainer/HBoxContainer/StatList
var modline = preload("res://scenes/UI/ModItem.tscn")

func render(gene):
				for child in gene_stats.get_children():
								child.queue_free()

				if gene.has("quality") and gene.quality > 0:
								var max_quality = GeneGenerator.get_max_quality(gene.level)
								$VBoxContainer/GeneQualityLabel.visible = true
								$VBoxContainer/GeneQualityLabel.text = "+" + str(gene.quality) + "% Affix Effectiveness"

				for mod in gene.implicits:
								var label = modline.instantiate()
								label.gene = gene
								label.mod = mod
								label.is_implicit = true
								label.show_advanced = false
								gene_stats.add_child(label)
				if len(gene.implicits) > 0:
								gene_stats.add_child(HSeparator.new())
				for mod in gene.prefixes:
								var label = modline.instantiate()
								label.gene = gene
								label.mod = mod
								label.show_advanced = false
								gene_stats.add_child(label)
				for mod in gene.suffixes:
								var label = modline.instantiate()
								label.gene = gene
								label.mod = mod
								label.show_advanced = false
								gene_stats.add_child(label)

				if gene.unique:
								var unique_info = UniqueGenes.get_unique_data(gene.unique_id)
								if unique_info and unique_info.has("flavor"):
												$VBoxContainer/GeneFlavor.visible = true
												$VBoxContainer/GeneFlavor.text = unique_info.flavor

				$VBoxContainer/GeneNameLabel.text = gene.name
				$VBoxContainer/GeneSlotLabel.text = Genes.name_for_gene_type[Genes.slot_for_base(gene.type)]
				$VBoxContainer/GeneTypeLabel.text = Genes.name_for_base_type[gene.type]
				$VBoxContainer/GeneLevelLabel.text = "Item Level: " + str(gene.level)


