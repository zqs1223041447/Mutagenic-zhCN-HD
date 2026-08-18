extends Node

signal mods_changed





enum Target{
				PLAYER
				MOB
}

func sort_mods(a, b):
				return a.target < b.target


const ModOptions = {
				"health_max": {
								"target": Target.MOB, 
								"stat": "health_max", 
								"roll": [0.1, 0.9], 
								"stepified": 0.1, 
								"scaling_type": Constants.ScalingType.MORE, 
				}, 
				"all_damage": {
								"target": Target.MOB, 
								"stat": "all_damage", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"movement_speed": {
								"target": Target.MOB, 
								"stat": "movement_speed", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"cast_speed": {
								"target": Target.MOB, 
								"stat": "cast_speed", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"projectile_speed": {
								"target": Target.MOB, 
								"stat": "projectile_speed", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.4, 1.25], 
				}, 
				"physical_resistance": {
								"target": Target.MOB, 
								"stat": "physical_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"curse_resistance": {
								"target": Target.MOB, 
								"stat": "curse_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"lightning_resistance": {
								"target": Target.MOB, 
								"stat": "lightning_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.1, 0.7], 
				}, 
				"cold_resistance": {
								"target": Target.MOB, 
								"stat": "cold_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.1, 0.7], 
				}, 
				"fire_resistance": {
								"target": Target.MOB, 
								"stat": "fire_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.1, 0.7], 
				}, 
				"toxic_resistance": {
								"target": Target.MOB, 
								"stat": "toxic_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.1, 0.7], 
				}, 
				"physical_damage": {
								"target": Target.MOB, 
								"stat": "physical_damage", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"lightning_damage": {
								"target": Target.MOB, 
								"stat": "lightning_damage", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"cold_damage": {
								"target": Target.MOB, 
								"stat": "cold_damage", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"fire_damage": {
								"target": Target.MOB, 
								"stat": "fire_damage", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"toxic_damage": {
								"target": Target.MOB, 
								"stat": "toxic_damage", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.1, 0.9], 
				}, 
				"area_of_effect": {
								"target": Target.MOB, 
								"stat": "area_of_effect", 
								"scaling_type": Constants.ScalingType.MORE, 
								"stepified": 0.1, 
								"roll": [0.3, 1.5], 
				}, 
				"mitigation": {
								"target": Target.MOB, 
								"stat": "mitigation", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 1, 
								"roll": [25, 300], 
				}, 
				"physical_penetration": {
								"target": Target.MOB, 
								"stat": "physical_penetration", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.08, 0.18], 
				}, 
				"lightning_penetration": {
								"target": Target.MOB, 
								"stat": "lightning_penetration", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.08, 0.18], 
				}, 
				"cold_penetration": {
								"target": Target.MOB, 
								"stat": "cold_penetration", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.08, 0.18], 
				}, 
				"fire_penetration": {
								"target": Target.MOB, 
								"stat": "fire_penetration", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.08, 0.18], 
				}, 
				"toxic_penetration": {
								"target": Target.MOB, 
								"stat": "toxic_penetration", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.08, 0.18], 
				}, 
				"block_chance": {
								"target": Target.MOB, 
								"stat": "block_chance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.1, 
								"roll": [0.1, 0.4], 
				}, 
				"ailment_avoidance": {
								"target": Target.MOB, 
								"stat": "ailment_avoidance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.05, 
								"roll": [0.15, 0.35], 
				}, 

				
				"player_less_physical_resistance": {
								"target": Target.PLAYER, 
								"stat": "physical_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.01, 
								"roll": [ - 0.35, - 0.15], 
				}, 
				
				"player_less_lightning_resistance": {
								"target": Target.PLAYER, 
								"stat": "lightning_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.01, 
								"roll": [ - 0.35, - 0.15], 
				}, 
				
				"player_less_cold_resistance": {
								"target": Target.PLAYER, 
								"stat": "cold_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.01, 
								"roll": [ - 0.35, - 0.15], 
				}, 
				
				"player_less_fire_resistance": {
								"target": Target.PLAYER, 
								"stat": "fire_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.01, 
								"roll": [ - 0.35, - 0.15], 
				}, 
				
				"player_less_toxic_resistance": {
								"target": Target.PLAYER, 
								"stat": "toxic_resistance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.01, 
								"roll": [ - 0.35, - 0.15], 
				}, 
				"player_less_block_chance": {
								"target": Target.PLAYER, 
								"stat": "block_chance", 
								"scaling_type": Constants.ScalingType.FLAT, 
								"stepified": 0.01, 
								"roll": [ - 0.25, - 0.15], 
				}, 
}

var active_mods = {}

func reroll_mods(zone_level):
				var number_of_mods = ZoneScaling.get_map_mod_count(zone_level)
				active_mods = []
				var possible_mods = ModOptions.keys()
				var chosen_mods = []
				for i in range(min(len(possible_mods), number_of_mods)):
								var picked_mod = possible_mods[randi() % len(possible_mods)]
								chosen_mods.append(picked_mod)
								possible_mods.erase(picked_mod)

				for mod in chosen_mods:
								var option = ModOptions[mod]
								active_mods.append({
												"mod_id": mod, 
												"target": option.target, 
												"stat": option.stat, 
												"roll": roll_stat(option.roll[0], option.roll[1], option.stepified)
								})

				active_mods.sort_custom(self, "sort_mods")
				print("Mods rolled:", active_mods)
				emit_signal("mods_changed")

func roll_stat(low, high, stepified = 0.1):
				return stepify(low + (high - low) * randf(), stepified)

func get_map_mods():
				return active_mods

func render_stat(mod):
				var bundle = {
								"scaling_type": ModOptions[mod.mod_id].scaling_type, 
								"stepified": ModOptions[mod.mod_id].stepified, 
								"amount": mod.roll
				}
				var prefix = "Enemies have "
				if mod.target == Target.PLAYER:
								prefix = "Players have "

				return prefix + StatsInfo.render_passive_stat_line(mod.stat, bundle)
