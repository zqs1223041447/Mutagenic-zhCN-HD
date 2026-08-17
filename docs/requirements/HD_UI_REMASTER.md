# Mutagenic HD UI Remaster —— 总设计与实施任务（需求记录）

> **记录信息**
> - 来源：用户需求附件（2026-08-16 提交），原文记录，未改动内容。
> - 状态：RECORDED — PHASE 0（Visual Audit）进行中。
> - 追踪：deepwork 进度 `.slim/deepwork/hd-ui-remaster.md`；status.json gate `visual_ui_remaster`。
> - 定位：本文件是 Source of Truth（Git 管理），不可删除；后续阶段产物（audit/设计系统/资产清单）作为子文档追加到 `docs/requirements/`。

---

你现在同时担任以下角色：

1. **游戏视觉总监 / Art Director**
2. **高级 UI/UX 设计师**
3. **Godot 3.x 2D/UI 高级工程师**
4. **Mutagenic MOD 构建工程师**
5. **视觉质量 QA**

你的任务不是简单“调几个画质参数”，而是：

> 在保持 Mutagenic 原有玩法、信息结构、操作逻辑和暗色 ARPG 气质的前提下，把当前明显带有 prototype / pixel-art / programmer UI 感的界面，系统升级为一套高清、现代、克制、精致、响应迅速的 PC 独立 ARPG 视觉系统。

最终目标可以概括为：

> **Mutagenic HD UI Remaster**

不要把游戏做成手机 App，也不要机械模仿 Path of Exile、Diablo 或其他商业游戏。

我们需要建立属于 Mutagenic 自己的视觉语言：

**Dark Arcane Tactical UI**

关键词：

* 暗色
* 清晰
* 精密
* 克制
* 冷峻
* 微弱神秘感
* 信息密集但不拥挤
* 平滑而非像素化
* 快速而非花哨的交互反馈
* 少量发光而非满屏 Bloom
* 高完成度 PC 游戏，而不是网页 UI

---

# 一、项目现状

游戏：Mutagenic

类型：

* 类 Path of Exile 玩法
* 2D
* Godot 3.x
* GLES3

当前工程不是普通源码项目，而是一个确定性的汉化/MOD 构建系统：

原始 EXE
→ 提取 PCK
→ 反编译恢复源码
→ 声明式 MOD
→ 编译/加密
→ 打包 PCK
→ 从原始 EXE 新鲜嵌入
→ Candidate Build
→ 自动与人工验证

MOD 主要通过：

* CODE_PATCH
* VALUE_PATCH
* RESOURCE_PATCH
* ASSET_PATCH
* TEXT_PATCH

完成。

必须继续尊重现有 deterministic build 流程。

不要为了视觉修改而绕过 MOD 系统直接制造不可重复的手工文件。

---

# 二、当前已知技术状态

目前已经完成：

* 中文核心可玩版本
* 全量 Help 系统
* CJK 向量字体
* Noto Sans SC / DengXian
* 保留字体 hint
* `use_filter=false`
* Stretch Mode 已改为 `STRETCH_MODE_2D`
* Aspect 使用 `KEEP`
* 基础逻辑分辨率 1280×800
* 项目存在 `rendering/2d/snapping/use_gpu_pixel_snap`

现有资源包中位图资源极少。

绝大多数 UI / 世界视觉元素来自：

* CanvasItem
* Control
* GDScript `_draw()`
* draw_line
* draw_rect
* draw_polygon
* draw_circle
* Line2D
* Label
* Font
* Godot 2D 原生绘制系统

因此：

**本项目优先走“程序化高清重制”，而不是 AI 图片放大。**

---

# 三、当前截图的视觉问题

以提供的当前游戏截图为视觉基线。

必须首先承认当前界面的问题主要不是“清晰度”，而是以下因素组合造成的。

## 1. 世界画面像调试界面

当前游戏世界表现为：

* 大面积纯黑
* 强烈规则网格
* 世界层与 HUD 层缺乏视觉分离
* 场景缺少深度
* 物体缺少落地感
* 互动对象像直接放在开发网格上

网格目前承担了太多视觉权重。

目标：

让网格成为辅助空间感的背景，而不是画面的主体。

---

## 2. 世界文字缺少 UI 容器

当前：

“仓库转移”

“外观装扮”

