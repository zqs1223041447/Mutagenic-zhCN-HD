extends Node

var warrior_icon = preload("res://sprites/gui/class_icons/warrior_icon.png")
var rogue_icon = preload("res://sprites/gui/class_icons/rogue_icon.png")
var mage_icon = preload("res://sprites/gui/class_icons/mage_icon.png")
var tank_icon = preload("res://sprites/gui/class_icons/tank_icon.png")

var PLAYABLE_CLASSES = {
				"ROGUE": "ROGUE", 
				"WARRIOR": "WARRIOR", 
				"MAGE": "MAGE", 
				"TANK": "TANK", 
}

var PLAYABLE_SPECIALIZATIONS = {
				"WARLOCK": "WARLOCK", 
				"MERCENARY": "MERCENARY", 
				"VAMPIRE": "VAMPIRE", 
				"MARKSMAN": "MARKSMAN", 
				"SHAMAN": "SHAMAN", 
				"FIEND": "FIEND", 
				"TITAN": "TITAN", 
				"BATTLEMAGE": "BATTLEMAGE", 
}

var PLAYABLE_SPECIALIZATIONS_IDS = {
				"WARLOCK": 1, 
				"MERCENARY": 2, 
				"VAMPIRE": 3, 
				"MARKSMAN": 4, 
				"SHAMAN": 5, 
				"FIEND": 6, 
				"TITAN": 7, 
				"BATTLEMAGE": 8, 
}

func get_playable_spec_id(cls):
				if PLAYABLE_SPECIALIZATIONS_IDS.has(cls):
								return PLAYABLE_SPECIALIZATIONS_IDS[cls]
				return 0

func get_spec_name_from_id(cls):
				for key in PLAYABLE_SPECIALIZATIONS_IDS.keys():
								if PLAYABLE_SPECIALIZATIONS_IDS[key] == cls:
												return specialization_name[key]
				return "Unknown"

func get_spec_color_from_id(cls):
				for key in PLAYABLE_SPECIALIZATIONS_IDS.keys():
								if PLAYABLE_SPECIALIZATIONS_IDS[key] == cls:
												return Colors.color_for_spec[key]
				return Color.white

var root_nodes = {
				PLAYABLE_CLASSES.ROGUE: "root_rogue", 
				PLAYABLE_CLASSES.WARRIOR: "root_warrior", 
				PLAYABLE_CLASSES.MAGE: "root_mage", 
				PLAYABLE_CLASSES.TANK: "root_tank", 
}

var class_names = {
				PLAYABLE_CLASSES.ROGUE: "Rogue", 
				PLAYABLE_CLASSES.WARRIOR: "Warrior", 
				PLAYABLE_CLASSES.MAGE: "Mage", 
				PLAYABLE_CLASSES.TANK: "Tank", 
}

var class_descriptions = {
				PLAYABLE_CLASSES.ROGUE: "The Rogue class prioritizes dealing high damage with speed as it's main source of defense.", 
				PLAYABLE_CLASSES.WARRIOR: "The Warrior class specializes in slaying enemies with attacks.", 
				PLAYABLE_CLASSES.MAGE: "The Mage class prioritizes dealing high damage with spells and arcane magic.", 
				PLAYABLE_CLASSES.TANK: "The Tank class outlasts enemies through sheer durability and offense. ", 
}

var class_icons = {
				PLAYABLE_CLASSES.ROGUE: rogue_icon, 
				PLAYABLE_CLASSES.WARRIOR: warrior_icon, 
				PLAYABLE_CLASSES.MAGE: mage_icon, 
				PLAYABLE_CLASSES.TANK: tank_icon, 
}

var specializations_for_class = {
				PLAYABLE_CLASSES.ROGUE: [PLAYABLE_SPECIALIZATIONS.MARKSMAN, PLAYABLE_SPECIALIZATIONS.VAMPIRE], 
				PLAYABLE_CLASSES.MAGE: [PLAYABLE_SPECIALIZATIONS.WARLOCK, PLAYABLE_SPECIALIZATIONS.SHAMAN], 
				PLAYABLE_CLASSES.TANK: [PLAYABLE_SPECIALIZATIONS.TITAN, PLAYABLE_SPECIALIZATIONS.FIEND], 
				PLAYABLE_CLASSES.WARRIOR: [PLAYABLE_SPECIALIZATIONS.MERCENARY, PLAYABLE_SPECIALIZATIONS.BATTLEMAGE], 
}

var specialization_data_files = {
				PLAYABLE_SPECIALIZATIONS.BATTLEMAGE: "battlemage", 
				PLAYABLE_SPECIALIZATIONS.FIEND: "fiend", 
				PLAYABLE_SPECIALIZATIONS.MARKSMAN: "marksman", 
				PLAYABLE_SPECIALIZATIONS.MERCENARY: "mercenary", 
				PLAYABLE_SPECIALIZATIONS.SHAMAN: "shaman", 
				PLAYABLE_SPECIALIZATIONS.TITAN: "titan", 
				PLAYABLE_SPECIALIZATIONS.VAMPIRE: "vampire", 
				PLAYABLE_SPECIALIZATIONS.WARLOCK: "warlock", 
}

var specialization_name = {
				PLAYABLE_SPECIALIZATIONS.BATTLEMAGE: "Battlemage", 
				PLAYABLE_SPECIALIZATIONS.FIEND: "Fiend", 
				PLAYABLE_SPECIALIZATIONS.MARKSMAN: "Marksman", 
				PLAYABLE_SPECIALIZATIONS.MERCENARY: "Mercenary", 
				PLAYABLE_SPECIALIZATIONS.SHAMAN: "Shaman", 
				PLAYABLE_SPECIALIZATIONS.TITAN: "Titan", 
				PLAYABLE_SPECIALIZATIONS.VAMPIRE: "Vampire", 
				PLAYABLE_SPECIALIZATIONS.WARLOCK: "Warlock", 
}

var specialization_descriptions = {
				PLAYABLE_SPECIALIZATIONS.BATTLEMAGE: "The Battlemage is adept at dealing damage with both Attacks and Spells.", 
				PLAYABLE_SPECIALIZATIONS.FIEND: "The Fiend is highly attuned to Lightning.", 
				PLAYABLE_SPECIALIZATIONS.MARKSMAN: "The Marksman excels at slaying enemies from afar.", 
				PLAYABLE_SPECIALIZATIONS.MERCENARY: "The Mercenary is puts itself at risk for a greater power.", 
				PLAYABLE_SPECIALIZATIONS.SHAMAN: "The Shaman commands the power of nature to slay it's foes.", 
				PLAYABLE_SPECIALIZATIONS.TITAN: "The Titan is an unmovable beast on the battlefield.", 
				PLAYABLE_SPECIALIZATIONS.VAMPIRE: "The Vampire uses it's knowledge of blood to gain the upperhand.", 
				PLAYABLE_SPECIALIZATIONS.WARLOCK: "The Warlock defeats it's opponents with it's knowledge of Poison.", 
}

func get_root_node(cn):
				if root_nodes.has(cn):
								return root_nodes[cn]
				return null

func get_class_name(cn, spec = null):
				if spec and specialization_name.has(spec):
								return specialization_name[spec]
				if class_names.has(cn):
								return class_names[cn]
				return "Unknown"
