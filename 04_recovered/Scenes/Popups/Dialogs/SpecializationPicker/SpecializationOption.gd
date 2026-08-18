extends VBoxContainer

var specialization_class

func _ready() -> void :
				var cn = PlayableClasses.specialization_name[specialization_class]
				$SpecializationNameLabel.text = cn
				var desc = PlayableClasses.specialization_descriptions[specialization_class]
				$SpecializationDescriptionLabel.text = desc
				$ChooseButton.text = "Specialize as a " + cn

				

func _on_ChooseButton_pressed() -> void :
				GameState.change_specialization(specialization_class)
				PopupManager.pop_popup()
