extends CanvasLayer

signal show_info

var stats
var gear
var player

var context_entity = null

var mtx_menu = preload("res://scenes/Popups/Dialogs/MTXStore/MTXStore.tscn")
var escape_menu = preload("res://scenes/Popups/EscapeMenu.tscn")
var loadout_menu = preload("res://scenes/Popups/Dialogs/GeneEditor/GeneLoadout.tscn")
var message_scene = preload("res://scenes/GUI/NotificationMessage.tscn")
var skilldisplay = preload("res://scenes/GUI/SkillDisplay.tscn")
var buff_display = preload("res://scenes/GUI/BuffDisplay.tscn")

var status_display = preload("res://scenes/GUI/StatusDisplay.tscn")

@onready var world = GameState.get_global("world")

@onready var skillcontainer = $SkillBar/PanelContainer/VBoxContainer/SkillContainer/WeaponContainer
@onready var buffbar = $BuffContainer/VBoxContainer/MarginContainer/BuffBar
@onready var xp_label = $SkillBar/PanelContainer/VBoxContainer/VBoxContainer/MutationInfoContainer/MutationXP
@onready var xp_bar = $SkillBar/PanelContainer/VBoxContainer/VBoxContainer/MutationInfoContainer/MutationTierXP
@onready var globe = $Globe
@onready var context_label = $MarginContainer/VBoxContainer/ContextDisplay/ContextContainer/ContextLabel
@onready var status_effect_list = $MarginContainer/VBoxContainer/StatusContainer/StatusEffectsList


class SkillSorter:
				static func sort_by_damage(a, b):
								return a.total_damage > b.total_damage

func _ready() -> void :
				# P4-A lane A: readability + screen feedback surfaces
				var feedback_config: P4FeedbackConfig = preload("res://scenes/GUI/Feedback/p4_feedback_config.tres")
				var vignette: P4VignetteOverlay = preload("res://scenes/GUI/Feedback/VignetteOverlay.gd").new()
				vignette.config = feedback_config
				vignette.add_to_group("p4_vignette")
				add_child(vignette)
				var enemy_feedback: P4EnemyFeedbackController = preload("res://scenes/GUI/Feedback/EnemyFeedbackController.gd").new()
				enemy_feedback.config = feedback_config
				enemy_feedback.add_to_group("p4_feedback_controller")
				add_child(enemy_feedback)

				Globals.connect("context_changed", Callable(self, "_update_context"))
				Globals.connect("context_entity_changed", Callable(self, "_update_context_entity"))
				Globals.connect("show_notification", Callable(self, "_render_notification"))
				Globals.connect("show_message", Callable(self, "show_message"))

				GameState.connect("account_xp_changed", Callable(self, "_update_mutation_xp"))
				GameState.connect("mutation_tier_increased", Callable(self, "_update_mutation_tier"))
				GameState.connect("settings_changed", Callable(self, "_on_settings_changed"))
				GameState.connect("stage_completion_changed", Callable(self, "_on_stage_completed"))
				GameState.connect("passives_changed", Callable(self, "_update_mutation_tier"))
				Genes.connect("gene_edited", Callable(self, "_update_orbs"))

				$NotificationContainer/NotificationList.connect("child_exiting_tree", Callable(self, "_on_remove_child"))
				$NotificationContainer/NotificationList.connect("child_entered_tree", Callable(self, "_on_add_child"))

				_on_remove_child()

				if not Constants.ENABLE_MTX_SHOP or not Constants.USE_STEAM:
								$SkillBar/PanelContainer/VBoxContainer/SkillContainer/CosmeticButton.visible = false


func bind_player():
				var next_player = GameState.get_global("player")
				if next_player != player:
								player = next_player
								stats = player.stats
								gear = player.get_node("Gear")
								stats.connect("health_changed", Callable(self, "_update_globe"))
								stats.connect("status_effect_changed", Callable(self, "_render_buffs"))
								stats.connect("damage_taken", Callable(self, "_render_damage_notification"))
								stats.connect("kill_change", Callable(self, "_on_stats_changed"))
								stats.connect("orb_pickup", Callable(self, "_render_pickup_notification"))
								stats.connect("orb_pickup", Callable(self, "_update_orbs"))
								player.connect("gear_changed", Callable(self, "_on_gear_changed"))

				self._update_globe()
				self._on_stats_changed()
				self._render_buffs()

				_on_settings_changed()
				_update_mutation_xp()
				_update_mutation_tier()
				_on_gear_changed()
				_update_orbs()


func _on_level_changed():
				$LevelInfoContainer/MarginContainer/LevelInfo/ZoneLevel/LevelLabel.text = str(Globals.zone_level)
				$LevelInfoContainer/MarginContainer/LevelInfo/ZoneName/NameLabel.text = Levels.get_current_level_name()
				bind_player()

				if Levels.is_current_level_arena():
								show_message("Defeat the Mutant")
				elif not Levels.is_current_level_ladder() and not Levels.is_current_level_hideout() and not StageProgress.is_stage_completed(GameState.get_global("active_stage_id")):
								show_message("Slay 250 Enemies to Complete Stage")
				elif Levels.is_current_level_hideout():
								show_message("Your Hideout")
				elif Levels.is_current_level_ladder():
								show_message("Survive Endless Waves of Enemies")

