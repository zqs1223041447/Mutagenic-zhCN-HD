# PHASE 1 — HD Cleanup 设计规格（Design Spec）

> 记录：2026-08-17。作者：designer lane。只读产出，未修改任何游戏文件。
> 权威依据：`docs/requirements/HD_UI_REMASTER.md`（§五 色板 / §六 颜色规则 / §九 间距 / §十 圆角 / §十一 边框 / §十九 按钮 / §三十三 验收）、`docs/requirements/PHASE0_VISUAL_AUDIT.md`、`.slim/deepwork/hd-ui-remaster.md` §PHASE 1 门禁评审结论。
> 用途：fixer lane 按本规格直接转录为 mod.json（old_text/new_text 逐字节）。**不写 mod.json、不改布局、不改字号、不新增资产。**
> 行尾事实（已逐字节验证）：MainTheme.tres / GUI.tscn / TooltipBase.gd / Player.tscn 均为 **LF-only**；StatusBar.tscn 为 **CRLF-only**（本次不改动它）。

---

## 0. 本次用到的色板值（全部来自 HD_UI_REMASTER §五，或由 §五 直接推导）

| Token | Hex | Godot Color 8bit 浮点（0-1） |
|---|---|---|
| Surface 1 | `#121820` | `Color( 0.0705882, 0.0941176, 0.12549, 1 )` |
| Surface 2 | `#18212A` | `Color( 0.0941176, 0.129412, 0.164706, 1 )` |
| Elevated Surface | `#1D2731` | `Color( 0.113725, 0.152941, 0.192157, 1 )` |
| Background Deep | `#090C10` | `Color( 0.0352941, 0.0470588, 0.0627451, 1 )` |
| Normal Border | `#293642` | `Color( 0.160784, 0.211765, 0.258824, 1 )` |
| Highlight Border | `#405365` | `Color( 0.25098, 0.32549, 0.396078, 1 )` |
| Secondary Text | `#9DA9B5` | `Color( 0.615686, 0.662745, 0.709804, 1 )` |
| Arcane Accent（品牌绿） | `#79D98B` | `Color( 0.47451, 0.85098, 0.545098, 1 )` |

> 换算核对：`0x79=121/255=0.47451`、`0xD9=217/255=0.85098`、`0x8B=139/255=0.545098`；`0x12=18/255=0.0705882`、`0x20=32/255=0.12549`（勿误写 0.129412=0x21）。

---

## P1. TooltipBase 水平定位 bug 修复（oracle 范围第 1 项）

- **目标文件:行号**：`04_recovered/Scenes/Tooltips/TooltipBase.gd:17`
- **当前值（原样引用）**：
  ```
  centered_position.x += position_offset.y
  ```
  垂直分支（`centered_position.y > viewport_size.y / 2` 的 else）里污染了水平坐标：把 `position_offset.y`（垂直偏移）加进了 `.x`。对照 L13 的对称分支用的是 `.x += position_offset.x`。
- **新值**：`centered_position.x += position_offset.x`
- **old_text → new_text**（⚠ 该行缩进为 **12 个 TAB**，非空格；下方代码块内为真实 TAB，逐字节复制）：

  ```
  old_text:
  												centered_position.x += position_offset.y

  new_text:
  												centered_position.x += position_offset.x
  ```

  > 仅 L17 一行被替换；行尾 LF。`centered_position.x += position_offset.y` 全文件唯一（L13 是 `.x += position_offset.x`，不误匹配）。
- **影响面**：`TooltipBase.gd` 的全部子类——`SkillTooltip/SkillTooltip.gd`（L1 `extends TooltipBase`）与 `GeneTooltip/GeneTooltip.gd`（L1 `extends TooltipBase`）。即所有技能/基因 Tooltip 在"鼠标位于视口下半区"时的水平落点修正（此前被垂直偏移污染，tooltip 可能偏离光标水平位置）。
- **风险标注**：低。纯逻辑等价修复，不影响布局结构。**fixer 关键**：CODE_PATCH 只编译 manifest 声明的脚本——本 patch 后必须把 `TooltipBase.gd` 加入该 mod 的编译声明（若其子类已声明，确认依赖链覆盖），否则 .gde 不重编译、修复不生效。

---

## P2. XP 条 StyleBox 精修（oracle 范围第 2 项）

### P2a. fg（填充）StyleBox —— `GUI.tscn:19-25`

- **目标文件:行号**：`04_recovered/Scenes/GUI/GUI.tscn:19-25`（`[sub_resource type="StyleBoxFlat" id=1]`）
- **当前值（原样引用）**：
  ```
  [sub_resource type="StyleBoxFlat" id=1]
  bg_color = Color( 1, 1, 1, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0.8, 0.8, 0.8, 0 )
  ```
