extends Node2D
class_name GenericSkill

@onready var stats = get_parent().get_parent().get_node("Stats")
@onready var entity = get_parent().get_parent().get_parent()
@onready var player = GameState.get_global("player")
@onready var level = GameState.get_global("level_layer")
@onready var ground_effect_level = GameState.get_global("ground")
@onready var projectile_layer = GameState.get_global("projectiles")
@onready var sky_layer = GameState.get_global("sky")

@export var texture = null
@export var target_group = "enemies"
@export var is_castable = true

var damage_tag = null

var cooldown = 0.0
var is_disabled = false
var is_triggered = false
var time_alive = 0.0

var slot = "primary"


var highest_damage = 0
var total_damage = 0
var total_kills = 0
var cached_tags = {}
var cached_tag_list = []
var cached_support_stats = {}
var cached_conditional_support_stats = {}
var computed_support_stats_added = {}
var computed_support_stats_inc = {}
var computed_support_stats_more = {}
var computed_conditional_support_stats = {}
var keystones = {}
@export var is_ally_buff = false

var cached_swiftness_chance = 0.0
var cached_toughness_chance = 0.0
var cached_precision_on_crit_chance = 0.0
var cached_lgoh = 0.0

var css = {}
var cached_outputs = {}

func _ready() -> void :
				recompute_tags()
				if get_parent().get_parent().is_in_group("allies"):
								target_group = "enemies"
								if is_ally_buff:
												target_group = "allies"
								recompute_supported_stats()
								stats.connect("stats_changed", Callable(self, "recompute_supported_stats"))
				else:
								target_group = "allies"
								if is_ally_buff:
												target_group = "enemies"
				call_deferred("set_damage_tag")

				stats.connect("stats_changed", Callable(self, "recompute_chances"))
				stats.connect("stats_changed", Callable(self, "reset_output_cache"))
				stats.connect("stats_changed", Callable(self, "_handle_stat_change"))

func recompute_tags():
				cached_tags = {}
				cached_tag_list = []
				for tag in get_tags():
								cached_tags[tag] = true
								cached_tag_list.append(tag)

func recompute_chances():
				if cached_tags.has(SkillTags.Tags.HIT):
								cached_swiftness_chance = get_swiftness_boon_on_hit_chance()
								cached_toughness_chance = get_toughness_boon_on_hit_chance()
								cached_precision_on_crit_chance = get_precision_boon_on_crit_chance()
								cached_lgoh = get_life_gain_on_hit()

func reset_output_cache():
				cached_outputs = {}
				css = {}

func _handle_stat_change():
				pass

func on_crit():
				if randf() <= cached_precision_on_crit_chance:
								
								stats.add_precision_boon(1)
				if not is_triggered and stats.is_player:
								stats.trigger_on_crit()

func on_hit():
				if randf() <= cached_swiftness_chance:
								
								stats.add_swiftness_boon(1)
				if randf() <= cached_toughness_chance:
								
								stats.add_toughness_boon(1)

				if not is_triggered and stats.is_player:
								stats.trigger_on_hit()
				if cached_lgoh > 0.0:
								stats.recover_health(cached_lgoh)

func set_damage_tag():
				
				cooldown = randf() * get_cooldown()
				damage_tag = get_damage_tag()

func _physics_process(delta: float) -> void :
				if stats.status_flags.has(Constants.StatusFlags.FROZEN):
								return
				time_alive += delta
				cooldown -= delta
				if cooldown <= 0.0:
								if is_castable and not is_triggered:
												_cast()

func get_tags():
				var tags = Skills.get("config")[self.name].tags.duplicate()
				if stats.keystones.has("TREE_WEAPON_DEXTERITY"):
								if tags.has(SkillTags.Tags.ATTACK):
												tags.append(SkillTags.Tags.SPELL)
								elif tags.has(SkillTags.Tags.SPELL):
												tags.append(SkillTags.Tags.ATTACK)
				return tags


func get_damage_tag():
				if Skills.get("config").has(self.name):
								if Skills.get("config")[self.name].has("damage_tag"):
												return Skills.get("config")[self.name].damage_tag
				return null

func recompute_supported_stats():
				reset_output_cache()
				recompute_tags()
				cached_support_stats = {}
				cached_conditional_support_stats = {}
				computed_support_stats_added = {}
				computed_support_stats_inc = {}
				computed_support_stats_more = {}
				computed_conditional_support_stats = {}
				keystones = {}
				is_triggered = false
				is_disabled = false

				var equipped_skills = GameState.get_equipped_skills()
				var skill_config = equipped_skills[slot]
				for support_key in skill_config.supports:
								var support = skill_config.supports[support_key]
								if support != null:
												var support_config = SkillSupports.supports[support]

												if support_config.has("keystones"):
																for item in support_config.keystones:
																				
																				keystones[item] = true

												if support_config.has("is_triggered"):
																if support_config.is_triggered and cached_tags.has(SkillTags.Tags.TRIGGERABLE):
																				if is_triggered:
																								
																								is_disabled = true
																				is_triggered = true

												for item in support_config.stats:
																var stat = item.stat
																var type = item.scaling_type
																var amount = item.amount

																if item.has("tags"):
																				for tag in item.tags:
																								if not cached_conditional_support_stats.has(tag):
																												cached_conditional_support_stats[tag] = {}
																								if not cached_conditional_support_stats[tag].has(stat):
																												cached_conditional_support_stats[tag][stat] = {}

																								if cached_conditional_support_stats[tag][stat].has(type):
																												if type == Constants.ScalingType.FLAT:
																																cached_conditional_support_stats[tag][stat][type] += amount
																												if type == Constants.ScalingType.PERCENT:
																																cached_conditional_support_stats[tag][stat][type] += amount
																												if type == Constants.ScalingType.MORE:
																																cached_conditional_support_stats[tag][stat][type] *= 1.0 + amount
																								else:
																												if type == Constants.ScalingType.FLAT:
																																cached_conditional_support_stats[tag][stat][type] = amount
																												if type == Constants.ScalingType.PERCENT:
																																cached_conditional_support_stats[tag][stat][type] = amount
																												if type == Constants.ScalingType.MORE:
																																cached_conditional_support_stats[tag][stat][type] = 1.0 + amount
																else:
																				if not cached_support_stats.has(stat):
																								cached_support_stats[stat] = {}
																				if cached_support_stats[stat].has(type):
																								if type == Constants.ScalingType.FLAT:
																												cached_support_stats[stat][type] += amount
																								if type == Constants.ScalingType.PERCENT:
																												cached_support_stats[stat][type] += amount
																								if type == Constants.ScalingType.MORE:
																												cached_support_stats[stat][type] *= 1.0 + amount
																				else:
																								if type == Constants.ScalingType.FLAT:
																												cached_support_stats[stat][type] = amount
																								if type == Constants.ScalingType.PERCENT:
																												cached_support_stats[stat][type] = amount
																								if type == Constants.ScalingType.MORE:
																												cached_support_stats[stat][type] = 1.0 + amount

				for stat in cached_support_stats:
								var scale_mods = cached_support_stats[stat]
								
								for scaling_type in scale_mods:
												var amount = scale_mods[scaling_type]
												if scaling_type == Constants.ScalingType.FLAT:
																if not computed_support_stats_added.has(stat):
																				computed_support_stats_added[stat] = amount
																else:
																				computed_support_stats_added[stat] += amount
												elif scaling_type == Constants.ScalingType.PERCENT:
																if not computed_support_stats_inc.has(stat):
																				computed_support_stats_inc[stat] = amount
																else:
																				computed_support_stats_inc[stat] += amount
												elif scaling_type == Constants.ScalingType.MORE:
																if not computed_support_stats_more.has(stat):
																				computed_support_stats_more[stat] = amount
																else:
																				computed_support_stats_more[stat] *= 1.0 + amount

				for tag in cached_conditional_support_stats:
								if not computed_conditional_support_stats.has(tag):
												computed_conditional_support_stats[tag] = {
																"added": {}, 
																"inc": {}, 
																"more": {}
												}
								for stat in cached_conditional_support_stats[tag]:
												var scale_mods = cached_conditional_support_stats[tag][stat]
												
												for scaling_type in scale_mods:
																var amount = scale_mods[scaling_type]
																if scaling_type == Constants.ScalingType.FLAT:
																				if not computed_conditional_support_stats[tag].added.has(stat):
																								computed_conditional_support_stats[tag].added[stat] = amount
																				else:
																								computed_conditional_support_stats[tag].added[stat] += amount
																elif scaling_type == Constants.ScalingType.PERCENT:
																				if not computed_conditional_support_stats[tag].inc.has(stat):
																								computed_conditional_support_stats[tag].inc[stat] = amount
																				else:
																								computed_conditional_support_stats[tag].inc[stat] += amount
																elif scaling_type == Constants.ScalingType.MORE:
																				if not computed_conditional_support_stats[tag].more.has(stat):
																								computed_conditional_support_stats[tag].more[stat] = amount
																				else:
																								computed_conditional_support_stats[tag].more[stat] *= 1.0 + amount

				compute_attribute_additions()

