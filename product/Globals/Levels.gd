extends Node


var default_level = preload("res://Scenes/Levels/Default/DefaultLevel.tscn")
var hideout_level = preload("res://Scenes/Levels/Hideout/HideoutLevel.tscn")
var boss_level = preload("res://Scenes/Levels/BossArenas/BossArena.tscn")
var spirit_of_the_ancient_level = preload("res://Scenes/Levels/BossArenas/SpiritOfTheAncient/SpiritOfTheAncient.tscn")
var ladder_level = preload("res://Scenes/Levels/Ladder/Ladder.tscn")
var test_level = preload("res://Scenes/Levels/TestLevel/TestLevel.tscn")


var tileset_factory = preload("res://Tilesets/tileset_factory.png")
var tileset_dungeon = preload("res://Tilesets/tileset_dungeon.png")
var tileset_beach = preload("res://Tilesets/tileset_beach.png")
var tileset_cemetery = preload("res://Tilesets/tileset_cemetery.png")
var tileset_dead_grass = preload("res://Tilesets/tileset_dead_grass.png")
var tileset_grass = preload("res://Tilesets/tileset_grass.png")
var tileset_dirt = preload("res://Tilesets/tileset_dirt.png")
var tileset_snow = preload("res://Tilesets/tileset_snow.png")
var tileset_shrine = preload("res://Tilesets/tileset_shrine.png")
var tileset_blood_church = preload("res://Tilesets/tileset_blood_church.png")
var tileset_hideout = preload("res://Tilesets/tileset_hideout.png")
var tileset_sota = preload("res://Tilesets/tileset_sota.png")
var tileset_red_cave = preload("res://Tilesets/tileset_red_cave.png")
var tileset_pit = preload("res://Tilesets/tileset_pit.png")


var icon_mountain = preload("res://sprites/worldmap/mountain.png")
var icon_blood_church = preload("res://sprites/worldmap/blood_church.png")
var icon_sandstorm = preload("res://sprites/worldmap/sandstorm.png")
var icon_grasslands = preload("res://sprites/worldmap/grasslands.png")
var icon_catacombs = preload("res://sprites/worldmap/catacombs.png")
var icon_fields_of_despair = preload("res://sprites/worldmap/field_of_despair.png")
var icon_musty_den = preload("res://sprites/worldmap/musty_den.png")
var icon_dungeon = preload("res://sprites/worldmap/dungeon.png")


var icon_boss = preload("res://sprites/worldmap/boss.png")


var icon_ladder = preload("res://sprites/worldmap/ladder.png")


var gatekeeper = preload("res://Scenes/Mobs/Bosses/GateKeeper.tscn")
var sludge = preload("res://Scenes/Mobs/Bosses/Sludge.tscn")
var spirit_of_the_ancient = preload("res://Scenes/Mobs/Bosses/SpiritOfTheAncient.tscn")
var mutated_spider = preload("res://Scenes/Mobs/Bosses/MutatedSpider.tscn")

enum Layout{
				FIXED,
				CIRCLE,
				FIELD,
				CELLS,
				OPEN,
				FORKED,
}

enum MAP_TYPE{
				HIDEOUT,
				MAP,
				BOSS,
				LADDER,
}

var generator_for_layout = {
				Layout.FIXED: LayoutFixed, 
				Layout.CIRCLE: LayoutCircle, 
				Layout.FIELD: LayoutField, 
				Layout.CELLS: LayoutCells, 
				Layout.OPEN: LayoutCircle, 
				Layout.FORKED: LayoutCircle, 
}

