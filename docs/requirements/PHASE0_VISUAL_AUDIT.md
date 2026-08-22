# 3.5.3 视觉只读审计（2026-08-16）

只读事实，路径相对仓库根。**不是**实施合同，不启动 HD / PHASE 1–6 / 像素资产轨。当前主线是 P1 Godot 4.7.1 迁移。

---

## 0. 关键结论（先读）

1. **"优先程序化高清重制"的前提不成立**。世界层 100% 由贴图构成（Sprite/AnimatedSprite/TileMap/Label），无任何 `_draw()`（全仓仅 3 处 `_draw`：Minimap/WorldMap/PassiveTree）。HUD 亦以 16×16/32×32 贴图为主。像素感的源头是**低分辨率像素美术资产（C 类）**，不是渲染参数。
2. 若将来做资产替换，清单会显著偏大（玩家/雕像/工作台/火把/传送门/技能图标/装备图标/血球/九宫格按钮/tileset）。那是 P4+ 的事，不是 P1。
3. 3.5.3 上曾观察到的渲染杠杆（当时不是布局改动）：`use_gpu_pixel_snap=true` 关掉、按钮 pressed/disabled 状态缺失、ProgressBar 全局亮红 fg、TooltipBase 定位 bug、字体描边层级混乱。迁到 Godot 4 后必须重新验证，不能照搬。
4. `project.binary` 实测值已全部解码（见 §D）：pixel_snap=true、texture filter=false、default_clear_color 中灰、tooltip_delay=0。

---

## A. 世界层审计（Hub / Hideout）

表中「建议 / PHASE 2 / PHASE 6」是 2026-08-16 对 3.5.3 的观察，**不是当前实施任务**。

| # | 元素 | 场景 | 脚本 | 渲染方法 | 质量现状 | 分类 | 建议 |
|---|---|---|---|---|---|---|---|
| A1 | 背景+网格 | `03_raw/Scenes/Levels/BaseLevel.tscn:17-35`（ParallaxBackground 黑 ColorRect 3840×2160 + 空 TextureRect 960×540）；`HideoutLevel.tscn:193-196`（TileMap cell 32×32，tile_data 272 格） | `HideoutLevel.gd:8-16`（_ready 覆写贴图替换） | TileMap autotile；**网格烤死在贴图** `Tilesets/tileset_factory.png` 224×96（主 `#252B38` 64%、棋盘 `#222326` 30%、**1px 格线 `#151C1F` 2.3%**） | 线宽/颜色/alpha 全部烤死不可调；0.5 相机缩放下 1px 线亚像素闪烁；平台原点仅 8×2 格 | **C** | 改运行时 `_draw()` 网格（可调 alpha/线宽）或重绘 tileset；tile_data 稀疏重复是调试遗迹 |
| A2 | 玩家 | `Player.tscn:542-730` | `Player.gd:184-228` | AnimatedSprite 七部件 16-32px aseprite；shadow.png 16×16；血条 24×4 StyleBoxFlat 绿 `#25D21B`+1px 黑（`:574-584`）；护盾 shader | 相机 zoom=0.5（`:567-572`）→ 屏上仅 8-16px；品质变色用 modulate 混色（`Player.gd:218-228`） | **C** | 放大部件贴图+filter，或相机 zoom 提到 1.0 配大视口（PHASE 6 决策） |
| A3 | NPC | `ClassStatue.tscn:20-22`、`SpecializationStatue.tscn:20-22`、`TrainingDummy.tscn:65-68` | `ClassStatue.gd:6-7` 等 | statue.aseprite 32×32（`#203030`/`#304040` 暗青灰，46% 不透明）；dummy = skeleton_warrior.aseprite 32×32 灰白+黑描边 | 无轮廓/发光/hover；与背景 tileset 同为暗色系，对比度不足 | **C** | 复用 Mob 已有 OutlineShader 或地面高亮环 |
| A4 | 工作台/仓库 | `Interactable.tscn` 实例：SkillBench frame=1 / MutationBench=2 / CraftingBench=3 / LoadoutBench=4 / OutfitBench=5 / SharedStash=chest | `*Bench.gd:5-13` | bench.aseprite 96×64 六帧 32×32（棕 `#301000` 系+绿 `#306000`）；chest 32×32；shadow scale(2,2) | 六台靠同贴图换帧、差异小难辨识；暗棕 vs 暗底对比低 | **C** | 统一边缘光/地面 halo；或高分辨率矢量化图标 |
| A5 | 火把 | `Brazier.tscn:40-49`（Hideout 放 8 个，`HideoutLevel.tscn:234-256`） | 无脚本 | brazier.aseprite 32×16 两帧 16×16（火 `#F05010`/`#D0C040`/`#F08000`）；Particles2D 烟 16×16 | 16px 火苗 0.5 缩放下仅 8px；**不发光**（场景无任何 Light2D） | **C** | 粒子 additive+glow，或接受"装饰火"定位 |
| A6 | 中央绿十字=Portal | `Portal.tscn:13-17`（Hideout (0,-128)，`HideoutLevel.tscn:213-214`） | `Portal.gd:6-18` | portal.aseprite 128×128 四帧 64×64（绿 `#409020`/亮绿 `#70F040`）；6 帧循环 @5fps；交互圈 r=32 | 全场景唯一高饱和元素但无光晕；5fps 有跳帧感 | **C** | 加 outline glow、提帧率、Light2D 光锥 |
| A7 | 世界漂浮标签 | `Interactable.tscn:25-54`：Node2D **scale=0.5** > VBox(theme InGameText) > Label | `Interactable.gd:10/15-23/41-45` | Label；主题 `Themes/InGameText.tres:5-10`（rsans 18px、outline 1px 黑、use_filter=true） | **scale=0.5 把 18px 打成 9px、描边减半**；无底衬、白字直落暗底 | **D** | 去节点缩放；16-20px+2px 描边+半透明深色底衬（PHASE 2 World Label 系统） |
| A8 | 选择圈/halo | shadow.png 全场景；`Notice.tscn`+`Notice.gd:6-8`（红 `#D01010` 16×16 浮动）；Mob 描边 `Mob.tscn:15-24` OutlineShader(width=1, enabled=false 默认关；magic `#0024E5`/rare `#E3E500` α0.31，`Colors.gd:46-47`) | — | 全贴图/Sprite | **无选择圈/无地面 halo/无点选高亮环**；hover 无视觉反馈 | **C** | 复用 OutlineShader 或程序圆环（draw_arc）做选中态 |
| A9 | 光照 | `World.tscn:8-12` ShaderMaterial + `Shaders/ScreenSpaceGI.tres:4` | — | **ScreenSpaceGI shader 内容为空**（仅 `shader_type canvas_item;`）；全仓无 Light2D/WorldEnvironment/CanvasModulate | **零光照**：纯黑底+平涂贴图，暗度全靠 tileset 单色 | **A** | 删空 shader 或实现真 screen-space 光晕+色温层 |