func compute_attribute_additions():
				if computed_support_stats_added.has("physical_per_25_strength"):
								var added_amount = floor(computed_support_stats_added.physical_per_25_strength * floor(stats.gs("strength") / 25.0))
								if computed_support_stats_added.has("physical_damage"):
												computed_support_stats_added["physical_damage"] += added_amount
								else:
												computed_support_stats_added["physical_damage"] = added_amount

				if computed_support_stats_added.has("lightning_per_25_agility"):
								var added_amount = floor(computed_support_stats_added.lightning_per_25_agility * floor(stats.gs("agility") / 25.0))
								if computed_support_stats_added.has("lightning_damage"):
												computed_support_stats_added["lightning_damage"] += added_amount
								else:
												computed_support_stats_added["lightning_damage"] = added_amount

				if computed_support_stats_added.has("cold_per_25_wisdom"):
								var added_amount = floor(computed_support_stats_added.cold_per_25_wisdom * floor(stats.gs("wisdom") / 25.0))
								if computed_support_stats_added.has("cold_damage"):
												computed_support_stats_added["cold_damage"] += added_amount
								else:
												computed_support_stats_added["cold_damage"] = added_amount

				if computed_support_stats_added.has("fire_per_25_constitution"):
								var added_amount = floor(computed_support_stats_added.fire_per_25_constitution * floor(stats.gs("constitution") / 25.0))
								if computed_support_stats_added.has("fire_damage"):
												computed_support_stats_added["fire_damage"] += added_amount
								else:
												computed_support_stats_added["fire_damage"] = added_amount

				if computed_support_stats_added.has("toxic_per_25_finesse"):
								var added_amount = floor(computed_support_stats_added.toxic_per_25_finesse * floor(stats.gs("finesse") / 25.0))
								if computed_support_stats_added.has("toxic_damage"):
												computed_support_stats_added["toxic_damage"] += added_amount
								else:
												computed_support_stats_added["toxic_damage"] = added_amount

func render_supports():
				if Skills.get("config")[self.name].playable:
								var supports = []
								var eq = GameState.get_equipped_skills()

								var skill_config = eq[slot]
								for support_key in skill_config.supports:
												var support = skill_config.supports[support_key]
												if support != null:
																supports.append(SkillSupports.supports[support].name)
								if len(supports) == 0:
												return "No Supports Active"
								return ", ".join(PackedStringArray(supports))
				else:
								return ""

func get_effective_tier():
				var parent_level = stats.get_effective_level()
				if stats.is_enemy:
								parent_level = 1
				return Skills.tier_for_level(parent_level)

func is_skill():
				return Skills.get("config")[self.name].type == Constants.ItemType.SKILL

func has_tag(tag):
				return cached_tags.has(tag)

func get_tiers():
				if Skills.tiers.has(self.name):
								return Skills.tiers[self.name].get_tiers()
				return []

func get_aura_buffs():
				var tiers = get_tiers()
				var et = get_effective_tier()
				if len(tiers) > et:
								return tiers[et].aura
				return {}

func get_stat(stat, default = 0):
				var tiers = get_tiers()
				var et = get_effective_tier()
				if len(tiers) > et:
								var s = tiers[et].skill
								if s.has(stat):
												return s[stat]

				return default

func get_supporting_stat_added(stat, default = 0):
				var s = computed_support_stats_added
				if s.has(stat):
								return s[stat]
				return default

func get_supporting_stat_inc(stat, default = 0):
				var s = computed_support_stats_inc
				if s.has(stat):
								return s[stat]
				return default

func get_supporting_stat_more(stat, default = 0):
				var s = computed_support_stats_more
				if s.has(stat):
								return s[stat]
				return default

func get_conditional_supporting_stat_added(tag, stat, default = 0):
				if not computed_conditional_support_stats.has(tag):
								return default
				var s = computed_conditional_support_stats[tag].added
				if s.has(stat):
								return s[stat]
				return default

func get_conditional_supporting_stat_inc(tag, stat, default = 0):
				if not computed_conditional_support_stats.has(tag):
								return default
				var s = computed_conditional_support_stats[tag].inc
				if s.has(stat):
								return s[stat]
				return default

func get_conditional_supporting_stat_more(tag, stat, default = 0):
				if not computed_conditional_support_stats.has(tag):
								return default
				var s = computed_conditional_support_stats[tag].more
				if s.has(stat):
								return s[stat]
				return default

func get_total_damage_multiplier():
				if stats.is_enemy:
								return 1.0
				return SlotScaling.damage_multiplier[slot]

func get_damage_effectiveness():
				return get_stat("damage_effectiveness", 1.0)


func get_conversion_physical_to_lightning():
				if css.has("conversion_physical_to_lightning"):
								return css["conversion_physical_to_lightning"]
				css["conversion_physical_to_lightning"] = get_stat("conversion_physical_to_lightning", 0.0) + stats.get_conditional_modified_stat("conversion_physical_to_lightning", cached_tag_list, self)
				return css["conversion_physical_to_lightning"]

