# Mutagenic 源码地图(Source Map)

> **文档角色**:源码参考工程的核心索引。525 个 .gd 脚本逐文件职责速查表。
> **数据来源**:`docs/ai/source_index.json`(机器提取的元数据)+ 逐目录职责分析(基于函数名/信号/extends 推断,INFERENCE_HIGH)。
> **可信度**:文件路径与函数列表为 FACT(机器提取);职责摘要为 INFERENCE_HIGH(反编译源码无注释,由函数签名推断)。
> **生成日期**:2026-08-14。仅限参考与定位,不构成生产输入(见 AGENTS.md §5.3/§13)。
> **统计**:Globals 185 / Scenes 326(战斗 225 + UI·弹窗 91 + 根级 10)/ addons 14 = 525。

## 目录

- [1. Globals — 全局单例与系统](#1-globals--全局单例与系统)(185)
- [2. Scenes — 战斗/玩法](#2-scenes--战斗玩法)(225)
- [3. Scenes — UI/弹窗/玩家](#3-scenes--ui弹窗玩家)(101)
- [4. addons — 编辑器插件](#4-addons--编辑器插件)(14)

---

## 1. Globals — 全局单例与系统(185)

| 脚本 | extends | 职责摘要 | 关键函数 |
|---|---|---|---|

| Globals/Achievements.gd | Node | Steam成就管理:初始化并排队解锁成就 | _get_Achievement,initialize,_is_ready,_process,queue_achievement |
| Globals/Colors.gd | Node | 定义全局UI/品质/词缀/状态颜色常量 | - |
| Globals/Constants.gd | Node | 全局枚举常量:缩放/物品/词缀/品质/状态 | - |
| Globals/Filters.gd | Node | 判断物品是否应隐藏(低等级过滤) | should_hide_item |
| Globals/GameState.gd | Node | 游戏核心状态:存档/角色/天赋/基因/技能/设置 | _ready,_physics_process,get_save_name,quit,has_save_been_modded |
| Globals/GeneGenerator.gd | Node | 按区域等级随机生成基因(品质/词缀) | generate_random_gene,generate_random_unique,generate_random_rare,generate_random_basic,create_new_gene |
| Globals/Genes.gd | Node | 基因核心管理:创建/词缀/工艺制作 | random_weapon_base_type,mod_sorter,mods_for_base_type,implicit_count_for_base_type,slot_for_base |
| Globals/Genes/BaseTypes/Amulets/AttackAmuletMods.gd | GeneMods | 攻击系护身符基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Amulets/CasterAmuletMods.gd | GeneMods | 施法系护身符基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Amulets/LifeAmuletMods.gd | GeneMods | 生命系护身符基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Amulets/ResistantAmuletMods.gd | GeneMods | 抗性系护身符基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Belts/ArmorBeltMods.gd | GeneMods | 护甲腰带基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Belts/CasterBeltMods.gd | GeneMods | 施法腰带基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Belts/EvasionBeltMods.gd | GeneMods | 闪避腰带基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Belts/HybridBeltMods.gd | GeneMods | 混合腰带基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Belts/LifeBeltMods.gd | GeneMods | 生命腰带基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Body/ArmorBodyMods.gd | GeneMods | 护甲胸甲基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Body/CasterBodyMods.gd | GeneMods | 施法胸甲基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Body/EvasionBodyMods.gd | GeneMods | 闪避胸甲基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Body/HybridBodyMods.gd | GeneMods | 混合胸甲基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Body/LifeBodyMods.gd | GeneMods | 生命胸甲基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Boots/ArmorBootsMods.gd | GeneMods | 护甲鞋子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Boots/CasterBootsMods.gd | GeneMods | 施法鞋子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Boots/EvasionBootsMods.gd | GeneMods | 闪避鞋子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Boots/HybridBootsMods.gd | GeneMods | 混合鞋子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Boots/LifeBootsMods.gd | GeneMods | 生命鞋子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Gloves/ArmorGlovesMods.gd | GeneMods | 护甲手套基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Gloves/CasterGlovesMods.gd | GeneMods | 施法手套基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Gloves/EvasionGlovesMods.gd | GeneMods | 闪避手套基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Gloves/HybridGlovesMods.gd | GeneMods | 混合手套基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Gloves/LifeGlovesMods.gd | GeneMods | 生命手套基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Helmets/ArmorHelmetMods.gd | GeneMods | 护甲头盔基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Helmets/CasterHelmetMods.gd | GeneMods | 施法头盔基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Helmets/EvasionHelmetMods.gd | GeneMods | 闪避头盔基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Helmets/HybridHelmetMods.gd | GeneMods | 混合头盔基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Helmets/LifeHelmetMods.gd | GeneMods | 生命头盔基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Minors/MinorMods.gd | GeneMods | 次要(小件)部位基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Pants/ArmorPantsMods.gd | GeneMods | 护甲裤子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Pants/CasterPantsMods.gd | GeneMods | 施法裤子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Pants/EvasionPantsMods.gd | GeneMods | 闪避裤子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Pants/HybridPantsMods.gd | GeneMods | 混合裤子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Pants/LifePantsMods.gd | GeneMods | 生命裤子基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Rings/AttackRingMods.gd | GeneMods | 攻击戒指基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Rings/CasterRingMods.gd | GeneMods | 施法戒指基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Rings/LifeRingMods.gd | GeneMods | 生命戒指基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Rings/ResistantRingMods.gd | GeneMods | 抗性戒指基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Shields/ArmorShieldMods.gd | GeneMods | 护甲盾牌基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Shields/CasterShieldMods.gd | GeneMods | 施法盾牌基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Shields/EvasionShieldMods.gd | GeneMods | 闪避盾牌基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Shields/HybridShieldMods.gd | GeneMods | 混合盾牌基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Shields/LifeShieldMods.gd | GeneMods | 生命盾牌基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Weapons/CasterWeaponMods.gd | GeneMods | 施法武器基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Weapons/MeleeWeaponMods.gd | GeneMods | 近战武器基础词缀池定义 | _ready |
| Globals/Genes/BaseTypes/Weapons/RangeWeaponMods.gd | GeneMods | 远程武器基础词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonAmuletMods.gd | GeneMods | 通用护身符词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonBeltMods.gd | GeneMods | 通用腰带词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonBodyMods.gd | GeneMods | 通用胸甲词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonBootsMods.gd | GeneMods | 通用鞋子词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonGlovesMods.gd | GeneMods | 通用手套词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonHelmetMods.gd | GeneMods | 通用头盔词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonMinorMods.gd | GeneMods | 通用次要部位词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonPantsMods.gd | GeneMods | 通用裤子词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonRingMods.gd | GeneMods | 通用戒指词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonShieldMods.gd | GeneMods | 通用盾牌词缀池定义 | _ready |
| Globals/Genes/CommonMods/CommonWeaponMods.gd | GeneMods | 通用武器词缀池定义 | _ready |
| Globals/Genes/DropOnlyMods/BaseTypes/DropCasterWeaponMods.gd | GeneMods | 施法武器掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/BaseTypes/DropMeleeWeaponMods.gd | GeneMods | 近战武器掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/BaseTypes/DropRangeWeaponMods.gd | GeneMods | 远程武器掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/Common/DropCommonArmorMods.gd | GeneMods | 护甲类掉落专属通用词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/Common/DropCommonJewelleryMods.gd | GeneMods | 首饰类掉落专属通用词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/Common/DropCommonWeaponMods.gd | GeneMods | 武器掉落专属通用词缀定义(空) | _ready |
| Globals/Genes/DropOnlyMods/DropAmuletMods.gd | GeneMods | 护身符掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropBeltMods.gd | GeneMods | 腰带掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropBodyMods.gd | GeneMods | 胸甲掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropBootsMods.gd | GeneMods | 鞋子掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropGlovesMods.gd | GeneMods | 手套掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropHelmetMods.gd | GeneMods | 头盔掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropMinorMods.gd | GeneMods | 次要部位掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropPantsMods.gd | GeneMods | 裤子掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropRingMods.gd | GeneMods | 戒指掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropShieldMods.gd | GeneMods | 盾牌掉落专属词缀定义 | _ready |
| Globals/Genes/DropOnlyMods/DropWeaponMods.gd | GeneMods | 武器掉落专属词缀定义 | _ready |
| Globals/Genes/GeneMods.gd | Node | 基因词缀基类:编译词缀池/加权抽样/属性计算 | compile,cache_ids,suffix_weight_for_level,prefix_weight_for_level,implicit_weight_for_level |
| Globals/Genes/UniqueGenes.gd | Node | 唯一基因池注册并按部位加权抽取 | _ready,get_unique_ids_for_slot,weighted_distribution,roll_random_unique,get_unique_data |
| Globals/Genes/UniquePools/UniquePoolGeneric.gd | Node | 通用唯一基因池数据(品质/词缀/权重) | - |
| Globals/Genes/UniquePools/UniquePoolSOTA.gd | Node | SOTA专属唯一基因池数据 | - |
| Globals/Globals.gd | Node | 全局总控:暂停/输入/通知/Steam/富文本状态 | _ready,request_pause,release_pause,_on_overlay,_process |
| Globals/ItemManager.gd | Node | 物品装备/背包/仓库槽位管理 | get_free_inventory_slot,get_free_stash_slot,sort_inventory,sort_stash,equip_item |
| Globals/ItemNameGenerator.gd | Node | 用前后缀词库随机生成物品名称 | generate_name |
| Globals/Keybindings.gd | Node | 可配置按键动作与UI映射定义 | - |
| Globals/Keystones.gd | Node | 汇总三类基石天赋数据(支持/树/唯一) | _ready |
| Globals/Keystones/SupportKeystones.gd | Node | 支持类基石天赋数据定义 | - |
| Globals/Keystones/TreeKeystones.gd | Node | 天赋树基石天赋数据定义 | - |
| Globals/Keystones/UniqueKeystones.gd | Node | 唯一(暗金)基石天赋数据定义 | - |
| Globals/LayoutGenerators/Layout.gd | Node | 关卡布局生成器基类(class_name) | - |
| Globals/LayoutGenerators/LayoutCells.gd | LayoutGenerator | 分叉细胞式关卡地图布局生成 | generate |
| Globals/LayoutGenerators/LayoutCircle.gd | LayoutGenerator | 圆形辐射式关卡地图布局生成 | generate |
| Globals/LayoutGenerators/LayoutField.gd | LayoutGenerator | 田字形分支关卡地图布局生成 | generate |
| Globals/LayoutGenerators/LayoutFixed.gd | LayoutGenerator | 固定布局生成(空实现占位) | generate |
| Globals/Leaderboard.gd | Node | Steam排行榜:查找/上传/读取成绩 | initialize,load_leaderboard_handles,reload_leaderboards,_on_leaderboard_find_result,_on_leaderboard_score_uploaded |
| Globals/Levels.gd | Node | 关卡场景/贴图/图标与地图等级查询 | is_current_level_hideout,is_current_level_arena,is_current_level_ladder,is_current_level_map,get_current_level_name |
| Globals/MTXManager.gd | Node | 商店微交易物品:拉取/价格/购买 | initialize,fetch_items,handle_inventory_full_update,handle_inventory_result_ready,request_prices |
| Globals/MapMods.gd | Node | 地图词缀:生成/重掷/属性渲染 | sort_mods,reroll_mods,roll_stat,get_map_mods,render_stat |
| Globals/Mitigation.gd | Node | 计算有效减伤与有效闪避率 | get_effective_mitigation,get_effective_evasion |
| Globals/MonsterLevels.gd | Node | 怪物场景与各区域怪物池配置 | - |
| Globals/MonsterMods.gd | Node | 怪物词缀池:选择随机词缀(含光环) | choose,choose_with_auras |
| Globals/MonsterStats/MonsterStats.gd | Node | 各怪物类型基础属性数据表 | - |
| Globals/MonsterTypes.gd | Node | 怪物类型常量枚举(class_name) | - |
| Globals/OrbTypes.gd | Node | 掉落球体类型纹理/动画映射 | - |
| Globals/Outfits.gd | Node | 玩家外观部件(头/手/裤/鞋)资源查询 | get_helmet,get_head,get_hands,get_pants,get_feet |
| Globals/PassiveTagStats.gd | Node | 被动标签属性配置查询表 | get_passive_config |
| Globals/PassiveTreeData.gd | Node | 被动天赋树JSON加载/节点提取/连通查询 | _load_json_data,_ready,extract_nodes,get_neighbors,integrity_check |
| Globals/PassiveTreeUtils.gd | Node | 天赋树最短分配路径BFS计算 | compute_shortest_allocation_path,find_nodes_in_path,bfs,clear_shortest_allocation_path,edge_in_path |
| Globals/PassiveTypes.gd | Node | 被动类型常量(小/大/基石) | - |
| Globals/PlayableClasses.gd | Node | 可玩职业/专精定义与查询 | get_playable_spec_id,get_spec_name_from_id,get_spec_color_from_id,get_root_node,get_class_name |
| Globals/PopupManager.gd | Node | 弹窗队列管理(排队/层级/销毁) | _ready,show_popup,reset,_process,maybe_pop |
| Globals/Powerups.gd | Node | 随机生成增益道具实例 | create_random_powerup |
| Globals/SearchUtils.gd | Node | 生成物品搜索字符串(渲染词缀) | get_search_string |
| Globals/SkillSupports.gd | Node | 技能辅助宝石定义与过滤字符串 | get_filter_string |
| Globals/SkillTags.gd | Node | 技能标签枚举/渲染/字符串转换 | get_tag_list,render_tag_list,tags_to_string |
| Globals/SkillTiers/AmplificationAuraTiers.gd | TierLoader | 加载增幅光环技能等级JSON数据 | _ready |
| Globals/SkillTiers/ArcTiers.gd | TierLoader | 加载电弧(Arc)技能等级JSON数据 | _ready |
| Globals/SkillTiers/ArrowTiers.gd | TierLoader | 加载箭矢(Arrow)技能等级JSON数据 | _ready |
| Globals/SkillTiers/AxeTiers.gd | TierLoader | 加载斧(Axe)技能等级JSON数据 | _ready |
| Globals/SkillTiers/BaneTiers.gd | TierLoader | 加载祸害(Bane)技能等级JSON数据 | _ready |
| Globals/SkillTiers/BladeShieldTiers.gd | TierLoader | 加载刀盾(BladeShield)技能等级JSON数据 | _ready |
| Globals/SkillTiers/BlizzardTiers.gd | TierLoader | 加载暴风雪(Blizzard)技能等级JSON数据 | _ready |
| Globals/SkillTiers/BloodSlashTiers.gd | TierLoader | 加载血斩(BloodSlash)技能等级JSON数据 | _ready |
| Globals/SkillTiers/BrittleTiers.gd | TierLoader | 加载脆化(Brittle)技能等级JSON数据 | _ready |
| Globals/SkillTiers/ChainLightningTiers.gd | TierLoader | 加载连锁闪电技能等级JSON数据 | _ready |
| Globals/SkillTiers/ClusterBombsTiers.gd | TierLoader | 加载集束炸弹技能等级JSON数据 | _ready |
| Globals/SkillTiers/ColdAuraTiers.gd | TierLoader | 加载冰霜光环技能等级JSON数据 | _ready |
| Globals/SkillTiers/DebilitateTiers.gd | TierLoader | 加载削弱(Debilitate)技能等级JSON数据 | _ready |
| Globals/SkillTiers/DoTAuraTiers.gd | TierLoader | 加载持续伤害光环技能等级JSON数据 | _ready |
| Globals/SkillTiers/DoomTetherTiers.gd | TierLoader | 加载厄运锁链技能等级JSON数据 | _ready |
| Globals/SkillTiers/ElusivenessTiers.gd | TierLoader | 加载缥缈(Elusiveness)技能等级JSON数据 | _ready |
| Globals/SkillTiers/EnergizedAxeTiers.gd | TierLoader | 加载充能斧技能等级JSON数据 | _ready |
| Globals/SkillTiers/FireAuraTiers.gd | TierLoader | 加载火焰光环技能等级JSON数据 | _ready |
| Globals/SkillTiers/FlameTetherTiers.gd | TierLoader | 加载火焰锁链技能等级JSON数据 | _ready |
| Globals/SkillTiers/HinderTiers.gd | TierLoader | 加载阻滞(Hinder)技能等级JSON数据 | _ready |
| Globals/SkillTiers/HoningTiers.gd | TierLoader | 加载磨砺(Honing)技能等级JSON数据 | _ready |
| Globals/SkillTiers/HypothermiaTiers.gd | TierLoader | 加载低温(Hypothermia)技能等级JSON数据 | _ready |
| Globals/SkillTiers/IceOrbTiers.gd | TierLoader | 加载冰球(IceOrb)技能等级JSON数据 | _ready |
| Globals/SkillTiers/LavaSurgeTiers.gd | TierLoader | 加载熔岩涌动技能等级JSON数据 | _ready |
| Globals/SkillTiers/LightningAuraTiers.gd | TierLoader | 加载闪电光环技能等级JSON数据 | _ready |
| Globals/SkillTiers/LightningSpearTiers.gd | TierLoader | 加载闪电长矛技能等级JSON数据 | _ready |
| Globals/SkillTiers/MinigunTiers.gd | TierLoader | 加载机枪(Minigun)技能等级JSON数据 | _ready |
| Globals/SkillTiers/OrbTiers.gd | TierLoader | 加载法球(Orb)技能等级JSON数据 | _ready |
| Globals/SkillTiers/PhysicalAuraTiers.gd | TierLoader | 加载物理光环技能等级JSON数据 | _ready |
| Globals/SkillTiers/PlagueCloudsTiers.gd | TierLoader | 加载瘟疫云技能等级JSON数据 | _ready |
| Globals/SkillTiers/PlasmaOrbTiers.gd | TierLoader | 加载等离子球技能等级JSON数据 | _ready |
| Globals/SkillTiers/PoisonDartTiers.gd | TierLoader | 加载毒镖技能等级JSON数据 | _ready |
| Globals/SkillTiers/PolarizeTiers.gd | TierLoader | 加载极化(Polarize)技能等级JSON数据 | _ready |
| Globals/SkillTiers/PrismaticSlashTiers.gd | TierLoader | 加载棱彩斩技能等级JSON数据 | _ready |
| Globals/SkillTiers/ProtractionTiers.gd | TierLoader | 加载延长(Protraction)技能等级JSON数据 | _ready |
| Globals/SkillTiers/RegenerationTiers.gd | TierLoader | 加载再生(Regeneration)技能等级JSON数据 | _ready |
| Globals/SkillTiers/ResilienceTiers.gd | TierLoader | 加载坚韧(Resilience)技能等级JSON数据 | _ready |
| Globals/SkillTiers/RushTiers.gd | TierLoader | 加载冲刺(Rush)技能等级JSON数据 | _ready |
| Globals/SkillTiers/ScorchTiers.gd | TierLoader | 加载灼烧(Scorch)技能等级JSON数据 | _ready |
| Globals/SkillTiers/ShardOrbTiers.gd | TierLoader | 加载碎片球技能等级JSON数据 | _ready |
| Globals/SkillTiers/SharknadoShotTiers.gd | TierLoader | 加载鲨卷风射击技能等级JSON数据 | _ready |
| Globals/SkillTiers/ShockOrbTiers.gd | TierLoader | 加载电击球技能等级JSON数据 | _ready |
| Globals/SkillTiers/ShockwaveTiers.gd | TierLoader | 加载冲击波技能等级JSON数据 | _ready |
| Globals/SkillTiers/ShotgunTiers.gd | TierLoader | 加载霰弹枪技能等级JSON数据 | _ready |
| Globals/SkillTiers/ShrapnelBombTiers.gd | TierLoader | 加载榴弹炸弹技能等级JSON数据 | _ready |
| Globals/SkillTiers/ShurikenTiers.gd | TierLoader | 加载手里剑技能等级JSON数据 | _ready |
| Globals/SkillTiers/SturdinessTiers.gd | TierLoader | 加载坚固(Sturdiness)技能等级JSON数据 | _ready |
| Globals/SkillTiers/TierLoader.gd | Node | 技能等级数据基类:加载JSON并变换光环 | _load_json_data,transform_for_aura,get_tiers |
| Globals/SkillTiers/ToxicAuraTiers.gd | TierLoader | 加载剧毒光环技能等级JSON数据 | _ready |
| Globals/SkillTiers/VolcanoTiers.gd | TierLoader | 加载火山(Volcano)技能等级JSON数据 | _ready |
| Globals/Skills.gd | Node | 技能等级数据聚合与等级渲染 | render_tier_diff,render_tier_skill_buff,render_tier_player_buff,tier_for_level |
| Globals/SlotRequirements.gd | Node | 技能槽/辅助槽解锁等级需求表 | get_required_level_for_support,get_required_level_for_skill |
| Globals/SlotScaling.gd | Node | 各技能槽伤害倍率定义 | - |
| Globals/SpecializationData.gd | Node | 专精天赋树JSON加载/节点提取/连通查询 | _load_json_data,_ready,extract_nodes,get_neighbors,integrity_check |
| Globals/SpecializationTreeUtils.gd | Node | 专精天赋树最短分配路径BFS计算 | compute_shortest_allocation_path,find_nodes_in_path,bfs,clear_shortest_allocation_path,edge_in_path |
| Globals/StageProgress.gd | Node | 关卡完成度查询(自身/相邻) | is_stage_completed,is_neighbor_completed |
| Globals/StarterBuilds.gd | Node | 各职业新手技能构筑模板 | get_starters_for_class |
| Globals/StatsInfo.gd | Node | 属性标签/名称/数值渲染与格式化 | skill_sorter,_ready,is_stat_valid,render_skill_stat_line,render_stat_name |
| Globals/StatusEffects.gd | Node | 状态效果(异常/增益)纹理映射 | should_show_flag |
| Globals/UUID.gd | Node | 生成UUID v4随机标识 | getRandomInt,uuidbin,v4 |
| Globals/Utils.gd | Node | 数值格式化:符号/大数缩写/时间 | get_sign,render_suffix_number,render_time |
| Globals/WorldMapData.gd | Node | 世界地图JSON加载/节点提取/连通查询 | _load_json_data,_ready,extract_nodes,get_neighbors,integrity_check |
| Globals/WorldMapUtils.gd | Node | 地图到根距离/关卡等级计算 | get_distance_to_root,edge_in_path,is_node_level_fixed,get_stage_level |
| Globals/ZoneScaling.gd | Node | 区域等级缩放:伤害/生命/经验/掉落系数 | get_map_mod_count,get_damage_scaler,get_health_scaler,get_xp_scaler,get_iiq_scaler |
| Globals/__OldPassiveStats.gd | Node | 旧版被动属性配置查询表(废弃保留) | get_passive_config |


-
-
-




#
#
 
2
.
 
S
c
e
n
e
s
 
—
 
战
斗
/
玩
法
(
2
2
5
)




|
 
脚
本
 
|
 
e
x
t
e
n
d
s
 
|
 
职
责
摘
要
 
|
 
关
键
函
数
 
|


|
-
-
-
|
-
-
-
|
-
-
-
|
-
-
-
|


| Scenes/AreaInstantDamageApplier/AreaInstanceDamageApplier.gd | Area2D | 区域进入即施加一次即时伤害,定时清空列表 | _ready,_on_Timer_timeout,_on_AreaInstanceDamageApplier_area_entered |
| Scenes/DelayedSkill/ClusterBombs/ClusterBombs.gd | DelayedSkill | 集束炸弹延迟技能:延迟后触发爆炸 | _physics_process,cast |
| Scenes/DelayedSkill/DelayedSkill.gd | Node2D | 延迟技能基类:延时到期自动施放并自毁 | _ready,_physics_process,set_radius,track_hit,get_visible_enemies |
| Scenes/DelayedSkill/ShrapnelBomb/ShrapnelBomb.gd | DelayedSkill | 弹片炸弹延迟技能:延迟后爆炸散射 | _physics_process,cast |
| Scenes/Explosions/FlipbookExplosion.gd | Particles2D | 翻页动画爆炸特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Explosions/SanguineDecayExplosion.gd | Node2D | 猩红衰败爆炸视觉节点,初始化特效 | _ready |
| Scenes/Explosions/TexturedExplosions/BookedShrapnelExplosion.gd | FlipbookExplosion | 登记弹片爆炸翻页特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Explosions/TexturedExplosions/PoisonExplosion.gd | FlipbookExplosion | 毒爆翻页特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Explosions/TexturedExplosions/ShockExplosion.gd | FlipbookExplosion | 电击爆炸翻页特效 | _ready |
| Scenes/GroundDegens/BeamDegen.gd | GroundDegen | 光束地面伤害:更新光束朝向尺寸并开关 | _ready,update_beam,enable,disable |
| Scenes/GroundDegens/GroundDegen.gd | Area2D | 地面持续伤害区域:进出目标施加每秒伤害 | _ready,_physics_process,_on_GroundDegen_area_entered,_on_GroundDegen_area_exited |
| Scenes/GroundDegens/OnDeathEffects/ToxicPoolDegen.gd | GroundDegen | 死亡遗留毒池伤害区(纯数据配置,无逻辑) | (无) |
| Scenes/GroundDegens/Skills/Blizzard/BlizzardDegen.gd | GroundDegen | 暴雪技能地面持续伤害区域 | _ready,_physics_process |
| Scenes/Interactables/ClassChanger/ClassStatue.gd | Interactable | 职业雕像交互:显示上下文并打开转职 | get_context_text,on_interact |
| Scenes/Interactables/CraftingBench/CraftingBench.gd | Interactable | 制作台交互:打开制作界面 | get_context_text,on_interact |
| Scenes/Interactables/GearBench/SkillBench.gd | Interactable | 技能工作台:校验后打开技能装配界面 | _ready,get_context_text,on_interact,_check |
| Scenes/Interactables/Interactable.gd | Node2D | 可交互物基类:悬停显示上下文与交互处理 | _ready,get_context_text,_on_mouse_entered,_on_mouse_exited,_physics_process |
| Scenes/Interactables/LoadoutBench/LoadoutBench.gd | Interactable | 装配台交互:打开技能/基因装配界面 | get_context_text,on_interact |
| Scenes/Interactables/MutationBench/MutationBench.gd | Interactable | 突变台交互:打开基因突变工艺界面 | get_context_text,on_interact |
| Scenes/Interactables/OutfitBench/OutfitBench.gd | Interactable | 外观台交互:打开外观装备界面 | get_context_text,on_interact |
| Scenes/Interactables/Portal/Portal.gd | Interactable | 传送门交互:显示地图选择关卡 | get_context_text,on_interact,show_map |
| Scenes/Interactables/SharedStash/SharedStash.gd | Interactable | 共享仓库交互:打开共享存储 | get_context_text,on_interact |
| Scenes/Interactables/SpecializationStatue/SpecializationStatue.gd | Interactable | 专精雕像交互:校验后打开专精天赋 | _ready,get_context_text,on_interact,_check |
| Scenes/KeystoneCycles/CycleOfDestruction.gd | Node | 毁灭循环基石:定时切换增益效果 | _ready,_on_SwitchTimer_timeout,trigger |
| Scenes/KeystoneCycles/GoblinsGirdle.gd | Node | 地精腰带基石:定时切换增益效果 | _ready,_on_SwitchTimer_timeout,trigger |
| Scenes/KeystoneCycles/PhantomShield.gd | Node | 幻影护盾基石:定时补充护盾值 | _ready,trigger,_on_AddShieldTimer_timeout |
| Scenes/KeystoneCycles/RegenerativeFlesh.gd | Node | 再生之肉基石:定时切换回复效果 | _ready,_on_SwitchTimer_timeout,trigger |
| Scenes/KeystoneCycles/Unleash.gd | Node | 释放基石:定时切换施放强化 | _ready,_on_SwitchTimer_timeout,trigger |
| Scenes/Levels/BaseLevel.gd | Node2D | 关卡基类:瓦片生成、刷怪点与怪物生成 | connect_points,expand_cell,has_potential_tile,set_potential_tile,get_potential_neighbor_count_all |
| Scenes/Levels/BossArenas/BossArena.gd | BaseLevel | 首领竞技场关卡,初始化配置 | _ready |
| Scenes/Levels/BossArenas/SpiritOfTheAncient/SpiritOfTheAncient.gd | BaseLevel | 远古之灵首领战关卡,初始化配置 | _ready |
| Scenes/Levels/Default/DefaultLevel.gd | BaseLevel | 默认关卡:定义刷怪表 | get_spawnables,_ready |
| Scenes/Levels/Hideout/HideoutLevel.gd | BaseLevel | 藏身处关卡:无战斗,处理新手初始配置 | get_spawnables,_ready,_input,check_for_starter_build |
| Scenes/Levels/Ladder/Ladder.gd | BaseLevel | 天梯关卡:波次刷怪推进与计时 | get_spawnables,_ready,_physics_process,spawn_next_wave,_on_Timer_timeout |
| Scenes/Levels/LevelLoader.gd | CanvasLayer | 关卡加载界面:显示状态消息 | on_status_change |
| Scenes/Levels/NavMesh.gd | Node2D | 导航网格:构建寻路并查询最短路径 | test_seen,mark_seen,get_point,create_point,build_navmesh |
| Scenes/Levels/SpawnLocation.gd | Node2D | 出生点:加载瓦片并定时尝试刷怪 | _ready,_load_tiles,_on_Timer_timeout,try_to_spawn |
| Scenes/Levels/TestLevel/TestLevel.gd | BaseLevel | 测试关卡:定义刷怪表 | get_spawnables,_ready |
| Scenes/Mobs/Basic/Creatures/PoisonDeath.gd | Mob | 毒死怪物:死亡时触发毒爆 | _on_death |
| Scenes/Mobs/Basic/Creatures/SkeletonCurser.gd | Mob | 骷髅诅咒者:随机装备一种诅咒技能 | _ready |
| Scenes/Mobs/DissolveMob.gd | Node2D | 怪物溶解消失动画,定时销毁 | _on_Timer_timeout,_process |
| Scenes/Mobs/Mob.gd | RigidBody2D | 怪物基类:物理移动、受击伤害与死亡掉落 | _ready,recache_ms,reset_target_offset,_integrate_forces,_physics_process |
| Scenes/Mobs/PathingController.gd | Node2D | 怪物寻路控制器:定期重算路径与目标可见性 | _ready,_physics_process,_on_RecomputePathTimer_timeout,is_target_visible,is_offset_visible |
| Scenes/Particles/Beams/Beam.gd | Node2D | 光束视觉:更新光束朝向与长度 | _ready,_process,_update_position |
| Scenes/Particles/BloodExplosion.gd | Particles2D | 血爆粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/BombExplosion.gd | Particles2D | 炸弹爆炸粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/ChainLightning.gd | Particles2D | 连锁闪电粒子:追踪更新位置,定时销毁 | _ready,_process,_update_position,_on_Timer_timeout |
| Scenes/Particles/ChillExplosion.gd | Particles2D | 寒冷爆炸粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/CollateralDamageExplosion.gd | Particles2D | 附带伤害爆炸粒子,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/DoomTether.gd | Node2D | 末日锁链视觉:连接两点更新链状纹理 | _ready,_process,_update_position |
| Scenes/Particles/FlameTether.gd | Node2D | 火焰锁链视觉:连接两点更新链状纹理 | _ready,_process,_update_position |
| Scenes/Particles/FloatingDamage.gd | Node2D | 单个飘字伤害显示 | show_value |
| Scenes/Particles/FloatingDamageManager.gd | Node2D | 飘字管理器:显示伤害/经验等 | show_value,show_damage,show_xp |
| Scenes/Particles/InfectionChain.gd | Node2D | 感染链视觉:连接目标更新位置,定时销毁 | _ready,_process,_update_position,_on_Timer_timeout |
| Scenes/Particles/LevelupEffect.gd | Particles2D | 升级粒子特效,定时销毁 | _on_Timer_timeout |
| Scenes/Particles/Nova.gd | Node2D | 新星爆发特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/OnKill/OnKill.gd | Particles2D | 击杀触发粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/PoisonExplosion.gd | Particles2D | 毒爆粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/ShockwaveBurst.gd | Particles2D | 冲击波爆发粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/SparkExplosion.gd | Particles2D | 火花爆炸粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Particles/VolcanoOrbExplosion.gd | Particles2D | 火山珠爆炸粒子特效,定时销毁 | _ready,_on_Timer_timeout |
| Scenes/Pickups/Gene/GenePickup.gd | Pickup | 基因掉落物:拾取时获取基因 | _ready,on_pickup |
| Scenes/Pickups/Orb/OrbPickup.gd | Pickup | 宝珠掉落物:拾取时获取宝珠 | _ready,on_pickup |
| Scenes/Pickups/Pickup.gd | Area2D | 掉落物基类:区域拾取、信息展示与按钮交互 | _ready,_on_Pickup_area_entered,_on_Pickup_area_exited,_physics_process,_on_pickup |
| Scenes/Pickups/Portal/PortalPickup.gd | Pickup | 传送门掉落:确认后触发传送 | on_pickup,_on_confirm |
| Scenes/Projectiles/MeleeSkills/ShockwaveProjectile.gd | Projectile | 冲击波投射物:命中爆炸,定时销毁 | _ready,_on_Timer_timeout,on_hit |
| Scenes/Projectiles/MobSkills/Glob/Glob.gd | Projectile | 黏液弹投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/MobSkills/SotaSpear/SotaSpear.gd | Projectile | 长矛投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/MobSkills/SpiderWeb/SpiderWeb.gd | Projectile | 蛛网投射物:命中施加蛛网缠绕 | on_hit |
| Scenes/Projectiles/Projectile.gd | Area2D | 投射物基类:飞行、命中判定、销毁与音效 | _ready,_process,_physics_process,_on_Area2D_area_entered,on_enter |
| Scenes/Projectiles/Skills/ArrowProjectile.gd | Projectile | 箭矢投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/AxeProjectile.gd | Projectile | 斧头投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/BaneProjectile.gd | Projectile | 灾厄投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/BladeShieldProjectile.gd | Projectile | 剑盾环绕投射物:物理帧移动与命中 | _ready,_physics_process,on_hit |
| Scenes/Projectiles/Skills/BloodSlashProjectile.gd | Projectile | 血斩投射物:物理帧移动与命中 | _ready,_physics_process,on_hit |
| Scenes/Projectiles/Skills/BrittleProjectile.gd | Projectile | 脆化投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/DebilitateProjectile.gd | Projectile | 虚弱投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/EnergizedAxeProjectile.gd | Projectile | 充能斧投射物:物理帧移动与命中 | _ready,_physics_process,on_hit |
| Scenes/Projectiles/Skills/HinderProjectile.gd | Projectile | 迟缓投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/HypothermiaProjectile.gd | Projectile | 低温投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/IceOrbProjectile.gd | Projectile | 冰球投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/LightningSpearProjectile.gd | Projectile | 闪电长矛投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/MinigunProjectile.gd | Projectile | 机枪投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/OrbProjectile.gd | Projectile | 球体投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/PlagueCloudsProjectile.gd | Projectile | 瘟疫云投射物:脉冲对半径内目标施加瘟疫 | _ready,on_pulse |
| Scenes/Projectiles/Skills/PlasmaOrbProjectile.gd | Projectile | 等离子球投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/PoisonDartProjectile.gd | Projectile | 毒镖投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/PolarizeProjectile.gd | Projectile | 极化投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/ProtractProjectile.gd | Projectile | 延长投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/ScorchProjectile.gd | Projectile | 灼烧投射物:生成时对半径内目标施加诅咒 | _ready |
| Scenes/Projectiles/Skills/ShardMainProjectile.gd | Projectile | 碎片主投射物:脉冲触发效果 | on_pulse |
| Scenes/Projectiles/Skills/ShardOrbProjectile.gd | Projectile | 碎片球投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/SharknadoShardProjectile.gd | Projectile | 鲨卷风碎片投射物:物理帧移动与命中 | _ready,_physics_process,on_hit |
| Scenes/Projectiles/Skills/SharknadoShotProjectile.gd | Projectile | 鲨卷风射击投射物:命中与销毁触发 | _ready,on_hit,on_destroy |
| Scenes/Projectiles/Skills/ShockOrbProjectile.gd | Projectile | 电击球投射物:物理帧移动与命中 | _physics_process,on_hit |
| Scenes/Projectiles/Skills/ShotgunProjectile.gd | Projectile | 霰弹投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/ShurikenProjectile.gd | Projectile | 手里剑投射物:命中触发效果 | on_hit |
| Scenes/Projectiles/Skills/VolcanoOrbProjectile.gd | Projectile | 火山珠投射物:销毁时触发喷发 | on_destroy |
| Scenes/Projectiles/Skills/VolcanoProjectile.gd | Projectile | 火山投射物:脉冲触发效果 | on_pulse |
| Scenes/ShaderExplosions/CollateralDamageExplosion/CollateralDamageExplosion.gd | ShaderExplosion | 附带伤害着色爆炸(纯数据配置,无逻辑) | (无) |
| Scenes/ShaderExplosions/DoomExplosion/DoomExplosion.gd | ShaderExplosion | 末日着色爆炸:播放时触发音效 | _ready |
| Scenes/ShaderExplosions/InfectionExplosion/InfectionExplosion.gd | ShaderExplosion | 感染着色爆炸(纯数据配置,无逻辑) | (无) |
| Scenes/ShaderExplosions/ShaderExplosion.gd | Node2D | 着色爆炸基类:播放着色特效并定时销毁 | _ready,_process,_on_Timer_timeout |
| Scenes/ShaderExplosions/ShockExplosion/ShockExplosion.gd | ShaderExplosion | 电击着色爆炸(纯数据配置,无逻辑) | (无) |
| Scenes/ShaderExplosions/ShrapnelExplosion/ShrapnelExplosion.gd | ShaderExplosion | 弹片着色爆炸(纯数据配置,无逻辑) | (无) |
| Scenes/ShaderExplosions/SlashEffect/SlashEffect.gd | ShaderExplosion | 斩击着色特效(纯数据配置,无逻辑) | (无) |
| Scenes/ShaderExplosions/VolcanoExplosion/VolcanoExplosion.gd | ShaderExplosion | 火山着色爆炸(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/AcquiredSkills/AcquiredAura.gd | GenericAura | 已获得光环:覆写属性并查询层级/属性 | _ready,initialize_override_stats,get_effective_tier,get_tiers,get_stat |
| Scenes/Skills/AcquiredSkills/AcquiredSkill.gd | GenericSkill | 已获得技能:覆写属性并查询层级/属性 | _ready,initialize_override_stats,get_damage_tag,get_effective_tier,get_tiers |
| Scenes/Skills/AcquiredSkills/BloodArmorExplosion/BloodArmorExplosion.gd | AcquiredSkill | 血甲爆炸技能:施放时按基础伤害爆炸 | get_base_damage,get_tiers,get_damage_tag,cast |
| Scenes/Skills/AcquiredSkills/BondedElectrons/BondedElectrons.gd | AcquiredAura | 键合电子光环:光环效果与半径 | get_tiers,get_radius,get_aura_effect |
| Scenes/Skills/AcquiredSkills/DreadAura/DreadAura.gd | AcquiredAura | 恐惧光环:光环效果与半径 | get_tiers,get_radius,get_aura_effect |
| Scenes/Skills/AcquiredSkills/EnergeticFlesh/EnergeticFlesh.gd | AcquiredAura | 活力之肉光环:光环伤害与半径 | get_radius,get_base_damage,get_tiers,get_aura_effect |
| Scenes/Skills/AcquiredSkills/VileDomainAura/VileDomainAura.gd | AcquiredAura | 邪恶领域光环:光环效果与半径 | get_tiers,get_radius,get_aura_effect |
| Scenes/Skills/Auras/AmplificationAura/AmplificationAura.gd | GenericAura | 增幅光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/ColdAura/ColdAura.gd | GenericAura | 冰冷光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/DoTAura/DoTAura.gd | GenericAura | 持续伤害光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/DoomTether/DoomTether.gd | GenericAura | 末日锁链光环:定义光环效果 | get_aura_effect |
| Scenes/Skills/Auras/Elusiveness/Elusiveness.gd | GenericAura | 闪避光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/FireAura/FireAura.gd | GenericAura | 火焰光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/FlameTether/FlameTether.gd | GenericAura | 火焰锁链光环:定义光环效果 | get_aura_effect |
| Scenes/Skills/Auras/GenericAura.gd | GenericSkill | 光环技能基类:半径内施加/移除光环效果 | _ready,_initialize,recheck_enabled,_update_radius,get_buffs_and_nerfs |
| Scenes/Skills/Auras/Honing/Honing.gd | GenericAura | 磨砺光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/LightningAura/LightningAura.gd | GenericAura | 闪电光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/PhysicalAura/PhysicalAura.gd | GenericAura | 物理光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/Regeneration/Regeneration.gd | GenericAura | 再生光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/Resilience/Resilience.gd | GenericAura | 坚韧光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/Rush/Rush.gd | GenericAura | 疾跑光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/Sturdiness/Sturdiness.gd | GenericAura | 稳固光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/Auras/ToxicAura/ToxicAura.gd | GenericAura | 毒素光环(纯数据配置,无逻辑) | (无) |
| Scenes/Skills/GenericSkill.gd | Node2D | 技能基类:伤害/属性计算、施放与支援宝石 | _ready,recompute_tags,recompute_chances,reset_output_cache,_handle_stat_change |
| Scenes/Skills/MobSkills/BasicAttack/BasicAttack.gd | MobSkill | 怪物普攻:返回父节点伤害类型 | get_damage_tag |
| Scenes/Skills/MobSkills/BossSludgeSkills/GlobThrow.gd | MobSkill | 黏液投掷:覆写属性后施放 | initialize_override_mob_stats,get_damage_tag,cast |
| Scenes/Skills/MobSkills/MobSkill.gd | GenericSkill | 怪物技能基类:覆写怪物属性数据 | _ready,initialize_override_mob_stats,get_tags,get_damage_tag,get_stat |
| Scenes/Skills/MobSkills/MutatedSpiderSkills/WebThrow.gd | MobSkill | 蛛网投掷:覆写属性、冷却与施放 | initialize_override_mob_stats,get_damage_tag,get_cooldown,cast |
| Scenes/Skills/MobSkills/SotaSkills/SpearThrow.gd | MobSkill | 长矛投掷:覆写属性、冷却与施放 | initialize_override_mob_stats,get_damage_tag,get_cooldown,cast |
| Scenes/Skills/MobSkills/TheGatekeeperSkills/PoisonNova.gd | MobSkill | 毒新星:覆写属性后施放 | initialize_override_mob_stats,get_damage_tag,cast |
| Scenes/Skills/MobSkills/TheGatekeeperSkills/ZombieSummoner.gd | MobSkill | 僵尸召唤:施放召唤僵尸 | get_damage_tag,cast |
| Scenes/Skills/Playable/Arc/Arc.gd | GenericSkill | 电弧技能:半径内连锁电弧施放 | _ready,can_cast,cast,_update_radius |
| Scenes/Skills/Playable/Arrow/Arrow.gd | GenericSkill | 箭矢技能:射出箭矢 | can_cast,cast |
| Scenes/Skills/Playable/Axe/Axe.gd | GenericSkill | 斧头技能:投掷斧头 | can_cast,cast |
| Scenes/Skills/Playable/Bane/Bane.gd | GenericSkill | 灾厄诅咒技能:对最近敌人降下诅咒投射物 | cast |
| Scenes/Skills/Playable/BladeShield/BladeShield.gd | GenericSkill | 剑盾技能:环绕剑刃并冷却 | can_cast,cast,get_cooldown |
| Scenes/Skills/Playable/Blizzard/Blizzard.gd | GenericSkill | 暴雪技能:对目标降下持续暴雪区域 | can_cast,cast |
| Scenes/Skills/Playable/BloodSlash/BloodSlash.gd | GenericSkill | 血斩技能:范围血斩 | get_cast_range,can_cast,get_duration,cast |
| Scenes/Skills/Playable/Brittle/Brittle.gd | GenericSkill | 脆化诅咒技能:对最近敌人降下诅咒 | cast |
| Scenes/Skills/Playable/ChainLightning/ChainLightning.gd | GenericSkill | 连锁闪电技能:连锁电击目标 | can_cast,cast |
| Scenes/Skills/Playable/ClusterBombs/ClusterBombs.gd | GenericSkill | 集束炸弹技能:投掷延迟爆炸炸弹 | can_cast,cast |
| Scenes/Skills/Playable/Debilitate/Debilitate.gd | GenericSkill | 虚弱诅咒技能:对最近敌人降下诅咒 | cast |
| Scenes/Skills/Playable/EnergizedAxe/EnergizedAxe.gd | GenericSkill | 充能斧技能:范围充能斩 | get_cast_range,can_cast,get_duration,cast |
| Scenes/Skills/Playable/Hinder/Hinder.gd | GenericSkill | 迟缓诅咒技能:对最近敌人降下诅咒 | cast |
| Scenes/Skills/Playable/Hypothermia/Hypothermia.gd | GenericSkill | 低温诅咒技能:对最近敌人降下诅咒 | cast |
| Scenes/Skills/Playable/IceOrb/IceOrb.gd | GenericSkill | 冰球技能:射出冰球 | can_cast,cast |
| Scenes/Skills/Playable/LavaSurge/LavaSurge.gd | GenericSkill | 熔岩涌技能:追踪目标旋转光束并开关 | _ready,setup,_handle_stat_change,_physics_process,_on_Timer_timeout |
| Scenes/Skills/Playable/LightningSpear/LightningSpear.gd | GenericSkill | 闪电长矛技能:射出闪电长矛 | can_cast,cast |
| Scenes/Skills/Playable/Minigun/Minigun.gd | GenericSkill | 机枪技能:连续射击投射物 | can_cast,cast |
| Scenes/Skills/Playable/Orb/Orb.gd | GenericSkill | 球体技能:射出法术球 | can_cast,cast |
| Scenes/Skills/Playable/PlagueClouds/PlagueClouds.gd | GenericSkill | 瘟疫云技能:降下持续瘟疫云 | cast,get_cooldown |
| Scenes/Skills/Playable/PlasmaOrb/PlasmaOrb.gd | GenericSkill | 等离子球技能:射出等离子球 | can_cast,cast |
| Scenes/Skills/Playable/PoisonDart/PoisonDart.gd | GenericSkill | 毒镖技能:射出毒镖 | can_cast,cast |
| Scenes/Skills/Playable/Polarize/Polarize.gd | GenericSkill | 极化诅咒技能:对最近敌人降下诅咒 | cast |
| Scenes/Skills/Playable/PrismaticSlash/PrismaticSlash.gd | GenericSkill | 棱镜斩技能:多元素斩击 | can_cast,cast,get_damage_bundle |
| Scenes/Skills/Playable/Protract/Protract.gd | GenericSkill | 延长诅咒技能:对最近敌人降下诅咒 | cast |
| Scenes/Skills/Playable/Scorch/Scorch.gd | GenericSkill | 灼烧诅咒技能:对最近敌人降下诅咒 | cast |
| Scenes/Skills/Playable/ShardOrb/ShardOrb.gd | GenericSkill | 碎片球技能:射出碎片球 | can_cast,cast |
| Scenes/Skills/Playable/SharknadoShot/SharknadoShot.gd | GenericSkill | 鲨卷风射击技能:射出鲨卷风弹 | can_cast,cast |
| Scenes/Skills/Playable/ShockOrb/ShockOrb.gd | GenericSkill | 电击球技能:射出电击球 | can_cast,cast |
| Scenes/Skills/Playable/Shockwave/Shockwave.gd | GenericSkill | 冲击波技能:范围推击地面冲击波 | get_cast_range,get_force,can_cast,cast |
| Scenes/Skills/Playable/Shotgun/Shotgun.gd | GenericSkill | 霰弹技能:扇形散射投射物 | can_cast,cast |
| Scenes/Skills/Playable/ShrapnelBomb/ShrapnelBomb.gd | GenericSkill | 弹片炸弹技能:投掷延迟爆炸炸弹 | can_cast,cast |
| Scenes/Skills/Playable/Shuriken/Shuriken.gd | GenericSkill | 手里剑技能:投掷手里剑 | can_cast,cast |
| Scenes/Skills/Playable/Volcano/Volcano.gd | GenericSkill | 火山技能:召唤喷发并冷却 | can_cast,cast,get_cooldown |
| Scenes/StatusEffects/Auras/AuraEffect.gd | BaseEffect | 光环状态效果:标记光环状态标志 | get_status_flags |
| Scenes/StatusEffects/BaseEffect.gd | Node | 状态效果基类:应用、计时触发、移除与属性加成 | initialize,_ready,trigger,_physics_process,remove_effect |
| Scenes/StatusEffects/Boons/PrecisionBoon.gd | BaseEffect | 精准增益:应用时生效 | on_apply,get_status_flags |
| Scenes/StatusEffects/Boons/SwiftnessBoon.gd | BaseEffect | 迅捷增益:应用时生效 | on_apply,get_status_flags |
| Scenes/StatusEffects/Boons/ToughnessBoon.gd | BaseEffect | 坚韧增益:应用时生效 | on_apply,get_status_flags |
| Scenes/StatusEffects/Curses/Bane.gd | BaseEffect | 灾厄诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Curses/Brittle.gd | BaseEffect | 脆化诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Curses/Debilitate.gd | BaseEffect | 虚弱诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Curses/Hinder.gd | BaseEffect | 迟缓诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Curses/Hypothermia.gd | BaseEffect | 低温诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Curses/Polarize.gd | BaseEffect | 极化诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Curses/Protract.gd | BaseEffect | 延长诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Curses/Scorch.gd | BaseEffect | 灼烧诅咒效果:初始化诅咒减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/DamageAilments/Bleed.gd | BaseEffect | 流血异常:周期流血伤害与伤害合并 | on_apply,on_tick,get_status_flags,get_remaining_bleed_damage,get_damage |
| Scenes/StatusEffects/DamageAilments/Burn.gd | BaseEffect | 燃烧异常:周期燃烧伤害并传播 | on_apply,on_tick,get_status_flags,is_better_than,proliferate |
| Scenes/StatusEffects/DamageAilments/Charred.gd | BaseEffect | 焦化异常:初始化减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/DamageAilments/Chill.gd | BaseEffect | 寒冷异常:减速减益 | initialize,get_status_flags,is_better_than,on_apply,get_effect_amount |
| Scenes/StatusEffects/DamageAilments/Electrocution.gd | BaseEffect | 电刑异常:初始化减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/DamageAilments/Freeze.gd | BaseEffect | 冰冻异常:定身控制 | on_apply,is_better_than,get_status_flags |
| Scenes/StatusEffects/DamageAilments/Infection.gd | BaseEffect | 感染异常:周期伤害并传播 | on_apply,on_tick,proliferate,get_status_flags,get_damage |
| Scenes/StatusEffects/DamageAilments/Jolt.gd | BaseEffect | 电击异常:初始化减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/DamageAilments/Poison.gd | BaseEffect | 中毒异常:周期毒素伤害 | on_apply,on_tick,get_status_flags,get_damage,merge_damage |
| Scenes/StatusEffects/DamageAilments/Rupture.gd | BaseEffect | 撕裂异常:周期流血伤害 | on_apply,on_tick,get_status_flags,get_remaining_bleed_damage,get_damage |
| Scenes/StatusEffects/Generic/Echoing.gd | BaseEffect | 回响标志效果:标记状态标志 | get_status_flags |
| Scenes/StatusEffects/Generic/Exposed.gd | BaseEffect | 暴露效果:初始化减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Generic/Hamstrung.gd | BaseEffect | 跛行效果:初始化减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Generic/RecentlyHit.gd | BaseEffect | 近期受击标志效果 | get_status_flags |
| Scenes/StatusEffects/Generic/Vulnerable.gd | BaseEffect | 易伤效果:初始化减益数值 | initialize,is_better_than,get_status_flags,get_effect_amount |
| Scenes/StatusEffects/Keystones/Adrenaline.gd | BaseEffect | 肾上腺素基石:移动速度加成 | initialize |
| Scenes/StatusEffects/Keystones/BloodBoil.gd | BaseEffect | 血液沸腾基石:状态标志与初始化 | get_status_flags,initialize |
| Scenes/StatusEffects/Keystones/CycleOfDestructionEffect.gd | BaseEffect | 毁灭循环基石效果:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/Endurance.gd | BaseEffect | 耐力基石:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/GrowingPain.gd | BaseEffect | 成长之痛基石:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/HardenedFlesh.gd | BaseEffect | 硬化之肤基石:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/KillMomentum.gd | BaseEffect | 击杀动量基石:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/PhantomShield.gd | BaseEffect | 幻影护盾基石:消耗护盾与标志 | consume,get_status_flags |
| Scenes/StatusEffects/Keystones/RegenerativeFleshEffect.gd | BaseEffect | 再生之肉基石效果:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/SpikeArmor.gd | BaseEffect | 尖刺护甲基石:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/ToxicRunner.gd | BaseEffect | 毒跑者基石:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/Transfusion.gd | BaseEffect | 输血基石:状态标志 | get_status_flags |
| Scenes/StatusEffects/Keystones/UnleashEffect.gd | BaseEffect | 释放基石效果:初始化加成 | initialize |
| Scenes/StatusEffects/Keystones/VampiricSkin.gd | BaseEffect | 吸血皮肤基石:初始化加成 | initialize |
| Scenes/StatusEffects/Pickups/Frenzy.gd | BaseEffect | 狂乱拾取效果:初始化加成 | initialize |
| Scenes/StatusEffects/Pickups/Magnifier.gd | BaseEffect | 放大拾取效果:初始化加成 | initialize |
| Scenes/StatusEffects/Skills/BondedElectrons.gd | BaseEffect | 键合电子技能效果:闪电覆写与标志 | get_lightning_override,get_status_flags |
| Scenes/StatusEffects/Skills/ChainLightning.gd | BaseEffect | 连锁闪电技能效果:过期移除 | get_status_flags,_exit_tree,on_expire |
| Scenes/StatusEffects/Skills/DoomTether.gd | BaseEffect | 末日锁链技能效果:周期伤害 | on_apply,on_tick,on_expire,get_status_flags |
| Scenes/StatusEffects/Skills/Dread.gd | BaseEffect | 恐惧技能效果:状态标志 | get_status_flags |
| Scenes/StatusEffects/Skills/EnergeticFlesh.gd | BaseEffect | 活力之肉技能效果:周期恢复 | on_apply,on_tick,get_status_flags |
| Scenes/StatusEffects/Skills/FlameTether.gd | BaseEffect | 火焰锁链技能效果:周期燃烧伤害 | initialize,on_apply,on_tick,on_expire,get_status_flags |
| Scenes/StatusEffects/Skills/Plague.gd | BaseEffect | 瘟疫技能效果:周期伤害 | on_apply,on_tick,get_status_flags |
| Scenes/StatusEffects/Skills/VileDomain.gd | BaseEffect | 邪恶领域技能效果:初始化与标志 | initialize,get_status_flags |
| Scenes/StatusEffects/Skills/Webbed.gd | BaseEffect | 蛛网效果:减速缠绕减益 | initialize,get_status_flags,is_better_than,get_effect_amount |


-
-
-




#
#
 
3
.
 
S
c
e
n
e
s
 
—
 
U
I
/
弹
窗
/
玩
家
(
1
0
1
)




|
 
脚
本
 
|
 
e
x
t
e
n
d
s
 
|
 
职
责
摘
要
 
|
 
关
键
函
数
 
|


|
-
-
-
|
-
-
-
|
-
-
-
|
-
-
-
|


| Scenes/GUI/BuffDisplay.gd | HBoxContainer | HUD 增益/减益条目:图标、剩余时间与层数 | _ready,_on_Timer_timeout,update_count |
| Scenes/GUI/GUI.gd | CanvasLayer | HUD 总控制器:球体/技能/通知/按钮及各类更新 | _ready,bind_player,_on_level_changed,_on_settings_changed,_update_mutation_xp |
| Scenes/GUI/Globes/Globe.gd | Control | 生命/资源球体:进度条与数值更新 | update_progress |
| Scenes/GUI/NotificationMessage.gd | RichTextLabel | 屏幕浮动通知消息文本,播放动画 | _ready |
| Scenes/GUI/SkillDisplay.gd | VBoxContainer | HUD 技能槽:图标/伤害显示,悬停弹技能提示 | _ready,_on_Timer_timeout,_on_TextureRect_mouse_entered,_on_TextureRect_mouse_exited |
| Scenes/GUI/StatusDisplay.gd | VBoxContainer | HUD 状态效果图标与数值(百分比)显示 | _ready |
| Scenes/Minimap/Minimap.gd | CanvasLayer | 小地图界面:渲染地图与区域词缀列表 | _ready,_render_mods,_render_map,render_portal |
| Scenes/Minimap/TextureRect.gd | Control | 小地图绘制控件:瓦片纹理与玩家位置标记 | initialize,_process,_draw |
| Scenes/Player/ArrowToPortalSprite.gd | Sprite | 指向传送门的箭头精灵,实时旋转朝向 | _ready,_set_target,_process |
| Scenes/Player/Player.gd | RigidBody2D | 玩家角色:移动、死亡/升级/装备/技能/属性联动 | _ready,_physics_process,_on_gear_changed,_on_update_healthbar,_on_death |
| Scenes/Popups/DeathScreen.gd | PopupBase | 死亡结算界面:显示结果并上传排行榜成绩 | _ready,_exit_tree,_on_Button_pressed,upload_score_and_show_result,_on_upload |
| Scenes/Popups/EscapeMenu.gd | PopupBase | 暂停/退出菜单:角色、天赋、基因、设置等入口 | _ready,render,_focus_tab_zero,_process,_select |
| Scenes/Popups/EscapeMenuStat.gd | HBoxContainer | 暂停菜单中单条角色属性统计行 | _ready |
| Scenes/Popups/ItemTabContent.gd | ScrollContainer | 技能物品详情面板:名称/等级/描述/词缀渲染 | damage_sorter,_ready |
| Scenes/Popups/PopupBase.gd | CanvasLayer | 所有弹窗基类:入树注册与焦点管理 | _enter_tree,_exit_tree,_grab_focus |
| Scenes/Popups/SkipButton.gd | Button | 跳过按钮:鼠标/焦点悬停提示 | _ready,_on_SkipButton_mouse_entered,_on_SkipButton_focus_entered |
| Scenes/Popups/Unlocks/CharacterUnlockItem.gd | VBoxContainer | 角色解锁条目:图标/说明/解锁条件 | _ready |
| Scenes/Popups/Unlocks/LevelUnlockItem.gd | VBoxContainer | 等级解锁条目:说明/解锁条件 | _ready |
| Scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.gd | PopupBase | 更换角色确认弹窗:选择后切换角色 | _ready,_on_class_chosen,_on_CancelButton_pressed |
| Scenes/Popups/Dialogs/CharacterSelect/CharacterClass.gd | VBoxContainer | 角色职业卡片:职业名展示与文本输入 | _ready,_on_Button_pressed,_grab_focus,_on_text_input |
| Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.gd | PopupBase | 新建角色弹窗:选职业并创建 | _ready,_on_class_chosen,_on_CancelButton_pressed |
| Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.gd | PopupBase | 角色选择界面:列出/新建/删除角色 | _ready,render,_on_Button2_pressed,_on_CharacterCreateButton_pressed,_refocus_new |
| Scenes/Popups/Dialogs/CharacterSelect/CharacterSlot.gd | HBoxContainer | 角色槽位行:展示角色,进入或删除 | _ready,render,_on_Button_pressed,focus,_on_DeleteButton_pressed |
| Scenes/Popups/Dialogs/ConfirmWindow/ConfirmWindow.gd | PopupBase | 通用确认对话框:确认/取消回调 | _ready,_on_confirm,_on_cancel |
| Scenes/Popups/Dialogs/GeneEditor/CraftButton.gd | VBoxContainer | 基因工艺按钮:配方费用与可用状态 | _ready,set_gene_id,_update_enabled_state,_on_Crafter_pressed |
| Scenes/Popups/Dialogs/GeneEditor/GeneButton.gd | HBoxContainer | 基因列表行:名称/搜索/选中/快速删除 | _ready,update_seen_label,_check_visibility,_check_search,_update_name |
| Scenes/Popups/Dialogs/GeneEditor/GeneEditor.gd | PopupBase | 基因编辑器主界面:列表、工艺、资源 | _ready,_process,_update_resources,close,render |
| Scenes/Popups/Dialogs/GeneEditor/GeneInventoryPopup.gd | PopupBase | 基因背包弹窗:展示基因,筛选/搜索 | _ready,_process,_on_BackButton_pressed,render_genes,select_button |
| Scenes/Popups/Dialogs/GeneEditor/GeneLoadout.gd | PopupBase | 基因配装界面:槽位、统计、重命名 | _ready,_on_BackButton_pressed,_refocus,_on_loadout_changed,clear_loadout_stats |
| Scenes/Popups/Dialogs/GeneEditor/ItemList.gd | VBoxContainer | 基因列表排序容器(普通/共享) | gene_sorter,shared_gene_sorter,_ready |
| Scenes/Popups/Dialogs/GeneEditor/LoadoutSlot.gd | PanelContainer | 配装基因槽:渲染/选中/悬停/删除 | _ready,update_seen_label,render,_on_Button_pressed,_select |
| Scenes/Popups/Dialogs/GeneEditor/StashTransferPopup.gd | PopupBase | 仓库基因转移弹窗:本地/共享列表 | _ready,_process,_on_BackButton_pressed,render_genes,select_button |
| Scenes/Popups/Dialogs/GeneSelector/GeneOption.gd | Button | 基因选择条目:新基因标记/搜索过滤 | _ready,update_new_label,_on_GeneOption_pressed,_on_GeneOption_mouse_entered,_on_GeneOption_focus_entered |
| Scenes/Popups/Dialogs/GeneSelector/GeneSelector.gd | PopupBase | 基因选择器:可用/已装备基因,移除装备 | _ready,render,close,_process,_sort_genes |
| Scenes/Popups/Dialogs/Help/Help.gd | PopupBase | 帮助文档弹窗:Tab 浏览/滚动/搜索 | _ready,_physics_process,_input,_on_Button_pressed,_on_LineEdit_text_changed |
| Scenes/Popups/Dialogs/HelpTip/CraftingHelp/CraftingHelp.gd | HelpTip | 工艺系统帮助提示弹窗(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/HelpTip/GeneTip/GeneTip.gd | HelpTip | 基因系统帮助提示弹窗(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/HelpTip/HelpTip.gd | PopupBase | 帮助提示基类:内容与关闭按钮 | _ready,_on_Button_pressed |
| Scenes/Popups/Dialogs/HelpTip/LevelupTip/LevelupTip.gd | HelpTip | 升级提示弹窗(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/HelpTip/LoadoutScreenTip/LoadoutScreenTip.gd | HelpTip | 配装界面提示弹窗(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/HelpTip/NoWeaponWarning/NoWeaponWarning.gd | HelpTip | 无武器警告提示弹窗(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/HelpTip/OrbHelp/OrbTip.gd | HelpTip | 宝珠(Orb)玩法帮助提示(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/HelpTip/SpecializationTip/SpecializationTip.gd | HelpTip | 专精系统帮助提示弹窗(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/HelpTip/WeaponIntro/WeaponIntro.gd | HelpTip | 武器介绍提示弹窗(继承 HelpTip) | 无 |
| Scenes/Popups/Dialogs/Keybinds/KeybindOption.gd | HBoxContainer | 单个按键绑定行:显示并捕获重绑按键 | _ready,_update,_on_Button_pressed,_unhandled_key_input |
| Scenes/Popups/Dialogs/Keybinds/Keybinds.gd | PopupBase | 按键设置弹窗:列出全部键位配置 | _ready,_on_DoneButton_pressed,_reset_focus |
| Scenes/Popups/Dialogs/MTXStore/MTXItem.gd | VBoxContainer | 商城物品条目:展示并购买 | _ready,_on_Button_pressed |
| Scenes/Popups/Dialogs/MTXStore/MTXStore.gd | PopupBase | 商城弹窗:拉取并渲染商品列表 | _ready,_on_CloseButton_pressed,_render_shop |
| Scenes/Popups/Dialogs/ModHelp/ModHelp.gd | PopupBase | 词缀图鉴:按类别列出/搜索词缀 | _ready,_on_item_selected,_physics_process,_on_Button_pressed,render_mods |
| Scenes/Popups/Dialogs/ModHelp/ModTab.gd | VBoxContainer | 词缀图鉴分类 Tab 内容容器 | _ready |
| Scenes/Popups/Dialogs/ModHelp/TierGroup.gd | VBoxContainer | 词缀 Tier 分组:等级标签与搜索过滤 | _ready,get_tier_label,_search_changed |
| Scenes/Popups/Dialogs/OutfitSelector/OutfitOption.gd | Button | 外观选择条目按钮 | _ready,_on_OutfitOption_pressed,_update |
| Scenes/Popups/Dialogs/OutfitSelector/OutfitSelector.gd | PopupBase | 外观选择器:分 Tab 选择装备外观 | _ready,_physics_process,_on_tab_changed,_on_outfit_changed,_on_Button_pressed |
| Scenes/Popups/Dialogs/PassiveTree/Edge.gd | Node2D | 天赋树节点连线绘制 | _ready,_update_edge,_process,_draw |
| Scenes/Popups/Dialogs/PassiveTree/PassiveNode.gd | Node2D | 天赋节点:选中/悬停/搜索高亮/缩放 | _ready,_resync,reset_focus_sprite,reset_modulate,toggle |
| Scenes/Popups/Dialogs/PassiveTree/PassiveTree.gd | - | 未确定,函数:无(空脚本文件) | 无 |
| Scenes/Popups/Dialogs/PassiveTree/PassiveTreeContainer.gd | Node2D | 天赋树画布:平移/缩放/居中聚焦节点 | _ready,center_on,_input,_on_input_changed,_process |
| Scenes/Popups/Dialogs/PassiveTree/PassiveTreePopup.gd | PopupBase | 天赋树弹窗:重建、加点/退款、生效统计 | _ready,_process,rebuild,_on_tree_changed,resync |
| Scenes/Popups/Dialogs/Settings/Settings.gd | PopupBase | 设置弹窗:音量/特效/画面/按键入口 | _ready,_refocus,_on_ResetButton_pressed,_on_confirm,_on_ReturnButton_pressed |
| Scenes/Popups/Dialogs/SkillLoadoutSelector/LoadOption.gd | HBoxContainer | 技能配装存档条目:加载/删除 | _ready,_on_LoadButton_pressed,_on_DeleteButton_pressed |
| Scenes/Popups/Dialogs/SkillLoadoutSelector/SkillLoadoutSelector.gd | PopupBase | 技能配装选择弹窗 | _ready,_on_CloseButton_pressed |
| Scenes/Popups/Dialogs/SkillSelect/SkillButton.gd | VBoxContainer | 技能槽按钮:渲染并装备技能 | _ready,select,update_skill,render_skill,_on_SkillButton_pressed |
| Scenes/Popups/Dialogs/SkillSelect/SkillConfigurator.gd | PanelContainer | 未确定(仅声明技能槽位变量),函数:无 | 无 |
| Scenes/Popups/Dialogs/SkillSelect/SkillList.gd | PopupBase | 技能列表弹窗:选择/装备/清除技能 | sort_skills,_ready,_grab_focus,select_skill,equip_skill |
| Scenes/Popups/Dialogs/SkillSelect/SkillListOption.gd | Button | 技能列表条目按钮 | _ready,_on_SkillListOption_mouse_entered |
| Scenes/Popups/Dialogs/SkillSelect/SkillSelect.gd | PopupBase | 技能选择界面:槽位编辑与配装管理 | _ready,_grab_focus,_on_Button_pressed,_on_NewLoadoutButton_pressed,_on_ChangeLoadoutButton_pressed |
| Scenes/Popups/Dialogs/SkillSelect/SupportButton.gd | VBoxContainer | 辅助技能槽按钮:渲染并装备辅助 | _ready,select,update_support,render_support,_equip_support |
| Scenes/Popups/Dialogs/SkillSelect/SupportList.gd | PopupBase | 辅助技能列表弹窗:选择/过滤/装备 | _ready,_grab_focus,select_support,equip_support,_on_CancelButton_pressed |
| Scenes/Popups/Dialogs/SkillSelect/SupportListOption.gd | Button | 辅助技能列表条目:过滤/悬停 | _ready,_on_SkillListOption_mouse_entered,set_filter |
| Scenes/Popups/Dialogs/SpecializationPicker/SpecializationOption.gd | VBoxContainer | 专精选项卡片:选择专精 | _ready,_on_ChooseButton_pressed |
| Scenes/Popups/Dialogs/SpecializationPicker/SpecializationPicker.gd | PopupBase | 专精选择弹窗 | _ready |
| Scenes/Popups/Dialogs/StarterPicker/StarterOption.gd | VBoxContainer | 新手配装选项卡片 | _ready,_on_ChooseButton_pressed |
| Scenes/Popups/Dialogs/StarterPicker/StarterPicker.gd | PopupBase | 新手配装选择弹窗 | _ready |
| Scenes/Popups/Dialogs/StarterPicker/StarterSkillInfo.gd | VBoxContainer | 新手配装中的技能信息展示 | _ready |
| Scenes/Popups/Dialogs/TextInputDialog.gd | PopupBase | 文本输入对话框:输入并提交 | _ready,_process,_on_AcceptButton_pressed,_on_CloseButton_pressed,submit |
| Scenes/Popups/Dialogs/TintedConfirmationDialog.gd | ConfirmationDialog | 带主题色确认对话框扩展 | _enter_tree,_ready |
| Scenes/Popups/Dialogs/TreeSelector/LoadOption.gd | HBoxContainer | 天赋树存档条目:加载/删除 | _ready,_on_LoadButton_pressed,_on_DeleteButton_pressed |
| Scenes/Popups/Dialogs/TreeSelector/TreeSelector.gd | PopupBase | 天赋树存档选择弹窗 | _ready,_on_CloseButton_pressed |
| Scenes/Popups/Dialogs/UniqueHelp/UniqueHelp.gd | PopupBase | 暗金基因图鉴:列出/搜索/词缀范围 | _ready,_on_item_selected,_physics_process,_on_Button_pressed,render_items |
| Scenes/Popups/Dialogs/UniqueHelp/UniqueItem.gd | VBoxContainer | 暗金基因条目展示 | _ready |
| Scenes/Popups/Dialogs/UniqueHelp/UniqueModRange.gd | VBoxContainer | 暗金词缀取值范围显示行 | _ready,render_mod |
| Scenes/Popups/Dialogs/WorldMap/Edge.gd | Node2D | 世界地图关卡间连线绘制 | _ready,_draw |
| Scenes/Popups/Dialogs/WorldMap/MapNode.gd | Node2D | 地图关卡节点:聚焦/悬停/点击/排行榜 | _ready,render_leaderboard,set_zoom,grab_focus,release_focus |
| Scenes/Popups/Dialogs/WorldMap/WorldMapContainer.gd | Node2D | 世界地图画布:平移/缩放/居中聚焦 | _ready,center_on,_input,_on_input_changed,_process |
| Scenes/Popups/Dialogs/WorldMap/WorldMapPopup.gd | PopupBase | 世界地图弹窗:重建节点与连线 | _ready,_process,rebuild,create_nodes,create_edges |
| Scenes/Tooltips/GeneTooltip/GeneInfo.gd | PanelContainer | 基因提示内容面板:渲染词缀与统计 | render |
| Scenes/Tooltips/GeneTooltip/GeneTooltip.gd | TooltipBase | 基因悬浮提示框 | render |
| Scenes/Tooltips/SkillTooltip/SkillTooltip.gd | TooltipBase | 技能悬浮提示:绑定统计并渲染/隐藏 | _ready,bind_to_stats,render,hide,update_info |
| Scenes/Tooltips/TooltipBase.gd | CanvasLayer | 提示框基类:限制显示在窗口范围内 | confine_to_window |
| Scenes/UI/ModItem.gd | HBoxContainer | 词缀条目行:名称/数值/锁定状态/品质 | _ready,_on_LockedIcon_pressed |
| Scenes/UI/Notice.gd | Node2D | 场景提示标记精灵:上下浮动动画 | _process |
| Scenes/AreaSkillEffects/AreaSkillEffect.gd | Node2D | 区域性技能效果显示,按半径绘制内外圈并计时到期 | _ready,_update_radius,start,_physics_process,expired |
| Scenes/GrayableButton.gd | CenterContainer | 可置灰按钮的容器节点(空实现) | _ready |
| Scenes/IdleFrame.gd | Reference | 帧计时器:等待N帧后发出timeout信号 | _ready,_on_timeout,idle_frame |
| Scenes/LoadGame.gd | PanelContainer | 载入游戏界面:按刷新率设物理帧率并读档 | _ready |
| Scenes/Menu.gd | PanelContainer | 主菜单:处理开始/退出/设置/帮助等按钮 | _ready,render,_on_StartButton_pressed,_on_QuitButton_pressed,_on_UpgradeButton_pressed |
| Scenes/SoundEffect.gd | Node2D | 播放一次性音效,播完自动释放节点 | _ready |
| Scenes/Stats.gd | Node2D | 实体核心属性系统:伤害/状态/暴击/经验/属性重算 | _initialize_stats,_ready,_recache_gear,get_effective_level,handle_status_change |
| Scenes/StatsContainer.gd | VBoxContainer | 状态栏垂直布局容器(空实现) | 无函数 |
| Scenes/StatusBar/StatusBar.gd | VBoxContainer | 血条与状态标志UI更新显示 | _ready,update_healthbar,_process,update_flags |
| Scenes/World.gd | Node2D | 世界根节点:切换关卡、渲染地图词缀并派发信号 | _enter_tree,_ready,_process,_on_show_info,_on_unplug |


-
-
-




#
#
 
4
.
 
a
d
d
o
n
s
 
—
 
编
辑
器
插
件
(
1
4
)




|
 
脚
本
 
|
 
e
x
t
e
n
d
s
 
|
 
职
责
摘
要
 
|
 
关
键
函
数
 
|


|
-
-
-
|
-
-
-
|
-
-
-
|
-
-
-
|


| addons/AsepriteWizard/animated_sprite/animated_sprite_inspector_dock.gd | - | 编辑器停靠面板:配置并导入AnimatedSprite动画 | _ready,_load_config,_load_default_config,_set_source,_set_layer |
| addons/AsepriteWizard/animated_sprite/import_plugin.gd | - | 自定义导入器:将Aseprite文件导入为动画资源 | get_importer_name,get_visible_name,get_recognized_extensions,get_save_extension,get_resource_type |
| addons/AsepriteWizard/animated_sprite/inspector_plugin.gd | - | 编辑器检查器解析插件(AnimatedSprite) | can_handle,parse_begin,parse_end |
| addons/AsepriteWizard/animated_sprite/sf_wizard_dock.gd | - | 精灵帧向导窗口:选择文件并执行导入 | _ready,_exit_tree,init,_load_persisted_config,_open_aseprite_file_selection_dialog |
| addons/AsepriteWizard/animated_sprite/sprite_frames_creator.gd | - | 从Aseprite文件/图层创建SpriteFrames动画 | init,_loop_config_prefix,_is_loop_config_enabled,create_animations,_create_animations_from_file |
| addons/AsepriteWizard/animation_player/animation_creator.gd | Reference | 从Aseprite创建AnimationPlayer帧动画 | init,create_animations,_create_animations_from_file,_import,_load_texture |
| addons/AsepriteWizard/animation_player/inspector_plugin.gd | - | 编辑器检查器解析插件(AnimationPlayer) | can_handle,parse_begin,parse_end |
| addons/AsepriteWizard/animation_player/sprite_inspector_dock.gd | - | 停靠面板:配置AnimationPlayer动画导入 | _ready,_load_config,_load_default_config,_set_source,_set_animation_player |
| addons/AsepriteWizard/aseprite/aseprite.gd | - | 封装Aseprite命令行:导出文件/图层/列表 | init,export_file,export_layers,export_layer,_add_ignore_layer_arguments |
| addons/AsepriteWizard/config/config.gd | - | 插件配置读写:命令、路径、导入选项 | load_config,save,default_command,get_command,set_command |
| addons/AsepriteWizard/config/config_dialog.gd | - | 配置对话框:编辑并测试Aseprite命令 | _ready,init,_on_save_button_up,_on_close_button_up,_on_test_pressed |
| addons/AsepriteWizard/config/result_codes.gd | - | Aseprite命令返回码到错误消息的映射 | get_error_message |
| addons/AsepriteWizard/config/wizard_config.gd | - | 向导配置的序列化与base64编解码 | encode,decode,_decode_base64,_is_wizard_config |
| addons/AsepriteWizard/plugin.gd | - | 插件主入口:注册菜单/导入器/停靠面板 | _enter_tree,_exit_tree,_load_config,_setup_menu_entries,_remove_menu_entries |