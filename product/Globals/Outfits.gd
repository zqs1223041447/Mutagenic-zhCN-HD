extends Node


var head_default = load("res://sprites/_acquired/generated_spriteframes/actors/default.spriteframes.tres")
var head_mutant = load("res://sprites/_acquired/generated_spriteframes/actors/mutant.spriteframes.tres")
var head_robot = load("res://sprites/_acquired/generated_spriteframes/actors/robot.spriteframes.tres")
var head_dragon = load("res://sprites/_acquired/generated_spriteframes/actors/dragon.spriteframes.tres")
var head_fire = load("res://sprites/_acquired/generated_spriteframes/actors/fire.spriteframes.tres")
var head_vampire = load("res://sprites/_acquired/generated_spriteframes/actors/vampire.spriteframes.tres")
var head_skull = load("res://sprites/_acquired/generated_spriteframes/actors/skull.spriteframes.tres")
var head_chiller = load("res://sprites/_acquired/generated_spriteframes/actors/chiller.spriteframes.tres")
var head_zombie = load("res://sprites/_acquired/generated_spriteframes/actors/zombie.spriteframes.tres")


var helmet_flame = load("res://sprites/_acquired/generated_spriteframes/actors/flame_helmet.spriteframes.tres")
var helmet_iron = load("res://sprites/_acquired/generated_spriteframes/actors/iron.spriteframes.tres")
var helmet_horned = load("res://sprites/_acquired/generated_spriteframes/actors/horned.spriteframes.tres")
var helmet_crown = load("res://sprites/_acquired/generated_spriteframes/actors/crown.spriteframes.tres")
var helmet_fire = load("res://sprites/_acquired/generated_spriteframes/actors/fire.spriteframes.tres")
var helmet_top_hat = load("res://sprites/_acquired/generated_spriteframes/actors/top_hat.spriteframes.tres")
var helmet_ninja = load("res://sprites/_acquired/generated_spriteframes/actors/ninja.spriteframes.tres")


var feet_default = load("res://sprites/_acquired/generated_spriteframes/actors/default.spriteframes.tres")
var feet_flaming = load("res://sprites/_acquired/generated_spriteframes/actors/flame_boots.spriteframes.tres")
var feet_frozen = load("res://sprites/_acquired/generated_spriteframes/actors/frozen_boots.spriteframes.tres")
var feet_mutant = load("res://sprites/_acquired/generated_spriteframes/actors/mutant.spriteframes.tres")
var feet_claws = load("res://sprites/_acquired/generated_spriteframes/actors/claws.spriteframes.tres")
var feet_golden = load("res://sprites/_acquired/generated_spriteframes/actors/golden.spriteframes.tres")
var feet_glow = load("res://sprites/_acquired/generated_spriteframes/actors/glow.spriteframes.tres")
var feet_hoof = load("res://sprites/_acquired/generated_spriteframes/actors/hoof.spriteframes.tres")


var pants_default = load("res://sprites/_acquired/generated_spriteframes/actors/default.spriteframes.tres")
var pants_winged = load("res://sprites/_acquired/generated_spriteframes/actors/wings.spriteframes.tres")
var pants_dragon = load("res://sprites/_acquired/generated_spriteframes/actors/dragon.spriteframes.tres")
var pants_coal = load("res://sprites/_acquired/generated_spriteframes/actors/coal.spriteframes.tres")
var pants_emerald = load("res://sprites/_acquired/generated_spriteframes/actors/emerald.spriteframes.tres")
var pants_fire = load("res://sprites/_acquired/generated_spriteframes/actors/fire.spriteframes.tres")
var pants_golden = load("res://sprites/_acquired/generated_spriteframes/actors/golden.spriteframes.tres")
var pants_ninja = load("res://sprites/_acquired/generated_spriteframes/actors/ninja.spriteframes.tres")
var pants_zombie = load("res://sprites/_acquired/generated_spriteframes/actors/zombie.spriteframes.tres")


var hands_default = load("res://sprites/_acquired/generated_spriteframes/actors/default.spriteframes.tres")
var hands_wands = load("res://sprites/_acquired/generated_spriteframes/actors/wands.spriteframes.tres")
var hands_knife = load("res://sprites/_acquired/generated_spriteframes/actors/knife.spriteframes.tres")
var hands_swords = load("res://sprites/_acquired/generated_spriteframes/actors/swords.spriteframes.tres")
var hands_icicles = load("res://sprites/_acquired/generated_spriteframes/actors/icicles.spriteframes.tres")
var hands_chains = load("res://sprites/_acquired/generated_spriteframes/actors/chains.spriteframes.tres")
var hands_orbs = load("res://sprites/_acquired/generated_spriteframes/actors/orbs.spriteframes.tres")
var hands_guns = load("res://sprites/_acquired/generated_spriteframes/actors/guns.spriteframes.tres")
var hands_blades = load("res://sprites/_acquired/generated_spriteframes/actors/blades.spriteframes.tres")
var hands_spear = load("res://sprites/_acquired/generated_spriteframes/actors/spear.spriteframes.tres")


