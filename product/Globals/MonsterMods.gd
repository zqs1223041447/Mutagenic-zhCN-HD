extends Node


var mods = {
				"extra_life": {
								"description": "Extra Life", 
								"stats": {
												"health_max": {
																Constants.ScalingType.MORE: 2.0
												}
								}
				}, 
				"fast": {
								"description": "Quick", 
								"stats": {
												"movement_speed": {
																Constants.ScalingType.FLAT: 45.0, 
																Constants.ScalingType.PERCENT: 0.2, 
												}, 
												"cast_speed": {
																Constants.ScalingType.MORE: 3.0
												}
								}
				}, 
				"tough": {
								"description": "Resistant", 
								"stats": {
												"physical_resistance": {
																Constants.ScalingType.FLAT: 0.3, 
												}, 
												"lightning_resistance": {
																Constants.ScalingType.FLAT: 0.3, 
												}, 
												"cold_resistance": {
																Constants.ScalingType.FLAT: 0.3, 
												}, 
												"fire_resistance": {
																Constants.ScalingType.FLAT: 0.3, 
												}, 
												"toxic_resistance": {
																Constants.ScalingType.FLAT: 0.3, 
												}, 
								}
				}, 
				"precise": {
								"description": "Critically Attuned", 
								"stats": {
												"crit_chance": {
																Constants.ScalingType.FLAT: 0.25
												}, 
												"crit_multi": {
																Constants.ScalingType.FLAT: 1.25
												}
								}
				}, 
				"extra_cold_damage": {
								"description": "Cold Attuned", 
								"stats": {
												"cold_damage": {
																Constants.ScalingType.FLAT: 2, 
																Constants.ScalingType.MORE: 0.5, 
												}, 
												"extra_physical_as_cold": {
																Constants.ScalingType.FLAT: 0.3
												}, 
												"cold_ailment_chance": {
																Constants.ScalingType.FLAT: 1.0
												}
								}
				}, 
				"extra_fire_damage": {
								"description": "Fire Attuned", 
								"stats": {
												"fire_damage": {
																Constants.ScalingType.FLAT: 2, 
																Constants.ScalingType.MORE: 0.5, 
												}, 
												"extra_physical_as_fire": {
																Constants.ScalingType.FLAT: 0.3
												}, 
												"fire_ailment_chance": {
																Constants.ScalingType.FLAT: 1.0
												}
								}
				}, 
				"extra_lightning_damage": {
								"description": "Lightning Attuned", 
								"stats": {
												"lightning_damage": {
																Constants.ScalingType.FLAT: 2, 
																Constants.ScalingType.MORE: 0.5, 
												}, 
												"extra_physical_as_lightning": {
																Constants.ScalingType.FLAT: 0.3
												}, 
												"lightning_ailment_chance": {
																Constants.ScalingType.FLAT: 1.0
												}
								}
				}
}

var auras = {

}

func choose(n):
				var options = mods.keys()
				options.shuffle()
				if n > len(options):
								return []
				var result = []
				for i in range(n):
								var item = mods[options.pop_back()]
								result.append(item)
				return result

func choose_with_auras(n):
				var options = mods.keys()
				options.shuffle()
				var aura_options = auras.keys()
				aura_options.shuffle()
				if n > len(options) - 1:
								return []
				var result = []
				for i in range(n - 1):
								var item = mods[options.pop_back()]
								result.append(item)

				if len(aura_options) == 0:
								return result

				
				result.append(auras[aura_options[0]])

				return result
