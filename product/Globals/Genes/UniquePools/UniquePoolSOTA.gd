extends Node

var ancients_charm_texture = load("res://sprites/_mapped/equipment/ancients_charm.png")

var pool = {
				"ancients_charm": {
								"texture": ancients_charm_texture, 
								"min_level_requirement": 125, 
								"unique": true, 
								"name": "Ancient's Charm", 
								"flavor": "A token of the Ancient Spirit.", 
								"type": Genes.BaseType.CASTER_RING, 
								"implicits": [], 
								"prefixes": [{
												"mod_id": "ancients_charm_life", 
								}], 
								"suffixes": [{
												"mod_id": "ancients_charm_cast_speed", 
								}, 
								{
												"mod_id": "ancients_charm_aoe", 
								}], 
								"weight": 5, 
								"locked": true
				}
}