**世界层 Top 5 根因**：
1. `HideoutLevel.tscn:66-196` + `tileset_factory.png` — 网格烤死在贴图，1px 格线不可调、0.5 缩放下闪烁，地面细节贫。
2. `Interactable.tscn:27` — 标签 scale=0.5 → 9px 中文最差可读点。
3. `Player.tscn:567-572` — 相机 zoom=0.5 把全部 16-32px 像素画再缩一半，HD 化最大全局杠杆。
4. `World.tscn:8-12` + `ScreenSpaceGI.tres:4` — 空 shader 冒充 GI，世界层零光照，暗底平涂。
5. `Portal.tscn:13-17` — 中央绿十字全场景最亮却无光晕、5fps 跳帧，锚点质感粗糙。

---

## B. HUD / UI 层审计

| # | 元素 | 场景 | 脚本 | 渲染/样式方法 | 质量现状 | 分类 | 建议 |
|---|---|---|---|---|---|---|---|
| B1 | 生命球 | `GUI/Globes/Globe.tscn`（39 行）；挂载 `GUI.tscn:331-334`（左下） | `Globe.gd:3-6`（update_progress 仅 2 行） | TextureProgress 双 256×256 PNG（under=globe_inner_dark_2 / progress=globe_overlay_dark_final，fill_mode=3 自下而上液位）；数字 HBox x∈[-174,426] 600px 宽，ChivoMono 24px "150 / 200" 压球心 | **256px 巨球+大面积纯红+24px 数字居中+零动画反馈**；PNG filter=false | **C** | 缩小 25-40%（~160px）、深色金属外框+内暗环+径向渐变液、数字下移弱化、100-180ms 受伤反馈（禁屏幕闪红） |
| B2 | 底部 Dock | `GUI.tscn:133-329`（SkillBar HBox） | `GUI.gd`：XP/等级 99-110、资源 332-337、快捷栏 156-171、按钮 323-342 | PanelContainer 600px 底部居中 theme=MainTheme → ninepatch_panel.png 九宫格（`MainTheme.tres:53-63`，region 32×32 margin 16） | 600×~150px 灰调试框；三块信息同平面无分隔；子间距随意（16/8/4px）；按钮纯文字默认 UI | **C+A** | Compact Command Dock：更薄更暗半透明、spacing/divider/surface 三级分区、按钮统一层级 |
| B3 | XP 条 | `GUI.tscn:205-216`（MutationTierXP 304×12） | `GUI.gd:99-104` | fg=StyleBoxFlat 纯白（`GUI.tscn:19-25`）；bg=`#484848`+1px 黑（`:27-33`） | 纯白填充、无圆角、12px 过薄；满级文字 "Maxed" | **A** | fg 品牌色、bg 圆角内边距、高度 16-20px |
| B4 | 区域/小地图 | `GUI.tscn:336-425`（LevelInfoContainer 右顶窄列）；`Minimap/Minimap.tscn:32-56`（206×206，`BaseLevel.tscn:49`）；词缀 `Minimap.tscn:16-30`（margin_top=346） | `GUI.gd:82-94/116-117/186-197`；`Minimap.gd:22-62/64-89`；`TextureRect.gd:24-31`（_draw + 1px 绿玩家点，zoom 6.0） | 三处散落：Label + Image.set_pixel + draw_circle + StyleBoxFlat 黑 α0.706 无边框（`Minimap.tscn:7-10`）；地图框 ColorRect 黑 α0.196 7px 内边距（`:50-56`） | **三块信息三个容器，边框语言互不相干**；词缀面板 70% 纯黑突兀；地图无外框无网格线 | **A** | 合并为统一 Zone/Minimap Information Module（§21） |
| B5 | 按钮 | `Themes/MainTheme.tres` 全局（53 场景引用） | — | normal/pressed/disabled 全 = ninepatch_58.png（`:136-145`），hover/focus = ninepatch_58_focus.png（`:23-41`）；文字色 normal `#E0E0E0`/disabled `#5F5F5F`/hover 绿 `#4BA646`/pressed `#E0E0E0` | **pressed/disabled 与 normal 无任何视觉差异；无 Selected 态**；StyleBoxTexture 无圆角参数；PickupTheme 例外（`#E5E8E8` α0.737+2px 边） | **C** | 统一 StyleBoxFlat 4 态色板；Pressed 位移 1px+变暗；不做大胶囊/亮白边框 |
| B6 | Tooltip | `TooltipBase.gd:4-18`；`SkillTooltip.tscn:6-28`（PanelContainer+RichTextLabel 480px）；`GeneTooltip` | `SkillTooltip.gd:19-27`；`SkillDisplay.gd:23-27` | 面板 = ninepatch_panel；`gui/timers/tooltip_delay_sec=0.0` 瞬现 | **BUG `TooltipBase.gd:17`：`centered_position.x += position_offset.y`（应为 .x）**；无过渡动画（modulate 硬切换） | **C** | 修 L17；统一容器样式；50-100ms 淡入；delay 0.2-0.3s |
| B7 | 技能/装备图标 | `Skills.gd:153-177` preload + `179-209` 注册；`SkillDisplay.tscn:33-40`（32×32）；`BuffDisplay.tscn:39-52`（**48×48 3x**）；`StatusBar.tscn:41-48`（**8×8 0.5x 缩小 → 模糊**）；`Genes.gd:285`；`UniquePools/*.gd`；`OrbTypes.gd:15` | — | 全部 16×16 PNG 拉大 2-3x；filter=false | **16×16 像素小图拉至 32/48px；StatusBar 旗标 0.5x 降采样糊**；与 18px 矢量中文三套视觉年代 | **C** | 重绘 32/48px 图标（AsepriteWizard 管线可重建）；StatusBar 至少 16×16 |
| B8 | 全局主题 | `Themes/MainTheme.tres`（188 行，唯一全局主题）；`InGameText.tres`；`PickupTheme.tres`；`StatusBarShader.tres` | — | 14 个 StyleBox（4 贴图 + LineEdit + Tab×3 + Tree×2 + **ProgressBar fg 亮红 `#FF0000`** + VScrollBar） | 3 主题 + **7 处内联 StyleBox**（`GUI.tscn:19-33`、`SkillDisplay.tscn:7-13`、`Minimap.tscn:7-10`、`Player.tscn:25-37` 等）风格漂移；ProgressBar 全局亮红是隐藏炸弹 | 资源 | 收敛为主题变量+每组件状态集；内联样式抽回主题 |
| B9 | 字体 | `MainTheme.tres:115-119,135`（default rsans 18px outline 1px 黑） | — | 层级实测：64（MessageLabel space）/28（ContextLabel space **outline 2**）/24（Globe ChivoMono）/18（rsans 默认）/16（Buff/通知/词缀 space/ChivoMono） | 4 字体+5 字号无规范层级；16px 档偏小；outline 不一致；CJK overlay 经 c5-l1/c5-l21 mod（hint 保留，use_filter=false） | **B** | 按 1280×800 定字号 scale；统一 outline=1；16px→18px；长期收敛 2 套字体 |
| B10 | 渲染设置 | `project.binary`（已解码） | c5-l24 运行时 set_screen_stretch(STRETCH_MODE_2D, KEEP, 1280×800, 1.0) | 见 §D | 见 §D | — | 见 §D |

