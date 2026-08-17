# PHASE 2a — 世界层（Hub/Hideout）设计规格（Design Spec）

> 记录：2026-08-17。作者：designer lane。只读产出，未修改任何游戏文件、未写 mod.json。
> 权威依据：`docs/requirements/HD_UI_REMASTER.md`（§五 色板 / §六 颜色规则 / §九 间距 / §十 圆角 / §十一 边框 / §十二 阴影 / §十三 网格 / §十四 世界互动对象 / §十五 世界名称标签 / §十六 Arcane Waypoint / §二十九 性能 / §三十五 决策优先级）、`docs/requirements/PHASE0_VISUAL_AUDIT.md`（A1-A9 世界层审计）、`docs/requirements/PHASE1_DESIGN_SPEC.md`（token 折算范例）、`.slim/deepwork/hd-ui-remaster.md`（ora-2 裁决：PHASE 2 拆 2a/2b；2a 五项=Grid→背景→标签→物体展示；**tileset ASSET_PATCH 链路为 2a Grid 可行性闸门，由 fixer 并行预检**；project.binary 不可 patch）。
> 用途：fixer lane 按本规格转录为 mod.json。**本规格不新增任何文件路径**（roundtrip 3744 路径集合先验结论：改动全部落在既有文件内；新增 .gd/.tscn/.tres 会破坏 roundtrip，禁止）。不引入全屏后处理 / 大 blur / 大 bloom / 新资产贴图（tileset 路径除外，见 §1-B）。不修改玩法、碰撞、输入、相机 zoom、基础分辨率。

---

## 0. 本次用到的色板与折算（全部来自 §五 token，或由 §五 直接推导；浮点取 PHASE 1 同款 6 位风格）

| Token | Hex | Godot Color 8bit 浮点（0-1） | 备注 |
|---|---|---|---|
| Background Deep | `#090C10` | `Color( 0.0352941, 0.0470588, 0.0627451, 1 )` | §五；PHASE 1 已用 |
| **World Background** | `#0C1015` | `Color( 0.0470588, 0.0627451, 0.0823529, 1 )` | §五世界背景；A1 ColorRect 纯黑 → 本值 |
| Surface 1 | `#121820` | `Color( 0.0705882, 0.0941176, 0.12549, 1 )` | §五；PHASE 1 已用 |
| Surface 2 | `#18212A` | `Color( 0.0941176, 0.129412, 0.164706, 1 )` | §五；PHASE 1 已用 |
| Elevated Surface | `#1D2731` | `Color( 0.113725, 0.152941, 0.192157, 1 )` | §五；PHASE 1 已用 |
| Normal Border | `#293642` | `Color( 0.160784, 0.211765, 0.258824, 1 )` | §五；PHASE 1 已用 |
| Highlight Border | `#405365` | `Color( 0.25098, 0.32549, 0.396078, 1 )` | §五；PHASE 1 已用 |
| Primary Text | `#E4E9EF` | `Color( 0.894118, 0.913725, 0.937255, 1 )` | §五主文本；世界标签文字 |
| Secondary Text | `#9DA9B5` | `Color( 0.615686, 0.662745, 0.709804, 1 )` | §五；PHASE 1 已用 |
| Disabled Text | `#626D78` | `Color( 0.384314, 0.427451, 0.470588, 1 )` | §五禁用；物体 Disabled 态 |
| Arcane Accent | `#79D98B` | `Color( 0.47451, 0.85098, 0.545098, 1 )` | §五品牌绿；PHASE 1 已用 |
| Warm Interaction | `#D99A4E` | `Color( 0.85098, 0.603922, 0.305882, 1 )` | §五暖交互；本规格仅作 Disabled 备选/注释，默认不用 |

> 折算核对：`0x0C=12/255=0.0470588`、`0x10=16/255=0.0627451`、`0x15=21/255=0.0823529`；`0xE4=228/255=0.894118`、`0xE9=233/255=0.913725`、`0xEF=239/255=0.937255`；`0x62=98/255=0.384314`、`0x6D=109/255=0.427451`、`0x78=120/255=0.470588`。
> 世界层附加色（§五 推导，仅用于网格/描边/底色，仍是同一灰蓝 family）：`#141C25 = Color( 0.0784314, 0.109804, 0.145098, 1 )`、`#1F2934 = Color( 0.121569, 0.160784, 0.203922, 1 )`、`#1A222C = Color( 0.101961, 0.133333, 0.172549, 1 )`、`#161E27 = Color( 0.0862745, 0.117647, 0.152941, 1 )`、`#222D38 = Color( 0.133333, 0.176471, 0.219608, 1 )`。

### 0.1 绘制量纲换算（重要，fixer 转录前必须先确认）

- 相机 `Camera2D.zoom = Vector2( 0.5, 0.5 )`（`Player.tscn:567-572`，审计 A2）。**世界 1px 屏上 = 0.5px**。为获得"屏上 1px"的稳定线条（消灭 A1 亚像素闪烁），**地面系线条线宽一律按 2 世界像素**给出（AA 开启）；对象系/标签系（微小件）同理按 2 世界像素起。
- 逻辑视口 1280×800 → 可见世界范围 = 2560×1600（以玩家为中心 ±1280 / ±800）。
- `BaseLevel._ready` L365 `$TileMap.tile_set.tile_set_texture(0, Levels.config[Globals.selected_level].tileset)` 会将 Hideout 的 TileSet 第 0 号贴图**运行时替换为 `tileset_hideout`**（`Levels.gd:270`）。即：**Hideout 实际地面贴图 = `tileset_hideout.png`，A1 审计的 `tileset_factory.png`（224×96）与之属同一生成规格**；§1-B 重绘目标与预检都以"运行时实际生效贴图"为准（fixer 确认）。

