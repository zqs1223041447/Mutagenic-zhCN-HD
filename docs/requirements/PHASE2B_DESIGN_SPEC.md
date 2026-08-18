# PHASE 2b — HUD 层（Buttons / Zone-Minimap / Health Orb / Command Dock）设计规格（Design Spec）

> 记录：2026-08-18。作者：designer lane（des-A1，重试）。只读产出，未修改任何游戏文件、未写 mod.json。
> 权威依据：`docs/requirements/HD_UI_REMASTER.md`（§五 色板 / §六 颜色规则 / §九 间距 / §十 圆角 / §十一 边框 / §十七 生命球 / §十八 底部 HUD / §十九 按钮 / §二十一 右侧区域小地图 / §三十五 决策优先级）、`docs/requirements/PHASE0_VISUAL_AUDIT.md`（B1-B5 HUD 审计 + §E PHASE 1 范围）、`docs/requirements/PHASE2_DESIGN_SPEC.md`（2a 同系列格式与 token 折算先例）、`.slim/deepwork/hd-ui-remaster.md`（ora-2 Q4：2b 四批顺序；派发表 fix-A2 写域）。
> 用途：fixer lane（fix-A2）按本规格转录为 mod（`mods/w2b-*`）。**本规格不新增任何文件路径**（roundtrip 3744 铁律：所有改动落在既有文件内；禁止新建 .tscn/.tres/.gd/资产）。不修改玩法、碰撞、输入、相机 zoom、基础分辨率、字体字号档（PHASE 4）。不晋升 baseline。**c5-l33 继续排除**（独立轨已验证，oracle Q1 裁决）。
> 批次顺序（deepwork 2b 待办原文）：B1 Buttons → B2 Zone/Minimap → B3 Health Orb → B4 Bottom Command Dock，每批独立 candidate + 机器 gate + S5。

---

## 0. 本次用到的色板（全部来自 §五 token 或 PHASE 2a §0 已折算值；浮点 6 位风格同 PHASE 1/2a）

| Token | Hex | Godot Color 8bit 浮点（0-1） | 备注 |
|---|---|---|---|
| Background Deep | `#090C10` | `Color( 0.0352941, 0.0470588, 0.0627451, 1 )` | PHASE 1/2a 已用；本规格用于血球描边/内暗底/闪动后恢复 |
| Surface 1 | `#121820` | `Color( 0.0705882, 0.0941176, 0.12549, 1 )` | 本规格所有 HUD 容器统一表面（zone 面板/词缀面板/地图框/dock） |
| Surface 2 | `#18212A` | `Color( 0.0941176, 0.129412, 0.164706, 1 )` | 按钮 normal 底（比容器高一级） |
| Elevated Surface | `#1D2731` | `Color( 0.113725, 0.152941, 0.192157, 1 )` | 按钮 hover 底；PHASE 1 已用于 pressed |
| Normal Border | `#293642` | `Color( 0.160784, 0.211765, 0.258824, 1 )` | 全部容器/按钮常态边框 |
| Highlight Border | `#405365` | `Color( 0.25098, 0.32549, 0.396078, 1 )` | hover/focus 边框（§十一"提高约一个视觉层级"） |
| Primary Text | `#E4E9EF` | `Color( 0.894118, 0.913725, 0.937255, 1 )` | 按钮文字/主数字/区域名 |
| Secondary Text | `#9DA9B5` | `Color( 0.615686, 0.662745, 0.709804, 1 )` | 次要文字（Zone Level:/Kills: 等 caption） |
| Disabled Text | `#626D78` | `Color( 0.384314, 0.427451, 0.470588, 1 )` | 禁用（PHASE 1 已定 disabled 底/边框，本规格不重开） |
| Arcane Accent | `#79D98B` | `Color( 0.47451, 0.85098, 0.545098, 1 )` | hover 文字色；小地图玩家点 |
| Health 深 | `#8B1F24` | `Color( 0.545098, 0.121569, 0.141176, 1 )` | §五 Health 下限；血球液底 |
| Health 亮 | `#C83E42` | `Color( 0.784314, 0.243137, 0.258824, 1 )` | §五 Health 上限；血球液面 |
| 语义红（Completion No） | nerfed 现值 | `Color( 0.605469, 0.108795, 0.108795, 1 )` | `Colors.gd:12` nerfed；替换 GUI.tscn 内联纯红 `#FF0000`（语义不变，去纯红） |

> 折算核对：`#12=18/255=0.0705882`、`#18=24/255=0.0941176`、`#1D=29/255=0.113725`、`#29=41/255=0.160784`、`#40=64/255=0.25098`；`#8B=139/255=0.545098`、`#1F=31/255=0.121569`、`#24=36/255=0.141176`、`#C8=200/255=0.784314`、`#3E=62/255=0.243137`、`#42=66/255=0.258824`。
> 透明度惯例：HUD 容器 α **0.85**（少量半透明，§十八），dock α **0.92**；均低于 1 且不透明度递减到足以"半透但可读"。

---

## 1. 关键机制事实（已核对，fixer 转录前必须采信）

