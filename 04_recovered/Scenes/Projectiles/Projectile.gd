extends Area2D

class_name Projectile

var splash_effect = preload("res://Scenes/ShaderExplosions/CollateralDamageExplosion/CollateralDamageExplosion.tscn")
var splash_applier = preload("res://Scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.tscn")
signal collided_signal

export var does_hit = true
export var always_collide = false
export var hits = 1
export var chains = 0
export var damage = {"damage": {}}
var _initial_damage = null
export var radius = 0.0
export var target_group = "enemies"
export var can_bounce = false
export var has_limited_hits = true
export var expire_on_distance = true
export var manual_movement = false
export var max_distance_travelled = 300
export var ignore_terrain = false
export var tint_for_enemy = true

var skill_parent
var skill_parent_weakref

var distance_traveled = 0.0
var lifetime = 2.0
var lifetime_expired = 0.0

var pulse_expired = 0.0
export var pulse_cooldown = 0.0

var ricochet_bonus_damage = 0.0

var last_enemy_id = null

var expired = false

onready var sprite = $Sprite

var start_position
var linear_velocity = Vector2.ZERO
export var does_rotate = false

var nearby_enemies = {}

func _ready() -> void :
				skill_parent_weakref = weakref(skill_parent)

				if not does_hit:
								
								if not always_collide:
												monitorable = false
												monitoring = false


				start_position = global_position
				_initial_damage = damage.duplicate(true)

				if target_group == "allies":
								if tint_for_enemy:
												$Sprite.modulate = Color(0.960938, 0.295673, 0.295673)
								$Glow.visible = false
								collision_mask |= 1
				else:
								collision_mask |= 2

func _process(delta: float) -> void :
				if does_rotate:
								rotation = linear_velocity.angle()

func _physics_process(delta: float) -> void :
				lifetime_expired += delta
				if lifetime_expired >= lifetime:
								destroy_projectile()
								return
				pulse_expired -= delta
				distance_traveled += linear_velocity.length() * delta

				if pulse_cooldown > 0.0:
								if pulse_expired <= 0.0:
												pulse_expired += pulse_cooldown
												call_deferred("on_pulse", pulse_cooldown)

				if not manual_movement:
								global_position += linear_velocity * delta

				if distance_traveled >= max_distance_travelled and expire_on_distance:
								destroy_projectile()


func _on_Area2D_area_entered(area: Area2D) -> void :
				if not does_hit:
								return
				if area.get_parent().is_in_group(target_group):
								on_enter(area)

func on_enter(area):
				if expired:
								
								
								return

				if area.get_parent().is_in_group(target_group):
								var target = area.get_parent()

								if target.stats.health <= 0:
												
												return

								
								
								hits -= 1


								on_hit(target)
								_on_hit(target)

								if hits <= 0 and has_limited_hits:
												destroy_projectile()

func destroy_projectile():
				if expired:
								return
				expired = true
				on_destroy()
				call_deferred("queue_free")

func set_proj_scale(_scale):
				sprite.scale *= _scale
				scale *= _scale

func _on_hit(target):
				var sp = skill_parent_weakref.get_ref()
				var stats
				if sp:
								stats = sp.stats
				var should_splash = sp and sp.keystones.has("SUPPORT_COLLATERAL_DAMAGE")
				

				
				if should_splash and stats and randf() < 0.1:
								var effective_radius = 30 * sqrt(sp.get_aoe(true))
								var splash_damage = damage.duplicate(true)
								for k in splash_damage.damage:
																splash_damage.damage[k] *= 3.0

								var splash_applier_instance = splash_applier.instance()
								splash_applier_instance.global_position = target.stats.global_position
								splash_applier_instance.damage_bundle = splash_damage

								splash_applier_instance.radius = effective_radius
								splash_applier_instance.skill_parent = sp
								splash_applier_instance.can_be_blocked = false
								GameState.get_global("ground").call_deferred("add_child", splash_applier_instance)

								var effect = splash_effect.instance()
								effect.global_position = target.stats.global_position
								effect.radius = effective_radius
								GameState.get_global("ground").call_deferred("add_child", effect)

				if chains > 0:
								chains -= 1
								var visible_enemies = target.stats.get_visible_allies()
								if len(visible_enemies) == 0:
												return

								
								if stats and stats.keystones.has("TREE_RICOCHET"):
												ricochet_bonus_damage += 0.3
												var effective_damage = _initial_damage.duplicate()
												var damage_multiplier = (1.0 + ricochet_bonus_damage)
												for k in effective_damage.damage:
																effective_damage.damage[k] *= damage_multiplier
												
												damage = effective_damage

								var index = randi() % len(visible_enemies)
								var enemy = visible_enemies[index]
								linear_velocity = global_position.direction_to(enemy.global_position) * linear_velocity.length()

func on_hit(target):
				pass

func on_pulse(delta):
				
				pass

func on_destroy():
				pass

func track_hit(info):
				
				var sp = skill_parent_weakref.get_ref()
				if sp:
								sp.track_hit(info)

func _on_Projectile_body_entered(body: Node):
				if expired:
								return
				if can_bounce:
								linear_velocity = - linear_velocity
				elif ignore_terrain:
								pass
				else:
								destroy_projectile()

func play_sound():
				if has_node("Audio"):
								var sp = skill_parent_weakref.get_ref()
								if sp:
												if sp.get_parent().get_parent().is_in_group("player"):
																Globals.play_sound_effect(get_node("Audio").stream)
