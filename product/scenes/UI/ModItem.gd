extends HBoxContainer

@onready var mod_label = $VBoxContainer/ModLabel
@onready var mod_title = $VBoxContainer/ModName
@onready var lock_container = $LockContainer
@onready var lock_icon = $LockContainer/LockedIcon

var gene
var gene_id
var mod
var show_advanced = false
var is_implicit = false


func _ready() -> void :
				var quality_multiplier = 1.0
				if gene == null and gene_id:
								gene = GameState.get_active_stats().genes[gene_id]
				var mod_options = Genes.mods_for_base_type(gene.type)
				if mod.has("drop_only") and mod.drop_only:
								mod_options = Genes.drop_only_mods_for_base_type(gene.type)

				if gene.has("quality"):
								quality_multiplier = 1.0 + (gene.quality / 100.0)

				var mod_stat = mod_options.calculate_effective_stat(mod, quality_multiplier)
				if mod_stat.has("keystone"):
								mod_title.visible = true
								mod_title.text = Keystones.keystones[mod_stat.keystone].name
								mod_title.modulate = Colors.keystone
								mod_label.text = Keystones.keystones[mod_stat.keystone].description
				else:
								mod_label.text = StatsInfo.render_item_stat_line(mod_options.mod_option_for_id[mod.mod_id].stat, mod_stat)
								if show_advanced and not is_implicit:
												mod_label.text += "\n"
												var roll_range = mod_options.get_tier_bounds(mod.mod_id, mod.tier, quality_multiplier)
												if mod.drop_only:
																mod_label.text += "Mod Level %s: (%s - %s)" % [mod.tier + 1, roll_range.min_formatted, roll_range.max_formatted]
																mod_label.text += "\nDrop Only: Cannot be upgraded"
												else:
																if mod_options.is_tier_maxed_for_level(mod, gene.level):
																				mod_label.text += "Mod Level Maxed: (%s - %s)" % [roll_range.min_formatted, roll_range.max_formatted]
																else:
																				mod_label.text += "Mod Level %d: (%s - %s)" % [mod.tier + 1, roll_range.min_formatted, roll_range.max_formatted]


				if not gene_id:
								lock_container.visible = false
								lock_icon.visible = false
								if mod.drop_only:
												mod_label.modulate = Colors.drop_only
								else:
												if mod_options.is_tier_maxed_for_level(mod, gene.level):
																mod_label.modulate = Colors.max_tier
				else:
								if mod.locked:
												lock_icon.text = "Locked"
												lock_icon.modulate = Colors.mod_locked
												lock_container.visible = true
								else:
												lock_icon.text = "Unlocked"
												lock_icon.icon = null
												lock_container.visible = true

								if mod.drop_only:
												mod_label.modulate = Colors.drop_only
								else:
												if mod_options.is_tier_maxed_for_level(mod, gene.level):
																mod_label.modulate = Colors.max_tier

								if mod.locked:
												mod_label.modulate = Colors.mod_locked
												if Genes.can_perform_craft(gene_id, Genes.CraftType.UNLOCK_SPECIFIC_MOD, mod.mod_id):
																lock_icon.disabled = false
												else:
																lock_icon.disabled = true
								else:
												if Genes.can_perform_craft(gene_id, Genes.CraftType.LOCK_SPECIFIC_MOD, mod.mod_id):
																lock_icon.disabled = false
												else:
																lock_icon.disabled = true

				if is_implicit:
								if not mod.drop_only:
												mod_label.modulate = Colors.implicit
								mod_label.align = HORIZONTAL_ALIGNMENT_CENTER
								lock_container.visible = false

func _on_LockedIcon_pressed() -> void :
				if mod.locked:
								Genes.purchase_craft(gene_id, Genes.CraftType.UNLOCK_SPECIFIC_MOD, mod.mod_id)
				else:
								Genes.purchase_craft(gene_id, Genes.CraftType.LOCK_SPECIFIC_MOD, mod.mod_id)