“物品与词缀加工”

“装备”

等文字直接浮在世界里。

这容易产生：

* debug label 感
* 信息漂浮感
* 视觉层级混乱

需要建立统一的 World Label / Interaction Label 系统。

普通情况下标签保持克制。

当玩家靠近、Hover 或可交互时再加强。

---

## 3. 左下血球视觉权重严重过大

当前生命球：

* 尺寸过大
* 大面积纯红
* 高光方式偏旧
* 与其他 HUD 没有形成一套框架
* 100/100 直接压在球中央
* 占据极大的视觉注意力

不要完全取消生命球。

生命球是很适合 ARPG 的视觉识别元素。

但需要重新设计。

目标：

**保留“生命宝珠”的身份，但缩小、精炼、框架化。**

建议视觉方向：

* 大小明显缩小
* 深色金属/暗灰外框
* 内部红色液体
* 柔和径向渐变
* 很弱的内阴影
* 非常轻的边缘高光
* 避免巨大白色光斑
* 数字清晰但不要抢眼
* 生命变化时提供非常轻微动态反馈

不要设计成夸张 MMORPG 血球。

---

## 4. 底部 HUD 像一个灰色调试框

当前底部角色栏问题：

* 大块纯灰矩形
* 边框僵硬
* 控件间距不统一
* 图标、数字、按钮没有统一层级
* 信息全部堆在同一个视觉平面
* “装备”“菜单/属性”等按钮非常像默认 UI

需要重做为：

**Compact Bottom Command Dock**

特征：

* 更薄
* 更紧凑
* 更暗
* 分区明确
* 少量半透明
* 边框克制
* 有非常轻的层次
* 重要数字突出
* 次要文字弱化

不要制造巨大的底部 MMORPG Action Bar。

---

## 5. 右侧地图/区域信息缺少统一设计

当前右侧：

* 区域名称
* 等级
* 击杀数
* 地图方框
* 区域词缀

分别散落。

应该统一成为一个：

**Zone / Minimap Information Module**

结构建议：

区域名称
区域等级 · 击杀进度

[小地图]

区域词缀 / 当前效果

整体使用同一视觉容器。

---

## 6. 世界物体和 UI 高清程度不统一

中文字体已经明显比世界小图标清晰。

因此现在形成：

> 高清文字 + 像素物件 + 简单程序 UI

三套不同年代的视觉语言。

必须审计玩家、NPC、工作台、火焰、技能图标等元素到底如何生成。

如果是：

### 程序绘制

直接升级绘图方式。

如果是：

### Vector / Polygon

重新调整 AA、线宽、形状和颜色。

如果是：

### 真正的低分辨率 Sprite

不要简单 Bilinear 放大。

不要假装能够通过 AA 让低分辨率 Sprite 变成现代美术。

必须：

1. 标记资产来源；
2. 判断是否可以重新制作；
3. 给出 replacement asset 清单；
4. 在没有新素材前，通过阴影、选择圈、光晕、背景层降低违和感。

---

# 四、总体视觉方向

设计语言：

## Dark Arcane Tactical

不是：

* 纯黑 + 纯灰
* 高饱和 Neon
* 手机 App
* Material Design
* Cyberpunk UI
* 复杂哥特式雕花
* 大量金色 POE 模仿
* 满屏 Bloom

而是：

**低饱和暗色结构 + 清晰字体 + 少量魔法色彩 + 精确的间距 + 微弱光效。**

---

# 五、全局颜色系统

不要在代码中到处散落随机颜色。

建立统一 Design Tokens。

推荐基础色方向：

Background Deep
`#090C10`

World Background
`#0C1015`

Surface 1
`#121820`

Surface 2
`#18212A`

Elevated Surface
`#1D2731`

Normal Border
`#293642`

Highlight Border
`#405365`

Primary Text
`#E4E9EF`

Secondary Text
`#9DA9B5`

Disabled Text
`#626D78`

Arcane Accent
柔和青绿/翠绿色，不要荧光绿。

建议约：

`#79D98B`

Warm Interaction Accent：

`#D99A4E`

Health：

深红到亮红的有限范围。

不要纯 `#FF0000`。

例如：

`#8B1F24`
→
`#C83E42`

Mana / Arcane：

如果游戏存在对应资源，再建立独立颜色。

---

