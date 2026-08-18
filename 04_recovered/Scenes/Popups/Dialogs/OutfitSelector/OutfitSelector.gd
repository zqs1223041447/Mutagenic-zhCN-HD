extends PopupBase

var outfit_option = preload("res://Scenes/Popups/Dialogs/OutfitSelector/OutfitOption.tscn")

onready var tab_container = $CenterContainer / PanelContainer / VBoxContainer / HBoxContainer

func _ready():
				for item in Outfits.helmets:
								var option = outfit_option.instance()
								option.slot = "helmet"
								option.outfit_name = item
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Helmets / ScrollContainer / HBoxContainer / Helmets.add_child(option)
				for item in Outfits.heads:
								var option = outfit_option.instance()
								option.slot = "head"
								option.outfit_name = item
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Faces / ScrollContainer / HBoxContainer / Heads.add_child(option)
				for item in Outfits.hands:
								var option = outfit_option.instance()
								option.slot = "hands"
								option.outfit_name = item
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Gloves / ScrollContainer / HBoxContainer / Hands.add_child(option)
				for item in Outfits.pants:
								var option = outfit_option.instance()
								option.slot = "pants"
								option.outfit_name = item
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Body / ScrollContainer / HBoxContainer / Pants.add_child(option)
				for item in Outfits.feet:
								var option = outfit_option.instance()
								option.slot = "feet"
								option.outfit_name = item
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Boots / ScrollContainer / HBoxContainer / Feet.add_child(option)
				for item in Outfits.back:
								var option = outfit_option.instance()
								option.slot = "back"
								option.outfit_name = item
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Back / ScrollContainer / HBoxContainer / Back.add_child(option)

				GameState.connect("outfit_changed", self, "_on_outfit_changed")
				tab_container.connect("tab_changed", self, "_on_tab_changed")

				_on_outfit_changed()
				_on_tab_changed(0)

func _physics_process(delta: float) -> void :
				if Input.is_action_just_pressed("ui_focus_next"):
								tab_container.current_tab = (tab_container.current_tab + 1) % tab_container.get_tab_count()
				if Input.is_action_just_pressed("ui_focus_prev"):
								tab_container.current_tab = (tab_container.current_tab - 1 + tab_container.get_tab_count()) % tab_container.get_tab_count()

func _on_tab_changed(active_tab):
				if active_tab == 0:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Helmets / ScrollContainer / HBoxContainer / Helmets.get_child(0).grab_focus()
				if active_tab == 1:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Faces / ScrollContainer / HBoxContainer / Heads.get_child(0).grab_focus()
				if active_tab == 2:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Gloves / ScrollContainer / HBoxContainer / Hands.get_child(0).grab_focus()
				if active_tab == 3:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Body / ScrollContainer / HBoxContainer / Pants.get_child(0).grab_focus()
				if active_tab == 4:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Boots / ScrollContainer / HBoxContainer / Feet.get_child(0).grab_focus()
				if active_tab == 5:
								$CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / Back / ScrollContainer / HBoxContainer / Back.get_child(0).grab_focus()


func _on_outfit_changed():
				var helmet = Outfits.get_helmet()
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / HeadAttachment / HelmetSprite.frames = helmet
				var head = Outfits.get_head()
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / HeadAttachment / HeadSprite.frames = head
				var pants = Outfits.get_pants()
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / PantsSprite.frames = pants
				var hands = Outfits.get_hands()
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / LeftHand / Hand.frames = hands
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / RightHand / Hand.frames = hands
				var feet = Outfits.get_feet()
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / LeftFoot / Foot.frames = feet
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / RightFoot / Foot.frames = feet
				var back = Outfits.get_back()
				$CenterContainer / PanelContainer / VBoxContainer / PlayerRenderer / Viewport / BodyParts / PantsAttachment / BackSprite.frames = back


func _on_Button_pressed() -> void :
				PopupManager.pop_popup()