**HUD/UI 层 Top 5 根因**：
1. `GUI.tscn:144-149` + `MainTheme.tres:53-63` — 底部 600px 灰色九宫格调试框，无分区层级。
2. `Globe.tscn:15-24` — 256px 巨球+纯红+24px 数字压中心、零反馈。
3. `MainTheme.tres:136-145` — 按钮 pressed/disabled 无状态、无 Selected → "像默认 UI"。
4. `GUI.tscn:336-425` + `Minimap.tscn:16-56` — 区域名/等级/击杀/地图框/词缀三处散落、容器语言互不相干。
5. `StatusBar.tscn:41-48`（8×8）+ 全局 16×16 贴图 vs `MainTheme.tres:115-119` 18px 矢量中文 — 三套视觉年代并存。

---

## C. 资产分类汇总

| 分类 | 含义 | 世界层 | HUD/UI |
|---|---|---|---|
| A 程序绘制 | 可脚本层直接改 | 1（空 shader） | XP 条/小地图/词缀面板（StyleBoxFlat/_draw） |
| B 矢量 | 字体 | 0 | 字体系统（rsans/space/ChivoMono/monogram/stack_pixel） |
| C 贴图 | 低分辨率像素美术 | **7**（tileset/玩家/NPC/工作台/火把/Portal/阴影/Notice） | 血球/九宫格面板/按钮切片/全部图标/缓冲底纹 |
| D 未知/文本 | — | 1（世界标签 Label，可脚本改写） | — |

