extends RigidBody2D
class_name Mob

var dissolve_sprite = preload("res://scenes/Mobs/DissolveMob.tscn")
var plague_clouds = preload("res://scenes/Skills/Playable/PlagueClouds/PlagueClouds.tscn")
var speed_aura = preload("res://scenes/Skills/Auras/Rush/Rush.tscn")

var shatter = preload("res://scenes/Explosions/TexturedExplosions/ShatterExplosion.tscn")
var poof = preload("res://scenes/Explosions/TexturedExplosions/BurningDeath.tscn")


var gene_pickup = load("res://scenes/Pickups/Gene/GenePickup.tscn")
var orb_pickup = load("res://scenes/Pickups/Orb/OrbPickup.tscn")
var portal_pickup = load("res://scenes/Pickups/Portal/PortalPickup.tscn")

@onready var target = GameState.get_global("player")
@onready var level = GameState.get_global("level_layer")
@onready var ground_layer = GameState.get_global("ground")
@onready var attack_skill = $Gear/BasicAttack
@onready var gear = $Gear
@onready var stats = $Stats
@onready var status_bar = $StatusBar
@onready var pathing = $PathingController
var velocity

@export var type = ""
@export var disable_when_out_of_view = true
@export var target_proximity = 20.0
@export var is_flying = false
@export var does_melee_attack = true
@export var is_level_boss = false
var damage_type = SkillTags.Tags.PHYSICAL
var damage = 5
var xp = 1
var wave = 1
var effective_level = 1
var is_elite = false
var is_magic = false
var monster_mods = []


var attacking = false
var attack_time = 1.0
var attack_delay = 0.0
var attack_range = 50.0
var time_since_attack = 0.0
var attack_windup_done = false

var chase_distance = 300

var cached_ms = 0.0


var last_check_time = 1.5
var last_attack_test = 0.0
var target_visible = false
var offset_visible = false
var is_moving_to_start = false
var can_reset = false


var target_offset = Vector2.ZERO
var start_position = Vector2.ZERO


var last_global_position
var _needs_recheck = false

func _ready() -> void :
				
				effective_level = Globals.zone_level + 20 * (wave - 1)
				start_position = global_position


				if randf() < 0.01:
								
								var plague = plague_clouds.instantiate()
								gear.add_child(plague)

				if Levels.is_current_level_ladder():
								chase_distance = 800

				if is_level_boss:
								chase_distance = 500

				
				damage = MonsterStats.monster_stats[type].damage
				damage_type = MonsterStats.monster_stats[type].damage_type
				attack_range = MonsterStats.monster_stats[type].attack_range

				attack_time = MonsterStats.monster_stats[type].attack_time
				attack_delay = MonsterStats.monster_stats[type].attack_delay

				xp = MonsterStats.monster_stats[type].xp

				
				var override_stats = MonsterStats.monster_stats[type].stat_overrides
				stats.override_stats = {}
				for stat in override_stats:
								stats.override_stats[stat] = override_stats[stat]
				stats._initialize_stats()

				pathing.target = target
				pathing.pathing_target = target.global_position
				stats.connect("died", Callable(self, "_on_death"))
				stats.connect("health_changed", Callable(self, "_on_update_healthbar"))
				stats.connect("status_effect_changed", Callable(self, "_on_stats_changed"))
				var zone_damage_multiplier = ZoneScaling.get_damage_scaler(effective_level)
				stats.level = effective_level
				if is_elite:
								set_mob_scale(1.75)
								stats.base_stats["health_max"] = round(stats.base_stats["health_max"] * 5.0)
								stats.base_stats["all_damage"] = stats.base_stats["all_damage"] * 1.2
								damage *= 1.2
								xp *= 16.0
								$SpriteContainer/Sprite.material.set("shader_param/color", Colors.rare_mob)
								$SpriteContainer/Sprite.material.set("shader_param/enabled", true)
				elif is_magic:
								set_mob_scale(1.25)
								stats.base_stats["health_max"] = round(stats.base_stats["health_max"] * 2.0)
								stats.base_stats["all_damage"] = stats.base_stats["all_damage"] * 1.1
								damage *= 1.1
								xp *= 4.0
								$SpriteContainer/Sprite.material.set("shader_param/color", Colors.magic_mob)
								$SpriteContainer/Sprite.material.set("shader_param/enabled", true)
				else:
								$SpriteContainer/Sprite.material = null

				
				damage *= zone_damage_multiplier

				
				stats.base_stats["health_max"] *= ZoneScaling.get_health_scaler(effective_level)
				stats.base_stats["all_damage"] *= zone_damage_multiplier

				if not is_level_boss:
								stats.base_stats["cast_speed"] /= 2.0

				stats.recompute_stats(true)
				stats.fill_health()

				status_bar.update_healthbar(stats)

				if $SpriteContainer/Sprite.sprite_frames != null:
							$SpriteContainer/Sprite.frame = randi() % $SpriteContainer/Sprite.sprite_frames.get_frame_count("default")

				
				reset_target_offset()
				$Timer.wait_time = 8.0 + 4.0 * randf()

				
				if get_parent() != level:
								await FrameTimer.idle_frame(self).timeout
								get_parent().remove_child(self)
								level.add_child(self)

				stats.connect("stats_changed", Callable(self, "recache_ms"))
				recache_ms()

