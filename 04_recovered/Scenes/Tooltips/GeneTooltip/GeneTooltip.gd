extends TooltipBase

onready var gene_info = $GeneInfo

func render(gene_id, position, position_offset, is_in_shared = false):
				if gene_id == null:
								return
				var gene
				if is_in_shared:
								gene = GameState.saved_stats.shared_stash[gene_id]
				else:
								gene = GameState.get_active_stats().genes[gene_id]
				gene_info.render(gene)
				visible = true
				$GeneInfo.modulate = Color.transparent
				confine_to_window($GeneInfo, position, position_offset)
				$GeneInfo.modulate = Color.white

