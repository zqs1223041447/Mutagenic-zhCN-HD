extends Projectile

var vulnerable_effect = preload("res://scenes/StatusEffects/Generic/Vulnerable.tscn")

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var info = target.stats.apply_damage(damage, Color.WHITE, stats, true, false, sp)
				track_hit(info)