func recache_ms():
				cached_ms = stats.gs("movement_speed")

func reset_target_offset():
				target_offset = Vector2.RIGHT.rotated(randf() * 2 * PI) * (attack_range - 8) * 0.95
				pathing.offset = target_offset

func _integrate_forces(state):
				rotation_degrees = 0

func _physics_process(delta: float) -> void :
				last_check_time += delta * (0.5 + 0.5 * randf())
				last_attack_test += delta * (0.5 + 0.5 * randf())
				time_since_attack += delta

				if cached_ms == 0 or stats.status_flags.has(Constants.StatusFlags.FROZEN):
								apply_central_impulse( - linear_velocity)
								return

				if is_moving_to_start:
								var d_to_t = global_position.distance_to(start_position)
								var dir_to_t = global_position.direction_to(start_position)
								if d_to_t > 50:
												var delta_v = dir_to_t * cached_ms * 3.0 - linear_velocity
												apply_central_impulse(delta_v * 15.0 * delta)
								else:
												is_moving_to_start = false
				elif attacking:
								if time_since_attack > attack_delay and not attack_windup_done:
												attack_windup_done = true
												var v_target = global_position.direction_to(target.global_position) * (8.0 + attack_range) / (attack_time)
												var delta_v = v_target - linear_velocity
												apply_central_impulse(delta_v)
								if time_since_attack > attack_time + attack_delay or _needs_recheck:
												apply_central_impulse( - linear_velocity)
												call_deferred("stop_attack")
				elif last_attack_test > 1.0:
								last_attack_test = 0.0
								if can_attack():
												call_deferred("attack")
				else:
								if last_check_time > 2.0 or _needs_recheck:
												if pathing.is_offset_visible():
																offset_visible = true
																target_visible = true
												elif pathing.is_target_visible():
																offset_visible = false
																target_visible = true
												else:
																offset_visible = false
																target_visible = false
												last_check_time = 0.0
												_needs_recheck = false

												if start_position.distance_to(global_position) > 800 and start_position != Vector2.ZERO:
																if can_reset:
																				is_moving_to_start = true


								var target_movement_position = target.global_position
								if offset_visible:
												target_movement_position += target_offset
								var d_to_t = global_position.distance_to(target_movement_position)
								var dir_to_t = global_position.direction_to(target_movement_position)
								if target_visible:
												if d_to_t < chase_distance or (stats.health < stats.gs("health_max") and d_to_t < 300):
																var delta_v = dir_to_t * cached_ms - linear_velocity
																if d_to_t <= target_proximity:
																				apply_central_impulse( - linear_velocity)
																else:
																				apply_central_impulse(delta_v * 15.0 * delta)

				var target_direction = global_position.direction_to(target.global_position)
				if target_direction.x < 0:
								$SpriteContainer/Sprite.flip_h = true
				elif target_direction.x > 0:
								$SpriteContainer/Sprite.flip_h = false

func _on_update_healthbar():
				status_bar.update_healthbar(stats)

