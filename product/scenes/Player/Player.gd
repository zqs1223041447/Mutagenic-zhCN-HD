extends RigidBody2D
class_name Player

signal gear_changed

var velocity = Vector2()
@onready var gear = $Gear
@onready var stats = $Stats
@onready var healthbar = $Healthbar
@onready var sound_hit_damage = $TakeHitDamageSound
@onready var sound_xp = $PickupXPSound
@onready var sound_mutagen = $PickupMutagenSound
@onready var sound_levelup = $LevelupSound
@onready var sound_powerup = $PickupPowerupSound
@onready var sound_treasure = $TreasureSound
@onready var sound_orb = $OrbSound
@onready var animation_tree = $AnimationTree
@onready var state_machine = $AnimationTree.get("parameters/playback")
@onready var animation_player = $BodyParts/AnimationPlayer

@onready var pathing_target = global_position

var _needs_check = true

var levelup_effect = preload("res://scenes/Particles/LevelupEffect.tscn")
var death_screen = preload("res://scenes/Popups/DeathScreen.tscn")

var debug_path_points = []

var dash_cooldown = 0.0

# P4-A R2: player-follow camera (shake / zoom punch / hit-stop host)
var camera: P4PlayerCamera

func _ready() -> void :
				stats.connect("health_changed", Callable(self, "_on_update_healthbar"))
				stats.connect("died", Callable(self, "_on_death"))
				stats.connect("damage_taken", Callable(self, "_on_damage"))
				stats.connect("orb_pickup", Callable(self, "_on_orb"))
				stats.connect("powerup", Callable(self, "_on_powerup"))
				stats.connect("vulnerable", Callable(self, "_on_vulnerable_change"))
				stats.connect("shielded", Callable(self, "_on_shielded"))

				
				GameState.connect("passives_changed", Callable(stats, "_on_passives_changed"))
				GameState.connect("tree_changed", Callable(stats, "_on_passives_changed"))
				GameState.connect("gene_loadout_changed", Callable(stats, "_on_loadout_changed"))
				Genes.connect("gene_edited", Callable(stats, "_on_loadout_changed"))

				GameState.connect("mutation_tier_increased", Callable(self, "_on_levelup"))
				GameState.connect("outfit_changed", Callable(self, "_on_outfit_changed"))
				GameState.connect("skills_changed", Callable(self, "_on_skills_changed"))
				GameState.connect("skill_loadout_changed", Callable(self, "_on_skills_changed"))

				GameState.connect("specialization_changed", Callable(self, "_on_spec_changed"))
				GameState.connect("class_changed", Callable(self, "_on_class_changeds"))

				stats.connect("status_effect_changed", Callable(self, "_on_stats_changed"))

				Globals.connect("run_time_expired", Callable(self, "_on_time_expired"))

				gear.connect("child_entered_tree", Callable(self, "_on_gear_changed"))
				gear.connect("child_exiting_tree", Callable(self, "_on_gear_changed"))

				self._on_update_healthbar()
				state_machine.start("Default")
				_on_skills_changed()
				stats.recompute_stats(true)
				stats.fill_health()

				_on_outfit_changed()

				# P4-A R2: spawn the feedback camera under the player
				camera = P4PlayerCamera.new()
				camera.config = preload("res://scenes/GUI/Feedback/p4_feedback_config.tres")
				add_child(camera)

func _physics_process(delta):
				if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
								pathing_target = get_global_mouse_position()

				velocity = Vector2()
				velocity = Input.get_vector("move_left", "move_right", "move_up", "move_down")

				if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
								velocity = global_position.direction_to(pathing_target)
								velocity = velocity.normalized() * stats.gs("movement_speed")
				else:
								velocity = velocity.normalized() * stats.gs("movement_speed")

				var force_direction = (velocity - linear_velocity).normalized() * stats.gs("movement_speed")

				apply_central_impulse(delta * 15.0 * force_direction)

				if dash_cooldown > 0.0:
								dash_cooldown -= delta
								dash_cooldown = max(0.0, dash_cooldown)

				if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0:
								apply_central_impulse(velocity.normalized() * Constants.DASH_AMOUNT)
								Globals.play_sound_effect($DashSound.stream)
								dash_cooldown = 0.75

				if velocity.length_squared() > 0:
								if velocity.x <= 1.0:
												$BodyParts.scale.x = - 1.0
								elif velocity.x >= 1.0:
												$BodyParts.scale.x = 1.0
								animation_tree.set("parameters/Default/Animation/blend_position", 1.0)
								var playback_speed = 2.0 * stats.gs("movement_speed") / StatsInfo.defaults.movement_speed
								animation_tree.set("parameters/Default/TimeScale/scale", playback_speed)
				else:
								animation_tree.set("parameters/Default/Animation/blend_position", - 1.0)
								animation_tree.set("parameters/Default/TimeScale/scale", 1.0)

