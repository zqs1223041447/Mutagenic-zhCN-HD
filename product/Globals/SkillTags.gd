extends Node

enum Tags{
				PROJECTILE, 
				AREA, 
				CURSE, 
				BUFF, 
				CASTABLE, 
				CHAINING, 
				PASSIVE, 
				DURATION, 
				TRIGGERABLE, 
				HIT, 
				BOMB, 
				FIRE, 
				COLD, 
				LIGHTNING, 
				PHYSICAL, 
				TOXIC, 
				DAMAGING, 
				UTILITY, 
				ELEMENTAL, 
				AURA, 
				DOT, 
				MELEE, 
				ATTACK, 
				SPELL, 
				NONE,
}

var TagNames = {
				Tags.PROJECTILE: "Projectile", 
				Tags.AREA: "Area", 
				Tags.CURSE: "Curse", 
				Tags.PASSIVE: "Passive", 
				Tags.CASTABLE: "Castable", 
				Tags.CHAINING: "Chain", 
				Tags.TRIGGERABLE: "Triggerable", 
				Tags.BUFF: "Buff", 
				Tags.DURATION: "Duration", 
				Tags.HIT: "Hit", 
				Tags.BOMB: "Bomb", 
				Tags.FIRE: "Fire", 
				Tags.COLD: "Cold", 
				Tags.LIGHTNING: "Lightning", 
				Tags.PHYSICAL: "Physical", 
				Tags.TOXIC: "Toxic", 
				Tags.DAMAGING: "Damaging", 
				Tags.UTILITY: "Utility", 
				Tags.ELEMENTAL: "Elemental", 
				Tags.DOT: "Damage Over Time", 
				Tags.AURA: "Aura", 
				Tags.MELEE: "Melee", 
				Tags.ATTACK: "Attack", 
				Tags.SPELL: "Spell"
}

var DAMAGE_TAGS = [
				Tags.PHYSICAL, Tags.LIGHTNING, Tags.COLD, Tags.FIRE, Tags.TOXIC
]

func get_tag_list(skill_name):
				var tags = Skills.config[skill_name].tags
				return render_tag_list(tags)

func render_tag_list(tags):
				var names = []
				for tag in tags:
								names.append(TagNames[tag])
				return ", ".join(PackedStringArray(names))

func tags_to_string(tags = []):
				var names = []
				for tag in tags:
								names.append(TagNames[tag])
				return ", ".join(PackedStringArray(names))
