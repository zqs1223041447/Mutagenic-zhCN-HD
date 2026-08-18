# PHASE 6 —— 像素轨（Art Asset Pass 提前轨）设计规格（des-B1）

> 记录：2026-08-18。设计 lane：des-B1（像素轨）。写域：**仅本文件**。
> 定位：PHASE 6 Pixel Asset Pass 的提前轨设计规格（与 2b HUD 轨并行推进，不等 PHASE 2 程序化 UI 完成）。
> 触发：用户 S5 反馈"人物仍然是像素风，技能图标也是像素风"（2026-08-17 22:0x），用户显式指示本轨与 2b 并行。
> 关联：需求 `docs/requirements/HD_UI_REMASTER.md`（§三/§三十）；审计 `docs/requirements/PHASE0_VISUAL_AUDIT.md`；stex 契约预检 `10_logs/v2-tileset-precheck-20260817-011959/precheck_report.json`；进度 `.slim/deepwork/hd-ui-remaster.md`。
> 事实基线：本规格中所有路径/尺寸/计数均经本次只读核查（03_raw/04_recovered 实际文件 + stex 二进制头解析），非截图推测。

---

## 0. 结论速览（先读）

1. **C 类像素资产按"能否程序化"分三档**：
   - **可程序化（零资产）**：伤害数字（monogram 观感 = `FloatingDamage.tscn:7` 节点 scale=0.5 把矢量字体压成 9px，**monogram/stack_pixel 字体本体全仓零引用**）、玩家地面阴影（draw 椭圆）、过渡期降违和（outline/光环）。
   - **必须资产替换（管线外产出合法 stex/.res）**：技能图标 57 个 16×16、状态/增益/装备/独有图标约 177 个 16×16、玩家精灵七部件（SpriteFrames .res 二进制，本轨最大工作量项）。
   - **不在本轨写域**：小地图本体（Minimap.gd 程序绘制 + 2b 文件域）、StatusBar 旗标显示尺寸（StatusBar.tscn 属 2b 域；本轨只升级 sprites/skills/* 资产源）。
2. **资产替换唯一可行路径** = 管线外产出（人工 Godot 3.5 编辑器 import 或受控 GDST+WebP 生成器）→ 以 stex 字节入库 `mods/<id>/assets/` → asset_overlays 注入。管线内 PNG reimport 已判死（fix-2 预检 C 结论），本规格沿用。
3. **关键新增约束（本次核查发现）**：当前 asset_contract 门校验 **same-dimension**——16×16 → 32/48 升分辨率替换会撞门，需先扩展 gate 契约（开放决策点 D1）。技能图标 32×32 原生替换恰好 1:1 匹配 `SkillDisplay.tscn` 显示尺寸，是 P2a 的最小改动路径。
4. **批次**：B-p1 伤害数字（程序化）→ B-p2 图标 stex 替换（P2a 核心技能 / P2b 状态增益 / P2c 装备）→ B-p3 玩家精灵（管线外重制，最大项）→ B-p4 小地图图标/旗标链路（依赖 2b）。每批独立 candidate + 机器 gate + S5。

---

## 1. 任务背景与 S5 反馈映射

| 用户 S5 反馈项 | PHASE 0 审计定位 | 本次核查结论 | 归属轨 |
|---|---|---|---|
| 人物像素风 | A2 玩家七部件 16-32px aseprite + shadow 16×16，相机 zoom=0.5 → 屏上 8-16px | 部件 = SpriteFrames `.res`（RSRC 二进制含内嵌子资源，见 §3.1.2），资产替换成本最高；zoom 是全局杠杆需评审 | **本轨**（资产）＋ 用户评审（zoom） |
| 技能图标像素风 | B7 全部 16×16 PNG 拉大 2-3x，filter=false | skills 58 个 stex（57×16×16 + 1×32×32）；显示侧 SkillDisplay 32×32 / BuffDisplay 48×48 | **本轨**（stex 源） |
| 伤害数字（monogram 像素字体） | B9 字体档含 monogram/stack_pixel | **事实修正**：monogram-extended.ttf / stack_pixel.ttf 存在于 `03_raw/Fonts/` 但 03_raw 与 04_recovered **全仓零引用**（orphan）。真实渲染 = `FloatingDamage.tscn:7` 父节点 `scale=0.5` 把 MainTheme 默认 rsans 18px 压到 9px 有效字号 + filter=false + pixel_snap → 观感即"像素字体" | **本轨**（程序化） |
| 装备图标 | B7 Genes.gd:285 / UniquePools / OrbTypes / base_types | base_types 47×16×16、uniques 23×16×16、gui/equipment 槽位 16×16 | **本轨**（stex 源） |
| 小地图 | B4 Minimap.tscn 206×206，Minimap.gd set_pixel + draw_circle，zoom 6.0 | 本体 = A 类程序绘制（逐像素 set_pixel），非贴图；worldmap 图标 16×16 stex 为 C 类 | 本体 **2b 轨**；worldmap 资产源 **本轨**（低优先） |
| StatusBar 8×8 旗标 | B7 8×8 0.5x 降采样糊 | `StatusBar.tscn:41-118` 8 个 TextureRect 8×8 stretch_mode=6 显示 16×16 源 → 降采样糊；显示尺寸修复属 StatusBar.tscn（**2b 域**），资产源 sprites/skills/*（**本轨**） | 显示侧 **2b**；资产源 **本轨** |

---

## 2. 硬约束（本轨全程遵守）

1. **引擎**：Godot 3.x（实际 3.5.3）/ GLES3。禁止升级 Godot 4；禁止依赖 4.x 导入产物。
2. **行尾**：`.gd/.tscn/.tres/.json/.md` 一律 LF；`.ps1/.bat` CRLF（.gitattributes 约束）。preimage 逐字节匹配，禁止混入 CRLF。
3. **roundtrip 3744 铁律**：不增删任何 pack 路径。ASSET_PATCH/asset_overlays 只覆盖**既有** stex 路径（target is_file 守卫）；人工资产以 stex 字节入库 `mods/<id>/assets/`（Git 内新增文件，不在 pack 路径集合，不破坏 roundtrip）。
4. **像素画不简单放大**（需求 §三原文）：禁止把 runtime bilinear（`Texture.flags |= FLAG_FILTER`）或 filter=true 当"高清重制"主方案；禁止"放大 + 模糊"假装新美术。
5. **不晋升 baseline**：所有批次 candidate 定位 = S5 人工视觉抽查对象，晋升需 oracle + 用户显式批准。
6. **禁止访问 F: 盘**；脚本路径相对 repo root，禁止硬编码 `G:\`。
7. **不写 2b 域文件**（写域隔离见 §6）；越界需主 agent 裁决。
8. **不改玩法/碰撞/移动/伤害逻辑/快捷键**（需求 §三十一）；相机 zoom 变更属全局视觉变更，见开放决策点 D2。
9. 本次任务（des-B1）零 git add / git commit。

---

## 3. 可行性裁定（逐资产）

### 3.1 全局技术事实（本次核查，规格依赖）

**3.1.1 stex 二进制契约（复核 fix-2 预检 + 实测）**

- 28 字节 GDST 头：`GDST` magic(4) + W(4) + H(4) + flags(4) + 字节16-19=`00 00 20 06` + format(4) + data_size(4) + 负载。
- 实测 `arc.png-...stex`（技能图标代表）：16×16，flags=0，format=1，146 字节，负载 = WebP VP8L（`WEBP` RIFF 容器）。
- **format=1 = WebP 负载**，与 tileset 同构（预检结论一致）。技能图标与 tileset 同契约，**无第二个格式族**。
- 运行时读取路径 = `.import/xxx.png-<hash>.stex`（.import 侧车 remap），替换该路径字节即运行时生效；**PNG 源本体不在包内也无需在包内**。
- **同尺寸约束（本次明确）**：fix-2 预检记录 asset_contract 门 = "valid same-dimension STEX with preserved flags and WebP marker"——**当前门强制替换前后同尺寸**。16×16 → 32/48 升分辨率替换将撞门，需要 gate 扩展（D1）。

**3.1.2 SpriteFrames `.res`（玩家部件）二进制结构**

- 实测 `default.aseprite-....res`（1910B）：RSRC 魔数 + SpriteFrames 资源 + **内嵌子资源引用 `local://2/3/4`**（帧贴图内嵌在同文件）+ atlas 路径引用。
- 含义：玩家部件不是"一个 PNG"，是**二进制 SpriteFrames 资源**。ASSET_PATCH 字节替换 = 需整体重建 .res（含内嵌帧），人工无法手写；唯一现实路径 = 管线外 Godot 3.5 编辑器重制动画并 reimport 出 .res/.stex 对。

**3.1.3 字体孤儿事实（本次核查）**

- `03_raw/Fonts/`：ChivoMono / monogram-extended.ttf / rsans.ttf / space.ttf / stack_pixel.ttf。
- `rg -i monogram|stack_pixel` 在 03_raw 与 04_recovered **零命中**（含 .gd/.tscn/.tres/.import）。两字体为孤儿资产。
- 实际伤害数字渲染链：`FloatingDamage.tscn`（Label，theme=MainTheme，默认 rsans 18px）→ 父 `FloatingDamageText` Node2D `scale=0.5` → 有效 9px。
- 推论：**"monogram 像素伤害数字"是观感不是字体**；修复 = 程序化，且**不涉及任何字体文件替换**。

**3.1.4 16×16 图标存量盘点（本次实测，03_raw/.import stex 头解析）**

| 目录 | stex 数 | 尺寸分布 | 显示侧 |
|---|---|---|---|
| sprites/skills | 58 | 57×16×16 + 1×32×32 | SkillDisplay 32×32 / BuffDisplay 48×48 / StatusBar 8×8 |
| sprites/status_effects | 27 | 27×16×16 | StatusBar（8×8）/ BuffDisplay |
| sprites/status_effects_new | 13 | 13×16×16 | BuffDisplay |
| sprites/buff_icons | 20 | 20×16×16 | BuffDisplay |
| sprites/base_types | 47 | 47×16×16 | 装备栏/词缀面板 |
| sprites/uniques | 23 | 23×16×16 | 独有装备图标 |
| sprites/effects | 13 | 11×16×16 + 2×32×32 | 世界特效 |
| sprites/characters | 12 | 12×16×16 | NPC/角色头像 |
| sprites/gui（含 equipment 槽位） | 41 | 16×16×24 + 32×32×10 + 64×128×3 + 15×15 + 64×64 + 128×128 + 60×60 | 槽位/九宫格/血球（256×256×8 属 2b 域） |

16×16 图标类合计 ≈ **234 个 stex**（skills 57 + status 27+13 + buff 20 + base_types 47 + uniques 23 + effects 11 + characters 12 + gui 24）。

**3.1.5 玩家部件存量盘点**

- `04_recovered/sprites/player/`：heads 8、helmets 7、hands 10、feet 8、pants 10、back 8 ≈ **51 个 .aseprite**（→ SpriteFrames .res），另有 shadow.png 16×16（`Player.tscn:553`）、shielded.png。
- `Player.tscn:542-730`：7 个 SpriteFrames 引用（pants/helmet/head/feet/hands/back/hands-orbs）+ shadow + shielded；`Player.gd:184-228` 品质变色用 modulate 混色。
- `Outfits.gd` 全部 preload aseprite → 资产替换必须覆盖 Outfits 引用面（51 文件 + 引用脚本）。

### 3.2 逐资产裁定表

| # | 资产 | 现状 | 方案 | 裁定 | 理由 |
|---|---|---|---|---|---|
| P1 | **伤害数字**（FloatingDamage 链） | 矢量字体被 scale=0.5 压成 9px；monogram/stack_pixel 为孤儿字体 | **程序化**（TEXT_PATCH/CODE_PATCH） | ✅ 程序化 | 零资产依赖、零新文件；根因是节点缩放不是字体。去掉 scale=0.5 + 显式字号（16-18px 逻辑）+ 可选数字专用矢量字体。降级：仅去 scale 保留 rsans |
| P2 | **技能图标**（sprites/skills/*，57×16×16） | 16×16 → 显示 32×32（2x 最近邻）/48×48（3x） | **资产替换**（管线外 stex） | 必须替换 | 53 个具象图标（武器/法术/元素）无法矢量重绘且失辨识度；`_draw` 程序化重绘只适用于抽象符号。32×32 替换后 SkillDisplay 1:1 无损。`Skills.gd:59-111` 引用面不变（路径不变，仅 stex 字节变） |
| P3 | **状态/增益图标**（status_effects 27+13、buff_icons 20） | 16×16；StatusBar 8×8 降采样、BuffDisplay 48×48 3x | **资产替换**（stex）＋ 显示侧 2b 配合 | 必须替换（资产侧）；显示尺寸归 2b | 与 P2 同理由；StatusBar 修复主杠杆在 2b 显示 rect（8→16px），本轨升级 16×16 源后 2b 改 rect 即 1:1。依赖链：P3 资产先于/并行 2b StatusBar patch |
| P4 | **装备图标**（base_types 47、uniques 23、gui/equipment 槽位） | 16×16 → 装备栏放大显示 | **资产替换**（stex） | 必须替换 | 同 P2；数量大（94+），按词缀优先切分；passives 24×24（4 个）原生尺寸合理，低优先级 |
| P5 | **玩家精灵七部件**（51 aseprite → .res + shadow 16×16） | 16-32px 像素画，zoom=0.5 → 屏上 8-16px | **资产替换**（管线外重制 .res/.stex 对）＋ 过渡期程序化降违和 | 必须替换（资产侧）；程序化重构判不可行 | SpriteFrames .res 二进制含内嵌帧，字节替换需整体重建（§3.1.2）；`_draw` 重构角色 = 破坏动画/碰撞/Outfits 绑定（§三十一禁令）。**本轨最大工作量项**。过渡期：玩家侧 outline/地面光环（CODE_PATCH）降低违和感（需求 §三 允许）；shadow 可先程序化（draw 椭圆）后替换 |
| P6 | **玩家阴影** shadow.png 16×16 | 16×16 像素圆 | 程序化优先（draw 椭圆接触阴影）→ 替换备选 | ✅ 程序化优先 | 阴影是纯几何（椭圆+alpha 渐变），`_draw` 输出远好于 16×16 贴图放大；零资产 |
| P7 | **StatusBar 旗标**（显示侧） | 8×8 TextureRect stretch_mode=6 显示 16×16 | **2b 轨**（rect 8→16） | 移交 2b | `StatusBar.tscn` 属 2b 写域（§6）；本轨仅保证资产源（P3）。本规格登记并声明依赖，不实施 |
| P8 | **小地图**（本体） | Minimap.gd set_pixel 逐像素 + draw_circle + zoom 6.0 | **2b 轨**（程序绘制精修） | 移交 2b | A 类程序绘制，无资产可换；文件域 Minimap.tscn/Minimap.gd 归 2b |
| P9 | **小地图图标**（sprites/worldmap，Levels.gd:28-41 preload） | 16×16 stex | 资产替换（stex，低优先级） | 替换（低优先） | C 类贴图；影响小，排在 P2c 之后 |
| P10 | **相机 zoom=0.5**（全局杠杆） | 16-32px 资产 → 屏上 8-16px | **不默认执行**；需用户+oracle 评审 | 开放决策点 D2 | zoom 0.5→1.0 会减少可见视野（zoom in），属全局视觉/布局变更，影响所有关卡与 6 分辨率验证；不是本轨默认项。若批准，需全套 S2 回归 |

### 3.3 资产替换的实施约束（适用于 P2/P3/P4/P5/P9）

1. **产出位置**：管线外。二选一：
   - 首选：人工使用 Godot 3.5 编辑器临时工程 import 新 PNG（aseprite 重绘）→ 产出 stex（图标）或 .res+.stex 对（玩家 SpriteFrames）。与 fix-2 预检 future 能力一致。
   - 备选：受控 GDST+WebP 生成器脚本（新工具，需 oracle 批准立项）：输入人工 PNG → 28B GDST 头 + WebP VP8L 负载。逻辑封闭、可审计、可复现；WebP 编码依赖（Pillow 自带）需列入 toolchain hash。
2. **入库与注入**：stex 字节入库 `mods/<id>/assets/`（人工数据，Git 管理）→ `asset_overlays`（target = 既有 stex 路径，preimage + replacement 双哈希锁定）→ build_declared_pack copy2 覆盖。**不新增 pack 路径**（roundtrip 3744 安全）。
3. **尺寸策略**（同尺寸约束下的三个选项，D1 裁决）：
   - 选项 A（**推荐，零 gate 变更**）：**32×32 替换**。16→32 需 gate 扩展（同尺寸门）；但若目标定 32×32 且把 gate 改为"新尺寸 = 显示尺寸"校验——见选项 B。
   - 选项 B：**gate 扩展为新契约**（stex 自描述合法 + WebP VP8L + flags 保留 + 尺寸≤显示 rect 或 = 声明目标）。16→32/48 放行。需 oracle 评审资产契约校验逻辑（改动 scripts 校验脚本，属管线能力变更，走 2b 之外的新审批）。
   - 选项 C（保守，不推荐作主方案）：保持 16×16 同尺寸重绘——仅消除画质劣化，放大锯齿仍在（显示 32px），不符合需求"HD"目标。
4. **每 stex 契约自检**（注入前）：GDST 魔数、W/H 与内容一致、flags 保留（0）、format=1、WebP 负载可解码、data_size 一致。asset_contract 门继续校验。
5. **引用面不变**：`.import` 侧车路径、脚本 preload 路径、tscn ext_resource 全部不变——只换 stex 字节。`Skills.gd`/`Genes.gd`/`Outfits.gd`/`Levels.gd` 无需改动（P5 例外：若重制 aseprite 需整体换 .res，引用面仍不变，仅字节替换）。

---

## 4. HD Asset Replacement List（正式登记）

来源标记：**V** = 原版提取验证（03_raw/04_recovered 绑定）；**H** = 人工管线外重制（stex/.res 入 Git mods/<id>/assets/）；**P** = 程序化（CODE/TEXT_PATCH，零资产）。
可重新制作：✓ 可行（管线外重制工具链已验证可行性）/ ○ 可行但高成本 / ✗ 不可行（须程序化或放弃）。

| 资产族 | 资产路径（代表） | 存量 | 现状尺寸 | 目标方案 | 来源标记 | 可重新制作 | 批次 |
|---|---|---|---|---|---|---|---|
| 伤害数字渲染 | Scenes/Particles/FloatingDamage.tscn（:7 scale） | 1 节点 | 18px→有效 9px | 去 scale + 字号 16-18 + 数字矢量字体 | V | ✗（须程序化） | B-p1 |
| 孤儿像素字体 | Fonts/monogram-extended.ttf、stack_pixel.ttf | 2 | — | **不替换**（零引用，保留原位不删） | V | — | — |
| 技能图标 | sprites/skills/*（57 个 16×16 stex；arc/axe/bow/…） | 57 | 16×16 | 32×32 stex 替换（1:1 匹配 SkillDisplay） | V→H | ✓（人工重绘 + 编辑器 import 或生成器） | B-p2a |
| 技能动画帧 | sprites/skills/*.aseprite（34 个 SpriteFrames .res） | 34 | 多帧动画 | 暂缓（世界特效类，非 HUD 图标；B-p2 后评估） | V | ○ | 后置 |
| 状态图标 | sprites/status_effects/*（27）+ status_effects_new/*（13） | 40 | 16×16 | 16×16 同尺寸重绘 + 2b 显示 rect 16px | V→H | ✓ | B-p2b |
| 增益图标 | sprites/buff_icons/* | 20 | 16×16 | 32×32 stex 替换（BuffDisplay 48×48 的 1.5x 非整数 → 目标 48 或 2b 调显示） | V→H | ✓ | B-p2b |
| 装备类型图标 | sprites/base_types/* | 47 | 16×16 | 32×32 stex 替换 | V→H | ✓ | B-p2c |
| 独有装备图标 | sprites/uniques/* | 23 | 16×16 | 32×32 stex 替换 | V→H | ✓ | B-p2c |
| 装备槽位图标 | sprites/gui/equipment/*（helmet_slot 等，Genes.gd:9-17） | 8 | 16×16 | 32×32 stex 替换 | V→H | ✓ | B-p2c |
| 被动图标 | sprites/gui/passives/* | 4 | 24×24 | 保留（原生尺寸合理）或同尺寸重绘 | V | ○ | 低优先 |
| 世界特效图标 | sprites/effects/*（16×16 部分） | 11 | 16×16 | 32×32 stex 替换（低优先） | V→H | ✓ | 后置 |
| 角色/NPC 头像 | sprites/characters/* | 12 | 16×16 | 32×32 stex 替换（低优先） | V→H | ✓ | 后置 |
| 小地图图标 | sprites/worldmap/*（Levels.gd:28-41） | 9 | 16×16 | 32×32 stex 替换（低优先） | V→H | ✓ | B-p4 |
| **玩家部件** | sprites/player/{heads,helmets,hands,feet,pants,back}/*.aseprite（→ .res） | 51 | 16-32px 多帧 | 管线外重制（重绘动画 → 新 .res+.stex 对，路径不变） | V→H | ○（最大工作量） | B-p3 |
| 玩家阴影 | sprites/effects/shadow.png（Player.tscn:553） | 1 | 16×16 | 程序化 draw 椭圆优先 → 重制 32×32 备选 | V→P | ✓ | B-p3 |
| 玩家护盾贴图 | sprites/effects/shielded.png（Player.tscn:632） | 1 | 16×16 | 32×32 重制（随 B-p3） | V→H | ✓ | B-p3 |
| StatusBar 旗标显示 | Scenes/StatusBar/StatusBar.tscn:41-118 | 8 节点 | 8×8 rect | **2b 轨**：rect 8→16（配合本轨 16×16 资产源即 1:1） | V | —（移交 2b） | 2b 依赖 |
| 小地图本体 | Scenes/Minimap/Minimap.tscn、Minimap.gd、TextureRect.gd | — | 206×206 程序绘制 | **2b 轨**（set_pixel 逐像素精修/图标渲染） | V | —（移交 2b） | 2b 依赖 |
| 相机 zoom | Player.tscn:567-572 | 1 属性 | 0.5 | **开放决策点 D2**（需评审，非默认） | V | — | D2 |
| 血球 256×256 / 九宫格 / 按钮切片 | sprites/gui/globes/*、ninepatch* | 8+7 | 256/32/60/128 | **2b 轨**（Globe.tscn/MainTheme.tres 域） | V | —（移交 2b） | 2b 依赖 |

> 注：sprites/gui 中 globes/ninepatch/cursor 虽同为 C 类贴图，但其消费方（Globe.tscn/MainTheme.tres/GUI.tscn）全部在 2b 写域，本轨不登记实施、只登记事实；替换决定权归 2b + oracle。

---

## 5. 实施批次（每批独立 candidate + 机器 gate + S5）

依赖链前缀（所有批次）：`zhcn v8.1 信任链 → v1-hd-cleanup → w2a-aggregate → 本批`（与 2b 各批平行，二者零交集）。

### B-p1 —— 伤害数字程序化（零资产，先做，最快见效）

- 目标：`Scenes/Particles/FloatingDamage.tscn`（TEXT_PATCH）：`scale = Vector2(0.5, 0.5)` → `Vector2(1, 1)`；Label 显式字号（16-18px 逻辑坐标）；可选 `FloatingDamage.gd`（CODE_PATCH）crit 缩放路径复核（crit 时 rect_scale×2 在 1.0 基础上是否过大，需 designer 定参数）。
- 策略：TEXT_PATCH（tscn 精确字段）+ 可选 CODE_PATCH；preimage = 整文件 SHA；零新文件；roundtrip 3744 安全。
- Gate：resolve/apply/compile（无脚本则跳过）/pack/roundtrip 3744/boot 无 ALERT/GDRE semantic（字号属性或 scale 属性断言）；S5 战斗区伤害数字 + XP 提示两类截图（FCT 复用，两类都要验）。
- 风险与降级：FloatingDamage 是通用 FCT（伤害/XP/提示共用）——改动影响所有浮动文本；降级 = 仅去 scale 不动字号，字号微调放 B-p1 后续补丁。

### B-p2 —— 图标 stex 替换（P2a 核心技能 → P2b 状态增益 → P2c 装备）

- 前置：**D1 gate 扩展裁决**（同尺寸门 vs 新契约）。选项 A（32×32 目标 + gate 扩展）为推荐路径。
- 目标：
  - P2a：sprites/skills/* 中 Skills.gd:59-111 preload 的 53 个具象图标 → 32×32 stex（SkillDisplay 1:1 无损）。
  - P2b：status_effects/status_effects_new/buff_icons → 16×16 同尺寸重绘或 32×32（配合 2b StatusBar/BuffDisplay 显示调整）。
  - P2c：base_types/uniques/gui-equipment → 32×32。
- 策略：ASSET_PATCH / asset_overlays（人工 stex 入 `mods/w2b-pixel/assets/`，preimage+replacement 双哈希）；`.import` 与脚本引用面零改动。
- Gate：机器 gate 全链 + **asset_contract 门（扩展后新契约）**：每 stex GDST 魔数/W/H/flags/format=1/WebP 可解码 + 尺寸 = 声明目标 + 与显示 rect 兼容性表；roundtrip 3744；boot；GDRE semantic（Skills.gd preload 路径不变断言）。S5：技能栏 6 图标 + 装备栏 + 状态栏 8×8 修复后截图。
- 风险与降级：gate 未裁决 → 降级为同尺寸 16×16 重绘（画质改善、无放大消除，记规格偏差）；icon 语义漂移（重绘认不出）→ 每图标 S5 抽查 10% 抽样 + 用户重点图标清单；WebP 编码工具未批准 → 人工 Godot 3.5 编辑器 import 路线（无新脚本）。

### B-p3 —— 玩家精灵（管线外重制，最大工作量）

- 前置：B-p1/B-p2 完成 + D2（zoom）裁决落地（若 D2 批准 zoom→1.0，重制目标尺寸与细节密度随之调整）。
- 目标：sprites/player/* 51 个 aseprite 重制（保持 7 部件装配结构、动画帧数/朝向、Outfits 变体映射）→ 管线外 Godot 3.5 编辑 import → 新 .res/.stex 对 → 字节替换。shadow 先行程序化（P6）。
- 策略：ASSET_PATCH（.res+.stex 字节替换，路径不变）+ CODE_PATCH（过渡期 outline/地面光环；shadow draw 椭圆）。
- Gate：机器 gate 全链 + roundtrip 3744 + boot + GDRE semantic（SpriteFrames 资源类型/动画名断言）+ S5 玩家移动/攻击/品质变色三态截图。**动画帧数与命名契约**：重制必须逐帧对照原 .res 动画名（Idle/Walk/Attack…），差异需在 GDRE semantic 断言中列明。
- 风险与降级：工作量最大（51 文件 + 动画对齐），拆子批（先 default 套装 → 后 Outfits 变体）；动画回归（帧序/offset 错位）→ 以 GDRE 恢复动画名 + S5 逐动作验证；资源未就绪期间保持现状 + 过渡期程序化增强，不阻塞其他批次。

### B-p4 —— 小地图图标 / 旗标链路收尾

- 目标：sprites/worldmap/* 9 个 16×16 → 32×32 stex（低优先）；StatusBar 旗标**资产侧**交付确认（16×16 源就位），显示侧修复由 2b 轨实施，本批只做依赖链声明与联合 S5。
- 策略：asset_overlays（同 B-p2）；无 2b 文件改动。
- Gate：机器 gate + 联合 S5（与 2b StatusBar patch 的聚合 candidate 一起验收 8×8→16×16 清晰度）。
- 风险与降级：2b StatusBar 未完成 → 本批仅交付资产源，验收推迟到 2b 聚合；worldmap 图标影响面小，可随时后置。

---

## 6. 与 2b 轨的边界（写域隔离声明）

**本轨（像素轨，fix-B2 实施域）**：
- 文件域：`Scenes/Particles/FloatingDamage.tscn`、`FloatingDamage.gd`（B-p1）；`sprites/skills/*.stex`、`sprites/status_effects/*`、`sprites/status_effects_new/*`、`sprites/buff_icons/*`、`sprites/base_types/*`、`sprites/uniques/*`、`sprites/gui/equipment/*`、`sprites/worldmap/*`、`sprites/effects/shadow.png`/`shielded.png`（stex 字节）；`sprites/player/*`（.res/.stex 字节）；`Player.tscn`/`Player.gd`（仅 B-p3 过渡期 CODE_PATCH 与 shadow 程序化）；`Skills.gd`/`Genes.gd`/`Outfits.gd`/`Levels.gd`（**默认零改动**，仅当引用面必须变化时经主 agent 批准）；`mods/w2b-pixel/`、`10_logs/nl2mod-w2b-pixel-*/`。
- **本轨不得碰**：GUI.tscn、MainTheme.tres、Minimap.tscn、Minimap.gd、Globe.tscn、StatusBar.tscn、StatusBar.gd、sprites/gui/globes/*、ninepatch*、cursor、BuffDisplay.tscn（未分配域，见下）。

**2b 轨（fix-A2 实施域，冲突硬规则 §2）**：GUI.tscn / MainTheme.tres / Minimap.tscn / Globe.tscn / StatusBar 相关。本规格要求 2b 轨**不得改动 sprites/* 任何 stex/PNG/aseprite 源**（含 sprites/gui/equipment/*、sprites/skills/*）——图标源品质归本轨。

**未分配域（需主 agent 裁决）**：
- `BuffDisplay.tscn`（48×48 显示 3x）：既不在 2b 明确列表也不在本轨列表。本轨**默认不碰**；其显示尺寸调整若需配合 P2b 32/48 替换，由主 agent 裁决归属（建议归 2b，因属 HUD 显示组件）。
- `sprites/gui/skill_supports/*`（22×32×32）：原生 32×32，无需替换，登记不实施。

**依赖链声明**（冲突硬规则 §4）：
- 2b StatusBar 显示 rect 修复（8→16）**依赖**本轨 P2b 资产源交付（或可先于资产独立做——16×16 源在 8×8 rect 下仍是降采样，所以顺序应为：本轨源 → 2b rect）。
- 本轨 B-p2 的 gate 扩展（D1）**依赖** oracle/主 agent 对 asset_contract 校验逻辑的裁决（scripts 改动，非本轨写域，需单独立项或主 agent 授权 fixer）。

---

## 7. 开放决策点（需 oracle / 主 agent / 用户裁决）

| # | 决策点 | 选项 | 建议 | 影响 |
|---|---|---|---|---|
| D1 | asset_contract 门是否扩展以放行升分辨率 stex | A. 扩展为新契约（自描述校验 + 目标尺寸声明）；B. 保持同尺寸，全部 16×16 重绘；C. 每批单独白名单 | A（B 为保底降级） | 决定 B-p2 是否真正"HD"（消除 2x/3x 放大） |
| D2 | 相机 zoom=0.5 → 1.0 | A. 保持 0.5（靠资产重制取胜）；B. 全局 1.0（视野减半，需全套 S2 + 6 分辨率回归）；C. 分关卡试点 | 先 A，资产到位后 S5 评估再议 | 屏上 8-16px → 16-32px，直接影响 B-p3 细节密度需求 |
| D3 | 图标重制生产方式 | A. 人工 Aseprite 重绘 + Godot 3.5 编辑器 import（无新脚本）；B. AI 生成后人工处理（需求 §三十 允许，但需用户批准 + 版权/一致性约束）；C. 受控 GDST+WebP 生成器脚本立项 | A 起步；B 需用户显式批准；C 作为工具链选项 | 工作量与批次节奏 |
| D4 | BuffDisplay.tscn 归属 | 归 2b / 归本轨 / 保持不动 | 归 2b（HUD 显示组件） | 边界澄清 |
| D5 | 批次顺序 | B-p1→B-p2→B-p3→B-p4（本规格默认）或用户指定 | 默认 | 每条 candidate 独立评审 |

---

## 8. 证据与参考

- 需求：`docs/requirements/HD_UI_REMASTER.md`（§三 C 类资产处理规则、§三十 PHASE 6）。
- 审计：`docs/requirements/PHASE0_VISUAL_AUDIT.md`（A2/B4/B7/B9、C 类汇总、预登记清单）。
- stex 契约：`10_logs/v2-tileset-precheck-20260817-011959/precheck_report.json`（A_c4_mechanism / B_asset_forms / C_reimport_capability / D1_asset_patch_shape / D3_tres_res_patch_to_raw_png）。
- 本次核查实测：`03_raw/.import/arc.png-b6f2699e96953d22a518bc2f45c3f192.stex`（16×16/146B/format=1 WebP）；`default.aseprite-7466b98ae71f87b14343848bf1822e04.res`（1910B RSRC SpriteFrames 内嵌子资源）；03_raw/04_recovered 全仓 rg（monogram/stack_pixel 零引用）；03_raw/sprites 全目录 stex 尺寸扫描（§3.1.4）。
- 进度：`.slim/deepwork/hd-ui-remaster.md`（lane 表、冲突硬规则、像素轨待办）。