extends VBoxContainer

var mod
var searchable_string = ""


func _ready() -> void :
				if mod.has("affix_type"):
								if mod.affix_type == Constants.ModType.PREFIX:
												$AffixType.text = "Prefix"
								elif mod.affix_type == Constants.ModType.SUFFIX:
												$AffixType.text = "Suffix"
								elif mod.affix_type == Constants.ModType.IMPLICIT:
												$AffixType.text = "Implicit"
								else:
												$AffixType.text = "Unknown"
				else:
								$AffixType.visible = false

				if mod.has("keystone"):
								$StatName.text = Keystones.keystones[mod.keystone].name + "\n" + Keystones.keystones[mod.keystone].description
								searchable_string = Keystones.keystones[mod.keystone].name + " " + Keystones.keystones[mod.keystone].description
								searchable_string = searchable_string.to_lower()
								$Tiers.visible = false
				else:
								var tags = []
								if mod.has("tags") and len(mod.tags) > 0:
												tags = mod.tags
								var text = StatsInfo.render_stat_name(mod.stat, mod.type, tags)
								$StatName.text = text
								searchable_string = text.to_lower()
								if mod.affix_type == Constants.ModType.PREFIX:
												searchable_string += " prefix "
								elif mod.affix_type == Constants.ModType.SUFFIX:
												searchable_string += " suffix "
								elif mod.affix_type == Constants.ModType.IMPLICIT:
												searchable_string += " implicit "

								if mod.drop_only:
												searchable_string += " drop only"
								$Tiers.visible = true
								for tier in mod.tiers:
												var label = get_tier_label(tier)
												$Tiers.add_child(label)

				$HBoxContainer / WeightLabel.text = str(mod.weight)

				Globals.connect("search_changed", self, "_search_changed")
				_search_changed(Globals.search_string)


func get_tier_label(tier):
				
				var label = Label.new()
				label.text = "Mod Level " + str(tier.tier) + " (" + str(tier.chance) + "%) (Minimum Drop Level: " + \
				str(tier.level_requirement) + "): " + tier.range.min_formatted + " - " + tier.range.max_formatted
				return label


func _search_changed(search_string):
				if not search_string or len(search_string) <= 1:
								visible = true
								return

				if search_string in searchable_string:
								visible = true
				else:
								visible = false
