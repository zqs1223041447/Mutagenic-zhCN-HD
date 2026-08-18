extends PopupBase

var mtx_item = preload("res://Scenes/Popups/Dialogs/MTXStore/MTXItem.tscn")
onready var mtx_grid = $MarginContainer / CenterContainer / PanelContainer / VBoxContainer / MTXItemContainer

func _ready() -> void :
				$MarginContainer / CenterContainer / PanelContainer / VBoxContainer / HBoxContainer / CloseButton.grab_focus()
				if not Constants.ENABLE_MTX_SHOP or not Constants.USE_STEAM:
								PopupManager.pop_popup()
								return

				MtxManager.connect("inventory_changed", self, "_render_shop")
				MtxManager.connect("shop_changed", self, "_render_shop")
				_render_shop()

func _on_CloseButton_pressed() -> void :
				PopupManager.pop_popup()

func _render_shop():
				for child in mtx_grid.get_children():
								child.queue_free()

				for item in MtxManager.get_all_mtx():
								var shop_item = mtx_item.instance()
								shop_item.currency_string = MtxManager.currency_string
								shop_item.currency_cents = item.price
								shop_item.item_id = item.item
								mtx_grid.add_child(shop_item)
