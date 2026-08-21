extends Node

var ACHIEVEMENTS = {
				
				"LEVEL_10": false, 
				"LEVEL_20": false, 
				"LEVEL_30": false, 
				"LEVEL_40": false, 
				"LEVEL_50": false, 
				"LEVEL_60": false, 
				"LEVEL_70": false, 
				"LEVEL_90": false, 
				"LEVEL_100": false, 
				"LEVEL_110": false, 
				"LEVEL_120": false, 
				"LEVEL_130": false, 
				"LEVEL_140": false, 
				"LEVEL_150": false, 
}

var ready_to_achieve = false
var achievement_queue = []


func _get_Achievement(value: String) -> void :
				var ACHIEVEMENT: Dictionary = Steam.getAchievement(value)
				
				if ACHIEVEMENT["ret"]:
								
								if ACHIEVEMENT["achieved"]:
												ACHIEVEMENTS[value] = true
								
								else:
												ACHIEVEMENTS[value] = false
				
				else:
								ACHIEVEMENTS[value] = false

func initialize():
				print("Initializing Achievements...")
				if Constants.USE_STEAM:
								Steam.connect("current_stats_received", self, "_is_ready", [], CONNECT_ONESHOT)
								Steam.requestCurrentStats()

func _is_ready(game, result, user):
				
				"""
    for k in ACHIEVEMENTS.keys():
        _get_Achievement(k)
        if ACHIEVEMENTS[k]:
            Steam.clearAchievement(k)
    """

				ready_to_achieve = true

func _process(delta: float) -> void :
				if not ready_to_achieve:
								return
				if len(achievement_queue) > 0:
								var achievement = achievement_queue.pop_back()
								_complete_achievement(achievement)

func queue_achievement(achievement):
				if ACHIEVEMENTS.has(achievement):
								if ACHIEVEMENTS[achievement]:
												return
				print("Achievement Queued: ", achievement)
				achievement_queue.append(achievement)

func _complete_achievement(achievement):
				print("Completing achievement: ", achievement)
				if Constants.USE_STEAM:
								ACHIEVEMENTS[achievement] = true
								Steam.setAchievement(achievement)
								Steam.storeStats()