| # | 事实 | 证据 |
|---|---|---|
| M1 | **行尾分叉**：`MainTheme.tres`、`GUI.tscn`、`Globe.gd`、`TextureRect.gd`、`GUI.gd` 为 **LF**；**`Globe.tscn`（39 处 CRLF）、`Minimap.tscn`（56 处 CRLF）为 CRLF** | 实测字节扫描；PHASE 1 只验证过 MainTheme/GUI.tscn（LF），**本规格新增验证**。old_text 必须按目标文件行尾逐字节（含换行）复制 |
| M2 | 按钮现状（post-PHASE 1，即 B1 的 preimage 基准）：normal=`SubResource( 34 )`（ninepatch_58.png 贴图）、hover=`SubResource( 37 )`、focus=`SubResource( 38 )`（ninepatch_58_focus.png）、pressed=`SubResource( 40 )`（StyleBoxFlat，PHASE 1）、disabled=`SubResource( 41 )`（StyleBoxFlat，PHASE 1）；`load_steps=32`；文字色 normal `#E0E0E0`/focus/hover 绿 `Color(0.294118,0.65098,0.27451,1)`（= `Colors.buffed` 同值）/pressed `#E0E0E0`/disabled `#5F5F5F` | `MainTheme.tres:136-145` + `mods/v1-hd-cleanup/mod.json` P4a-P4c |
| M3 | `ninepatch_58.png` / `ninepatch_58_focus.png` 全仓仅 MainTheme.tres 引用（ext id=8/9，sub id=34/37/38）；B1 改完后成死引用，**可安全移除**（03_raw 资产仍在，roundtrip 3744 不受影响） | rg 实测 |
| M4 | 血球贴图 `globe_inner_dark_2.png`/`globe_overlay_dark_final.png` 仅 Globe.tscn 引用（其余只剩 .import）→ 移除 ext 引用安全；**移除后 ext id 不需要重编号**（剩余 id=2 ChivoMono、id=3 Globe.gd，引用不变），仅 `load_steps 6→4` | rg 实测 + Globe.tscn 全文 |
| M5 | `Globe.tscn` 仅被 GUI.tscn:331-334 实例化；`Globe.gd` 仅被 Globe.tscn 引用 → 血球几何/脚本改动零辐射 | rg 实测 |
| M6 | Zone 列（GUI.tscn:336-425）：`LevelInfoContainer` 是 **HBoxContainer**（单子 MarginContainer）；GUI.gd 以 `$LevelInfoContainer/MarginContainer/LevelInfo/...` 硬编码路径（L83-84/117/188-197）→ **节点改名/改层级会断路径**；HBox 内新增"背景 Panel"子节点会被当作 box 子项布局（非背景）→ 背景容器方案 = **仅改节点 type（HBox→Panel），不改名** | GUI.tscn + GUI.gd 全文 |
| M7 | Minimap（CanvasLayer）由 `BaseLevel.tscn:49` 实例化，GUI 由 World 实例化 → **两 CanvasLayer 层级不同，物理合一（reparent）需跨场景重构可见性逻辑** | Minimap.tscn:12-14 + GUI.tscn:41-42 |
| M8 | 右缘对齐现状：zone 列右缘 x=1280（anchor_right=1）；MinimapContainer 右缘 x=1280（anchor_right=1）；词缀 PanelContainer 右缘 x=**1258**（`margin_right=-22`，`Minimap.tscn:21`）→ 差 22px，需对齐 | 三处锚点计算 |
| M9 | 词缀面板 `ModList` margin 仅 right/bottom=10（左/上 0，不对称）；地图框内 ColorRect `Color(0,0,0,0.196078)`（`Minimap.tscn:56`）；地图 7px 内边距（`:43-46`）；玩家点 `Color.green`（`TextureRect.gd:30`） | Minimap.tscn 全文 |
| M10 | CompletionLabel 静态纯红 `Color( 1, 0, 0, 1 )`（GUI.tscn:400），运行时被 `Colors.buffed/nerfed` 覆盖（GUI.gd:188-192）→ 静态值替换为 nerfed 同值（去纯红，语义零变化） | GUI.tscn + GUI.gd + Colors.gd:10-13 |
| M11 | dock PanelContainer（GUI.tscn:144-149）无 custom_styles → 继承 MainTheme `PanelContainer/styles/panel = SubResource( 32 )`（ninepatch_panel，MainTheme.tres:53-63/153）。**id=32 同时被 PopupMenu（L160）与 TooltipPanel（L172）共用** → 全局改 id=32 会连带全游戏弹窗/Tooltip（超垂直切片范围），故 B4 走 **GUI.tscn 局部覆盖** | MainTheme.tres 全文 |
| M12 | GUI.tscn 现有 sub id：1（XP fg）、2（XP bg）、3（DynamicFont 28）、4（DynamicFont 64）→ 新增 StyleBoxFlat 用 **id=5（B2 zone 面板）、id=6（B4 dock）**，`load_steps 14→15→16`（B2→B4 顺序递增） | GUI.tscn:13-39 |

---

## 2. B1 —— 按钮系统补全（Buttons）

> 范围裁定：PHASE 1 已做 pressed/disabled（MainTheme id=40/41，**本批不重开**）；本批做 **normal/hover/focus 三槽 + 文字色**。Godot 3 Button 无 Selected 样式槽（oracle 已裁），Selected 态归 PHASE 3。过渡动画时长（hover 80-120ms 等，§十九）归 PHASE 3 Interaction Pass，本批静态。

### 2.0 现状与目标

| 项 | 值 |
|---|---|
| 现状 | normal/hover/focus = 三张像素九宫格贴图（ninepatch_58(_focus)）；hover/focus 文字同绿 `(0.294118,0.65098,0.27451)`；normal 文字 `#E0E0E0`；**贴图语言与 PHASE 1 的 Flat 态（pressed/disabled）混搭** |
| 目标 | 按钮五槽（normal/hover/pressed/focus/disabled）统一为 StyleBoxFlat 同 family：Surface2→Elevated 一档上移、边框 Normal→Highlight 一档上移、圆角 4、无布局跳动；hover 文字 Arcane（§六 绿=可交互） |

### 2.1 精确参数（MainTheme.tres，LF；preimage = post-PHASE 1 整文件 SHA）

**新增 3 个 sub_resource（插在 `[resource]` 之前，即 PHASE 1 id=41 块之后；`[resource]` 全文件唯一，occurrences=1）：**

