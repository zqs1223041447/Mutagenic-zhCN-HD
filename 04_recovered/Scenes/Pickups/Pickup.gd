extends Area2D
class_name Pickup

export var auto_pickup = false
export var does_vaccuum = false
export var persistent = false
var in_range = false
var hovered = false
var picked_up = false

var is_vaccuuming = false
var vaccuum_target = null
var speed = 0.0

onready var info = $Node2D / VBoxContainer / InfoContainer

func _ready():
				render_info()

func _on_Pickup_area_entered(area: Area2D) -> void :
				
				if area.get_parent().is_in_group("player") and can_pickup():
								in_range = true
								info.visible = true
								if auto_pickup:
												_on_pickup()
								elif does_vaccuum:
												_on_pickup(area.get_parent())

func _on_Pickup_area_exited(area: Area2D) -> void :
				if area.get_parent().is_in_group("player"):
								in_range = false
								info.visible = false

func _physics_process(delta: float) -> void :
				if Input.is_action_just_pressed("interact"):
								if in_range:
												_on_pickup()

				if vaccuum_target != null:
								global_position += global_position.direction_to(vaccuum_target.global_position) * speed
								speed += 10.0 * delta
								speed = min(speed, 200.0)

								if global_position.distance_to(vaccuum_target.global_position) < 10.0:
												do_pickup()

func _on_pickup(target = null):
				
				if picked_up and not persistent:
								return
				picked_up = true
				if does_vaccuum and not vaccuum_target:
								vaccuum_target = target
								is_vaccuuming = true
				else:
								do_pickup()

func do_pickup():
				on_pickup()
				if not persistent:
								queue_free()

func get_background_color():
				return Color.white

func get_font_color():
				return Color.black

func get_name():
				return "Some Pickup"

func can_pickup():
				return true

func on_pickup():
				pass

func render_info():
				pass

func _on_Button_pressed() -> void :
				do_pickup()

func _on_Button_mouse_entered() -> void :
				hovered = true
				info.visible = true

func _on_Button_mouse_exited() -> void :
				hovered = false
				info.visible = false