---

## §1. 网格重设计（HD_UI_REMASTER §十三）

### 1.0 目标与现状

| 项 | 值 |
|---|---|
| 目标 | 网格从"画面主体"降为"辅助空间导航背景"：显著降 alpha、减线宽、降对比；保留 32×32 格距语义；不引入昂贵 shader |
| 现状（A1） | TileMap autotile；网格烤死在贴图 `tileset_factory.png` 224×96：主面 `#252B38` 64%、棋盘 `#222326` 30%、**1px 格线 `#151C1F` 2.3%**（alpha 3.6% 左右逐通道）；0.5 zoom 下 1px 线亚像素闪烁；线宽/颜色/alpha 全烤死不可调 |
| 机制裁决 | **待 fixer 预检**（oracle Q3：ASSET_PATCH 注入 PNG → 重导入 → stex → pack 链路按 c4 先例预检）。两条路径本规格都给完整视觉参数，最终生效参数组取裁决结果 |
| 硬约束 | 不改 collider（TileMap `collision_layer=256` 与 `ConvexPolygonShape2D` 集合不动）、不改 tile_data、不改 cell_size=32 |

### 1.0 统一格距语义（两路径共用）

- 基础格距 = **32×32 世界 px**（= 16×16 屏 px @zoom0.5），与 `BaseLevel.tscn:41 cell_size`/`cell_custom_transform` 对齐，网格锚定 **世界原点 (0,0)** 与 TileMap 格对齐（对齐 `tile_data` 网格，偏移 0）。
- **major 每 4 格增强**（128 世界 px = 64 屏 px），major 线只轻微增强，不改变"导航"语义。
- **距离衰减：默认不做**（推荐）。理由：可见世界范围固定 2560×1600，恒定弱网格零 per-frame 开销（静态绘制，仅布局时 `update()` 一次）。远处隐约网格提供"世界延续感"（§十三"保持空间导航作用"）。**备选简易衰减**（不引 shader，仅当 S5 判定近景网格仍过强时启用）：以玩家为中心，距离 d<600 全 alpha、600≤d≤1200 线性降至 0.5×、>1200 0.5×（实现为逐线计算 alpha，约 130 条线/帧，成本可忽略）。
- 视觉词表（目标）：minor = 几乎不可见的"织物质感"，major = 隐约的模块分隔。**网格透明度任何状态下不得高于世界物件贴图主体对比度**（§十三禁止）。对象（32×32 贴图）自身即空间锚点。

### 1.1 路径 A —— 运行时网格覆盖层（CODE_PATCH，推荐主路径）

> 若 fixer 预检判定 ASSET_PATCH 链路不可行或成本超限，走本路径。**不新增文件**：把绘制逻辑放进现有 `BaseLevel.gd`，用 `Levels.is_current_level_hideout()` 条件开关，PHASE 5 全局推广时去掉条件即可。

- **宿主**：`04_recovered/Scenes/Levels/BaseLevel.gd`（该文件现无 `_draw`，可安全添加；全仓 _draw 仅 Minimap/WorldMap/PassiveTree 3 处，无冲突）。
- **节点层级**：网格画在根节点（BaseLevel 自身，Node2D）→ 绘制序在所有子节点（含 TileMap z=-4096）**之后**，即网格浮于地面贴图之上、对象/玩家之下（根 z=0，子 TileMap z=-4096 在根之下；玩家在 `World/Level` z=512 的 YSort 中，高于一切）。**禁止**另挂新节点。
- **精确参数**：
  | 参数 | minor | major |
  |---|---|---|
  | 颜色 | Normal Border `#293642` → `Color( 0.160784, 0.211765, 0.258824, 1 )` | Highlight Border `#405365` → `Color( 0.25098, 0.32549, 0.396078, 1 )` |
  | 叠加 alpha | **0.10**（屏上等效 ≈ 5% 视觉） | **0.20** |
  | 线宽 | **2 世界 px**（屏 1px；AA on） | **2 世界 px** |
  | 间距 | 32 世界 px | 每 4 格（128 世界 px） |
  | AA | `antialiased = true` | `antialiased = true` |
  | 绘制范围 | 以玩家为中心 `±(1280, 800)` 世界 + 外扩 1 格（32），整格对齐 `floor((p - range)/32)*32` | 同左 |
  | 距离衰减 | 默认无；备选见 1.0 | 同左 |
- **GDScript 语义（供 fixer 转录，锚点 = 文件末尾 `_on_MobDisabler_timeout` 之后；不逐字节给整文件）**：
  ```
  func _draw_grid_cover() -> void:      # 在 _ready 末尾调用一次；备选衰减模式下每帧调用
      if not Levels.is_current_level_hideout():  return
      var cam_pos = GameState.get_global("player").global_position
      var range_v := Vector2(1280.0, 800.0)          # 世界可见范围 /zoom
      var start := (cam_pos - range_v - Vector2(32,32)).snapped(Vector2(32,32))
      var end   := cam_pos + range_v + Vector2(32,32)
      draw_line 用循环：minor 每条 `Color(0.160784,0.211765,0.258824,0.10)` 宽 2 AA
      major 条件循环：`(int(x/32)%4==0)` 时用 `Color(0.25098,0.32549,0.396078,0.20)` 宽 2 AA
  ```
- **影响文件**：仅 `BaseLevel.gd`（CODE_PATCH；compile manifest 需声明该脚本重编译）。
- **风险**：低-中。① 所有关卡条件为 false 时零开销（`is_current_level_hideout` 快速返回）；Hideout 首次 `_draw` 约 130 条线一次性绘制。② 网格浮于贴图之上——若贴图本身还有格线（现状 tileset 未替换时），会形成"双重格线"：**本路径默认配合"贴图不动"使用，出现双重线时把运行时网格再降 alpha（minor 0.06 / major 0.14）或用 §1-B 重绘贴图消除烤死格线**（联动 S5）。③ 不改碰撞（TileMap collider 原样）。