func get_conversion_physical_to_cold():
				if css.has("conversion_physical_to_cold"):
								return css["conversion_physical_to_cold"]
				css["conversion_physical_to_cold"] = get_stat("conversion_physical_to_cold", 0.0) + stats.get_conditional_modified_stat("conversion_physical_to_cold", cached_tag_list, self)
				return css["conversion_physical_to_cold"]

func get_conversion_physical_to_fire():
				if css.has("conversion_physical_to_fire"):
								return css["conversion_physical_to_fire"]
				css["conversion_physical_to_fire"] = get_stat("conversion_physical_to_fire", 0.0) + stats.get_conditional_modified_stat("conversion_physical_to_fire", cached_tag_list, self)
				return css["conversion_physical_to_fire"]

func get_conversion_physical_to_toxic():
				if css.has("conversion_physical_to_toxic"):
								return css["conversion_physical_to_toxic"]
				css["conversion_physical_to_toxic"] = get_stat("conversion_physical_to_toxic", 0.0) + stats.get_conditional_modified_stat("conversion_physical_to_toxic", cached_tag_list, self)
				return css["conversion_physical_to_toxic"]

func get_conversion_lightning_to_cold():
				if css.has("conversion_lightning_to_cold"):
								return css["conversion_lightning_to_cold"]
				css["conversion_lightning_to_cold"] = get_stat("conversion_lightning_to_cold", 0.0) + stats.get_conditional_modified_stat("conversion_lightning_to_cold", cached_tag_list, self)
				return css["conversion_lightning_to_cold"]

func get_conversion_lightning_to_fire():
				if css.has("conversion_lightning_to_fire"):
								return css["conversion_lightning_to_fire"]
				css["conversion_lightning_to_fire"] = get_stat("conversion_lightning_to_fire", 0.0) + stats.get_conditional_modified_stat("conversion_lightning_to_fire", cached_tag_list, self)
				return css["conversion_lightning_to_fire"]

func get_conversion_lightning_to_toxic():
				if css.has("conversion_lightning_to_toxic"):
								return css["conversion_lightning_to_toxic"]
				css["conversion_lightning_to_toxic"] = get_stat("conversion_lightning_to_toxic", 0.0) + stats.get_conditional_modified_stat("conversion_lightning_to_toxic", cached_tag_list, self)
				return css["conversion_lightning_to_toxic"]

func get_conversion_cold_to_fire():
				if css.has("conversion_cold_to_fire"):
								return css["conversion_cold_to_fire"]
				css["conversion_cold_to_fire"] = get_stat("conversion_cold_to_fire", 0.0) + stats.get_conditional_modified_stat("conversion_cold_to_fire", cached_tag_list, self)
				return css["conversion_cold_to_fire"]

func get_conversion_cold_to_toxic():
				if css.has("conversion_cold_to_toxic"):
								return css["conversion_cold_to_toxic"]
				css["conversion_cold_to_toxic"] = get_stat("conversion_cold_to_toxic", 0.0) + stats.get_conditional_modified_stat("conversion_cold_to_toxic", cached_tag_list, self)
				return css["conversion_cold_to_toxic"]

func get_conversion_fire_to_toxic():
				if css.has("conversion_fire_to_toxic"):
								return css["conversion_fire_to_toxic"]
				css["conversion_fire_to_toxic"] = get_stat("conversion_fire_to_toxic", 0.0) + stats.get_conditional_modified_stat("conversion_fire_to_toxic", cached_tag_list, self)
				return css["conversion_fire_to_toxic"]



func get_extra_physical_as_lightning():
				if css.has("extra_physical_as_lightning"):
								return css["extra_physical_as_lightning"]
				css["extra_physical_as_lightning"] = get_stat("extra_physical_as_lightning", 0.0) + stats.get_conditional_modified_stat("extra_physical_as_lightning", cached_tag_list, self)
				return css["extra_physical_as_lightning"]

func get_extra_physical_as_cold():
				if css.has("extra_physical_as_cold"):
								return css["extra_physical_as_cold"]
				css["extra_physical_as_cold"] = get_stat("extra_physical_as_cold", 0.0) + stats.get_conditional_modified_stat("extra_physical_as_cold", cached_tag_list, self)
				return css["extra_physical_as_cold"]

func get_extra_physical_as_fire():
				if css.has("extra_physical_as_fire"):
								return css["extra_physical_as_fire"]
				css["extra_physical_as_fire"] = get_stat("extra_physical_as_fire", 0.0) + stats.get_conditional_modified_stat("extra_physical_as_fire", cached_tag_list, self)
				return css["extra_physical_as_fire"]

func get_extra_physical_as_toxic():
				if css.has("extra_physical_as_toxic"):
								return css["extra_physical_as_toxic"]
				css["extra_physical_as_toxic"] = get_stat("extra_physical_as_toxic", 0.0) + stats.get_conditional_modified_stat("extra_physical_as_toxic", cached_tag_list, self)
				return css["extra_physical_as_toxic"]

func get_extra_lightning_as_cold():
				if css.has("extra_lightning_as_cold"):
								return css["extra_lightning_as_cold"]
				css["extra_lightning_as_cold"] = get_stat("extra_lightning_as_cold", 0.0) + stats.get_conditional_modified_stat("extra_lightning_as_cold", cached_tag_list, self)
				return css["extra_lightning_as_cold"]

func get_extra_lightning_as_fire():
				if css.has("extra_lightning_as_fire"):
								return css["extra_lightning_as_fire"]
				css["extra_lightning_as_fire"] = get_stat("extra_lightning_as_fire", 0.0) + stats.get_conditional_modified_stat("extra_lightning_as_fire", cached_tag_list, self)
				return css["extra_lightning_as_fire"]

func get_extra_lightning_as_toxic():
				if css.has("extra_lightning_as_toxic"):
								return css["extra_lightning_as_toxic"]
				css["extra_lightning_as_toxic"] = get_stat("extra_lightning_as_toxic", 0.0) + stats.get_conditional_modified_stat("extra_lightning_as_toxic", cached_tag_list, self)
				return css["extra_lightning_as_toxic"]

func get_extra_cold_as_fire():
				if css.has("extra_cold_as_fire"):
								return css["extra_cold_as_fire"]
				css["extra_cold_as_fire"] = get_stat("extra_cold_as_fire", 0.0) + stats.get_conditional_modified_stat("extra_cold_as_fire", cached_tag_list, self)
				return css["extra_cold_as_fire"]

func get_extra_cold_as_toxic():
				if css.has("extra_cold_as_toxic"):
								return css["extra_cold_as_toxic"]
				css["extra_cold_as_toxic"] = get_stat("extra_cold_as_toxic", 0.0) + stats.get_conditional_modified_stat("extra_cold_as_toxic", cached_tag_list, self)
				return css["extra_cold_as_toxic"]

func get_extra_fire_as_toxic():
				if css.has("extra_fire_as_toxic"):
								return css["extra_fire_as_toxic"]
				css["extra_fire_as_toxic"] = get_stat("extra_fire_as_toxic", 0.0) + stats.get_conditional_modified_stat("extra_fire_as_toxic", cached_tag_list, self)
				return css["extra_fire_as_toxic"]

