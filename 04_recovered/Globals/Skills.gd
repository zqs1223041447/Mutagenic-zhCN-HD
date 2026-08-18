extends Node

var tiers = {
				"Orb": OrbTiers, 
				"Arc": ArcTiers, 
				"Shotgun": ShotgunTiers, 
				"PoisonDart": PoisonDartTiers, 
				"Shuriken": ShurikenTiers, 
				"Blizzard": BlizzardTiers, 
				"PlagueClouds": PlagueCloudsTiers, 
				"Debilitate": DebilitateTiers, 
				"Brittle": BrittleTiers, 
				"Scorch": ScorchTiers, 
				"Polarize": PolarizeTiers, 
				"Protract": ProtractionTiers, 
				"Hinder": HinderTiers, 
				"Bane": BaneTiers, 
				"Hypothermia": HypothermiaTiers, 
				"IceOrb": IceOrbTiers, 
				"Axe": AxeTiers, 
				"ShrapnelBomb": ShrapnelBombTiers, 
				"ShockOrb": ShockOrbTiers, 
				"Volcano": VolcanoTiers, 
				"Arrow": ArrowTiers, 
				"ShardOrb": ShardOrbTiers, 
				"Minigun": MinigunTiers, 
				"ChainLightning": ChainLightningTiers, 
				"FlameTether": FlameTetherTiers, 
				"DoomTether": DoomTetherTiers, 
				"PrismaticSlash": PrismaticSlashTiers, 
				"LavaSurge": LavaSurgeTiers, 
				"LightningSpear": LightningSpearTiers, 
				"ClusterBombs": ClusterBombsTiers, 
				"Shockwave": ShockwaveTiers, 
				"BladeShield": BladeShieldTiers, 
				"EnergizedAxe": EnergizedAxeTiers, 
				"SharknadoShot": SharknadoShotTiers, 
				"BloodSlash": BloodSlashTiers, 
				"PlasmaOrb": PlasmaOrbTiers, 


				
				"Rush": RushTiers, 
				"Regeneration": RegenerationTiers, 
				"Resilience": ResilienceTiers, 
				"Sturdiness": SturdinessTiers, 
				"Elusiveness": ElusivenessTiers, 
				"Honing": HoningTiers, 
				"AmplificationAura": AmplificationAuraTiers, 
				"PhysicalAura": PhysicalAuraTiers, 
				"LightningAura": LightningAuraTiers, 
				"ColdAura": ColdAuraTiers, 
				"FireAura": FireAuraTiers, 
				"ToxicAura": ToxicAuraTiers, 
				"DoTAura": DoTAuraTiers, 
}