### 1.2 路径 B —— tileset 重绘替换（ASSET_PATCH，可行性由 fixer 预检裁决）

> fixer 预检通过（c4 先例：`.import/*.stex` 替换 + replacement_sha256）才走本路径。重新绘制 **224×96（7×3 格 @32px）工厂主题贴图**；由 fixer 确认运行时实际生效目标贴图（`tileset_factory.png` 或 `tileset_hideout.png`，见 0.1；两文件生成规格相同，重绘复用同一 TDL，各自的 autotile 变体位沿用原 bitmask 语义，**不得改变 tile 区域几何与 bitmask_flags**）。
- **重绘 TDL（视觉分层，@32px 模数，逐像素见图）**：
  | 层 | 色值 | 说明 |
  |---|---|---|
  | 主面基底 | `#1A222C` | 暗蓝灰工厂地板（= §五 Surface2→Elevated 之间的灰蓝 family，取代现 `#252B38`，降 25% 亮度对比） |
  | 棋盘交替 | `#161E27` | 每格交替，与主面 ΔRGB ≤6/255，形成极弱针织感（取代现 `#222326`） |
  | minor 格线 | `#141C25` 1px，每 32px 一格 | 取代现 `#151C1F` 2.3%；**对比度再降约 40%**，视觉 = 接缝而非线条 |
  | major 格线 | `#1F2934` 1px，每 128px（第 4 格） | 轻微增强的模块分隔 |
  | 平台外沿（autotile 边界 tile） | `#222D38` 1px，仅外侧 | 地面与"虚空"交界处的克制的收边，辅助空间读解 |
  | 顶部渐变蒙版 | 无（不做贴图内渐变） | 克制 |
- **与路径 A 的关系**：B 生效后贴图自带弱网格 → **不再叠加运行时层**（二选一，不双开；若 S5 需要可叠加运行时层并降 A 参数至 minor 0.06/major 0.14，但默认单层）。
- **影响文件**：`03_raw/Tilesets/tileset_factory.png` 与 `tileset_hideout.png` 的对应 `.import` `.stex`（ASSET_PATCH，c4 先例：source_path / preimage_sha256 / replacement_sha256 / expected_dimensions=[224,96] / expected_format_marker）；目标贴图路径以外**不得**新增其他资产。
- **风险**：中（预检闸门内）。① PNG 本体在 03_raw 中不存在（仅 .import），重绘需由 fixer 的 asset 注入链路生成/替换 stex，preimage 以既有 stex 为准；② autotile 变体位（bitmask_flags 16 项 + shapes 关联）必须逐位对齐，任何一格的视觉改造不得移动几何——重绘只改色值不改形状；③ 若 fixer 判定链路不可行 → 回退 §1.1 路径 A（参数已就绪，零阻塞）。

---

## §2. 世界背景（暗色底）

### 2.0 目标与现状

| 项 | 值 |
|---|---|
| 目标 | 统一暗色底：`World Background #0C1015`；加极弱冷色调层次（克制，不做新贴图）；清理空 ScreenSpaceGI 死代码 |
| 现状（A1/A9） | `BaseLevel.tscn` ParallaxBackground > ParallaxLayer (motion_mirroring 160×160) > ColorRect **纯黑 `Color(0,0,0,1)`** 3840×2160 + TextureRect 空（无贴图）；引擎 `default_clear_color` 中灰 `Color(0.255,0.255,0.255,1)`（project.binary 实测）；`World.tscn` 根节点挂 `ScreenSpaceGI.tres`（**空 shader，仅 `shader_type canvas_item;`**） |
| 硬约束 | project.binary 不可 patch → clear color 类改动**须 CODE_PATCH 运行时**；不新增背景贴图资产 |

### 2.1 设计参数

- **ColorRect 纯黑 → `World Background #0C1015`**：`Color( 0.0470588, 0.0627451, 0.0823529, 1 )`。
  - 这是主改动：世界底从"纯黑"变"冷蓝黑"，与 tileset 灰蓝、Arcane 绿形成同冷暖语言（§五 World Background 设计意图）。
  - 辐射面：**全部关卡**（BaseLevel 是唯一背景宿主；地图/Boss/Ladder 均继承）背景统一，一致性收益（非 Hideout 专项破坏）。
- **极弱色调层次（备选，默认不做）**：Godot 3 无 GradientTexture2D；若 S5 判定纯色底过于"平"，加**单层垂直渐变**：在 `BaseLevel.tscn` 内联 `GradientTexture`（sub_resource，非资产文件）：顶部 `Color(0.027451, 0.0352941, 0.0470588, 1)`（≈#07090C）→ 底部 `World Background #0C1015`，叠加到 ColorRect 之上的半透明 TextureRect（modulate alpha 0.35），营造"自上而下的微弱空气感"。**克制标准：渐变范围 ≤ ΔRGB 8/255，alpha ≤ 0.4**。默认档不做，等 S5 证据。
- **default_clear_color 中灰 → 同色**：`VisualServer.set_default_clear_color(Color(0.0470588, 0.0627451, 0.0823529, 1))`（Godot 3.5 API）。ColorRect 3840×2160 理论上全覆盖视口，clear color 仅在 ColorRect 未覆盖边缘露出——**统一为同一色，杜绝任何视角下的中灰闪现**。
- **ScreenSpaceGI（A9）——清理引用，保留文件**：
  - `World.tscn:11-12` 根节点 `material = SubResource( 1 )`（空 shader）→ **删除该 material 赋值**（RESOURCE_PATCH，最小 diff：删 L11-12 两行或令 material 引用解除）。
  - **`ScreenSpaceGI.tres` 文件本身保留**（不删路径；删除会改变 roundtrip 3744 路径集合，违反铁律）。文件保留=零风险，仅不再被引用。
  - 不实现"真 GI/色温层"（§二十九：Shader 是调味不是主体；世界层光照交给 PHASE 6 资产/光照决策）。