var config = {
				"cave": {
								"name": "Chilly Cavern", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CIRCLE, 
								"tileset": tileset_snow, 
								"icon": icon_mountain, 
				}, 
				"dirt_cave": {
								"name": "Musty Den", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CIRCLE, 
								"tileset": tileset_dirt, 
								"icon": icon_musty_den, 
				}, 
				"red_cave": {
								"name": "Gemling Cave", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CIRCLE, 
								"tileset": tileset_red_cave, 
								"icon": icon_musty_den, 
				}, 
				"pit": {
								"name": "Pit", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CIRCLE, 
								"tileset": tileset_pit, 
								"icon": icon_musty_den, 
				}, 
				"forest": {
								"name": "Grasslands", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.FIELD, 
								"tileset": tileset_grass, 
								"icon": icon_grasslands, 
				}, 
				"hell": {
								"name": "Blood Shrine", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CELLS, 
								"tileset": tileset_shrine, 
								"icon": icon_blood_church, 
				}, 
				"catacombs": {
								"name": "Catacombs", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CELLS, 
								"tileset": tileset_blood_church, 
								"icon": icon_catacombs, 
				}, 
				"flats": {
								"name": "Field of Despair", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.FIELD, 
								"tileset": tileset_dead_grass, 
								"icon": icon_fields_of_despair, 
				}, 
				"sands": {
								"name": "Sandstorm", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CIRCLE, 
								"tileset": tileset_beach, 
								"icon": icon_sandstorm, 
				}, 
				"dungeon": {
								"name": "Dungeon", 
								"level_scene": default_level, 
								"map_type": MAP_TYPE.MAP, 
								"zone_level": 1, 
								"calculate_level_from_start": true, 
								"layout": Layout.CELLS, 
								"tileset": tileset_dungeon, 
								"icon": icon_dungeon, 
				}, 
				"boss_1": {
								"name": "The Gatekeeper", 
								"level_scene": boss_level, 
								"boss_scene": gatekeeper, 
								"map_type": MAP_TYPE.BOSS, 
								"zone_level": 20, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_beach, 
								"icon": icon_boss, 
				}, 
				"boss_2": {
								"name": "Sludge", 
								"level_scene": boss_level, 
								"boss_scene": sludge, 
								"map_type": MAP_TYPE.BOSS, 
								"zone_level": 50, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_blood_church, 
								"icon": icon_boss, 
				}, 
				"boss_3": {
								"name": "Mutated Spider", 
								"level_scene": boss_level, 
								"boss_scene": mutated_spider, 
								"map_type": MAP_TYPE.BOSS, 
								"zone_level": 100, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_blood_church, 
								"icon": icon_boss, 
				}, 
				"spirit_of_the_ancient": {
								"name": "Spirit of the Ancients", 
								"level_scene": spirit_of_the_ancient_level, 
								"boss_scene": spirit_of_the_ancient, 
								"map_type": MAP_TYPE.BOSS, 
								"zone_level": 125, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_sota, 
								"icon": icon_boss, 
				}, 
				"leaderboard_25": {
								"name": "Challenge Ladder 1", 
								"leaderboard": "challenge_ladder_1_prod", 
								"level_scene": ladder_level, 
								"map_type": MAP_TYPE.LADDER, 
								"zone_level": 25, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_dead_grass, 
								"icon": icon_ladder, 
				}, 
				"leaderboard_50": {
								"name": "Challenge Ladder 2", 
								"leaderboard": "challenge_ladder_2_prod", 
								"level_scene": ladder_level, 
								"map_type": MAP_TYPE.LADDER, 
								"zone_level": 50, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_cemetery, 
								"icon": icon_ladder, 
				}, 
				"leaderboard_75": {
								"name": "Challenge Ladder 3", 
								"leaderboard": "challenge_ladder_3_prod", 
								"level_scene": ladder_level, 
								"map_type": MAP_TYPE.LADDER, 
								"zone_level": 75, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_blood_church, 
								"icon": icon_ladder, 
				}, 
				"leaderboard_100": {
								"name": "Challenge Ladder 4", 
								"leaderboard": "challenge_ladder_4_prod", 
								"level_scene": ladder_level, 
								"map_type": MAP_TYPE.LADDER, 
								"zone_level": 100, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_shrine, 
								"icon": icon_ladder, 
				}, 
				"hideout": {
								"name": "Hideout", 
								"level_scene": hideout_level, 
								"map_type": MAP_TYPE.HIDEOUT, 
								"zone_level": 1, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_hideout, 
								"icon": null, 
				}, 
				"test_level": {
								"name": "Testing Zone", 
								"level_scene": test_level, 
								"leaderboard": null, 
								"map_type": MAP_TYPE.LADDER, 
								"zone_level": 1, 
								"calculate_level_from_start": false, 
								"layout": Layout.FIXED, 
								"tileset": tileset_shrine, 
								"icon": null, 
				}
}


func is_current_level_hideout():
				return config[Globals.selected_level].map_type == MAP_TYPE.HIDEOUT

func is_current_level_arena():
				return config[Globals.selected_level].map_type == MAP_TYPE.BOSS

func is_current_level_ladder():
				return config[Globals.selected_level].map_type == MAP_TYPE.LADDER

func is_current_level_map():
				return config[Globals.selected_level].map_type == MAP_TYPE.MAP

func get_current_level_name():
				return config[Globals.selected_level].name

func get_current_leaderboard_name():
				return config[Globals.selected_level].leaderboard

func is_map_fixed_level(map_name):
				return not config[map_name].calculate_level_from_start

func get_map_zone_level(map_name):
				return config[map_name].zone_level

func get_current_level_zone_level():
				return config[Globals.selected_level].zone_level

func get_layout_for_stage_id(stage_id):
				var map_name = WorldMapData.get_map_name(stage_id)
				return generator_for_layout[config[map_name].layout]
