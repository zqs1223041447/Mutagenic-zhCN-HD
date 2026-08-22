extends VBoxContainer


@export var craft_type = ""
var gene_id

func _ready() -> void :
				Genes.connect("gene_edited", Callable(self, "_update_enabled_state"))

				$Crafter.text = Genes.craft_name[craft_type]

				var costs = Genes.craft_costs[craft_type]

				if len(costs) == 0:
								$CostBox/CostLabel.text = "Free"
				else:
								for cost in costs:
												var label = Label.new()
												label.text = str(cost.cost)
												$CostBox.add_child(label)
												var tex = TextureRect.new()
												tex.expand = true
												tex.custom_minimum_size = Vector2(32, 32)
												tex.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
												tex.texture = OrbTypes.texture_for_orb[cost.orb]
												$CostBox.add_child(tex)

func set_gene_id(id):
				
				
				gene_id = id
				_update_enabled_state()

func _update_enabled_state():
				if Genes.can_perform_craft(gene_id, craft_type) and Genes.can_afford_craft(craft_type):
								$Crafter.disabled = false
				else:
								$Crafter.disabled = true

func _on_Crafter_pressed() -> void :
				Genes.purchase_craft(gene_id, craft_type)
