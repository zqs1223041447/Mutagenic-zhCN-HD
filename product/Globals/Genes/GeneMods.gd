extends Node
class_name GeneMods

"""
Mods have the following attributes:

mod_id
stat
tier
tier_strength

"""

var mod_option_configs = []
var mod_option_for_id = {}
var mod_weight_accumulated = []
var prefix_weight = 0
var suffix_weight = 0
var implicit_weight = 0


func compile(drop_only = false):
				for option in mod_option_configs:
								if drop_only:
												option.drop_only = true
												option.min_level = 80
								elif not option.has("min_level"):
												option.min_level = 0
												option.drop_only = false
								if option.unique:
												continue
								if option.affix_type == Constants.ModType.PREFIX:
												prefix_weight += option.weight
												mod_weight_accumulated.append(prefix_weight)
								elif option.affix_type == Constants.ModType.SUFFIX:
												suffix_weight += option.weight
												mod_weight_accumulated.append(suffix_weight)
								elif option.affix_type == Constants.ModType.IMPLICIT:
												implicit_weight += option.weight
												mod_weight_accumulated.append(implicit_weight)
								else:
												print("Invalid option affix type:", option)
												get_tree().quit()

				cache_ids()

func cache_ids():
				for option in mod_option_configs:
								if mod_option_for_id.has(option.id):
												print("Duplicate mod id found: ", option.id)
												get_tree().quit()
								mod_option_for_id[option.id] = option

func suffix_weight_for_level(level = 0):
				var weight = 0
				var accum = []
				for option in mod_option_configs:
								if option.unique:
												continue
								if option.min_level > level:
												continue
								if option.affix_type == Constants.ModType.SUFFIX:
												weight += option.weight
												accum.append(weight)
				return [weight, accum]

func prefix_weight_for_level(level = 0):
				var weight = 0
				var accum = []
				for option in mod_option_configs:
								if option.unique:
												continue
								if option.min_level > level:
												continue
								if option.affix_type == Constants.ModType.PREFIX:
												weight += option.weight
												accum.append(weight)
				return [weight, accum]

func implicit_weight_for_level(level = 0):
				var weight = 0
				var accum = []
				for option in mod_option_configs:
								if option.unique:
												continue
								if option.min_level > level:
												continue
								if option.affix_type == Constants.ModType.IMPLICIT:
												weight += option.weight
												accum.append(weight)
				return [weight, accum]

func sample_suffix(level = 0):
				var info = suffix_weight_for_level(level)
				var weight = info[0]
				var accum = info[1]
				var roll = randf() * weight
				var index = 0
				for option in mod_option_configs:
								if option.unique:
												continue
								if option.min_level > level:
												continue
								if option.affix_type == Constants.ModType.SUFFIX:
												if accum[index] >= roll:
																return option
												index += 1
				print("Failed to roll a suffix. Weights are wrong.")
				get_tree().quit()

func roll_tier(max_tiers, roll_max = false, n_rolls = 1):
				var max_value = (max_tiers) * (max_tiers + 1) / 2

				if roll_max:
								return max_tiers - 1

				var highest_tier = - 1
				for roll_attempt in range(n_rolls):
								var roll = randi() % max_value
								var accum = 0
								for i in range(max_tiers):
												accum += i + 1
												if roll < accum:
																var tier = max_tiers - i - 1
																if tier > highest_tier:
																				highest_tier = tier

				if highest_tier > - 1:
								return highest_tier

				print("Invalid value!")

func get_tier_chance(tier, max_tiers):
				var max_value = (max_tiers) * (max_tiers + 1) / 2
				return snapped(100.0 * (max_tiers - tier) / max_value, 0.1)

