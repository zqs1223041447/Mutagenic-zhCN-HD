extends Node






func generate_random_gene(zone_level, rarity_bonus = 0.0, always_rare = false, pools = []):
				
				var slot_options = Genes.base_types_for_slot.keys()
				var slot_chosen = slot_options[randi() % len(slot_options)]
				var gene_options = Genes.base_types_for_slot[slot_chosen]
				var gene_type = gene_options[randi() % len(gene_options)]

				
				if slot_chosen == Genes.GeneSlot.WEAPON:
								if Genes.is_shield(gene_type) and randf() < 0.5:
												
												print("rolling shield instead")
												gene_type = Genes.random_weapon_base_type()


								if gene_type == Genes.BaseType.MELEE_WEAPON or gene_type == Genes.BaseType.RANGE_WEAPON:
												var player = GameState.get_global("player")
												if player and player.stats.keystones.has("TREE_TRANSMOGRIFICATION"):
																gene_type = Genes.BaseType.CASTER_WEAPON

				var rarity_roll = randf() * 100.0

				var unique_cutoff = max(50.0, 100.0 - 3.0 * (1.0 + rarity_bonus))

				if always_rare:
								return generate_random_rare(gene_type, zone_level, rarity_bonus)

				
				if rarity_roll >= unique_cutoff and len(pools) > 0:
								return generate_random_unique(zone_level, rarity_bonus, pools)
				if rarity_roll > unique_cutoff * 0.75:
								return generate_random_rare(gene_type, zone_level, rarity_bonus)
				else:
								return generate_random_basic(gene_type, zone_level, rarity_bonus)

func generate_random_unique(zone_level, rarity_bonus, pools = []):
				var gene = UniqueGenes.roll_random_unique(zone_level, pools)
				var drop_mods = Genes.drop_only_mods_for_base_type(gene.type)
				var mods = Genes.mods_for_base_type(gene.type)
				
				var rolled_drop_only = false
				
				if zone_level >= 80 and randf() < 0.25:
								rolled_drop_only = true

				
				var n_impl = Genes.implicit_count_for_base_type(gene.type)
				for i in range(n_impl):
								if rolled_drop_only and randf() < 0.5:
												var implicit = roll_implicit(gene, drop_mods)
												gene.implicits.append(implicit)
								else:
												var implicit = roll_implicit(gene, mods)
												gene.implicits.append(implicit)

				return gene

func generate_random_rare(gene_type, zone_level, rarity_bonus):
				var mods = Genes.mods_for_base_type(gene_type)
				var drop_mods = Genes.drop_only_mods_for_base_type(gene_type)
				var gene = create_new_gene(gene_type, zone_level)

				
				var rolled_drop_only = false
				
				if zone_level >= 80 and randf() < 0.7:
								rolled_drop_only = true

				
				var n_impl = Genes.implicit_count_for_base_type(gene_type)
				for i in range(n_impl):
								if rolled_drop_only and randf() < 0.5:
												var implicit = roll_implicit(gene, drop_mods)
												gene.implicits.append(implicit)
								else:
												var implicit = roll_implicit(gene, mods)
												gene.implicits.append(implicit)

				var n_prefix = 2
				var n_suffix = 2

				
				var rolled_max_prefix = false
				var rolled_max_suffix = false

				
				var roll_drop_only_prefix = randf() < 0.5
				var drop_only_prefixes = 0
				var drop_only_suffixes = 0

				if rolled_drop_only:
								
								if randf() < 0.5:
												drop_only_prefixes += 1
								else:
												drop_only_suffixes += 1

								
								if zone_level >= 100 and randf() < 0.5:
												if randf() < 0.5:
																drop_only_prefixes += 1
												else:
																drop_only_suffixes += 1

								
								if zone_level >= 125 and randf() < 0.5:
												if randf() < 0.5:
																drop_only_prefixes += 1
												else:
																drop_only_suffixes += 1

				

				for i in range(n_prefix):
								if drop_only_prefixes > 0:
												var p = roll_prefix(gene, drop_mods)
												drop_only_prefixes -= 1
												p.locked = true
												gene.prefixes.append(p)
								else:
												var should_roll_max = randf() < 0.3 and not rolled_max_prefix
												if should_roll_max:
																rolled_max_prefix = true
												var p = roll_prefix(gene, mods, should_roll_max)
												gene.prefixes.append(p)
				for i in range(n_suffix):
								if drop_only_suffixes > 0:
												var p = roll_suffix(gene, drop_mods)
												drop_only_suffixes -= 1
												p.locked = true
												gene.suffixes.append(p)
								else:
												var should_roll_max = randf() < 0.3 and not rolled_max_suffix
												if should_roll_max:
																rolled_max_suffix = true
												var p = roll_suffix(gene, mods, should_roll_max)
												gene.suffixes.append(p)

				return gene