func _on_stats_changed():
				var modulate_color = Color.WHITE
				if stats.status_flags.has(Constants.StatusFlags.POISONED) or stats.status_flags.has(Constants.StatusFlags.INFECTED):
								modulate_color = modulate_color.blend(Color.GREEN)
				if stats.status_flags.has(Constants.StatusFlags.BLEEDING):
								modulate_color = modulate_color.blend(Color.RED)
				if stats.status_flags.has(Constants.StatusFlags.BURNING):
								modulate_color = modulate_color.blend(Color.ORANGE_RED)
				if stats.status_flags.has(Constants.StatusFlags.CHILLED):
								modulate_color = modulate_color.blend(Color.AQUA)
				if stats.status_flags.has(Constants.StatusFlags.JOLTED):
								modulate_color = modulate_color.blend(Color.YELLOW)
				if stats.status_flags.has(Constants.StatusFlags.VULNERABLE):
								modulate_color = modulate_color.blend(Color.GRAY)
				if stats.status_flags.has(Constants.StatusFlags.EXPOSED):
								modulate_color = modulate_color.blend(Color.DARK_ORCHID)

				if stats.status_flags.has(Constants.StatusFlags.FROZEN):
								modulate_color = Color.BLUE
								$SpriteContainer/Sprite.speed_scale = 0
				else:
								$SpriteContainer/Sprite.speed_scale = 1

				$SpriteContainer/Sprite.modulate = modulate_color

func _on_MobCollider_area_entered(area: Area2D) -> void :
				if area.get_parent().is_in_group("player"):
								if attack_windup_done:
												stop_attack()
												call_deferred("do_damage")

								
								if Globals.is_using_controller():
												Globals.set_context_entity(self)

func get_ailment_chances():
				return {
								SkillTags.Tags.PHYSICAL: stats.gs("physical_ailment_chance"), 
								SkillTags.Tags.LIGHTNING: stats.gs("lightning_ailment_chance"), 
								SkillTags.Tags.COLD: stats.gs("cold_ailment_chance"), 
								SkillTags.Tags.FIRE: stats.gs("fire_ailment_chance"), 
								SkillTags.Tags.TOXIC: stats.gs("toxic_ailment_chance"), 
				}

func get_ailment_effects():
				return {
								SkillTags.Tags.PHYSICAL: stats.gs("physical_ailment_effect"), 
								SkillTags.Tags.LIGHTNING: stats.gs("lightning_ailment_effect"), 
								SkillTags.Tags.COLD: stats.gs("cold_ailment_effect"), 
								SkillTags.Tags.FIRE: stats.gs("fire_ailment_effect"), 
								SkillTags.Tags.TOXIC: stats.gs("toxic_ailment_effect"), 
				}

func get_amplify_chance():
				return min(1.0, stats.gs("amplify_ailment_chance"))

