extends Node
class_name TierLoader

var tiers = []

func _load_json_data(skill):
				var datafile = "res://skillgen/skills/%s.json" % skill
				var f = FileAccess.open(datafile, FileAccess.READ)
				if FileAccess.file_exists(datafile):
								var data = f.get_as_text()
								var json = JSON.parse_string(data)
								if json.error == OK and typeof(json) == TYPE_ARRAY:
												print("Loaded data for ", skill)
												tiers = json
								else:
												print("Failed to load data for ", skill)
												get_tree().quit()

				transform_for_aura()

func transform_for_aura():
				for tier in tiers:
								if tier.has("aura"):
												for stat in tier.aura:
																for item in tier.aura[stat]:
																				if item.type == "flat":
																								item.type = Constants.ScalingType.FLAT
																				elif item.type == "percent":
																								item.type = Constants.ScalingType.PERCENT
																				elif item.type == "more":
																								item.type = Constants.ScalingType.MORE

func get_tiers():
				return tiers