| 槽 | id | bg_color | border 1px | corner_radius ×4 | content_margin L/T/R/B | 语义 |
|---|---|---|---|---|---|---|
| normal | **42** | Surface 2 `(0.0941176, 0.129412, 0.164706, 1)` | Normal Border `(0.160784, 0.211765, 0.258824, 1)` | 4 | 10/10/10/10 | 静息：比容器高一档的暗石板 |
| hover | **43** | Elevated Surface `(0.113725, 0.152941, 0.192157, 1)` | Highlight Border `(0.25098, 0.32549, 0.396078, 1)` | 4 | 10/10/10/10 | §十一 hover 提升一档；margin 与 normal 相同 → 无跳动 |
| focus | **44** | `Color( 1, 1, 1, 0 )`（透明） | Highlight Border `(0.25098, 0.32549, 0.396078, 1)` | 4 | 10/10/10/10 | 键盘焦点环（Godot 3 focus stylebox 叠加绘制在 normal 之上）；透明底不遮 hover |

> pressed（id=40，PHASE 1）margin 10/11/10/9 = 内容下移 1px（§十九 Pressed 位移），与 normal 10/10/10/10 衔接一致 ✓。

**槽位重接线（3 行 old_text，每行 occurrences=1，LF 逐字节）：**

| 行 | old_text | new_text |
|---|---|---|
| L144 | `Button/styles/normal = SubResource( 34 )` | `Button/styles/normal = SubResource( 42 )` |
| L143 | `Button/styles/hover = SubResource( 37 )` | `Button/styles/hover = SubResource( 43 )` |
| L142 | `Button/styles/focus = SubResource( 38 )` | `Button/styles/focus = SubResource( 44 )` |

**文字色（3 行，occurrences=1）：**

| 行 | old_text | new_text |
|---|---|---|
| L136 | `Button/colors/font_color = Color( 0.878431, 0.878431, 0.878431, 1 )` | `Button/colors/font_color = Color( 0.894118, 0.913725, 0.937255, 1 )`（Primary Text） |
| L138 | `Button/colors/font_color_focus = Color( 0.294118, 0.65098, 0.27451, 1 )` | `Button/colors/font_color_focus = Color( 0.894118, 0.913725, 0.937255, 1 )`（焦点由边框环表示，文字回归主色） |
| L139 | `Button/colors/font_color_hover = Color( 0.294118, 0.65098, 0.27451, 1 )` | `Button/colors/font_color_hover = Color( 0.47451, 0.85098, 0.545098, 1 )`（Arcane） |

**死引用清理（主路径，M3）：** 删除 2 行 ext（`[ext_resource path="res://sprites/gui/ninepatch_58.png" type="Texture" id=8]`、`...ninepatch_58_focus.png... id=9`）+ 3 个 sub 块（id=34、38、37 整块，MainTheme.tres:13-41）；`load_steps=32` → `load_steps=30`（9-2 ext + 22-3+3 sub + 1 = 30）。**降级路径（fixer 判定删除 preimage 风险高时）**：保留死条目不删，仅新增 42/43/44，`load_steps=32` → `load_steps=35`；参数不变。

### 2.2 影响 / 风险 / 降级

- 影响文件：仅 `Themes/MainTheme.tres`（LF；53 场景共享 → **全局视觉变更**，与 PHASE 1 P3 ProgressBar 全局先例一致）。
- 风险：中。① 全局按钮换肤：EscapeMenu/各 Popup 内按钮同批换新语言——S5 必须抽查弹窗按钮；② 贴图按钮（如 CosmeticButton 文字橙 `GUI.tscn:167` 为局部 custom_colors，不受影响 ✓）；③ focus 环在鼠标流下几乎不出现，属键盘导航增强，不回归。
- 降级路径：若 S5 判定"贴图 normal 可保留"，仅重接 hover/focus 两槽（参数不变，跳过 normal 槽与死引用清理）。

### 2.3 B1 gate 标准

- 机器 gate：resolve/apply（preimage 全 PASS）/compile（无脚本声明）/delta/pck checksum/exe_structure/**roundtrip 3744=3744**/boot 无 ALERT 无 fatal。
- GDRE semantic 断言（从最终 EXE 恢复 MainTheme.tres）：含 `Button/styles/normal = SubResource( 42 )`、`hover = SubResource( 43 )`、`focus = SubResource( 44 )`；sub 42 bg `(0.0941176, 0.129412, 0.164706, 1)`、43 bg `(0.113725, 0.152941, 0.192157, 1)` + Highlight 边框、44 透明底；hover 文字 `(0.47451, 0.85098, 0.545098, 1)`；`load_steps` 与实施路径一致（30 或 35）。
- S5 抽查（Hub 截图）：dock 三按钮 normal/hover/pressed/disabled 四态可辨且无内容跳动；EscapeMenu 按钮同语言；键盘 Tab 焦点环可见。

---

## 3. B2 —— Zone / Minimap 信息模块（三处散落视觉统一）

> **"合一"裁定（本规格正式裁决）：视觉统一 + 右缘对齐 + 容器语言统一，不做代码级整合。** 理由：Minimap（CanvasLayer，BaseLevel 实例化）与 GUI（CanvasLayer，World 实例化）层级不同，物理 reparent 需跨场景重构可见性逻辑并改写 GUI.gd/Minimap.gd 全部 `$` 路径（M6/M7）；roundtrip 铁律禁止新建场景文件；垂直切片阶段收益 < 风险。PHASE 5 全局推广时可再议是否真整合。**不新建任何节点之外的场景/脚本**。

### 3.0 现状与目标（三处）

| 处 | 现状 | 目标 |
|---|---|---|
| Zone 列（GUI.tscn:336-425） | 无任何容器，白字直落世界；CompletionLabel 静态纯红 | 统一 Panel 容器（Surface1 α0.85 + Normal Border + 圆角 4）；文字三级层次（区域名 Primary / caption Secondary / 数字 Primary）；去纯红 |
| 词缀面板（Minimap.tscn:16-30） | StyleBoxFlat 纯黑 α0.706、无边框无圆角、右缘 x=1258 | 同容器语言；右缘对齐 x=1280 |
| 地图框（Minimap.tscn:32-56） | ninepatch 面板 + 内 ColorRect 黑 α0.196 | 同容器语言（薄框，§21）；内底 Surface1 α0.85 提升白格对比 |

