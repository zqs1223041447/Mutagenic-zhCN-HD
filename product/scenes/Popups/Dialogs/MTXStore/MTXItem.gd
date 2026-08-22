extends VBoxContainer


var item_id = 0
var currency_cents = 0
var currency_string = ""



func _ready() -> void :
				$PriceLabel.text = str(snapped(currency_cents / 100.0, 0.01)) + " " + currency_string
				$NameLabel.text = MtxManager.MTX_DEFINITIONS[item_id].name

				if not MtxManager.is_item_purchased(item_id):
								$PurchaseButton.visible = true
				else:
								$PriceLabel.text = "Owned"
								$PriceLabel.modulate = Colors.buffed

func _on_Button_pressed() -> void :
				print("Purchase button clicked.")
				MtxManager.try_purchase_item(item_id)