var orb_tex = preload("res://sprites/skills/orb.png")
var plasma_orb_tex = preload("res://sprites/skills/plasma_orb_skill.png")
var arc_tex = preload("res://sprites/skills/arc.png")
var amplifier_tex = preload("res://sprites/skills/amplifier.png")
var boots_tex = preload("res://sprites/skills/boots.png")
var growthwand_tex = preload("res://sprites/skills/growth_wand.png")
var pinpoint_tex = preload("res://sprites/skills/pinpoint.png")
var ring_tex = preload("res://sprites/skills/ring.png")
var salamander_tex = preload("res://sprites/skills/salamander.png")
var steak_tex = preload("res://sprites/skills/steak.png")
var oak_shield_tex = preload("res://sprites/skills/oak_shield.png")
var jar_tex = preload("res://sprites/skills/jar.png")
var gunpowder_tex = preload("res://sprites/skills/gunpowder.png")
var mirror_tex = preload("res://sprites/skills/mirror.png")
var shotgun_tex = preload("res://sprites/skills/shotgun.png")
var poison_dart_tex = preload("res://sprites/skills/syringe.png")
var shuriken_tex = preload("res://sprites/skills/shuriken.png")
var blizzard_tex = preload("res://sprites/skills/blizzard_skill.png")
var plague_clouds_tex = preload("res://sprites/skills/plague_clouds_skill.png")
var debilitate_tex = preload("res://sprites/skills/debilitate.png")
var hinder_tex = preload("res://sprites/skills/hinder.png")
var brittle_tex = preload("res://sprites/skills/brittle.png")
var scorch_tex = preload("res://sprites/skills/scorch.png")
var hypothermia_tex = preload("res://sprites/skills/hypothermia.png")
var bane_tex = preload("res://sprites/skills/bane.png")
var polarize_tex = preload("res://sprites/skills/polarize.png")
var protraction_tex = preload("res://sprites/skills/protraction.png")
var iceorb_tex = preload("res://sprites/skills/ice_orb.png")
var axe_tex = preload("res://sprites/skills/axe.png")
var shrapnelbomb_tex = preload("res://sprites/skills/shrapnelbomb.png")
var shockorb_tex = preload("res://sprites/skills/shock_orb.png")
var volcano_tex = preload("res://sprites/skills/volcano.png")
var physicalessence_tex = preload("res://sprites/skills/physical_essence.png")
var lightningessence_tex = preload("res://sprites/skills/lightning_essence.png")
var coldessence_tex = preload("res://sprites/skills/cold_essence.png")
var fireessence_tex = preload("res://sprites/skills/fire_essence.png")
var toxicessence_tex = preload("res://sprites/skills/toxic_essence.png")
var bow_tex = preload("res://sprites/skills/bow.png")
var lucky_charm_tex = preload("res://sprites/skills/lucky_charm.png")
var shard_orb_tex = preload("res://sprites/skills/shard_orb.png")
var minigun_tex = preload("res://sprites/skills/minigun.png")
var chain_lightning_tex = preload("res://sprites/skills/chain_lightning.png")
var flame_tether_tex = preload("res://sprites/skills/flame_tether.png")
var doom_tether_tex = preload("res://sprites/skills/doom_tether.png")
var prismatic_slash_tex = preload("res://sprites/skills/prismatic_slash.png")
var lava_surge_tex = preload("res://sprites/skills/flame_surge.png")
var lightning_spear_tex = preload("res://sprites/skills/lightning_spear.png")
var cluster_bombs_tex = preload("res://sprites/skills/cluster_bombs.png")
var blade_shield_tex = preload("res://sprites/skills/blade_shield.png")
var shockwave_tex = preload("res://sprites/skills/shockwave.png")
var energized_axe_tex = preload("res://sprites/skills/energized_axe.png")
var sharknado_shot_tex = preload("res://sprites/skills/sharknado_shot.png")
var blood_slash_tex = preload("res://sprites/skills/blood_slash.png")