### 3.1 精确参数

**A. Zone 列容器（GUI.tscn，LF）**

1. **LevelInfoContainer 节点 type 改 HBoxContainer → PanelContainer**（L336 `[node name="LevelInfoContainer" type="HBoxContainer" ...]`）：节点名不变 → GUI.gd 全部 `$LevelInfoContainer/MarginContainer/...` 路径零影响（M6）。删除 `alignment = 2` 行（L343，单子容器无布局效果）；`theme = ExtResource( 3 )` 保留（custom_styles 局部覆盖优先）。
2. **新增 sub_resource id=5**（插在 `[resource]` 前；GUI.tscn 无 `[resource]` 段——**插在文件末尾最后一行 `[connection ...]` 之后**，fixer 按 preimage 选最小 diff 插入点，语义同"新增一个 StyleBoxFlat 定义"）：
   ```
   [sub_resource type="StyleBoxFlat" id=5]
   bg_color = Color( 0.0705882, 0.0941176, 0.12549, 0.85 )
   border_width_left = 1
   border_width_top = 1
   border_width_right = 1
   border_width_bottom = 1
   border_color = Color( 0.160784, 0.211765, 0.258824, 1 )
   corner_radius_top_left = 4
   corner_radius_top_right = 4
   corner_radius_bottom_right = 4
   corner_radius_bottom_left = 4
   ```
   （无 content_margin——内边距由 MarginContainer 承担。）
3. **LevelInfoContainer 节点加** `custom_styles/panel = SubResource( 5 )`；`load_steps=14` → `load_steps=15`。
4. **MarginContainer（L345-349）补齐对称边距**（声明式布局微调，≤16px）：`custom_constants/margin_left = 16`、`custom_constants/margin_bottom = 16`（现仅 right/top=16）。影响：VBox 内缩进对称，右对齐标签 x 不变。
5. **文字层次（全部 custom_colors/font_color 逐节点加，零布局）**：
   | 节点 | 位置 | 值 |
   |---|---|---|
   | NameLabel（区域名） | GUI.tscn:361-365 | Primary `(0.894118, 0.913725, 0.937255, 1)` |
   | "Zone Level:" | GUI.tscn:373-377 | Secondary `(0.615686, 0.662745, 0.709804, 1)` |
   | LevelLabel | GUI.tscn:379-383 | Primary |
   | "Completed:" | GUI.tscn:391-395 | Secondary |
   | CompletionLabel | GUI.tscn:396-401 | 静态 `Color( 1, 0, 0, 1 )` → nerfed `Color( 0.605469, 0.108795, 0.108795, 1 )`（M10；运行时 Colors.buffed/nerfed 覆盖逻辑不动） |
   | KillLabel | GUI.tscn:415-419 | Primary |
   | KillLabel2 " / 250" | GUI.tscn:421-425 | Secondary |

**B. 词缀面板（Minimap.tscn，CRLF！old_text 必须 CRLF 逐字节）**

1. **sub_resource id=1 重写**（L7-10，occurrences=1）：
   ```
   [sub_resource type="StyleBoxFlat" id=1]
   bg_color = Color( 0.0705882, 0.0941176, 0.12549, 0.85 )
   border_width_left = 1
   border_width_top = 1
   border_width_right = 1
   border_width_bottom = 1
   border_color = Color( 0.160784, 0.211765, 0.258824, 1 )
   corner_radius_top_left = 4
   corner_radius_top_right = 4
   corner_radius_bottom_right = 4
   corner_radius_bottom_left = 4
   expand_margin_left = 4.0
   expand_margin_right = 4.0
   ```
   （expand_margin 4/4 保留 = 布局零变化的视觉 padding。）
2. **右缘对齐**：`margin_right = -22.0`（L21）→ `margin_right = 0.0`（M8；面板右缘 1258→1280 与地图框/zone 列对齐；grow_horizontal=0 保持 → 向左生长，不影响内容宽度）。声明式布局微调：面板整体右移 22px。
3. **（S5 门控的可选微调，默认不做）**：ModList margin 10/10 不对称 → 8 全边（M9）。

**C. 地图框（Minimap.tscn，CRLF）**

1. **新增 sub_resource id=2**（薄框，同容器语言）：
   ```
   [sub_resource type="StyleBoxFlat" id=2]
   bg_color = Color( 0.0705882, 0.0941176, 0.12549, 0.85 )
   border_width_left = 1
   border_width_top = 1
   border_width_right = 1
   border_width_bottom = 1
   border_color = Color( 0.160784, 0.211765, 0.258824, 1 )
   corner_radius_top_left = 4
   corner_radius_top_right = 4
   corner_radius_bottom_right = 4
   corner_radius_bottom_left = 4
   ```
2. **MinimapContainer（L32-40）加** `custom_styles/panel = SubResource( 2 )`（覆盖 MainTheme ninepatch 默认）；`rect_min_size 206×206`、`rect_clip_content`、7px 内边距（L43-46）全不动。
3. **内 ColorRect（L50-56）**：`color = Color( 0, 0, 0, 0.196078 )` → `Color( 0.0705882, 0.0941176, 0.12549, 0.85 )`（M9；白色可行走格 α0.7 在新底上对比提升）。
4. **`load_steps=5` → `load_steps=6`**。

**D. 玩家点（TextureRect.gd，LF，CODE_PATCH）**

- L30 `draw_circle(rect_size / 2.0, 1, Color.green)` → `draw_circle(rect_size / 2.0, 1, Color(0.47451, 0.85098, 0.545098, 1))`（Arcane；occurrences=1）。
- compile manifest 声明 `Scenes/Minimap/TextureRect.gd` 重编译。

