extends Node2D

var mutation_tier_levelup_sound = preload("res://Sounds/Misc/levelup.wav")
var block_sound = preload("res://Sounds/SFX/block.wav")
var arc_spark = preload("res://Scenes/Particles/SparkExplosion.tscn")
var sanguine_explosion = preload("res://Scenes/Explosions/SanguineDecayExplosion.tscn")
var hysteria_explosion = preload("res://Scenes/Explosions/TexturedExplosions/HysteriaExplosion.tscn")
var fury_explosion = preload("res://Scenes/Explosions/TexturedExplosions/EchoingFuryExplosion.tscn")
var area_damage_applier = preload("res://Scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.tscn")
var toxic_runner_effect = preload("res://Scenes/StatusEffects/Keystones/ToxicRunner.tscn")
var kill_momentum_effect = preload("res://Scenes/StatusEffects/Keystones/KillMomentum.tscn")
var growing_pain_effect = preload("res://Scenes/StatusEffects/Keystones/GrowingPain.tscn")
var recently_hit_effect = preload("res://Scenes/StatusEffects/Generic/RecentlyHit.tscn")
var adrenaline_effect = preload("res://Scenes/StatusEffects/Keystones/Adrenaline.tscn")
var spike_armor_effect = preload("res://Scenes/StatusEffects/Keystones/SpikeArmor.tscn")
var vampiric_skin_effect = preload("res://Scenes/StatusEffects/Keystones/VampiricSkin.tscn")
var endurance_effect = preload("res://Scenes/StatusEffects/Keystones/Endurance.tscn")
var hardened_flesh_effect = preload("res://Scenes/StatusEffects/Keystones/HardenedFlesh.tscn")
var transfusion_effect = preload("res://Scenes/StatusEffects/Keystones/Transfusion.tscn")
var blood_boil_effect = preload("res://Scenes/StatusEffects/Keystones/BloodBoil.tscn")
var echoing_effect = preload("res://Scenes/StatusEffects/Generic/Echoing.tscn")

var swiftness_boon_effect = preload("res://Scenes/StatusEffects/Boons/SwiftnessBoon.tscn")
var precision_boon_effect = preload("res://Scenes/StatusEffects/Boons/PrecisionBoon.tscn")
var toughness_boon_effect = preload("res://Scenes/StatusEffects/Boons/ToughnessBoon.tscn")

var arc_sound = preload("res://Sounds/Skills/Shots/arc.wav")


var bleed_effect = preload("res://Scenes/StatusEffects/DamageAilments/Bleed.tscn")
var rupture_effect = preload("res://Scenes/StatusEffects/DamageAilments/Rupture.tscn")

var jolt_effect = preload("res://Scenes/StatusEffects/DamageAilments/Jolt.tscn")
var electrocute_effect = preload("res://Scenes/StatusEffects/DamageAilments/Electrocution.tscn")

var chilled_effect = preload("res://Scenes/StatusEffects/DamageAilments/Chill.tscn")
var frozen_effect = preload("res://Scenes/StatusEffects/DamageAilments/Freeze.tscn")

var charred_effect = preload("res://Scenes/StatusEffects/DamageAilments/Charred.tscn")
var burn_effect = preload("res://Scenes/StatusEffects/DamageAilments/Burn.tscn")

var poison_effect = preload("res://Scenes/StatusEffects/DamageAilments/Poison.tscn")
var infection_effect = preload("res://Scenes/StatusEffects/DamageAilments/Infection.tscn")

var vulnerable_status_effect = preload("res://Scenes/StatusEffects/Generic/Vulnerable.tscn")
var exposed_status_effect = preload("res://Scenes/StatusEffects/Generic/Exposed.tscn")

var hamstring_effect = preload("res://Scenes/StatusEffects/Generic/Hamstrung.tscn")


var cycle_of_destruction = preload("res://Scenes/KeystoneCycles/CycleOfDestruction.tscn")
var goblins_girdle = preload("res://Scenes/KeystoneCycles/GoblinsGirdle.tscn")
var regenerative_flesh = preload("res://Scenes/KeystoneCycles/RegenerativeFlesh.tscn")
var phantom_shield = preload("res://Scenes/KeystoneCycles/PhantomShield.tscn")
var unleash = preload("res://Scenes/KeystoneCycles/Unleash.tscn")


var dread_aura = preload("res://Scenes/Skills/AcquiredSkills/DreadAura/DreadAura.tscn")
var vile_domain_aura = preload("res://Scenes/Skills/AcquiredSkills/VileDomainAura/VileDomainAura.tscn")
var blood_armor_skill = preload("res://Scenes/Skills/AcquiredSkills/BloodArmorExplosion/BloodArmorExplosion.tscn")
var energetic_flesh_skill = preload("res://Scenes/Skills/AcquiredSkills/EnergeticFlesh/EnergeticFlesh.tscn")
var bonded_electrons_skill = preload("res://Scenes/Skills/AcquiredSkills/BondedElectrons/BondedElectrons.tscn")

onready var level_scene = GameState.get_global("level_layer")
onready var ground_layer = GameState.get_global("ground")
onready var floating_damage = $FloatingDamageManager
onready var status_effects = $StatusEffects
onready var cycles = $Cycles
onready var damage_text = $DamageText

signal status_effect_changed
signal health_changed
signal stats_changed
signal damage_taken(amounts, attacker_stats, was_crit)
signal kill_change
signal orb_pickup(type, amount)
signal died
signal powerup
signal shielded
signal vulnerable(is_vulnerable)


var _needs_recompute_on_status_changed = false
var _needs_status_flag_recache = false

var active_damaging_ailments = {}
var damage_ailment_applier = {}
var accumulated_time = 0
var health = 100.0
var prior_health = 0.0
var is_boss = false

var nearby_enemies = {}

export var target_group = "enemies"
export var allies_group = "allies"


var cached_stats = {}


export var override_stats = {}


var base_stats = {}


var added_stats = {}

var inc_stats = {}

var more_stats = {}


var effect_added_stats = {}
var effect_inc_stats = {}
var effect_more_stats = {}


var level = 1


var accumulated_dot_damage = 0.0
var accumulated_capacity_damage = 0.0
var accumulated_applied_damage = 0.0
var last_damage_time = 0.0
var time_since_first_damage = 0.0
export var track_dps = false

var keystones = {}
var status_flags = {}
var unique_status_flags = {}
var status_flag_amounts = {}
var affecting_ailment_count = 0
var cached_effects = []
var cached_level_buffs = null
var cached_passive_buffs = null
var cached_gene_buffs = null


var effective_mitigation = 0.0
var effective_evasion = 0.0

var has_incoming_conversions = false

var use_conditional_stats = false
var conditional_stats = {}

var _should_recompute = false

var metrics = {
				"kills": 0, 
				"xp": 0, 
				"mutagen": 0, 
				"unlocks": 0, 
				"recovered_health": 0, 
				"orbs": {
								"blue": 0, 
								"red": 0, 
								"green": 0, 
								"gold": 0, 
								"corruption": 0, 
				}, 
				"elite_kills": 0, 
				"boss_kills": 0
}

var is_dead = false

var effect_for_group = {}

var is_player = false
var is_enemy = false

var cached_gear = []
var has_triggered_skill = false


func _initialize_stats():
				initialize_override_stats()
				initialize_monster_map_mod_stats()
				initialize_player_map_mod_stats()
				reset_stats()

func _ready() -> void :
				if get_parent().is_in_group("player"):
								is_player = true
								GameState.connect("mutation_tier_increased", self, "_on_levelup")
								get_parent().connect("gear_changed", self, "_recache_gear")
								GameState.connect("skills_changed", self, "_recache_gear")
								call_deferred("_recache_gear")
				if get_parent().is_in_group("enemies"):
								is_enemy = true
								is_boss = get_parent().is_level_boss

				if target_group == "allies":
								$Area2D.collision_mask = 1

				if target_group == "enemies":
								$Area2D.collision_mask = 2

				_initialize_stats()

				if is_player:
								use_conditional_stats = true
								recompute_level_buffs()
								recompute_passive_stats()
								recompute_gene_stats()

				if not track_dps:
								damage_text.visible = false

				health = gs("health_max")

func _recache_gear():
				has_triggered_skill = false
				cached_gear = []
				var candidates = get_parent().gear.get_children()
				for skill in candidates:
								if skill.is_queued_for_deletion():
												print("Skipping deleted gear")
								else:
												cached_gear.append(skill)
												if skill.is_triggered:
																has_triggered_skill = true

func get_effective_level():
				if is_player:
								return GameState.get_account_level()
				return level

func handle_status_change(should_recompute = false):
				_needs_recompute_on_status_changed = false
				_needs_status_flag_recache = false
				_should_recompute = false

				perform_recompute_status_effects()

				
				cached_effects = []
				for child in status_effects.get_children():
								if child.expired:
												continue
								if not child.is_active:
												continue
								if child.is_queued_for_deletion():
												continue
								cached_effects.append(weakref(child))
				if should_recompute:
								
								recompute_stats()

func _physics_process(delta: float) -> void :
				if _needs_recompute_on_status_changed or _needs_status_flag_recache or _should_recompute:
								
								handle_status_change(_needs_recompute_on_status_changed)

				health += gs("health_regen") * delta
				health = min(gs("health_max"), health)
				if prior_health != health:
								emit_signal("health_changed")
								metrics.recovered_health += health - prior_health
				prior_health = health

				if track_dps:
								last_damage_time += delta
								time_since_first_damage += delta
								if time_since_first_damage > 30.0 or last_damage_time > 2.0:
												accumulated_applied_damage = 0.0
												time_since_first_damage = 0.0
												damage_text.visible = false
								elif accumulated_applied_damage > 0:
												damage_text.text = Utils.render_suffix_number(round(accumulated_applied_damage / time_since_first_damage))
												damage_text.visible = true
																


func _on_levelup():
				recompute_level_buffs()
				recompute_stats(true)
				fill_health()

func _on_passives_changed():
				recompute_passive_stats()
				recompute_stats(true)

func _on_loadout_changed():
				recompute_gene_stats()
				recompute_stats(true)

func apply_status_effect(effect: BaseEffect):
				
				if effect.is_ailment:
								if randf() <= gs("ailment_avoidance"):
												
												effect.queue_free()
												return

				

				effect.stats = self
				effect.initialize()
				if effect.unique_group == null or effect.only_apply_strongest:
								effect.connect("on_apply", self, "on_status_effect_changed", [effect])
								effect.connect("on_expire", self, "on_status_effect_changed", [effect])
								$StatusEffects.add_child(effect)
				else:
								var group = effect.unique_group
								if effect_for_group.has(group) and effect_for_group[group].get_ref():
												var existing = effect_for_group[group].get_ref()
												if existing.expired:
																effect_for_group[group] = weakref(effect)
																effect.connect("on_apply", self, "on_status_effect_changed", [effect])
																effect.connect("on_expire", self, "on_status_effect_changed", [effect])

																$StatusEffects.add_child(effect)
												else:
																if effect.damage_combine_group:
																				
																				effect.trigger()
																				if not effect.expired:
																								
																								existing.merge_damage(effect)
																								
																else:
																				
																				existing.lifetime_expired = min(existing.lifetime_expired, effect.lifetime_expired)
																				existing.buffs_and_nerfs = effect.get_buffs_and_nerfs()
																				if existing.retriggerable:
																								existing.trigger()
																effect.queue_free()
								else:
												effect_for_group[group] = weakref(effect)
												effect.connect("on_apply", self, "on_status_effect_changed", [effect])
												effect.connect("on_expire", self, "on_status_effect_changed", [effect])
												$StatusEffects.add_child(effect)

				recompute_status_effects(effect.fast_flags)

