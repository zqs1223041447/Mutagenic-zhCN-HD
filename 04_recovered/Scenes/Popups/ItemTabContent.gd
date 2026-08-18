extends ScrollContainer

onready var player_stats = GameState.get_global("player").get_node("Stats")
onready var content = $ItemTabContent / ItemContent
var item

func damage_sorter(a, b):
				return a[1] > b[1]


func _ready() -> void :
				$ItemTabContent / ItemNameLabel.text = Skills.config[item.name].name

				
				var tiers = item.get_tiers()
				var current_tier = item.get_effective_tier()
				$ItemTabContent / ItemTierLabel.text = "Current Tier: " + str(current_tier + 1)
				$ItemTabContent / ItemSupportLabel.text = item.render_supports()

				var tier_info = tiers[current_tier]
				$ItemTabContent / ItemDescriptionLabel.text = Skills.config[item.name].description
				$ItemTabContent / ItemTagsLabel.text = SkillTags.render_tag_list(item.get_tags())

				if Skills.config[item.name].has("damage_tag"):
								var damage_type_tag = Skills.config[item.name].damage_tag
								$ItemTabContent / DamageTypeContainer / DamageTypeLabel.text = str(item.get_base_damage()) + " " + SkillTags.TagNames[damage_type_tag]
								$ItemTabContent / DamageTypeContainer / DamageTypeLabel.modulate = Colors.color_for_skill_tag[damage_type_tag]
				else:
								$ItemTabContent / DamageTypeContainer.visible = false

				var label
				if tier_info.skill.size() > 0:
								content.newline()

								var damage_bundle = item.get_damage_bundle(false, false)

								var valid_stats = {}
								for stat in tier_info.skill:
												if stat == "cooldown" and item.has_tag(SkillTags.Tags.DOT):
																continue
												valid_stats[stat] = true
								if tier_info.has("aura"):
												for stat in tier_info.aura:
																valid_stats[stat] = true
								elif item.has_tag(SkillTags.Tags.DAMAGING):
												for stat in StatsInfo.all_skill_list:
																if "chance" in stat and not item.has_tag(SkillTags.Tags.HIT):
																				continue
																if "effect" in stat and not item.has_tag(SkillTags.Tags.HIT):
																				if stat != "skill_effectiveness":
																								continue
																if stat == "cast_speed" and not item.has_tag(SkillTags.Tags.CASTABLE):
																				continue
																if stat == "cast_speed" and item.is_triggered:
																				continue
																if stat == "cooldown" and item.has_tag(SkillTags.Tags.DOT):
																				continue

																if "ailment_chance" in stat and stat != "amplify_ailment_chance":
																				if item.get_effective_stat(stat) > 0.0:
																								var damage_tag = StatsInfo.type_for_chance[stat]
																								if damage_bundle.damage.has(damage_tag):
																												if damage_bundle.damage[damage_tag] > 0:
																																valid_stats[stat] = true
																																valid_stats[StatsInfo.effect_for_chance[stat]] = true
																								if "toxic" in stat and player_stats.keystones.has("TREE_CHAOTIC_RESONANCE") and damage_bundle.damage.has(SkillTags.Tags.LIGHTNING) and damage_bundle.damage[SkillTags.Tags.LIGHTNING] > 0:
																												valid_stats[stat] = true
																												valid_stats[StatsInfo.effect_for_chance[stat]] = true
																								if "physical" in stat and player_stats.keystones.has("TREE_COATED_BLADES") and damage_bundle.damage.has(SkillTags.Tags.PHYSICAL) and damage_bundle.damage[SkillTags.Tags.PHYSICAL] > 0:
																												valid_stats[stat] = true
																												valid_stats[StatsInfo.effect_for_chance[stat]] = true
																elif "penetration" in stat:
																				if item.get_effective_stat(stat) > 0.0:
																								var damage_tag = StatsInfo.type_for_penetration[stat]
																								if damage_bundle.damage.has(damage_tag):
																												if damage_bundle.damage[damage_tag] > 0:
																																valid_stats[stat] = true
																elif stat == "crit_chance" and item.get_effective_stat(stat) > 0.0 and not item.has_tag(SkillTags.Tags.DOT):
																				valid_stats["crit_multi"] = true
																elif stat == "infection_count":
																				if item.get_effective_stat("toxic_ailment_chance") > 0:
																								valid_stats[stat] = true
																elif stat == "vulnerable_effect":
																				if item.get_effective_stat("vulnerable_chance") > 0:
																								valid_stats[stat] = true
																elif stat == "exposure_effect":
																				if item.get_effective_stat("exposure_chance") > 0:
																								valid_stats[stat] = true
																elif stat == "life_gain_on_hit":
																				if item.has_tag(SkillTags.Tags.HIT):
																								valid_stats[stat] = true
																else:
																				valid_stats[stat] = true
								var statlist = valid_stats.keys()
								statlist.sort_custom(StatsInfo, "skill_sorter")
								for stat in statlist:
												var effective_stat = item.get_effective_stat(stat)
												var stat_name = StatsInfo.stat_name[stat]

												if typeof(effective_stat) == TYPE_REAL or typeof(effective_stat) == TYPE_INT:
																if effective_stat == 0:
																				continue
																content.add_text(stat_name + ": " + StatsInfo.render_skill_stat_line(stat, effective_stat))
												elif typeof(effective_stat) == TYPE_DICTIONARY:
																content.add_text(stat_name + ": ")
																
																var sorted_items = []
																for s in effective_stat:
																				sorted_items.append([s, effective_stat[s]])
																sorted_items.sort_custom(self, "damage_sorter")
																for pair in sorted_items:
																				var pair_item = pair[0]
																				content.push_color(Colors.color_for_skill_tag[pair_item])
																				content.add_text(" [" + str(stepify(effective_stat[pair_item], 0.1)) + " " + SkillTags.TagNames[pair_item] + "]")
																				content.pop()
												content.newline()

								if tier_info.has("aura"):
												content.newline()
												content.push_color(Colors.keystone)
												content.add_text("Aura Effects")
												content.pop()
												var effective_aura_stats = item.get_buffs_and_nerfs()
												for stat in effective_aura_stats:
																for item in effective_aura_stats[stat]:
																				content.newline()
																				var stat_name = StatsInfo.stat_name[stat]
																				content.add_text(StatsInfo.render_passive_stat_line(stat, {"amount": item.amount, "scaling_type": item.type}))