func get_effective_stat(stat):
				if stat == "damage":
								return get_damage(false)
				if stat == "skill_effectiveness":
								return get_total_damage_multiplier()
				if stat == "damage_effectiveness":
								return get_damage_effectiveness()
				if stat == "cast_speed":
								return get_cast_speed(false)
				if stat == "crit_chance":
								return get_crit_chance(false)
				if stat == "crit_multi":
								return get_crit_multi(false)
				if stat == "projectile_speed":
								return get_force(false)
				if stat == "projectile_count":
								return get_projectiles(false)
				if stat == "skill_pierce":
								return get_pierces(false)
				if stat == "skill_chain":
								return get_chains(false)
				if stat == "base_duration":
								return get_duration(false)
				if stat == "cooldown":
								return get_cooldown(false)
				if stat == "area_of_effect":
								return get_aoe(false)
				if stat == "radius":
								return get_radius(false)
				if stat == "curse_effect":
								return get_curse_effect(false)
				if stat == "amplify_ailment_chance":
								return get_amplify_chance(false)

				if stat == "conversion_physical_to_lightning":
								return get_conversion_physical_to_lightning()
				if stat == "conversion_physical_to_cold":
								return get_conversion_physical_to_cold()
				if stat == "conversion_physical_to_fire":
								return get_conversion_physical_to_fire()
				if stat == "conversion_physical_to_toxic":
								return get_conversion_physical_to_toxic()
				if stat == "conversion_lightning_to_cold":
								return get_conversion_lightning_to_cold()
				if stat == "conversion_lightning_to_fire":
								return get_conversion_lightning_to_fire()
				if stat == "conversion_lightning_to_toxic":
								return get_conversion_lightning_to_toxic()
				if stat == "conversion_cold_to_fire":
								return get_conversion_cold_to_fire()
				if stat == "conversion_cold_to_toxic":
								return get_conversion_cold_to_toxic()
				if stat == "conversion_fire_to_toxic":
								return get_conversion_fire_to_toxic()

				if stat == "extra_physical_as_lightning":
								return get_extra_physical_as_lightning()
				if stat == "extra_physical_as_cold":
								return get_extra_physical_as_cold()
				if stat == "extra_physical_as_fire":
								return get_extra_physical_as_fire()
				if stat == "extra_physical_as_toxic":
								return get_extra_physical_as_toxic()
				if stat == "extra_lightning_as_cold":
								return get_extra_lightning_as_cold()
				if stat == "extra_lightning_as_fire":
								return get_extra_lightning_as_fire()
				if stat == "extra_lightning_as_toxic":
								return get_extra_lightning_as_toxic()
				if stat == "extra_cold_as_fire":
								return get_extra_cold_as_fire()
				if stat == "extra_cold_as_toxic":
								return get_extra_cold_as_toxic()
				if stat == "extra_fire_as_toxic":
								return get_extra_fire_as_toxic()
				if stat == "ailment_duration":
								return get_ailment_duration()

				if "_ailment_chance" in stat:
								return get_ailment_chance(stat)
				if "_ailment_effect" in stat:
								return get_ailment_effect(stat)


				if stat == "vulnerable_chance":
								return get_vulnerable_chance()
				if stat == "vulnerable_effect":
								return get_vulnerable_effect()
				if stat == "exposure_chance":
								return get_exposure_chance()
				if stat == "exposure_effect":
								return get_exposure_effect()
				if stat == "infection_count":
								return get_infection_count()

				if stat == "swiftness_boon_on_hit_chance":
								return get_swiftness_boon_on_hit_chance()
				if stat == "toughness_boon_on_hit_chance":
								return get_toughness_boon_on_hit_chance()
				if stat == "precision_boon_on_crit_chance":
								return get_precision_boon_on_crit_chance()

				if stat == "swiftness_boon_on_kill_chance":
								return get_swiftness_boon_on_kill_chance()
				if stat == "precision_boon_on_kill_chance":
								return get_precision_boon_on_kill_chance()
				if stat == "toughness_boon_on_kill_chance":
								return get_toughness_boon_on_kill_chance()
				if stat == "life_gain_on_hit":
								return get_life_gain_on_hit()

				if stat == "physical_penetration":
								return get_physical_penetration()
				if stat == "lightning_penetration":
								return get_lightning_penetration()
				if stat == "cold_penetration":
								return get_cold_penetration()
				if stat == "fire_penetration":
								return get_fire_penetration()
				if stat == "toxic_penetration":
								return get_toxic_penetration()

				return 0


func get_extra_physicals(apply_rand_keystones = false):
				return {
								SkillTags.Tags.LIGHTNING: get_extra_physical_as_lightning(), 
								SkillTags.Tags.COLD: get_extra_physical_as_cold(), 
								SkillTags.Tags.FIRE: get_extra_physical_as_fire(), 
								SkillTags.Tags.TOXIC: get_extra_physical_as_toxic(), 
				}

func get_extra_lightnings(apply_rand_keystones = false):
				return {
								SkillTags.Tags.COLD: get_extra_lightning_as_cold(), 
								SkillTags.Tags.FIRE: get_extra_lightning_as_fire(), 
								SkillTags.Tags.TOXIC: get_extra_lightning_as_toxic(), 
				}

func get_extra_colds(apply_rand_keystones = false):
				return {
								SkillTags.Tags.FIRE: get_extra_cold_as_fire(), 
								SkillTags.Tags.TOXIC: get_extra_cold_as_toxic(), 
				}

func get_extra_fires(apply_rand_keystones = false):
				return {
								SkillTags.Tags.TOXIC: get_extra_fire_as_toxic(), 
				}

func get_penetrations(apply_rand_keystones = false):
				return {
								SkillTags.Tags.PHYSICAL: get_physical_penetration(), 
								SkillTags.Tags.LIGHTNING: get_lightning_penetration(), 
								SkillTags.Tags.COLD: get_cold_penetration(), 
								SkillTags.Tags.FIRE: get_fire_penetration(), 
								SkillTags.Tags.TOXIC: get_toxic_penetration(), 
				}

func get_base_damage(apply_rand_keystones = true):
				return get_stat("damage")