func get_status_effects():
				return cached_effects

func override_all_status_changes():
				
				return false

func on_status_effect_changed(effect):
				if not effect.is_active:
								print("Returning because not active")
								return
				if effect.recompute_stats or override_all_status_changes():
								_needs_recompute_on_status_changed = true
				else:
								_needs_status_flag_recache = true

func compute_resisted_damage(damage_bundle, attacker_stats = null):
				var damage_out = {}
				var damage_accumulated = 0.0
				var incoming_damages = damage_bundle.damage
				var incoming_penetrations = null
				if damage_bundle.has("penetrations"):
								incoming_penetrations = damage_bundle.penetrations

				
				if has_incoming_conversions:
								incoming_damages = incoming_damages.duplicate(true)
								
								if incoming_damages.has(SkillTags.Tags.PHYSICAL):
												var converted_amount = 0.0
												var lightning_amount = gs("physical_taken_as_lightning")
												if lightning_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.LIGHTNING):
																				incoming_damages[SkillTags.Tags.LIGHTNING] += incoming_damages[SkillTags.Tags.PHYSICAL] * lightning_amount
																else:
																				incoming_damages[SkillTags.Tags.LIGHTNING] = incoming_damages[SkillTags.Tags.PHYSICAL] * lightning_amount
																converted_amount += lightning_amount
												var cold_amount = gs("physical_taken_as_cold")
												if cold_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.COLD):
																				incoming_damages[SkillTags.Tags.COLD] += incoming_damages[SkillTags.Tags.PHYSICAL] * cold_amount
																else:
																				incoming_damages[SkillTags.Tags.COLD] = incoming_damages[SkillTags.Tags.PHYSICAL] * cold_amount
																converted_amount += cold_amount
												var fire_amount = gs("physical_taken_as_fire")
												if fire_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.FIRE):
																				incoming_damages[SkillTags.Tags.FIRE] += incoming_damages[SkillTags.Tags.PHYSICAL] * fire_amount
																else:
																				incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.PHYSICAL] * fire_amount
																converted_amount += fire_amount
												var toxic_amount = gs("physical_taken_as_toxic")
												if toxic_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.TOXIC):
																				incoming_damages[SkillTags.Tags.TOXIC] += incoming_damages[SkillTags.Tags.PHYSICAL] * toxic_amount
																else:
																				incoming_damages[SkillTags.Tags.TOXIC] = incoming_damages[SkillTags.Tags.PHYSICAL] * toxic_amount
																converted_amount += toxic_amount
												converted_amount = min(1.0, converted_amount)
												if converted_amount == 1.0:
																incoming_damages.erase(SkillTags.Tags.PHYSICAL)
												else:
																incoming_damages[SkillTags.Tags.PHYSICAL] = incoming_damages[SkillTags.Tags.PHYSICAL] * (1.0 - converted_amount)

								
								if incoming_damages.has(SkillTags.Tags.LIGHTNING):
												if attacker_stats:
																if status_flags.has(Constants.StatusFlags.ELECTROCUTED):
																				var extra_lightning = attacker_stats.gs("extra_lightning_as_cold_against_electrocuted")
																				if extra_lightning > 0:
																								if incoming_damages.has(SkillTags.Tags.COLD):
																												incoming_damages[SkillTags.Tags.COLD] += incoming_damages[SkillTags.Tags.LIGHTNING] * extra_lightning
																								else:
																												incoming_damages[SkillTags.Tags.COLD] = incoming_damages[SkillTags.Tags.LIGHTNING] * extra_lightning
												var converted_amount = 0.0
												var cold_amount = gs("lightning_taken_as_cold")
												if cold_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.COLD):
																				incoming_damages[SkillTags.Tags.COLD] += incoming_damages[SkillTags.Tags.LIGHTNING] * cold_amount
																else:
																				incoming_damages[SkillTags.Tags.COLD] = incoming_damages[SkillTags.Tags.LIGHTNING] * cold_amount
																converted_amount += cold_amount
												var fire_amount = gs("lightning_taken_as_fire")
												if fire_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.FIRE):
																				incoming_damages[SkillTags.Tags.FIRE] += incoming_damages[SkillTags.Tags.LIGHTNING] * fire_amount
																else:
																				incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.LIGHTNING] * fire_amount
																converted_amount += fire_amount
												var toxic_amount = gs("lightning_taken_as_toxic")
												if toxic_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.TOXIC):
																				incoming_damages[SkillTags.Tags.TOXIC] += incoming_damages[SkillTags.Tags.LIGHTNING] * toxic_amount
																else:
																				incoming_damages[SkillTags.Tags.TOXIC] = incoming_damages[SkillTags.Tags.LIGHTNING] * toxic_amount
																converted_amount += toxic_amount
												converted_amount = min(1.0, converted_amount)
												if converted_amount == 1.0:
																incoming_damages.erase(SkillTags.Tags.LIGHTNING)
												else:
																incoming_damages[SkillTags.Tags.LIGHTNING] = incoming_damages[SkillTags.Tags.LIGHTNING] * (1.0 - converted_amount)

								
								if incoming_damages.has(SkillTags.Tags.COLD):
												if attacker_stats:
																if status_flags.has(Constants.StatusFlags.FROZEN):
																				var extra_cold = attacker_stats.gs("extra_cold_as_fire_against_frozen")
																				if extra_cold > 0:
																								if incoming_damages.has(SkillTags.Tags.FIRE):
																												incoming_damages[SkillTags.Tags.FIRE] += incoming_damages[SkillTags.Tags.COLD] * extra_cold
																								else:
																												incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.COLD] * extra_cold
																if status_flags.has(Constants.StatusFlags.CHILLED):
																				var extra_cold = attacker_stats.gs("extra_cold_as_fire_against_chilled")
																				if extra_cold > 0:
																								if incoming_damages.has(SkillTags.Tags.FIRE):
																												incoming_damages[SkillTags.Tags.FIRE] += incoming_damages[SkillTags.Tags.COLD] * extra_cold
																								else:
																												incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.COLD] * extra_cold
												var converted_amount = 0.0
												var fire_amount = gs("cold_taken_as_fire")
												if fire_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.FIRE):
																				incoming_damages[SkillTags.Tags.FIRE] += incoming_damages[SkillTags.Tags.COLD] * fire_amount
																else:
																				incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.COLD] * fire_amount
																converted_amount += fire_amount
												var toxic_amount = gs("cold_taken_as_toxic")
												if toxic_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.TOXIC):
																				incoming_damages[SkillTags.Tags.TOXIC] += incoming_damages[SkillTags.Tags.COLD] * toxic_amount
																else:
																				incoming_damages[SkillTags.Tags.TOXIC] = incoming_damages[SkillTags.Tags.COLD] * toxic_amount
																converted_amount += toxic_amount
												converted_amount = min(1.0, converted_amount)
												if converted_amount == 1.0:
																incoming_damages.erase(SkillTags.Tags.COLD)
												else:
																incoming_damages[SkillTags.Tags.COLD] = incoming_damages[SkillTags.Tags.COLD] * (1.0 - converted_amount)

								
								if incoming_damages.has(SkillTags.Tags.FIRE):
												var converted_amount = 0.0
												var toxic_amount = gs("fire_taken_as_toxic")
												if toxic_amount != 0.0:
																if incoming_damages.has(SkillTags.Tags.TOXIC):
																				incoming_damages[SkillTags.Tags.TOXIC] += incoming_damages[SkillTags.Tags.FIRE] * toxic_amount
																else:
																				incoming_damages[SkillTags.Tags.TOXIC] = incoming_damages[SkillTags.Tags.FIRE] * toxic_amount
																converted_amount += toxic_amount
												converted_amount = min(1.0, converted_amount)
												if converted_amount == 1.0:
																incoming_damages.erase(SkillTags.Tags.FIRE)
												else:
																incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.FIRE] * (1.0 - converted_amount)
				else:
								if attacker_stats:
												if incoming_damages.has(SkillTags.Tags.LIGHTNING):
																if status_flags.has(Constants.StatusFlags.ELECTROCUTED):
																				var extra_lightning = attacker_stats.gs("extra_lightning_as_cold_against_electrocuted")
																				if extra_lightning != 0:
																								if incoming_damages.has(SkillTags.Tags.COLD):
																												incoming_damages[SkillTags.Tags.COLD] += incoming_damages[SkillTags.Tags.LIGHTNING] * extra_lightning
																								else:
																												incoming_damages[SkillTags.Tags.COLD] = incoming_damages[SkillTags.Tags.LIGHTNING] * extra_lightning
												if incoming_damages.has(SkillTags.Tags.COLD):
																if status_flags.has(Constants.StatusFlags.FROZEN):
																				var extra_cold = attacker_stats.gs("extra_cold_as_fire_against_frozen")
																				if extra_cold != 0:
																								if incoming_damages.has(SkillTags.Tags.FIRE):
																												incoming_damages[SkillTags.Tags.FIRE] += incoming_damages[SkillTags.Tags.COLD] * extra_cold
																								else:
																												incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.COLD] * extra_cold
																if status_flags.has(Constants.StatusFlags.CHILLED):
																				var extra_cold = attacker_stats.gs("extra_cold_as_fire_against_chilled")
																				if extra_cold != 0:
																								if incoming_damages.has(SkillTags.Tags.FIRE):
																												incoming_damages[SkillTags.Tags.FIRE] += incoming_damages[SkillTags.Tags.COLD] * extra_cold
																								else:
																												incoming_damages[SkillTags.Tags.FIRE] = incoming_damages[SkillTags.Tags.COLD] * extra_cold

				if incoming_damages.has(SkillTags.Tags.PHYSICAL):
								var damage = incoming_damages[SkillTags.Tags.PHYSICAL]
								
								var effective_resistance = cap_resistance(gs("physical_resistance"), gs("maximum_physical_resistance"))

								if attacker_stats and attacker_stats.keystones.has("TREE_MAGMATIC_BLOOD") and status_flags.has(Constants.StatusFlags.BLEEDING):
												effective_resistance = - 0.25

								if incoming_penetrations:
												if incoming_penetrations.has(SkillTags.Tags.PHYSICAL):
																effective_resistance -= incoming_penetrations[SkillTags.Tags.PHYSICAL]
								var unresisted_damage = damage * (1.0 - effective_resistance)
								damage_out[SkillTags.Tags.PHYSICAL] = unresisted_damage

				if incoming_damages.has(SkillTags.Tags.LIGHTNING):
								var damage = incoming_damages[SkillTags.Tags.LIGHTNING]
								
								var effective_resistance = cap_resistance(gs("lightning_resistance"), gs("maximum_lightning_resistance"))
								if status_flags.has(Constants.StatusFlags.BONDED_ELECTRONS):
												if unique_status_flags.has(Constants.StatusFlags.BONDED_ELECTRONS):
																var effect = unique_status_flags[Constants.StatusFlags.BONDED_ELECTRONS]
																if effect:
																				effective_resistance = effect.get_lightning_override()
												else:
																print("ERROR: Bonded electrons missing unique group")

								if attacker_stats:
												if attacker_stats.keystones.has("UNIQUE_MERCURIAL_VENOM"):
																effective_resistance -= 0.01 * affecting_ailment_count
								if incoming_penetrations:
												if incoming_penetrations.has(SkillTags.Tags.LIGHTNING):
																effective_resistance -= incoming_penetrations[SkillTags.Tags.LIGHTNING]

								var unresisted_damage = damage * (1.0 - effective_resistance)
								damage_out[SkillTags.Tags.LIGHTNING] = unresisted_damage

				if incoming_damages.has(SkillTags.Tags.COLD):
								var damage = incoming_damages[SkillTags.Tags.COLD]
								
								var effective_resistance = cap_resistance(gs("cold_resistance"), gs("maximum_cold_resistance"))
								if attacker_stats and attacker_stats.keystones.has("UNIQUE_FROZEN_SLUDGE") and status_flags.has(Constants.StatusFlags.POISONED):
												effective_resistance = - 1.0
								if incoming_penetrations:
												if incoming_penetrations.has(SkillTags.Tags.COLD):
																effective_resistance -= incoming_penetrations[SkillTags.Tags.COLD]
								var unresisted_damage = damage * (1.0 - effective_resistance)
								damage_out[SkillTags.Tags.COLD] = unresisted_damage

				if incoming_damages.has(SkillTags.Tags.FIRE):
								var damage = incoming_damages[SkillTags.Tags.FIRE]
								
								var effective_resistance = cap_resistance(gs("fire_resistance"), gs("maximum_fire_resistance"))

								
								if attacker_stats and attacker_stats.keystones.has("TREE_MAGMATIC_BLOOD") and status_flags.has(Constants.StatusFlags.BLEEDING):
												effective_resistance = - 0.25

								if incoming_penetrations:
												if incoming_penetrations.has(SkillTags.Tags.FIRE):
																effective_resistance -= incoming_penetrations[SkillTags.Tags.FIRE]

								var unresisted_damage = damage * (1.0 - effective_resistance)
								damage_out[SkillTags.Tags.FIRE] = unresisted_damage

				if incoming_damages.has(SkillTags.Tags.TOXIC):
								var damage = incoming_damages[SkillTags.Tags.TOXIC]
								
								var effective_resistance = cap_resistance(gs("toxic_resistance"), gs("maximum_toxic_resistance"))
								if incoming_penetrations:
												if incoming_penetrations.has(SkillTags.Tags.TOXIC):
																effective_resistance -= incoming_penetrations[SkillTags.Tags.TOXIC]
								var unresisted_damage = damage * (1.0 - effective_resistance)
								damage_out[SkillTags.Tags.TOXIC] = unresisted_damage

				return damage_out