### 2.2 落地路径标注

| 改动 | 类型 | 目标文件 | 备注 |
|---|---|---|---|
| ColorRect 颜色 | RESOURCE_PATCH | `04_recovered/Scenes/Levels/BaseLevel.tscn`（L27 `color = Color( 0, 0, 0, 1 )` → 新色；`mouse_filter`、`rect_min_size` 不动） | old_text 逐字节，LF |
| （备选）渐变层 | RESOURCE_PATCH | 同上（内联 GradientTexture + 半透明 TextureRect） | 默认不做 |
| clear color | **CODE_PATCH** | 运行时——锚点候选：`Scenes/World.gd` `_ready()`（L18-20 已有 Input/GUI 连接，插入 1 行）或 `GameState._ready`（fixer 确认存在性与安全锚点） | 必须运行时；project.binary 不可 patch |
| 移除空 shader 引用 | RESOURCE_PATCH | `04_recovered/Scenes/World.tscn`（L11-12） | `ScreenSpaceGI.tres` 文件保留 |

### 2.3 影响文件 / 风险

- 影响：`BaseLevel.tscn`、`World.tscn`、`World.gd`（或 GameState）、（S5 后才可能的 `BaseLevel.tscn` 渐变段）。全部既有路径。
- 风险：低。① clear color 运行时设置点若锚不到安全位置（GameState._ready 不确定），可**跳过**并声明"ColorRect 全覆盖已保证无中灰露出"（降级，非阻塞）；② 背景变冷蓝黑会影响所有关卡的"暗度感"——与 PHASE 1 已上线的按钮/XP 等暗色系一致，预期良性，S5 确认；③ TextureRect 空（无贴图）保持不动，不补图。

---

## §3. 世界名称标签（HD_UI_REMASTER §十五）

### 3.0 目标与现状

| 项 | 值 |
|---|---|
| 目标 | 统一 World Label：Normal = 仅文字、透明度适中；Nearby = 极轻半透明底；Hover = Accent 下划线/小边框。克制：不套巨大 UI 卡片，不占大量空间 |
| 现状（A7） | `Interactable.tscn:25-27`：标签父节点 **Node2D scale=0.5、pos(0,-6)** > VBoxContainer（anchor 半居中 margin_top=-40、256 宽、theme=`InGameText.tres`）> HBoxContainer > Label（align=1）。`InGameText.tres:5-10`：rsans **18px、outline 1px 纯黑、use_filter=true**。**结果：屏上 9px、描边减半为 0.5px 且亚采样**；无底衬、白字直落暗底 |
| 机制事实 | `InGameText.tres` 全仓仅 `Interactable.tscn` 1 处引用（已 grep 核实）→ 可安全精修主题。`Interactable.tscn` 被 8+ 子场景继承（Bench×5 / Statue×2 / SharedStash / Portal；Portal 的标签 `Node2D` 子节点 `visible=false`） |

### 3.1 设计参数

- **去节点缩放**：`Interactable.tscn:27` `scale = Vector2( 0.5, 0.5 )` → **`scale = Vector2( 1, 1 )`**（或删除该行，Godot 默认 1,1）。位置 `(0,-6)` 保持。→ 文字从屏上 9px 恢复 18px。
- **字号定值：18px**（任务区间 16-20px 内取 18，**保持 `InGameText.tres` size=18 不动**——PHASE 1 明确"字号=布局，16px→18px 推后 PHASE 4"，此处去缩放即恢复 18px，不改字号档）。
- **描边 2px**（任务要求"2px 描边色值"；屏上 2px 在 18px CJK 上保证叠于物件上的可读性）：
  - `InGameText.tres` `outline_size = 1` → **`outline_size = 2`**
  - `outline_color = Color( 0, 0, 0, 1 )` → **`Color( 0.0352941, 0.0470588, 0.0627451, 0.9 )`**（Background Deep 90% 不透明——与底衬/世界暗底同 family，比纯黑更"冷"且与底衬融合，不产生锐利黑边）
  - `use_filter = true` 保持（矢量字体 AA）。
- **半透明深色底衬 + 三态**（实现：`Interactable.tscn` 内联 `StyleBoxFlat` + `Interactable.gd` 状态控制；**默认不显示底衬**，Normal 态仅文字）：

  | 状态 | 触发条件（沿用现有信号，不加新输入） | 文字 opacity | 底衬（StyleBoxFlat） | 附加 |
  |---|---|---|---|---|
  | **Normal** | 默认 | `Color( 0.894118, 0.913725, 0.937255, 0.85 )`（Primary Text 85%） | 无（`bg_color alpha 0`） | 无 |
  | **Nearby** | `Area2D.area_entered`（玩家已进入；`_on_Area2D_area_entered` 现有回调） | `Color( 0.894118, 0.913725, 0.937255, 1 )` | `bg_color = #0C1015 alpha 0.45`，圆角 **4**，content margin L/R=**8**、T/B=**4** | 无 |
  | **Hover** | `mouse_entered`（`_on_mouse_entered` 现有回调；控制器忽略） | 同 Nearby (1.0) | `bg_color alpha **0.62**`，圆角 4，margin 同左 | **Accent 下划线**：`border_width_bottom = 2` + `border_color = Arcane #79D98B (alpha 0.85)`（§十五"Accent underline"；其余边 = 0） |

  > 底衬参数：`corner_radius_top/bottom_left/right = 4`（§十 Small Radius）；`content_margin` 用 spacing token 8/4（§九）；底衬与标签文字不重叠（Panel 包裹 Label，margin 即内边距）。
  > **三态切换由 `Interactable.gd` 现有布尔驱动**：`mouse_hover`（Hover/Normal）+ 玩家邻近（Nearby，可用 `Globals.current_context_instance == self` 或 area 回调标志，fixer 选实现最简者）。禁止新增信号/输入。
