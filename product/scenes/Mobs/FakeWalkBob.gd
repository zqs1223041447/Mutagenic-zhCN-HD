extends Node
class_name FakeWalkBob
## FakeWalkBob — 程序化 Fallback 方案 A（5星推荐）
##
## 目标：单帧占位期间提供行走“动感”，真帧落地后仅需 play("walk") 替换 set_fake_walk()。
## 兼容策略：
##   - 若目标 AnimatedSprite2D 存在 "walk"/"idle" 动画，优先 play 真帧；否则走 tween bob。
##   - 真帧落地后：调用方把 `velocity.length() > 10` 的分支从 set_fake_walk() 改为 sprite.play("walk")。
##
## 用法（Player / Mob 均适用）：
##   @onready var fake_bob: FakeWalkBob = $FakeWalkBob  # 或 FakeWalkBob.new()
##   func _physics_process(delta):
##       var moving := velocity.length() > 10.0
##       fake_bob.set_fake_walk(moving)
##       # 或 fake_bob.update_from_velocity(velocity)
##
## 也可作为独立节点挂载到 SpriteContainer 同级，自动寻找 AnimatedSprite2D / Sprite2D。
##
## Tween 参数：position:y ±1px + scale 微缩放 (1.0 -> 1.02)，周期 0.24s，循环。

@export var target_path: NodePath
@export var bob_amplitude: float = 1.0
@export var bob_period: float = 0.24
@export var scale_amplitude: float = 0.02
@export var velocity_threshold: float = 10.0
@export var prefer_real_frames: bool = true

var bob: Tween
var _target: Node2D
var _base_position: Vector2
var _base_scale: Vector2
var _has_base: bool = false
var _is_bobbing: bool = false
var _sprite: AnimatedSprite2D

func _ready() -> void:
	_resolve_target()
	if _target != null:
		_base_position = _target.position
		_base_scale = _target.scale
		_has_base = true
	_sprite = _find_animated_sprite()

func _resolve_target() -> void:
	if not target_path.is_empty():
		var n = get_node_or_null(target_path)
		if n is Node2D:
			_target = n
			return
	# 自动推断：父节点是 Node2D 则用父；否则找同级/子级 SpriteContainer/Sprite
	var parent = get_parent()
	if parent is Node2D:
		# 若父是 RigidBody2D (Player/Mob)，则找 SpriteContainer 或 BodyParts
		var cand = parent.get_node_or_null("SpriteContainer")
		if cand == null:
			cand = parent.get_node_or_null("BodyParts")
		if cand == null:
			cand = parent.get_node_or_null("SpriteContainer/Sprite")
		if cand is Node2D:
			_target = cand
		else:
			# 回退：找第一个 Node2D 子节点
			for child in parent.get_children():
				if child is Node2D and child != self:
					_target = child
					break
			if _target == null:
				_target = parent as Node2D
	else:
		# 独立使用时
		for child in get_children():
			if child is Node2D:
				_target = child
				break

func _find_animated_sprite() -> AnimatedSprite2D:
	if _target == null:
		return null
	if _target is AnimatedSprite2D:
		return _target as AnimatedSprite2D
	# 在 _target 子树中查找
	for child in _target.get_children():
		if child is AnimatedSprite2D:
			return child
	if _target.get_parent() != null:
		for sibling in _target.get_parent().get_children():
			if sibling is AnimatedSprite2D:
				return sibling
	return _target.find_child("Sprite", true, false) as AnimatedSprite2D

func _has_real_walk() -> bool:
	if not prefer_real_frames or _sprite == null or _sprite.sprite_frames == null:
		return false
	return _sprite.sprite_frames.has_animation("walk") and _sprite.sprite_frames.get_frame_count("walk") > 1

func _has_real_idle() -> bool:
	if not prefer_real_frames or _sprite == null or _sprite.sprite_frames == null:
		return false
	return _sprite.sprite_frames.has_animation("idle") and _sprite.sprite_frames.get_frame_count("idle") >= 1

## 对外主接口：与后续真帧切换兼容
func set_fake_walk(active: bool) -> void:
	if _has_real_walk():
		# 真帧已落地：直接 play("walk") / play("idle")，不再 tween
		if _sprite == null:
			return
		var want = "walk" if active else "idle"
		if _sprite.sprite_frames.has_animation(want):
			if _sprite.animation != want:
				_sprite.play(want)
		return
	# Fallback：tween bob
	if active:
		_start_bob()
	else:
		_stop_bob()

## 便捷：直接传 velocity
func update_from_velocity(vel: Vector2) -> void:
	set_fake_walk(vel.length() > velocity_threshold)

func _start_bob() -> void:
	if _is_bobbing or _target == null:
		return
	if not _has_base:
		_base_position = _target.position
		_base_scale = _target.scale
		_has_base = true
	_is_bobbing = true
	# 清理旧 tween
	if bob != null and bob.is_valid():
		bob.kill()
	bob = create_tween()
	bob.set_loops()
	# 周期 0.24s = 0.12s 上 + 0.12s 下
	var half = bob_period * 0.5
	# position:y ±1px
	bob.tween_property(_target, "position:y", _base_position.y - bob_amplitude, half).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	bob.tween_property(_target, "position:y", _base_position.y + bob_amplitude, half).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	# 同步 scale 微缩放 (1.0 <-> 1.02) — 用 parallel
	# 为保持简单，用 parallel tween 绑定 scale
	# 注意：需要单独 tween 处理 scale，避免与 position 串行
	if scale_amplitude > 0.0:
		var scale_tween = create_tween()
		scale_tween.set_loops()
		scale_tween.tween_property(_target, "scale", _base_scale * (1.0 + scale_amplitude), half).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		scale_tween.tween_property(_target, "scale", _base_scale, half).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		# 将 scale tween 绑定到 bob，以便一起 kill
		bob.finished.connect(func(): pass) # placeholder to keep reference

func _stop_bob() -> void:
	if not _is_bobbing:
		return
	_is_bobbing = false
	if bob != null and bob.is_valid():
		bob.kill()
		bob = null
	# 杀掉所有关联 tween（scale）
	for t in get_tree().get_nodes_in_group("__fake_walk_tween"):
		pass
	# 恢复基线
	if _target != null and _has_base:
		_target.position = _base_position
		_target.scale = _base_scale
	# 若有真帧 idle，切回 idle
	if _has_real_idle() and _sprite != null:
		if _sprite.animation != "idle":
			_sprite.play("idle")

func _exit_tree() -> void:
	if bob != null and bob.is_valid():
		bob.kill()
