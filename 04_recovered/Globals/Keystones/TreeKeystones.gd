extends Node


var keystones = {
				"TREE_DETERIORATION": {
								"name": "Deterioration", 
								"description": "Skills have a 10% chance to apply Exposed on Hit"
				}, 
				"TREE_RAPID_DECAY": {
								"name": "Rapid Decay", 
								"description": "Poisons and Infections deal Damage 20% faster."
				}, 
				"TREE_PROJECTILE_SPEED_DAMAGE": {
								"name": "Impact Speed", 
								"description": "12% of Increased Projectile Speed also applies as More Projectile Damage"
				}, 
				"TREE_GOLIATH": {
								"name": "Goliath", 
								"description": "10% of Increased Maximum Life also applies as More Area Damage"
				}, 
				
				"TREE_PHANTOM_SHIELD": {
								"name": "Phantom Veil", 
								"description": "Every 3 seconds, gain a Phantom Shield up to a maximum of 1. When you will be hit, you instead avoid getting hit, consuming the Phantom Shield. Phantom Shields cannot block Damage over Time."
				}, 
				"TREE_REGENERATIVE_FLESH": {
								"name": "Regenerative Flesh", 
								"description": "Every 10 seconds, gain 20% Maximum Life Regenerated per Second for 1 seconds."
				}, 
				"TREE_VAMPIRIC_SKIN": {
								"name": "Vampiric Skin", 
								"description": "100% More Life Regeneration per Second if you've taken Damage in the past 5 seconds"
				}, 
				"TREE_CROCODILE_SKIN": {
								"name": "Crocodile Skin", 
								"description": "Take 90% Less Damage from hits if you have not been hit in the past 5 seconds."
				}, 
				"TREE_HARDENED_FLESH": {
								"name": "Hardened Flesh", 
								"description": "Take 10% Less Damage if you have been hit in the past 5 seconds."
				}, 
				"TREE_SPIKE_ARMOR": {
								"name": "Spiked Carapace", 
								"description": "Deal 20% More Damage if you've been hit in the past 5 seconds"
				}, 
				"TREE_DEFLECTING_ARMOR": {
								"name": "Deflecting Armor", 
								"description": "20% chance to avoid all Damage from hits"
				}, 
				"TREE_ADRENALINE": {
								"name": "Adrenaline", 
								"description": "Gain 25% More Movement Speed for 5 seconds when hit"
				}, 
				"TREE_ENDURANCE": {
								"name": "Endurance", 
								"description": "Gain 30% More Armor if you've been hit in the past 5 seconds"
				}, 
				"TREE_TOXICOLOGIST": {
								"name": "Toxicologist", 
								"description": "35% Less Damage taken from Damage over Time"
				}, 
				"TREE_BRICK": {
								"name": "Brick", 
								"description": "Take 15% Less Damage from Hits"
				}, 
				"TREE_LEECHER": {
								"name": "Leecher", 
								"description": "Recover 1% of Maximum Life when you kill an enemy."
				}, 
				"TREE_POTENTIAL_ENERGY": {
								"name": "Damage Capacitor", 
								"description": "Damage over Time does not deal Damage, but instead stores Damage as potential energy on the enemy. When the enemy is killed, 15% of stored Damage is released in a large explosion as Physical Damage around the enemy.", 
				}, 
				"TREE_INFECTIOUS_MALIGNANCY": {
								"name": "Infectious Malignancy", 
								"description": "Curses have 10% Less effect. Curses on enemies are spread to nearby enemies when they are killed"
				}, 
				"TREE_FRAGILE_CURSES": {
								"name": "Curse Fragility", 
								"description": "Curses have 50% Less Duration, but 30% More Curse Effect"
				}, 
				"TREE_IMPENDING_DEATH": {
								"name": "Marked for Death", 
								"description": "Enemies take 10% More Damage for each curse on them"
				}, 
				"TREE_CURSE_DURATION": {
								"name": "Prolonged Depression", 
								"description": "Curses have 50% More Duration"
				}, 
				"TREE_REPEATER": {
								"name": "Repeater", 
								"description": "Skills have 15% More Cast Speed. Duration skills have 30% Less Duration"
				}, 
				"TREE_RANGER": {
								"name": "Way of the Ranger", 
								"description": "Skills have 30% More Projectile Speed"
				}, 
				"TREE_MAGUS": {
								"name": "Way of the Magus", 
								"description": "Skills have 30% More Area of Effect"
				}, 
				"TREE_PIERCING_TRUTH": {
								"name": "Piercing Truth", 
								"description": "Skills pierce twice as many enemies"
				}, 
				"TREE_CYCLE": {
								"name": "Cyclic Destruction", 
								"description": "Every 5 seconds, switch between dealing 20% More Area Damage, and having 40% More Area of Effect"
				}, 
				"TREE_GROWING_PAIN": {
								"name": "Growing Pain", 
								"description": "30% More Area of Effect if you've killed in the past 5 seconds"
				}, 
				"TREE_QUICK_GETAWAY": {
								"name": "Quick Getaway", 
								"description": "Gain 25% Increased Movement Speed for 1 seconds when you are hit"
				}, 
				"TREE_CRYOMANCER": {
								"name": "Cryomancer", 
								"description": "Chills have 100% More Duration"
				}, 
				"TREE_CHARGED_FIELD": {
								"name": "Charged Field", 
								"description": "Nearby enemies take 30% More Damage"
				}, 
				"TREE_KINETIC_PROJECTILES": {
								"name": "Kinetic Projectiles", 
								"description": "Projectiles deal 30% More Damage. Projectiles always travel at their base speed", 
				}, 
				"TREE_GLASS_CANNON": {
								"name": "Glass Cannon", 
								"description": "65% Less Maximum Life, 10% More Cast Speed, 25% More Damage"
				}, 
				"TREE_TIME_WARP": {
								"name": "Time Warp", 
								"description": "Damage over Time deals damage 40% faster"
				}, 
				"TREE_RAGING_MOMENTUM": {
								"name": "Raging Momentum", 
								"description": "Deal 15% More Damage if you've killed in the past 5 seconds"
				}, 
				"TREE_PRECISION_STRIKES": {
								"name": "Precision Strikes", 
								"description": "Deal 25% More Damage to enemies inflicted with Vulnerable"
				}, 
				"TREE_TEMPERATURE_DELTAS": {
								"name": "Temperature Delta", 
								"description": "Chilled enemies take 15% More Damage"
				}, 
				"TREE_IMPENDING_CONTAGION": {
								"name": "Contagious Infections", 
								"description": "Infections spread to 1 More enemy."
				}, 
				"TREE_SANGUINE_DECAY": {
								"name": "Sanguine Decay", 
								"description": "Bleeding and Ruptured enemies explode on death, dealing 50% of the remaining total Bleed and Rupture Damage on them to nearby enemies."
				}, 
				"TREE_RICOCHET": {
								"name": "Ricochet", 
								"description": "Projectiles deal 30% More Damage each time it Chains"
				}, 
				"TREE_SABOTEUR": {
								"name": "Saboteur", 
								"description": "50% chance to cast an extra Bomb"
				}, 
				"TREE_VOLLEY": {
								"name": "Unstable Volley", 
								"description": "Skills have a 10% chance to fire double projectiles"
				}, 
				"TREE_UNLEASH": {
								"name": "Unleashed", 
								"description": "Every 10 seconds, gain 30% More Cast Speed for 4 seconds"
				}, 
				"TREE_SIPHONER": {
								"name": "Siphoner of Life", 
								"description": "Recover 2% of Maximum Life when you kill an enemy with Damage Over Time.", 
				}, 
				"TREE_OVERLOADED_SHELLS": {
								"name": "Overloaded Shells", 
								"description": "Projectiles deal 10% More Damage"
				}, 

				"TREE_HYSTERIA": {
								"name": "Hysteria", 
								"description": "Enemies Killed have a 30% Chance to Explode dealing 10% of their Maximum Life as Toxic Damage to nearby Enemies", 
				}, 
				"TREE_PARANOIA": {
								"name": "Paranoia", 
								"description": "Poisoned Enemies take 20% More Damage", 
				}, 
				"TREE_DREAD": {
								"name": "Dread", 
								"description": "Nearby Enemies are Cursed with Dread. Dread causes Enemies to take 25% More Damage per unique Non-Enhanced Elemental Ailment on them.", 
				}, 
				"TREE_TRANSMOGRIFICATION": {
								"name": "Transmogrification", 
								"description": "All Weapons that drop are Caster Weapons.", 
				}, 


				"TREE_FURY": {
								"name": "Fury", 
								"description": "While you have your maximum Boons, deal 40% More Damage", 
				}, 
				
				"TREE_TRANSFUSION": {
								"name": "Retaliatory Mark", 
								"description": "Enemies that hit you are marked with Transfusion. Transfused Enemies take 50% More Damage Over Time.", 
				}, 
				"TREE_BLOOD_ARMOR": {
								"name": "Blood Armor", 
								"description": "Gain 1 Blood Boil for 4 seconds when hit. Gain 20% Increased Life Recovery per Blood Boil, 15% Less Damage Taken per Blood Boil. Upon reaching 5 Blood Boils, release a powerful Blood Burst.", 
				}, 
				"TREE_MAGMATIC_BLOOD": {
								"name": "Magmatic Blood", 
								"description": "Bleeds and Ruptures apply as Fire Damage. Bleeding Enemies have -25% Physical and Fire Resistance.", 
				}, 
				"TREE_VILE_DOMAIN": {
								"name": "Vile Domain", 
								"description": "Nearby Enemies count as Poisoned. Nearby Enemies deal 20% Less Damage."
				}, 

				
				"TREE_ENERGETIC_FLESH": {
								"name": "Energetic Flesh", 
								"description": "Nearby Jolted Enemies take 300% of your Maximum Life as Lightning Damage per Second. Deals More Damage equal to your Lightning Ailment Effect."
				}, 
				"TREE_CHAOTIC_RESONANCE": {
								"name": "Chaotic Resonance", 
								"description": "Your Lightning Damage can inflict Toxic Ailments."
				}, 
				"TREE_BONDED_ELECTRONS": {
								"name": "Bonded Electrons", 
								"description": "Nearby enemies have Lightning Resistance equal to yours."
				}, 

				
				"TREE_WEAPON_DEXTERITY": {
								"name": "Weapon Dexterity", 
								"description": "Attack Skills also count as Spell Skills. Spell Skills also count as Attack Skills."
				}, 
				"TREE_OVERCOOK": {
								"name": "Overcook", 
								"description": "Charred Enemies take 40% More Fire Damage."
				}, 

				
				"TREE_CAPABLE_COMBATANT": {
								"name": "Capable Combatant", 
								"description": "Capped Block Chance also applies as More Damage."
				}, 
				"TREE_COATED_BLADES": {
								"name": "Coated Blades", 
								"description": "Physical Damage can inflict Toxic Ailments."
				}, 

				
				"TREE_VIRIDIAN_SAGE": {
								"name": "Viridian Sage", 
								"description": "You take 1% Less Damage per 30 Wisdom, up to 30% Less Damage Taken."
				}, 
				"TREE_STIFLED_CURSING": {
								"name": "Stifled Cursing", 
								"description": "You take 20% Less Damage from Cursed Enemies."
				}, 

				
				"TREE_SHOCKING_MOVES": {
								"name": "Shocking Moves", 
								"description": "Gain 1% Increased Lightning Damage for every 200 Total Evasion, up to 5000%"
				}, 

				
				"TREE_HOPLITE": {
								"name": "Hoplite", 
								"description": "Deal 60% More Damage if both a Melee Weapon and any Shield are equipped."
				}, 
				"TREE_SWORDSMAN": {
								"name": "Swordsman", 
								"description": "If two Melee Weapons are equipped, gain 30% More Cast Speed, 20% More Damage, and take 20% Less Damage."
				}
}
