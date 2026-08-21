extends Node

var all_uniques = {}
var unique_ids_for_slot = {}

func _ready() -> void :
				for unique_gene_id in UniquePoolGeneric.pool:
								all_uniques[unique_gene_id] = UniquePoolGeneric.pool[unique_gene_id]
								var slot = Genes.slot_for_base(UniquePoolGeneric.pool[unique_gene_id].type)
								if unique_ids_for_slot.has(slot):
												unique_ids_for_slot[slot].append(unique_gene_id)
								else:
												unique_ids_for_slot[slot] = [unique_gene_id]

				for unique_gene_id in UniquePoolSota.pool:
								all_uniques[unique_gene_id] = UniquePoolSota.pool[unique_gene_id]
								var slot = Genes.slot_for_base(UniquePoolSota.pool[unique_gene_id].type)
								if unique_ids_for_slot.has(slot):
												unique_ids_for_slot[slot].append(unique_gene_id)
								else:
												unique_ids_for_slot[slot] = [unique_gene_id]


func get_unique_ids_for_slot(slot):
				if unique_ids_for_slot.has(slot):
								return unique_ids_for_slot[slot]
				return []

func weighted_distribution(options):
				var weight = 0
				var accum = []
				for option in options:
								weight += option[0].weight
								accum.append(weight)
				return [weight, accum]

func roll_random_unique(level, drop_pool = [UniquePoolGeneric.pool]):
				var options = []
				for pool in drop_pool:
								for unique_id in pool:
												var option = pool[unique_id]
												if option.min_level_requirement <= level:
																options.append([option, unique_id])

				
				var weights = weighted_distribution(options)
				var weight = weights[0]
				var accum = weights[1]
				var roll = randf() * weight
				var index = 0
				var rolled_unique = null
				var rolled_unique_id = null
				for option in options:
								if accum[index] >= roll:
												rolled_unique = option[0]
												rolled_unique_id = option[1]
												break
								index += 1
				if not rolled_unique:
								print("Failed to roll a unique")
								get_tree().quit()
				else:
								print("Rolled unique: ", rolled_unique)

				var mod_options = Genes.mods_for_base_type(rolled_unique.type)
				var prefixes = []
				var suffixes = []
				for prefix in rolled_unique.prefixes:
								if mod_options.mod_option_for_id.has(prefix.mod_id):
												var mod_config = mod_options.mod_option_for_id[prefix.mod_id]
												prefixes.append(mod_options.roll_prefix(level, mod_config))
				for suffix in rolled_unique.suffixes:
								if mod_options.mod_option_for_id.has(suffix.mod_id):
												var mod_config = mod_options.mod_option_for_id[suffix.mod_id]
												suffixes.append(mod_options.roll_suffix(level, mod_config))

				return {
								"id": Genes.get_next_id(), 
								"level": level, 
								"quality": GeneGenerator.roll_quality(level), 
								"unique_id": rolled_unique_id, 
								"unique": true, 
								"name": rolled_unique.name, 
								"type": rolled_unique.type, 
								"implicits": [], 
								"prefixes": prefixes, 
								"suffixes": suffixes, 
								"locked": true
				}

func get_unique_data(id):
				if all_uniques.has(id):
								return all_uniques[id]
				return null

