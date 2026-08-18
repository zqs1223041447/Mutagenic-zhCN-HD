extends Button

var slot
var outfit_name


func _ready() -> void :
				var equipped = Outfits.get_outfit_in_slot(slot, outfit_name)
				if equipped:
								$Outfit.texture = equipped.get_frame("default", 0)

				GameState.connect("outfit_changed", self, "_update")
				_update()

				var is_equipped = GameState.is_outfit_equipped(slot, outfit_name)
				if is_equipped:
								grab_focus()

func _on_OutfitOption_pressed() -> void :
				GameState.equip_outfit(slot, outfit_name)


func _update():
				
				var is_equipped = GameState.is_outfit_equipped(slot, outfit_name)
				if is_equipped:
								$EquippedStatus.visible = true
				else:
								$EquippedStatus.visible = false
