extends Node


var head_default = load("res://sprites/player/heads/default.aseprite")
var head_mutant = load("res://sprites/player/heads/mutant.aseprite")
var head_robot = load("res://sprites/player/heads/robot.aseprite")
var head_dragon = load("res://sprites/player/heads/dragon.aseprite")
var head_fire = load("res://sprites/player/heads/fire.aseprite")
var head_vampire = load("res://sprites/player/heads/vampire.aseprite")
var head_skull = load("res://sprites/player/heads/skull.aseprite")
var head_chiller = load("res://sprites/player/heads/chiller.aseprite")
var head_zombie = load("res://sprites/player/heads/zombie.aseprite")


var helmet_flame = load("res://sprites/player/helmets/flame_helmet.aseprite")
var helmet_iron = load("res://sprites/player/helmets/iron.aseprite")
var helmet_horned = load("res://sprites/player/helmets/horned.aseprite")
var helmet_crown = load("res://sprites/player/helmets/crown.aseprite")
var helmet_fire = load("res://sprites/player/helmets/fire.aseprite")
var helmet_top_hat = load("res://sprites/player/helmets/top_hat.aseprite")
var helmet_ninja = load("res://sprites/player/helmets/ninja.aseprite")


var feet_default = load("res://sprites/player/feet/default.aseprite")
var feet_flaming = load("res://sprites/player/feet/flame_boots.aseprite")
var feet_frozen = load("res://sprites/player/feet/frozen_boots.aseprite")
var feet_mutant = load("res://sprites/player/feet/mutant.aseprite")
var feet_claws = load("res://sprites/player/feet/claws.aseprite")
var feet_golden = load("res://sprites/player/feet/golden.aseprite")
var feet_glow = load("res://sprites/player/feet/glow.aseprite")
var feet_hoof = load("res://sprites/player/feet/hoof.aseprite")


var pants_default = load("res://sprites/player/pants/default.aseprite")
var pants_winged = load("res://sprites/player/pants/wings.aseprite")
var pants_dragon = load("res://sprites/player/pants/dragon.aseprite")
var pants_coal = load("res://sprites/player/pants/coal.aseprite")
var pants_emerald = load("res://sprites/player/pants/emerald.aseprite")
var pants_fire = load("res://sprites/player/pants/fire.aseprite")
var pants_golden = load("res://sprites/player/pants/golden.aseprite")
var pants_ninja = load("res://sprites/player/pants/ninja.aseprite")
var pants_zombie = load("res://sprites/player/pants/zombie.aseprite")


var hands_default = load("res://sprites/player/hands/default.aseprite")
var hands_wands = load("res://sprites/player/hands/wands.aseprite")
var hands_knife = load("res://sprites/player/hands/knife.aseprite")
var hands_swords = load("res://sprites/player/hands/swords.aseprite")
var hands_icicles = load("res://sprites/player/hands/icicles.aseprite")
var hands_chains = load("res://sprites/player/hands/chains.aseprite")
var hands_orbs = load("res://sprites/player/hands/orbs.aseprite")
var hands_guns = load("res://sprites/player/hands/guns.aseprite")
var hands_blades = load("res://sprites/player/hands/blades.aseprite")
var hands_spear = load("res://sprites/player/hands/spear.aseprite")


var back_dragon_wings = load("res://sprites/player/back/dragon_wings.aseprite")
var back_pixie_wings = load("res://sprites/player/back/pixie_wings.aseprite")
var back_cape = load("res://sprites/player/back/ninja_cape.aseprite")
var back_demon = load("res://sprites/player/back/demon_wings.aseprite")
var back_thrusters = load("res://sprites/player/back/thrusters.aseprite")
var back_poison = load("res://sprites/player/back/poison.aseprite")
var back_bloody = load("res://sprites/player/back/bloody.aseprite")
var back_tail = load("res://sprites/player/back/tail.aseprite")

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
