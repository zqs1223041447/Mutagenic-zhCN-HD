extends Node


var rarity = {
				"magic": Color(0.285245, 0.525921, 0.738281), 
				"rare": Color(0.780167, 0.816406, 0.352539), 
				"unique": Color(0.832031, 0.403975, 0.255282)
}

var buffed = Color(0.294118, 0.65098, 0.27451)
var item_name = buffed
var nerfed = Color(0.605469, 0.108795, 0.108795)
var locked = nerfed
var healing = Color(0.047607, 0.9375, 0.103226)
var mutagen = Color(0.047607, 0.666361, 0.9375)
var tag = Color(0.827451, 0.545098, 0.101961)
var keystone = Color(0.827451, 0.545098, 0.101961)
var unique = Color(0.101961, 0.113297, 0.827451)
var unique_description = Color(0.541176, 0.301961, 0.301961)
var implicit = Color(0.815686, 0.866667, 0.364706)
var keystone_description = Color(0.527344, 0.358885, 0.09272, 0.988235)
var info = Color(0.3125, 0.3125, 0.3125)
var mod_locked = Color(0.329412, 0.507782, 0.886275)
var max_tier = Color(0.180392, 0.713726, 0.164706)
var disabled = Color(0.513726, 0.513726, 0.513726, 0.596078)
var drop_only = Color(0.580392, 0.164706, 0.713726)

var drop_only_1 = Color(0.580392, 0.164706, 0.713726)
var drop_only_2 = Color(0.164706, 0.456373, 0.713726)
var drop_only_3 = Color(0.349821, 0.898438, 0.151385)

var edge_locked = Color(0.136719, 0.131711, 0.131711)
var edge_unlocked = Color(0.088141, 0.471614, 0.546875)
var edge_in_path = Color(0.38277, 0.692638, 0.941406)

var color_passive_tree = Color(0.01614, 0.017451, 0.023438)

var unequipped = Color(0.867188, 0.845895, 0.762363)
var equipped = Color(0.886275, 0.773162, 0.329412)

var orb = Color(0.32549, 0.87451, 0.87451)
var critical = Color(0.870693, 0.875, 0.323718)

var path = Color(0.203125, 0.166795, 0.110119)

var magic_mob = Color(0, 0.141176, 0.898039, 0.313726)
var rare_mob = Color(0.891023, 0.898039, 0, 0.313726)

var corruption = Color(0.737255, 0.094118, 0.113725)

var color_for_skill_tag = {
				SkillTags.Tags.PHYSICAL: Color(0.701961, 0.701961, 0.701961), 
				SkillTags.Tags.LIGHTNING: Color(0.662745, 0.709804, 0.152941), 
				SkillTags.Tags.COLD: Color(0.14902, 0.388235, 0.733333), 
				SkillTags.Tags.FIRE: Color(0.815686, 0.321569, 0.196078), 
				SkillTags.Tags.TOXIC: Color(0.678431, 0.376471, 0.890196), 
}


var tint_for_skill_tag = {
				SkillTags.Tags.PHYSICAL: Color(0.433594, 0.433594, 0.433594), 
				SkillTags.Tags.LIGHTNING: Color(0.639216, 0.701961, 0), 
				SkillTags.Tags.COLD: Color(0, 0.423529, 0.701961), 
				SkillTags.Tags.FIRE: Color(0.701961, 0.231373, 0), 
				SkillTags.Tags.TOXIC: Color(0.466667, 0, 0.701961), 
}

var color_for_spec = {
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.BATTLEMAGE: Color(0.326705, 0.527122, 0.625), 
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.FIEND: Color(0.3276, 0.63, 0.52416), 
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.MARKSMAN: Color(0.34272, 0.63, 0.3276), 
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.MERCENARY: Color(0.61488, 0.63, 0.3276), 
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.SHAMAN: Color(0.51912, 0.3276, 0.63), 
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.TITAN: Color(0.574219, 0.384988, 0.388141), 
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.VAMPIRE: Color(0.63, 0.3276, 0.3276), 
				PlayableClasses.PLAYABLE_SPECIALIZATIONS.WARLOCK: Color(0.217448, 0.246441, 0.652344), 
}
