extends Node


var brittle_texture = preload("res://sprites/skills/brittle.png")
var bane_texture = preload("res://sprites/skills/bane.png")
var debilitate_texture = preload("res://sprites/skills/debilitate.png")
var protract_texture = preload("res://sprites/skills/protraction.png")
var hinder_texture = preload("res://sprites/skills/hinder.png")
var polarize_texture = preload("res://sprites/skills/polarize.png")
var hypothermia_texture = preload("res://sprites/skills/hypothermia.png")
var scorch_texture = preload("res://sprites/skills/scorch.png")

var exposed_texture = preload("res://sprites/buff_icons/exposed.png")
var vulnerable_texture = preload("res://sprites/buff_icons/vulnerable.png")
var hamstrung_texture = preload("res://sprites/status_effects_new/hamstrung.png")

var chilled_texture = preload("res://sprites/status_effects_new/chilled.png")
var frozen_texture = preload("res://sprites/status_effects_new/frozen.png")

var jolt_texture = preload("res://sprites/status_effects_new/jolt.png")
var electrocution_texture = preload("res://sprites/status_effects_new/electrocuted.png")

var burn_texture = preload("res://sprites/status_effects_new/burning.png")
var char_texture = preload("res://sprites/status_effects_new/char.png")

var bleed_texture = preload("res://sprites/status_effects/bleeding.png")
var rupture_texture = preload("res://sprites/status_effects/ruptured.png")

var poisoned_texture = preload("res://sprites/status_effects/poison.png")
var infected_texture = preload("res://sprites/status_effects/infection.png")

var dread_texture = preload("res://sprites/status_effects_new/dread.png")
var transfusion_texture = preload("res://sprites/status_effects_new/transfusion.png")
var blood_boil_texture = preload("res://sprites/status_effects_new/blood_boil.png")
var vile_domain_texture = preload("res://sprites/status_effects_new/vile_domain.png")
var bonded_electrons_texture = preload("res://sprites/status_effects_new/bonded_electrons.png")







































var status_effects = {
				
				Constants.StatusFlags.BRITTLE: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": brittle_texture
				}, 
				Constants.StatusFlags.BANE: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": bane_texture
				}, 
				Constants.StatusFlags.DEBILITATE: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": debilitate_texture
				}, 
				Constants.StatusFlags.PROTRACT: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": protract_texture
				}, 
				Constants.StatusFlags.HINDER: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": hinder_texture
				}, 
				Constants.StatusFlags.POLARIZE: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": polarize_texture
				}, 
				Constants.StatusFlags.HYPOTHERMIA: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": hypothermia_texture
				}, 
				Constants.StatusFlags.SCORCH: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": scorch_texture
				}, 

				Constants.StatusFlags.EXPOSED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": exposed_texture
				}, 
				Constants.StatusFlags.VULNERABLE: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": vulnerable_texture
				}, 
				Constants.StatusFlags.HAMSTRUNG: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": hamstrung_texture
				}, 

				
				Constants.StatusFlags.CHILLED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": chilled_texture
				}, 
				Constants.StatusFlags.FROZEN: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": frozen_texture
				}, 

				
				Constants.StatusFlags.JOLTED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": jolt_texture
				}, 
				Constants.StatusFlags.ELECTROCUTED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": electrocution_texture
				}, 

				
				Constants.StatusFlags.BURNING: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": burn_texture
				}, 
				Constants.StatusFlags.CHARRED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": char_texture
				}, 

				
				Constants.StatusFlags.BLEEDING: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": bleed_texture
				}, 
				Constants.StatusFlags.RUPTURED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": rupture_texture
				}, 

					
				Constants.StatusFlags.POISONED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": poisoned_texture
				}, 
				Constants.StatusFlags.INFECTED: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": infected_texture
				}, 

				
				Constants.StatusFlags.DREAD: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": dread_texture
				}, 
				Constants.StatusFlags.TRANSFUSION: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": transfusion_texture
				}, 
				Constants.StatusFlags.BLOOD_BOIL: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": blood_boil_texture
				}, 
				Constants.StatusFlags.VILE_DOMAIN: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": vile_domain_texture
				}, 
				Constants.StatusFlags.BONDED_ELECTRONS: {
								"type": Constants.ScalingType.PERCENT, 
								"texture": bonded_electrons_texture
				}, 
}

func should_show_flag(flag):
				return status_effects.has(flag)
