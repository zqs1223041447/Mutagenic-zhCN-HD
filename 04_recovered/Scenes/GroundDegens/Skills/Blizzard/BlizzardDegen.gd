extends GroundDegen

var chill = preload("res://Scenes/StatusEffects/DamageAilments/Chill.tscn")
var vulnerable = preload("res://Scenes/StatusEffects/Generic/Vulnerable.tscn")

func _ready():
				var stats = null
				var sp = skill_parent_weakref.get_ref()
				if sp:
								stats = sp.stats


func _physics_process(delta: float) -> void :
				if len(instances_to_damage) > 0:
								var stats = null
								var sp = skill_parent_weakref.get_ref()
								if sp:
												stats = sp.stats
								for entity in instances_to_damage:
												if not entity.stats.status_flags.has(Constants.StatusFlags.CHILLED):
																var ailment = chill.instance()
																ailment.skill_parent_weakref = skill_parent_weakref
																ailment.applier_stats_weakref = weakref(stats)
																entity.stats.apply_status_effect(ailment)
