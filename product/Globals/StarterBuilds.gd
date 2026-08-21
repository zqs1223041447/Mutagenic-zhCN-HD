extends Node


var templates = {
				"lightning": {
								"name": "Lightning Starter", 
								"description": "Deal massive damage with Lightning Skills.", 
								"loadout": {
												"primary": {
																"skill": "ShockOrb", 
																"supports": {"a": "fast_hands", "b": "quicker_projectiles", "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"secondary": {
																"skill": "Rush", 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_one": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_two": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_three": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_four": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
								}
				}, 
				"fire": {
								"name": "Fire Starter", 
								"description": "Set enemies on fire with Fire Skills", 
								"loadout": {
												"primary": {
																"skill": "Orb", 
																"supports": {"a": "extra_projectiles", "b": "extra_pierce", "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"secondary": {
																"skill": "FlameTether", 
																"supports": {"a": "area_mastery", "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_one": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_two": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_three": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_four": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
								}
				}, 
				"cold": {
								"name": "Cold Starter", 
								"description": "Freeze your enemies with Cold Skills.", 
								"loadout": {
												"primary": {
																"skill": "ShardOrb", 
																"supports": {"a": "collateral_damage", "b": "enhanced_ailments", "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"secondary": {
																"skill": "Regeneration", 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_one": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_two": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_three": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_four": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
								}, 
				}, 

				
				"gunner": {
								"name": "Gunner", 
								"description": "Mow down enemies with a machine gun.", 
								"loadout": {
												"primary": {
																"skill": "Minigun", 
																"supports": {"a": "extra_pierce", "b": "extra_projectiles", "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"secondary": {
																"skill": "Rush", 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_one": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_two": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_three": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_four": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
								}
				}, 

				"shotgun": {
								"name": "Destroyer", 
								"description": "Blast down enemies with a powerful shotgun.", 
								"loadout": {
												"primary": {
																"skill": "Shotgun", 
																"supports": {"a": "extra_pierce", "b": "sacrifice", "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"secondary": {
																"skill": "Regeneration", 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_one": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_two": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_three": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_four": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
								}
				}, 

				"archer": {
								"name": "Bleed Archer", 
								"description": "Damage enemies with a powerful bow attack.", 
								"loadout": {
												"primary": {
																"skill": "Arrow", 
																"supports": {"a": "physical_ailment", "b": "physical_ailment_effect", "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"secondary": {
																"skill": "DoTAura", 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_one": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_two": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_three": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
												"support_four": {
																"skill": null, 
																"supports": {"a": null, "b": null, "c": null, "d": null, "e": null, "f": null}, 
												}, 
								}
				}
}

var DEFAULT = ["lightning", "cold", "fire"]

var templates_for_class = {
				PlayableClasses.PLAYABLE_CLASSES.WARRIOR: ["lightning", "cold", "fire"], 
				PlayableClasses.PLAYABLE_CLASSES.TANK: ["lightning", "cold", "fire"], 
				PlayableClasses.PLAYABLE_CLASSES.MAGE: ["lightning", "cold", "fire"], 
				PlayableClasses.PLAYABLE_CLASSES.ROGUE: ["gunner", "shotgun", "archer"], 
}

func get_starters_for_class(c):
				if templates_for_class.has(c):
								return templates_for_class[c]
				return DEFAULT

