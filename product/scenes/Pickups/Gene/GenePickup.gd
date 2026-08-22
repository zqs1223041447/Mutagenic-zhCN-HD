extends "res://scenes/Pickups/Pickup.gd"
## Gene ground drop. Restored from 04_recovered/Scenes/Pickups/Gene and
## ported to Godot 4 (P3-D E6 loot loop). Mob._on_death (scenes/Mobs/Mob.gd)
## instantiates this scene when a gene drop rolls.
##
## Asset boundary: drop_only.wav, gene_unique.png and the GeneTip help popup
## are still missing from product/ (art/content lane). They are resolved with
## ResourceLoader.exists() guards so loot logic never depends on them; add
## them back under the same paths to re-enable sound/skin/popup.

@onready var gene_info: Node = $Node2D/VBoxContainer/InfoContainer/GeneInfo
@onready var button: Button = $Node2D/VBoxContainer/HBoxContainer/HBoxContainer/Button
@onready var sprite: Sprite2D = $Sprite
@onready var glow: Sprite2D = $Glow

var gene
var zone_level
var always_rare := false
var rarity_bonus := 0.0
var unique_pools = null

var drop_only_sound: AudioStream = null
var unique_gene_sprite: Texture2D = null
var help_tip: PackedScene = null


func _ready() -> void:
	if ResourceLoader.exists("res://Sounds/Pickups/drop_only.wav"):
		drop_only_sound = load("res://Sounds/Pickups/drop_only.wav")
	if ResourceLoader.exists("res://sprites/_mapped/ui/gene_unique.png"):
		unique_gene_sprite = load("res://sprites/_mapped/ui/gene_unique.png")
	if ResourceLoader.exists("res://scenes/Popups/Dialogs/HelpTip/GeneTip/GeneTip.tscn"):
		help_tip = load("res://scenes/Popups/Dialogs/HelpTip/GeneTip/GeneTip.tscn")

	gene = GeneGenerator.generate_random_gene(zone_level, rarity_bonus, always_rare, unique_pools)
	gene_info.render(gene)

	button.text = gene.name

	if gene.has("quality") and gene.quality > 0:
		button.text += " (" + str(gene.quality) + "%)"

	if gene.unique:
		if drop_only_sound != null:
			Globals.play_sound_effect(drop_only_sound, "Drops")
		var unique_info: Variant = UniqueGenes.get_unique_data(gene.unique_id)
		if unique_info != null and unique_info.has("texture"):
			sprite.texture = unique_info.texture
		elif unique_gene_sprite != null:
			sprite.texture = unique_gene_sprite
		button.add_theme_color_override("font_color", Colors.rarity.unique)
		glow.visible = true
	else:
		var tex: Texture2D = Genes.texture_for_base_type(gene.type)
		if tex != null:
			sprite.texture = tex

		var affix_count: int = len(gene.suffixes) + len(gene.prefixes)

		if affix_count <= 2:
			button.add_theme_color_override("font_color", Colors.rarity.magic)
		else:
			button.add_theme_color_override("font_color", Colors.rarity.rare)

		var drop_only_count := 0
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
			if drop_only_sound != null:
				Globals.play_sound_effect(drop_only_sound, "Drops")
			glow.visible = true
			if drop_only_count == 1:
				glow.modulate = Colors.drop_only_1
			if drop_only_count == 2:
				glow.modulate = Colors.drop_only_2
			if drop_only_count == 3:
				glow.modulate = Colors.drop_only_3

	var type_name: String = Genes.name_for_base_type[gene.type]
	$Node2D/VBoxContainer/HBoxContainer/TypeLabel.text = type_name


func on_pickup() -> void:
	Genes.pickup_gene(gene)
	if not GameState.is_help_tip_read("gene_pickup"):
		GameState.mark_help_tip_read("gene_pickup")
		if help_tip != null:
			var popup := help_tip.instantiate()
			var world: Node = get_tree().get_root().get_node_or_null("World")
			if world != null:
				PopupManager.show_popup(popup, world)
