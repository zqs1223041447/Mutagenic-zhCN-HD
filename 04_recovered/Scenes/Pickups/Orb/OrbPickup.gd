extends Pickup

var collect_sound = preload("res://Sounds/Pickups/collect_orb.wav")
var help_tip = preload("res://Scenes/Popups/Dialogs/HelpTip/OrbHelp/OrbTip.tscn")


onready var button = $Node2D / VBoxContainer / HBoxContainer / HBoxContainer / Button
onready var sprite = $Sprite
onready var animated_sprite = $AnimatedSprite
onready var player = GameState.get_global("player")

var orb_type
var zone_level
var amount = 1
var quantity_multiplier = 1.0

func _ready():
				var roll = randf()
				if roll < 0.7:
								orb_type = Constants.OrbType.BLUE
				elif roll < 0.9:
								orb_type = Constants.OrbType.GREEN
				elif roll < 0.97:
								orb_type = Constants.OrbType.RED
				else:
								orb_type = Constants.OrbType.GOLD

				var max_amount = ceil(sqrt(zone_level))

				
				if zone_level >= 100 and randf() < 0.025:
								orb_type = Constants.OrbType.CORRUPTION
								max_amount = 1

				Globals.play_orb_sound(orb_type)

				amount = floor(max(1, round(rand_range(1, max_amount))) * quantity_multiplier)
				animated_sprite.frames = OrbTypes.animation_for_orb[orb_type]
				if amount == 1:
								button.text = Constants.OrbName[orb_type]
				else:
								button.text = str(amount) + "x " + Constants.OrbName[orb_type]

				if orb_type == Constants.OrbType.CORRUPTION:
								button.set("custom_colors/font_color", Colors.corruption)

func on_pickup():
				player.stats.add_orb(orb_type, amount)
				Globals.play_sound_effect(collect_sound, "Drops")
				if not GameState.is_help_tip_read("orb_pickup"):
								GameState.mark_help_tip_read("orb_pickup")
								var popup = help_tip.instance()
								PopupManager.show_popup(popup, get_tree().get_root().get_node("World"))