### 3.2 影响 / 风险 / 降级

- 影响文件：`GUI.tscn`（LF）、`Minimap.tscn`（CRLF）、`TextureRect.gd`（LF）。Zero 新路径。
- 风险：中。① `Minimap.tscn`/`Globe.tscn` 是本仓库首批 **CRLF 目标**（M1），old_text 逐字节含 CRLF，fixer 必须用字节级工具转录；② LevelInfoContainer type 变更（HBox→Panel）：单子容器布局等价，但 `alignment=2` 行删除需 preimage 精确；若 fixer 判定 type 变更风险高 → **降级 = 跳过容器（A1-A2 不做），仅做 A5 文字层次 + B/C 容器统一**（视觉一致性部分达成，zone 列仍无底衬，S5 记录为已知偏差）；③ CompletionLabel 静态色替换不影响运行时语义色。
- 玩法零影响：Minimap.gd 显隐逻辑、GUI.gd 全部 `$` 路径、ColorRect/TextureRect 节点名（含怪名 "TextureRect"）均不动。

### 3.3 B2 gate 标准

- 机器 gate：同 2.3（compile 含 TextureRect.gd）。
- GDRE semantic 断言：恢复 GUI.tscn 含 `type="PanelContainer"`（LevelInfoContainer）+ `custom_styles/panel = SubResource( 5 )` + id=5 bg `(0.0705882, 0.0941176, 0.12549, 0.85)`；恢复 Minimap.tscn 含 id=1/id=2 边框色 `(0.160784, 0.211765, 0.258824, 1)`、`margin_right = 0.0`、ColorRect 新色、`load_steps=6`；恢复 TextureRect.gd 含 `(0.47451, 0.85098, 0.545098, 1)`。
- S5 抽查（Hub 截图）：三容器同表面/边框/圆角；右缘三处对齐 x=1280；CompletionLabel Yes/No 语义色保留；词缀文字在 α0.85 底上可读；地图白格对比提升；玩家点 Arcane 绿。

---

## 4. B3 —— Health Orb 重设计（256px 纯红 → 160px Dark Arcane）

> 范围裁定：**程序化重绘**（零新资产）。Godot 3 无法 per-node 纹理 filter；256→160 对像素贴图做最近邻缩样 = 毛边。PHASE 6 才重绘 globe PNG（C 类资产登记在案）；本批把血球改成 `_draw` 程序绘制（圆环/渐变液/内阴影/高光/伤害脉冲），贴图引用移除（M4 安全）。

### 4.0 现状与目标

| 项 | 值 |
|---|---|
| 现状 | Globe.tscn（CRLF）：TextureProgress 256×256（anchor bottom，margin_top=-256/margin_right=256）、fill_mode=3、双 256×256 PNG（under/progress 纯红像素画）；数字 HBox 600px 宽 x∈[-174,426] 居中、24px ChivoMono "150 / 200" 压球心；Globe.gd update_progress 仅 2 行；零反馈 |
| 目标 | §十七：缩小 25-40%（256→**160** = -37.5% ✓）、深色金属外框 + 内暗环 + 径向渐变液（§五 Health `#8B1F24`→`#C83E42`）+ 内阴影 + 极轻高光；数字下移弱化但一眼可读；受伤 100-180ms 极弱脉冲（**禁屏幕闪红**） |

### 4.1 布局影响声明（任务要求显式声明）

- Globe 根（GUI.tscn:331-334 实例，anchor_top/bottom=1）占用区域 x∈[0,256] y∈[544,800] → **x∈[0,160] y∈[640,800]**（左下收窄 96×96 屏 px）。
- 无重叠风险：dock x∈[340,940]（M11），血球 x∈[0,160] 零交集 ✓；`mouse_filter=2`（GUI.tscn:334）无命中。
- `$Globe.visible` 开关（GUI.gd:97 `enable_health_globe`）与 `update_progress` 调用契约（GUI.gd:119-120）**签名不变** → GUI.gd 零改动。
- 数字行从"球心"移到"球下 1/3"（y 中心 720→763.5，即球心下方 43.5px）。

### 4.2 精确参数（Globe.tscn，CRLF！；Globe.gd，LF）

**Globe.tscn（RESOURCE_PATCH，old_text 全部 CRLF 逐字节）：**

1. `[gd_scene load_steps=6 format=2]` → `load_steps=4`；**删除 2 行 ext**（L3 `globe_inner_dark_2.png id=1`、L6 `globe_overlay_dark_final.png id=4`；剩余 id=2/id=3 引用不变，M4）。
2. 根节点（L12-13）加几何：`anchor_top = 1.0`、`anchor_bottom = 1.0`、`margin_top = -160.0`、`margin_right = 160.0`（160×160，左下锚定）。
3. TextureProgress（L15-24）：删除 `anchor_top/anchor_bottom/margin_top/margin_right` 4 行（回归 0,0,0,0 不可见值槽）；删除 `texture_under = ExtResource( 1 )`、`texture_progress = ExtResource( 4 )`；`step = 0.0`、`value = 80.0`、`fill_mode = 3` 保留（值槽驱动 `_draw` 液面；null 贴图零渲染、零报错）。
4. DynamicFont id=1（L8-10）加：`outline_size = 1`、`outline_color = Color( 0.0352941, 0.0470588, 0.0627451, 0.9 )`（Background Deep 90%，同 2a 标签描边惯例）。
5. 数字 HBox（L26-31）：`margin_left = -40.0`、`margin_top = -52.0`、`margin_right = 200.0`、`margin_bottom = -21.0`（240 宽、以 x=80 居中；y∈[108,139] 根坐标 = 球下 1/3）；`alignment = 1` 保留。
6. HealthLabel（L33-38）：`margin_left/margin_right` 清为 `0.0`（容器居中接管）；`margin_bottom = 29.0` 保留；加 `custom_colors/font_color = Color( 0.894118, 0.913725, 0.937255, 1 )`（Primary Text）；`text`/`align` 保留。

