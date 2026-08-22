extends "res://scenes/Pickups/Pickup.gd"
## Boss-kill portal drop. Restored from 04_recovered/Scenes/Pickups/Portal and
## ported to Godot 4 (P4-B C1 real loot chain). Mob._on_death instantiates this
## scene when a level boss dies (or the 250-kill stage milestone is hit).
##
## Asset boundary: sprites/environment/portal.png is still missing from
## product/ (art lane). The portal visual is procedural in the meantime:
## an olive particle swirl (ported from the legacy ParticlesMaterial) over the
## effects/shadow.png blob. Drop portal.png back under its original path to
## restore the painted art.

var death_screen = preload("res://scenes/Popups/DeathScreen.tscn")
var confirm = preload("res://scenes/Popups/Dialogs/TintedConfirmationDialog.tscn")


func on_pickup() -> void :
				var popup := confirm.instantiate()
				popup.title = "Return to Hideout?"
				popup.connect("confirmed", Callable(self, "_on_confirm"))
				add_child(popup)
				popup.popup_centered()


func _on_confirm() -> void :
				var instance := death_screen.instantiate()
				var world: Node = get_tree().get_root().get_node_or_null("World")
				if world != null:
								PopupManager.show_popup(instance, world)
