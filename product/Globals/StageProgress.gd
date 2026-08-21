extends Node

func is_stage_completed(stage_id):
				return GameState.get_active_stats().completed_stages.has(stage_id)

func is_neighbor_completed(stage_id):
				var neighbors = WorldMapData.get_neighbors(stage_id)
				for n in neighbors:
								if is_stage_completed(n):
												return true

				return false