func generate_random_basic(gene_type, zone_level, rarity_bonus):
				var mods = Genes.mods_for_base_type(gene_type)
				var drop_only_mods = Genes.drop_only_mods_for_base_type(gene_type)
				var gene = create_new_gene(gene_type, zone_level)

				
				var n_impl = Genes.implicit_count_for_base_type(gene_type)
				for i in range(n_impl):
								var implicit = roll_implicit(gene, mods)
								gene.implicits.append(implicit)

				var n_prefix = 1
				var n_suffix = 1
				var rolled_max = false
				
				for i in range(n_prefix):
								var should_roll_max = randf() < 0.5 and not rolled_max
								if should_roll_max:
												rolled_max = true
								var p = roll_prefix(gene, mods, should_roll_max)
								gene.prefixes.append(p)
				for i in range(n_prefix):
								var should_roll_max = randf() < 0.5 and not rolled_max
								if should_roll_max:
												rolled_max = true
								var p = roll_suffix(gene, mods, should_roll_max)
								gene.suffixes.append(p)
				return gene

func create_new_gene(type, level):
				var id = Genes.get_next_id()

				if not (type in Genes.BaseType.values()):
								print("Type", type, " is not a Gene Type")
								get_tree().quit()

				var quality = roll_quality(level)

				var gene = {
								"id": id, 
								"level": level, 
								"quality": quality, 
								"unique": false, 
								"name": ItemNameGenerator.generate_name(), 
								"type": type, 
								"implicits": [], 
								"prefixes": [], 
								"suffixes": [], 
								"locked": false, 
				}

				return gene

func get_max_quality(level):
				return max(0, level - 100)

func roll_quality(level):
				if level < 100:
								return 0
				var max_roll = get_max_quality(level)
				return max(0, min(100, round(max_roll * randf())))

func roll_implicit(gene, mods, roll_max = false):
				var implicit_ids = []
				var implicit_group_ids = []
				for implicit in gene.implicits:
								implicit_ids.append(implicit.mod_id)
								if implicit.has("group_id"):
												implicit_group_ids.append(implicit.group_id)
				while true:
								var potential = mods.roll_implicit(gene.level, mods.sample_implicit(gene.level), roll_max)
								if potential.mod_id in implicit_ids:
												continue
								
								if potential.has("group_id"):
												if potential.group_id in implicit_group_ids:
																continue
								return potential

func roll_prefix(gene, mods, roll_max = false):
				var prefix_ids = []
				var prefix_group_ids = []
				for prefix in gene.prefixes:
								prefix_ids.append(prefix.mod_id)
								if prefix.has("group_id"):
												prefix_group_ids.append(prefix.group_id)
				while true:
								var potential_prefix = mods.roll_prefix(gene.level, mods.sample_prefix(gene.level), roll_max)
								if potential_prefix.mod_id in prefix_ids:
												continue
								
								if potential_prefix.has("group_id"):
												if prefix_group_ids.has(potential_prefix.group_id):
																continue
								return potential_prefix

func roll_suffix(gene, mods, roll_max = false):
				var suffix_ids = []
				var suffix_group_ids = []
				for suffix in gene.suffixes:
								suffix_ids.append(suffix.mod_id)
								if suffix.has("group_id"):
												suffix_group_ids.append(suffix.group_id)
				while true:
								var potential_suffix = mods.roll_suffix(gene.level, mods.sample_suffix(gene.level), roll_max)
								if potential_suffix.mod_id in suffix_ids:
												continue
								
								if potential_suffix.has("group_id"):
												if potential_suffix.group_id in suffix_group_ids:
																continue
								return potential_suffix