- **新值（设计参数）**：
  - `bg_color`：**Arcane Accent `#79D98B`**（品牌色，§五；审计 B3 原话"fg 品牌色"）
  - `border_color`：**Surface 1 `#121820`**（1px 深色收边，压制品牌绿的亮度，保持"精密"感）
  - 圆角：**4**（§十 Small Radius；12px 高条安全上限为 6，取 4 稳妥）
  - `border_width_*` 保持 1 不变
- **old_text → new_text**：

  ```
  old_text:
  [sub_resource type="StyleBoxFlat" id=1]
  bg_color = Color( 1, 1, 1, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0.8, 0.8, 0.8, 0 )

  new_text:
  [sub_resource type="StyleBoxFlat" id=1]
  bg_color = Color( 0.47451, 0.85098, 0.545098, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0.0705882, 0.0941176, 0.12549, 1 )
  corner_radius_top_left = 4
  corner_radius_top_right = 4
  corner_radius_bottom_right = 4
  corner_radius_bottom_left = 4
  ```

  > `[sub_resource type="StyleBoxFlat" id=1]` 在 GUI.tscn 内唯一（该 id 只被 MutationTierXP 的 `custom_styles/fg` 引用）。expected_occurrences = 1。

### P2b. bg（背景槽）StyleBox —— `GUI.tscn:27-33`

- **目标文件:行号**：`04_recovered/Scenes/GUI/GUI.tscn:27-33`（`[sub_resource type="StyleBoxFlat" id=2]`）
- **当前值（原样引用）**：
  ```
  [sub_resource type="StyleBoxFlat" id=2]
  bg_color = Color( 0.282353, 0.282353, 0.282353, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0, 0, 0, 1 )
  ```
- **新值（设计参数）**：
  - `bg_color`：**Surface 2 `#18212A`**（暗蓝灰槽，比九宫格灰面板深一档形成"凹槽"）
  - `border_color`：**Normal Border `#293642`**（§十一 普通边框低亮度灰蓝）
  - 圆角：**4**（与 fg 一致，保证填充时四角不外露）
  - `border_width_*` 保持 1 不变
- **old_text → new_text**：

  ```
  old_text:
  [sub_resource type="StyleBoxFlat" id=2]
  bg_color = Color( 0.282353, 0.282353, 0.282353, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0, 0, 0, 1 )

  new_text:
  [sub_resource type="StyleBoxFlat" id=2]
  bg_color = Color( 0.0941176, 0.129412, 0.164706, 1 )
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

  > `[sub_resource type="StyleBoxFlat" id=2]` 在 GUI.tscn 内唯一（只被 MutationTierXP 的 `custom_styles/bg` 引用）。expected_occurrences = 1。

### P2 共用说明

- **影响面**：仅 `GUI.tscn` 内 `MutationTierXP`（SkillBar/PanelContainer/VBoxContainer/VBoxContainer/MutationInfoContainer）一处。已核实 `GUI.gd:99-104 _update_mutation_xp()` 只写 `xp_bar.value`，**无任何样式覆盖**，内联 StyleBox 生效且不会被运行时改写。
- **硬约束遵守**：`rect_min_size = Vector2( 0, 12 )`（L210）**保持不动**（高度 12 不变）；`margin_*`（L206-209）不动；`custom_styles/fg|bg` 引用关系（L213-214）不动。
- **风险标注**：中低。① 12px 高 + 圆角 4 + fg 1px 边框 → 可视填充约 10px，视觉比原纯白条"细一格"，但属预期（精密感）；② 品牌绿 `#79D98B` 与玩家自身血条绿 `#25D21B`（Player.tscn:574 内联）同属绿色系——两者屏幕位置（底部 Dock vs 玩家头顶 24×4 微条）与尺寸层级（304×12 vs 屏上约 12×2px）分离，S5 抽查确认不混淆；若混淆，PHASE 2 可切 Warm Accent 或调玩家血条（范围外）。③ 与 Globals 全局默认 ProgressBar 无关（本条已内联覆盖）。

---

## P3. ProgressBar 全局 fg `#FF0000` → 中性色（oracle 范围第 3 项）

- **目标文件:行号**：`04_recovered/Themes/MainTheme.tres:69-76`（`[sub_resource type="StyleBoxFlat" id=2]`，被 `ProgressBar/styles/fg` 引用，见 L162）
- **当前值（原样引用）**：
  ```
  [sub_resource type="StyleBoxFlat" id=2]
  bg_color = Color( 1, 0, 0, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0, 0, 0, 1 )
  corner_detail = 1
  ```