func _on_settings_changed():
				$Globe.visible = GameState.saved_stats.settings.enable_health_globe

func _update_mutation_xp():
				if GameState.get_active_stats().account_level == 150:
								xp_label.text = "Maxed"
				else:
								xp_label.text = str(floor(GameState.get_active_stats().account_xp)) + " / " + str(floor(GameState.get_active_stats().account_xp_next))
				xp_bar.value = 100.0 * GameState.get_active_stats().account_xp / GameState.get_active_stats().account_xp_next

func _update_mutation_tier():
				var st = GameState.get_active_stats()
				var cn = st.mutation_tree_loadout. class 
				var spec = st.specialization_loadout. class 
				$SkillBar/PanelContainer/VBoxContainer/VBoxContainer/MutationInfoContainer/MutationTierLabel.text = "Level: " + str(st.account_level) + "\n" + PlayableClasses.get_class_name(cn, spec)

func _refresh_on_new_map():
				_on_stats_changed()
				update_completion_status(GameState.get_global("active_stage_id"))

func _on_stats_changed():
				$LevelInfoContainer/MarginContainer/LevelInfo/ZoneKills/KillLabel.text = str(Globals.stage_kills)

func _update_globe():
				globe.update_progress(stats.health, stats.gs("health_max"))

func _render_buffs():
				for child in buffbar.get_children():
								child.queue_free()

				var stackable_buffs = {}

				for status_effect in player.stats.get_status_effects():
								var effect = status_effect.get_ref()
								if effect:
												if effect.texture == null:
																continue
												else:
																if effect.stack_group:
																				if stackable_buffs.has(effect.stack_group):
																								var buff = stackable_buffs[effect.stack_group]
																								buff.buff_count += 1
																								buff.update_count()
																				else:
																								var buff = buff_display.instantiate()
																								buff.effect = effect
																								buff.texture = effect.texture
																								buff.buff_count = 1
																								buffbar.add_child(buff)
																								stackable_buffs[effect.stack_group] = buff
																else:
																				
																				var buff = buff_display.instantiate()
																				buff.effect = effect
																				buff.texture = effect.texture
																				if effect.does_ramp:
																								buff.buff_count = effect.n_applications
																								buff.update_count()
																				buffbar.add_child(buff)

func _on_gear_changed():
				for n in skillcontainer.get_children():
								n.queue_free()

				var sorted_gear = gear.get_children()
				sorted_gear.sort_custom(SkillSorter.sort_by_damage)

				for item in sorted_gear:
								if item.is_queued_for_deletion():
												continue
								var display = skilldisplay.instantiate()
								display.tier = item.get_effective_tier()
								display.texture = item.texture
								display.item = item
								if Skills.config[item.name].type == Constants.ItemType.SKILL:
												skillcontainer.add_child(display)

func _update_context(text):
				if text == "":
								$MarginContainer/VBoxContainer/ContextDisplay/ContextContainer.visible = false
				else:
								$MarginContainer/VBoxContainer/ContextDisplay/ContextContainer.visible = true
								context_label.text = text

func _on_stage_completed(stage_id):
				var stage_level = WorldMapUtils.get_stage_level(stage_id)
				var stage_name = Levels.get_current_level_name()
				show_message("Completed Zone Level " + str(stage_level) + " " + stage_name, Colors.buffed)
				update_completion_status(stage_id)

func update_completion_status(stage_id):
				if StageProgress.is_stage_completed(stage_id):
								$LevelInfoContainer/MarginContainer/LevelInfo/ZoneCompletion/CompletionLabel.set("custom_colors/font_color", Colors.buffed)
								$LevelInfoContainer/MarginContainer/LevelInfo/ZoneCompletion/CompletionLabel.text = "Yes"
				else:
								$LevelInfoContainer/MarginContainer/LevelInfo/ZoneCompletion/CompletionLabel.set("custom_colors/font_color", Colors.nerfed)
								$LevelInfoContainer/MarginContainer/LevelInfo/ZoneCompletion/CompletionLabel.text = "No"

				if Levels.is_current_level_hideout():
								$LevelInfoContainer/MarginContainer/LevelInfo/ZoneCompletion.visible = false
				else:
								$LevelInfoContainer/MarginContainer/LevelInfo/ZoneCompletion.visible = true

func _render_damage_notification(amounts, attacker_stats, was_crit):
				var content = message_scene.instantiate()
				$NotificationContainer/NotificationList.add_child(content)
				content.add_text("Took ")
				if was_crit:
								content.push_color(Colors.critical)
								content.add_text("Critical ")
								content.pop()
				var types = amounts.keys()
				for i in range(len(types)):
								var type = types[i]
								content.push_color(Colors.color_for_skill_tag[type])
								content.add_text(str(snapped(amounts[type], 0.1)))
								content.pop()
								if i < len(amounts) - 1:
												content.add_text(" +")
				content.add_text(" Hit Damage")
				trim_notifications()

