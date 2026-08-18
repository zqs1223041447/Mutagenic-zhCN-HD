extends Area2D
class_name GroundDegen


export var target_group = "enemies"
export var lifetime = 4.0
export var is_permanent = false
export var is_beam = false
var damage_bundle = null
var radius = 1.0
var length = 1.0
var skill_parent = null
var skill_parent_weakref = null
var instances_to_damage = []
var enabled = true


func _ready() -> void :
				if not is_beam:
								$ColorRect.rect_position = Vector2( - radius, - radius)
								$ColorRect.rect_size = Vector2(2 * radius, 2 * radius)
								$ColorRect2.rect_position = Vector2( - radius, - radius)
								$ColorRect2.rect_size = Vector2(2 * radius, 2 * radius)
								$CollisionShape2D.shape.radius = radius
								$Particles2D.process_material.emission_sphere_radius = radius
								$Particles2D.amount *= 0.5 * sqrt(PI * radius * radius)

				skill_parent_weakref = weakref(skill_parent)

func _physics_process(delta: float) -> void :
				if not enabled:
								return
				if len(instances_to_damage) > 0:
								var stats = null
								var sp = skill_parent_weakref.get_ref()
								if sp:
												stats = sp.stats

								
								var applied_damage = damage_bundle.duplicate(true)
								for k in applied_damage.damage:
												applied_damage.damage[k] *= delta

								for entity in instances_to_damage:
												var info = entity.stats.apply_damage(applied_damage, Color.white, stats, false, true, sp)
												if sp:
																sp.track_hit(info)

				if not is_permanent:
								lifetime -= delta

								if lifetime <= 0:
												call_deferred("queue_free")

func _on_GroundDegen_area_entered(area: Area2D) -> void :
				var p = area.get_parent()
				if p.is_in_group(target_group):
								instances_to_damage.append(p)

func _on_GroundDegen_area_exited(area: Area2D) -> void :
				var p = area.get_parent()
				if p.is_in_group(target_group):
								instances_to_damage.erase(p)
