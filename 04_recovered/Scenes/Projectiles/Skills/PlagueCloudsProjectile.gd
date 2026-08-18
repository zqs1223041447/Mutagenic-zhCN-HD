extends Projectile

var plague_effect = preload("res://Scenes/StatusEffects/Skills/Plague.tscn")

var pulses = 0
var particle_multiplier = 1.0

var effective_radius = 0

func _ready():
				
				
				$Particles2D.lifetime = radius / $Particles2D.process_material.initial_velocity
				$Particles2D.amount *= particle_multiplier

				if target_group == "allies":
								$Particles2D.process_material.color = Color(0.586274, 0.65098, 0.27451)
				effective_radius = radius

func on_pulse(delta):
				var targets = get_tree().get_nodes_in_group(target_group)

				for target in targets:
								if target.global_position.distance_to(global_position) < effective_radius:
												var stats
												var skill_parent = skill_parent_weakref.get_ref()
												if skill_parent != null:
																stats = skill_parent.stats

												var plague = plague_effect.instance()
												plague.skill_parent_weakref = weakref(skill_parent)
												plague.applier_stats_weakref = weakref(stats)
												plague.damage_per_second = damage

												target.stats.apply_status_effect(plague)


