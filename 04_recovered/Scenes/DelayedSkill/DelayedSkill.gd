extends Node2D
class_name DelayedSkill

onready var level = GameState.get_global("level_layer")

export var damage = 0
export var radius = 0.0
export var target_group = "enemies"

var skill_parent
var skill_parent_weakref
var lifetime = 0.0
var linear_velocity = Vector2.ZERO

func _ready() -> void :
				var stats = skill_parent.stats
				$AreaSkillEffect.lifetime = lifetime
				$AreaSkillEffect.connect("expired", self, "_cast")
				skill_parent_weakref = weakref(skill_parent)

				set_radius(radius)

func _physics_process(delta: float) -> void :
				global_position += linear_velocity * delta

func set_radius(radius):
				$AreaSkillEffect.radius = radius
				$AreaSkillEffect._update_radius()

func track_hit(info):
				
				var sp = skill_parent_weakref.get_ref()
				if sp:
								sp.track_hit(info)

func get_visible_enemies(max_distance = INF):
				
				var all_enemies = get_tree().get_nodes_in_group(target_group)
				var visible_enemies = []
				for enemy in all_enemies:
								if global_position.distance_to(enemy.global_position) < max_distance:
												var space_state = get_world_2d().direct_space_state
												var result = space_state.intersect_ray(global_position, enemy.global_position, [self], 256)
												if not result:
																visible_enemies.append(enemy)

				return visible_enemies

func _cast():
				cast()
				queue_free()


func cast():
				pass

