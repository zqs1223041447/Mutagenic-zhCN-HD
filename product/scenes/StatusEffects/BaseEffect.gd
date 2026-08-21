extends Node
class_name BaseEffect

@onready var ground_layer = GameState.get_global("ground")

signal on_apply
signal on_expire




@export var permanent = false
@export var recompute_stats = true
@export var description = ""
@export var on_apply_tip = ""
@export var is_powerup = false
@export var reversed = false
@export var retriggerable = false
@export var target_group = "enemies"
@export var texture = null
@export var is_ailment = false
@export var only_apply_strongest = false
@export var stack_group = null
@export var does_ramp = false


@export var fast_flags = false

@export var damage_combine_group = null
@export var is_damaging_ailment = false


var lifetime = 0.0

@export var base_lifetime = 0.0

@export var unique_group = null
@export var does_tick = true
@export var is_unique_status_flag = false
var lifetime_expired = 0.0
var buffs_and_nerfs = {}
var applier_stats_weakref
var skill_parent_weakref
var ailment_effects = {}
var stats
var expired = false
var is_active = true
var has_applied = false
var n_applications = 1

var ramped_damage_for_applying_skill = {}
var total_applying_damage = 0.0

func initialize():
				pass

func _ready() -> void :
				trigger()

func trigger():
				lifetime = base_lifetime
				if stats:
								lifetime *= stats.gs("self_duration")
				on_apply()
				has_applied = true
				emit_signal("on_apply")


func _physics_process(delta: float) -> void :
				if is_active and does_tick:
								on_tick(delta)
				lifetime_expired += delta
				if lifetime_expired >= lifetime and not permanent:
								remove_effect()

func remove_effect():
				if expired:
								return
				expired = true
				queue_free()
				if is_active:
								on_expire()
								emit_signal("on_expire")

func on_apply():
				
				pass

func on_tick(delta):
				
				pass

func on_expire():
				
				pass

func track_hit(info):
				if not skill_parent_weakref:
								return
				var sp = skill_parent_weakref.get_ref()
				if sp:
								sp.track_hit(info)

func get_buffs_and_nerfs():
				return buffs_and_nerfs

func get_status_flags():
				return []

func is_better_than(other):
				var remaining = lifetime - lifetime_expired
				var o_remaining = other.lifetime - other.lifetime_expired
				return remaining > o_remaining

func get_remaining_duration():
				return lifetime - lifetime_expired

func get_visible_allies(max_distance = INF):
				if stats:
								return stats.get_visible_allies(max_distance)

func get_damage():
				return {}

func get_effect_amount():
				return 0

func get_physical_ailment_effect():
				if ailment_effects.has(SkillTags.Tags.PHYSICAL):
								return ailment_effects[SkillTags.Tags.PHYSICAL]
				return 1.0

func get_lightning_ailment_effect():
				if ailment_effects.has(SkillTags.Tags.LIGHTNING):
								return ailment_effects[SkillTags.Tags.LIGHTNING]
				return 1.0

func get_cold_ailment_effect():
				if ailment_effects.has(SkillTags.Tags.COLD):
								return ailment_effects[SkillTags.Tags.COLD]
				return 1.0

func get_fire_ailment_effect():
				if ailment_effects.has(SkillTags.Tags.FIRE):
								return ailment_effects[SkillTags.Tags.FIRE]
				return 1.0

func get_toxic_ailment_effect():
				if ailment_effects.has(SkillTags.Tags.TOXIC):
								return ailment_effects[SkillTags.Tags.TOXIC]
				return 1.0

func update_tracked_skill_amount(skill, amount):
				if ramped_damage_for_applying_skill.has(skill):
								ramped_damage_for_applying_skill[skill] += amount
				else:
								ramped_damage_for_applying_skill[skill] = amount
				total_applying_damage += amount
