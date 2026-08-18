extends Projectile

var webbed = preload("res://Scenes/StatusEffects/Skills/Webbed.tscn")

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var effect = webbed.instance()
				effect.skill_parent_weakref = skill_parent_weakref
				effect.applier_stats_weakref = weakref(stats)
				target.stats.apply_status_effect(effect)
				var info = target.stats.apply_damage(damage, Color.white, stats, true, false, sp)
				track_hit(info)

