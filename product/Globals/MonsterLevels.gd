extends Node


var skeleton_warrior = preload("res://scenes/Mobs/Basic/Creatures/SkeletonWarrior.tscn")
var skeleton_mage = preload("res://scenes/Mobs/Basic/Creatures/SkeletonMage.tscn")
var skeleton_archer = preload("res://scenes/Mobs/Basic/Creatures/SkeletonArcher.tscn")
var skeleton_sparker = preload("res://scenes/Mobs/Basic/Creatures/SkeletonSparker.tscn")
var skeletor = preload("res://scenes/Mobs/Basic/Creatures/Skeletor.tscn")
var chilled_bones = preload("res://scenes/Mobs/Basic/Creatures/ChilledBones.tscn")
var attack_dog = preload("res://scenes/Mobs/Basic/Creatures/AttackDog.tscn")
var lightning_dog = preload("res://scenes/Mobs/Basic/Creatures/LightningDog.tscn")
var zombie = preload("res://scenes/Mobs/Basic/Creatures/Zombie.tscn")
var spider = preload("res://scenes/Mobs/Basic/Creatures/Spider.tscn")
var fire_bomber = preload("res://scenes/Mobs/Basic/Creatures/FireBomber.tscn")
var ice_golem = preload("res://scenes/Mobs/Basic/Creatures/IceGolem.tscn")
var skeleton_curser = preload("res://scenes/Mobs/Basic/Creatures/SkeletonCurser.tscn")
var ninja = preload("res://scenes/Mobs/Basic/Creatures/Ninja.tscn")

var leaderboard_mobs = [skeleton_warrior, attack_dog, skeleton_sparker, skeleton_mage, zombie, skeletor, spider, lightning_dog, chilled_bones, ice_golem, fire_bomber, skeleton_archer, skeleton_curser, ninja]

var monsters_in = {
				"cave": [skeleton_warrior, skeleton_sparker, attack_dog, skeletor, spider, chilled_bones, ice_golem], 
				"dirt_cave": [skeleton_warrior, attack_dog, skeletor, lightning_dog, fire_bomber, skeleton_archer], 
				"red_cave": [skeleton_warrior, lightning_dog, fire_bomber, skeleton_archer, ninja], 
				"pit": [skeleton_warrior, attack_dog, skeletor, lightning_dog, fire_bomber, skeleton_archer, ninja], 
				"forest": [skeleton_warrior, attack_dog, skeletor, lightning_dog], 
				"hell": [skeleton_warrior, skeleton_mage, zombie, skeletor, skeleton_curser], 
				"dungeon": [skeleton_warrior, skeleton_mage, zombie, skeletor, skeleton_curser, ninja], 
				"catacombs": [skeleton_warrior, skeleton_mage, zombie, skeletor, spider, skeleton_archer, skeleton_curser], 
				"flats": [zombie, attack_dog, skeleton_warrior, skeletor, chilled_bones], 
				"sands": [skeleton_warrior, attack_dog, lightning_dog], 
				"leaderboard_25": leaderboard_mobs, 
				"leaderboard_50": leaderboard_mobs, 
				"leaderboard_75": leaderboard_mobs, 
				"leaderboard_100": leaderboard_mobs, 
				"test_level": leaderboard_mobs, 
}