func _render_pickup_notification(orb_type, amount):
				var content = message_scene.instantiate()
				$NotificationContainer/NotificationList.add_child(content)
				content.add_text("Picked up ")
				content.add_text(str(amount) + " ")
				content.push_color(Colors.orb)
				content.add_text(Constants.OrbName[orb_type])
				content.pop()

				trim_notifications()

func _render_notification(notif):
				$NotificationContainer/NotificationList.add_child(notif)
				trim_notifications()

func show_message(message, color = Color.WHITE):
				$CanvasLayer/CenterContainer/MessageList/MessageLabel.text = message
				$CanvasLayer/CenterContainer/MessageList/MessageLabel.visible = true
				$CanvasLayer/CenterContainer/MessageList/MessageLabel.set("custom_colors/font_color", color)
				var t = Timer.new()
				t.autostart = true
				t.wait_time = 5.0
				add_child(t)
				await t.timeout
				$CanvasLayer/CenterContainer/MessageList/MessageLabel.visible = false
				t.queue_free()

func trim_notifications():
				var n_children = $NotificationContainer/NotificationList.get_child_count()
				var to_trim = max(0, n_children - 10)

				var children_to_remove = []
				for i in range(to_trim):
								var child = $NotificationContainer/NotificationList.get_child(i)
								children_to_remove.append(child)

				for c in children_to_remove:
								c.queue_free()

func _update_context_entity(entity):
				
				if context_entity != null and is_instance_valid(context_entity):
								context_entity.stats.disconnect("status_effect_changed", self, "update_flags")
								context_entity = null
				if entity:
								context_entity = entity
								entity.stats.connect("status_effect_changed", Callable(self, "update_flags"))
								_update_context(entity.stats.get_entity_name())
								update_flags()
								update_mod_list()
								$MarginContainer/VBoxContainer/MonsterMods.visible = true
								$MarginContainer/VBoxContainer/StatusContainer.visible = true
				else:
								_update_context("")
								update_flags()
								$MarginContainer/VBoxContainer/MonsterMods.visible = false
								$MarginContainer/VBoxContainer/StatusContainer.visible = false

func update_mod_list():
				for child in $MarginContainer/VBoxContainer/MonsterMods.get_children():
								child.queue_free()
				var mods = context_entity.monster_mods
				for i in range(len(mods)):
								var mod = mods[i]
								var label = Label.new()
								label.text = mod.description
								if i < len(mods) - 1:
												label.text += ","
								$MarginContainer/VBoxContainer/MonsterMods.add_child(label)


func update_flags():
				if context_entity == null or not is_instance_valid(context_entity):
								$MarginContainer/VBoxContainer/StatusContainer.visible = false
								return

				for child in status_effect_list.get_children():
								child.queue_free()

				var show_panel = false
				var flags = context_entity.stats.status_flags.keys()
				flags.sort()

				for flag in flags:
								if StatusEffects.should_show_flag(flag):
												var child = status_display.instantiate()
												child.flag = flag
												if context_entity.stats.status_flag_amounts.has(flag):
																child.amount = context_entity.stats.status_flag_amounts[flag]
																status_effect_list.add_child(child)

				if show_panel:
								$MarginContainer/VBoxContainer/StatusContainer/StatusEffectsList.visible = false
				else:
								$MarginContainer/VBoxContainer/StatusContainer/StatusEffectsList.visible = true

func _on_remove_child(_node = null):
				if $NotificationContainer/NotificationList.get_child_count() <= 1:
								$NotificationContainer.visible = false
				else:
								$NotificationContainer.visible = true

func _on_add_child(_node = null):
				$NotificationContainer.visible = true

func _on_MenuButton_pressed() -> void :
				var menu_popup = escape_menu.instantiate()
				PopupManager.show_popup(menu_popup, self)


func _on_GenesButton_pressed() -> void :
				var menu_popup = loadout_menu.instantiate()
				PopupManager.show_popup(menu_popup, self)

func _update_orbs(orb_type = null, amount = null):
				$SkillBar/PanelContainer/VBoxContainer/LootContainer/HBoxContainer/BlueOrbs.text = str(stats.metrics.orbs.blue + GameState.get_active_stats().orbs.blue)
				$SkillBar/PanelContainer/VBoxContainer/LootContainer/HBoxContainer2/RedOrbs.text = str(stats.metrics.orbs.red + GameState.get_active_stats().orbs.red)
				$SkillBar/PanelContainer/VBoxContainer/LootContainer/HBoxContainer3/GreenOrbs.text = str(stats.metrics.orbs.green + GameState.get_active_stats().orbs.green)
				$SkillBar/PanelContainer/VBoxContainer/LootContainer/HBoxContainer4/GoldOrbs.text = str(stats.metrics.orbs.gold + GameState.get_active_stats().orbs.gold)
				$SkillBar/PanelContainer/VBoxContainer/LootContainer/HBoxContainer5/CorruptionShards.text = str(stats.metrics.orbs.corruption + GameState.get_active_stats().orbs.corruption)


func _on_CosmeticButton_pressed() -> void :
				var popup = mtx_menu.instantiate()
				PopupManager.show_popup(popup, self)