func roll_crit(damage_bundle) -> bool:
				var chance = damage_bundle.crit.chance
				var multi = 1.0 + (damage_bundle.crit.multi - 1.0) * max(0.0, (1.0 - cap_resistance(gs("crit_resistance"), 1.0)))
				if randf() <= chance:
								for tag in damage_bundle.damage:
												damage_bundle.damage[tag] *= multi
								return true

				return false

func apply_damage(damage_bundle, color = Color.white, attacker_stats = null, show_damage = false, is_dot_damage = false, skill_parent = null, can_block = true):
				
				if health <= 0:
								return {
												"did_kill": false, 
												"damage": 0
								}

				if is_dead:
								return {
												"did_kill": false, 
												"damage": 0
								}

				if not damage_bundle.has("damage"):
								return {
												"did_kill": false, 
												"damage": 0
								}

				if can_block:
								if not is_dot_damage and randf() <= cap_block(gs("block_chance")):
												$FloatingDamageManager.show_value("Block", color)
												on_block()
												return {
																"did_kill": false, 
																"damage": 0
												}

				if not is_dot_damage and randf() <= effective_evasion:
								$FloatingDamageManager.show_value("Evade", color)
								return {
												"did_kill": false, 
												"damage": 0
								}

				var damage_multiplier = 1.0
				var did_crit = false
				

				if health <= 0:
								return {
												"did_kill": false, 
												"damage": 0
								}

								
				if status_flags.has(Constants.StatusFlags.PHANTOM_SHIELD) and not is_dot_damage:
								if status_flags[Constants.StatusFlags.PHANTOM_SHIELD] > 0:

												var did_consume_shield = false

												
												for status_effect in get_status_effects():
																var effect = status_effect.get_ref()
																if effect:
																				if effect.get_status_flags().has(Constants.StatusFlags.PHANTOM_SHIELD):
																								if effect.consume():
																												effect.remove_effect()
																												did_consume_shield = true
																												
																												break

												if did_consume_shield:
																$FloatingDamageManager.show_value("Shielded", Color.purple)
																emit_signal("shielded")

																return {
																				"did_kill": false, 
																				"damage": 0
																}

				var did_duplicate = false
				if damage_bundle.has("crit") and not is_dot_damage:
								damage_bundle = damage_bundle.duplicate(true)
								did_crit = roll_crit(damage_bundle)
								did_duplicate = true

				if attacker_stats and attacker_stats.keystones.has("TREE_PARANOIA"):
								if damage_bundle.damage.has(SkillTags.Tags.TOXIC):
												if not did_duplicate:
																damage_bundle = damage_bundle.duplicate(true)
																did_duplicate = true
												damage_bundle.damage[SkillTags.Tags.TOXIC] *= 1.2

				if attacker_stats != null:
								var effective_radius = (25 + gs("radius")) * sqrt(attacker_stats.gs("area_of_effect"))

								if attacker_stats.keystones.has("TREE_TEMPERATURE_DELTAS") and status_flags.has(Constants.StatusFlags.CHILLED):
												
												damage_multiplier *= 1.15

								if attacker_stats.keystones.has("TREE_CHARGED_FIELD") and get_parent().global_position.distance_to(attacker_stats.get_parent().global_position) < effective_radius * 2.0:
												damage_multiplier *= 1.3

								if attacker_stats.status_flags.has(Constants.StatusFlags.CURSED) and keystones.has("TREE_STIFLED_CURSING"):
												damage_multiplier *= 0.8

								if attacker_stats.keystones.has("TREE_IMPENDING_DEATH") and status_flags.has(Constants.StatusFlags.CURSED):
												var curses_on_enemy = status_flags[Constants.StatusFlags.CURSED]
												damage_multiplier *= 1.0 + 0.1 * curses_on_enemy

								
								if status_flags.has(Constants.StatusFlags.VULNERABLE):
												if attacker_stats.keystones.has("TREE_PRECISION_STRIKES"):
																damage_multiplier *= 1.25

								
								if status_flags.has(Constants.StatusFlags.TRANSFUSION) and is_dot_damage:
												damage_multiplier *= 1.5

				
				if not is_dot_damage:
								damage_multiplier *= effective_mitigation

				
				damage_multiplier *= gs("incoming_damage")

				
				if keystones.has("TREE_TOXICOLOGIST") and is_dot_damage:
								damage_multiplier *= 0.65

				if keystones.has("TREE_BRICK") and not is_dot_damage:
								damage_multiplier *= 0.85

				if keystones.has("TREE_DEFLECTING_ARMOR") and randf() < 0.2 and not is_dot_damage:
								damage_multiplier = 0
								$FloatingDamageManager.show_value("Deflect", color)

				if not is_dot_damage and keystones.has("TREE_CROCODILE_SKIN") and not status_flags.has(Constants.StatusFlags.RECENTLY_HIT):
								damage_multiplier *= 0.1

				
				if status_flags.has(Constants.StatusFlags.DREAD):
								if status_flags.has(Constants.StatusFlags.REGULAR_ELEMENTAL_AILMENT):
												var count = status_flags[Constants.StatusFlags.REGULAR_ELEMENTAL_AILMENT]
												if count > 0:
																damage_multiplier *= 1.0 + 0.25 * count

				
				damage_multiplier = damage_multiplier * 0.9 + randf() * damage_multiplier * 0.2

				var effective_damage = compute_resisted_damage(damage_bundle, attacker_stats)

				var combined_effective_damage = 0
				for type in effective_damage:
								effective_damage[type] = max(0, effective_damage[type] * damage_multiplier)
								combined_effective_damage += effective_damage[type]

				if attacker_stats and attacker_stats.keystones.has("TREE_POTENTIAL_ENERGY") and is_dot_damage:
								accumulated_capacity_damage += combined_effective_damage
								return {
												"did_kill": false, 
												"damage": 0
								}
				else:
								reduce_health(combined_effective_damage)

				if is_dot_damage:
								accumulated_dot_damage += combined_effective_damage
				else:
								if keystones.has("TREE_QUICK_GETAWAY"):
												var buff = toxic_runner_effect.instance()
												apply_status_effect(buff)

				accumulated_applied_damage += combined_effective_damage
				last_damage_time = 0

				var did_kill = false

				
				if not is_dot_damage and damage_multiplier != 0:
								on_take_damage(attacker_stats, damage_bundle, effective_damage, is_dot_damage, did_crit, skill_parent)

				if health <= 0:
								handle_status_change(false)
								call_deferred("emit_signal", "died")
								health = 0
								is_dead = true
								did_kill = true

				var effective_radius = 60
				if attacker_stats:
								effective_radius = (60 + attacker_stats.gs("radius")) * sqrt(attacker_stats.gs("area_of_effect"))

				if did_kill:
								
								if status_flags.has(Constants.StatusFlags.INFECTED):
												proliferate_strongest_infection()

								if attacker_stats and status_flags.has(Constants.StatusFlags.BURNING) and attacker_stats.keystones.has("UNIQUE_SPREADING_FLAMES"):
												proliferate_burn()

								if accumulated_capacity_damage > 0.0:
												var explosion = sanguine_explosion.instance()
												explosion.global_position = get_parent().global_position
												explosion.radius = effective_radius
												explosion.damage = {"damage": {SkillTags.Tags.PHYSICAL: accumulated_capacity_damage * 0.15}}
												explosion.stats = self
												explosion.attacker_stats = attacker_stats
												level_scene.add_child(explosion)

				if attacker_stats != null and did_kill:
								
								attacker_stats.on_kill(self, is_dot_damage)

								if attacker_stats.keystones.has("TREE_HYSTERIA") and randf() < 0.3:
												var splash_applier_instance = area_damage_applier.instance()
												splash_applier_instance.global_position = global_position
												splash_applier_instance.target_group = allies_group
												splash_applier_instance.damage_bundle = {
																"damage": {
																				SkillTags.Tags.TOXIC: gs("health_max") * 0.4
																}
												}
												splash_applier_instance.radius = effective_radius
												GameState.get_global("ground").call_deferred("add_child", splash_applier_instance)

												var explosion_instance = hysteria_explosion.instance()
												explosion_instance.radius = effective_radius
												explosion_instance.global_position = global_position
												GameState.get_global("ground").call_deferred("add_child", explosion_instance)

								if attacker_stats.keystones.has("TREE_SANGUINE_DECAY") and (status_flags.has(Constants.StatusFlags.BLEEDING) or status_flags.has(Constants.StatusFlags.RUPTURED)):
												
												var remaining_bleed_damage = collect_and_remove_bleeds()
												for k in remaining_bleed_damage.damage:
																remaining_bleed_damage.damage[k] *= 0.5
												
												var explosion = sanguine_explosion.instance()
												explosion.global_position = get_parent().global_position
												explosion.radius = effective_radius
												explosion.damage = remaining_bleed_damage
												explosion.stats = self
												explosion.attacker_stats = attacker_stats
												ground_layer.add_child(explosion)

								if attacker_stats.keystones.has("TREE_INFECTIOUS_MALIGNANCY") and status_flags.has(Constants.StatusFlags.CURSED):
												var allies = get_visible_allies(effective_radius * 1.5)
												if len(allies) > 0:
																var effects_to_transfer = get_status_effects()
																for status_effect in effects_to_transfer:
																				var effect = status_effect.get_ref()
																				if effect:
																								var flags = effect.get_status_flags()
																								
																								if flags.has(Constants.StatusFlags.CURSED):
																												
																												var enemy = allies[randi() % len(allies)]
																												var c = effect.duplicate()
																												c.applier_stats_weakref = weakref(effect.applier_stats_weakref.get_ref())
																												c.lifetime = effect.lifetime
																												c.lifetime_expired = effect.lifetime_expired
																												c.curse_effect = effect.curse_effect
																												enemy.stats.apply_status_effect(c)

				return {
								"did_kill": did_kill, 
								"damage": combined_effective_damage
				}