func roll_suffix(level, option, roll_max = false, n_rolls = 1):
				var suffix
				if option.has("keystone"):
								suffix = {
												"mod_id": option.id, 
												"keystone": option.keystone, 
												"locked": false, 
								}
				else:
								var max_tier = 1
								for i in range(option.tiers):
												if level >= get_level_requirement(i, option.tiers, option.min_level):
																max_tier = i + 1
								suffix = {
												"mod_id": option.id, 
												"stat": option.stat, 
												"tier": roll_tier(max_tier, roll_max, n_rolls), 
												"tier_strength": Genes.roll_tier_strength(), 
												"locked": false, 
								}
								if option.has("tags") and len(option.tags) > 0:
												suffix.tags = option.tags.duplicate(true)

				if option.has("group_id"):
								suffix.group_id = option.group_id

				if option.has("drop_only") and option.drop_only:
								suffix.drop_only = true
				else:
								suffix.drop_only = false

				return suffix

func sample_prefix(level = 0):
				var info = prefix_weight_for_level(level)
				var weight = info[0]
				var accum = info[1]
				var roll = randf() * weight
				var index = 0
				for option in mod_option_configs:
								if option.unique:
												continue
								if option.min_level > level:
												continue
								if option.affix_type == Constants.ModType.PREFIX:
												if accum[index] >= roll:
																return option
												index += 1
				print("Failed to roll a suffix. Weights are wrong.")
				get_tree().quit()

func sample_implicit(level = 0):
				var info = implicit_weight_for_level(level)
				var weight = info[0]
				var accum = info[1]
				var roll = randf() * weight
				var index = 0
				for option in mod_option_configs:
								if option.unique:
												continue
								if option.min_level > level:
												continue
								if option.affix_type == Constants.ModType.IMPLICIT:
												if accum[index] >= roll:
																return option
												index += 1
				print("Failed to roll a implicit. Weights are wrong.")
				get_tree().quit()

func roll_implicit(level, option, roll_max = false, n_rolls = 1):
				var implicit
				if option.has("keystone"):
								implicit = {
												"mod_id": option.id, 
												"keystone": option.keystone, 
												"locked": false, 
								}
				else:
								var max_tier = 1
								for i in range(option.tiers):
												if level >= get_level_requirement(i, option.tiers, option.min_level):
																max_tier = i + 1
								implicit = {
												"mod_id": option.id, 
												"stat": option.stat, 
												"tier": roll_tier(max_tier, roll_max, n_rolls), 
												"tier_strength": Genes.roll_tier_strength(), 
												"locked": false, 
								}
								if option.has("tags") and len(option.tags) > 0:
												implicit.tags = option.tags.duplicate(true)

				if option.has("group_id"):
								implicit.group_id = option.group_id

				if option.has("drop_only") and option.drop_only:
								implicit.drop_only = true
				else:
								implicit.drop_only = false

				return implicit

func roll_prefix(level, option, roll_max = false, n_rolls = 1):
				var prefix
				if option.has("keystone"):
								prefix = {
												"mod_id": option.id, 
												"keystone": option.keystone, 
												"locked": false, 
								}
				else:
								var max_tier = 1
								for i in range(option.tiers):
												if level >= get_level_requirement(i, option.tiers, option.min_level):
																max_tier = i + 1
								prefix = {
												"mod_id": option.id, 
												"stat": option.stat, 
												"tier": roll_tier(max_tier, roll_max, n_rolls), 
												"tier_strength": Genes.roll_tier_strength(), 
												"locked": false, 
								}
								if option.has("tags") and len(option.tags) > 0:
												prefix.tags = option.tags.duplicate(true)

				if option.has("group_id"):
								prefix.group_id = option.group_id

				if option.has("drop_only") and option.drop_only:
								prefix.drop_only = true
				else:
								prefix.drop_only = false

				return prefix

func get_tier_bounds(mod_id, tier, quality = 1.0):
				var mod_config = mod_option_for_id[mod_id]
				var min_value = mod_config.min_value
				var step = mod_config.step

				var tiered_min = snapped(quality * min_value * pow(step, tier), mod_config.stepified)
				var tiered_max = snapped(quality * min_value * pow(step, tier + 1), mod_config.stepified)
				if tiered_min > tiered_max:
								var old_min = tiered_min
								tiered_min = tiered_max
								tiered_max = old_min

				var formatted_min = StatsInfo.render_formatted_number(tiered_min, mod_config.stat, mod_config.type)
				var formatted_max = StatsInfo.render_formatted_number(tiered_max, mod_config.stat, mod_config.type)

				return {
								"min": tiered_min, 
								"max": tiered_max, 
								"min_formatted": formatted_min, 
								"max_formatted": formatted_max
				}

