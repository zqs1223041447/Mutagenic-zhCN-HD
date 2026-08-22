extends VBoxContainer

var tier_group = preload("res://scenes/Popups/Dialogs/ModHelp/TierGroup.tscn")

var base_type

func _ready() -> void :
				name = Genes.name_for_base_type[base_type]
				var label = Label.new()
				label.align = HORIZONTAL_ALIGNMENT_CENTER
				label.text = "Available Affixes"
				add_child(label)
				var mods = Genes.mods_for_base_type(base_type)
				var tiers = mods.get_explicit_tiers()
				for mod in tiers:
								if mod.unique:
												continue
								var group = tier_group.instantiate()
								group.mod = mod
								add_child(group)


				label = Label.new()
				label.align = HORIZONTAL_ALIGNMENT_CENTER
				label.text = "Drop Only Mods"
				add_child(label)
				mods = Genes.drop_only_mods_for_base_type(base_type)
				tiers = mods.get_explicit_tiers()
				for mod in tiers:
								if mod.unique:
												continue
								var group = tier_group.instantiate()
								group.mod = mod
								add_child(group)
