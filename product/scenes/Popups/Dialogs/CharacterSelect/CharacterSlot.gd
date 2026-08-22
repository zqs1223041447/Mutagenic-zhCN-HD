extends HBoxContainer

var confirm_dialog = preload("res://scenes/Popups/Dialogs/TintedConfirmationDialog.tscn")

var character_name
var save_stats


func _ready():
				save_stats = GameState.saved_stats.characters[character_name]
				render()

func render():
				$VBoxContainer/NameLabel.text = save_stats.character_name
				$VBoxContainer/LevelLabel.text = "Level: " + str(save_stats.account_level)
				var cn = PlayableClasses.get_class_name(save_stats.mutation_tree_loadout. class , save_stats.specialization_loadout. class )
				$VBoxContainer/ClassLabel.text = cn

				var helmet = Outfits.get_helmet(save_stats)
				$Viewport/BodyParts/PantsAttachment/HeadAttachment/HelmetSprite.frames = helmet
				var head = Outfits.get_head(save_stats)
				$Viewport/BodyParts/PantsAttachment/HeadAttachment/HeadSprite.frames = head
				var pants = Outfits.get_pants(save_stats)
				$Viewport/BodyParts/PantsAttachment/PantsSprite.frames = pants
				var hands = Outfits.get_hands(save_stats)
				$Viewport/BodyParts/PantsAttachment/LeftHand/Hand.frames = hands
				$Viewport/BodyParts/PantsAttachment/RightHand/Hand.frames = hands
				var feet = Outfits.get_feet(save_stats)
				$Viewport/BodyParts/PantsAttachment/LeftFoot/Foot.frames = feet
				$Viewport/BodyParts/PantsAttachment/RightFoot/Foot.frames = feet
				var back = Outfits.get_back(save_stats)
				$Viewport/BodyParts/PantsAttachment/BackSprite.frames = back

func _on_Button_pressed() -> void :
				Globals.selected_character_name = character_name
				Globals.selected_level = "hideout"
				get_tree().change_scene_to_file("res://scenes/World.tscn")

func focus():
				$HBoxContainer/VBoxContainer/Button.grab_focus()

func _on_DeleteButton_pressed() -> void :
				var popup = confirm_dialog.instantiate()
				popup.window_title = "Permanently Delete this Character?"
				popup.connect("confirmed", Callable(self, "_on_delete_character"))
				add_child(popup)
				popup.popup_centered()

func _on_delete_character():
				print("CONFIRMED DELETE")
				GameState.delete_character(character_name)
