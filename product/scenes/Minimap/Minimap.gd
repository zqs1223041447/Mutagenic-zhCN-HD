extends CanvasLayer

var mod_label = preload("res://scenes/Minimap/MinimapModLabel.tscn")

@onready var level = GameState.get_global("level_scene")
@onready var player = GameState.get_global("player")
@onready var texture_rect = $MinimapContainer/TextureRect
@onready var mod_list = $PanelContainer/ModList

var image: Image
var image_texture: ImageTexture

var offset_x
var offset_y
const IMAGE_PADDING = 80

func _ready() -> void :
				level.connect("map_done", Callable(self, "_render_map"))
				MapMods.connect("mods_changed", Callable(self, "_render_mods"))
				_render_mods()

func _render_mods():
				for mod in mod_list.get_children():
								mod.queue_free()

				var mods = MapMods.get_map_mods()

				if len(mods) > 0 or Levels.is_current_level_hideout():
								var label = Label.new()
								label.text = "Zone Mods"
								label.align = HORIZONTAL_ALIGNMENT_RIGHT
								mod_list.add_child(label)
								$PanelContainer.visible = true
				else:
								$PanelContainer.visible = false

				for mod in mods:
								var text = MapMods.render_stat(mod)
								var label = mod_label.instantiate()
								label.text = text
								label.align = HORIZONTAL_ALIGNMENT_RIGHT
								mod_list.add_child(label)

				if Levels.is_current_level_hideout():
								var label = mod_label.instantiate()
								label.text = "Players have 25% More Movement Speed"
								label.align = HORIZONTAL_ALIGNMENT_RIGHT
								mod_list.add_child(label)

				if Globals.stage_iiq > 0.0:
								var label = mod_label.instantiate()
								label.text = str(snapped(Globals.stage_iiq * 100.0, 1)) + "% Increased Quantity of Items Found"
								label.align = HORIZONTAL_ALIGNMENT_RIGHT
								mod_list.add_child(label)
								$PanelContainer.visible = true

				if Globals.stage_iir > 0.0:
								var label = mod_label.instantiate()
								label.text = str(snapped(Globals.stage_iir * 100.0, 1)) + "% Increased Rarity of Items Found"
								label.align = HORIZONTAL_ALIGNMENT_RIGHT
								mod_list.add_child(label)
								$PanelContainer.visible = true

func _render_map():
				var bounds = level.get_bounds()

				var width = bounds[2] - bounds[0] + 1
				var height = bounds[3] - bounds[1] + 1

				var size = Vector2(width, height)

				if width > 0 and height > 0:
								image = Image.new()
								image.create(width + IMAGE_PADDING, height + IMAGE_PADDING, false, Image.FORMAT_RGBA8)

								offset_x = bounds[0]
								offset_y = bounds[1]

								
								image.lock()
								for i in range(width):
												for j in range(height):
																if level.is_spawnable_tile(i + offset_x, j + offset_y):
																				image.set_pixel(IMAGE_PADDING + i, IMAGE_PADDING + j, Color(1, 1, 1, 0.7))
								image.unlock()

								image_texture = ImageTexture.new()
								image_texture.create_from_image(image, 0)
								texture_rect.initialize()


func render_portal(x_pixel, y_pixel):
				var x_step = level.tiles.cell_size.x
				var y_step = level.tiles.cell_size.y
				var x = round(x_pixel / x_step)
				var y = round(y_pixel / y_step)
				image.lock()
				for i in [ - 1, 0, 1]:
								for j in [ - 1, 0, 1]:
												if i == 0 and j == 0:
																continue
												image.set_pixel(IMAGE_PADDING + x - offset_x + i, IMAGE_PADDING + y - offset_y + j, Color.BLUE)
				image.unlock()
				image_texture.create_from_image(image, 0)