var orb_skill = preload("res://Scenes/Skills/Playable/Orb/Orb.tscn")
var plasma_orb_skill = preload("res://Scenes/Skills/Playable/PlasmaOrb/PlasmaOrb.tscn")
var arc_skill = preload("res://Scenes/Skills/Playable/Arc/Arc.tscn")
var shotgun_skill = preload("res://Scenes/Skills/Playable/Shotgun/Shotgun.tscn")
var poison_dart_skill = preload("res://Scenes/Skills/Playable/PoisonDart/PoisonDart.tscn")
var shuriken_skill = preload("res://Scenes/Skills/Playable/Shuriken/Shuriken.tscn")
var blizzard_skill = preload("res://Scenes/Skills/Playable/Blizzard/Blizzard.tscn")
var plague_clouds_skill = preload("res://Scenes/Skills/Playable/PlagueClouds/PlagueClouds.tscn")
var debilitate_skill = preload("res://Scenes/Skills/Playable/Debilitate/Debilitate.tscn")
var hinder_skill = preload("res://Scenes/Skills/Playable/Hinder/Hinder.tscn")
var brittle_skill = preload("res://Scenes/Skills/Playable/Brittle/Brittle.tscn")
var scorch_skill = preload("res://Scenes/Skills/Playable/Scorch/Scorch.tscn")
var protraction_skill = preload("res://Scenes/Skills/Playable/Protract/Protract.tscn")
var bane_skill = preload("res://Scenes/Skills/Playable/Bane/Bane.tscn")
var hypothermia_skill = preload("res://Scenes/Skills/Playable/Hypothermia/Hypothermia.tscn")
var polarize_skill = preload("res://Scenes/Skills/Playable/Polarize/Polarize.tscn")
var iceorb_skill = preload("res://Scenes/Skills/Playable/IceOrb/IceOrb.tscn")
var axe_skill = preload("res://Scenes/Skills/Playable/Axe/Axe.tscn")
var shrapnelbomb_skill = preload("res://Scenes/Skills/Playable/ShrapnelBomb/ShrapnelBomb.tscn")
var shockorb_skill = preload("res://Scenes/Skills/Playable/ShockOrb/ShockOrb.tscn")
var volcano_skill = preload("res://Scenes/Skills/Playable/Volcano/Volcano.tscn")
var arrow_skill = preload("res://Scenes/Skills/Playable/Arrow/Arrow.tscn")
var shard_orb_skill = preload("res://Scenes/Skills/Playable/ShardOrb/ShardOrb.tscn")
var minigun_skill = preload("res://Scenes/Skills/Playable/Minigun/Minigun.tscn")
var chain_lightning_skill = preload("res://Scenes/Skills/Playable/ChainLightning/ChainLightning.tscn")
var flame_tether_skill = preload("res://Scenes/Skills/Auras/FlameTether/FlameTether.tscn")
var doom_tether_skill = preload("res://Scenes/Skills/Auras/DoomTether/DoomTether.tscn")
var prismatic_slash_skill = preload("res://Scenes/Skills/Playable/PrismaticSlash/PrismaticSlash.tscn")
var lava_surge_skill = preload("res://Scenes/Skills/Playable/LavaSurge/LavaSurge.tscn")
var lightning_spear_skill = preload("res://Scenes/Skills/Playable/LightningSpear/LightningSpear.tscn")
var cluster_bombs_skill = preload("res://Scenes/Skills/Playable/ClusterBombs/ClusterBombs.tscn")
var shockwave_skill = preload("res://Scenes/Skills/Playable/Shockwave/Shockwave.tscn")
var blade_shield_skill = preload("res://Scenes/Skills/Playable/BladeShield/BladeShield.tscn")
var energized_axe_skill = preload("res://Scenes/Skills/Playable/EnergizedAxe/EnergizedAxe.tscn")
var sharknado_shot_skill = preload("res://Scenes/Skills/Playable/SharknadoShot/SharknadoShot.tscn")
var blood_slash_skill = preload("res://Scenes/Skills/Playable/BloodSlash/BloodSlash.tscn")


var rush_skill = preload("res://Scenes/Skills/Auras/Rush/Rush.tscn")
var rush_tex = preload("res://sprites/status_effects/rush.png")
var regeneration_skill = preload("res://Scenes/Skills/Auras/Regeneration/Regeneration.tscn")
var regeneration_tex = preload("res://sprites/status_effects/regeneration.png")
var resilience_skill = preload("res://Scenes/Skills/Auras/Resilience/Resilience.tscn")
var resilience_tex = preload("res://sprites/status_effects/resilience.png")
var sturdiness_tex = preload("res://sprites/status_effects/sturdiness.png")
var sturdiness_skill = preload("res://Scenes/Skills/Auras/Sturdiness/Sturdiness.tscn")
var elusiveness_tex = preload("res://sprites/status_effects/elusiveness.png")
var elusiveness_skill = preload("res://Scenes/Skills/Auras/Elusiveness/Elusiveness.tscn")
var amplification_tex = preload("res://sprites/status_effects/amplification.png")
var amplification_skill = preload("res://Scenes/Skills/Auras/AmplificationAura/AmplificationAura.tscn")
var honing_skill = preload("res://Scenes/Skills/Auras/Honing/Honing.tscn")
var honing_tex = preload("res://sprites/status_effects/honing.png")
var physical_aura_skill = preload("res://Scenes/Skills/Auras/PhysicalAura/PhysicalAura.tscn")
var physical_aura_tex = preload("res://sprites/status_effects/physical_aura.png")
var lightning_aura_skill = preload("res://Scenes/Skills/Auras/LightningAura/LightningAura.tscn")
var lightning_aura_tex = preload("res://sprites/status_effects/lightning_aura.png")
var cold_aura_skill = preload("res://Scenes/Skills/Auras/ColdAura/ColdAura.tscn")
var cold_aura_tex = preload("res://sprites/status_effects/cold_aura.png")
var fire_aura_skill = preload("res://Scenes/Skills/Auras/FireAura/FireAura.tscn")
var fire_aura_tex = preload("res://sprites/status_effects/fire_aura.png")
var toxic_aura_skill = preload("res://Scenes/Skills/Auras/ToxicAura/ToxicAura.tscn")
var toxic_aura_tex = preload("res://sprites/status_effects/toxic_aura.png")
var dot_aura_skill = preload("res://Scenes/Skills/Auras/DoTAura/DoTAura.tscn")
var dot_aura_tex = preload("res://sprites/status_effects/dot_aura.png")

