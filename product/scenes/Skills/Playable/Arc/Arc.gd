extends GenericSkill

var arc_spark = preload("res://scenes/Particles/SparkExplosion.tscn")

var potential_targets = []

func _ready() -> void :
				await FrameTimer.idle_frame(self).timeout
				get_parent().get_parent().stats.connect("stats_changed", Callable(self, "_update_radius"))
				_update_radius()

func can_cast():
				var all_enemies = get_visible_enemies(true)
				var effect_radius = get_radius()
				potential_targets = []
				for enemy in all_enemies:
								var dist_to_enemy = enemy.global_position.distance_to(global_position)
								if dist_to_enemy < effect_radius:
												potential_targets.append(enemy)
				return len(potential_targets) > 0

func cast(damage_multiplier = 1.0, consume_boons = false):
				play_sound()
				var n_proj = get_projectiles()
				var base_damage = get_damage_bundle()
				consume_boons()
				for i in range(n_proj):
								if len(potential_targets) > 0:
												var target_index = randi() % len(potential_targets)
												var target = potential_targets[target_index]
												var inst = arc_spark.instantiate()
												inst.global_position = target.global_position
												level.call_deferred("add_child", inst)
												
												var base_radius = get_radius()
												var distance_to_enemy = target.global_position.distance_to(global_position)
												var damage_ratio = 0.5 + 2.0 * (base_radius - distance_to_enemy) / base_radius
												var effective_damage = base_damage.duplicate(true)
												for k in effective_damage.damage:
																effective_damage.damage[k] *= damage_ratio
												var info = target.stats.apply_damage(effective_damage, Color.WHITE, stats, true, false, self)
												track_hit(info)

func _update_radius():
				
				var r = get_radius()
				$ColorRect.size = Vector2(r * 2.0, r * 2.0)
				$ColorRect.position = Vector2( - r, - r)
