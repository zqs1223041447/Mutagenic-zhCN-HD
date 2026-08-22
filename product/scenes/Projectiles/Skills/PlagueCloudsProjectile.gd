extends Projectile

var plague_effect = preload("res://scenes/StatusEffects/Skills/Plague.tscn")

var pulses = 0
var particle_multiplier = 1.0

var effective_radius = 0
func _ready():
				# P3-H3a: Godot 4 no longer auto-chains parent _ready(); run
				# Projectile._ready() first (weakref/collision/damage snapshot).
				super._ready()
				
				
				
				
				var particles = get_node_or_null("GPUParticles2D")
				if particles == null or particles.process_material == null:
								
								set_physics_process(false)
								return

				particles.lifetime = radius / particles.process_material.initial_velocity
				particles.amount *= particle_multiplier

				if target_group == "allies":
								particles.process_material.color = Color(0.586274, 0.65098, 0.27451)
				effective_radius = radius

func on_pulse(delta):
				var targets = get_tree().get_nodes_in_group(target_group)

				for target in targets:
								if target.global_position.distance_to(global_position) < effective_radius:
												var stats
												var skill_parent = skill_parent_weakref.get_ref()
												if skill_parent != null:
																stats = skill_parent.stats

												var plague = plague_effect.instantiate()
												plague.skill_parent_weakref = weakref(skill_parent)
												plague.applier_stats_weakref = weakref(stats)
												plague.damage_per_second = damage

												target.stats.apply_status_effect(plague)


