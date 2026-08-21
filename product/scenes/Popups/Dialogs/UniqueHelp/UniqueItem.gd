extends VBoxContainer

var mod_range = preload("res://scenes/Popups/Dialogs/UniqueHelp/UniqueModRange.tscn")

var unique_id


func _ready():
				
				var data = UniqueGenes.all_uniques[unique_id]

				if data:
								$HBoxContainer/TextureRect.texture = data.texture
								if data.has("flavor"):
												$Description.text = data.flavor
								$Name.text = data.name

								var base_name = Genes.name_for_base_type[data.type]
								$Basename.text = base_name

								$DropLevel.text = "Minimum Drop Level: " + str(data.min_level_requirement)

								for affix in data.prefixes:
												var mod_id = affix.mod_id
												var item = mod_range.instantiate()
												item.mod_id = mod_id
												item.base_type = data.type
												$Stats.add_child(item)

								for affix in data.suffixes:
												var mod_id = affix.mod_id
												var item = mod_range.instantiate()
												item.mod_id = mod_id
												item.base_type = data.type
												$Stats.add_child(item)

