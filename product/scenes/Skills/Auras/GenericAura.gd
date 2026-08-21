extends GenericSkill
class_name GenericAura

var aura_effect = preload("res://scenes/StatusEffects/Auras/AuraEffect.tscn")

@onready var area = $Area2D

@export var status_effect_description = ""
@export var status_effect_texture = null
var unique_aura_id
var buffs_and_nerfs = {}
var instances_affected = []
var radius = - 1.0
var rotation_multiplier = 1.0
var enabled = false
var prior_effect = 0.0

func _ready() -> void :
				unique_aura_id = "ae-" + str(get_instance_id())
				rotation_multiplier = PI / 2.0 * (0.8 + 0.4 * randf())
				if randf() < 0.5:
								rotation_multiplier *= - 1
				call_deferred("_initialize")

func _initialize():
				get_parent().get_parent().stats.connect("stats_changed", Callable(self, "_update_radius"))
				get_parent().get_parent().stats.connect("stats_changed", Callable(self, "reapply_aura_effect"))
				get_parent().get_parent().stats.connect("stats_changed", Callable(self, "recheck_enabled"))
				reapply_aura_effect()
				_update_radius()
				if target_group == "allies":
								area.collision_mask |= 1
				if target_group == "enemies":
								area.collision_mask |= 2
				recheck_enabled()

func recheck_enabled():
				enabled = true
				if stats.keystones.has("UNIQUE_BOMB_SPECIALIST"):
								
								if cached_tags.has(SkillTags.Tags.DAMAGING) and not cached_tags.has(SkillTags.Tags.BOMB):
												enabled = false

func _update_radius():
				
				var r = get_radius()
				if r == radius:
								return
				radius = r
				$Area2D/CollisionShape2D.shape.radius = radius
				$AuraDisplay.rect_size = Vector2(2.0 * radius, 2.0 * radius)
				$AuraDisplay.rect_position = Vector2( - radius, - radius)

func get_buffs_and_nerfs():
				var b_and_n = get_aura_buffs().duplicate(true)
				var aura_effect = stats.gs("aura_effect")
				for item in b_and_n:
								for scaling_type in b_and_n[item]:
												scaling_type.amount *= aura_effect
				return b_and_n

func get_aura_effect():
				var effect = aura_effect.instantiate()
				effect.unique_group = unique_aura_id
				effect.texture = status_effect_texture
				effect.description = status_effect_description
				effect.buffs_and_nerfs = get_buffs_and_nerfs()
				return effect

func _physics_process(delta: float) -> void :
				$AnimatedSprite2D.rotation += rotation_multiplier * delta
				if not enabled:
								return
				if len(instances_affected) > 0:
								for entity in instances_affected:
												if entity.stats.is_affected_by_group(unique_aura_id):
																continue
												var effect = get_aura_effect()
												entity.stats.apply_status_effect(effect)

func _on_Area2D_area_entered(area: Area2D) -> void :
				var p = area.get_parent()
				if p.is_in_group(target_group):
								instances_affected.append(p)

func _on_Area2D_area_exited(area: Area2D) -> void :
				var p = area.get_parent()
				if p.is_in_group(target_group) and instances_affected.has(p):
								instances_affected.erase(p)
								p.stats.remove_effect_for_group(unique_aura_id)

func reapply_aura_effect():
				var aura_effect = stats.gs("aura_effect")
				if aura_effect != prior_effect:
								prior_effect = aura_effect
								if len(instances_affected) > 0:
												for entity in instances_affected:
																if entity.stats.is_affected_by_group(unique_aura_id):
																				entity.stats.remove_effect_for_group(unique_aura_id)
																var effect = get_aura_effect()
																entity.stats.apply_status_effect(effect)