# 六、颜色使用规则

一个界面不允许同时存在十几个高饱和颜色。

高饱和颜色仅用于：

* 当前选中
* 可交互
* 危险
* 元素状态
* 稀有度
* 生命
* 技能效果

普通结构：

全部使用暗灰、灰蓝和文字灰白。

目标：

**让颜色本身代表意义。**

---

# 七、字体系统

继续优先使用当前已经完成的 CJK 向量字体。

不要退回 Bitmap Font。

建立统一 Typography Hierarchy。

至少分为：

## Display / Zone Title

用于区域名称、重大提示。

## Heading

用于面板标题。

## Body

普通说明。

## Secondary

次要说明。

## Numbers

血量、伤害、经验、计数。

## Caption

快捷键、辅助文字。

不要所有文字使用相同：

* 字号
* 字重
* 亮度

建议基础字号按 1280×800 逻辑坐标设计。

不要为了“高清”单纯把所有字放大。

需要实际检查：

* 中文可读性
* 行间距
* 左右 padding
* 数字对齐
* 标题和正文间距

---

# 八、字体渲染实验

建立 A/B 测试。

测试：

* 当前 Hinting
* LIGHT Hinting
* NONE Hinting

检查字体 AA。

检查 DynamicFont oversampling。

目标：

文字应：

* 清晰
* 稳定
* 平滑
* 不明显像素对齐
* 不发糊

不要自动把 `use_filter=true` 当作万能解决方案。

---

# 九、空间设计系统

建立统一 spacing token。

建议：

4
8
12
16
24
32

所有界面 padding、控件间距尽量来自这些值。

禁止出现大量：

13 px
19 px
27 px
31 px

这样的随机间距。

现代感很大程度来自：

**一致性。**

---

# 十、圆角规则

不要把游戏做成手机 App。

圆角必须克制。

建议：

Small Radius：4

Medium Radius：6

Large Radius：8

只有大型特殊卡片才允许更大。

按钮不要做成巨大胶囊。

---

# 十一、边框系统

普通边框：

低亮度灰蓝。

Hover：

提高约一个视觉层级。

Selected：

使用 Accent。

Rare / Special：

允许使用对应语义颜色。

禁止：

所有按钮都有亮白边框。

---

# 十二、阴影系统

阴影只承担“层级”。

不要做明显黑色外发光。

建议：

Panel Shadow：

小范围、低透明度。

Popup / Tooltip：

比普通 Panel 稍明显。

World Object：

使用微弱 contact shadow，让物体真正“站在地面上”。

---

# 十三、网格重设计

当前网格过于醒目。

需要：

* 显著降低 Alpha
* 减弱线宽
* 减少对比
* 保持空间导航作用

可以考虑：

Minor Grid
非常弱。

Major Grid
每若干格稍微增强。

禁止：

让网格比世界物件更加醒目。

如果技术简单，可以增加：

距离玩家越远，网格越弱。

但不要为了这一点引入昂贵 Shader。

---

# 十四、世界互动对象系统

仓库、工作台、职业 NPC、升级点等需要统一视觉。

每个对象至少考虑：

Normal
Nearby
Hover
Interactable
Disabled

Normal：

不抢眼。

Nearby：

标签可读性提高。

Hover：

边缘轻微亮起。

Interactable：

小范围 Accent 提示。

不要：

整个对象突然高亮成白色。

可以增加：

* 非常轻的 ground shadow
* 选择圈
* 小范围 halo
* interaction marker

---

# 十五、世界名称标签

现在世界名称只是白字。

改成统一 World Label。

建议：

Normal：

仅文字，透明度适中。

Nearby：

增加极轻的半透明底。

Hover：

Accent underline 或小边框。

Selected：

进一步提升。

标签不要占据大量空间。

不要给每一个物体套一个巨大 UI 卡片。

---

# 十六、中央绿色节点/方向装置

当前中央绿色十字节点是画面中很重要的元素。

不要简单保留为高饱和绿色十字。

重新设计为：

**Arcane Waypoint / Navigation Node**

特征：

* 圆形结构
* 内部精确几何线条
* AA
* 柔和 Arcane Green
* 非常轻的 Glow
* 缓慢呼吸
* 激活时稍亮
* 不激活时低亮度

动画应该非常慢且克制。

---

# 十七、生命球重设计

