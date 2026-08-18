extends TooltipBase

var item_weakref
onready var container = $PanelContainer
onready var content = $PanelContainer / VBoxContainer / ItemContent

func _ready() -> void :
				call_deferred("bind_to_stats")

func bind_to_stats():
				var item = item_weakref.get_ref()
				if item:
								item.stats.connect("stats_changed", self, "update_info")
								
								update_info()
				else:
								print("No item to bind")

func render(position, position_offset):
				visible = true
				update_info()
				container.modulate = Color.transparent
				confine_to_window(container, position, position_offset)
				container.modulate = Color.white

func hide():
				visible = false

func update_info():
				if not visible:
								return
				var item = item_weakref.get_ref()
				if not item:
								print("No item found")
								return

				content.clear()


				var config = Skills.config[item.name]
				content.add_text(config.name)
				content.newline()
				content.add_text(config.description)
				
				var tiers = item.get_tiers()
				var current_tier = item.get_effective_tier()
				var tier_info = tiers[current_tier]
				var label
				if tier_info.skill.size() > 0:
								content.newline()

								var damage_bundle = item.get_damage_bundle(false, false)

								var stats = {}
								for stat in tier_info.skill:
												if stat == "cooldown" and item.has_tag(SkillTags.Tags.DOT):
																continue
												stats[stat] = true

								if tier_info.has("aura"):
												for stat in tier_info.aura:
																stats[stat] = true
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
																																stats[stat] = true
																																stats[StatsInfo.effect_for_chance[stat]] = true
																								if "toxic" in stat and item.stats.keystones.has("TREE_CHAOTIC_RESONANCE") and damage_bundle.damage.has(SkillTags.Tags.LIGHTNING) and damage_bundle.damage[SkillTags.Tags.LIGHTNING] > 0:
																												stats[stat] = true
																												stats[StatsInfo.effect_for_chance[stat]] = true
																								if "physical" in stat and item.stats.keystones.has("TREE_COATED_BLADES") and damage_bundle.damage.has(SkillTags.Tags.PHYSICAL) and damage_bundle.damage[SkillTags.Tags.PHYSICAL] > 0:
																												stats[stat] = true
																												stats[StatsInfo.effect_for_chance[stat]] = true
																elif "penetration" in stat:
																				if item.get_effective_stat(stat) > 0.0:
																								var damage_tag = StatsInfo.type_for_penetration[stat]
																								if damage_bundle.damage.has(damage_tag):
																												if damage_bundle.damage[damage_tag] > 0:
																																stats[stat] = true
																elif stat == "crit_chance" and item.get_effective_stat(stat) > 0.0 and not item.has_tag(SkillTags.Tags.DOT):
																				stats["crit_multi"] = true
																elif stat == "infection_count":
																				if item.get_effective_stat("toxic_ailment_chance") > 0 and item.has_tag(SkillTags.Tags.HIT):
																								stats[stat] = true
																elif stat == "vulnerable_effect":
																				if item.get_effective_stat("vulnerable_chance") > 0:
																								stats[stat] = true
																elif stat == "exposure_effect":
																				if item.get_effective_stat("exposure_chance") > 0:
																								stats[stat] = true
																else:
																				stats[stat] = true

								if tier_info.has("aura"):
												content.newline()
												content.push_color(Colors.keystone)
												content.add_text("Aura Effects")
												content.pop()
												var effective_aura_stats = item.get_buffs_and_nerfs()
												for stat in effective_aura_stats:
																for stat_inst in effective_aura_stats[stat]:
																				content.newline()
																				var stat_name = StatsInfo.stat_name[stat]
																				content.add_text(StatsInfo.render_passive_stat_line(stat, {"amount": stat_inst.amount, "scaling_type": stat_inst.type}))
								else:
												var statlist = stats.keys()
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