**Globe.gd（CODE_PATCH，LF；compile manifest 声明重编译；Godot 3 语法——`_draw` 直接定义、**禁 `super._draw()`**（2a 教训））：**

- 新增常量：`FRAME=Surface 2 (0.0941176,0.129412,0.164706,1)`、`INNER=Background Deep (0.0352941,0.0470588,0.0627451,1)`、`RIM=Normal Border (0.160784,0.211765,0.258824,1)`、`BLOOD_DEEP=(0.545098,0.121569,0.141176,1)`、`BLOOD_TOP=(0.784314,0.243137,0.258824,1)`、`SHADOW=Background Deep α0.30`、`HILITE=Primary α0.10`、`ARCANE` 不用于血球。
- `_draw()` 语义（圆心 c=(80,80)，全部常量，AA 开）：
  1. `draw_circle(c, 80, FRAME)` —— 金属暗底座
  2. `draw_circle(c, 74, INNER)` —— 内暗底
  3. `draw_arc(c, 77, 0, TAU, 48, 3.0, RIM, true)` —— 外主环
  4. `draw_arc(c, 70, 0, TAU, 40, 1.0, RIM α0.6, true)` —— 内细环
  5. 液面：`pct = $TextureProgress.value / 100.0`；pct>0.005 时画 **32 条水平条带**（弦宽 `2*sqrt(max(0, 66²-(cy-80)²))`，y∈[80-66, 80-66+132*pct]），条带色 = `BLOOD_DEEP.lerp(BLOOD_TOP, (cy-top)/h)` 逐条渐变（**径向渐变感，克制；禁 shader/禁贴图**）；条带法成本 ≈ 32 rect/帧，仅值变化时 `update()`，无 per-frame 重绘
  6. 内阴影（上缘，画在液面之后）：`draw_arc(c, 66, PI, TAU, 24, 4.0, SHADOW, true)`（上弧 4px 深色——液面与内环交界处给"凹槽感"）
  7. 高光：`draw_arc(c, 62, PI*1.12, PI*1.38, 12, 2.0, HILITE, true)`（左上短弧，极轻）
- 伤害脉冲（§十七 100-180ms 极弱，禁屏幕闪红）：
  - `var _flash := 0.0`、`var _last_amount := -1.0`
  - `_process(delta)`：`_flash>0` 时 `_flash -= delta`；`modulate = Color(1, 1-0.10*k, 1-0.14*k, 1)`（k=clamp(_flash/0.12,0,1)，**通道偏移 ≤14%，仅血球自身，非屏幕级**）；到 0 恢复 `Color(1,1,1,1)`
  - `update_progress(amount, amount_max)` 内：`if amount < _last_amount: _flash = 0.12`（120ms ∈ 100-180ms ✓）；`_last_amount = amount`；末尾加 `update()`（液面重绘）
- `update_progress` 现有两行（value + 文本拼接，含 `$HBoxContainer / HealthLabel.text` 原样空格写法）**保留不动**——old_text 锚点 = 该函数结尾 + 文件尾部追加。

### 4.3 影响 / 风险 / 降级

- 影响文件：`Globe.tscn`（CRLF）、`Globe.gd`（LF）。M5 零辐射。
- 风险：中。① 程序化重绘是本批最大视觉重写——条带渐变在 160px 圆内 32 条 = 5px/条，肉眼应平滑；若 S5 见色带，条数 32→64（参数化，单值）；② 液面在 pct≈1 时顶部被内阴影弧盖 4px——设计意图（凹槽），非 bug；③ 像素贴图 era 的"液位机械感"消失，数字 24px 保留在 α0.85 液面上，S5 验证可读性；④ Godot 3 `draw_arc` 无宽度小数支持——用 3.0/2.0/1.0 整数宽 ✓。
- 降级路径：若 fixer 判定 CRLF 大段重写 preimage 风险不可控 → **降级 = 保留贴图双 PNG（256 缩 160 + 运行时尺寸），仅做数字下移 + 描边 + 脉冲**（贴图语言待 PHASE 6 重绘；S5 记录为已知偏差）。
- 玩法零影响：数值/文本逻辑、`enable_health_globe`、GUI.gd 全部不变。

### 4.4 B3 gate 标准

- 机器 gate：同 2.3（compile 含 Globe.gd）。
- GDRE semantic 断言：恢复 Globe.tscn 含 `margin_top = -160.0`/`margin_right = 160.0`、无 `texture_under`/`texture_progress`、`load_steps=4`、HBox `margin_top = -52.0`；恢复 Globe.gd 含 `BLOOD_DEEP`/`BLOOD_TOP` 两常量浮点、`_flash = 0.12`、`draw_arc(c, 77, 0, TAU, 48, 3.0` 语义行。
- S5 抽查（Hub 截图）：160px 球比例正确；液面渐变无硬色带；受伤脉冲 ≤120ms 仅球身；数字靠下可读、无截断；与 dock 无重叠；`enable_health_globe` 关闭开关仍生效。

---

## 5. B4 —— Bottom Command Dock 重设计（最后一批）

> 范围裁定：**局部覆盖**（M11：MainTheme id=32 被 PopupMenu/TooltipPanel 共用，全局改 = 超垂直切片范围 → **MainTheme.tres:53-63 保持不动**，弹窗/Tooltip 归 PHASE 3/5）。Dock 容器在 GUI.tscn 局部加 `custom_styles/panel`。

### 5.0 现状与目标

