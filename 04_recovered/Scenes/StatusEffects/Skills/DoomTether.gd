extends BaseEffect

var doom_chain = preload("res://Scenes/Particles/DoomTether.tscn")
var doom_explosion = preload("res://Scenes/Explosions/TexturedExplosions/DoomExplosion.tscn")
var splash_applier = preload("res://Scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.tscn")

onready var target_stats = get_parent().get_parent()
onready var target = target_stats.get_parent()

var tether
var cooldown = 0.0
var can_tick = false

func on_apply():
				var source = applier_stats_weakref.get_ref()
				if source:
								var target = get_parent().get_parent()
								tether = doom_chain.instance()
								tether.source_target = source
								tether.dest_target = target
								ground_layer.call_deferred("add_child", tether)

				var sp = skill_parent_weakref.get_ref()
				if sp:
								can_tick = true
								cooldown = sp.get_cooldown()

func on_tick(delta):
				if not can_tick:
								return
				cooldown -= delta
				if cooldown <= 0:
								var sp = skill_parent_weakref.get_ref()
								if sp:
												cooldown += sp.get_cooldown()
												if sp.can_cast():
																if sp.can_pay_cost():
																				sp.pay_cost()
																				var attacker_stats = applier_stats_weakref.get_ref()
																				var damage_bundle = sp.get_damage_bundle()
																				var curse_count = 0
																				if target_stats.status_flags.has(Constants.StatusFlags.CURSED):
																								curse_count = target_stats.status_flags[Constants.StatusFlags.CURSED]
																				if curse_count > 0:
																								for tag in damage_bundle.damage:
																												damage_bundle.damage[tag] *= (1.0 + 0.5 * curse_count)

																				var info = target_stats.apply_damage(damage_bundle, Color.blueviolet, attacker_stats, false, false, sp)
																				track_hit(info)

																				if curse_count > 0:
																								var expl = doom_explosion.instance()
																								expl.global_position = target_stats.global_position
																								var radius = 20 * sp.get_aoe()
																								expl.radius = radius
																								ground_layer.add_child(expl)

																								var splash_applier_instance = splash_applier.instance()
																								splash_applier_instance.radius = radius
																								splash_applier_instance.ignore_instance = target
																								splash_applier_instance.damage_bundle = damage_bundle
																								splash_applier_instance.global_position = target_stats.global_position
																								ground_layer.call_deferred("add_child", splash_applier_instance)

func on_expire():
				
				if tether:
								tether.queue_free()

func get_status_flags():
				return []