- 标签尺寸预算：7 字 × 18px ≈ 140px 文字 + 16px 底衬 padding ≈ **156px 宽 × 26px 高**，远小于 256px 容器（容器宽度不改，VBox anchor/margins 不动 → **布局零改动**）。

### 3.2 落地路径标注

| 改动 | 类型 | 目标文件 |
|---|---|---|
| `scale` 0.5 → 1 | RESOURCE_PATCH | `Interactable.tscn` L27（`scale = Vector2( 0.5, 0.5 )` 删除或改 `Vector2( 1, 1 )`） |
| 内联底衬 StyleBoxFlat（sub_resource 新增 id=20 等；VBox/HBox 结构不动，给 HBoxContainer 挂 `custom_styles/panel` 或就近容器挂 StyleBox——**fixer 依 preimage 选最小 diff 挂载点**） | RESOURCE_PATCH | `Interactable.tscn` |
| `outline_size` / `outline_color` 精修 | RESOURCE_PATCH | `InGameText.tres`（L7-8；注意 `load_steps=3` 不变量，只改两行值） |
| 三态 opacity/底衬显隐逻辑 | CODE_PATCH | `Interactable.gd`（`_ready`/`_on_mouse_entered`/`_on_mouse_exited`/area 回调内设置 Label modulate 与 StyleBox；compile manifest 声明） |

### 3.3 影响文件 / 风险

- 影响：`Interactable.tscn`（8+ 实例继承）、`InGameText.tres`（唯一引用方 = Interactable.tscn）、`Interactable.gd`（基类，全 Interactable 子类继承——子类均未覆写 `_draw`，已 grep 核实；`_ready` 有子类覆写（SkillBench 等）但**不调用 super** → 标签文字由各自 `get_context_text` 经 PopupManager 触发或原样继承，本改动只在基类加样式控制，不破坏子类既有 `_ready` 行为）。
- 风险：中。① `Interactable.tscn` 是 8+ 场景的共享父场景，结构微调（仅样式挂载点）需 preimage 逐字节，fixer 确认最小 diff；若挂载点判定风险高，可退化为"底衬全部由 `Interactable.gd` `_draw` 绘制矩形"（参数不变，仅实现路径变化，需 fixer/designer 复评）；② Portal 标签 `visible=false` 不受影响；③ 18px + 2px 描边在 0.5 zoom 下 = 屏上 9px 字号（已恢复），S5 验证中文 4-7 字可读；若仍不足，PHASE 4 字号档统一处理（本阶段不改字号档）。

---

## §4. 世界互动对象展示（HD_UI_REMASTER §十四）

### 4.0 目标与现状

| 项 | 值 |
|---|---|
| 目标 | 仓库/工作台/NPC/升级点统一视觉语言：非常轻 ground shadow + 选择圈 + 小范围 halo + interaction marker；五态 Normal/Nearby/Hover/Interactable/Disabled 精确切换；不改 gameplay/碰撞/输入 |
| 现状（A3/A4/A8） | 无任何选择圈/halo/点选高亮环；hover 无视觉反馈。物体 = 32×32 像素贴图（bench 六帧 96×64 / statue 32×32 / chest 32×32），`SharedStash.tscn`/`SkillBench.tscn` 有 `shadow.png`（scale(2,2)）；`Mob.tscn:15-24` OutlineShader（width=1，enabled=false 默认关；magic `#0024E5`/rare `#E3E500` α0.31）；`Notice.tscn` 红 `#D01010` 浮动（装饰，不属此系统） |
| 机制事实 | 全仓 `_draw` 仅 3 处（Minimap/WorldMap/PassiveTree）→ 在 `Interactable.gd` 加 `_draw` 无冲突。**OutlineShader.tres 无 `enabled` uniform**（shader 源码无该 uniform；Mob.tscn 设置了 `shader_param/enabled=false` 但 shader 不读它，Mob.gd:116-117/124-125 set color+enabled 实际只改颜色）→ **该 shader 不满足"默认关"语义，且被 18+ Mob 场景引用，共享修改会牵连怪物** → 结论见 4.1 |

### 4.1 实现策略裁决（designer 结论，供 fixer）

- **不直接复用 Mob OutlineShader**：① shader 无 enabled 开关（预设的 enabled/pattern/inside/make_transparent/add_margins 均非 shader uniform，写入无效）；② 共享文件（Mob/18+ 子场景 + Pickup + 3 Boss）改 code 会全局牵连；③ 像素贴图（32×32）轮廓像素化，AA 质量差。
- **不新建 shader**：新增 `.tres` 文件 = 新路径 = 破坏 roundtrip 3744。**禁止**。
- **走程序绘制**：`Interactable.gd`（基类）加 `_draw()` + 状态变量 → 全部 8+ 子场景（bench/statue/stash/portal）自动继承，零新文件、零新资产、不动碰撞（Area2D/CollisionShape2D/StaticBody2D 全部原样）。**这是一个设计决策 + fixer 联动确认项**（若 fixer 判定基类插桩有 preimage 风险，可在 `Interactable.tscn` 内联 `_custom_draw` Node2D 子节点挂 `Interactable.gd` 内的绘制函数，参数不变）。
- 绘制层序：ground shadow/halo **画在 Sprite 之下**（在根 `_draw` 中先画，或加 z 低于 Sprite 的绘制段）；选择圈/交互标记画在 Sprite 之上（`_draw` 中后画段）。同一 `_draw` 内用 draw 顺序控制即可（Godot 同节点内后者在上）。

