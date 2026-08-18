extends Pickup

var drop_only_sound = preload("res://Sounds/Pickups/drop_only.wav")

var offensive_gene_sprite = preload("res://sprites/gui/gene_offensive.png")
var defensive_gene_sprite = preload("res://sprites/gui/gene_defensive.png")
var utility_gene_sprite = preload("res://sprites/gui/gene_utility.png")
var lesser_gene_sprite = preload("res://sprites/gui/gene_lesser.png")
var unique_gene_sprite = preload("res://sprites/gui/gene_unique.png")
var help_tip = preload("res://Scenes/Popups/Dialogs/HelpTip/GeneTip/GeneTip.tscn")

var important_sprite = preload("res://sprites/gui/important.png")

onready var gene_info = $Node2D / VBoxContainer / InfoContainer / GeneInfo
onready var button = $Node2D / VBoxContainer / HBoxContainer / HBoxContainer / Button
onready var sprite = $Sprite
var gene
var zone_level
var always_rare = false
var rarity_bonus = 0.0
var unique_pools = null

func _ready():
				gene = GeneGenerator.generate_random_gene(zone_level, rarity_bonus, always_rare, unique_pools)
				gene_info.render(gene)

				button.text = gene.name

				if gene.has("quality") and gene.quality > 0:
								button.text += " (" + str(gene.quality) + "%)"

				if gene.unique:
								Globals.play_sound_effect(drop_only_sound, "Drops")
								var unique_info = UniqueGenes.get_unique_data(gene.unique_id)
								if unique_info.has("texture"):
												sprite.texture = unique_info.texture
								else:
												sprite.texture = unique_gene_sprite
								button.set("custom_colors/font_color", Colors.rarity.unique)
								$Glow.visible = true
				else:
								sprite.texture = Genes.texture_for_base_type(gene.type)

								var affix_count = len(gene.suffixes) + len(gene.prefixes)

								if affix_count <= 2:
												button.set("custom_colors/font_color", Colors.rarity.magic)
								else:
												button.set("custom_colors/font_color", Colors.rarity.rare)

								var drop_only_count = 0
								for affix in gene.implicits:
												if affix.has("drop_only") and affix.drop_only:
																drop_only_count += 1
								for affix in gene.suffixes:
												if affix.has("drop_only") and affix.drop_only:
																drop_only_count += 1
								for affix in gene.prefixes:
												if affix.has("drop_only") and affix.drop_only:
																drop_only_count += 1

								if drop_only_count > 0:
												Globals.play_sound_effect(drop_only_sound, "Drops")
												$Glow.visible = true
												if drop_only_count == 1:
																$Glow.modulate = Colors.drop_only_1
												if drop_only_count == 2:
																$Glow.modulate = Colors.drop_only_2
												if drop_only_count == 3:
																$Glow.modulate = Colors.drop_only_3

				var type_name = Genes.name_for_base_type[gene.type]
				$Node2D / VBoxContainer / HBoxContainer / TypeLabel.text = type_name


func on_pickup():
				Genes.pickup_gene(gene)
				if not GameState.is_help_tip_read("gene_pickup"):
								GameState.mark_help_tip_read("gene_pickup")
								var popup = help_tip.instance()
								PopupManager.show_popup(popup, get_tree().get_root().get_node("World"))
