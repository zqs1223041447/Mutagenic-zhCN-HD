extends VBoxContainer

@onready var tooltip = $SkillTooltip

var texture
var tier
var item
var item_weakref


func _ready() -> void :
				item_weakref = weakref(item)
				$SkillContainer/PanelContainer/TextureRect.texture = texture
				tooltip.item_weakref = item_weakref


func _on_Timer_timeout() -> void :
				var i = item_weakref.get_ref()
				if i:
								$Label.text = str(Utils.render_suffix_number(i.total_damage))


func _on_TextureRect_mouse_entered() -> void :
				tooltip.render(rect_global_position, Vector2.ZERO)

func _on_TextureRect_mouse_exited() -> void :
				tooltip.hide()