### 4.2 五态精确参数（屏上量纲 @zoom0.5，世界值已 ×2）

| 状态 | 触发（沿用现有回调/标志，不加新信号） | ground shadow | 选择圈 | halo | interaction marker | 物件 modulate |
|---|---|---|---|---|---|---|
| **Normal** | 默认 | 保留既有 shadow 贴图（已有场景）或程序椭圆（新统一：`draw_set_transform` 压扁圆，rx=18/ry=6 世界，`Color(0.0352941,0.0470588,0.0627451,0.35)`，位置物件底 (0, 本体高/2)） | 无 | 无 | 无 | `Color(1,1,1,1)` |
| **Nearby** | `area_entered`（玩家入 512 layer Area2D） | 同 Normal | 无（或超弱环，见注） | 微弱 halo：`draw_circle r=26 世界, Arcane alpha 0.08` | 无 | 1.0 |
| **Hover** | `mouse_entered` | 同 Normal | **选择圈**：`draw_arc(center=Vector2.ZERO, radius=22 世界, start=0, end=TAU, points=32, width=2 世界, antialiased=true, color=Highlight Border alpha 0.75)` | halo 升至 alpha **0.14** | 无 | 微亮 `Color(1.0,1.0,1.0,1.0)`（不调色相） |
| **Interactable** | Hover/Nearby 且可执行交互（`mouse_hover == true`；点击由现有 `_input`/`on_interact` 不变） | 同 Normal | 圈色 → **Arcane `#79D98B` alpha 0.85**，radius 同 22，width 2 | halo `0.10`（回落，避免与圈抢视觉） | **marker**：物件上方 (0, -20 世界) 小圆点 `draw_circle r=2.5 世界, Arcane alpha 0.85, AA`（§十四"小范围 Accent 提示"） | 1.0 |
| **Disabled** | 子类设置 `disabled = true`（预留标志；Portal 未装备武器、加载中等不可交互——**本阶段仅预留参数，不接玩法判定**） | 无（或 α 0.15） | 无 | 无 | 无 | `Color(0.384314,0.427451,0.470588,0.55)`（Disabled Text 55%） |

> 参数语义：圈/环全部 `antialiased=true`（§二十四 AA）；线宽 2 世界 px=屏 1px；halo 用 `draw_circle`（铺底 alpha 圆，非描边）成本极低（≤4 图元/帧，静态态不重画除外——**状态切换才 `update()`，非 per-frame**，性能零压力）。
> Nearby 超弱环（备选，默认不加）：`r=22, Width 1 世界, Normal Border alpha 0.15`——仅当 S5 认为"玩家接近但未悬停"需要空间提示时启用。
> contrast 规则（§六/三十五）：非交互态一律无 Accent；Accent 只出现在 Interactable 与 Hover 下划线（§3）两处。

### 4.3 落地路径标注

| 改动 | 类型 | 目标文件 |
|---|---|---|
| `_draw()` 五态绘制 + 状态标志（`mouse_hover` 已有；补 `nearby`/`disabled` 变量）+ 状态切换时 `update()` | CODE_PATCH | `Interactable.gd` |
| （可选）程序 ground shadow 统一：若 S5 判定各场景 shadow.png 大小不一违和，统一走程序椭圆（`_draw 第一段`） | CODE_PATCH | 同上（场景内 shadow Sprite 保留、视觉由程序层统一，不删节点） |
| 已有 shadow 贴图场景保持不动 | — | `SkillBench/SharedStash` 等（零改动） |

### 4.4 影响文件 / 风险

- 影响：`Interactable.gd`（基类；8+ 子场景继承自动生效）。compile manifest 需声明 `Interactable.gd` 重编译，且**其子类脚本若已声明编译须确认依赖链覆盖**（沿用 PHASE 1 P1 先例））。
- 风险：中。① 基类 `_draw` 需要全部子类不覆写 `_draw`（已 grep 核实全仓无 Interactable 子类绘制覆写）✓；② 若子类场景自带 shadow 贴图（SharedStash scale(2,2)），程序椭圆与贴图 shadow 并存会重影——**设计决定：程序椭圆仅在无 shadow 贴图的场景生效（`has_node("Shadow")` 检测），有贴图的保持贴图**（统一"轻"语义即可，不强求同实现）；③ 不动 Area2D/Collision/StaticBody → 玩法零影响；④ 训练木桩（`TrainingDummy.tscn`）**不是** Interactable，不在本系统内（A3 归入 Mob 体系，PHASE 5/6 处理）。

---

## §5. Arcane Waypoint（HD_UI_REMASTER §十六；审计 A6 中央绿十字）

### 5.0 目标与现状

| 项 | 值 |
|---|---|
| 目标 | 中央绿十字 → 圆形结构 Arcane Waypoint：程序绘制 + AA + 柔和 Arcane Green + 极轻 glow + 缓慢呼吸（**<0.3Hz**）+ 激活/未激活双态；优先程序绘制（可调），不引入昂贵 shader |
| 现状（A6） | `Portal.tscn`：Interactable 实例 + `portal.aseprite` 128×128 四帧 64×64（绿 `#409020`/亮绿 `#70F040`）Sprite（frame=3、speed_scale=0.5、playing）；交互圈 `CircleShape2D r=32`；Hideout 位置 `(0,-128)`（`HideoutLevel.tscn:213-214`）；标签子节点 `visible=false`。全场景唯一高饱和元素但无光晕、5fps 有跳帧感 |
| 硬约束 | 不改交互圈半径/玩法（`on_interact` → map/warning 原样）；不新增贴图/shader；呼吸频率必须 **<0.3Hz**（§十六） |

