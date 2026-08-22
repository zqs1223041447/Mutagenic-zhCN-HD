extends Camera2D
class_name P4PlayerCamera
## P4-A R2: player-follow camera with screen shake, zoom punch and hit-stop.
## All magnitudes/durations come from P4FeedbackConfig.

var config: P4FeedbackConfig

var _shake_time_left := 0.0
var _shake_total := 0.0
var _shake_amp := 0.0
var _zoom_tween: Tween
var _hitstop_count := 0


func _ready() -> void:
	make_current()


func _process(delta: float) -> void:
	if _shake_time_left > 0.0:
		_shake_time_left -= delta
		if _shake_time_left <= 0.0:
			offset = Vector2.ZERO
		else:
			var decayed: float = _shake_amp * (_shake_time_left / maxf(_shake_total, 0.0001))
			offset = Vector2(randf_range(-decayed, decayed), randf_range(-decayed, decayed))


func shake(amplitude: float = -1.0, duration: float = -1.0) -> void:
	if config == null or not config.enable_shake:
		return
	_shake_amp = amplitude if amplitude > 0.0 else config.shake_amplitude
	_shake_total = duration if duration > 0.0 else config.shake_duration
	_shake_time_left = _shake_total


func zoom_punch(amount: float = -1.0, duration: float = -1.0) -> void:
	if config == null or not config.enable_kill_zoom:
		return
	var amt: float = amount if amount > 0.0 else config.kill_zoom_amount
	var dur: float = duration if duration > 0.0 else config.kill_zoom_duration
	if _zoom_tween != null and _zoom_tween.is_valid():
		_zoom_tween.kill()
	zoom = Vector2.ONE
	_zoom_tween = create_tween()
	_zoom_tween.tween_property(self, "zoom", Vector2.ONE * (1.0 + amt), dur * 0.35)
	_zoom_tween.tween_property(self, "zoom", Vector2.ONE, dur * 0.65)


func hit_stop(scale_factor: float = -1.0, duration: float = -1.0) -> void:
	if config == null or not config.enable_hitstop:
		return
	_hitstop_count += 1
	if _hitstop_count > 1:
		return  # nested guard: already slowed by an earlier trigger
	var s: float = scale_factor if scale_factor > 0.0 else config.hitstop_scale
	var d: float = duration if duration > 0.0 else config.hitstop_duration
	Engine.time_scale = s
	# ignore_time_scale=true so the pause lasts real seconds, not scaled ones.
	await get_tree().create_timer(d, true, false, true).timeout
	_hitstop_count -= 1
	if _hitstop_count <= 0:
		_hitstop_count = 0
		Engine.time_scale = 1.0