- **新值（设计参数）**：
  - `bg_color`：**Secondary Text `#9DA9B5`**（中性灰蓝，§五"文字灰白"档；§六 普通结构用暗灰/灰蓝/文字灰白；可见但不刺眼，不抢任何语义色）
  - `border_width_*`/`border_color`/`corner_detail` 全部保持不动（1px 黑边 + corner_detail 1）——最小 diff，只换底色一行
- **old_text → new_text**：

  ```
  old_text:
  [sub_resource type="StyleBoxFlat" id=2]
  bg_color = Color( 1, 0, 0, 1 )

  new_text:
  [sub_resource type="StyleBoxFlat" id=2]
  bg_color = Color( 0.615686, 0.662745, 0.709804, 1 )
  ```

  > `Color( 1, 0, 0, 1 )` 在 MainTheme.tres 内唯一；`[sub_resource type="StyleBoxFlat" id=2]` 唯一。expected_occurrences = 1。
- **影响面（盘点复核结论）**：全仓仅 3 处 ProgressBar——
  | 实例 | fg 是否内联覆盖 | 受本次影响 |
  |---|---|---|
  | `GUI.tscn:205` MutationTierXP | 是（SubResource( 1 ) 纯白） | 否 |
  | `Player.tscn:574` Healthbar（玩家自身血条） | 是（SubResource( 4 ) 绿 `#25D21B` + SubResource( 3 ) 透明 bg） | 否 |
  | **`StatusBar.tscn:127` Healthbar** | **否**——仅有 `theme = ExtResource( 2 )`（MainTheme.tres），无 `custom_styles/fg` | **是（唯一受影响实例）** |
  
  StatusBar 是**怪物/敌人血条模板**：`Mob.tscn:98` 实例化（`margin_top = -30.0` 挂在怪物头顶上方），全部 18 个怪物/Boss 场景继承（AttackDog/Spider/Zombie/SkeletonWarrior/各 Boss 等）。`StatusBar.gd:23-40` 满血时 `modulate.a = 0` 隐藏、受伤时显示并同步 value。
- **风险标注**：中。怪物受伤时头顶血条从亮红 `#FF0000` 变中性灰蓝 `#9DA9B5`——**红色"敌人危险"语义暂时丢失**（由左下 Globe 生命球承担玩家自身 HP 语义；怪物血条语义待 PHASE 2 Vertical Slice 世界表现统一处理）。若 oracle S5 抽查判定不可接受，追加方案（**不在 PHASE 1 默认范围，待 oracle 裁决**）：`StatusBar.tscn:127` 增加 `custom_styles/fg = SubResource( N )` 内联生命红 `#C83E42`（0.784314, 0.243137, 0.258824），注意 StatusBar.tscn 是 **CRLF**。另：`ProgressBar/styles/bg = null`（L161）保持不动。

---

## P4. 按钮 pressed / disabled 差异化（oracle 范围第 4 项）

> oracle 裁决：StyleBoxTexture 无 color/modulate 属性 → 走 **StyleBoxFlat 变体**；Selected 态降级 PHASE 3 不做。normal/hover/focus 保持贴图（ninepatch_58 / ninepatch_58_focus）不动——本阶段只替换 pressed、disabled 两个槽。

### P4a. 新增 StyleBoxFlat `id=40`（pressed）

- **设计参数**：底色 **Elevated Surface `#1D2731`**（比 normal 贴图灰暗一个档 = "按下变暗"，§十九 允许"Surface 稍暗"）；边框 **Highlight Border `#405365`**（按下时边框提亮一个视觉层级，§十一）；圆角 **4**；**内容下移 1px**：`content_margin_top = 11` / `content_margin_bottom = 9`（normal 贴图 content margin = margin_* = 10；上增 1 下减 1 → 文字/图标中心下移 1px，§十九"Pressed 可以向下偏移 1 logical px"的 theme 层实现，无需引擎位移）。
- **插入位置**：`MainTheme.tres` 的 `[resource]` 行（L134）之前（即 L133 空行之后）。
- **old_text → new_text**：

  ```
  old_text:
  [resource]

  new_text:
  [sub_resource type="StyleBoxFlat" id=40]
  content_margin_left = 10.0
  content_margin_top = 11.0
  content_margin_right = 10.0
  content_margin_bottom = 9.0
  bg_color = Color( 0.113725, 0.152941, 0.192157, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0.25098, 0.32549, 0.396078, 1 )
  corner_radius_top_left = 4
  corner_radius_top_right = 4
  corner_radius_bottom_right = 4
  corner_radius_bottom_left = 4

  [sub_resource type="StyleBoxFlat" id=41]
  content_margin_left = 10.0
  content_margin_top = 10.0
  content_margin_right = 10.0
  content_margin_bottom = 10.0
  bg_color = Color( 0.0352941, 0.0470588, 0.0627451, 1 )
  border_width_left = 1
  border_width_top = 1
  border_width_right = 1
  border_width_bottom = 1
  border_color = Color( 0.160784, 0.211765, 0.258824, 1 )
  corner_radius_top_left = 4
  corner_radius_top_right = 4
  corner_radius_bottom_right = 4
  corner_radius_bottom_left = 4

  [resource]
  ```

  > 一个 patch 同时插入 pressed（id=40）与 disabled（id=41）两个块。`[resource]` 在 MainTheme.tres 内唯一。expected_occurrences = 1。