func get_damage(apply_rand_keystones = true, use_cache = true, apply_as = null):
				
				var damage = get_base_damage()
				var effectiveness_of_added = get_damage_effectiveness()

				var global_damage_parts = stats.get_conditional_modified_stat_parts("all_damage", cached_tag_list, self)
				var keystone_damage_multiplier = 1.0

				if stats.keystones.has("TREE_KINETIC_PROJECTILES") and has_tag(SkillTags.Tags.PROJECTILE):
								keystone_damage_multiplier *= 1.3

				if stats.keystones.has("TREE_TIME_WARP") and has_tag(SkillTags.Tags.DURATION):
								keystone_damage_multiplier *= 1.4

				
				if stats.keystones.has("TREE_OVERLOADED_SHELLS") and has_tag(SkillTags.Tags.PROJECTILE):
								keystone_damage_multiplier *= 1.1

				
				var all_damage = global_damage_parts.inc
				var more_damage = 1.0 * global_damage_parts.more * global_damage_parts.base * keystone_damage_multiplier * get_total_damage_multiplier()

				if is_triggered and keystones.has("SUPPORT_VOLATILITY"):
								var n_boons = stats.get_boon_count()
								var damage_multiplier = 1.0 + 0.2 * n_boons
								more_damage *= damage_multiplier

				
				for tag in get_tags():
								if tag == SkillTags.Tags.PROJECTILE:
												var parts = stats.get_conditional_modified_stat_parts("projectile_damage", cached_tag_list, self)
												all_damage += parts.inc
												more_damage *= parts.more
								elif tag == SkillTags.Tags.AREA:
												var parts = stats.get_conditional_modified_stat_parts("area_damage", cached_tag_list, self)
												all_damage += parts.inc
												more_damage *= parts.more
								elif tag == SkillTags.Tags.DOT:
												var parts = stats.get_conditional_modified_stat_parts("dot_damage", cached_tag_list, self)
												all_damage += parts.inc
												more_damage *= parts.more
								elif tag == SkillTags.Tags.HIT:
												var parts = stats.get_conditional_modified_stat_parts("hit_damage", cached_tag_list, self)
												all_damage += parts.inc
												more_damage *= parts.more

				
				var base_damages = {}
				var computed_damages = {}

				
				for tag in SkillTags.DAMAGE_TAGS:
								base_damages[tag] = []

				
				for tag in SkillTags.DAMAGE_TAGS:
								var parts
								var amount = 0
								if tag == SkillTags.Tags.PHYSICAL:
													parts = stats.get_conditional_modified_stat_parts("physical_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.LIGHTNING:
													parts = stats.get_conditional_modified_stat_parts("lightning_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.COLD:
													parts = stats.get_conditional_modified_stat_parts("cold_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.FIRE:
													parts = stats.get_conditional_modified_stat_parts("fire_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.TOXIC:
													parts = stats.get_conditional_modified_stat_parts("toxic_damage", cached_tag_list, self)

									
								if tag == damage_tag:
												amount += damage

								amount += parts.add * effectiveness_of_added

								if keystones.has("SUPPORT_SACRIFICE") and tag == SkillTags.Tags.PHYSICAL:
												var sacrifice_added = 0.05 * stats.gs("health_max")
												amount += sacrifice_added

								if amount > 0:
												base_damages[tag].append({"amount": amount, "tags": [tag]})

				
				for tag in SkillTags.DAMAGE_TAGS:
								var parts
								var amounts = base_damages[tag]

								if len(amounts) == 0:
												
												continue

								var total_amount = 0
								for info in amounts:
												total_amount += info.amount

								
								if tag == SkillTags.Tags.PHYSICAL:
												var lightning = get_conversion_physical_to_lightning()
												var cold = get_conversion_physical_to_cold()
												var fire = get_conversion_physical_to_fire()
												var toxic = get_conversion_physical_to_toxic()
												var total_conversion = lightning + cold + fire + toxic
												if lightning > 0:
																var lightning_amount = (lightning / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * lightning_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.LIGHTNING)
																				base_damages[SkillTags.Tags.LIGHTNING].append({"amount": transferred_amount, "tags": transferred_tags})
												if cold > 0:
																var cold_amount = (cold / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * cold_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.COLD)
																				base_damages[SkillTags.Tags.COLD].append({"amount": transferred_amount, "tags": transferred_tags})
												if fire > 0:
																var fire_amount = (fire / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * fire_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.FIRE)
																				base_damages[SkillTags.Tags.FIRE].append({"amount": transferred_amount, "tags": transferred_tags})
												if toxic > 0:
																var toxic_amount = (toxic / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * toxic_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})

												
												var physical_extras = get_extra_physicals(apply_rand_keystones)
												var extra_lightning = physical_extras[SkillTags.Tags.LIGHTNING]
												var extra_cold = physical_extras[SkillTags.Tags.COLD]
												var extra_fire = physical_extras[SkillTags.Tags.FIRE]
												var extra_toxic = physical_extras[SkillTags.Tags.TOXIC]
												if extra_lightning > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_lightning
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.LIGHTNING)
																				base_damages[SkillTags.Tags.LIGHTNING].append({"amount": transferred_amount, "tags": transferred_tags})
												if extra_cold > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_cold
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.COLD)
																				base_damages[SkillTags.Tags.COLD].append({"amount": transferred_amount, "tags": transferred_tags})
												if extra_fire > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_fire
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.FIRE)
																				base_damages[SkillTags.Tags.FIRE].append({"amount": transferred_amount, "tags": transferred_tags})
												if extra_toxic > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_toxic
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})

												
												for amount in base_damages[tag]:
																
																amount.amount *= max(0.0, 1.0 - total_conversion)

								
								if tag == SkillTags.Tags.LIGHTNING:
												var cold = get_conversion_lightning_to_cold()
												var fire = get_conversion_lightning_to_fire()
												var toxic = get_conversion_lightning_to_toxic()
												var total_conversion = cold + fire + toxic
												if cold > 0:
																var cold_amount = (cold / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * cold_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.COLD)
																				base_damages[SkillTags.Tags.COLD].append({"amount": transferred_amount, "tags": transferred_tags})
												if fire > 0:
																var fire_amount = (fire / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * fire_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.FIRE)
																				base_damages[SkillTags.Tags.FIRE].append({"amount": transferred_amount, "tags": transferred_tags})
												if toxic > 0:
																var toxic_amount = (toxic / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * toxic_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})

												
												var lightning_extras = get_extra_lightnings(apply_rand_keystones)
												var extra_cold = lightning_extras[SkillTags.Tags.COLD]
												var extra_fire = lightning_extras[SkillTags.Tags.FIRE]
												var extra_toxic = lightning_extras[SkillTags.Tags.TOXIC]
												if extra_cold > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_cold
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.COLD)
																				base_damages[SkillTags.Tags.COLD].append({"amount": transferred_amount, "tags": transferred_tags})
												if extra_fire > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_fire
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.FIRE)
																				base_damages[SkillTags.Tags.FIRE].append({"amount": transferred_amount, "tags": transferred_tags})
												if extra_toxic > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_toxic
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})

												
												for amount in base_damages[tag]:
																
																amount.amount *= max(0.0, 1.0 - total_conversion)


								
								if tag == SkillTags.Tags.COLD:
												var fire = get_conversion_cold_to_fire()
												var toxic = get_conversion_cold_to_toxic()
												var total_conversion = fire + toxic
												if fire > 0:
																var fire_amount = (fire / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * fire_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.FIRE)
																				base_damages[SkillTags.Tags.FIRE].append({"amount": transferred_amount, "tags": transferred_tags})
												if toxic > 0:
																var toxic_amount = (toxic / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * toxic_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})

												
												var cold_extras = get_extra_colds(apply_rand_keystones)
												var extra_fire = cold_extras[SkillTags.Tags.FIRE]
												var extra_toxic = cold_extras[SkillTags.Tags.TOXIC]
												if extra_fire > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_fire
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.FIRE)
																				base_damages[SkillTags.Tags.FIRE].append({"amount": transferred_amount, "tags": transferred_tags})
												if extra_toxic > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_toxic
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})

												
												for amount in base_damages[tag]:
																
																amount.amount *= max(0.0, 1.0 - total_conversion)


								
								if tag == SkillTags.Tags.FIRE:
												var toxic = get_conversion_fire_to_toxic()
												var total_conversion = toxic
												if toxic > 0:
																var toxic_amount = (toxic / max(total_conversion, 1.0))
																for amount in amounts:
																				var transferred_amount = amount.amount * toxic_amount
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})
																								

												
												var fire_extras = get_extra_fires(apply_rand_keystones)
												var extra_toxic = fire_extras[SkillTags.Tags.TOXIC]
												if extra_toxic > 0:
																for amount in amounts:
																				var transferred_amount = amount.amount * extra_toxic
																				var transferred_tags = amount.tags.duplicate()
																				transferred_tags.append(SkillTags.Tags.TOXIC)
																				base_damages[SkillTags.Tags.TOXIC].append({"amount": transferred_amount, "tags": transferred_tags})
												
												for amount in base_damages[tag]:
																
																amount.amount *= max(0.0, 1.0 - total_conversion)

				var parts_for_tag = {}

				
				for tag in SkillTags.DAMAGE_TAGS:
								if len(base_damages[tag]) == 0 and not stats.keystones.has("UNIQUE_CROWN_OF_ICE") and not apply_as:
												continue
								if tag == SkillTags.Tags.PHYSICAL:
													parts_for_tag[tag] = stats.get_conditional_modified_stat_parts("physical_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.LIGHTNING:
													parts_for_tag[tag] = stats.get_conditional_modified_stat_parts("lightning_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.COLD:
													parts_for_tag[tag] = stats.get_conditional_modified_stat_parts("cold_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.FIRE:
													parts_for_tag[tag] = stats.get_conditional_modified_stat_parts("fire_damage", cached_tag_list, self)
								if tag == SkillTags.Tags.TOXIC:
													parts_for_tag[tag] = stats.get_conditional_modified_stat_parts("toxic_damage", cached_tag_list, self)

				if stats.keystones.has("UNIQUE_CROWN_OF_ICE"):
								
								for tag in SkillTags.DAMAGE_TAGS:
												if tag == SkillTags.Tags.COLD:
																continue
												for amount in base_damages[tag]:
																var transferred_amount = amount.amount
																var transferred_tags = amount.tags.duplicate()
																if not transferred_tags.has(SkillTags.Tags.COLD):
																				transferred_tags.append(SkillTags.Tags.COLD)
																base_damages[SkillTags.Tags.COLD].append({"amount": transferred_amount, "tags": transferred_tags})
												
												base_damages[tag] = []
				else:
								if apply_as != null:
												
												for tag in SkillTags.DAMAGE_TAGS:
																if tag == apply_as:
																				continue
																for amount in base_damages[tag]:
																				var transferred_amount = amount.amount
																				var transferred_tags = amount.tags.duplicate()
																				if not transferred_tags.has(apply_as):
																								transferred_tags.append(apply_as)
																				base_damages[apply_as].append({"amount": transferred_amount, "tags": transferred_tags})
																
																base_damages[tag] = []

				for tag in SkillTags.DAMAGE_TAGS:
								var accumulated = 0
								for amount in base_damages[tag]:
												var applicable_tag_more = 1.0
												var applicable_tag_inc = 0.0
												for applied_tag in amount.tags:
																var more_amount = parts_for_tag[applied_tag].more * parts_for_tag[applied_tag].base
																applicable_tag_more *= more_amount
																var inc_amount = parts_for_tag[applied_tag].inc
																applicable_tag_inc += inc_amount

												var combined_inc = all_damage + applicable_tag_inc
												var combined_more = more_damage * applicable_tag_more
												var amount_from_amount = amount.amount * (1.0 + combined_inc) * combined_more
												accumulated += amount_from_amount
								if accumulated > 0:
												computed_damages[tag] = accumulated

				return computed_damages


func get_ailment_chance(type):
				if css.has(type):
								return css[type]
				var parts = stats.get_conditional_modified_stat_parts(type, cached_tag_list, self)
				var base = get_stat(type)
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css[type] = output
				return output

func get_ailment_effect(type):
				if css.has(type):
								return css[type]
				var parts = stats.get_conditional_modified_stat_parts(type, cached_tag_list, self)
				var base = get_stat(type)
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = compiled
				css[type] = output
				return output

func get_ailment_duration(apply_rand_keystones = true):
				if css.has("ailment_duration"):
								return css["ailment_duration"]
				var parts = stats.get_conditional_modified_stat_parts("ailment_duration", cached_tag_list, self)
				var base = get_stat("ailment_duration")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["ailment_duration"] = compiled
				return compiled

func get_ailment_chances(apply_rand_keystones = true):
				return {
								SkillTags.Tags.PHYSICAL: get_ailment_chance("physical_ailment_chance"), 
								SkillTags.Tags.LIGHTNING: get_ailment_chance("lightning_ailment_chance"), 
								SkillTags.Tags.COLD: get_ailment_chance("cold_ailment_chance"), 
								SkillTags.Tags.FIRE: get_ailment_chance("fire_ailment_chance"), 
								SkillTags.Tags.TOXIC: get_ailment_chance("toxic_ailment_chance"), 
				}

func get_ailment_effects(apply_rand_keystones = true):
				return {
								SkillTags.Tags.PHYSICAL: get_ailment_effect("physical_ailment_effect"), 
								SkillTags.Tags.LIGHTNING: get_ailment_effect("lightning_ailment_effect"), 
								SkillTags.Tags.COLD: get_ailment_effect("cold_ailment_effect"), 
								SkillTags.Tags.FIRE: get_ailment_effect("fire_ailment_effect"), 
								SkillTags.Tags.TOXIC: get_ailment_effect("toxic_ailment_effect"), 
				}

func get_amplify_chance(apply_rand_keystones = true):
				if css.has("amplify_ailment_chance"):
								return css["amplify_ailment_chance"]
				var parts = stats.get_conditional_modified_stat_parts("amplify_ailment_chance", cached_tag_list, self)
				var base = get_stat("amplify_ailment_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["amplify_ailment_chance"] = output
				return output

func get_vulnerable_chance(apply_rand_keystones = true):
				if css.has("vulnerable_chance"):
								return css["vulnerable_chance"]
				var parts = stats.get_conditional_modified_stat_parts("vulnerable_chance", cached_tag_list, self)
				var base = get_stat("vulnerable_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["vulnerable_chance"] = output
				return output


func get_vulnerable_effect(apply_rand_keystones = true):
				if css.has("vulnerable_effect"):
								return css["vulnerable_effect"]
				var parts = stats.get_conditional_modified_stat_parts("vulnerable_effect", cached_tag_list, self)
				var base = get_stat("vulnerable_effect")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["vulnerable_effect"] = compiled
				return compiled

func get_exposure_chance(apply_rand_keystones = true):
				if css.has("exposure_chance"):
								return css["exposure_chance"]
				var parts = stats.get_conditional_modified_stat_parts("exposure_chance", cached_tag_list, self)
				var base = get_stat("exposure_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["exposure_chance"] = output
				return output

func get_exposure_effect(apply_rand_keystones = true):
				if css.has("exposure_effect"):
								return css["exposure_effect"]
				var parts = stats.get_conditional_modified_stat_parts("exposure_effect", cached_tag_list, self)
				var base = get_stat("exposure_effect")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["exposure_effect"] = compiled
				return compiled

func get_infection_count(apply_rand_keystones = true):
				if css.has("infection_count"):
								return css["infection_count"]
				var parts = stats.get_conditional_modified_stat_parts("infection_count", cached_tag_list, self)
				var base = get_stat("infection_count")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["infection_count"] = compiled
				return compiled

func get_dot_damage(apply_rand_keystones = true):
				if css.has("dot_damage"):
								return css["dot_damage"]
				var parts = stats.get_conditional_modified_stat_parts("dot_damage", cached_tag_list, self)
				var base = get_stat("dot_damage")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["dot_damage"] = compiled
				return compiled

func get_physical_penetration(apply_rand_keystones = true):
				if css.has("physical_penetration"):
								return css["physical_penetration"]
				var parts = stats.get_conditional_modified_stat_parts("physical_penetration", cached_tag_list, self)
				var base = get_stat("physical_penetration")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["physical_penetration"] = compiled
				return compiled

func get_lightning_penetration(apply_rand_keystones = true):
				if css.has("lightning_penetration"):
								return css["lightning_penetration"]
				var parts = stats.get_conditional_modified_stat_parts("lightning_penetration", cached_tag_list, self)
				var base = get_stat("lightning_penetration")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["lightning_penetration"] = compiled
				return compiled

func get_cold_penetration(apply_rand_keystones = true):
				if css.has("cold_penetration"):
								return css["cold_penetration"]
				var parts = stats.get_conditional_modified_stat_parts("cold_penetration", cached_tag_list, self)
				var base = get_stat("cold_penetration")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["cold_penetration"] = compiled
				return compiled

func get_fire_penetration(apply_rand_keystones = true):
				if css.has("fire_penetration"):
								return css["fire_penetration"]
				var parts = stats.get_conditional_modified_stat_parts("fire_penetration", cached_tag_list, self)
				var base = get_stat("fire_penetration")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["fire_penetration"] = compiled
				return compiled

func get_toxic_penetration(apply_rand_keystones = true):
				if css.has("toxic_penetration"):
								return css["toxic_penetration"]
				var parts = stats.get_conditional_modified_stat_parts("toxic_penetration", cached_tag_list, self)
				var base = get_stat("toxic_penetration")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["toxic_penetration"] = compiled
				return compiled

func get_crit_multi(apply_rand_keystones = true):
				if css.has("crit_multi"):
								return css["crit_multi"]
				var parts = stats.get_conditional_modified_stat_parts("crit_multi", cached_tag_list, self)
				var base = get_stat("crit_multi")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["crit_multi"] = compiled
				return compiled

func get_crit_chance(apply_rand_keystones = true):
				if css.has("crit_chance"):
								return css["crit_chance"]
				var crit_parts = stats.get_conditional_modified_stat_parts("crit_chance", cached_tag_list, self)
				var base = get_stat("crit_chance")
				var crit_chance = (base + crit_parts.base + crit_parts.add) * (1.0 + crit_parts.inc) * crit_parts.more
				var output = min(1.0, crit_chance)
				css["crit_chance"] = output
				return output

func get_swiftness_boon_on_hit_chance(apply_rand_keystones = true):
				if css.has("swiftness_boon_on_hit_chance"):
								return css["swiftness_boon_on_hit_chance"]
				var parts = stats.get_conditional_modified_stat_parts("swiftness_boon_on_hit_chance", cached_tag_list, self)
				var base = get_stat("swiftness_boon_on_hit_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["swiftness_boon_on_hit_chance"] = output
				return output

func get_toughness_boon_on_hit_chance(apply_rand_keystones = true):
				if css.has("toughness_boon_on_hit_chance"):
								return css["toughness_boon_on_hit_chance"]
				var parts = stats.get_conditional_modified_stat_parts("toughness_boon_on_hit_chance", cached_tag_list, self)
				var base = get_stat("toughness_boon_on_hit_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["toughness_boon_on_hit_chance"] = output
				return output

func get_precision_boon_on_crit_chance(apply_rand_keystones = true):
				if css.has("precision_boon_on_crit_chance"):
								return css["precision_boon_on_crit_chance"]
				var parts = stats.get_conditional_modified_stat_parts("precision_boon_on_crit_chance", cached_tag_list, self)
				var base = get_stat("precision_boon_on_crit_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["precision_boon_on_crit_chance"] = output
				return output

func get_swiftness_boon_on_kill_chance(apply_rand_keystones = true):
				if css.has("swiftness_boon_on_kill_chance"):
								return css["swiftness_boon_on_kill_chance"]
				var parts = stats.get_conditional_modified_stat_parts("swiftness_boon_on_kill_chance", cached_tag_list, self)
				var base = get_stat("swiftness_boon_on_kill_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["swiftness_boon_on_kill_chance"] = output
				return output

func get_precision_boon_on_kill_chance(apply_rand_keystones = true):
				if css.has("precision_boon_on_kill_chance"):
								return css["precision_boon_on_kill_chance"]
				var parts = stats.get_conditional_modified_stat_parts("precision_boon_on_kill_chance", cached_tag_list, self)
				var base = get_stat("precision_boon_on_kill_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["precision_boon_on_kill_chance"] = output
				return output

func get_toughness_boon_on_kill_chance(apply_rand_keystones = true):
				if css.has("toughness_boon_on_kill_chance"):
								return css["toughness_boon_on_kill_chance"]
				var parts = stats.get_conditional_modified_stat_parts("toughness_boon_on_kill_chance", cached_tag_list, self)
				var base = get_stat("toughness_boon_on_kill_chance")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				var output = min(1.0, compiled)
				css["toughness_boon_on_kill_chance"] = output
				return output

func get_life_gain_on_hit(apply_rand_keystones = true):
				if css.has("life_gain_on_hit"):
								return css["life_gain_on_hit"]
				var parts = stats.get_conditional_modified_stat_parts("life_gain_on_hit", cached_tag_list, self)
				var base = get_stat("life_gain_on_hit")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["life_gain_on_hit"] = compiled
				return compiled

func get_damage_bundle(apply_rand_keystones = true, use_cache = true, apply_as = null):
				if use_cache and cached_outputs.has("damage_bundle"):
								return cached_outputs.damage_bundle.duplicate(true)

				cached_outputs.damage_bundle = {
								"damage": get_damage(apply_rand_keystones, use_cache, apply_as), 
								"crit": {
												"chance": get_crit_chance(apply_rand_keystones), 
												"multi": get_crit_multi(apply_rand_keystones), 
								}, 
								"ailment": {
												"chance": get_ailment_chances(apply_rand_keystones), 
												"effect": get_ailment_effects(apply_rand_keystones), 
												"amplify": get_amplify_chance(apply_rand_keystones)
								}, 
								"vulnerable": {
												"chance": get_vulnerable_chance(apply_rand_keystones), 
												"effect": get_vulnerable_effect(apply_rand_keystones), 
								}, 
								"exposure": {
												"chance": get_exposure_chance(apply_rand_keystones), 
												"effect": get_exposure_effect(apply_rand_keystones), 
								}, 
								"infections": get_infection_count(apply_rand_keystones)
				}
				var pens = get_penetrations(apply_rand_keystones)
				var passed = false
				for p in pens:
								if pens[p] != 0:
												passed = true
				if passed:
								cached_outputs.damage_bundle["penetrations"] = pens
				return cached_outputs.damage_bundle

func get_force(apply_rand_keystones = true):
				if css.has("projectile_speed"):
								return css["projectile_speed"]
				if stats.keystones.has("TREE_KINETIC_PROJECTILES"):
								css["projectile_speed"] = get_stat("projectile_speed")
								return css["projectile_speed"]
				var parts = stats.get_conditional_modified_stat_parts("projectile_speed", cached_tag_list, self)
				var base = get_stat("projectile_speed")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["projectile_speed"] = compiled
				return compiled

func get_projectiles(apply_rand_keystones = true):
				if css.has("projectile_count") and not stats.keystones.has("TREE_VOLLEY"):
								return css["projectile_count"]
				var parts = stats.get_conditional_modified_stat_parts("projectile_count", cached_tag_list, self)
				var base = get_stat("projectile_count")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more

				if stats.keystones.has("TREE_VOLLEY") and randf() < 0.1 and has_tag(SkillTags.Tags.PROJECTILE) and apply_rand_keystones:
								compiled *= 2

				css["projectile_count"] = ceil(compiled)
				return css["projectile_count"]

func get_pierces(apply_rand_keystones = true):
				if css.has("skill_pierce"):
								return css["skill_pierce"]
				var parts = stats.get_conditional_modified_stat_parts("skill_pierce", cached_tag_list, self)
				var base = get_stat("skill_pierce")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				if stats.keystones.has("TREE_PIERCING_TRUTH"):
								compiled *= 2
				css["skill_pierce"] = compiled
				return compiled

func get_chains(apply_rand_keystones = true):
				if css.has("skill_chain"):
								return css["skill_chain"]
				var parts = stats.get_conditional_modified_stat_parts("skill_chain", cached_tag_list, self)
				var base = get_stat("skill_chain")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["skill_chain"] = compiled
				return compiled

func get_extra_hits():
				return get_pierces() + get_chains()

func get_duration(apply_rand_keystones = true):
				if css.has("duration"):
								return css["duration"]
				var parts = stats.get_conditional_modified_stat_parts("increased_duration", cached_tag_list, self)
				var base = get_stat("base_duration")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more

				if stats.keystones.has("TREE_CURSE_DURATION") and has_tag(SkillTags.Tags.CURSE):
								compiled *= 1.5

				if stats.keystones.has("TREE_FRAGILE_CURSES") and has_tag(SkillTags.Tags.CURSE):
								compiled *= 0.5

				if stats.keystones.has("TREE_TIME_WARP") and has_tag(SkillTags.Tags.DAMAGING) and has_tag(SkillTags.Tags.DURATION):
								compiled /= 1.4

				if stats.keystones.has("TREE_REPEATER") and has_tag(SkillTags.Tags.DURATION):
								compiled *= 0.7

				css["duration"] = compiled
				return compiled

func get_cast_speed(apply_rand_keystones = true):
				if css.has("cast_speed"):
								return css["cast_speed"]
				var parts = stats.get_conditional_modified_stat_parts("cast_speed", cached_tag_list, self)
				var base = get_stat("cast_speed")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["cast_speed"] = compiled
				return compiled

func get_cooldown(apply_rand_keystones = true):
				if is_triggered:
								return 0.1
				var cp = get_cast_speed()
				if cp == 0:
								return 1.0
				var cd = get_stat("cooldown", 1.0) / cp
				var clamped = max(cd, 0.025)
				return clamped

func get_aoe(apply_rand_keystones = true):
				if css.has("area_of_effect"):
								return css["area_of_effect"]
				var parts = stats.get_conditional_modified_stat_parts("area_of_effect", cached_tag_list, self)
				var base = get_stat("area_of_effect")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["area_of_effect"] = compiled
				return compiled

func get_radius(apply_rand_keystones = true):
				if css.has("radius"):
								return css["radius"]
				var parts = stats.get_conditional_modified_stat_parts("radius", cached_tag_list, self)
				var base = get_stat("radius")
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["radius"] = compiled * sqrt(get_aoe())
				return css["radius"]

func get_cast_range(apply_random_keystones = true):
				return get_radius(apply_random_keystones)

func get_curse_effect(apply_rand_keystones = true):
				if css.has("curse_effect"):
								return css["curse_effect"]
				var parts = stats.get_conditional_modified_stat_parts("curse_effect", cached_tag_list, self)
				var base = get_stat("curse_effect", 1.0)
				var compiled = (base + parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				css["curse_effect"] = compiled
				return compiled

func get_projectile_spread(n_proj):
				if keystones.has("SUPPORT_SNIPER"):
								return 0
				return max(0, min(45, (n_proj - 1) * 15) * PI / 180)

func _cast():
				if cooldown <= 0:
								cooldown = get_cooldown()
								if not is_disabled and can_cast():
												
												if stats.keystones.has("UNIQUE_BOMB_SPECIALIST"):
																
																if cached_tags.has(SkillTags.Tags.DAMAGING) and not cached_tags.has(SkillTags.Tags.BOMB):
																				return
												if can_pay_cost():
																pay_cost()
																cast()

func consume_boons():
				if is_triggered and keystones.has("SUPPORT_VOLATILITY"):
								stats.remove_all_boons()

func can_pay_cost():
				if keystones.has("SUPPORT_SACRIFICE"):
								var cost = stats.gs("health_max") * 0.1
								if stats.health <= stats.gs("health_max") * 0.1:
												return false
				return true

func pay_cost():
				if keystones.has("SUPPORT_SACRIFICE"):
								var cost = stats.gs("health_max") * 0.1
								stats.reduce_health(cost)

func can_cast():
				return true

func cast():
				return false

func get_visible_enemies(check_collision = false, max_distance = INF):
				return stats.get_visible_enemies(check_collision, max_distance)

func track_hit(info):
				var did_kill = info.did_kill
				var damage = info.damage
				highest_damage = max(highest_damage, damage)
				if did_kill:
								total_kills += 1
				total_damage += damage

func play_sound():
				if has_node("Audio"):
								if get_parent().get_parent().is_in_group("player"):
												Globals.play_sound_effect(get_node("Audio").stream)