保留生命球。

但：

当前体积缩小约 25%～40%。

实际尺寸根据布局决定。

不要死守固定百分比。

生命球结构：

Outer Frame
Inner Dark Ring
Liquid
Subtle Inner Shadow
Very Soft Highlight

数值不要巨大压在正中央。

可考虑：

100 / 100

放在较靠下区域。

或者：

100

主数字

100 MAX

弱化。

必须保证一眼可读。

生命下降：

液体下降或色彩变化。

受到伤害：

允许 100～180ms 极弱反馈。

禁止：

明显屏幕闪红。

---

# 十八、底部 HUD 重设计

目标：

**Compact Command Dock**

当前大灰色框需要明显缩减视觉体积。

推荐结构：

左：

等级 / 职业 / XP

中：

核心资源 / 快捷栏

右：

装备
属性/菜单

不同信息块之间通过：

spacing
divider
surface level

区分。

不要每一个区域都有独立大边框。

---

# 十九、按钮系统

建立统一按钮状态：

Normal

Hover

Pressed

Selected

Disabled

Focused

交互节奏：

Hover：

80～120ms

Pressed：

50～80ms

Release：

80～120ms

Panel Enter：

120～180ms

Tooltip：

约 100～150ms

不要大量使用：

Bounce
Elastic
Overshoot

这是 ARPG，不是卡通手游。

Pressed 可以：

* 向下偏移 1 logical px
* Scale 0.98～0.99
* Surface 稍暗

不要使用夸张缩放。

---

# 二十、Tooltip 系统

所有 Tooltip 应统一：

* Surface
* Border
* Padding
* Title
* Description
* Stat rows
* Modifier colors

出现：

Fade + 轻微位移。

不要：

瞬间闪现。

也不要：

慢慢飘出来。

目标：

**快，但不生硬。**

---

# 二十一、右侧区域 / 小地图

将当前散落内容统一。

建议：

Zone Name

Level · Kill Progress

[Map]

Zone Modifier

整个模块：

* 右上 Anchor
* 半透明 dark surface
* 细边框
* 统一 padding
* 清晰层级

地图自身不需要巨大边框。

地图 frame 应尽量薄。

---

# 二十二、Player / NPC / Workbench 像素问题

必须调查实际来源。

不要根据截图猜。

逐个找到：

* 玩家
* NPC
* 火把
* 工作台
* 技能 Icon
* 装备 Icon
* 中央节点

对应的：

Script
Node
Texture
Resource
Draw Function

形成一份 Visual Asset Audit。

标记为：

A. Procedural

B. Vector-like

C. Texture

D. Unknown

如果 C 类确实是低分辨率纹理：

单独列出需要未来重新制作的资产。

不要偷偷用滤镜假装已经“高清重制”。

---

# 二十三、Godot 3 实现优先级

优先使用原生能力：

## Control Theme

统一：

* Button
* Panel
* Label
* Popup
* Tooltip

## StyleBoxFlat

用于：

* Surface
* Border
* Radius
* Shadow
* AA

## CanvasItem `_draw()`

继续用于：

* 世界几何
* Grid
* 圆
* 节点
* 线条

但必须检查 AA。

## Line2D

需要检查：

* antialiased
* round joint
* round cap
* width

## Tween

用于所有 micro interaction。

## CanvasItem Shader

仅用于必要效果：

* Health orb
* Subtle glow
* 少量特殊节点

不要一开始建立复杂的全屏 Post Processing。

---

# 二十四、抗锯齿升级

全文扫描：

`draw_line`

`draw_polyline`

`draw_polyline_colors`

`draw_polygon`

`draw_colored_polygon`

`draw_rect`

`draw_circle`

`Line2D`

检查所有视觉上重要的线条。

可以开启 AA 的地方：

优先尝试开启。

检查：

* 边缘是否正常
* Alpha 是否出现伪影
* 性能
* GLES3 行为

不要机械地全部替换。

需要按最终画面判断。

---

# 二十五、Pixel Snap

对：

`rendering/2d/snapping/use_gpu_pixel_snap`

建立明确的 A/B 实验。

优先测试：

OFF。

但不要同时修改十个其他 rendering setting。

GUI pixel snapping 与 GPU pixel snap 分开考虑。

---

# 二十六、不要现在修改基础分辨率

