extends Projectile

func on_hit(target):
				var stats
				var sp = skill_parent_weakref.get_ref()
				if sp != null:
								stats = sp.stats
				var info = target.stats.apply_damage(damage, Color.white, stats, true, false, sp)
				track_hit(info)