func reduce_health(amount):
				health -= amount
				health = max(0, health)

func on_kill(target, is_dot_damage = false):
				if keystones.has("TREE_RAGING_MOMENTUM"):
								var buff = kill_momentum_effect.instance()
								apply_status_effect(buff)
				if keystones.has("TREE_GROWING_PAIN"):
								var buff = growing_pain_effect.instance()
								apply_status_effect(buff)
				if keystones.has("TREE_LEECHER"):
								recover_health(gs("health_max") * 0.01)
				if keystones.has("TREE_SIPHONER") and is_dot_damage:
								recover_health(gs("health_max") * 0.02)

				if get_parent().is_in_group("player"):
								var other_skills = get_parent().gear.get_children()
								for skill in other_skills:
												if skill == self:
																continue
												if skill.keystones.has("SUPPORT_CAST_ON_KILL") and randf() <= 0.3 and skill.is_triggered:
																skill._cast()

				if randf() < gs("toughness_boon_on_kill_chance"):
								add_toughness_boon(1)
				if randf() < gs("precision_boon_on_kill_chance"):
								add_precision_boon(1)
				if randf() < gs("swiftness_boon_on_kill_chance"):
								add_swiftness_boon(1)

func trigger_on_crit():
				if is_player and has_triggered_skill:
								for skill in cached_gear:
												if is_instance_valid(skill):
																if not skill.is_triggered:
																				continue
																if skill.keystones.has("SUPPORT_CAST_ON_CRIT"):
																				skill._cast()
												else:
																print("invalid skill")

func trigger_on_hit():
				if is_player and has_triggered_skill:
								for skill in cached_gear:
												if is_instance_valid(skill):
																if not skill.is_triggered:
																				continue
																if skill.keystones.has("SUPPORT_VOLATILITY"):
																				
																				if get_boon_count() > 0:
																								skill._cast()
												else:
																print("invalid skill, waiting on gear refresh")

func on_block():
				if gs("life_gain_on_block") != 0:
								recover_health(gs("life_gain_on_block"))
				if is_player:
								Globals.play_sound_effect(block_sound)

func remove_all_boons():
				var removed_precision_boons = 0
				var removed_swiftness_boons = 0
				var removed_toughness_boons = 0
				for effect in $StatusEffects.get_children():
								if effect.is_active and effect.get_status_flags().has(Constants.StatusFlags.BOON):
												if effect.get_status_flags().has(Constants.StatusFlags.PRECISION_BOON):
																removed_precision_boons += 1
												if effect.get_status_flags().has(Constants.StatusFlags.SWIFTNESS_BOON):
																removed_swiftness_boons += 1
												if effect.get_status_flags().has(Constants.StatusFlags.TOUGHNESS_BOON):
																removed_toughness_boons += 1
												effect.remove_effect()
				if keystones.has("UNIQUE_BALANCE_OF_POWER"):
								if removed_precision_boons > 0:
												print("Adding ", removed_precision_boons, " Swiftness")
												add_swiftness_boon(removed_precision_boons)
				perform_recompute_status_effects()

func get_boon_count():
				return get_precision_boons() + get_toughness_boons() + get_swiftness_boons()

func get_precision_boons():
				return status_flags.get(Constants.StatusFlags.PRECISION_BOON, 0)

func get_toughness_boons():
				return status_flags.get(Constants.StatusFlags.TOUGHNESS_BOON, 0)

func get_swiftness_boons():
				return status_flags.get(Constants.StatusFlags.SWIFTNESS_BOON, 0)

func remove_precision_boon(boons):
				pass

func remove_toughness_boon(boons):
				pass

func remove_swiftness_boon(boons):
				pass

func add_precision_boon(boons):
				if boons > 0:
								if status_flags.get(Constants.StatusFlags.PRECISION_BOON, 0) < gs("precision_boon"):
												
												for i in range(boons):
																var buff = precision_boon_effect.instance()
																apply_status_effect(buff)
								refresh_precision_buffs()

func refresh_precision_buffs():
				for child in status_effects.get_children():
								
								if child.expired:
												continue
								if not child.has_applied:
												continue
								if child.is_queued_for_deletion():
												continue
								if not child.is_active:
												continue

								if child.get_status_flags().has(Constants.StatusFlags.PRECISION_BOON):
												child.lifetime_expired = 0.0

func add_swiftness_boon(boons):
				if boons > 0:
								if status_flags.get(Constants.StatusFlags.SWIFTNESS_BOON, 0) < gs("swiftness_boon"):
												
												for i in range(boons):
																var buff = swiftness_boon_effect.instance()
																apply_status_effect(buff)
								refresh_swiftness_buffs()

func refresh_swiftness_buffs():
				for child in status_effects.get_children():
								
								if child.expired:
												continue
								if not child.has_applied:
												continue
								if child.is_queued_for_deletion():
												continue
								if not child.is_active:
												continue

								if child.get_status_flags().has(Constants.StatusFlags.SWIFTNESS_BOON):
												child.lifetime_expired = 0.0

func add_toughness_boon(boons):
				if boons > 0:
								if status_flags.get(Constants.StatusFlags.TOUGHNESS_BOON, 0) < gs("toughness_boon"):
												
												for i in range(boons):
																var buff = toughness_boon_effect.instance()
																apply_status_effect(buff)
								refresh_toughness_buffs()

func refresh_toughness_buffs():
				for child in status_effects.get_children():
								
								if child.expired:
												continue
								if not child.has_applied:
												continue
								if child.is_queued_for_deletion():
												continue
								if not child.is_active:
												continue

								if child.get_status_flags().has(Constants.StatusFlags.TOUGHNESS_BOON):
												child.lifetime_expired = 0.0