static func get_level_requirement(tier, n_tiers, min_level = 0):
				if n_tiers == 1:
								return min_level
				var step = 80 - min_level
				return min_level + tier * ceil(step / (n_tiers - 1))

func calculate_effective_stat(mod, quality = 1.0):
				var mod_config = mod_option_for_id[mod.mod_id]

				if mod_config.has("keystone"):
								return {
												"keystone": mod_config.keystone
								}

				var bounds = get_tier_bounds(mod.mod_id, mod.tier, quality)
				var stat = {
								"type": mod_config.type, 
								"amount": snapped(bounds.min + (bounds.max - bounds.min) * mod.tier_strength, mod_config.stepified)
				}

				if mod_config.has("tags") and len(mod_config.tags) > 0:
								stat.tags = mod_config.tags

				return stat

func get_unique_mod_info(mod_id):
				if not mod_option_for_id.has(mod_id):
								print("Mod not found: ", mod_id)
								return {}

				var mod = mod_option_for_id[mod_id]
				if mod.has("keystone"):
								var res = {
												"keystone": mod.keystone, 
												"weight": mod.weight, 
												"unique": mod.unique, 
								}
								if not mod.unique:
												res["affix_type"] = mod.affix_type
								return res
				else:
								var n_tiers = mod.tiers
								var tiers = []
								for i in range(n_tiers):
												tiers.append({
																"tier": i + 1, 
																"range": get_tier_bounds(mod.id, i), 
																"chance": get_tier_chance(i, n_tiers), 
																"level_requirement": get_level_requirement(i, n_tiers, mod.min_level), 
												})


								var res = {
												"stat": mod.stat, 
												"type": mod.type, 
												"weight": mod.weight, 
												"tiers": tiers, 
												"unique": mod.unique, 
												"drop_only": mod.drop_only
								}

								if mod.has("tags"):
												res.tags = mod.tags

								if not mod.unique:
												res["affix_type"] = mod.affix_type

								return res

func get_explicit_tiers():
				var result = []
				for mod in mod_option_configs:
								if mod.has("keystone"):
												var res = {
																"keystone": mod.keystone, 
																"weight": mod.weight, 
																"unique": mod.unique, 
												}
												if not mod.unique:
																res["affix_type"] = mod.affix_type
												result.append(res)
								else:
												var n_tiers = mod.tiers
												var tiers = []
												for i in range(n_tiers):
																tiers.append({
																				"tier": i + 1, 
																				"range": get_tier_bounds(mod.id, i), 
																				"chance": get_tier_chance(i, n_tiers), 
																				"level_requirement": get_level_requirement(i, n_tiers, mod.min_level), 
																})


												var res = {
																"stat": mod.stat, 
																"type": mod.type, 
																"weight": mod.weight, 
																"tiers": tiers, 
																"unique": mod.unique, 
																"drop_only": mod.drop_only
												}

												if mod.has("tags"):
																res.tags = mod.tags

												if not mod.unique:
																res["affix_type"] = mod.affix_type

												result.append(res)
				result.sort_custom(self, "tier_sort")
				return result

func tier_sort(a, b):
				if a.has("affix_type") and b.has("affix_type"):
								if a.affix_type == b.affix_type:
												return b.weight < a.weight
								return a.affix_type < b.affix_type

				return b.weight < a.weight

func is_tier_maxed_for_level(mod, level):
				var mod_option = mod_option_for_id[mod.mod_id]
				if mod_option.has("unique") and mod_option.unique:
								return false
				var max_tier = 0
				for i in range(mod_option.tiers):
								if level >= get_level_requirement(i, mod_option.tiers, mod_option.min_level):
												max_tier = i + 1
				return mod.tier == max_tier - 1

