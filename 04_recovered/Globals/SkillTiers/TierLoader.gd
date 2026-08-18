extends Node
class_name TierLoader

var tiers = []

func _load_json_data(skill):
				var f = File.new()
				var datafile = "res://skillgen/skills/%s.json" % skill
				f.open(datafile, File.READ)
				if f.file_exists(datafile):
								var data = f.get_as_text()
								var json = JSON.parse(data)
								if json.error == OK and typeof(json.result) == TYPE_ARRAY:
												print("Loaded data for ", skill)
												tiers = json.result
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