**HD Asset Replacement List（预登记，PHASE 6 正式化）**：tileset_factory、玩家七部件+shadow、statue/skeleton_warrior、bench 六帧+chest、brazier+smoke、portal、globe 双 PNG、ninepatch_panel/ninepatch_58(_focus)/stone_vines、sprites/skills/* 与 status_effects/*（16×16 全量）、sprites/uniques/*、buff_background、cursor。

---

## D. project.binary 实测值（全部解码）

| 键 | 值 |
|---|---|
| display/window/size/width / height | **1280 / 800** |
| display/window/size/fullscreen | **true** |
| display/window/stretch/mode | **键不存在**（默认 disabled；c5-l24 运行时补丁 STRETCH_MODE_2D KEEP） |
| display/window/stretch/aspect | "keep_height" |
| **rendering/2d/snapping/use_gpu_pixel_snap** | **true**（PHASE 1 A/B 候选：OFF） |
| rendering/2d/options/use_nvidia_rect_flicker_workaround | true |
| rendering/environment/default_clear_color | **Color(0.255,0.255,0.255,1) 中灰** |
| rendering/environment/default_environment | res://default_env.tres |
| gui/timers/tooltip_delay_sec | **0.0**（瞬现） |
| importer_defaults/texture | filter=false / mipmaps=false / repeat=0（**像素贴图风默认**） |
| display/mouse_cursor/custom_image | sprites/gui/cursor.png 64×64 hotspot(0,0) |

---

## E. 当时拟定的 3.5.3 PHASE 1 范围（历史，不要当当前任务）

> 2026-08-16 的 oracle 记录。下面条目是当时对 3.5.3 MOD 的设想，**不要**再按 CODE_PATCH/RESOURCE_PATCH 实施。Godot 4 迁移后这些问题要重新验证。

1. **TooltipBase.gd:17 定位 bug 修复**（CODE_PATCH，最先做）：`centered_position.x += position_offset.y` → `.x`。
2. **XP 条 StyleBox 精修**（GUI.tscn 内联，RESOURCE_PATCH）：fg/bg 色、圆角 4-6、边框；**保持 rect_min_size 高度 12 不变**（高度 16-20 属布局变更，推后）。
3. **ProgressBar 全局 fg `#FF0000` → 中性色**（MainTheme.tres:69-76，RESOURCE_PATCH）：盘点已做（仅 3 处 ProgressBar），designer 定中性色值；注意只影响未覆盖 fg 的实例。
4. **按钮 pressed/disabled 差异化**（MainTheme.tres，RESOURCE_PATCH）：先由 designer 定 StyleBoxFlat 方案与精确参数（StyleBoxTexture 无 color 属性，不可用）。Selected 态降级 PHASE 3。
5. **字体 outline 一致化**（ContextLabel 28px outline 2→1，改动面小才做；其余 16px→18px 推后 PHASE 4）。

**明确不移除/推后**：pixel snap（不可行，判死）、网格（PHASE 2，记录规格偏差）、default_clear_color（PHASE 2）、血球/底部 Dock/小地图模块（PHASE 2 Vertical Slice）、16×16 图标（PHASE 6）。

**行尾注意**：MainTheme.tres / GUI.tscn 为 LF；preimage=整文件 SHA；old_text 必须逐字节（含换行）精确复制。
