extends CPUParticles2D
## P4-B F1a: programmatic hit-feedback particle burst.
##
## Spawned by Mob (scenes/Mobs/Mob.gd) when a mob's health drops, one burst
## per hit subject to a per-mob cooldown.  Burst color is configurable per
## damage element (SkillTags.Tags value): an explicit `color_override` wins,
## then the per-instance `element_color_overrides` table, then the shared
## defaults mirrored from Colors.color_for_skill_tag.
##
## Fully procedural (radial GradientTexture2D spark, no external frames), so
## it stays inside the P4 asset boundary; external frame sequences remain a
## WIRE-batch concern.  Honors GameState.is_fx_enabled() like every other
## explosion in scenes/Particles.

const DEFAULT_LIFETIME := 0.35

@export var element: int = 14  # SkillTags.Tags.PHYSICAL
@export var color_override := Color(0, 0, 0, 0)  # alpha 0 -> not overridden
@export var element_color_overrides: Dictionary = {}
@export var burst_amount := 10
@export var burst_lifetime := DEFAULT_LIFETIME
@export var burst_speed := 90.0

var _finished := false


static func default_element_colors() -> Dictionary:
				# Mirrors Colors.color_for_skill_tag keyed by SkillTags.Tags values
				# (autoloads are not reachable from static/parse-time contexts):
				# FIRE=11, COLD=12, LIGHTNING=13, PHYSICAL=14, TOXIC=15.
				return {
								11: Color(0.815686, 0.321569, 0.196078), 
								12: Color(0.14902, 0.388235, 0.733333), 
								13: Color(0.662745, 0.709804, 0.152941), 
								14: Color(0.701961, 0.701961, 0.701961), 
								15: Color(0.678431, 0.376471, 0.890196), 
				}


func burst_color() -> Color:
				if color_override.a > 0.0:
								return color_override
				if element_color_overrides.has(element):
								return element_color_overrides[element]
				return default_element_colors().get(element, Color.WHITE)


func _ready() -> void :
				one_shot = true
				explosiveness = 1.0
				emitting = false

				amount = max(1, burst_amount)
				lifetime = max(0.05, burst_lifetime)
				direction = Vector2.UP
				spread = 180.0
				gravity = Vector2.ZERO
				initial_velocity_min = burst_speed * 0.6
				initial_velocity_max = burst_speed
				damping_min = 220.0
				damping_max = 260.0
				scale_amount_min = 2.0
				scale_amount_max = 3.5
				color = burst_color()

				
				var shape_gradient := Gradient.new()
				shape_gradient.set_color(0, Color.WHITE)
				shape_gradient.set_color(1, Color(1, 1, 1, 0))
				var spark := GradientTexture2D.new()
				spark.width = 16
				spark.height = 16
				spark.fill = GradientTexture2D.FILL_RADIAL
				spark.fill_from = Vector2(0.5, 0.5)
				spark.fill_to = Vector2(0.5, 0.0)
				spark.gradient = shape_gradient
				texture = spark

				
				var fade := Gradient.new()
				fade.set_color(0, Color(1, 1, 1, 1))
				fade.set_color(1, Color(1, 1, 1, 0))
				color_ramp = fade

				var shrink := Curve.new()
				shrink.add_point(Vector2(0.0, 1.0))
				shrink.add_point(Vector2(1.0, 0.1))
				scale_amount_curve = shrink

				
				var free_timer := Timer.new()
				free_timer.one_shot = true
				free_timer.wait_time = lifetime * 3.0 + 1.0
				add_child(free_timer)
				free_timer.timeout.connect(_on_free_timer_timeout)
				free_timer.start()

				
				
				finished.connect(_on_finished)
				if GameState.is_fx_enabled():
								emitting = true
				else:
								_finished = true
								_on_finished.call_deferred()


func _on_finished() -> void :
				_finished = true
				
				queue_free()


func _on_free_timer_timeout() -> void :
				queue_free()


func has_finished() -> bool:
				return _finished
