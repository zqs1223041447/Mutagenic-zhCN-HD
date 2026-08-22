extends Area2D
## Ground drop entity base. Restored from 04_recovered/Scenes/Pickups and
## ported to Godot 4 (P3-D E6 loot loop).
##
## Detection model (unchanged from the original): this Area2D monitors
## (mask = 1) and reacts to any Area2D whose parent body is in group
## "player" — the real Player.tscn provides PlayerCollider (layer 1,
## monitorable) exactly like that. Pickup itself is layer 0 / non-monitorable.
##
## Trigger paths: auto_pickup on touch, vacuum chase (does_vaccuum),
## the "interact" action while in range, or the info Button.
## Subclasses implement on_pickup() to write the item into the character
## inventory (e.g. Genes.pickup_gene).

@export var auto_pickup := false
@export var does_vaccuum := false
@export var persistent := false

var in_range := false
var hovered := false
var picked_up := false

var is_vaccuuming := false
var vaccuum_target: Node2D = null
var speed := 0.0

@onready var info: Control = $Node2D/VBoxContainer/InfoContainer


func _ready() -> void:
	render_info()


func _on_Pickup_area_entered(area: Area2D) -> void:
	var source: Node = area.get_parent()
	if source != null and source.is_in_group("player") and can_pickup():
		in_range = true
		info.visible = true
		if auto_pickup:
			_on_pickup()
		elif does_vaccuum:
			_on_pickup(source)


func _on_Pickup_area_exited(area: Area2D) -> void:
	var source: Node = area.get_parent()
	if source != null and source.is_in_group("player"):
		in_range = false
		info.visible = false


func _physics_process(delta: float) -> void:
	if Input.is_action_just_pressed("interact"):
		if in_range:
			_on_pickup()

	if vaccuum_target != null:
		global_position += global_position.direction_to(vaccuum_target.global_position) * speed
		speed += 10.0 * delta
		speed = min(speed, 200.0)

		if global_position.distance_to(vaccuum_target.global_position) < 10.0:
			do_pickup()


func _on_pickup(target: Node2D = null) -> void:
	if picked_up and not persistent:
		return
	picked_up = true
	if does_vaccuum and vaccuum_target == null:
		vaccuum_target = target
		is_vaccuuming = true
	else:
		do_pickup()


func do_pickup() -> void:
	on_pickup()
	if not persistent:
		queue_free()


func get_background_color() -> Color:
	return Color.WHITE


func get_font_color() -> Color:
	return Color.BLACK


func display_name() -> String:
	return "Some Pickup"


func can_pickup() -> bool:
	return true


func on_pickup() -> void:
	pass


func render_info() -> void:
	pass


func _on_Button_pressed() -> void:
	do_pickup()


func _on_Button_mouse_entered() -> void:
	hovered = true
	info.visible = true


func _on_Button_mouse_exited() -> void:
	hovered = false
	info.visible = false
