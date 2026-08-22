extends ColorRect
class_name P4VignetteOverlay
## P4-A R1: full-screen red vignette flash on player damage.
## Lives under the GUI CanvasLayer; alpha tweens up then back to 0.

var config: P4FeedbackConfig
var _tween: Tween


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)
	color = Color(config.vignette_color, 0.0) if config != null else Color(0.75, 0.04, 0.04, 0.0)


func flash(strength: float = 1.0) -> void:
	if config == null:
		return
	if _tween != null and _tween.is_valid():
		_tween.kill()
	var peak: float = clampf(config.vignette_peak_alpha * strength, 0.0, 1.0)
	color = Color(config.vignette_color, peak)
	_tween = create_tween()
	_tween.tween_property(self, "color:a", 0.0, config.vignette_duration)
