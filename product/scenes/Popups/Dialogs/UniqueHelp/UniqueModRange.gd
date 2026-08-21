extends VBoxContainer

var mod_id
var base_type

@onready var mod_string = $ModString


func _ready() -> void :
				var mods = Genes.mods_for_base_type(base_type)
				var mod = mods.get_unique_mod_info(mod_id)
				render_mod(mod)

func render_mod(mod):
				mod_string.clear()
				mod_string.push_align(RichTextLabel.ALIGN_CENTER)
				
				if mod.has("keystone"):
								mod_string.add_text(Keystones.keystones[mod.keystone].description)
				else:
								
								StatsInfo.render_range_into_rtl(mod.stat, mod, 0, mod_string)
				mod_string.pop()
