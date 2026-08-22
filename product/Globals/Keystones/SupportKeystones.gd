extends Node


var keystones = {
				"SUPPORT_SNIPER": {
								"name": "Sniper", 
								"description": "Projectiles have no spread"
				}, 
				"SUPPORT_COLLATERAL_DAMAGE": {
								"name": "Collateral Damage", 
								"description": "Projectile Hits have a 10% chance to also deal an extra 300% of Damage the target and to Nearby Enemies."
				}, 
				"SUPPORT_CAST_ON_CRIT": {
								"name": "Cast on Crit", 
								"description": "Skill casts when another skill inflicts a critical strike. Skill does not auto cast, and cannot trigger other skills."
				}, 
				"SUPPORT_CAST_ON_KILL": {
								"name": "Cast on Kill", 
								"description": "Skill has a 10% chance to cast when another skill inflicts a killing blow. Skill does not auto cast, and cannot trigger other skills."
				}, 
				"SUPPORT_VOLATILITY": {
								"name": "Volatility", 
								"description": "Skill is cast when hitting an enemy with any non-triggered skill. Skill consumes all Boons to deal 20% more damage for each consumed Boon. Skill does not auto cast, and cannot trigger other skills."
				}, 
				"SUPPORT_HAMSTRING": {
								"name": "Hamstring", 
								"description": "Skill inflicts Hamstrung for 4 seconds on hit, causing 15% Less Movement Speed"
				}, 
				"SUPPORT_PROLIFERATE": {
								"name": "Proliferate", 
								"description": "Elemental Ailments inflicted by this Skill also apply to nearby enemies."
				}, 
				"SUPPORT_SACRIFICE": {
								"name": "Sacrifice", 
								"description": "Skills cost 10% of your Maximum Life per Cast, gaining half as much as Added Physical Damage. Supported Skills cannot be cast if you lack the required Life Cost."
				}, 
				"SUPPORT_STATIC_ELECTRICITY": {
								"name": "Static Electricity", 
								"description": "Hitting a Jolted Enemy has a 50% Chance to cause a bolt of Lightning to strike up to 3 nearby enemies, consuming the Jolt. Damage inflicted by Lightning deals damage equal to the initial Hit Damage multiplied by 200% of the Jolt on the original enemy. Lightning can Critically Strike, but it cannot inflict Ailments.", 
				}
}
