extends Node
class_name P4EnemyFeedbackController
## P4-A R1/R2: enemy-side readability without touching Mobs/**.
## Scans the "enemies" group, hooks each mob's Stats signals at runtime:
##   damage_taken -> white flash (modulate overbright tween) + screen shake
##   died         -> kill zoom punch + marker cleanup
## Elites additionally get a procedural ring marker above the sprite.

const SCAN_INTERVAL := 0.4

var config: P4FeedbackConfig
var _tracked := {}  # enemy -> bound damage_taken Callable (accurate is_connected)
var debug_connect_count := 0
var debug_flash_count := 0
var debug_marker_count := 0
var debug_damage_events := 0


func _ready() -> void:
	var timer := Timer.new()
	timer.wait_time = SCAN_INTERVAL
	timer.autostart = true
	timer.timeout.connect(_scan)
	add_child(timer)


func _process(_delta: float) -> void:
	# Polling fallback: signal dispatch on Stats.health_changed proved
	# unreliable for controller lambdas, while died-lambdas fire fine.
	# Frame-rate HP comparison catches every real hit deterministically.
	for enemy in _tracked.keys().duplicate():
		if not is_instance_valid(enemy):
			continue
		var key = _tracked[enemy]
		if typeof(key) != TYPE_DICTIONARY or not key.has("hp"):
			continue
		var st: Node = enemy.get("stats")
		if st == null:
			continue
		var now: float = float(st.get("health"))
		if now < float(key["hp"]):
			debug_damage_events += 1
			flash_enemy(enemy)
			var cam := get_viewport().get_camera_2d()
			if cam != null and cam.has_method("shake"):
				cam.shake()
		key["hp"] = now


func rescan() -> void:
	_scan()


func _scan() -> void:
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if not is_instance_valid(enemy):
			continue
		if not _tracked.has(enemy):
			var st: Node = enemy.get("stats")
			if st != null and is_instance_valid(st):
				# Flash trigger rides health_changed (no-arg signal): damage_taken
				# dispatch to controller lambdas proved unreliable in-engine,
				# while no-arg signals (died/health_changed) dispatch fine.
				var hp_handler := func() -> void:
					_handle_enemy_health_changed(enemy)
				var died_handler := func() -> void:
					_handle_enemy_died(enemy)
				if not st.health_changed.is_connected(hp_handler):
					st.health_changed.connect(hp_handler)
					debug_connect_count += 1
				if not st.died.is_connected(died_handler):
					st.died.connect(died_handler)
				_tracked[enemy] = {"hp": float(st.get("health")), "handlers": [hp_handler, died_handler]}
			else:
				_tracked[enemy] = null
		# elites can be flagged any time after spawn; (re)check every scan
		if bool(enemy.get("is_elite")):
			attach_elite_marker(enemy)


func flash_enemy(enemy: Node) -> void:
	if not is_instance_valid(enemy) or config == null:
		return
	debug_flash_count += 1
	enemy.modulate = Color(config.hit_flash_strength,
			config.hit_flash_strength, config.hit_flash_strength)
	var tw := create_tween()
	tw.tween_property(enemy, "modulate", Color.WHITE, config.hit_flash_duration)


func attach_elite_marker(enemy: Node) -> void:
	if not is_instance_valid(enemy) or config == null:
		return
	if enemy.has_node("P4EliteMarker"):
		return
	debug_marker_count += 1
	var ring := Polygon2D.new()
	ring.name = "P4EliteMarker"
	var pts := PackedVector2Array()
	var seg := 24
	for i in range(seg):
		var ang := TAU * float(i) / float(seg)
		pts.append(Vector2(cos(ang), sin(ang)) * config.elite_marker_radius)
	ring.polygon = pts
	ring.color = config.elite_marker_color
	ring.position = config.elite_marker_offset
	ring.z_index = 200
	enemy.add_child(ring)


func _handle_enemy_health_changed(enemy) -> void:
	# HP drop since last observation => the mob just got hit.
	if not is_instance_valid(enemy):
		return
	var st: Node = enemy.get("stats")
	if st == null or config == null:
		return
	var key = _tracked.get(enemy)
	var last: float = float(key["hp"]) if typeof(key) == TYPE_DICTIONARY and key.has("hp") else INF
	var now: float = float(st.get("health"))
	if typeof(key) == TYPE_DICTIONARY and key.has("hp"):
		key["hp"] = now
	if now < last:
		debug_damage_events += 1
		flash_enemy(enemy)
		var cam := get_viewport().get_camera_2d()
		if cam != null and cam.has_method("shake"):
			cam.shake()


func _handle_enemy_died(enemy) -> void:
	var cam := get_viewport().get_camera_2d()
	if cam != null and cam.has_method("zoom_punch"):
		cam.zoom_punch()
	_tracked.erase(enemy)
