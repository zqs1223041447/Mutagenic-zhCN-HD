extends Node


var keystones = {
}


func _ready() -> void :
				
				for keystone in SupportKeystones.keystones:
								keystones[keystone] = SupportKeystones.keystones[keystone].duplicate(true)
				for keystone in TreeKeystones.keystones:
								keystones[keystone] = TreeKeystones.keystones[keystone].duplicate(true)
				for keystone in UniqueKeystones.keystones:
								keystones[keystone] = UniqueKeystones.keystones[keystone].duplicate(true)