### 5.1 设计参数（程序绘制，`Portal.gd` 扩展）

- **宿主**：`Portal.gd`（extends Interactable，可安全加 `_process`/`_draw`；当前文件无二者）。`_draw` 挂在根节点（Portal Node2D）→ 绘制在 Sprite 之下；滚动环/光晕作"底座"，贴图动画作"内核"（职责分离，不产生遮挡问题）。
- **几何（圆心=Portal 原点，全部 AA）**：
  | 元素 | 几何 | 未激活（idle） | 激活（玩家进入 Area2D，沿用 `_on_Area2D_area_entered`） |
  |---|---|---|---|
  | 外层光晕 | `draw_circle r=34` 世界 | Arcane alpha **0.035** | **0.06** |
  | 次层光晕 | `draw_circle r=28` 世界 | Arcane alpha **0.055** | **0.09** |
  | 外主环 | `draw_arc r=26, width=2 世界, points=48, AA` | Arcane alpha **0.40** | **0.65** |
  | 内细环 | `draw_arc r=19, width=1 世界, points=40, AA` | Arcane alpha **0.22** | **0.35** |
  | 中心几何 | 贴图动画原生（绿十字内核）——**不重复绘制**，克制 | 贴图 `modulate = Color(1,1,1,1)` | 贴图 `modulate = Color(0.96,1.06,0.93,1)`（极微提亮，或 S5 后决定；默认 1,1,1 不动） |
- **呼吸（关键参数）**：
  - 频率：**0.2 Hz**（周期 5s；<0.3Hz ✓，§十六"缓慢"）。实现：`_process` 累积 `t += delta`，`phase = sin(t * TAU * 0.2)`。
  - 幅度：外主环 radius 26 **±1.5 世界**；外主环 alpha 0.40 ↔ 0.48（未激活）/ 0.65 ↔ 0.73（激活）——**振幅 ≤14%**，视觉为"缓慢起伏"而非"闪烁"。
  - 内细环不呼吸（静定，提供几何锚定）。
  - 光晕随相位同步微调 alpha（±0.01，可忽略）。
- **glow 策略**：三层叠加（r34 α0.035 / r28 α0.055 / 主环）≈ 柔和光晕；**不用 Bloom、不用后处理、不用 shader**（§十六"非常轻 Glow"+§二十九）。光晕圆为静态时仅每帧两处 alpha 变化，成本可忽略。
- **双态切换**：激活 = 玩家进入交互圈 Area2D（`_on_Area2D_area_entered` 已有 → 复用 Interactable 的 nearby 状态）；未激活 = 默认。**不做玩法判定**（是否可出图由 `on_interact` 原逻辑负责，视觉双态只反映"邻近度"）。
- 贴图动画跳帧感（5fps，审计 A6）**不改**（改 `speed_scale` 属素材行为，PHASE 6 重绘 portal.aseprite 时一并处理；程序层呼吸已提供平滑节奏锚点）。

### 5.2 落地路径标注

| 改动 | 类型 | 目标文件 |
|---|---|---|
| `_process` 呼吸计时 + `_draw` 三层光晕/双环/双态 | CODE_PATCH | `Portal.gd`（新增约 30-40 行；compile manifest 声明） |
| （可选）近邻标志接线：Portal 的 area 回调在基类已存在（`_on_Area2D_area_entered`），若需在 Portal.gd 感知邻近态，调 `queue_redraw` 或直接由 `_process` 读 `Globals.current_context_instance == self` | CODE_PATCH | `Portal.gd`（不新增信号） |

### 5.3 影响文件 / 风险

- 影响：`Portal.gd`（唯一文件；`Portal.tscn` 零改动——不引新节点，绘制全部在根 `_draw`）。全仓仅 1 个 Portal 场景。
- 风险：低。① 呼吸 `_process` 常驻 0.2Hz 相位计算（2 次 sin/帧）成本可忽略；② 绘制在 Sprite 之下——若贴图帧动画占满 64×64（r=32 世界）而环 r=19 会被贴图盖住：**设计取舍 = 环只保留外主环 r=26（贴图外露区域）与 r=19 内细环（若 S5 显示被贴图遮没，可把内细环半径改 r=20 并缩小贴图 Sprite scale 至 0.85——参数已备，S5 定）**；③ 不动交互圈/玩法；④ 标签 `visible=false` 保持（Waypoint 不显示文字标签，克制）。

---

## §6. 2a 实施顺序建议（依 oracle Q4：Grid→背景→标签→物体→Waypoint）

> oracle：2a=方向试金石，**轻量门禁**（机器 gate + 世界层专项 S5）。建议 2 个 mod、各自独立 candidate，避免一次 5 项导致 S5 回归定位困难：

| 批次 | 内容 | Mod 建议 | 验证重点（S5 世界层专项） |
|---|---|---|---|
| **W2a-1（底座）** | §1 网格（A 或 B，等 fixer 预检）+ §2 背景 | 1 个 mod（2 组 patch 或 2 个 mod 同 candidate） | 网格不再抢镜；底色冷蓝黑；无中灰闪现；ScreenSpaceGI 无引用残留（GDRE 断言印证） |
| **W2a-2（对象**)** | §3 标签 + §4 物体展示 + §5 Waypoint | 1 个 mod（3 组 patch） | 标签 18px/描边/三态；五态圈与 halo 层级；Waypoint 呼吸节奏（0.2Hz 目测 = 5s 周期） |