| 项 | 值 |
|---|---|
| 现状 | GUI.tscn:144-149 PanelContainer（600×150，theme=MainTheme → ninepatch_panel 贴图灰框）；三块信息（技能行 45px / 突变 XP 行 25px / 掉落行 32px + 16 边距 + 8 分隔）同平面无层级 |
| 目标 | §十八 Compact Command Dock：更薄更暗、半透明（α0.92）、分区靠 VBox 分隔 + 表面层级、按钮统一层级（B1 自动生效）；**不重构节点树、不新增分隔线节点**（克制） |

### 5.1 精确参数（GUI.tscn，LF）

**V0（主路径，布局零改动）：**

1. **新增 sub_resource id=6**（插在 id=5 之后；B4 依赖 B2 → 此时文件已含 id=5，`load_steps=15`）：
   ```
   [sub_resource type="StyleBoxFlat" id=6]
   content_margin_left = 16.0
   content_margin_top = 16.0
   content_margin_right = 16.0
   content_margin_bottom = 16.0
   bg_color = Color( 0.0705882, 0.0941176, 0.12549, 0.92 )
   border_width_left = 1
   border_width_top = 1
   border_width_right = 1
   border_width_bottom = 1
   border_color = Color( 0.160784, 0.211765, 0.258824, 1 )
   corner_radius_top_left = 4
   corner_radius_top_right = 4
   corner_radius_bottom_right = 4
   corner_radius_bottom_left = 4
   ```
   （content_margin 16 = 与 ninepatch id=32 一致 → **内层内容零位移**；α0.92 半透明暗表面。）
2. **dock PanelContainer（L144-149）加** `custom_styles/panel = SubResource( 6 )`；`rect_min_size 600`、`mouse_filter=2` 不动；`load_steps=15` → `load_steps=16`。
3. 内层层级（**全部零布局，纯色**）：掉落行数字（BlueOrbs 等 5 Label，GUI.tscn:244-329）→ Primary Text；MutationTierLabel/MutationXP（L199-223）→ Primary；LootContainer 32px 像素 orb 图标（blue_orb 等）→ **PHASE 6 范围，不动**。

**V1（可选紧凑档，声明式布局微调，默认不做；S5 判定"不够薄"才启用，作为 B4 之后单独小 candidate）：**

| 改动 | old → new | 风险 |
|---|---|---|
| id=6 content_margin T/B | 16 → 12（四边同改，内容整体内收 4px） | 内层位移 4px；按钮 45px 行/ProgressBar 行/掉落行相对位置不变 |
| VBoxContainer separation（GUI.tscn:156） | 8 → 6 | 行距 -2px；三段分隔仍清晰 |
| 总高 | 150 → 140（-10px） | 无命中（mouse_filter=2）；与血球无重叠（M11 几何不变） |

> 显式风险声明：V1 是唯一含布局数值改动的档位，属"布局改动最大"批次内的受控收窄；**默认不启用**，待 S5 证据。

### 5.2 影响 / 风险 / 降级

- 影响文件：仅 `GUI.tscn`（LF）。局部覆盖 → 弹窗/Tooltip/MainTheme 零波及。
- 风险：低。① 九宫格贴图 → Flat：dock 圆角 4 在屏幕底部，视觉收边正常；② α0.92 半透明叠于世界之上——Hub 背景暗蓝（2a #0C1015）下对比充足，S5 验证；③ 若 S5 判定"Flat 无层次、需要 divider"→ 降级 = VBox separation 8→6 并用 HSeparator（新节点，声明式结构变更，列入 PHASE 3 不做本批）；④ V1 含布局数值，失败即回退 V0（参数就绪，零阻塞）。
- 玩法零影响：`_on_*Button_pressed` 连接（GUI.tscn:469-471）、GUI.gd 全部 `$` 路径、按钮 hitbox（45px 行不变）不动。

### 5.3 B4 gate 标准

- 机器 gate：同 2.3（无脚本编译声明）。
- GDRE semantic 断言：恢复 GUI.tscn 含 id=6 bg `(0.0705882, 0.0941176, 0.12549, 0.92)`、dock 节点 `custom_styles/panel = SubResource( 6 )`、`load_steps=16`；MainTheme.tres 恢复结果 **不含** id=32 变更（证明未越界）。
- S5 抽查：dock 视觉体积明显收窄（对比 v8.1 截图）、更暗半透明；三行分区可辨；掉落数字 Primary/图标照旧；1280×800 + 1600×1000 + 1920×1200（KEEP）三档无错位/截断；与血球/右缘模块无重叠。

---

## 6. 批次顺序、依赖链与 gate 矩阵（deepwork 2b 待办原文顺序）

| 批次 | mod 建议 | 依赖 | 目标文件（写域=fix-A2） | 机器 gate | GDRE 断言 | S5 |
|---|---|---|---|---|---|---|
| B1 Buttons | `w2b-1-buttons` | `["w2a-aggregate"]`（deepwork 派发表；与 2a 零文件交集，若 oracle 想精简可直连 `v1-hd-cleanup`，本规格不预设） | `Themes/MainTheme.tres` | 全项（见 2.3） | 3 槽重接 + 3 文字色 + load_steps | 四态 + 弹窗 + 焦点环 |
| B2 Zone/Minimap | `w2b-2-zone-minimap` | `["w2b-1-buttons"]` | `GUI.tscn`、`Minimap.tscn`、`TextureRect.gd` | 全项（compile 含 TextureRect.gd） | 见 3.3 | 三容器同语言 + 右缘 + 语义色 |
| B3 Health Orb | `w2b-3-health-orb` | `["w2b-2-zone-minimap"]` | `Globe.tscn`、`Globe.gd` | 全项（compile 含 Globe.gd） | 见 4.4 | 球比例/渐变/脉冲/开关 |
| B4 Command Dock | `w2b-4-command-dock` | `["w2b-3-health-orb"]` | `GUI.tscn`（再次，同文件链式） | 全项 | 见 5.3 | 收窄/分区/三分辨率 |