func on_take_damage(attacker_stats, unmitigated_damage_bundle, effective_damage_bundle, is_dot, did_crit = false, skill_parent = null):
				
				if is_dot:
								return
				if is_player:
								emit_signal("damage_taken", effective_damage_bundle, attacker_stats, did_crit)

				if randf() <= gs("toughness_boon_on_get_hit_chance"):
								
								add_toughness_boon(1)

				var buff
				if is_player:
								buff = recently_hit_effect.instance()
								apply_status_effect(buff)

				if keystones.has("TREE_ADRENALINE"):
								buff = adrenaline_effect.instance()
								apply_status_effect(buff)
				if keystones.has("TREE_SPIKE_ARMOR"):
								buff = spike_armor_effect.instance()
								apply_status_effect(buff)
				if keystones.has("TREE_VAMPIRIC_SKIN"):
								buff = vampiric_skin_effect.instance()
								apply_status_effect(buff)
				if keystones.has("TREE_ENDURANCE"):
								buff = endurance_effect.instance()
								apply_status_effect(buff)
				if keystones.has("TREE_HARDENED_FLESH"):
								buff = hardened_flesh_effect.instance()
								apply_status_effect(buff)

				if attacker_stats and attacker_stats.keystones.has("UNIQUE_ECHOING_FURY"):
								if randf() < 0.1 and not status_flags.has(Constants.StatusFlags.ECHOING):
												buff = echoing_effect.instance()
												apply_status_effect(buff)
												
												var splash_applier_instance = area_damage_applier.instance()
												splash_applier_instance.global_position = global_position
												splash_applier_instance.target_group = allies_group
												splash_applier_instance.damage_bundle = unmitigated_damage_bundle.duplicate(true)
												for d_type in splash_applier_instance.damage_bundle.damage:
																splash_applier_instance.damage_bundle.damage[d_type] *= 1.4
												splash_applier_instance.radius = 45
												splash_applier_instance.skill_parent = skill_parent
												GameState.get_global("ground").call_deferred("add_child", splash_applier_instance)

												var expl = fury_explosion.instance()
												expl.radius = 45
												expl.global_position = global_position
												GameState.get_global("ground").call_deferred("add_child", expl)

				if skill_parent and skill_parent.keystones.has("SUPPORT_STATIC_ELECTRICITY") and status_flags.has(Constants.StatusFlags.JOLTED):
								if randf() < 0.5 and status_flag_amounts.has(Constants.StatusFlags.JOLTED):
												var jolt_strength = 2.0 * status_flag_amounts[Constants.StatusFlags.JOLTED]
												consume_all_effects(Constants.StatusFlags.JOLTED)
												
												var damage_to_apply = unmitigated_damage_bundle.duplicate(true)
												damage_to_apply.erase("ailment")
												for d_type in damage_to_apply.damage:
																damage_to_apply.damage[d_type] *= jolt_strength
												var lightning_targets = get_visible_allies(50 * sqrt(skill_parent.get_aoe()), true).slice(0, 3)
												for target in lightning_targets:
																var inst = arc_spark.instance()
																inst.global_position = target.global_position
																GameState.get_global("ground").call_deferred("add_child", inst)
																
																var info = target.stats.apply_damage(damage_to_apply, Color.white, attacker_stats, true, false, skill_parent)
																skill_parent.track_hit(info)


				if unmitigated_damage_bundle.has("ailment"):
								var should_proliferate = false
								var prolif_targets = []
								if skill_parent:
												if skill_parent.keystones.has("SUPPORT_PROLIFERATE"):
																should_proliferate = true
																prolif_targets = get_visible_allies(50 * sqrt(skill_parent.get_aoe())).slice(0, 10)

								var dmg = effective_damage_bundle
								var chances = unmitigated_damage_bundle.ailment.chance
								var effects = unmitigated_damage_bundle.ailment.effect
								var amplify = unmitigated_damage_bundle.ailment.amplify
								var penetrations = {}
								if unmitigated_damage_bundle.has("penetrations"):
												penetrations = unmitigated_damage_bundle.penetrations

								var can_apply_poison = dmg.has(SkillTags.Tags.TOXIC)
								var poison_damage = 0
								if dmg.has(SkillTags.Tags.TOXIC):
												poison_damage += dmg[SkillTags.Tags.TOXIC]

								if attacker_stats and attacker_stats.keystones.has("TREE_CHAOTIC_RESONANCE"):
												can_apply_poison = can_apply_poison or dmg.has(SkillTags.Tags.LIGHTNING)
												if dmg.has(SkillTags.Tags.LIGHTNING):
																poison_damage += dmg[SkillTags.Tags.LIGHTNING]
								if attacker_stats and attacker_stats.keystones.has("TREE_COATED_BLADES"):
												can_apply_poison = can_apply_poison or dmg.has(SkillTags.Tags.PHYSICAL)
												if dmg.has(SkillTags.Tags.PHYSICAL):
																poison_damage += dmg[SkillTags.Tags.PHYSICAL]

								if dmg.has(SkillTags.Tags.PHYSICAL) and randf() <= chances[SkillTags.Tags.PHYSICAL]:

												
												if randf() <= amplify:
																buff = rupture_effect.instance()
																buff.skill_parent_weakref = weakref(skill_parent)
																buff.applier_stats_weakref = weakref(attacker_stats)
																buff.hit_damage = dmg[SkillTags.Tags.PHYSICAL]
																if penetrations.has(SkillTags.Tags.PHYSICAL):
																				buff.penetration = penetrations[SkillTags.Tags.PHYSICAL]
																buff.ailment_effects = effects
																apply_status_effect(buff)
												buff = bleed_effect.instance()
												buff.skill_parent_weakref = weakref(skill_parent)
												buff.applier_stats_weakref = weakref(attacker_stats)
												buff.hit_damage = dmg[SkillTags.Tags.PHYSICAL]
												if penetrations.has(SkillTags.Tags.PHYSICAL):
																buff.penetration = penetrations[SkillTags.Tags.PHYSICAL]
												buff.ailment_effects = effects
												apply_status_effect(buff)

								if dmg.has(SkillTags.Tags.LIGHTNING) and randf() <= chances[SkillTags.Tags.LIGHTNING]:
												
												if randf() <= amplify:
																buff = electrocute_effect.instance()
																buff.skill_parent_weakref = weakref(skill_parent)
																buff.applier_stats_weakref = weakref(attacker_stats)
																buff.damage_percentage = dmg[SkillTags.Tags.LIGHTNING] / gs("health_max")
																buff.ailment_effects = effects
																apply_status_effect(buff)
																if should_proliferate:
																				for t in prolif_targets:
																								buff = electrocute_effect.instance()
																								buff.skill_parent_weakref = weakref(skill_parent)
																								buff.applier_stats_weakref = weakref(attacker_stats)
																								buff.damage_percentage = dmg[SkillTags.Tags.LIGHTNING] / gs("health_max")
																								buff.ailment_effects = effects
																								t.stats.apply_status_effect(buff)
												buff = jolt_effect.instance()
												buff.skill_parent_weakref = weakref(skill_parent)
												buff.applier_stats_weakref = weakref(attacker_stats)
												buff.damage_percentage = dmg[SkillTags.Tags.LIGHTNING] / gs("health_max")
												buff.ailment_effects = effects
												apply_status_effect(buff)
												if should_proliferate:
																for t in prolif_targets:
																				buff = jolt_effect.instance()
																				buff.skill_parent_weakref = weakref(skill_parent)
																				buff.applier_stats_weakref = weakref(attacker_stats)
																				buff.damage_percentage = dmg[SkillTags.Tags.LIGHTNING] / gs("health_max")
																				buff.ailment_effects = effects
																				t.stats.apply_status_effect(buff)

								if dmg.has(SkillTags.Tags.COLD) and randf() <= chances[SkillTags.Tags.COLD]:
												
												if randf() <= amplify and not is_boss:
																buff = frozen_effect.instance()
																buff.skill_parent_weakref = weakref(skill_parent)
																buff.applier_stats_weakref = weakref(attacker_stats)
																buff.damage_percentage = dmg[SkillTags.Tags.COLD] / gs("health_max")
																buff.ailment_effects = effects
																apply_status_effect(buff)
																if should_proliferate:
																				for t in prolif_targets:
																								buff = frozen_effect.instance()
																								buff.skill_parent_weakref = weakref(skill_parent)
																								buff.applier_stats_weakref = weakref(attacker_stats)
																								buff.damage_percentage = dmg[SkillTags.Tags.COLD] / gs("health_max")
																								buff.ailment_effects = effects
																								t.stats.apply_status_effect(buff)
												else:
																buff = chilled_effect.instance()
																buff.skill_parent_weakref = weakref(skill_parent)
																buff.applier_stats_weakref = weakref(attacker_stats)
																buff.damage_percentage = dmg[SkillTags.Tags.COLD] / gs("health_max")
																buff.ailment_effects = effects
																apply_status_effect(buff)
																if should_proliferate:
																				for t in prolif_targets:
																								buff = chilled_effect.instance()
																								buff.skill_parent_weakref = weakref(skill_parent)
																								buff.applier_stats_weakref = weakref(attacker_stats)
																								buff.damage_percentage = dmg[SkillTags.Tags.COLD] / gs("health_max")
																								buff.ailment_effects = effects
																								t.stats.apply_status_effect(buff)

								if dmg.has(SkillTags.Tags.FIRE) and randf() <= chances[SkillTags.Tags.FIRE]:
												
												if randf() <= amplify:
																buff = charred_effect.instance()
																buff.applier_stats_weakref = weakref(attacker_stats)
																buff.skill_parent_weakref = weakref(skill_parent)
																buff.damage_percentage = dmg[SkillTags.Tags.FIRE] / gs("health_max")
																buff.ailment_effects = effects
																apply_status_effect(buff)
																if should_proliferate:
																				for t in prolif_targets:
																								buff = charred_effect.instance()
																								buff.applier_stats_weakref = weakref(attacker_stats)
																								buff.skill_parent_weakref = weakref(skill_parent)
																								buff.damage_percentage = dmg[SkillTags.Tags.FIRE] / gs("health_max")
																								buff.ailment_effects = effects
																								t.stats.apply_status_effect(buff)
												buff = burn_effect.instance()
												buff.skill_parent_weakref = weakref(skill_parent)
												buff.applier_stats_weakref = weakref(attacker_stats)
												buff.hit_damage = dmg[SkillTags.Tags.FIRE]
												if penetrations.has(SkillTags.Tags.FIRE):
																buff.penetration = penetrations[SkillTags.Tags.FIRE]
												buff.ailment_effects = effects
												apply_status_effect(buff)
												if should_proliferate:
																for t in prolif_targets:
																				buff = burn_effect.instance()
																				buff.skill_parent_weakref = weakref(skill_parent)
																				buff.applier_stats_weakref = weakref(attacker_stats)
																				buff.hit_damage = dmg[SkillTags.Tags.FIRE]
																				if penetrations.has(SkillTags.Tags.FIRE):
																								buff.penetration = penetrations[SkillTags.Tags.FIRE]
																				buff.ailment_effects = effects
																				t.stats.apply_status_effect(buff)

								if can_apply_poison and randf() <= chances[SkillTags.Tags.TOXIC]:
												if randf() <= amplify:
																buff = infection_effect.instance()
																buff.skill_parent_weakref = weakref(skill_parent)
																buff.applier_stats_weakref = weakref(attacker_stats)
																buff.hit_damage = poison_damage
																if penetrations.has(SkillTags.Tags.TOXIC):
																				buff.penetration = penetrations[SkillTags.Tags.TOXIC]
																buff.ailment_effects = effects
																apply_status_effect(buff)
												buff = poison_effect.instance()
												buff.skill_parent_weakref = weakref(skill_parent)
												buff.applier_stats_weakref = weakref(attacker_stats)
												buff.hit_damage = poison_damage
												if penetrations.has(SkillTags.Tags.TOXIC):
																buff.penetration = penetrations[SkillTags.Tags.TOXIC]
												buff.ailment_effects = effects
												apply_status_effect(buff)

				if unmitigated_damage_bundle.has("exposure"):
								if randf() < unmitigated_damage_bundle.exposure.chance:
												buff = exposed_status_effect.instance()
												buff.exposure_effect = unmitigated_damage_bundle.exposure.effect
												buff.applier_stats_weakref = weakref(attacker_stats)
												buff.skill_parent_weakref = weakref(skill_parent)
												apply_status_effect(buff)

				if unmitigated_damage_bundle.has("vulnerable"):
								if randf() < unmitigated_damage_bundle.vulnerable.chance:
												buff = vulnerable_status_effect.instance()
												buff.vulnerable_effect = unmitigated_damage_bundle.vulnerable.effect
												buff.applier_stats_weakref = weakref(attacker_stats)
												buff.skill_parent_weakref = weakref(skill_parent)
												apply_status_effect(buff)

				if skill_parent:
								if skill_parent.keystones.has("SUPPORT_HAMSTRING"):
												var hamstring = hamstring_effect.instance()
												apply_status_effect(hamstring)

								skill_parent.on_hit()
								if did_crit:
												skill_parent.on_crit()

				if attacker_stats and keystones.has("TREE_TRANSFUSION"):
								
								var transfusion = transfusion_effect.instance()
								attacker_stats.apply_status_effect(transfusion)

				if keystones.has("TREE_BLOOD_ARMOR"):
								
								if status_flags.has(Constants.StatusFlags.BLOOD_BOIL) and status_flags[Constants.StatusFlags.BLOOD_BOIL] >= 4:
												var parent_gear = get_parent().get_node("Gear")
												var skill = parent_gear.get_node("BloodArmorExplosion")
												if skill:
																skill.cast()
												consume_all_effects(Constants.StatusFlags.BLOOD_BOIL)
								else:
												var boil = blood_boil_effect.instance()
												apply_status_effect(boil)

func add_kills(amount, elite = false, boss = false):
				if is_player:
								Globals.stage_kills += 1
				metrics.kills += amount
				if elite:
								print("Elite killed")
								metrics.elite_kills += amount
				if boss:
								print("Boss killed")
								metrics.boss_kills += amount
				emit_signal("kill_change")

func add_orb(orb_type, amount = 1):
				match orb_type:
								Constants.OrbType.BLUE:
												add_blue(amount)
								Constants.OrbType.GREEN:
												add_green(amount)
								Constants.OrbType.RED:
												add_red(amount)
								Constants.OrbType.GOLD:
												add_gold(amount)
								Constants.OrbType.CORRUPTION:
												add_corruption(amount)

func add_blue(amount):
				metrics.orbs.blue += amount
				emit_signal("orb_pickup", Constants.OrbType.BLUE, amount)

func add_red(amount):
				metrics.orbs.red += amount
				emit_signal("orb_pickup", Constants.OrbType.RED, amount)

func add_green(amount):
				metrics.orbs.green += amount
				emit_signal("orb_pickup", Constants.OrbType.GREEN, amount)

func add_gold(amount):
				metrics.orbs.gold += amount
				emit_signal("orb_pickup", Constants.OrbType.GOLD, amount)

func add_corruption(amount):
				metrics.orbs.corruption += amount
				emit_signal("orb_pickup", Constants.OrbType.CORRUPTION, amount)

func add_xp(amount):
				if is_player:
								GameState.add_account_xp(Globals.get_zone_scaled_xp() * amount)

func recompute_level_buffs():
				cached_level_buffs = {}
				if is_player:
								cached_level_buffs = {
												"stats": {
																"health_max": {
																				Constants.ScalingType.FLAT: 10 * (GameState.get_active_stats().account_level - 1)
																}
												}
								}

func recompute_passive_stats():
				cached_passive_buffs = GameState.collect_passive_tree_buffs()

