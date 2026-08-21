extends Node

func get_search_string(gene_id):
				var output = ""
				var st = GameState.get_active_stats()
				if st.genes.has(gene_id):
								var gene = st.genes[gene_id]
								var mod_config_type = Genes.mods_for_base_type(gene.type)
								var drop_only_mod_config_type = Genes.drop_only_mods_for_base_type(gene.type)
								output = gene.name
								var has_drop_only = false
								for mod in gene.implicits:
												var config = mod_config_type
												if mod.drop_only:
																config = drop_only_mod_config_type
																has_drop_only = true
												var mod_stat = config.calculate_effective_stat(mod)
												if mod_stat.has("keystone"):
																output += " " + Keystones.keystones[mod_stat.keystone].name + "\n" + Keystones.keystones[mod_stat.keystone].description
												else:
																output += " " + StatsInfo.render_item_stat_line(config.mod_option_for_id[mod.mod_id].stat, mod_stat)
								for mod in gene.prefixes:
												var config = mod_config_type
												if mod.drop_only:
																has_drop_only = true
																config = drop_only_mod_config_type
												var mod_stat = config.calculate_effective_stat(mod)
												if mod_stat.has("keystone"):
																output += " " + Keystones.keystones[mod_stat.keystone].name + "\n" + Keystones.keystones[mod_stat.keystone].description
												else:
																output += " " + StatsInfo.render_item_stat_line(config.mod_option_for_id[mod.mod_id].stat, mod_stat)
								for mod in gene.suffixes:
												var config = mod_config_type
												if mod.drop_only:
																has_drop_only = true
																config = drop_only_mod_config_type
												var mod_stat = config.calculate_effective_stat(mod)
												if mod_stat.has("keystone"):
																output += " " + Keystones.keystones[mod_stat.keystone].name + "\n" + Keystones.keystones[mod_stat.keystone].description
												else:
																
																output += " " + StatsInfo.render_item_stat_line(config.mod_option_for_id[mod.mod_id].stat, mod_stat)

								if has_drop_only:
												output += " drop only"
				return output.to_lower()