- 机器 gate 全项（PHASE 1 同款）：resolve（preimage 全 PASS）→ apply → compile（仅 manifest 声明脚本）→ delta 精确 → pck checksum → exe_structure → **roundtrip 3744=3744**（每批）→ boot 无 ALERT 无 fatal → GDRE semantic（上表断言）→ **不晋升 baseline**（S5 人工前不晋升，PHASE 1 定位维持）。
- 依赖链内 **c5-l33 确认不混入**（oracle Q1 裁决；独立轨补验已进行）。
- 每批通过后：归档 E2 → 进下一批；四批全过后做**聚合 candidate**（叠加链）供 HUD 层专项 S5（Hub 截图 BEFORE/AFTER）。

---

## 7. 需 fixer 联动确认项（参数依赖机制裁决）

| # | 联动项 | 裁决影响 | 本规格已备 |
|---|---|---|---|
| 1 | **CRLF 转录**（M1，新增机制事实）：Globe.tscn/Minimap.tscn 为 CRLF，MainTheme.tres/GUI.tscn/两 .gd 为 LF | old_text 逐字节含行尾；fixer 用字节级工具转录并回验 | 全部 old_text 语义 + 行尾标注 |
| 2 | **B1 死引用清理取舍**：删除 ext 8/9 + sub 34/37/38（load_steps 32→30）或保留（32→35） | fixer preimage 风险判断；两档参数一致，只切 load_steps 值 | 2.1 双档 |
| 3 | **LevelInfoContainer type 变更**（HBox→Panel，M6）：GUI.gd 路径零影响的理论需 fixer 复核（单子容器 + 无 container 布局依赖） | 可行 → B2 A 组全做；不可行 → 降级跳过容器只做文字层（3.2） | 3.1 A + 降级 |
| 4 | **GUI.tscn sub 插入点**：文件无 `[resource]` 段（2a 的 MainTheme 锚点不适用），StyleBoxFlat id=5/6 插文件尾 connection 之后 | fixer 选最小 diff 插入点；preimage 整文件 SHA 保障 | 3.1/5.1 语义完整 |
| 5 | **Globe.tscn ext 删除后 load_steps 核对**：6→4（删 2 ext、sub 仍 1） | 若 fixer 核对为其他值（Godot 版本差异）→ 以 Godot 3 实际校验为准，参数不变 | 4.2 语义 + 值 |
| 6 | **B2/B4 同文件（GUI.tscn）链式依赖**：B4 的 preimage 基准 = B2 应用后状态（含 id=5，load_steps=15） | 必须 B4 依赖 B2（已定序）；fixer 确认应用器按依赖链取 preimage | 6 依赖表 |
| 7 | **TextRect/Globe 编译依赖**：TextureRect.gd/Globe.gd 首次进 compile manifest（此前未声明） | compile 缓存机制按 PHASE 1 先例覆盖 | 3.1D/4.2 |

---

## 8. 与既有裁决一致性 & 冲突点声明

1. **顺序**：B1→B2→B3→B4 与 deepwork 2b 待办原文完全一致 ✓。
2. **不重开 pressed/disabled**：B1 只做 normal/hover/focus + 文字色；PHASE 1 id=40/41 原样 ✓。
3. **Selected 态**：归 PHASE 3（Godot 3 无 Selected 槽，oracle 裁决）✓ 本规格零越界。
4. **字号档**：B2 不加字号、B3 数字保持 24px（16→18 档归 PHASE 4）✓；B3 数字描边/位置属血球自身重设计，非全局字阶。
5. **StatusBar（8×8 图标）**：审计 B7 属像素轨（des-B1/PHASE 6），本规格不碰 ✓。
6. **"合一"裁定**：视觉统一 + 右缘对齐，非代码级整合（M7 + roundtrip 铁律）——本规格新裁决，与审计 B4 建议的"合并为统一模块"目标一致，实现路径不同；无冲突。
7. **潜在澄清点（无冲突，供主 agent 知悉）**：deepwork 派发表 fix-A2 写域 "MainTheme.tres（按钮态，PHASE1 后不重开）"——B1 触碰 normal/hover/focus 三槽属任务书"其余态未做"的明确授权，pressed/disabled 不重开；若主 agent 读作"按钮态整体不重开"，则 B1 缩为仅文字色 + hover/focus 槽（normal 槽降级，参数已备）。
8. **新机制事实（非冲突，登记）**：Globe.tscn/Minimap.tscn 为 CRLF（M1）；ninepatch_58 死引用可清（M3）；id=32 三消费者（M11）→ dock 走局部覆盖。
9. **PHASE 6 衔接**：血球 PNG / ninepatch_58 / orb 图标 / StatusBar 8×8 继续留在 HD Asset Replacement List（审计 §C）；本批程序化后血球 PNG 仅在 03_raw 存在，不再被引用。

---

## 9. 硬约束复述（fixer 转录红线）

1. **Godot 3.x 语法**：无 `super._draw()`（2a 教训）；HBoxContainer/VBoxContainer 不渲染 panel stylebox（2a 教训——本规格所有容器背景走 PanelContainer/Panel 或 `custom_styles`）；`draw_arc` 整数线宽；`TAU` 可用。
2. **行尾**：按 M1 表逐文件（Globe.tscn/Minimap.tscn CRLF，其余 LF）；`.md` 本文件 LF。
3. **roundtrip 3744 铁律**：不增删任何文件路径；不新建 .tscn/.tres/.gd/贴图；ASSET_PATCH 不启用（本批零资产改动）。
4. **preimage_sha256**：每 patch = 目标文件在依赖链应用后的**整文件 SHA**；old_text 逐字节（含行尾）；expected_occurrences 除注明外均为 1。
5. **c5-l33 排除**；**不晋升 baseline**；不 git add/commit（AGENTS.md §8）。
6. 不修改：玩法/碰撞/输入/相机 zoom/基础分辨率/字号档/`project.binary`。