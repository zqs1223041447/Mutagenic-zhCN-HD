extends GroundDegen


export var beam_length = 100
export var beam_width = 32


func _ready() -> void :
				$ColorRect.visible = false
				$ColorRect2.visible = false
				$Particles2D.visible = false
				skill_parent_weakref = weakref(skill_parent)
				update_beam()
				disable()


func update_beam():
				
				$Beam.length = beam_length
				$Beam.width = beam_width
				$CollisionShape2D.shape.extents = Vector2(beam_width / 2.0, beam_length / 2.0)
				$CollisionShape2D.position = Vector2(0, beam_length / 2.0)
				if damage_bundle:
								var tint_color = Color.white
								var max_dmg = 0.0
								for tag in damage_bundle.damage:
												if damage_bundle.damage[tag] > max_dmg:
																max_dmg = damage_bundle.damage[tag]
																tint_color = Colors.color_for_skill_tag[tag]
								$Beam / TextureRect.material.set_shader_param("color", tint_color)


func enable():
				enabled = true
				visible = true

func disable():
				enabled = false
				visible = false