func recompute_gene_stats():
				cached_gene_buffs = GameState.collect_gene_loadout_buffs()

func initialize_override_stats():
				
				for stat in StatsInfo.stat_list:
								if override_stats and override_stats.has(stat):
												if is_player:
																print("Overriding stat: ", stat, override_stats[stat])
												base_stats[stat] = override_stats[stat]
								else:
												base_stats[stat] = StatsInfo.defaults[stat]

func initialize_monster_map_mod_stats():
			if get_parent().is_in_group("enemies"):
								
								var active_mods = MapMods.get_map_mods()
								for mod in active_mods:
												var stat = mod.stat
												var amount = mod.roll
												if mod.target == MapMods.Target.MOB:
																if MapMods.ModOptions[stat].scaling_type == Constants.ScalingType.FLAT:
																				base_stats[stat] += amount
																if MapMods.ModOptions[stat].scaling_type == Constants.ScalingType.PERCENT:
																				base_stats[stat] *= (1.0 + amount)
																if MapMods.ModOptions[stat].scaling_type == Constants.ScalingType.MORE:
																				base_stats[stat] *= (1.0 + amount)

func initialize_player_map_mod_stats():
				if get_parent().is_in_group("allies"):
								
								var reduction = (floor(Globals.get_zone_level() / 2.0)) / 100.0
								base_stats["physical_resistance"] -= reduction
								base_stats["lightning_resistance"] -= reduction
								base_stats["cold_resistance"] -= reduction
								base_stats["fire_resistance"] -= reduction
								base_stats["toxic_resistance"] -= reduction

								
								var active_mods = MapMods.get_map_mods()
								for mod in active_mods:
												var stat = mod.stat
												var amount = mod.roll
												if mod.target == MapMods.Target.PLAYER:
																if MapMods.ModOptions[stat].scaling_type == Constants.ScalingType.FLAT:
																				base_stats[stat] += amount
																if MapMods.ModOptions[stat].scaling_type == Constants.ScalingType.PERCENT:
																				base_stats[stat] *= (1.0 + amount)
																if MapMods.ModOptions[stat].scaling_type == Constants.ScalingType.MORE:
																				base_stats[stat] *= (1.0 + amount)

								

func reset_stats():
				conditional_stats = {}
				
				for stat in StatsInfo.stat_list:
								
								added_stats[stat] = 0.0
								inc_stats[stat] = 0.0
								more_stats[stat] = 1.0

				if use_conditional_stats:
								for tag in SkillTags.Tags.values():
												conditional_stats[tag] = {
																"added": {}, 
																"inc": {}, 
																"more": {}
												}
												for stat in StatsInfo.stat_list:
																conditional_stats[tag].added[stat] = 0.0
																conditional_stats[tag].inc[stat] = 0.0
																conditional_stats[tag].more[stat] = 1.0

				
				keystones = {}
				status_flags = {}
				status_flag_amounts = {}
				affecting_ailment_count = 0

func recompute_stats(init = false):
				
				cached_stats = {}

				
				if init:
								reset_stats()
								load_from_monster_mods()
								load_from_level_buffs()
								load_from_genes()
								load_from_passives()
								recompute_status_effects()

				
				reset_effect_stats()
				load_from_effects()
				post_load()
				combine_stats()
				cached_stats = {}
				set_incoming_conversion_flag()
				emit_signal("stats_changed")
				emit_signal("health_changed")

func set_incoming_conversion_flag():
				for stat in StatsInfo.taken_as_list:
								if gs(stat) != 0:
												has_incoming_conversions = true
												return

func combine_stats():
				
				apply_attribute_effects()
				
				apply_boon_effects()

					
				change_effect_added("health_regen", gs("health_regen_percent") * gs("health_max"))

				
				change_effect_more("health_regen", gs("health_recovery_rate"))


				
				if is_player:
								
								if keystones.has("UNIQUE_GLADIATORS_RESOLVE"):
												change_effect_added("mitigation", gs("evasion"))
												change_effect_more("evasion", 0.0)

								
								if keystones.has("UNIQUE_STRENGTH_FROM_STRENGTH"):
												
												change_effect_inc("physical_damage", min(50.0, 4e-05 * gs("mitigation")))

								if keystones.has("TREE_SHOCKING_MOVES"):
												
												change_effect_inc("lightning_damage", min(50.0, 5e-05 * gs("evasion")))

								if keystones.has("UNIQUE_OGRE_TALISMAN"):
												change_effect_added("fire_damage", 0.05 * gs("health_max"))

								if Levels.is_current_level_hideout():
												change_effect_more("movement_speed", 1.25)

								if keystones.has("UNIQUE_CHEETAHS"):
												change_effect_inc("cast_speed", gi("movement_speed") * 0.5)

								if keystones.has("TREE_CAPABLE_COMBATANT"):
												var block_chance = cap_block(gs("block_chance"))
												change_effect_more("all_damage", 1.0 + block_chance)

								if keystones.has("TREE_HOPLITE"):
												var active_stats = GameState.get_active_stats()
												var has_melee = false
												var has_shield = false
												var weapons = active_stats.gene_loadout[Genes.GeneSlot.WEAPON]
												for slot in weapons:
																var item_id = weapons[slot]
																if item_id:
																				var item = GameState.get_gene(item_id)
																				if item.type == Genes.BaseType.MELEE_WEAPON:
																								has_melee = true
																				if Genes.is_shield(item.type):
																								has_shield = true
												if has_melee and has_shield:
																change_effect_more("all_damage", 1.6)

								if keystones.has("TREE_SWORDSMAN"):
												var active_stats = GameState.get_active_stats()
												var melee_count = 0
												var weapons = active_stats.gene_loadout[Genes.GeneSlot.WEAPON]
												for slot in weapons:
																var item_id = weapons[slot]
																if item_id:
																				var item = GameState.get_gene(item_id)
																				if item.type == Genes.BaseType.MELEE_WEAPON:
																								melee_count += 1
												if melee_count == 2:
																change_effect_more("cast_speed", 1.3)
																change_effect_more("all_damage", 1.2)
																change_effect_more("incoming_damage", 0.8)

								effective_evasion = Mitigation.get_effective_evasion(gs("evasion"), GameState.get_active_stats().account_level)
								effective_mitigation = Mitigation.get_effective_mitigation(gs("mitigation"), GameState.get_active_stats().account_level)
				else:
								effective_evasion = Mitigation.get_effective_evasion(gs("evasion"), level)
								effective_mitigation = Mitigation.get_effective_mitigation(gs("mitigation"), level)

func apply_attribute_effects():
				
				cached_stats["constitution"] = floor(gs("constitution"))
				cached_stats["strength"] = floor(gs("strength"))
				cached_stats["agility"] = floor(gs("agility"))
				cached_stats["wisdom"] = floor(gs("wisdom"))
				cached_stats["finesse"] = floor(gs("finesse"))

				
				change_effect_added("health_max", gs("constitution"))
				change_effect_inc("mitigation", gs("strength") / 100.0)
				change_effect_inc("evasion", gs("agility") / 100.0)
				change_effect_inc("all_damage", gs("wisdom") / 500.0)
				change_effect_inc("cast_speed", gs("finesse") / 500.0)

				
				change_effect_added("physical_damage", floor(gs("physical_per_25_strength")) * floor(gs("strength") / 25.0))
				change_effect_added("lightning_damage", floor(gs("lightning_per_25_agility")) * floor(gs("agility") / 25.0))
				change_effect_added("cold_damage", floor(gs("cold_per_25_wisdom")) * floor(gs("wisdom") / 25.0))
				change_effect_added("fire_damage", floor(gs("fire_per_25_constitution")) * floor(gs("constitution") / 25.0))
				change_effect_added("toxic_damage", floor(gs("toxic_per_25_finesse")) * floor(gs("finesse") / 25.0))

				
				change_effect_added("health_regen", gs("life_regen_per_wisdom") * gs("wisdom"))

				
				var total_attr = gs("constitution") + gs("agility") + gs("constitution") + gs("wisdom") + gs("finesse")
				change_effect_inc("all_damage", gi("damage_per_25_attributes") * floor(total_attr / 25.0))
				change_effect_more("all_damage", (1.0 + (gm("damage_per_25_attributes") - 1.0) * floor(total_attr / 25.0)))

				if keystones.has("TREE_VIRIDIAN_SAGE"):
								change_effect_more("incoming_damage", 1.0 - min(0.3, 0.01 * floor(gs("wisdom") / 30)))

func apply_boon_effects():
				
				var swiftness_boons = status_flags.get(Constants.StatusFlags.SWIFTNESS_BOON, 0)
				var toughness_boons = status_flags.get(Constants.StatusFlags.TOUGHNESS_BOON, 0)
				var precision_boons = status_flags.get(Constants.StatusFlags.PRECISION_BOON, 0)
				var total_boons = swiftness_boons + toughness_boons + precision_boons
				var max_boons = gs("swiftness_boon") + gs("toughness_boon") + gs("precision_boon")

				
				if swiftness_boons > 0:
								change_effect_more("movement_speed", 1.0 + (0.04 * swiftness_boons))
								change_effect_more("cast_speed", 1.0 + (0.04 * swiftness_boons))
								change_effect_added("lightning_damage", ga("lightning_per_swiftness") * swiftness_boons)
								change_effect_inc("lightning_damage", gi("lightning_per_swiftness") * swiftness_boons)
								change_effect_more("lightning_damage", (1.0 + (gm("lightning_per_swiftness") - 1.0) * swiftness_boons))

								
								change_effect_inc("all_damage", gi("damage_per_swiftness") * swiftness_boons)
								change_effect_more("all_damage", (1.0 + (gm("damage_per_swiftness") - 1.0) * swiftness_boons))

								
								change_effect_inc("projectile_speed", gi("projectile_speed_per_swiftness") * swiftness_boons)
								change_effect_more("projectile_speed", (1.0 + (gm("projectile_speed_per_swiftness") - 1.0) * swiftness_boons))

								
								change_effect_added("extra_physical_as_lightning", gs("extra_physical_as_lightning_per_swiftness") * swiftness_boons)

								change_effect_inc("area_of_effect", gi("aoe_per_swiftness") * swiftness_boons)
								change_effect_more("area_of_effect", (1.0 + (gm("aoe_per_swiftness") - 1.0) * swiftness_boons))

				if toughness_boons > 0:
								
								change_effect_more("incoming_damage", max(0.1, (1.0 - 0.05 * toughness_boons)))

								
								change_effect_added("health_regen_percent", toughness_boons * gs("health_regen_percent_toughness_boon"))

								
								change_effect_added("fire_damage", ga("fire_per_toughness") * toughness_boons)
								change_effect_inc("fire_damage", gi("fire_per_toughness") * toughness_boons)
								change_effect_more("fire_damage", (1.0 + (gm("fire_per_toughness") - 1.0) * toughness_boons))

								change_effect_added("mitigation", ga("armor_per_toughness") * toughness_boons)
								change_effect_inc("mitigation", gi("armor_per_toughness") * toughness_boons)
								change_effect_more("mitigation", (1.0 + (gm("armor_per_toughness") - 1.0) * toughness_boons))

								
								change_effect_inc("all_damage", gi("damage_per_toughness") * toughness_boons)
								change_effect_more("all_damage", (1.0 + (gm("damage_per_toughness") - 1.0) * toughness_boons))

								change_effect_added("extra_physical_as_fire", gs("extra_physical_as_fire_per_toughness") * toughness_boons)

								change_effect_inc("area_of_effect", gi("aoe_per_toughness") * toughness_boons)
								change_effect_more("area_of_effect", (1.0 + (gm("aoe_per_toughness") - 1.0) * toughness_boons))

				if precision_boons > 0:
								
								change_effect_inc("crit_chance", precision_boons * 0.3)

								
								change_effect_added("cold_damage", ga("cold_per_precision") * precision_boons)
								change_effect_inc("cold_damage", gi("cold_per_precision") * precision_boons)
								change_effect_more("cold_damage", (1.0 + (gm("cold_per_precision") - 1.0) * precision_boons))

								change_effect_added("crit_multi", ga("crit_multi_per_precision") * precision_boons)
								change_effect_inc("crit_multi", gi("crit_multi_per_precision") * precision_boons)
								change_effect_more("crit_multi", (1.0 + (gm("crit_multi_per_precision") - 1.0) * precision_boons))

								
								change_effect_inc("all_damage", gi("damage_per_precision") * precision_boons)
								change_effect_more("all_damage", (1.0 + (gm("damage_per_precision") - 1.0) * precision_boons))

								change_effect_inc("dot_damage", gi("dot_damage_per_precision") * precision_boons)
								change_effect_more("dot_damage", (1.0 + (gm("dot_damage_per_precision") - 1.0) * precision_boons))

								change_effect_added("extra_physical_as_cold", gs("extra_physical_as_cold_per_precision") * precision_boons)

								change_effect_inc("area_of_effect", gi("aoe_per_precision") * precision_boons)
								change_effect_more("area_of_effect", (1.0 + (gm("aoe_per_precision") - 1.0) * precision_boons))

				change_effect_inc("all_damage", gi("damage_per_boon") * total_boons)
				change_effect_more("all_damage", (1.0 + (gm("damage_per_boon") - 1.0) * total_boons))


				if total_boons == max_boons:
								if keystones.has("TREE_FURY"):
												change_effect_more("all_damage", 1.4)

