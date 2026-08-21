extends Node

signal inventory_changed
signal stash_changed

func get_free_inventory_slot():
				
				return null

func get_free_stash_slot():
				
				return null

func sort_inventory():
				
				pass

func sort_stash():
				
				pass

func equip_item(gene_id, slot):
				
				pass

func unequip_item(gene_id):
				
				pass

func is_item_equipped(gene_id):
				
				return false

func move_item_to_inventory(gene_id, location: Array):
				
				pass

func move_item_to_stash(gene_id, location: Array):
				
				pass

func move_item_to_ground(gene_id):
				
				pass