var back_dragon_wings = load("res://sprites/_acquired/generated_spriteframes/actors/dragon_wings.spriteframes.tres")
var back_pixie_wings = load("res://sprites/_acquired/generated_spriteframes/actors/pixie_wings.spriteframes.tres")
var back_cape = load("res://sprites/_acquired/generated_spriteframes/actors/ninja_cape.spriteframes.tres")
var back_demon = load("res://sprites/_acquired/generated_spriteframes/actors/demon_wings.spriteframes.tres")
var back_thrusters = load("res://sprites/_acquired/generated_spriteframes/actors/thrusters.spriteframes.tres")
var back_poison = load("res://sprites/_acquired/generated_spriteframes/actors/poison.spriteframes.tres")
var back_bloody = load("res://sprites/_acquired/generated_spriteframes/actors/bloody.spriteframes.tres")
var back_tail = load("res://sprites/_acquired/generated_spriteframes/actors/tail.spriteframes.tres")

var helmets = {
				"default": null, 
				"flame": helmet_flame, 
				"iron": helmet_iron, 
				"horned": helmet_horned, 
				"crown": helmet_crown, 
				"fire": helmet_fire, 
				"top_hat": helmet_top_hat, 
				"ninja": helmet_ninja, 
}

var heads = {
				"default": head_default, 
				"mutant": head_mutant, 
				"robot": head_robot, 
				"dragon": head_dragon, 
				"fire": head_fire, 
				"vampire": head_vampire, 
				"skull": head_skull, 
				"chiller": head_chiller, 
				"zombie": head_zombie, 
}

var feet = {
				"default": feet_default, 
				"flame": feet_flaming, 
				"frozen": feet_frozen, 
				"mutant": feet_mutant, 
				"claws": feet_claws, 
				"golden": feet_golden, 
				"glow": feet_glow, 
				"hoof": feet_hoof, 
}

var hands = {
				"default": hands_default, 
				"wands": hands_wands, 
				"knife": hands_knife, 
				"swords": hands_swords, 
				"icicles": hands_icicles, 
				"chains": hands_chains, 
				"orbs": hands_orbs, 
				"guns": hands_guns, 
				"blades": hands_blades, 
				"spear": hands_spear, 
}

var back = {
				"default": null, 
				"dragon_wings": back_dragon_wings, 
				"pixie_wings": back_pixie_wings, 
				"cape": back_cape, 
				"demon": back_demon, 
				"thrusters": back_thrusters, 
				"poison": back_poison, 
				"bloody": back_bloody, 
				"tail": back_tail, 
}

var pants = {
				"default": pants_default, 
				"winged": pants_winged, 
				"dragon": pants_dragon, 
				"coal": pants_coal, 
				"emerald": pants_emerald, 
				"fire": pants_fire, 
				"golden": pants_golden, 
				"ninja": pants_ninja, 
				"zombie": pants_zombie, 
}


func get_helmet(stats = null):
				if not stats:
								stats = GameState.get_active_stats()
				if stats.outfit.helmet != null and helmets.has(stats.outfit.helmet):
								return helmets[stats.outfit.helmet]
				return helmets.default

func get_head(stats = null):
				if not stats:
								stats = GameState.get_active_stats()
				if stats.outfit.head != null and heads.has(stats.outfit.head):
								return heads[stats.outfit.head]
				return heads.default

func get_hands(stats = null):
				if not stats:
								stats = GameState.get_active_stats()
				if stats.outfit.hands != null and hands.has(stats.outfit.hands):
								return hands[stats.outfit.hands]
				return hands.default

func get_pants(stats = null):
				if not stats:
								stats = GameState.get_active_stats()
				if stats.outfit.pants != null and pants.has(stats.outfit.pants):
								return pants[stats.outfit.pants]
				return pants.default

func get_feet(stats = null):
				if not stats:
								stats = GameState.get_active_stats()
				if stats.outfit.feet != null and feet.has(stats.outfit.feet):
								return feet[stats.outfit.feet]
				return feet.default

func get_back(stats = null):
				if not stats:
								stats = GameState.get_active_stats()
				if stats.outfit.back != null and back.has(stats.outfit.back):
								return back[stats.outfit.back]
				return back.default

func get_outfit_in_slot(slot, outfit):
				if slot == "helmet":
								if helmets.has(outfit):
												return helmets[outfit]
				if slot == "head":
								if heads.has(outfit):
												return heads[outfit]
				if slot == "hands":
								if hands.has(outfit):
												return hands[outfit]
				if slot == "pants":
								if pants.has(outfit):
												return pants[outfit]
				if slot == "feet":
								if feet.has(outfit):
												return feet[outfit]
				if slot == "back":
								if back.has(outfit):
												return back[outfit]

				return null