目前：

1280×800
Stretch Mode 2D
KEEP

在第一阶段全部保留。

不要通过：

1280×800 → 1920×1200

假装进行“高清化”。

视觉现代化首先通过：

AA
Typography
Spacing
Surface
Color
Interaction
Shader
Layout

解决。

只有后续有明确证据证明基础坐标系统成为限制，才讨论 base resolution。

---

# 二十七、布局原则

不要现在把整个游戏 UI 全部重写成 Container。

优先：

保留现有布局逻辑。

逐步建立：

Anchor
Margin
Safe Area

避免：

一次性大规模重构造成 UI 错位。

世界 HUD 与屏幕 HUD 要区分。

底部 HUD：

Bottom Anchor。

小地图：

Top Right Anchor。

生命：

Bottom Left Anchor。

中央提示：

Center / World Space。

---

# 二十八、1280×800 是设计基准，不是最终屏幕尺寸

视觉验证至少覆盖：

1280×800

1600×1000

1920×1200

2560×1600

1920×1080 + KEEP

重点检查：

* Chinese text clipping
* HUD anchoring
* 非整数缩放
* Tooltip
* Border
* Line AA
* Font
* Hitbox

---

# 二十九、性能原则

这是 Godot 3 GLES3 2D 游戏。

不要为了“高级感”：

* 每个控件一个 Shader
* 每个对象一个大 Blur
* 全屏多 Pass
* 大量实时模糊
* 大量粒子
* 大范围 Bloom

视觉应该来自：

设计本身。

Shader 是调味，不是主体。

---

# 三十、实施策略

禁止一次性修改全游戏。

按照以下阶段执行。

---

## PHASE 0 —— VISUAL AUDIT

先定位当前截图中的每一个主要视觉元素由什么代码/资源产生。

至少包括：

* World Background
* Grid
* Player
* NPC
* Workbench
* Torch
* Waypoint
* World Labels
* Health Orb
* Bottom HUD
* XP Bar
* Buttons
* Minimap
* Zone Text
* Modifier Text
* Skill / Item Icons

输出：

Visual Element
Node / Script
Rendering Method
Risk
Recommended Upgrade

但是：

**不要做完 Audit 就停止。**

随后继续实施。

---

# PHASE 1 —— HD CLEANUP

这一阶段禁止改变布局结构。

只处理：

* AA
* Pixel Snap
* Line quality
* Font rendering
* Grid contrast
* Border quality
* 基础颜色

目标：

> 保持原版布局，但明显消除 prototype / pixelated 感。

完成后生成第一个 Candidate。

---

# PHASE 2 —— HUB VERTICAL SLICE

以当前截图对应的这个 Hub / 城镇界面作为唯一完整样板。

不要马上改所有游戏界面。

重做：

* World background
* Grid
* Object presentation
* World labels
* Health Orb
* Bottom HUD
* Buttons
* Minimap
* Zone module

这一个场景必须真正达到：

**“现代独立游戏完成度”。**

只有样板成功后才能全局推广。

---

# PHASE 3 —— INTERACTION PASS

加入：

* Hover
* Press
* Focus
* Selected
* Tooltip transition
* Panel transition
* Waypoint breathing
* Object highlight
* Health feedback

目标：

不是让静态截图更炫。

而是：

**让鼠标操作明显更趁手。**

---

# PHASE 4 —— DESIGN SYSTEM

把 Vertical Slice 中验证成功的规则整理为统一 Design System。

建立集中式：

Colors
Typography
Spacing
Radius
Border
Shadow
Animation Timing

不要复制粘贴几十份颜色。

如果现有工程结构允许：

创建集中配置。

如果 deterministic MOD 系统不适合新增公共脚本：

选择最符合现有构建体系的等价实现。

---

# PHASE 5 —— GLOBAL ROLLOUT

逐步扩展到：

Inventory

Equipment

Skills

Help

Options

Crafting

Tooltips

Character

其他 UI。

每一批独立 Candidate。

禁止“一次性全部重做”。

---

# PHASE 6 —— ART ASSET PASS

只有完成程序 UI 高清化后，再判断：

哪些元素仍然因为低分辨率美术而显得像素化。

输出 Asset Replacement List。

例如：

Player

NPC

Workbench

Skill Icons

Equipment Icons

特殊环境对象

