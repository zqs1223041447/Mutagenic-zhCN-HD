extends Node

signal inventory_changed
signal shop_changed
signal purchase_done(success, item_id)

const MTX_DEFINITIONS = {
				1: {
								"name": "Example Item 1", 
				}, 
				2: {
								"name": "Example Item 2", 
				}, 
				100: {
								"name": "Example Item 3", 
				}, 
}

var MTX_PURCHASED = {}

var MTX_FOR_SALE = {}
var inventory_id = null
var loaded_shop = false
var loaded_inventory = false
var currency_string = ""

var Steam = Engine.get_singleton("Steam") if Engine.has_singleton("Steam") else null

func initialize():
				Steam.connect("inventory_full_update", Callable(self, "handle_inventory_full_update"))
				Steam.connect("inventory_request_prices_result", Callable(self, "handle_inventory_request_prices_result"))
				Steam.connect("inventory_start_purchase_result", Callable(self, "handle_inventory_start_purchase_result"))
				Steam.connect("inventory_result_ready", Callable(self, "handle_inventory_result_ready"))
				fetch_items()
				request_prices()




func fetch_items():
				print("Fetching inventory items")
				Steam.getAllItems()

func handle_inventory_full_update(inventory_handle):
				print("handle_inventory_full_update")
				print("Steam inventory result:", Steam.getResultStatus(inventory_handle))
				var items = Steam.getResultItems(inventory_handle)
				for item in items:
								MTX_PURCHASED[item.itemdefid] = item
				Steam.destroyResult(inventory_handle)
				emit_signal("inventory_changed")

func handle_inventory_result_ready(result, inventory_handle):
				print("handle_inventory_result_ready")
				if result == Steam.RESULT_OK:
								var items = Steam.getResultItems(inventory_handle)
								for item in items:
												MTX_PURCHASED[item.itemdefid] = item
				else:
								print("Purchase failed.")

				Steam.destroyResult(inventory_handle)
				emit_signal("inventory_changed")




func request_prices():
				Steam.requestPrices()

func handle_inventory_request_prices_result(result, currency):
				print("handle_inventory_request_prices_result")
				print("Local currency:", currency)
				currency_string = currency
				var n_items = Steam.getNumItemsWithPrices()
				
				var items_for_sale = Steam.getItemsWithPrices(n_items)
				print("Items for sale:", items_for_sale)
				for item in items_for_sale:
								MTX_FOR_SALE[item.item] = item
				emit_signal("shop_changed")



func handle_inventory_start_purchase_result(result, order_id, transaction_id):
				print("Purchase started:", result, " ", order_id, " ", transaction_id)

func try_purchase_item(item_id):
				if MTX_PURCHASED.has(item_id):
								print("MTX Already Owned")
								return false

				print("Starting purchase of item: ", item_id)
				Steam.startPurchase([item_id], 1)

				return true

func get_unpurchased_mtx():
				var available_items = []
				for key in MTX_FOR_SALE:
								if not MTX_PURCHASED.has(key):
												available_items.append(MTX_FOR_SALE[key])
				return available_items

func get_all_mtx():
				var available_items = []
				for key in MTX_FOR_SALE:
								available_items.append(MTX_FOR_SALE[key])
				return available_items

func is_item_purchased(item_def_id):
				return MTX_PURCHASED.has(item_def_id)