### P4b. 引用替换 —— `MainTheme.tres:141,145`

- **当前值（原样引用，L141 / L145）**：
  ```
  Button/styles/disabled = SubResource( 34 )
  Button/styles/pressed = SubResource( 34 )
  ```
- **新值**：
  ```
  Button/styles/disabled = SubResource( 41 )
  Button/styles/pressed = SubResource( 40 )
  ```
- **old_text → new_text**（两条独立替换，各自唯一）：

  ```
  old_text:
  Button/styles/disabled = SubResource( 34 )
  new_text:
  Button/styles/disabled = SubResource( 41 )

  old_text:
  Button/styles/pressed = SubResource( 34 )
  new_text:
  Button/styles/pressed = SubResource( 40 )
  ```

  > `Button/styles/normal = SubResource( 34 )`（L144）、`hover = SubResource( 37 )`（L143）、`focus = SubResource( 38 )`（L142）**均不动**。expected_occurrences 各 1。

### P4c. load_steps 同步（建议项）

- **目标文件:行号**：`MainTheme.tres:1`
- **当前值**：`[gd_resource type="Theme" load_steps=30 format=2]`（现 9 ext + 20 sub = 29 → 30）
- **新值**：`[gd_resource type="Theme" load_steps=32 format=2]`（新增 2 sub → 9 + 22 = 31 → 32）
- **old_text → new_text**：

  ```
  old_text:
  [gd_resource type="Theme" load_steps=30 format=2]

  new_text:
  [gd_resource type="Theme" load_steps=32 format=2]
  ```

  > 建议执行（保证 Godot 3 加载器无 load_steps 警告、GDRE 语义恢复干净）；若 fixer 验证判定非必需，可跳过并在报告中说明。

### P4 共用说明

- **影响面**：MainTheme.tres 是唯一全局主题（审计 B5：53 场景引用）。所有 Button 实例（底部 Dock 的 Shop/Equipment/Menu-Stats 等、各面板按钮）获得 pressed 视觉反馈（变暗 + 1px 下移）与 disabled 低对比态（暗底 + 暗边框，配合既有 `font_color_disabled = #5F5F5F`）。
- **风险标注**：中。① pressed/disabled 为纯色圆角块，normal/hover 仍为像素灰九宫格贴图 → 按下瞬间存在"贴图 ↔ 纯色块"的质感微差（PHASE 6 换九宫格贴图后统一；若 S5 判定跳动明显，可将 corner_radius 降为 0 或同步改 normal，需 oracle 追加）；② 按钮文字 pressed 色（L140 `#E0E0E0`）保持不变，底色变化足以区分；③ content_margin 只影响内容排版中心，不改控件 rect（布局零改动）。

---

## P5. 字体 outline 一致化（oracle 范围第 5 项）

- **盘点结论**：`outline_size = 2` 全仓仅 **1 处**（已全仓 grep 复核）：`GUI.tscn:15`（ContextLabel 的 28px DynamicFont `id=3`，space.ttf）。改动面极小 → **执行**。其余 outline 均为 1（MainTheme default_font 18px `L117`、GUI.tscn 64px `L37`、BuffDisplay/NotificationMessage 等），16px→18px 字号档推后 PHASE 4（字号=布局，PHASE 1 禁改）。
- **目标文件:行号**：`04_recovered/Scenes/GUI/GUI.tscn:15`
- **当前值（原样引用）**：
  ```
  outline_size = 2
  ```
- **新值**：
  ```
  outline_size = 1
  ```
- **old_text → new_text**：

  ```
  old_text:
  outline_size = 2

  new_text:
  outline_size = 1
  ```

  > `outline_size = 2` 在 GUI.tscn 内唯一（L37 是 `outline_size = 1`，不同文本不误匹配）。expected_occurrences = 1。