func get_crit_multi():
				var parts = stats.get_conditional_modified_stat_parts("crit_multi")
				var compiled = (parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				return compiled

func get_crit_chance():
				var parts = stats.get_conditional_modified_stat_parts("crit_chance")
				var compiled = (parts.base + parts.add) * (1.0 + parts.inc) * parts.more
				return compiled

func do_damage():
				var damage_bundle = attack_skill.get_damage_bundle()

				target.stats.apply_damage(damage_bundle, Colors.color_for_skill_tag[damage_type], stats, true)

func get_random_offset():
				return Vector2( - 10 + randf() * 20, - 10 + randf() * 20)

func get_unique_pools():
				if type == MonsterTypes.MonsterType.BOSS_SPIRIT_OF_THE_ANCIENT:
								return [UniquePoolSota.get("pool")]
				else:
								return [UniquePoolGeneric.get("pool")]

func _on_death():
				if stats.accumulated_applied_damage > 0.0:
								if GameState.saved_stats.settings.enable_floating_damage:
												stats.floating_damage.show_damage(ceil(stats.accumulated_applied_damage), Color.WHITE)

				target.stats.add_kills(1, is_elite, is_level_boss)
				var applied_xp = xp * ZoneScaling.get_xp_scaler(Globals.zone_level)
				target.stats.add_xp(applied_xp)
				if GameState.saved_stats.settings.enable_floating_xp:
								stats.floating_damage.show_xp(round(Globals.get_zone_scaled_xp() * applied_xp), Colors.keystone)
				var quantity_multiplier = 1.0 + Globals.stage_iiq
				var rarity_multiplier = Globals.stage_iir




				var drop_rate = 0.025 * quantity_multiplier
				var rarity_bonus = rarity_multiplier

				if Levels.is_current_level_ladder():
								
								
								pass
				else:
								if randf() < drop_rate or not GameState.is_tutorial_event_done("first_gene"):
												GameState.mark_tutorial_event_done("first_gene")
												var pickup = gene_pickup.instantiate()
												pickup.zone_level = effective_level
												pickup.unique_pools = get_unique_pools()
												pickup.rarity_bonus = (1.0 + rarity_bonus)
												ground_layer.add_child(pickup)
												pickup.global_position = global_position + get_random_offset()

								
								if randf() < drop_rate or is_elite:
												var n_count = 1
												if is_elite:
																if randf() < 0.7:
																				var pickup = gene_pickup.instantiate()
																				pickup.rarity_bonus = 3.5 * (1.0 + rarity_multiplier)
																				pickup.zone_level = effective_level
																				pickup.unique_pools = get_unique_pools()
																				ground_layer.add_child(pickup)
																				pickup.global_position = global_position + get_random_offset()
												var pickup = orb_pickup.instantiate()
												pickup.zone_level = effective_level
												pickup.quantity_multiplier = quantity_multiplier
												ground_layer.add_child(pickup)
												pickup.global_position = global_position + get_random_offset()

								if is_level_boss:
												GameState.complete_stage(GameState.get_global("active_stage_id"))
												var portal = portal_pickup.instantiate()
												portal.global_position = global_position
												level.call_deferred("add_child", portal)
												if randf() < 0.1 * quantity_multiplier:
																var pickup = gene_pickup.instantiate()
																pickup.rarity_bonus = 50.0
																pickup.zone_level = effective_level
																pickup.unique_pools = get_unique_pools()
																ground_layer.add_child(pickup)
																pickup.global_position = global_position + get_random_offset()
								elif Globals.stage_kills == 250:
												GameState.complete_stage(GameState.get_global("active_stage_id"))
												var portal = portal_pickup.instantiate()
												portal.global_position = global_position
												level.call_deferred("add_child", portal)

				spawn_death_animation()
				queue_free()

func _exit_tree() -> void :
				Globals.remove_context_entity(self)

func can_attack():
				return does_melee_attack and target_visible and global_position.distance_to(target.global_position) <= attack_range + target_proximity and attacking == false and time_since_attack > 1.0

func attack():
				if attacking or is_moving_to_start:
								return
				time_since_attack = 0.0
				attacking = true
				apply_central_impulse( - linear_velocity)

func stop_attack():
				attacking = false
				attack_windup_done = false
				time_since_attack = 0.0

func set_mob_scale(scale):
				$SpriteContainer.scale *= scale

func spawn_death_animation():
				var dissolve = dissolve_sprite.instantiate()
				dissolve.global_position = $SpriteContainer/Sprite.global_position
				level.add_child(dissolve)
				if $SpriteContainer/Sprite.sprite_frames != null:
							dissolve.sprite.sprite_frames = $SpriteContainer/Sprite.sprite_frames
				dissolve.sprite.scale = $SpriteContainer.scale
				dissolve.sprite.flip_h = $SpriteContainer/Sprite.flip_h

				
				if stats.status_flags.has(Constants.StatusFlags.FROZEN):
								var shatter_instance = shatter.instantiate()
								shatter_instance.global_position = global_position
								ground_layer.add_child(shatter_instance)
				elif stats.status_flags.has(Constants.StatusFlags.BURNING):
								var poof_instance = poof.instantiate()
								poof_instance.global_position = global_position
								ground_layer.add_child(poof_instance)

func _on_Timer_timeout() -> void :
				reset_target_offset()

func _on_MobCollider_mouse_entered() -> void :
				Globals.set_context_entity(self)


func _on_ResetTimer_timeout() -> void :
				start_position = global_position
				can_reset = true