然后再决定是否：

* 人工绘制
* AI 生成后人工处理
* Vector 重绘
* 新 Sprite
* 新 Shader 图形

不要在没有完成 UI Design System 的情况下先生成几百张 AI 图片。

---

# 三十一、不要做的事情

禁止：

1. 升级 Godot 4。
2. 为了高清修改所有逻辑分辨率。
3. 大规模加入 ReShade 当主要方案。
4. 用全屏 Bloom 掩盖设计问题。
5. 把所有东西做成圆角卡片。
6. 把 UI 做成手机 App。
7. 模仿 POE 金属雕花 UI。
8. 每个元素都加入 Glow。
9. 每个 Hover 都做弹跳。
10. 随机使用几十种颜色。
11. 大规模破坏原有节点树。
12. 修改玩法逻辑。
13. 修改碰撞、移动速度、伤害逻辑。
14. 改变用户已经习惯的核心快捷键。
15. 为视觉而破坏 deterministic build。

---

# 三十二、MOD 工程约束

所有修改必须优先通过现有声明式 MOD 系统实现。

记录：

修改来源
目标文件
Patch 类型
修改目的

Candidate Build 需要继续通过现有流程。

至少不得破坏：

* PCK 构建
* 原 EXE fresh embed
* Boot
* 资源路径 roundtrip
* GDRE 语义恢复
* 中文文本
* 字体
* Help 系统

已有的结构 roundtrip 验证涉及约 3744 路径。

视觉升级不得绕过这些验证。

---

# 三十三、视觉验收标准

不是：

“代码运行了。”

而是：

**实际画面达到要求。**

每轮必须回答：

### 清晰度

线条是否明显减少锯齿？

字体是否稳定？

### 层级

哪里最重要是否一眼可见？

### 一致性

按钮、Panel、Tooltip 是否属于同一个游戏？

### 空间

是否仍有 prototype grid 感？

### 操作

Hover / Click 是否更有反馈？

### 克制

是否出现过度 Glow、Blur、Gradient？

### 中文

中文是否：

* 不截断
* 不挤压
* 不错位
* 行距合理

---

# 三十四、视觉比较

如果环境允许启动游戏并截图：

每阶段保存：

BEFORE

AFTER

并检查同一场景。

不要只凭代码推测视觉结果。

如果环境无法运行游戏：

明确告诉我：

哪些修改需要人工截图验证。

不要假装已经验证。

---

# 三十五、总设计决策规则

当出现设计选择时：

优先级按以下顺序：

1. Gameplay Readability
2. Interaction Clarity
3. Visual Hierarchy
4. Consistency
5. Modern Appearance
6. Decoration

即：

**好用 > 好看 > 炫技。**

---

# 三十六、最终目标画面

希望玩家第一次看到重制版时的反应是：

> “这是同一个游戏，但怎么突然像一个正式发行的现代独立游戏了？”

而不是：

> “这个 MOD 加了好多特效。”

画面仍然应该能够认出：

这是 Mutagenic。

但：

* 不再像 prototype
* 不再像 debug UI
* 不再有明显 pixel-art UI 味道
* 字体清晰
* HUD 统一
* 世界更有层次
* 按钮有触感
* 菜单响应快速
* 视觉克制
* 高 DPI 屏幕上依然舒服

---

# 三十七、开始执行

现在开始工作。

第一步：

**扫描仓库，定位当前截图中所有主要视觉元素对应的场景、脚本、资源和绘制代码。**

然后输出一个简洁的 Visual Audit。

紧接着实施：

**PHASE 1 —— HD CLEANUP**

不要在给出分析和建议后停止。

完成 PHASE 1 后：

1. 构建 Candidate；
2. 运行现有自动验证；
3. 如果环境允许，启动游戏；
4. 截取与当前基准截图相同位置；
5. 对照判断改善；
6. 修复明显问题；
7. 报告实际修改文件、Patch、视觉变化以及仍需人工确认的位置。

然后进入：

**PHASE 2 —— 当前 Hub 场景 Vertical Slice。**

在任何时候，如果发现某个“像素感”来自真正的低分辨率 Sprite，而不是 Godot 绘图：

不要用模糊滤镜掩盖问题。

把该资产加入：

**HD Asset Replacement List**

继续完成其他可以程序化升级的部分。
