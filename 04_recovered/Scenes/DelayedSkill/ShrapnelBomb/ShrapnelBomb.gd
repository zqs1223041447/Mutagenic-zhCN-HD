extends DelayedSkill

var explosion = preload("res://Scenes/Explosions/TexturedExplosions/BookedShrapnelExplosion.tscn")
var splash_applier = preload("res://Scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.tscn")

func _physics_process(delta: float) -> void :
				if $AreaSkillEffect.started == false:
								$AreaSkillEffect.start()

func cast():
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats

				var explosion_instance = explosion.instance()
				explosion_instance.radius = radius
				explosion_instance.global_position = global_position
				level.add_child(explosion_instance)

				var splash_applier_instance = splash_applier.instance()
				splash_applier_instance.global_position = global_position
				splash_applier_instance.target_group = stats.target_group
				splash_applier_instance.damage_bundle = damage
				splash_applier_instance.radius = radius
				splash_applier_instance.skill_parent = sp
				GameState.get_global("ground").call_deferred("add_child", splash_applier_instance)