- 理由：Grid+背景是"画布级"改动，互相视觉耦合（网格浮于新底色上、双重格线风险见 §1.1 风险②）→ 同批验证；标签/物体/Waypoint 是"物件级"，共享 `Interactable.gd` 插桩（§3 三态 + §4 五态同文件）→ 同批验证。先底座效果确认，再堆物件层，S5 定位清晰。
- 每批完成后：机器 gate（resolve/apply/compile/delta/pck/roundtrip 3744/boot/GDRE）→ 世界层专项 S5（Hub 截图 BEFORE/AFTER 或 live 检查）→ 归档 E2 → 进下一批。**不晋升 baseline**（套 PHASE 1 定位：人工 S5 前不晋升）。

---

## §7. 需 fixer 预检结果联动项（参数依赖机制裁决）

| # | 联动项 | 裁决影响 | 本规格已备 |
|---|---|---|---|
| 1 | **tileset ASSET_PATCH 链路预检**（oracle Q3 闸门）：03_raw 无 PNG 本体（仅 .import）；c4 先例（stex 替换）是否在本仓复现（build_mod → 重导入 → stex → pack） | 可行 → §1.2 路径 B 生效（TDL 就绪）；不可行/成本超限 → §1.1 路径 A（参数就绪）。**二选一，不双开**；双线参数均已给全，裁决只切路由不调值 | §1.1 + §1.2 完整参数 |
| 2 | **运行时生效贴图确认**：`BaseLevel.gd:365` 把 TileSet 0 号贴图换为 `tileset_hideout`（Levels.gd:270）；审计基于 `tileset_factory.png` | 路径 B 的重绘目标文件 = tessellated 实际生效贴图（factory 或 hideout；两文件同规格，TDL 复用）；fixer 确认后锁定 ASSET_PATCH target | §1.2 TDL 与 fixer 确认项 |
| 3 | **clear color 运行时锚点**：project.binary 不可 patch；`World.gd._ready` 或 `GameState._ready` 选安全插入点（fixer 核实 GameState 存在性） | 锚点确定 → §2.2 CODE_PATCH 生效；锚不到 → 跳过并声明"ColorRect 全覆盖兜底"（非阻塞降级） | §2.2 两候选 + 降级声明 |
| 4 | **`Interactable.tscn` 结构挂载点**：底衬 StyleBox 挂哪个容器（保持 anchor/margins 不动的无 diff 或最小 diff 方案） | 若 fixer 判定 `.tscn` 结构改动 preimage 风险高 → 底衬/五态全部改由 `Interactable.gd _draw` 程序绘制矩形（参数不变，仅实现路径） | §3.2/§4.3 双实现路径（tscn StyleBox 或 gd _draw）已注明 |
| 5 | **`Interactable.gd` 基类插桩 preimage**：CODE_PATCH 该基类 + compile manifest（子类依赖链覆盖，PHASE 1 P1 先例） | 若判定影响面大 → 分拆为 `Interactable.tscn` 内联绘制子节点（仍用基类已有函数，零新文件） | §4.1 备选已注明 |
| 6 | **OutlineShader 不用于 Interactable**（设计决策，fixer 确认即可）：共享文件（Mob/18+ 子场景/Pickup/3 Boss）且无 `enabled` uniform；改动会污染怪物视觉 | 不联动参数，仅确认"零改动 OutlineShader" | §4.1 论证已写 |
| 7 | **行尾/字节**：BaseLevel.tscn / World.tscn / Interactable.tscn / InGameText.tres / Portal.gd / BaseLevel.gd 行尾由 fixer 逐字节确认（PHASE 1 先例：GUI.tscn/MainTheme.tres 为 LF；本规格不预设）；preimage = 整文件 SHA + old_text 逐字节 | 转录准确性依赖此步 | §3/§4/§5 old_text 语义均给 |

---

## §8. 与 PHASE 1 已确立 token 的一致性说明

1. **全部颜色取 §五 或由 §五 直接推导**：本次新增折算（World Background `#0C1015`、Primary Text、Disabled Text、网格 family `#141C25/#1F2934/#1A222C/#161E27/#222D38`）均为 §五 灰蓝/暗蓝 family 内的推导，未引入任何新色相；Arcane `#79D98B` 沿用 PHASE 1 已折算浮点值（0.47451, 0.85098, 0.545098），单值两阶段复用的先例保持。
2. **圆角 4/6/8 上限**：本规格全部圆角 = 4（标签底衬 §3）；无 6/8 档需求。
3. **间距 token 4-8-12-16-24-32**：底衬 margin 用 8/4；网格 32/128 与 cell_size 对齐；无 13/19/27 类随机值。
4. **§二十九 性能**：全部改动 = 静态绘制/低频重绘（网格一次性、五态切换 update、Waypoint 2 次 sin/帧）；无 per-frame 全屏绘制、无 shader 新增、无后处理、无粒子新增。
5. **§三十五 好用 > 好看 > 炫技**：网格降权保可读；标签 Nearby 才出底衬、Hover 才出 Accent；物体 Accent 只在 Interactable/Hover；Waypoint 呼吸 ≤14% 振幅——每项都是"信息层级先行"，样式仅为层级服务。
6. **与 PHASE 1 v1-hd-cleanup 的衔接**：PHASE 1 改的 MainTheme/GUI/Tooltip/XP/ProgressBar 不在本规格触碰（2a 世界层，2b HUD 层所在）；PHASE 1 判死项（pixel snap）与推后项（字号档、相机 zoom、Selection 标签态）本规格均未越界——标签 Selected 态按任务仅 Normal/Nearby/Hover 三态，Selected 留给 PHASE 3 交互过。
7. **范围自检（勿扩）**：本规格不含——HUD（血球/Dock/小地图/按钮，2b）、Brazier 火把发光（A5）、玩家/NPC 贴图重制（PHASE 6）、相机 zoom（PHASE 6 决策）、tileset 之外的任何 ASSET_PATCH 新资产、任何新文件路径。