func _on_gear_changed(child):
				emit_signal("gear_changed")

func _on_update_healthbar():
				healthbar.max_value = stats.gs("health_max")
				healthbar.value = stats.health

func _on_death():
				print("You died.")
				var instance = death_screen.instantiate()
				PopupManager.show_popup(instance, get_tree().get_root().get_node("World"))

func _on_levelup() -> void :
				Globals.play_sound_effect(sound_levelup.stream)
				var expl = levelup_effect.instantiate()
				expl.emitting = true
				add_child(expl)

func _on_class_changed(new_class) -> void :
				Globals.play_sound_effect(sound_levelup.stream)
				var expl = levelup_effect.instantiate()
				expl.emitting = true
				add_child(expl)

func _on_spec_changed(new_class) -> void :
				Globals.play_sound_effect(sound_levelup.stream)
				var expl = levelup_effect.instantiate()
				expl.emitting = true
				add_child(expl)

func _on_skills_changed(any = null):
				var equipped_already = {}
				for child in gear.get_children():
								equipped_already[child.name] = child

				var valid_skills = {}
				var equipped_skills = GameState.get_equipped_skills()
				for slot in equipped_skills:
								var skill_name = equipped_skills[slot].skill
								if skill_name != null:
												valid_skills[skill_name] = true
												if equipped_already.has(skill_name):
																
																equipped_already[skill_name].slot = slot
												else:
																
																var skill_config = Skills.config[skill_name]
																var skill_inst = skill_config.skill_scene.instantiate()
																skill_inst.slot = slot
																skill_inst.stats = stats
																gear.add_child(skill_inst)

				for child in gear.get_children():
								if not valid_skills.has(child.name):
												
												if Skills.config[child.name].playable:
																child.queue_free()
								elif not child.is_queued_for_deletion():
												
												child.recompute_supported_stats()
				stats.recompute_stats()

func _on_damage(amounts, attacker_stats, was_crit):
				Globals.play_sound_effect(sound_hit_damage.stream)
				# P4-A R1/R2: red vignette + shake; crit counts as a heavy hit for hit-stop.
				var vignette = get_tree().get_first_node_in_group("p4_vignette")
				if vignette != null and vignette.has_method("flash"):
								vignette.flash()
				if camera != null:
								camera.shake()
								if was_crit:
												camera.hit_stop()

func _on_shielded():
				Globals.play_sound_effect(sound_hit_damage.stream)

func _on_orb(orb_type, amount):
				Globals.play_sound_effect(sound_orb.stream)

func _on_powerup():
				Globals.play_sound_effect(sound_powerup.stream)

func _on_vulnerable_change(vulnerable):
				if vulnerable:
								$ShieldedSprite.visible = false
				else:
								$ShieldedSprite.visible = true

func _on_RecomputePathTimer_timeout() -> void :
				_needs_check = true

func recompute_path():
				var _pathing_target = Globals.navmesh.get_shortest_path_target(global_position, get_global_mouse_position())
				if _pathing_target != null:
								pathing_target = _pathing_target
				else:
								pathing_target = get_global_mouse_position()

func _on_outfit_changed():
				var helmet = Outfits.get_helmet()
				$BodyParts/PantsAttachment/HeadAttachment/HelmetSprite.frames = helmet
				var head = Outfits.get_head()
				$BodyParts/PantsAttachment/HeadAttachment/HeadSprite.frames = head
				var pants = Outfits.get_pants()
				$BodyParts/PantsAttachment/PantsSprite.frames = pants
				var hands = Outfits.get_hands()
				$BodyParts/PantsAttachment/LeftHand/Hand.frames = hands
				$BodyParts/PantsAttachment/RightHand/Hand.frames = hands
				var feet = Outfits.get_feet()
				$BodyParts/PantsAttachment/LeftFoot/Foot.frames = feet
				$BodyParts/PantsAttachment/RightFoot/Foot.frames = feet
				var back = Outfits.get_back()
				$BodyParts/PantsAttachment/BackSprite.frames = back

func _on_stats_changed():
				call_deferred("_recheck_modulation")

func _recheck_modulation():
				var modulate_color = Color.WHITE
				if stats.status_flags.has(Constants.StatusFlags.POISONED):
								modulate_color = modulate_color.blend(Color.GREEN)
				if stats.status_flags.has(Constants.StatusFlags.BLEEDING):
								modulate_color = modulate_color.blend(Color.RED)
				if stats.status_flags.has(Constants.StatusFlags.CHILLED):
								modulate_color = modulate_color.blend(Color.AQUA)
				if stats.status_flags.has(Constants.StatusFlags.VULNERABLE):
								modulate_color = modulate_color.blend(Color.GRAY)

				$BodyParts.modulate = modulate_color