var config = {
				"Orb": {
								"name": "Lava Orb", 
								"description": "Cast a ball of magma at a nearby enemy, with a chance to set them on fire.", 
								"skill_scene": orb_skill, 
								"skill_texture": orb_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.FIRE, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.CASTABLE, SkillTags.Tags.FIRE, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 










				"ChainLightning": {
								"name": "Chain Lightning", 
								"description": "Cast a surge of lightning towards an enemy, chaining to multiple enemies.", 
								"skill_scene": chain_lightning_skill, 
								"skill_texture": chain_lightning_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.LIGHTNING, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.CASTABLE, SkillTags.Tags.CHAINING, SkillTags.Tags.LIGHTNING, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"LightningSpear": {
								"name": "Lightning Spear", 
								"description": "Throw a spear of pure lightning, inflicting powerful Lightning ailments. If Lightning Spear hits an enemy affected by Jolt, it will consume the Jolt to deal 200% of the Jolts effect as More Damage.", 
								"skill_scene": lightning_spear_skill, 
								"skill_texture": lightning_spear_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.LIGHTNING, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.CASTABLE, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.LIGHTNING, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"FlameTether": {
								"name": "Flame Tether", 
								"description": "Tether yourself to nearby enemies, dealing damage to them. Enemies affected by Flame Tethers deal 25% Less Damage.", 
								"skill_scene": flame_tether_skill, 
								"skill_texture": flame_tether_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.FIRE, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.AREA, SkillTags.Tags.FIRE, SkillTags.Tags.DOT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL], 
								"playable": true, 
				}, 
				"LavaSurge": {
								"name": "Lava Surge", 
								"description": "Channel a stream of Lava towards a nearby enemy, dealing massive Fire damage in an area.", 
								"skill_scene": lava_surge_skill, 
								"skill_texture": lava_surge_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.FIRE, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.AREA, SkillTags.Tags.FIRE, SkillTags.Tags.DOT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL], 
								"playable": true, 
				}, 
				"DoomTether": {
								"name": "Doom Tether", 
								"description": "Tether yourself to nearby enemies, periodically causing damage. If the enemy is cursed, then Doom Tether will deal 50% More Damage for each Curse on the enemy, and deal damage in an area.", 
								"skill_scene": doom_tether_skill, 
								"skill_texture": doom_tether_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.TOXIC, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.CASTABLE, SkillTags.Tags.AREA, SkillTags.Tags.TOXIC, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING], 
								"playable": true, 
				}, 
				"IceOrb": {
								"name": "Frost Orb", 
								"description": "Cast a ball of ice at a nearby enemy. Deals 25% splash damage. Frost Orb cannot pierce or chain.", 
								"skill_scene": iceorb_skill, 
								"skill_texture": iceorb_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.COLD, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CASTABLE, SkillTags.Tags.AREA, SkillTags.Tags.COLD, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"ShardOrb": {
								"name": "Icy Shard Burst", 
								"description": "Cast a volatile ball of ice at a nearby enemy, which releases shards in random directions, having a high chance to Freeze. Extra projectiles affect the number of released shards. Shards cannot pierce or chain.", 
								"skill_scene": shard_orb_skill, 
								"skill_texture": shard_orb_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.COLD, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CASTABLE, SkillTags.Tags.COLD, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"ShockOrb": {
								"name": "Static Charges", 
								"description": "Cast statically charged particles around you. Charges cannot Chain.", 
								"skill_scene": shockorb_skill, 
								"skill_texture": shockorb_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.LIGHTNING, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CASTABLE, SkillTags.Tags.LIGHTNING, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Volcano": {
								"name": "Vesuvius", 
								"description": "A volcanic eruption spews orbs of magma which explode after a short delay, damaging nearby enemies. Cast speed increases the rate of magma orbs spewing.", 
								"skill_scene": volcano_skill, 
								"skill_texture": volcano_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.FIRE, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CASTABLE, SkillTags.Tags.DURATION, SkillTags.Tags.AREA, SkillTags.Tags.FIRE, SkillTags.Tags.BOMB, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL], 
								"playable": true, 
				}, 
				"Arc": {
								"name": "Arc", 
								"description": "Sparks shock nearby enemies, dealing more damage to closer enemies.", 
								"skill_scene": arc_skill, 
								"skill_texture": arc_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.LIGHTNING, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.HIT, SkillTags.Tags.LIGHTNING, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Axe": {
								"name": "Battle Axe", 
								"description": "Throws a slow, heavy axe dealing extremely high damage.", 
								"skill_scene": axe_skill, 
								"skill_texture": axe_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"BladeShield": {
								"name": "Blade Shield", 
								"description": "Summon an ethereal Blade to protect you, dealing Physical Damage to enemies hit by the blade. Blade Shield is unaffected by Cast Speed. Extra Projectiles reduce the cooldown instead.", 
								"skill_scene": blade_shield_skill, 
								"skill_texture": blade_shield_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.MELEE, SkillTags.Tags.DURATION, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING], 
								"playable": true, 
				}, 
				"ShrapnelBomb": {
								"name": "Shrapnel Bomb", 
								"description": "Throws a single explosive bomb which detonates after a delay, dealing massive damage. Shrapnel Bomb is not affected by extra projectiles.", 
								"skill_scene": shrapnelbomb_skill, 
								"skill_texture": shrapnelbomb_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.PHYSICAL, SkillTags.Tags.CASTABLE, SkillTags.Tags.HIT, SkillTags.Tags.BOMB, SkillTags.Tags.AREA, SkillTags.Tags.DAMAGING], 
								"playable": true, 
				}, 
				"ClusterBombs": {
								"name": "Cluster Bombs", 
								"description": "Throws a cluster of charged bombs which detonates, dealing damage in an area.", 
								"skill_scene": cluster_bombs_skill, 
								"skill_texture": cluster_bombs_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.LIGHTNING, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.LIGHTNING, SkillTags.Tags.CASTABLE, SkillTags.Tags.HIT, SkillTags.Tags.BOMB, SkillTags.Tags.AREA, SkillTags.Tags.DAMAGING], 
								"playable": true, 
				}, 
				"Shotgun": {
								"name": "Shotgun", 
								"description": "Short range, high damage skill.", 
								"skill_scene": shotgun_skill, 
								"skill_texture": shotgun_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Minigun": {
								"name": "Minigun", 
								"description": "Rapid fire weapon.", 
								"skill_scene": minigun_skill, 
								"skill_texture": minigun_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"PoisonDart": {
								"name": "Poison Darts", 
								"description": "Poison an enemy for a duration.", 
								"skill_scene": poison_dart_skill, 
								"skill_texture": poison_dart_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.TOXIC, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.CASTABLE, SkillTags.Tags.TOXIC, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Shuriken": {
								"name": "Shuriken", 
								"description": "Inflict a high damage bleed on an enemy.", 
								"skill_scene": shuriken_skill, 
								"skill_texture": shuriken_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Shockwave": {
								"name": "Shockwave", 
								"description": "Slam the ground and release a powerful shock wave towards a nearby enemy, dealing damage in an area.", 
								"skill_scene": shockwave_skill, 
								"skill_texture": shockwave_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.AREA, SkillTags.Tags.MELEE, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Blizzard": {
								"name": "Blizzard", 
								"description": "Chill and damage enemies in an area.", 
								"skill_scene": blizzard_skill, 
								"skill_texture": blizzard_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.COLD, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.DURATION, SkillTags.Tags.DOT, SkillTags.Tags.COLD, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL], 
								"playable": true, 
				}, 
				"PlagueClouds": {
								"name": "Plague Clouds", 
								"description": "Leave a trail of toxic poison in your wake. All damage dealt by Plague Clouds is affected by Toxic Ailment Effect.", 
								"skill_scene": plague_clouds_skill, 
								"skill_texture": plague_clouds_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.TOXIC, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.AREA, SkillTags.Tags.DURATION, SkillTags.Tags.DOT, SkillTags.Tags.PASSIVE, SkillTags.Tags.TOXIC, SkillTags.Tags.DAMAGING], 
								"playable": true, 
				}, 
				"Debilitate": {
								"name": "Debilitation Curse", 
								"description": "Curse enemies in an area with Debilitation, reducing their damage by 20%", 
								"skill_scene": debilitate_skill, 
								"skill_texture": debilitate_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Hinder": {
								"name": "Hindering Curse", 
								"description": "Curse enemies in an area with Hinder, reducing their movement speed by 30%.", 
								"skill_scene": hinder_skill, 
								"skill_texture": hinder_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Brittle": {
								"name": "Brittle Curse", 
								"description": "Curse enemies in an area with Brittle, increasing their damage taken by 20%.", 
								"skill_scene": brittle_skill, 
								"skill_texture": brittle_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Scorch": {
								"name": "Scorch Curse", 
								"description": "Curse enemies in an area with Scorch, lowering their Fire Resistance by 10%.", 
								"skill_scene": scorch_skill, 
								"skill_texture": scorch_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Protract": {
								"name": "Protracting Curse", 
								"description": "Curse enemies in an area with Protraction, increasing duration of effects on them by 30%.", 
								"skill_scene": protraction_skill, 
								"skill_texture": protraction_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Bane": {
								"name": "Bane Curse", 
								"description": "Curse enemies in an area with Bane, lowering their Toxic Resistance by 10%.", 
								"skill_scene": bane_skill, 
								"skill_texture": bane_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Polarize": {
								"name": "Polarize Curse", 
								"description": "Curse enemies in an area with Polarize, lowering their Lightning Resistance by 10%.", 
								"skill_scene": polarize_skill, 
								"skill_texture": polarize_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Hypothermia": {
								"name": "Hypothermia Curse", 
								"description": "Curse enemies in an area with Hyptothermia, lowering their Cold Resistance by 10%.", 
								"skill_scene": hypothermia_skill, 
								"skill_texture": hypothermia_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AREA, SkillTags.Tags.CASTABLE, SkillTags.Tags.CURSE, SkillTags.Tags.DURATION, SkillTags.Tags.UTILITY, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"Arrow": {
								"name": "Arrow Draw", 
								"description": "Fires an arrow dealing high physical damage.", 
								"skill_scene": arrow_skill, 
								"skill_texture": bow_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CHAINING, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"SharknadoShot": {
								"name": "Sharknado Shot", 
								"description": "Fires a mother shark at a nearby enemy, releasing a burst of dangerous baby sharks at nearby enemies.", 
								"skill_scene": sharknado_shot_skill, 
								"skill_texture": sharknado_shot_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.PROJECTILE, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 

				
				"PrismaticSlash": {
								"name": "Prismatic Slash", 
								"description": "Slash in an arc towards a nearby enemy, dealing damage in a cone. All Damage is applied as Fire, Lightning, or Cold at random. Every 3rd attack always inflicts a Critical Strike.", 
								"skill_scene": prismatic_slash_skill, 
								"skill_texture": prismatic_slash_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.MELEE, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.LIGHTNING, SkillTags.Tags.COLD, SkillTags.Tags.FIRE, SkillTags.Tags.HIT, SkillTags.Tags.AREA, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"EnergizedAxe": {
								"name": "Energized Axe", 
								"description": "Swing a Lightning Infused Axe in an arc towards nearby enemies.", 
								"skill_scene": energized_axe_skill, 
								"skill_texture": energized_axe_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.LIGHTNING, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.MELEE, SkillTags.Tags.CASTABLE, SkillTags.Tags.LIGHTNING, SkillTags.Tags.HIT, SkillTags.Tags.AREA, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 
				"BloodSlash": {
								"name": "Lacerating Slash", 
								"description": "Swing a serrated blade at nearby enemies, dealing damage with a chance to inflict Bleeds.", 
								"skill_scene": blood_slash_skill, 
								"skill_texture": blood_slash_tex, 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.PHYSICAL, 
								"tags": [SkillTags.Tags.ATTACK, SkillTags.Tags.MELEE, SkillTags.Tags.CASTABLE, SkillTags.Tags.PHYSICAL, SkillTags.Tags.HIT, SkillTags.Tags.AREA, SkillTags.Tags.DAMAGING, SkillTags.Tags.TRIGGERABLE], 
								"playable": true, 
				}, 

				
				"Rush": {
								"name": "Rush Aura", 
								"description": "You and nearby allies move faster.", 
								"skill_scene": rush_skill, 
								"skill_texture": rush_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"Regeneration": {
								"name": "Regeneration Aura", 
								"description": "You and nearby allies regenerate life.", 
								"skill_scene": regeneration_skill, 
								"skill_texture": regeneration_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"Resilience": {
								"name": "Resilience Aura", 
								"description": "You and nearby allies have a reduced chance to be inflicted by ailments.", 
								"skill_scene": resilience_skill, 
								"skill_texture": resilience_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"Sturdiness": {
								"name": "Sturdiness Aura", 
								"description": "You and nearby allies gain Armor.", 
								"skill_scene": sturdiness_skill, 
								"skill_texture": sturdiness_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"Elusiveness": {
								"name": "Elusiveness Aura", 
								"description": "You and nearby allies gain Evasion.", 
								"skill_scene": elusiveness_skill, 
								"skill_texture": elusiveness_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"Honing": {
								"name": "Honing Aura", 
								"description": "You and nearby allies gain Critical Strike Chance and Cast Speed.", 
								"skill_scene": honing_skill, 
								"skill_texture": honing_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"AmplificationAura": {
								"name": "Amplification Aura", 
								"description": "You and nearby allies gain More Damage.", 
								"skill_scene": amplification_skill, 
								"skill_texture": amplification_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"PhysicalAura": {
								"name": "Metallic Aura", 
								"description": "You and nearby allies gain bonuses with Physical Damage.", 
								"skill_scene": physical_aura_skill, 
								"skill_texture": physical_aura_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"LightningAura": {
								"name": "Static Aura", 
								"description": "You and nearby allies gain bonuses with Lightning Damage.", 
								"skill_scene": lightning_aura_skill, 
								"skill_texture": lightning_aura_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"ColdAura": {
								"name": "Frigid Aura", 
								"description": "You and nearby allies gain bonuses with Cold Damage", 
								"skill_scene": cold_aura_skill, 
								"skill_texture": cold_aura_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"FireAura": {
								"name": "Flame Aura", 
								"description": "You and nearby allies gain bonuses with Fire Damage.", 
								"skill_scene": fire_aura_skill, 
								"skill_texture": fire_aura_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"ToxicAura": {
								"name": "Vile Aura", 
								"description": "You and nearby allies gain bonuses with Toxic Damage.", 
								"skill_scene": toxic_aura_skill, 
								"skill_texture": toxic_aura_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 
				"DoTAura": {
								"name": "Contagion Aura", 
								"description": "You and nearby allies gain bonuses with Damage over Time.", 
								"skill_scene": dot_aura_skill, 
								"skill_texture": dot_aura_tex, 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": true, 
				}, 

				
				"DreadAura": {
								"name": "Dread Aura", 
								"description": "Nearby Enemies are afflicted by Dread. Dread causes Enemies to take 25% More Damage per unique Non-Enhanced Elemental Ailment on them.", 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": false, 
				}, 
				"BloodArmorExplosion": {
								"name": "Blood Burst", 
								"description": "Release an explosion of Boiling Blood, dealing base 250% of your Maximum Life as Fire Damage to nearby Enemies. Blood Burst always inflicts Burn.", 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.FIRE, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.AREA, SkillTags.Tags.HIT, SkillTags.Tags.FIRE, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL], 
								"playable": false, 
				}, 
				"VileDomainAura": {
								"name": "Vile Domain", 
								"description": "Nearby Enemies count as Poisoned. Nearby Enemies take 20% More Damage.", 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": false, 
				}, 
				"EnergeticFlesh": {
								"name": "Energetic Flesh", 
								"description": "Nearby Jolted Enemies take 300% of your Maximum Life as Lightning Damage per Second. Deals More Damage equal to your Lightning Ailment Effect.", 
								"type": Constants.ItemType.SKILL, 
								"damage_tag": SkillTags.Tags.LIGHTNING, 
								"tags": [SkillTags.Tags.SPELL, SkillTags.Tags.AREA, SkillTags.Tags.LIGHTNING, SkillTags.Tags.DOT, SkillTags.Tags.DAMAGING, SkillTags.Tags.ELEMENTAL], 
								"playable": false, 
				}, 
				"BondedElectrons": {
								"name": "Bonded Electrons", 
								"description": "Nearby Enemies have Lightning Resistance equal to yours.", 
								"type": Constants.ItemType.SKILL, 
								"tags": [SkillTags.Tags.AURA, SkillTags.Tags.AREA, SkillTags.Tags.PASSIVE, SkillTags.Tags.UTILITY], 
								"playable": false, 
				}
}

var skill_stat_names = {
				"damage": "Damage", 
				"projectile_count": "Projectiles", 
				"skill_pierce": "Pierce", 
				"projectile_speed": "Projectile Speed", 
				"base_duration": "Duration", 
				"radius": "Skill Radius", 
				"cooldown": "Cooldown", 
				"curse_effect": "Curse Effect", 
}

func render_tier_diff(tiers, current_tier):
				var built_string = ""

				var current_tier_info = tiers[current_tier]

				if current_tier == 0:
								
								for stat in current_tier_info.skill:
												built_string += render_tier_skill_buff(stat) + ": " + StatsInfo.render_skill_stat_line(stat, current_tier_info.skill[stat]) + "\n"
				else:
								var prior_tier_info = tiers[current_tier - 1]
								for stat in current_tier_info.skill:
												if prior_tier_info.skill[stat] == current_tier_info.skill[stat]:
																
																pass
												else:
																built_string += render_tier_skill_buff(stat) + ": " + StatsInfo.render_skill_stat_line(stat, prior_tier_info.skill[stat]) + " -> " + StatsInfo.render_skill_stat_line(stat, current_tier_info.skill[stat]) + "\n"

				return built_string

func render_tier_skill_buff(stat):
				if skill_stat_names.has(stat):
								return skill_stat_names[stat]

				if StatsInfo.stat_name.has(stat):
								return StatsInfo.stat_name[stat]

				return "Unknown stat:" + stat

func render_tier_player_buff(stat, meta, current_tier_info):
				var amount = meta.amount
				var type = meta.type
				var prior_amount = null
				var prior_type = null
				var has_prior_info = false
				if current_tier_info != null:
								if current_tier_info.player.has(stat):
												has_prior_info = true
												prior_amount = current_tier_info.player[stat].amount

				var render_color = Colors.buffed
				var amount_string = StatsInfo.render_item_stat_line(stat, meta)
				var final_amount_string = amount_string
				if has_prior_info:
								if amount < prior_amount:
												render_color = Colors.nerfed
								final_amount_string = StatsInfo.render_item_stat_line(stat, current_tier_info.player[stat]) + " -> " + amount_string
				elif amount < 0:
								render_color = Colors.nerfed

				if not StatsInfo.stat_name.has(stat):
								final_amount_string += " Unknown"


				return {
								"text": final_amount_string, 
								"color": render_color
				}

func tier_for_level(level):
				return max(0, min(49, floor(level / 3)))