func load_from_level_buffs():
				if is_player:
								var buffs = cached_level_buffs.stats
								for stat in buffs:
												var scale_mods = buffs[stat]
												
												for scaling_type in scale_mods:
																var amount = scale_mods[scaling_type]
																if scaling_type == Constants.ScalingType.FLAT:
																				added_stats[stat] += amount
																elif scaling_type == Constants.ScalingType.PERCENT:
																				inc_stats[stat] += amount
																elif scaling_type == Constants.ScalingType.MORE:
																				more_stats[stat] *= (1.0 + amount)


func load_from_monster_mods():
				if is_enemy:
								var mods = get_parent().monster_mods
								
								for mod in mods:
												for stat in mod.stats:
																var scale_mods = mod.stats[stat]
																
																for scaling_type in scale_mods:
																				var amount = scale_mods[scaling_type]
																				if scaling_type == Constants.ScalingType.FLAT:
																								added_stats[stat] += amount
																				elif scaling_type == Constants.ScalingType.PERCENT:
																								inc_stats[stat] += amount
																				elif scaling_type == Constants.ScalingType.MORE:
																								more_stats[stat] *= (1.0 + amount)

func load_from_passives():
				if is_player:
								for keystone in cached_passive_buffs.keystones:
												keystones[keystone] = true
								var buffs = cached_passive_buffs.stats
								for stat in buffs:
												var scale_mods = buffs[stat]
												
												for scaling_type in scale_mods:
																var amount = scale_mods[scaling_type]
																if scaling_type == Constants.ScalingType.FLAT:
																				added_stats[stat] += amount
																elif scaling_type == Constants.ScalingType.PERCENT:
																				inc_stats[stat] += amount
																elif scaling_type == Constants.ScalingType.MORE:
																				more_stats[stat] *= (1.0 + amount)

								var conditional_buffs = cached_passive_buffs.conditional_stats
								for tag in conditional_buffs:
												for stat in conditional_buffs[tag]:
																var scale_mods = conditional_buffs[tag][stat]
																
																for scaling_type in scale_mods:
																				var amount = scale_mods[scaling_type]
																				if scaling_type == Constants.ScalingType.FLAT:
																								conditional_stats[tag].added[stat] += amount
																				elif scaling_type == Constants.ScalingType.PERCENT:
																								conditional_stats[tag].inc[stat] += amount
																				elif scaling_type == Constants.ScalingType.MORE:
																								conditional_stats[tag].more[stat] *= (1.0 + amount)

func load_from_genes():
				if is_player:
								for keystone in cached_gene_buffs.keystones:
												keystones[keystone] = true
								var buffs = cached_gene_buffs.stats
								for stat in buffs:
												var scale_mods = buffs[stat]
												
												for scaling_type in scale_mods:
																var amount = scale_mods[scaling_type]
																if scaling_type == Constants.ScalingType.FLAT:
																				added_stats[stat] += amount
																elif scaling_type == Constants.ScalingType.PERCENT:
																				inc_stats[stat] += amount
																elif scaling_type == Constants.ScalingType.MORE:
																				more_stats[stat] *= (1.0 + amount)

								var conditional_buffs = cached_gene_buffs.conditional_stats
								for tag in conditional_buffs:
												for stat in conditional_buffs[tag]:
																var scale_mods = conditional_buffs[tag][stat]
																
																for scaling_type in scale_mods:
																				var amount = scale_mods[scaling_type]
																				if scaling_type == Constants.ScalingType.FLAT:
																								conditional_stats[tag].added[stat] += amount
																				elif scaling_type == Constants.ScalingType.PERCENT:
																								conditional_stats[tag].inc[stat] += amount
																				elif scaling_type == Constants.ScalingType.MORE:
																								conditional_stats[tag].more[stat] *= (1.0 + amount)

func reset_effect_stats():
				effect_added_stats.clear()
				effect_inc_stats.clear()
				effect_more_stats.clear()
				has_incoming_conversions = false

func load_from_effects():
				for effect in get_status_effects():
								var child = effect.get_ref()
								if not child:
												continue
								
								var changes = child.get_buffs_and_nerfs()
								var flags = child.get_status_flags()

								var reversed = child.reversed
								var inverter = 1.0
								if reversed:
												inverter = - 1.0

								for stat in changes:
												if typeof(changes[stat]) == TYPE_ARRAY:
																
																for item in changes[stat]:
																				if item.type == Constants.ScalingType.FLAT:
																								change_effect_added(stat, inverter * item.amount)
																				elif item.type == Constants.ScalingType.PERCENT:
																								change_effect_inc(stat, inverter * item.amount)
																				elif item.type == Constants.ScalingType.MORE:
																								change_effect_more(stat, (1.0 + inverter * item.amount))
												else:
																if changes[stat].type == Constants.ScalingType.FLAT:
																				change_effect_added(stat, inverter * changes[stat].amount)
																elif changes[stat].type == Constants.ScalingType.PERCENT:
																				change_effect_inc(stat, inverter * changes[stat].amount)
																elif changes[stat].type == Constants.ScalingType.MORE:
																				change_effect_more(stat, (1.0 + inverter * changes[stat].amount))

func perform_recompute_status_effects():
				status_flags = {}
				status_flag_amounts = {}
				unique_status_flags = {}
				active_damaging_ailments = {}
				damage_ailment_applier = {}
				affecting_ailment_count = 0

				var best_for_group = {}
				
				for child in status_effects.get_children():
								
								if child.expired:
												continue
								if not child.has_applied:
												continue
								if child.is_queued_for_deletion():
												continue
								
								child.is_active = true
								if child.unique_group != null and child.only_apply_strongest:
												child.is_active = false
												if not best_for_group.has(child.unique_group):
																
																best_for_group[child.unique_group] = child
																child.is_active = true
												elif child.is_better_than(best_for_group[child.unique_group]):
																
																best_for_group[child.unique_group].is_active = false
																best_for_group[child.unique_group].queue_free()
																best_for_group[child.unique_group] = child
																child.is_active = true
												else:
																child.queue_free()

				for child in status_effects.get_children():
								
								if child.expired:
												continue
								if not child.has_applied:
												continue
								if child.is_queued_for_deletion():
												continue
								if not child.is_active:
												continue

								
								if child.is_ailment:
												if child.does_ramp:
																affecting_ailment_count += child.n_applications
												else:
																affecting_ailment_count += 1

								var flags = child.get_status_flags()
								
								for flag in flags:
												if status_flags.has(flag):
																status_flags[flag] += 1
												else:
																status_flags[flag] = 1
																status_flag_amounts[flag] = child.get_effect_amount()

								if child.is_unique_status_flag:
												for flag in flags:
																unique_status_flags[flag] = child

				call_deferred("emit_signal", "status_effect_changed")

func recompute_status_effects(fast_flags = false):
				
				if fast_flags:
								perform_recompute_status_effects()
				_should_recompute = true

func post_load():
				if not is_player:
								return

				if keystones.has("TREE_RANGER"):
								change_effect_more("projectile_speed", 1.3)

				if keystones.has("TREE_MAGUS"):
								change_effect_more("area_of_effect", 1.3)

				if keystones.has("TREE_GLASS_CANNON"):
								change_effect_more("health_max", 0.35)
								change_effect_more("cast_speed", 1.1)
								change_effect_more("all_damage", 1.25)

				if keystones.has("TREE_REPEATER"):
								change_effect_more("cast_speed", 1.15)

				if keystones.has("UNIQUE_GOBLINS_GIRDLE"):
								if not cycles.has_node("GoblinsGirdle"):
												var cycle_buff = goblins_girdle.instance()
												cycle_buff.stats = self
												cycles.add_child(cycle_buff)
				elif cycles.has_node("GoblinsGirdle"):
								cycles.get_node("GoblinsGirdle").queue_free()

				if keystones.has("TREE_CYCLE"):
								if not cycles.has_node("CycleOfDestruction"):
												var cycle_buff = cycle_of_destruction.instance()
												cycle_buff.stats = self
												cycles.add_child(cycle_buff)
				elif cycles.has_node("CycleOfDestruction"):
								cycles.get_node("CycleOfDestruction").queue_free()

				if keystones.has("TREE_REGENERATIVE_FLESH"):
								if not cycles.has_node("RegenerativeFlesh"):
												var regen_buff = regenerative_flesh.instance()
												regen_buff.stats = self
												cycles.add_child(regen_buff)
				elif cycles.has_node("RegenerativeFlesh"):
								cycles.get_node("RegenerativeFlesh").queue_free()

				if keystones.has("TREE_PHANTOM_SHIELD"):
								if not cycles.has_node("PhantomShield"):
												var shield_buff = phantom_shield.instance()
												shield_buff.stats = self
												cycles.add_child(shield_buff)
				elif cycles.has_node("PhantomShield"):
								cycles.get_node("PhantomShield").queue_free()

				if keystones.has("TREE_UNLEASH"):
								if not cycles.has_node("Unleash"):
												var unleash_buff = unleash.instance()
												unleash_buff.stats = self
												cycles.add_child(unleash_buff)
				elif cycles.has_node("Unleash"):
								cycles.get_node("Unleash").queue_free()

				var parent_gear = get_parent().get_node("Gear")

				
				if keystones.has("TREE_DREAD"):
								if not parent_gear.has_node("DreadAura"):
												var dread = dread_aura.instance()
												dread.stats = self
												parent_gear.add_child(dread)
				elif parent_gear.has_node("DreadAura"):
								parent_gear.get_node("DreadAura").queue_free()

				
				if keystones.has("TREE_VILE_DOMAIN"):
								if not parent_gear.has_node("VileDomainAura"):
												var vile_domain = vile_domain_aura.instance()
												vile_domain.stats = self
												parent_gear.add_child(vile_domain)
				elif parent_gear.has_node("VileDomainAura"):
								parent_gear.get_node("VileDomainAura").queue_free()

				if keystones.has("TREE_BLOOD_ARMOR"):
								if not parent_gear.has_node("BloodArmorExplosion"):
												var blood_armor = blood_armor_skill.instance()
												blood_armor.stats = self
												parent_gear.add_child(blood_armor)
				elif parent_gear.has_node("BloodArmorExplosion"):
								parent_gear.get_node("BloodArmorExplosion").queue_free()

				if keystones.has("TREE_ENERGETIC_FLESH"):
								if not parent_gear.has_node("EnergeticFlesh"):
												var flesh = energetic_flesh_skill.instance()
												flesh.stats = self
												parent_gear.add_child(flesh)
				elif parent_gear.has_node("EnergeticFlesh"):
								parent_gear.get_node("EnergeticFlesh").queue_free()

				if keystones.has("TREE_BONDED_ELECTRONS"):
								if not parent_gear.has_node("BondedElectrons"):
												var electrons = bonded_electrons_skill.instance()
												electrons.stats = self
												parent_gear.add_child(electrons)
				elif parent_gear.has_node("BondedElectrons"):
								parent_gear.get_node("BondedElectrons").queue_free()

				
				if keystones.has("TREE_FRAGILE_CURSES"):
								change_effect_more("curse_effect", 1.3)

				if keystones.has("TREE_INFECTIOUS_MALIGNANCY"):
								change_effect_more("curse_effect", 0.9)

				if keystones.has("TREE_PROJECTILE_SPEED_DAMAGE"):
								change_effect_more("projectile_damage", (1.0 + 0.12 * gi("projectile_speed")))

				if keystones.has("TREE_GOLIATH"):
								change_effect_more("area_damage", (1.0 + 0.1 * gi("health_max")))


