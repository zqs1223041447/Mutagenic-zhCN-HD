extends Resource
class_name P4FeedbackConfig
## P4-A lane A: tunables for readability + camera/screen feedback.
## Single source of truth; .tres instance overrides any default.

# R1 enemy hit flash
@export var hit_flash_duration := 0.12
@export var hit_flash_strength := 3.0

# R1 elite marker
@export var elite_marker_color := Color(1.0, 0.82, 0.15, 0.85)
@export var elite_marker_radius := 9.0
@export var elite_marker_offset := Vector2(0, -44)

# R1 player vignette
@export var vignette_color := Color(0.75, 0.04, 0.04)
@export var vignette_peak_alpha := 0.45
@export var vignette_duration := 0.35

# R2 screen shake
@export var enable_shake := true
@export var shake_amplitude := 8.0
@export var shake_duration := 0.25

# R2 hit-stop (heavy hits = crits in this structural pass)
@export var enable_hitstop := true
@export var hitstop_scale := 0.25
@export var hitstop_duration := 0.09

# R2 kill micro-effect
@export var enable_kill_zoom := true
@export var kill_zoom_amount := 0.06
@export var kill_zoom_duration := 0.18
