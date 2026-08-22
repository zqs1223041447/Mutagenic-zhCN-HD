extends "res://scenes/Pickups/Pickup.gd"
## Orb ground drop. Restored from 04_recovered/Scenes/Pickups/Orb and ported
## to Godot 4 (P4-B C1 real loot chain). Mob._on_death instantiates this scene
## for elite kills and orb-drop rolls; the credit path is Stats.add_orb.
##
## Asset boundary (ART_SOURCE_POLICY): collect_orb.wav and the aseprite orb
## animations are waived/missing from product/. They are resolved through
## ResourceLoader.exists()/null-safe lookups so loot logic never depends on
## them; drop the assets back under the same paths to re-enable sound/animation.

const ORB_TIP_SCENE := "res://scenes/Popups/Dialogs/HelpTip/OrbHelp/OrbTip.tscn"
const COLLECT_SOUND := "res://Sounds/Pickups/collect_orb.wav"

@onready var button: Button = $Node2D/VBoxContainer/HBoxContainer/HBoxContainer/Button
@onready var sprite: Sprite2D = $Sprite
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite

var orb_type = null
var zone_level = 1
var amount = 1
var quantity_multiplier = 1.0

var collect_sound: AudioStream = null
var help_tip: PackedScene = null


func _ready() -> void :
				if ResourceLoader.exists(COLLECT_SOUND):
								collect_sound = load(COLLECT_SOUND)
				if ResourceLoader.exists(ORB_TIP_SCENE):
								help_tip = load(ORB_TIP_SCENE)

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

				amount = floor(max(1, round(randf_range(1, max_amount))) * quantity_multiplier)
				render_orb_visual()

				if amount == 1:
								button.text = Constants.OrbName[orb_type]
				else:
								button.text = str(amount) + "x " + Constants.OrbName[orb_type]

				if orb_type == Constants.OrbType.CORRUPTION:
								button.add_theme_color_override("font_color", Colors.corruption)
				else:
								button.add_theme_color_override("font_color", Colors.unique_description)


func render_orb_visual() -> void :
				
				
				var frames: SpriteFrames = OrbTypes.animation_for_orb.get(orb_type)
				if frames != null:
								animated_sprite.sprite_frames = frames
								animated_sprite.play("default")
								return

				
				animated_sprite.visible = false
				var tex: Texture2D = OrbTypes.texture_for_orb.get(orb_type)
				if tex != null:
								sprite.texture = tex
								sprite.visible = true


func on_pickup() -> void :
				var player = GameState.get_global("player")
				if player != null and player.get("stats") != null:
								player.stats.add_orb(orb_type, amount)
				if collect_sound != null:
								Globals.play_sound_effect(collect_sound, "Drops")
				if not GameState.is_help_tip_read("orb_pickup"):
								GameState.mark_help_tip_read("orb_pickup")
								if help_tip != null:
												var popup := help_tip.instantiate()
												var world: Node = get_tree().get_root().get_node_or_null("World")
												if world != null:
																PopupManager.show_popup(popup, world)