func fill_health():
				health = gs("health_max")
				emit_signal("health_changed")

func recover_health(amount, show_heal = false):
				var prior = health
				health = min(health + amount, gs("health_max"))
				if health != prior:
								var recovered = round(health - prior)
								if show_heal:
												$FloatingDamageManager.show_value("+" + str(recovered) + " hp", Colors.healing)
								emit_signal("health_changed")

func get_visible_enemies(check_collision = false, max_distance = INF):
				var enemies = nearby_enemies.keys()
				
				if max_distance < INF:
								var saved_enemies = []
								for enemy in enemies:
												if global_position.distance_to(enemy.global_position) <= max_distance:
																saved_enemies.append(enemy)
								enemies = saved_enemies

				
				if check_collision:
								var visible_enemies = []
								var space_state = get_parent().get_world_2d().direct_space_state
								for enemy in enemies:
												var result = space_state.intersect_ray(global_position, enemy.global_position, [], 256)
												if not result:
																visible_enemies.append(enemy)
								return visible_enemies
				else:
								return enemies

func get_visible_allies(max_distance = INF, can_target_self = false):
				var all_allies = get_tree().get_nodes_in_group(allies_group)
				var visible_allies = []
				for ally in all_allies:
								if ally.stats.is_dead:
												continue
								if ally.stats == self and not can_target_self:
												continue
								if global_position.distance_to(ally.global_position) < max_distance:
												visible_allies.append(ally)
				return visible_allies

func collect_and_remove_bleeds():
				var total_damage = {"damage": {}}
				var bleeds_to_remove = []
				for ref in get_status_effects():
								var effect = ref.get_ref()
								if not effect or not effect.is_active:
												continue
								var flags = effect.get_status_flags()
								if flags.has(Constants.StatusFlags.BLEEDING):
												var dmg = effect.get_remaining_bleed_damage()
												for k in dmg.damage:
																if total_damage.has(k):
																				total_damage.damage[k] += dmg.damage[k]
																else:
																				total_damage.damage[k] = dmg.damage[k]
												bleeds_to_remove.append(effect)

				for effect in bleeds_to_remove:
								effect.queue_free()

				return total_damage


func is_affected_by(flag):
				return status_flags.has(flag)

func get_conditional_modified_stat(stat, tags = null, skill = null):
				
				
				if tags == null:
								return self.gs(stat)
				if not use_conditional_stats:
								return self.gs(stat)

				
				var result = base_stats[stat]

				
				result += ga(stat)
				if skill:
								result += skill.get_supporting_stat_added(stat, 0.0)

				
				var base_increased_amount = gi(stat)
				if skill:
								base_increased_amount += skill.get_supporting_stat_inc(stat, 0.0)

				
				var base_more_amount = gm(stat)
				if skill:
								base_more_amount *= skill.get_supporting_stat_more(stat, 1.0)

				if skill:
								for tag in tags:
												if conditional_stats.has(tag):
																if conditional_stats[tag].added.has(stat):
																				result += conditional_stats[tag].added[stat] + skill.get_conditional_supporting_stat_added(tag, stat, 0.0)
																if conditional_stats[tag].inc.has(stat):
																				base_increased_amount += conditional_stats[tag].inc[stat] + skill.get_conditional_supporting_stat_inc(tag, stat, 0.0)
																if conditional_stats[tag].more.has(stat):
																				base_more_amount *= conditional_stats[tag].more[stat] * skill.get_conditional_supporting_stat_more(tag, stat, 1.0)
												else:
																result += skill.get_conditional_supporting_stat_added(tag, stat, 0.0)
																base_increased_amount += skill.get_conditional_supporting_stat_inc(tag, stat, 0.0)
																base_more_amount *= skill.get_conditional_supporting_stat_more(tag, stat, 1.0)

				
				result *= (1.0 + base_increased_amount)

				
				result *= base_more_amount

				
				
				

				
				

				return result

func get_conditional_modified_stat_parts(stat, tags = null, skill = null):
				
				var base = base_stats[stat]

				
				var base_added = ga(stat) + skill.get_supporting_stat_added(stat, 0.0)

				
				var base_increased_amount = gi(stat) + skill.get_supporting_stat_inc(stat, 0.0)

				
				var base_more_amount = gm(stat) * skill.get_supporting_stat_more(stat, 1.0)

				if use_conditional_stats:
								for tag in tags:
												if conditional_stats.has(tag):
																if conditional_stats[tag].added.has(stat):
																				base_added += conditional_stats[tag].added[stat] + skill.get_conditional_supporting_stat_added(tag, stat, 0.0)
																if conditional_stats[tag].inc.has(stat):
																				base_increased_amount += conditional_stats[tag].inc[stat] + skill.get_conditional_supporting_stat_inc(tag, stat, 0.0)
																if conditional_stats[tag].more.has(stat):
																				base_more_amount *= conditional_stats[tag].more[stat] * skill.get_conditional_supporting_stat_more(tag, stat, 1.0)
												else:
																base_added += skill.get_conditional_supporting_stat_added(tag, stat, 0.0)
																base_increased_amount += skill.get_conditional_supporting_stat_inc(tag, stat, 0.0)
																base_more_amount *= skill.get_conditional_supporting_stat_more(tag, stat, 1.0)

				return {
								"base": base, 
								"add": base_added, 
								"inc": base_increased_amount, 
								"more": base_more_amount, 
				}

func is_affected_by_group(group_id):
				return effect_for_group.has(group_id)

func remove_effect_for_group(group_id):
				if is_affected_by_group(group_id):
								var effect = effect_for_group[group_id].get_ref()
								if effect:
												effect.remove_effect()
								effect_for_group.erase(group_id)

func get_entity_name():
				if is_player:
								return "You"
				else:
								
								var mob_parent = get_parent()
								var mob_name = MonsterStats.monster_stats[mob_parent.type].name
								return mob_name

func proliferate_strongest_infection():
				var longest = 0
				var longest_effect = null
				for ref in get_status_effects():
								var effect = ref.get_ref()
								if effect and effect.is_active:
												var flags = effect.get_status_flags()
												if flags.has(Constants.StatusFlags.INFECTED):
																var duration_remaining = effect.get_remaining_duration()
																if duration_remaining > longest:
																				longest = duration_remaining
																				longest_effect = effect

				if longest_effect:
								longest_effect.proliferate()

func proliferate_burn():
				for ref in get_status_effects():
								var effect = ref.get_ref()
								if effect and effect.is_active:
												var flags = effect.get_status_flags()
												if flags.has(Constants.StatusFlags.BURNING):
																effect.proliferate()
																return

func _on_Area2D_area_entered(area: Area2D) -> void :
				var p = area.get_parent()
				if p == get_parent():
								return
				if p.is_in_group(target_group):
								nearby_enemies[p] = true

func _on_Area2D_area_exited(area: Area2D) -> void :
				var p = area.get_parent()
				if p == get_parent():
								return
				if p.is_in_group(target_group):
								nearby_enemies.erase(p)

func cc(stat):
				cached_stats.erase(stat)


func gs(stat):
				if cached_stats.has(stat):
								return cached_stats[stat]

				cached_stats[stat] = base_stats[stat]
				

				cached_stats[stat] += added_stats[stat]
				if effect_added_stats.has(stat):
								cached_stats[stat] += effect_added_stats[stat]

				
				var inc_amount = inc_stats[stat]
				if effect_inc_stats.has(stat):
								inc_amount += effect_inc_stats[stat]
				cached_stats[stat] *= (1.0 + inc_amount)

				
				cached_stats[stat] *= more_stats[stat]
				if effect_more_stats.has(stat):
								cached_stats[stat] *= effect_more_stats[stat]

				return cached_stats[stat]

func gi(stat):
				var inc_amount = inc_stats[stat]
				if effect_inc_stats.has(stat):
								inc_amount += effect_inc_stats[stat]
				return inc_amount


func ga(stat):
				var add_amount = added_stats[stat]
				if effect_added_stats.has(stat):
								add_amount += effect_added_stats[stat]
				return add_amount

func gm(stat):
				var more_amount = more_stats[stat]
				if effect_more_stats.has(stat):
								more_amount *= effect_more_stats[stat]
				return more_amount

func change_effect_added(stat, amount):
				if effect_added_stats.has(stat):
								effect_added_stats[stat] += amount
				else:
								effect_added_stats[stat] = amount
				cc(stat)

func change_effect_inc(stat, amount):
				if effect_inc_stats.has(stat):
								effect_inc_stats[stat] += amount
				else:
								effect_inc_stats[stat] = amount
				cc(stat)

func change_effect_more(stat, amount):
				if effect_more_stats.has(stat):
								effect_more_stats[stat] *= amount
				else:
								effect_more_stats[stat] = amount
				cc(stat)

func cap_resistance(resistance, maximum = 0.75):
				return min(1.0, min(maximum, resistance))

func cap_block(block):
				return min(0.75, block)

func consume_all_effects(flag):
				status_flags.erase(flag)
				status_flag_amounts.erase(flag)
				for effect in get_status_effects():
								var e = effect.get_ref()
								if e:
												if e.get_status_flags().has(flag):
																e.remove_effect()
