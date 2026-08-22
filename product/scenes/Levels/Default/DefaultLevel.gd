extends BaseLevel

func get_spawnables():
				return spawnables

func _ready():
				
				get_layout_generator().generate(self)

				
				
				process_tiles()

				Globals.set_rich_presence_zone(Globals.zone_level)
