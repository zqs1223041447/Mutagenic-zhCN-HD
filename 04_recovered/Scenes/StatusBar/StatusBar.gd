extends VBoxContainer

onready var brittle = $CenterContainer / HBoxContainer / Brittle
onready var debilitate = $CenterContainer / HBoxContainer / Debilitate
onready var hinder = $CenterContainer / HBoxContainer / Hinder
onready var protract = $CenterContainer / HBoxContainer / Protract
onready var scorch = $CenterContainer / HBoxContainer / Scorch
onready var bane = $CenterContainer / HBoxContainer / Bane
onready var polarize = $CenterContainer / HBoxContainer / Polarize
onready var hypothermia = $CenterContainer / HBoxContainer / Hypothermia
onready var healthbar = $HBoxContainer / Healthbar

var health_max = 0
var health = 0
var need_reset = false

func _ready() -> void :
				if not GameState.is_status_bars_enabled():
								$CenterContainer.visible = false
				else:
								$CenterContainer.visible = true

func update_healthbar(stats):
				health_max = stats.gs("health_max")
				health = stats.health
				need_reset = true

func _process(delta: float) -> void :
				if not need_reset:
								return
				need_reset = false
				if healthbar.max_value != health_max:
								healthbar.max_value = health_max
				if healthbar.value != health:
								healthbar.value = health

				if health == health_max:
								healthbar.modulate.a = 0
				else:
								healthbar.modulate.a = 1

func update_flags(flags):
				if flags.has(Constants.StatusFlags.BRITTLE):
								brittle.visible = true
				else:
								brittle.visible = false

				if flags.has(Constants.StatusFlags.DEBILITATE):
								debilitate.visible = true
				else:
								debilitate.visible = false

				if flags.has(Constants.StatusFlags.PROTRACT):
								protract.visible = true
				else:
								protract.visible = false

				if flags.has(Constants.StatusFlags.HINDER):
								hinder.visible = true
				else:
								hinder.visible = false

				if flags.has(Constants.StatusFlags.SCORCH):
								scorch.visible = true
				else:
								scorch.visible = false

				if flags.has(Constants.StatusFlags.BANE):
								bane.visible = true
				else:
								bane.visible = false

				if flags.has(Constants.StatusFlags.POLARIZE):
								polarize.visible = true
				else:
								polarize.visible = false

				if flags.has(Constants.StatusFlags.HYPOTHERMIA):
								hypothermia.visible = true
				else:
								hypothermia.visible = false

