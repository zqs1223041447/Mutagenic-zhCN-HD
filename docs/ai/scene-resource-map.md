# Mutagenic 场景与资源引用图(Scene & Resource Map)

> 只读对照：3.5.3 场景/资源「改哪里、依赖什么」。不是任务入口。当前主线见 `AGENT.MD`。  
> 本 clone **没有** `05_schema/game_schema.json`。文中 schema SHA `C4472A29…` 无法就地复核；数字以 `docs/ai/source_index.json` 与 `04_recovered` 为准。  
> 生成日期 2026-08-14。不构成生产输入。

---

## 1. 游戏结构总览

| 项 | 值 |
|---|---|
| 引擎 | Godot 3.5.3 custom_build |
| 主场景 | `res://Scenes/LoadGame.tscn` |
| 场景数 | 356 |
| 场景节点总数 | 2063 |
| 信号连接 | 209 |
| NodePath 引用 | 161 |
| 组声明 | 2 |
| 脚本数(.gd) | 525(Globals 185 / Scenes 326 / addons 14) |
| 资源引用(唯一) | 1371(res:// 引用,123 个未直接解析均已分类,无 UNRESOLVED) |

---

## 2. 重要场景清单(schema `structural_inventory.important_scenes`)

### 2.1 启动与主菜单

| 场景 | 用途 |
|---|---|
| `Scenes/LoadGame.tscn` | **主场景**——游戏启动入口 |
| `Scenes/Menu.tscn` | 主菜单(本地化切片 C5-L1 目标) |
| `Scenes/World.tscn` | 世界根场景 |

### 2.2 角色选择与创建(本地化切片 C5-L2/C5-L3 目标)

| 场景 | 用途 |
|---|---|
| `Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn` | 角色选择主对话框 |
| `Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn` | 角色创建 |
| `Scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.tscn` | 角色切换 |
| `Scenes/Popups/Dialogs/CharacterSelect/CharacterSlot.tscn` | 角色槽位 |
| `Scenes/Popups/Dialogs/CharacterSelect/CharacterClass.tscn` | 职业展示 |

### 2.3 世界地图与关卡

| 场景 | 用途 |
|---|---|
| `Scenes/Popups/Dialogs/WorldMap/WorldMapPopup.tscn` | 世界地图弹窗 |
| `Scenes/Popups/Dialogs/WorldMap/MapNode.tscn` | 地图节点 |
| `Scenes/Popups/Dialogs/WorldMap/Edge.tscn` | 地图连线 |
| `Scenes/Levels/LevelLoader.tscn` | 关卡加载器 |
| `Scenes/Levels/BaseLevel.tscn` | 关卡基类 |
| `Scenes/Levels/Default/DefaultLevel.tscn` | 默认关卡 |
| `Scenes/Levels/Hideout/HideoutLevel.tscn` | 藏身处 |
| `Scenes/Levels/NavMesh.tscn` / `SpawnLocation.tscn` | 导航网格 / 出生点 |
| `Scenes/Levels/Ladder/Ladder.tscn` / `LadderSpawner.tscn` | 天梯模式 |
| `Scenes/Levels/TestLevel/TestLevel.tscn` / `TestSpawner.tscn` | 测试关卡 |
| `Scenes/Levels/BossArenas/BossArena.tscn` | Boss 竞技场基座 |
| `Scenes/Levels/BossArenas/SpiritOfTheAncient/SpiritOfTheAncient.tscn` | 远古之灵竞技场 |

### 2.4 弹窗与杂项

| 场景 | 用途 |
|---|---|
| `Scenes/Popups/EscapeMenu.tscn` | 暂停菜单 |
| `Scenes/Popups/EscapeMenuStat.tscn` | 暂停菜单属性 |
| `Scenes/Popups/Unlocks/CharacterUnlockItem.tscn` | 角色解锁项 |

---

## 3. 关卡配置(schema `levels.config`,20 个)

| id | 显示名 | 布局 | Boss |
|---|---|---|---|
| cave | Chilly Cavern | CIRCLE | — |
| dirt_cave | Musty Den | CIRCLE | — |
| red_cave | Gemling Cave | CIRCLE | — |
| pit | Pit | CIRCLE | — |
| forest | Grasslands | FIELD | — |
| hell | Blood Shrine | CELLS | — |
| catacombs | Catacombs | CELLS | — |
| flats | Field of Despair | FIELD | — |
| sands | Sandstorm | CIRCLE | — |
| dungeon | Dungeon | CELLS | — |
| boss_1 | The Gatekeeper | FIXED | `Scenes/Mobs/Bosses/GateKeeper.tscn` |
| boss_2 | Sludge | FIXED | `Scenes/Mobs/Bosses/Sludge.tscn` |
| boss_3 | Mutated Spider | FIXED | `Scenes/Mobs/Bosses/MutatedSpider.tscn` |
| spirit_of_the_ancient | Spirit of the Ancients | FIXED | `Scenes/Mobs/Bosses/SpiritOfTheAncient.tscn` |
| leaderboard_25/50/75/100 | Challenge Ladder 1-4 | FIXED | — |
| hideout | Hideout | FIXED | — |
| test_level | Testing Zone | FIXED | — |

**世界地图**:59 节点、62 边,root 存在;18 个被动标签(boss_1/2/3、catacombs、cave、dirt_cave、dungeon、flats、forest、hell、leaderboard_*、pit、red_cave、sands、spirit_of_the_ancient)。

---

## 4. 玩家职业与专精(schema `player`)

**4 职业**(`Globals/PlayableClasses.gd`,INFERENCE_HIGH):

| id | 显示名 |
|---|---|
| MAGE | Mage |
| ROGUE | Rogue |
| TANK | Tank |
| WARRIOR | Warrior |

**8 专精**(numeric_id):

| id | 显示名 | numeric_id |
|---|---|---|
| WARLOCK | Warlock | 1 |
| MERCENARY | Mercenary | 2 |
| VAMPIRE | Vampire | 3 |
| MARKSMAN | Marksman | 4 |
| SHAMAN | Shaman | 5 |
| FIEND | Fiend | 6 |
| TITAN | Titan | 7 |
| BATTLEMAGE | Battlemage | 8 |

---

## 5. 技能与状态系统(schema `skills`)

- **技能实体**:53 个(`Globals/Skills.gd` 等)
- **技能支持(supports)**:60 个
- 统计注册表:`Globals/StatsInfo.gd`(FACT,含行号),主要分组:
  - `character_sheet_list` 角色面板属性(health_max、movement_speed、五系抗性、constitution/strength/agility/wisdom/finesse 等)
  - `damage_list` 五系伤害(physical/lightning/cold/fire/toxic)
  - `skill_sort_list` 技能排序属性(crit_chance、cast_speed、area_of_effect、skill_pierce/chain 等)
  - `all_skill_list` / `stat_list` 全量统计键
- 标签枚举 `Tags`(PHYSICAL/LIGHTNING/COLD/FIRE/TOXIC/DAMAGE/PROJECTILE/DEFENCE/CRIT…)

> 本 clone 没有 `05_schema/`。细目以 `04_recovered/Globals/Skills.gd`、`Globals/StatsInfo.gd` 和 `docs/ai/source_index.json` 为准。

---

## 6. 输入与按键(schema `controls`)

**27 个 project 输入动作**(project.godot,全部 FACT):move_up/down/left/right、dash、interact、click、zoom_in/out、ui_open_inventory、ui_open_menu、goto_test_level、gamepad_scroll_up/down 及 Godot 标准 ui_* 动作。

**可配置按键**(`Globals/Keybindings.gd`):interact、dash、move_left、move_right 等(configurable_actions)。

---

## 7. 存档与持久化(schema `save_and_persistence`)

| 组件 | 位置 | 说明 |
|---|---|---|
| checksum/stamp | `Globals/GameState.gd` L158/166 | `compute_checksum` / `compute_stamp` |
| stamp 校验 | `Globals/GameState.gd` L175 | `verify_stamp` |
| 修改标记 | `Globals/GameState.gd` L163 | `mark_modified` |
| 全局配置 | `Globals/GameState.gd` | characters / keybind_overrides / settings |
| 存档路径 | `user://_0_6_0.dat` | 本地分支;`USE_STEAM=false`(P7-FIX)后使用 |

> 运行时存档序列化仍为 UNKNOWN(schema 明确保留)。

---

## 8. 资源构成(`03_raw` 全量)

| 类型 | 数量 | 说明 |
|---|---|---|
| .import | 1119 | 导入 sidecar |
| .gde + .remap | 524 对 | 加密脚本(仅 `PassiveTree.gd` 为纯文本 .gd) |
| .stex | 513 | 纹理资源 |
| .res | 462 | 资源文件 |
| .tscn | 356 | 场景 |
| .sample | 140 | 采样 |
| .json | 61 | 数据注册表 |
| .tres | 30 | 资源 |
| .ttf | 5 | 字体(含 `Fonts/rsans.ttf` 中文字体 overlay) |
| 其他 | 9 | .oggstr/.png/.ico/.binary |

**合计 3744 个运行时路径**(与 `manifests/raw_manifest.json` 一致,FACT)。

---

## 9. 已知未建模项(schema `unknowns`)

1. `runtime_save_serialization` — 运行时存档序列化与 Steam/本地分支行为未执行验证
2. `schema_semantic_completeness` — 尚未穷尽建模所有玩法关系/存档标识/运行时生成值
3. `translation_safety_classification` — 显示/结构字符串分类属于 Phase 5,本 schema 不推断

---

## 10. 定位速查（只读）

这些是 `04_recovered` 里相关系统的入口，给迁移扫描用。不要直接改 `04_recovered`。本 clone 没有 `05_schema/`。

- 主菜单 → `Scenes/Menu.tscn`
- 角色选择 → `Scenes/Popups/Dialogs/CharacterSelect/*` + `Globals/PlayableClasses.gd`
- 技能数值 → `Globals/StatsInfo.gd` / `Globals/Skills.gd`
- 关卡 → `Scenes/Levels/*`
- 存档 → `Globals/GameState.gd`
- 按键 → `Globals/Keybindings.gd`
- 职业 → `Globals/PlayableClasses.gd`
- 装备/掉落 → `Globals/ItemManager.gd` / `Globals/ItemNameGenerator.gd`