- **影响面**：`GUI.tscn` 内 `ContextDisplay/ContextContainer/ContextLabel`（怪物上下文名称，28px 空间体，L72-80 引用 SubResource( 3 )）。28px 描边 2→1 后与全局 1px 描边统一（审计 B9"outline 不一致"消除）。
- **风险标注**：低。1px 描边在 28px 字号上仍足以保证暗底可读（与 MainTheme 18px 用 1px 一致）；如 S5 发现 28px 暗底上描边不足，PHASE 2 可单独为该档提 outline_color 亮度（不属本阶段）。

---

## 需要 fixer 注意清单

1. **行尾字节**：MainTheme.tres / GUI.tscn / TooltipBase.gd 均为 **LF-only**（已逐字节验证，无 CRLF）。所有 old_text/new_text 用 LF、无尾随空白（目标行均已验证无尾随 WS）。**StatusBar.tscn 是 CRLF-only**（133 行）——本次不改它，但 P3 风险注记中"追加内联覆盖"若被 oracle 批准，必须按 CRLF 处理。
2. **P1 缩进**：TooltipBase.gd:17 前缀为 **12 个 TAB**（非空格），old_text 必须含 12 TAB，否则 preimage/occurrence 守卫失败。
3. **expected_occurrences 汇总**：
   - P1 `centered_position.x += position_offset.y` → 1
   - P2a `[sub_resource type="StyleBoxFlat" id=1]` 块（含 bg_color 白）→ 1
   - P2b `[sub_resource type="StyleBoxFlat" id=2]` 块（含 bg_color #484848）→ 1
   - P3 `[sub_resource type="StyleBoxFlat" id=2]` + `bg_color = Color( 1, 0, 0, 1 )` → 1（MainTheme 内）
   - P4 插入锚点 `[resource]` → 1；`Button/styles/disabled = SubResource( 34 )` → 1；`Button/styles/pressed = SubResource( 34 )` → 1；`load_steps=30` → 1
   - P5 `outline_size = 2` → 1（GUI.tscn 内）
4. **同文件多 patch 分组**（共享整文件 preimage）：**GUI.tscn** 含 P2a、P2b、P5 三个改动点（建议 3 个 old_text 或一个覆盖 L15+L19-33 的组合）；**MainTheme.tres** 含 P3、P4a、P4b×2、P4c 共 5 个改动点。两个文件各自独立 mod 分组或同 mod 多 patch，注意 patch 顺序不互相踩踏（P4a 的 new_text 含 `[resource]`，不会与 P4b 冲突——P4b 的 old_text 不含 `[resource]`）。
5. **StatusBar ExtResource( 2 ) 结论（oracle 缺口 A 关闭）**：`StatusBar.tscn:132 theme = ExtResource( 2 )` → MainTheme.tres；Healthbar（L127-133）**无 custom_styles/fg 覆盖** → 继承全局 `ProgressBar/styles/fg`。P3 全局改色**会**使全部怪物/Boss 血条（Mob.tscn:98 模板 + 18 子场景）从亮红变中性灰蓝，这是预期行为；怪物血条红色语义恢复待 PHASE 2/oracle 裁决（规格见 P3 风险注记）。
6. **Player.tscn:574 确认（oracle 缺口 A 关闭）**：玩家自身血条 `custom_styles/fg = SubResource( 4 )`（绿 #25D21B）+ `custom_styles/bg = SubResource( 3 )`（透明黑边），**已完全覆盖全局 fg，不受 P3 影响**——无需改动，无需 patch。
7. **CODE_PATCH 编译声明**：P1 修改 `TooltipBase.gd` 后，必须确保该脚本在本 mod 的 compile manifest 中（或其依赖链被覆盖），否则 .gde 不重编译、修复不生效。
8. **range 检查（自我声明，勿扩）**：本规格未包含——Selected 按钮态（PHASE 3）、16px→18px 字号（PHASE 4）、像素网格/相机 zoom/世界标签（PHASE 2）、pixel snap / default_clear_color（oracle 判死或推后）、任何 ASSET_PATCH。任何超出项需 oracle 追加裁决。
9. **S5 视觉抽查项**：① XP 条（品牌绿填充 + 暗槽 + 圆角 4，12px 高度不变）；② 按钮 pressed（变暗 + 1px 下移）与 disabled（低对比）在至少一个面板内的表现；③ 怪物受伤血条中性灰蓝的可读性与语义接受度；④ ContextLabel 28px 描边 1px 暗底可读性。候选 build 定位为"人工视觉抽查（S5），不晋升 baseline"。
