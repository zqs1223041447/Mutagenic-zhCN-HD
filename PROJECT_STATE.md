# Mutagenic 项目状态

**最后更新**: 2026-08-16 08:10

> 本文件 16:35 版本的核心结论（「构建因缺少脚本加密而损坏」）已被证据推翻。
> 真正的启动失败根因是嵌入式 PCK 的两处偏移字段错误，见下文「本轮修复的根因」。

## 当前状态

**当前阶段**: `PHASE_6_INCREMENTAL_MOD_LOCALIZATION_INTEGRATION`

### 当前证据交接：zh_CN Core Playable v8 / v8.1 交付（2026-08-16 08:10 +08:00）

- **目标**: 按汉化.md 第八节剩余优先级继续扩大汉化——帮助/教程/剧情/lore/机制参考文本。
- **v8（E52611AE...）**: +66 DISPLAY_SAFE 单元——L26（基因提示/解锁通知）、L27（7 个教程弹窗含 BBCode）、L28（主菜单引用/按键/设置 15 项/角色选择/逃脱菜单/赞助商店/物品标签）。
- **v8.1（033A34F7...）**: 完成**整个帮助参考系统的中文翻译**——L30（默认操作、挑战天梯、工艺选项）+ L31（突变树 ~7300 字符、异常状态 ~4200 字符，含装备/伤害类型/属性/恩惠/触发技能/护甲/闪避/层层防御/增更多/独特修饰/伤害转化/持续伤害/异常堆积等完整机制说明）。
- **技术要点**: Help.tscn/CraftingHelp.tscn 使用 **CRLF 行尾**，patch old_text 必须以二进制精确提取（含 `\r\n` 与末尾换行）；已建立字节级提取+校验流程避免 LF/CRLF 不匹配。
- **机器 Gate**: 全 PASS（resolve 1545 / apply / compile 57 / delta 0 / pck 3744 / roundtrip / boot / semantic——默认操作/天赋树/异常状态/挑战天梯/工艺选项均已嵌入确认）。
- **交付物**: `09_output/zh_CN_Core_Playable_v8.1/Mutagenic_zhCN_v8.1.exe`（SHA-256 `033A34F76E8ED42E2F75E996F2DEBCDA283682EC95E1C55527131271118CAD84`，需同目录 `steam_api64.dll` `DCFAA13A...`）；存档工具同步。
- **卸载验证**: `00_original`（`C7B5D5A5...`）/`03_raw`（3744）/`04_recovered` 未变。
- **下一步**: 剩余低频/边缘文本（help tip 残余、编辑器占位符按设计保留）→ 人工检查点 → 技能与 Combat Modifier 开发作为之后单独任务。

### 当前证据交接：zh_CN Core Playable v7 交付（2026-08-15 20:40 +08:00）

- **背景**: 用户口述"文字在全屏下显示不清晰，在非全屏下显示清晰无误"（截图因模型限制无法读取）。结合代码诊断：游戏设计分辨率 1280x800、显示器 2560x1440；`project.binary` 中**无 `window/stretch/mode`**（Godot 3.5 默认 `disabled`）→ 全屏时 1280x800 画面直接像素拉伸到 2560x1440（宽 2.0x/高 1.8x 非整数倍）→ 文字模糊；窗口 1:1 原生渲染 → 清晰。
- **研究**: @librarian 确认 Godot 3.5 API——正确枚举为 `STRETCH_MODE_2D`（值 1，非 4.x 的 CANVAS_ITEMS）；autoload `_ready()` 时序上晚于引擎自身 `set_screen_stretch`，运行时覆盖有效；`STRETCH_MODE_2D` 会启用**字体过采样**（`_update_font_oversampling(screen/viewport)`），DynamicFont 按实际屏幕尺寸重新栅格化，全屏放大保持锐利。
- **修复**: 新增 `mods/c5-l24-stretch-mode-2d`（CODE_PATCH，preimage `0976E0F4...`）——在 `GameState._ready()` 中插入 `get_tree().set_screen_stretch(SceneTree.STRETCH_MODE_2D, SceneTree.STRETCH_ASPECT_KEEP, Vector2(1280, 800), 1.0)`。
- **交付物**: `09_output/zh_CN_Core_Playable_v7/Mutagenic_zhCN_v7.exe`（SHA-256 `8196ECBAE110F7A7BD3F79FA9DD6AFE7A5D9F0B987B486E58555A751BB326CBF`，需同目录 `steam_api64.dll` `DCFAA13A...`）；存档管理工具同步复制。
- **机器 Gate**: resolve(1469 patches)/apply/compile(57，含 GameState.gd)/delta(0 unexpected)/pck(3744)/roundtrip(3744=3744)/boot(真实窗口, 3 boot markers)/semantic 全 PASS；GDRE 恢复确认 `set_screen_stretch(STRETCH_MODE_2D,...)` 已嵌入、`USE_STEAM=false` 保留、Deng hint 字体保留。
- **卸载验证**: `00_original`（`C7B5D5A5...`）/`03_raw`（3744）/`04_recovered` 未变。
- **下一步**: 用户验证全屏 vs 窗口文字锐利度 → 若仍模糊，备选方案（按 @librarian）：开 `display/window/dpi/allow_hidpi`、或关闭字体过采样绕过 Godot 3.x #47957 已知 bug → 继续扩大汉化（lore/剧情/边缘文本）；技能与 Combat Modifier 开发是之后单独任务。

### 当前证据交接：zh_CN Core Playable v6 交付（2026-08-15 18:20 +08:00）

- **背景**: 用户反馈 v5 中文"略微清晰但仍不够清晰"。根因定位：`merge_fonts2.py` 用 pen 重建字形轮廓，**丢弃 TrueType hinting 指令**；Godot 3.5 DynamicFont 默认启用 hinting，小字号（18px）中文无 hint 指令时网格拟合差。
- **修复**: 新增 `scripts/merge_fonts3_hinted.py`——当 CJK 源与目标 upem 相同（Deng 2048 == rsans 2048）时**深拷贝 glyph 条目（含 program/hinting 指令）而非 pen 重建**，轮廓无需变换，hint 完整保留。rsans 27763 个 CJK 字形保留 hint（抽样 12 字 8 个带 hint 字节码）。
- **交付物**: `09_output/zh_CN_Core_Playable_v6/Mutagenic_zhCN_v6.exe`（SHA-256 `756AA5D85BA400D0088A1969692EDFDEB8EC15F01BEAC95201BDB50FF195A376`，需同目录 `steam_api64.dll` `DCFAA13A...`）；存档管理工具同步复制。
- **机器 Gate**: resolve(1468)/apply/compile(56)/delta(0 unexpected)/pck(3744)/boot(真实窗口, 3 boot markers)/semantic 全 PASS；EXE rsans SHA `EFB56C48...`（hinted 版逐字节匹配）、`use_filter=false`、`USE_STEAM=false` 已确认。
- **卸载验证**: `00_original`/`03_raw`/`04_recovered` 未变。
- **下一步**: 用户验证 18px 中文锐利度 → 继续扩大汉化（lore/剧情/边缘文本）；技能与 Combat Modifier 开发是之后单独任务。

### 当前证据交接：zh_CN Core Playable v5 交付（2026-08-15 17:40 +08:00）

- **目标**: 用户反馈两项 P0——(1) 中文字体显示模糊/像素风（数字清晰中文糊），(2) 存档导入/导出功能。
- **字体修复（P0）**: 根因组合——
  1. CJK 源 `NotoSansSC-VF.ttf`（upem=1000）合并进 rsans（upem=2048）需 2.048x 缩放，且 merge 用 pen 重建轮廓丢弃 hinting；渲染对比确认 Deng 版中文更锐利。
  2. `Themes/InGameText.tres` 显式 `use_filter = true`（MainTheme/PickupTheme 未设置），Godot 对小字号 CJK 字形做线性过滤导致糊化；数字用 ChivoMono 24px/space 28px 清晰。
  - **修复**: CJK 源换 `C:\Windows\Fonts\Deng.ttf`（等线，upem=2048 与 rsans 精确匹配，scale=1.0）重新合并 rsans/space/ChivoMono；`c5-l21-font-clear-zhcn` 增加 `InGameText.tres` `use_filter=true→false` patch。渲染验证（PIL FreeType 18px）：Deng 版中文与数字清晰度一致，Noto 版中文笔画密集处柔和模糊。
  - **证据**: EXE 提取 `Fonts/rsans.ttf` SHA `1AE4B055...`（Deng 版完全匹配）、`use_filter = false` 已嵌入、`Constants.USE_STEAM=false`（存档修复保留）。
- **存档导入/导出（P0）**: 交付 `09_output/zh_CN_Core_Playable_v5/存档管理工具.ps1`——中文菜单式工具，功能：导出存档到 `saves_backup\`、从备份导入、查看状态、打开存档目录。原理：直接复制 `%APPDATA%\Godot\app_userdata\Mutagenic\_0_6_0.dat`（本地存档，USE_STEAM=false 分支），不改游戏本体/存档格式。端到端验证 PASS：真实存档导出→删除→导入后 SHA 完全一致（`B233E45B...`）。
- **交付物**: `09_output/zh_CN_Core_Playable_v5/Mutagenic_zhCN_v5.exe`（SHA-256 `138FBF59FB06DF0588295FB2745DD618A9422500CFF44B726F354E5281EE106B`，需同目录 `steam_api64.dll` `DCFAA13A...`）。
- **机器 Gate**: resolve(1468 patches)/apply/compile(56)/delta(0 unexpected)/pck(3744)/roundtrip(3744=3744)/boot(真实窗口无 ALERT, 3 boot markers)/semantic(USE_STEAM=false + use_filter=false + Deng rsans) 全 PASS。
- **卸载验证**: `00_original/Mutagenic.exe` SHA 仍为 `C7B5D5A5...`、`03_raw` 3744 文件、`04_recovered` 纯净（`USE_STEAM=true`）。卸载 = 不再运行 modded EXE。
- **存档备注**: 角色重开后存在（v4 起有效）；**创建后立即删除角色再重启可能不存在的边缘情况已记录为低优先级后续项**（status.json known_issues P3）。
- **下一步**: 人工检查 v5（重点: 中文字体清晰度对比 + 角色持久化）→ 继续扩大汉化（lore/剧情/边缘文本）；技能与 Combat Modifier 开发是之后单独任务。

### 当前证据交接：zh_CN Core Playable v4 交付（2026-08-15 14:55 +08:00）

- **目标**: 三项并行任务——(A) 存档修复（创建角色后重开无人物），(B) 字体清晰度修复（中文字体像素风/模糊），(C) 继续汉化。
- **交付物**:
  - `09_output/zh_CN_Core_Playable_v4/Mutagenic_zhCN_v4.exe`（SHA-256 `0E5FE326F610973AF0ADFE8CF0B18BD3919AEF1A34A5CFE937D644592F1047C5`，需同目录 `steam_api64.dll` SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`）
  - 聚合 MOD: `mods/c5-l21-zhcn-core-playable-v4/mod.json`（依赖 = 完整 v3 链 20 MOD + `c5-l21-font-clear-zhcn` + `p7-fix-persistence`，1467 patches）
- **存档修复（Lane A）**: 根因 = v3 链未含 P7-FIX，`Constants.USE_STEAM` 仍为 `true` → 非 Steam 启动下存档走 Steam API 静默失败。v4 合入 `p7-fix-persistence`（`USE_STEAM=false` → 本地 `user://_0_6_0.dat` File 分支）。机器证据: GDRE 从最终 EXE 恢复 `Constants.gd` 确认 `var USE_STEAM = false`; 隔离 APPDATA 首次启动创建 `_0_6_0.dat`（729B），二次启动重新加载并写回（SHA `3589A399`→`ADB77315`，mtime 更新）——本地持久化闭环机器验证 PASS。
- **字体修复（B）**: 根因 = CJK 源为 `fusion-pixel-12px`（12px 像素字体），放大后模糊/锯齿。方案: 以系统 `NotoSansSC-VF.ttf`（思源黑体，OFL）为 CJK 源，`scripts/merge_fonts2.py` 重新合并（保留拉丁/图标字形不动）; c5-l1 的 rsans.ttf 资产更新为 Noto 版（10.7MB），新增 `c5-l21-font-clear-zhcn` 覆盖 `space.ttf`（GUI/通知/小地图）与 `ChivoMono-VariableFont_wght.ttf`（血量球/状态条）——此前这两个字体从未合并 CJK。pack/EXE 中字体字节与 Noto 合并版 SHA 逐字节一致。
- **继续汉化（C）**: explorer 后台调查被系统中断两次；剩余文本（lore/剧情/边缘）清单待下轮用轻量方式补做，不阻塞 v4 交付。
- **机器 Gate**: resolve/apply/compile(56)/delta(无意外路径)/pck(3744)/roundtrip(3744=3744)/listing(3744)/boot(真实窗口无 ALERT)/semantic(USE_STEAM=false + CJK 串恢复)/persistence_machine 全 PASS。
- **卸载验证**: `00_original/Mutagenic.exe` SHA 仍为 `C7B5D5A5...`、`03_raw` 3744 文件、`04_recovered` 纯净（`USE_STEAM=true`）。卸载 = 不再运行 modded EXE。
- **存档兼容**: 显示值汉化 + 本地存档分支（`USE_STEAM=false` 已由 P7-FIX 人工验证可存档重启保留角色）；v4 的字符重启可见性仍需一次性人工确认。
- **人工检查点**: 待建 `10_logs/C5-L21-core-playable-v4-20260815/human_checkpoint.json`（active_blocker=false）。
- **下一步**: 人工检查 v4（重点: 真实 UI 创建角色 → 关闭 → 重开角色存在 + 中文字体清晰度）→ 继续扩大汉化（lore/剧情/边缘文本）；技能与 Combat Modifier 开发是之后单独任务。

### 当前证据交接：zh_CN Core Playable v3 聚合交付（2026-08-15 13:00 +08:00）

- **续接确认（fork #3, 13:35）**：本会话从中断点（apply 后）核验全部机器证据——compile(56) / pack(3744) / delta(PASS, 无意外路径) / PCK / roundtrip(3744/3744) / listing / boot(PASS, 真实窗口无 ALERT) / semantic(PASS, 14 抽样含中文且结构 ID 英文保留) 均与 `10_logs/C5-L20-core-playable-v3-20260815/build.json` 一致；`09_output/zh_CN_Core_Playable_v3/` 已就绪（EXE SHA `0EAD58D1...D5EAE`、DLL `DCFAA13A...`）；`00_original` 未变（`C7B5D5A5...`）、`03_raw` 3744 文件、`04_recovered` 纯净（`USE_STEAM=true`）；`10_logs/status.json` 已更新（updated_at 13:35，新增 `zhcn_core_playable_v3` baseline 与 C5-L16..L20 gates=PASS）。

- **目标**: 按 `汉化.md` 第八节优先级将汉化扩大至「核心游玩内容」的怪物/区域/状态/装备/独特物品文本，交付可安装/可游玩/可卸载的中文版本 v3。
- **交付物**:
  - `09_output/zh_CN_Core_Playable_v3/Mutagenic_zhCN_v3.exe`（SHA-256 `0EAD58D1BD0B36BC0916C58154E1F8A44D078BEF27FEBB1C55D0F7A83F2D5EAE`，需同目录 `steam_api64.dll` SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`）
  - 聚合 MOD: `mods/c5-l20-zhcn-core-playable-v3/mod.json`（依赖链 17 个 manifest，1466 patches）
  - 4 个新切片: `mods/c5-l16-zones-monsters-ui-zhcn/`（65 patches，区域/怪物/地图 Mod/小地图/起始构筑）、`mods/c5-l17-status-effects-zhcn/`（50 patches，48 个状态效果场景）、`mods/c5-l18-equipment-names-zhcn/`（151 patches，`Genes.gd` 装备名 + `ItemNameGenerator.gd` 词缀）、`mods/c5-l19-unique-items-zhcn/`（46 patches，独特物品池）；C5-L10(全技能)…C5-L14(静态场景)此前已 PASS
- **新增覆盖**: 区域名（`Levels.gd`）、怪物名与数值（`MonsterStats.gd`）、地图 Mod 文本、小地图提示、起始构筑、状态效果（流血/灼烧/诅咒/祝福/基石/拾取物等 48 场景）、装备基底类型（近战武器/护甲盾等）与姓名/词缀、独特物品名。
- **机器 Gate**：C5-L16/L17/L18/L19 各自 resolve/apply/compile/pack/delta/pck/roundtrip/listing/boot 全 PASS；聚合 C5-L20 同样全 PASS（1466 patches 解析、56 脚本编译加密、delta 精确无意外路径、3744/3744 roundtrip、GDRE listing 3744、boot 真实窗口无 ALERT、语义确认 14 抽样 PASS）。
- **语义确认 PASS**（`semantic_confirmation.json`）：GDRE 从最终 EXE 恢复 14 个目标文件（6 状态场景 .tscn + 8 脚本 .gd），中文显示串全部存在；结构 key 英文保留（`"cave"`/`"lightning"`/`BaseType.MELEE_WEAPON`/`"expansion_charm"`/`Target.MOB`/`health_max` 等）。
- **构建说明**：L20 resolve/apply 在 fork #3 已完成且证据保留；本次从中断处继续 compile（对 `compile_manifest.json` 去重为 56 unique .gd，避免 1282 次重复 GDRE spawn）、pack、normalize、embed（从 `00_original/Mutagenic.exe` 新鲜嵌入）、roundtrip、listing、boot、semantic。
- **卸载验证**：卸载 = 不再运行 modded EXE，原版直接可用；`00_original/Mutagenic.exe` SHA 仍为 `C7B5D5A5...`、`03_raw` 仍 3744 文件。
- **存档兼容**：静态分析确认汉化只改显示值；存档标识符不变（结构 ID/区 key/怪物 key/枚举保持英文）。运行时存档兼容性需一次性 disposable-save 人工测试（未授权，未执行）。
- **人工检查点**：`10_logs/C5-L20-core-playable-v3-20260815/HUMAN_CHECK_REQUEST.md`（`HUMAN_REQUIRED`，active_blocker=false，10 项 SHA 绑定检查清单）。
- **覆盖率**：累计约 1878 个 DISPLAY_SAFE 文本单元（v2 1154 + v3 新增约 312 unique），覆盖核心可玩流程 + 全技能/全支撑/全天赋/全属性/全标签/动态 UI/静态场景/区域/怪物/状态/装备/独特物品；剩余低频文本（lore、边缘文本等）按 `汉化.md` 第八节优先级继续。
- **下一步**：人工检查候选 → 继续扩大汉化（剧情/lore、剩余边缘文本）；技能与 Combat Modifier 开发是之后单独任务。

### 当前证据交接:zh_CN Core Playable v2 聚合交付(2026-08-15 09:00 +08:00)

- **目标**:按 `汉化.md` 第八节优先级扩大汉化至「核心游玩内容」全量覆盖,并交付可安装/可游玩/可卸载的中文版本 v2。
- **交付物**:
  - `09_output/zh_CN_Core_Playable_v2/Mutagenic_zhCN_v2.exe`(SHA-256 `5226555657A09E4BD1CCA0A75C1161BA27F307D22EDD961B90F64AB6F72BA728`,需同目录 `steam_api64.dll` SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`)
  - 聚合 MOD: `mods/c5-l15-zhcn-core-playable-v2/mod.json`(依赖链 L1-L7 + L10-L14,1154 patches)
  - 4 个新切片: `mods/c5-l11-passive-tree-zhcn/`(502 patches)、`mods/c5-l12-stats-tags-zhcn/`(189 patches)、`mods/c5-l13-dynamic-ui-zhcn/`(83 patches)、`mods/c5-l14-static-scenes-zhcn/`(74 patches);C5-L10(226 patches,全技能+全支撑)此前已 PASS
- **覆盖**:主菜单/角色选择/职业对话框/设置/按键/暂停菜单/死亡界面/天赋弹窗/HUD/技能选择家族/关卡加载/拾取物/排行榜(L1-L6)+ 4 职业/8 专精(L7)+ **全部 53 技能 + 60 支撑**(L10)+ **326 天赋节点 + 88 基石**(L11)+ **149 属性 + 24 技能标签 + 前缀**(L12)+ **26 脚本动态 UI 字符串**(L13)+ **31 场景静态文本**(L14)。中文字体 `Fonts/rsans.ttf`(CJK 覆盖)。
- **机器 Gate**:C5-L10/L11/L12/L13/L14 各自 resolve/apply/compile/pack/delta/pck/roundtrip/listing/boot 全 PASS;聚合 C5-L15 同样全 PASS(1154 patches 应用、1020 编译条目、delta 精确无意外路径、3744/3744 roundtrip、GDRE listing 3744、boot 真实窗口无 ALERT)。
- **语义确认 PASS**:GDRE 从最终 EXE 恢复 11 个关键脚本,中文显示串全部存在,内部标识符(dict key/enum tag/stat key/节点路径/变量/%s %d 占位符)全部保留英文未翻译。
- **修复记录**:L12 manifest 两处重复 patch 缺陷(StatsInfo.gd 955/1011 用 4 行上下文消歧;EscapeMenu.gd 4 对合并为 occ=2)与 L13 同步;`compile_declared_scripts.py` 修复纯资源切片空编译集判定(empty_ok)。
- **卸载验证**:卸载 = 不再运行 modded EXE,原版直接可用;`00_original/Mutagenic.exe` SHA 仍为 `C7B5D5A5...`、`03_raw` 仍 3744 文件、`04_recovered` 抽样 30/30 哈希一致(Constants.gd 纯净 USE_STEAM=true 无注入)。
- **存档兼容**:静态分析确认汉化只改显示值;存档标识符不变。运行时存档兼容性需一次性 disposable-save 人工测试(未授权,未执行)。
- **人工检查点**:`10_logs/C5-L15-core-playable-v2-20260814/` 待建 HUMAN_CHECK_REQUEST(active_blocker=false)。
- **覆盖率**:累计约 1154 个 DISPLAY_SAFE 文本单元,覆盖核心可玩流程 + 全技能/全支撑/全天赋/全属性/全标签/动态 UI/静态场景;剩余低频文本(怪物名/状态名/lore 等)按 `汉化.md` 第八节优先级继续。
- **下一步**:人工检查候选 → 继续扩大汉化(怪物/状态相关文本、剧情/lore、边缘文本);技能与 Combat Modifier 开发是之后单独任务。

### 当前证据交接:zh_CN Core Playable PoC 交付(2026-08-14 21:00 +08:00)

- **目标**:按 `汉化.md` 交付首个可安装/可游玩/可卸载的中文版本(Core Playable PoC)。
- **交付物**:
  - `09_output/zh_CN_Core_Playable/Mutagenic_zhCN.exe`(SHA-256 `AD3D216593547491C0D22D085E1EFF8EEA7C1D1FA1246CF3721854BD9C20FE4C`,需同目录 `steam_api64.dll`)
  - 4 个新 MOD slice: `mods/c5-l6-localization-static-ui/`(47 单元)、`mods/c5-l7-playable-classes-zhcn/`(24 单元)、`mods/c5-l8-skills-zhcn/`(16 单元)、`mods/c5-l9-zhcn-core-playable/`(整合聚合)
  - 术语表: `docs/zh_CN_glossary.md`
- **覆盖**:累计 100 个 DISPLAY_SAFE 文本单元 = 主菜单/角色选择/职业对话框/设置/按键(C5-L1..L5)+ 暂停菜单/死亡界面/天赋弹窗/HUD 静态标签/技能选择家族/关卡加载/拾取物/排行榜(C5-L6)+ 4 职业/8 专精名称与描述(C5-L7)+ 8 技能名称与描述含数值(25%/200%/50%)(C5-L8)。中文字体 `Fonts/rsans.ttf`(CJK 310 字符全覆盖)。
- **机器 Gate**:C5-L6/C5-L7/C5-L8/C5-L9 各自 resolve/apply/compile/pack/embed/roundtrip/embedded text/semantic(GDRE 解密恢复)/font/boot 全 PASS;delta 精确(23 唯一路径,无意外);存档相关路径(GameState/Constants/save)未触碰;内部 ID(skill_id/class key)未修改。
- **卸载验证 PASS**:`00_original/Mutagenic.exe` SHA 仍为 `C7B5D5A5...`、`03_raw` 仍 3744 文件、`04_recovered` 纯净(`USE_STEAM=true`);卸载 = 不再运行 modded EXE,原版直接可用,无需恢复文件。
- **存档兼容**:静态分析确认汉化只改显示值;存档标识符不变。运行时存档兼容性需一次性 disposable-save 人工测试(未授权,未执行)。
- **人工检查点**:`10_logs/C5-L9-zhcn-core-playable-20260814/HUMAN_CHECK_REQUEST.md`,状态 `HUMAN_REQUIRED`(active_blocker=false),14 项 SHA 绑定检查清单。
- **覆盖率**:100 单元 / 487 unique display pairs(14% unique,按 occurrence 9.7%)——PoC 阶段覆盖核心可玩流程,剩余文本按 `汉化.md` 第八节优先级继续。
- **下一步**:人工检查候选 → 继续扩大汉化(全部技能/专精描述/装备/天赋/动态字符串);技能与 Combat Modifier 开发是之后单独任务。

### 当前证据交接:源码参考工程交付(2026-08-14 17:25 +08:00)

- **需求(方案 A 已批准)**:将游戏拆解为源码样式参考工程,方便后续扩展/维护/二次开发;不改变生产构建管线(遵守 AGENTS.md §5.3/§13/§28)。
- **纯净性验证**:`04_recovered/` 全部 **5058/5058 文件**与 `manifests/recovered_clean_manifest.json` 哈希一致(OK=5058 MISMATCH=0 MISSING=0);`Globals/Constants.gd` 确认 `USE_STEAM = true` 无污染、无 `_ready()` 注入。参考源完全可信。
- **交付物**:
  - `docs/ai/source_index.json` —— 机器索引:525 个 .gd 的 relpath/extends/funcs/signals/emits/行数/SHA-256,生成脚本 `scripts/recover/extract_source_index.py`(确定性、可复现)。
  - `docs/ai/source-map.md` —— 逐脚本职责表:525 行(Globals 185 / Scenes 战斗 225 / Scenes UI·弹窗·玩家 101 / addons 14),职责基于函数名/信号/extends 推断(INFERENCE_HIGH),路径集合与 source_index.json **525/525 完全一致**。
  - `docs/ai/scene-resource-map.md` —— 场景/资源/职业/技能/输入/存档引用图,基于 `05_schema/game_schema.json`(FACT 数据)。
  - `docs/ai/secondary-development-guide.md` —— 二次开发指引:心智模型、mod 工作流、构建链、禁止项、扩展场景速查。
- **机器证据**:source-map 与索引路径一致性 525/525(无缺失、无多余);场景图数据直接取自 schema(FACT)。
- **下一步**:用户可基于参考工程开展二次开发(通过声明式 mod 流程);不翻译额外标签(需 scope);不修改共享 `_0_6_0.dat`;Quit 观察保留在独立基线轨迹。

### 当前证据交接：P7-FIX 本地持久化修复（2026-08-14 15:30-16:05 +08:00）

- **用户目标范围**：自我研究/本地游玩（LOCAL_PLAY_ONLY）。Steam 验证、Steam 原版行为对齐**均不是目标**。因此修复采用最简方案：`Constants.USE_STEAM` 由 `true` 改为 `false`，保存/加载/退出全部走既有本地 File 分支（`user://_0_6_0.dat`）。
- **根因**：`GameState.gd` 在 `USE_STEAM=true` 时保存走 `Steam.fileWriteAsync()`（非 Steam 启动静默失败、无本地文件）、加载走 `Steam.fileExists()`（false → "No save file found" → 角色永不显示）、退出依赖 `_on_save()` 回调（永不触发 → Quit 无效）。本地 File 分支代码已存在且被外部 729B `_0_6_0.dat`（checksum/stamp 完整）证实可用。
- **manifest**：`mods/p7-fix-persistence/mod.json`，SHA-256 `8F1E674F499C3902C9DE2EA5B7097EFCDFA9B983300782A171A75D2D735017CA`；单行 CODE_PATCH（preimage `06C72082...DCF44`）。
- **静态可达性**：`USE_STEAM=false` 后 7 个引用文件的全部 Steam API 调用点不可达（`Globals._initialize_Steam` 不被 `_ready` 调用，Achievements/Leaderboard/MTXManager 的 initialize 不执行，商店 UI 有 `not USE_STEAM` 守卫隐藏）。
- **候选**：`10_logs/P7-fix-persistence-20260814/p7_fix_persistence.exe`（SHA-256 `83970CCF4B258D5C6370925BE7DEB574EC601B71D4A16F8D1FD2FBCFB7D3C495`，DLL `DCFAA13A...E67799`）；runtime 目录 `runtime_candidate/Mutagenic.exe` 同 SHA。
- **机器 Gate 全部 PASS**：patch preimage、单脚本编译加密、精确两路径 delta（`Globals/Constants.gde` + `.gd.remap`）、PCK 3744 条目、EXE 结构、完整复提取对比（3744/3744，sidecar 排除）、GDRE 从最终 EXE 恢复 Constants.gd 确认 `var USE_STEAM = false`、boot（真实窗口无 ALERT）。
- **运行时本地持久化闭环（机器证据）**：在隔离 APPDATA（`10_logs/P7-fix-persistence-20260814/isolated_appdata`）中，候选自身创建 `user://_0_6_0.dat`（729B，JSON+stamp 有效，SHA `2FE3636B...BF980`）；第二次启动后该文件被重新加载并写回（SHA 变 `0744FB7A...D6A74`、mtime 更新）——证明 `USE_STEAM=false` 时本地保存→加载→保存管线真实执行。证据：`machine_evidence.json`（SHA `155C570C...E1AD`）。
- **日志归属说明**：共享日志目录 15:55:14 的 godot.log 含 Steam 初始化行，系外部 F 盘进程同秒写入的污染；GDScript `print()` 不进本构建日志文件（已知限制），隔离 APPDATA 运行与窗口检查才是该候选的权威运行时证据。共享 `_0_6_0.dat` 在 15:57:23 被外部活动再次写入（SHA 变为 `9AC3EED3...AFFD`，不含协议角色），保持 UNBOUND 观察，未读取内容、未修改。
- **人工检查点**：`PASS`（2026-08-14 16:07 +08:00，观察者=用户）：在 `runtime_candidate` 中真实 UI 创建角色 `asdf` → 关闭游戏 → 重新打开 → **角色存在且可用**。存档 `C:/Users/ZQS/AppData/Roaming/Godot/app_userdata/Mutagenic/_0_6_0.dat`（2783B，SHA `A2DD4595...9844E99`）。**S3 持久化检查点已闭合**，实验状态 `COMPLETED`（`experiment.json`：status=COMPLETED, runtime_gate=PASS, human_checkpoint=PASS）。
- **下一步**：决定 P7-FIX 候选是否成为本地游玩的新可信基线；用户已提出后续工程需求「拆解为源码样式」用于扩展/维护/二次开发——**按用户要求，需先报告该需求与 AGENTS.md 的一致性再执行**（报告见当前交接段之后的「源码拆解需求一致性报告」待补章节）；不翻译额外标签（需明确 scope）；不修改共享目录外部 `_0_6_0.dat`；Quit 观察保留在独立基线轨迹。

**构建管线**: CLEAN NOOP、C0-C4 能力证据均有当前证据；C3 历史 retry 因使用脏 `06_worktree` 不作为输入，但其最终 EXE 与从 `03_raw` 新建的 clean C3 EXE 逐字节相同，截图已通过 SHA 绑定审查，C3 capability 恢复为 `PASS`。

**中文化进度**: C5-L1 受控主菜单切片与 C5-L2 角色选择切片均已通过机器 Gate 和用户检查点。C5-L3、C5-L4 与 C5-L5 的机器 Gate 已通过：C5-L3 新增角色创建/切换对话框 4 个 DISPLAY_SAFE 单元，C5-L4 新增 Settings 对话框导航 3 个 DISPLAY_SAFE 单元，C5-L5 新增 Keybinds 对话框 2 个 DISPLAY_SAFE 单元；均从 `03_raw` + 新鲜 `00_original` 构建，C5-L5 实际物理 delta 精确为 7 个路径，PCK/EXE 结构、完整复提取、嵌入文本、字体覆盖、启动均通过，且未修改脚本。C5-L3/C5-L4/C5-L5 人工检查点均为 `HUMAN_REQUIRED` 且 `active_blocker=false`，仅作为阶段记录点保留，不作为后续机器工作阻塞项。Phase 7 持久化轨迹已建立：静态契约和新增只读 preflight 均为 `PASS`；C5-L2 的一次性角色数据持久化授权已记录。ORIGINAL v2 按同一 SHA/DLL 路径重启后角色列表为空；CLEAN NOOP v3 用户报告 `Quit` 无效；本轮不再把 Quit 作为目标。C5-L2 当前按授权测试固定角色 `P7_ORIGINAL_20260814` 的创建、等待保存防抖、关闭/重开和角色可见性。

**当前候选**: `10_logs/C5-L2-character-select-20260814/c5_l2_character_select_normalized.exe`（需同目录 `steam_api64.dll`）；C5-L2 是当前最近一个已关闭的可信中文化里程碑。

**当前候选 SHA-256**: `4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3`

**当前机器候选**: `10_logs/C5-L3-character-class-dialogs-20260814/c5_l3_character_class_dialogs_normalized.exe`（需同目录 `steam_api64.dll`）。

**当前机器候选 SHA-256**: `B8564289CE2DEC95709F4230C558D7D56F22DA8E1C7C5D256C68331915EAB02A`

**上一机器候选**: `10_logs/C5-L4-settings-dialog-20260814/c5_l4_settings_dialog_normalized.exe`（需同目录 `steam_api64.dll`）。

**上一机器候选 SHA-256**: `8563851B812A2E1AA8C86DCA0ADB3A89CD060983249BD2446C727DAA7A475397`

**当前最新机器候选**: `10_logs/C5-L5-keybinds-dialog-20260814/c5_l5_keybinds_dialog_normalized.exe`（需同目录 `steam_api64.dll`）。

**当前最新机器候选 SHA-256**: `F1DAE1C7EAB8784DA44C14C06717C38E53709A1D95A49F185CE0D300A7C8E90E`

**当前人工动作**: C5-L1 与 C5-L2 人工检查均已完成并按候选 SHA 绑定记录；C5-L2 结果见 `10_logs/C5-L2-character-select-20260814/human_visual_result_c5_l2_v1.json`。C5-L3 v3 已按 SHA 绑定记录用户报告的 `Quit` 失败和角色缺失；C5-L4 仍在队列。C5-L5 候选 `F1DAE1C7EAB8784DA44C14C06717C38E53709A1D95A49F185CE0D300A7C8E90E` 已按 SHA 校验并启动人工会话（PID `17532`，窗口 `Mutagenic`，响应正常）；新截图已绑定到该候选，见 `10_logs/C5-L5-keybinds-dialog-20260814/human_checkpoint.json`。这些均是 `HUMAN_REQUIRED` checkpoint，不因其未完成而暂停独立的机器 Gate。P7 ORIGINAL v2 记录见 `10_logs/P7-persistence-track-20260814/runs/P7-authorized-original-v2/human_checkpoint_relaunch_v2.json`：候选 SHA `C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209`，截图 SHA `DCFF676223BDF99FE145DA4B6B91540D8CADE574AF3F3F1D726162CCEB9BD2D1`；角色 `P7_ORIGINAL_20260814` 未显示，用户报告 `Quit` 无法使用，结果为 `PARTIAL/HUMAN_REQUIRED`。该记录不证明保存曾成功，也不证明本地化根因。

**当前机器 Gate**: `ENVIRONMENT/FINGERPRINT/RAW_EXTRACTION/RECOVERY/SCRIPT_CRYPTO_KNOWLEDGE/CLEAN_NOOP/C0/C1/C2/C3/C4/SCHEMA = PASS`；`LOCALIZATION = IN_PROGRESS`（`C5-L1 = PASS`，`C5-L2 = PASS`，`C5-L3 machine = PASS`，`C5-L3 human checkpoint = HUMAN_REQUIRED`，`C5-L4 machine = PASS`，`C5-L4 human checkpoint = HUMAN_REQUIRED`，`C5-L5 machine = PASS`，`C5-L5 human checkpoint = HUMAN_REQUIRED`）；`PERSISTENCE_TRACK = IN_PROGRESS`（静态契约/只读 preflight `PASS`，C5-L2 存档授权已记录，当前创建/保存/重启证据待人工完成；Quit 结果单独保留，不作为本轮目标）；`RELEASE = NOT_STARTED`。`LOCALIZATION` 仍是 `IN_PROGRESS`，因为已通过的只是受控切片。

**可信状态源**: `10_logs/status.json`。本文件后续历史章节可能保留旧阶段叙述；当与 `status.json` 或最新证据冲突时，以当前证据为准，并在交接摘要中明确冲突。

### 当前证据交接：CLEAN NOOP Quit 人工复查（2026-08-14 11:35 +08:00）

- `10_logs/P7-persistence-track-20260814/preflight_after_original_v2.json` 为 `PASS`，SHA-256 `E307A35DA9EC74C882E912FCA73922E8EB9874CFEA060EAB22356323971D3793`。
- 该 preflight 重新确认 ORIGINAL、CLEAN NOOP、C5-L2 的 EXE/DLL SHA，`00_original` 与 `03_raw` 未变化；当前无 `Mutagenic` 进程、无匹配本地 save 文件，未读取 Steam 状态，也未执行存档变更。
- `authorization_granted_original_v2.json` 的授权对象是 `candidate_id=ORIGINAL`；不能推导出 CLEAN NOOP/C5-L2 的存档创建授权。下一步必须取得明确的候选范围授权，或保持在非变更检查范围内。
- `runs/P7-authorized-clean-noop-20260814/session_launch_no_save_v2.json` 记录 CLEAN NOOP 的 responding `Mutagenic` 窗口（PID `26432`），EXE SHA `94A53EF47AC49CF2F13157905387932BB517F648A15B7A0200B098237F0015DA`，DLL SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`；本次只允许英文页面和 `Quit` 观察，不允许创建角色或写存档。
- `quit_static_hypothesis_v2.json` 为只读 `INFERENCE_HIGH`：源码显示 `Quit` 依赖五秒保存防抖、Steam 异步写入回调和最终退出通知；这仍不是根因结论，必须以 ORIGINAL/CLEAN NOOP 的运行时对照区分基线行为。
- `runs/P7-authorized-clean-noop-20260814/human_checkpoint_quit_retry_v3.json` 记录用户报告 `Quit` 无效，候选 EXE SHA `94A53EF47AC49CF2F13157905387932BB517F648A15B7A0200B098237F0015DA`，DLL SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`；没有创建角色或执行存档变更。该结果证明 CLEAN NOOP 也出现同类用户报告，但不证明终止时序、Steam 回调或根因。

### 当前证据交接：C5-L2 角色数据持久化序列完成（2026-08-14 11:43-11:47 +08:00，收尾记录 15:28 +08:00）

- 授权记录：`10_logs/P7-persistence-track-20260814/authorization_granted_c5_l2_persistence_20260814.json`，授权对象为 C5-L2 候选 SHA `4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3`（DLL SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`），一次性 disposable 角色 `P7_ORIGINAL_20260814`。
- 序列证据链：`runs/P7-authorized-c5-l2-20260814/human_checkpoint_creation_v2.json`（用户报告已创建 Tank，8 秒防抖等待完成，未使用 Quit 关闭）→ `session_relaunch_after_creation_v2.json`（同 SHA/DLL 路径重开，PID 19972）→ `persistence_checkpoint_v2.json`（**result=FAIL，restart_persistence=FAIL_NOT_RESTORED_OBSERVED**，重开后角色列表不含 `P7_ORIGINAL_20260814`，用户报告「没有角色」）→ `session_end_after_persistence_failure_v2.json`（CLEANUP_COMPLETED，PID 19972 已清理）。
- 分类结论：`NOT_RESTORED_OBSERVED`；`localization_causality = NOT_ESTABLISHED`；`root_cause = UNKNOWN`。保存序列化、Steam 回调结果、本地 fallback 行为均未被证明。ORIGINAL v2 与 CLEAN NOOP v3 均报告 Quit 无效，归类为独立基线/环境轨迹，不是本地化回归。
- 新增只读观察：`10_logs/P7-persistence-track-20260814/runtime_observation_v3.json` 记录共享 user data 目录出现 729 字节 `_0_6_0.dat`（创建 14:06、最后写入 14:30、SHA `4E3969A8F68512181FE018CCB84E56C0509AF9AA5C7D6FABE6A17E9975B5439F`）。11:20 preflight 记录匹配 save 数为 0，C5-L2 测试窗口（11:33/11:38/11:44 日志）无保存写入；该文件出现在 status.json 更新（11:47）之后，属于**未绑定观察**：未读取内容、不归属任何 G 盘分支候选、不得删除或修改。
- 外部活动：同一观察记录了一个活动中的外部 Mutagenic 进程（PID 17596，15:29:33 启动，响应正常，窗口 `Mutagenic`），其可执行文件位于 **F 盘原工作树** 的 `P7-authorized-original-steam-ready-v2-20260814` run（该 run 在 G 盘分支不存在）。仅捕获 OS 进程表元数据：未读取任何 F 盘文件、未终止该进程、未执行存档变更。该外部活动很可能就是 `_0_6_0.dat`（14:06-14:30）写入的来源。
- 状态更新：`10_logs/status.json`（updated_at 15:30）的 `persistence_track` Gate 保持 `IN_PROGRESS`，runtime Gate 保持 `HUMAN_REQUIRED`；`experiment.json` 标记 `COMPLETED_FOR_C5_L2`。
- 下一步：不执行超出已记录一次性角色的额外 Steam/cloud 或存档变更；不翻译额外可见标签（需明确范围和出处）；等待用户决定是否继续受控持久化比较或另立 CODE_PATCH 根因实验。

### 当前证据交接：C5-L2 角色数据持久化复查（2026-08-14 11:41 +08:00）

- 用户明确将本轮目标限定为角色数据持久化，不再把 `Quit` 作为判定项；授权记录为 `10_logs/P7-persistence-track-20260814/authorization_granted_c5_l2_persistence_20260814.json`，SHA-256 `C7E7B7D5284E8B224786390AFCD63D7262CF5714B281CEA2A3384B27DD8C82DD`。
- 当前 C5-L2 临时窗口 PID `14088` 已按 EXE SHA `4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3`、DLL SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799` 绑定；角色列表截图显示为空，下一步只创建 `P7_ORIGINAL_20260814`，等待至少 8 秒保存防抖，再关闭/重开同一路径验证角色是否恢复。
- 授权门本身没有启动、Steam 读取或存档变更；本轮若角色创建完成，保存来源、重启可见性和清理必须分别记录，不能由截图或进程存活替代。

### 当前证据交接：C5-L5 Keybinds 对话框导航切片（2026-08-14 09:36 +08:00）

- C5-L5 manifest：`mods/c5-l5-localization-keybinds-dialog/mod.json`，SHA-256 `9D231769A3DF103246161B5A755BBF3100C4EF9B5866BC40B76D18D80D92B5F1`；mapping SHA-256 `8A650CD0854865EB18E67F2E279A5BDA26C1E6A61502A5B7B788BCDD7B50219E`；依赖链由 resolver 固定为 `c5-l1-localization-menu-play-font -> c5-l2-localization-character-select -> c5-l3-localization-character-class-dialogs -> c5-l4-localization-settings-dialog -> c5-l5-localization-keybinds-dialog`，解析结果 SHA-256 `09077DF7F575E539C0B61C0E599758AA95528309A0180D622D0944C845921D76`。
- C5-L5 从 `03_raw` 复制 pack，并从 `00_original/Mutagenic.exe` 新鲜嵌入；没有使用 C5-L4 EXE、脏根 `06_worktree` 或失败 worktree 作为生产输入。新增两个 `DISPLAY_SAFE` 单元：`Keyboard Settings` → `键盘设置`、`Done` → `完成`；累计 13 个文本单元，未修改脚本。`label_text`、`action_name`、输入动作、节点路径、信号与资源引用均保持结构值。
- 机器证据总索引：`10_logs/C5-L5-keybinds-dialog-20260814/build.json`。PCK SHA-256 `B2E40929A020E10C5D3871792A603D7E0792FD210EA4B30CE18C0073D049A385`；候选 EXE SHA-256 `F1DAE1C7EAB8784DA44C14C06717C38E53709A1D95A49F185CE0D300A7C8E90E`；同目录 DLL SHA-256 `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`。
- S0 结构、字体 coverage/license、资源结构 token、声明 delta、PCK listing/checksum、PE/PCK/entry、完整嵌入复提取、manifest-driven 精确 serialized text 与 S1 boot 均为 `PASS`；pack 与 raw 的实际物理 changed paths 精确为：`Fonts/rsans.ttf`、`Scenes/Menu.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn`、`Scenes/Popups/Dialogs/Settings/Settings.tscn`、`Scenes/Popups/Dialogs/Keybinds/Keybinds.tscn`。
- C5-L5 人工阶段 checkpoint：`10_logs/C5-L5-keybinds-dialog-20260814/human_checkpoint.json`，状态 `HUMAN_REQUIRED`、`result=PARTIAL`、`active_blocker=false`；精确候选已另存启动记录，截图 SHA `BAEA6CC7AFB58D97F62A40AE1B5E84E58E77CDD19688B26D6AC49766D4273AB8` 已绑定。它证明标题“键盘设置”、按钮“完成”、可见动作标签、字形和布局；不证明输入动作行为、完成后的返回路径、存档或 release；后续可继续独立机器工作。
- C5-L5 的嵌入文本权威验证器为 `scripts/validate/verify_embedded_localization_manifest.py`，SHA-256 `42704CF8172C57CF96B1C3E8BE1D04F2C87CA19FD9B174964E2EF0B2B1E4A219`；报告 `embedded_text_manifest_report.json` 证明 13 个声明字段逐一命中且旧字段消失。该精确 manifest 验证器不能证明视觉渲染或动态文本。
 - 最新已由用户确认的可信中文化里程碑仍为 C5-L2；C5-L5 机器结果为 `PASS`，人工检查点保持 `HUMAN_REQUIRED` 且不作为阻塞项。用户已明确授权一次性 disposable test-save；下一目标是完成 `10_logs/P7-persistence-track-20260814/experiment.json` 的 ORIGINAL → CLEAN NOOP → C5-L2 受控比较。

### 当前证据交接：Phase 7 持久化轨迹准备（2026-08-14 09:36 +08:00）

- 实验定义：`10_logs/P7-persistence-track-20260814/experiment.json`，状态 `IN_PROGRESS`；比较对象为 `00_original`、CLEAN NOOP 与用户已确认的 C5-L2，不修改存档或 Steam/cloud 状态。
- 输入完整性：`input_integrity_check.json` 为 `PASS`；`00_original/Mutagenic.exe` 仍匹配可信 SHA，`03_raw` 文件数 3744 与 canonical raw manifest 一致。该检查为只读，不替代完整 raw 内容复核。
- 运行前预检：`preflight.json` 为 `PASS`；ORIGINAL、CLEAN NOOP、C5-L2 及 DLL SHA 均匹配，当前无 Mutagenic 进程、无本地 save 文件，未读取 Steam 状态且未执行存档变更。ORIGINAL 只能在临时 staging 中补入同 SHA DLL，不能写入 `00_original`。
- 静态契约：`static_contract.json` 为 `PASS`，确认 `Constants.USE_STEAM=true`、Steam 保存名/本地 fallback、保存 debounce、创建角色与 Quit 的保存调用，以及加载校验/迁移路径；这不等于运行时持久化已通过。
 - 运行时观察：原 `runtime_observation.json` 仍为 `NOT_STARTED`，只记录了未找到本地 save 文件且未读取/修改 Steam/cloud 状态；本次授权后的 ORIGINAL 隔离会话另有 `runs/P7-authorized-original-20260814/session_launch_v1.json` 和 `human_checkpoint_original_v1.json`，记录窗口启动成功、英文页面观察及 `Quit` 无法使用，但不证明协议存档/重启/清理。人工协议见 `human_test_protocol.md`，人工检查点为阶段记录点，不作为独立机器工作阻塞项。
 - 授权门：`authorization_gate.json` 保留未授权的 `HUMAN_REQUIRED` 记录；`authorization_granted_original_v1.json` 记录用户提供 `AllowDisposableTestSave` 的一次性授权。`stage_manifest.json` 证明 ORIGINAL 字节副本与 DLL SHA 锁定且未写入 `00_original`/`03_raw`；`human_checkpoint_original_v1.json` 为 `PARTIAL/HUMAN_REQUIRED`，角色名 `Starry Fox` 未匹配协议名，保存证据不足。CLEAN NOOP 的 `stage_manifest.json`/`session_launch_v1.json` 已按 EXE/DLL SHA 锁定并启动，当前不修改存档；C5-L2 的 staging manifest 也已通过。`quit_static_hypothesis_v1.json` 以只读源码分析记录了 `Quit` 依赖 Steam 异步保存回调的 `INFERENCE_HIGH` 假设，尚未经过三个候选运行对照。下一步先按同一 SHA/DLL 规则完成 CLEAN NOOP 与 C5-L2 的 `Quit` 对照，再决定是否需要补做严格协议存档。
- 截图观察：`10_logs/human_review_queue_20260814/screenshot_observation_submission_v1.json` 保存了前一组三张截图的 SHA；其中英文 Keybinds 截图仍未绑定候选 SHA，因此不判定 C5-L5 失败。新的 C5-L5 截图已在候选 checkpoint 中按 SHA 绑定并完成可见字段的部分复查。

### 当前证据交接：Keybinds 默认键位显示审计（2026-08-14 10:01 +08:00）

- 审计报告：`10_logs/C5-L5-keybinds-dialog-20260814/keybind_defaults_audit.json`，状态 `PASS`，技术结论 `INFERENCE_HIGH`；脚本为 `scripts/validate/audit_keybind_defaults.py`。
- 静态事实：`project.godot` 声明了 Shift/Space/A/D/W/S 及 Show Inventory 的 I/Tab 默认输入；但 `global_configuration.keybind_overrides` 初始为空，`get_keybind()` 在没有 override 时返回 `Unassigned`，启动路径未调用 `load_keybinds()`，且 Show Inventory 不在 `configurable_actions`。
- 结论：截图中的 `Unassigned` 更符合原有初始化/配置路径，而不是 C5-L5 的两处文本 patch 删除了默认键位。该结论不证明运行时按键或存档行为，也不授权修改；若要改变显示，应另立 `CODE_PATCH` 实验。
- 资源边界：`keybind_resource_boundary_audit.json` 为 `PASS`；C5-L5 pack/提取资源只改变两处标题/按钮文本，`project.binary`、Keybinds 脚本/remap、动作标签和 action 名均与 raw 一致。因此 `Unassigned` 不属于本地化 delta。

### 当前证据交接：状态证据索引完整性（2026-08-14 10:05 +08:00）

- `10_logs/status_evidence_integrity_20260814.json` 为 `PASS`；以 UTF-8 读取时，`status.json` 索引的 65 份 JSON 证据及当前 C5-L5/P7 记录均存在且可解析。先前的 PowerShell 解析报错是默认编码造成的假阳性，未发现证据文件损坏。

### 当前证据交接：C5-L4 Settings 对话框导航切片（2026-08-14 08:45 +08:00）

- C5-L4 manifest：`mods/c5-l4-localization-settings-dialog/mod.json`，SHA-256 `C178303FEC4CCA3F100F65578E945BE954409749A04FC0F5AF7F2E73FD3A91F3`；依赖链由 resolver 固定为 `c5-l1-localization-menu-play-font -> c5-l2-localization-character-select -> c5-l3-localization-character-class-dialogs -> c5-l4-localization-settings-dialog`，解析结果 SHA-256 `DF7A1B7B45F9D67CCBBC22E1BC666D1972BF8F7568D9A73009DD037952CB2F34`。
- C5-L4 从 `03_raw` 复制 pack，并从 `00_original/Mutagenic.exe` 新鲜嵌入；没有使用 C5-L2/C5-L3 EXE、脏根 `06_worktree` 或失败 worktree 作为生产输入。新增 3 个 Settings 对话框导航 DISPLAY_SAFE 单元：`Settings` → `设置`、`Close Settings` → `关闭设置`、`Keybindings` → `按键设置`；累计 11 个文本单元，未修改脚本。
- 机器证据总索引：`10_logs/C5-L4-settings-dialog-20260814/build.json`。PCK SHA-256 `EC2E8363FCE870B7FE6B2A5FB92BFDF8F46A7D609BEA2D1CF75D6DC128B39FF7`；候选 EXE SHA-256 `8563851B812A2E1AA8C86DCA0ADB3A89CD060983249BD2446C727DAA7A475397`；同目录 DLL SHA-256 `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`。
- S0 结构、字体 coverage/license、资源结构 token、声明 delta、PCK listing/checksum、PE/PCK/entry、完整嵌入复提取、精确 serialized text 与 S1 boot 均为 `PASS`；pack 与 raw 的实际物理 changed paths 精确为：`Fonts/rsans.ttf`、`Scenes/Menu.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn`、`Scenes/Popups/Dialogs/Settings/Settings.tscn`。
- C5-L4 人工阶段 checkpoint：`10_logs/C5-L4-settings-dialog-20260814/human_checkpoint.json`，状态 `HUMAN_REQUIRED`，`active_blocker=false`。它证明清单已按候选 SHA 绑定并保留记录点，不证明尚未观察的 Settings 交互、视觉质量、剩余设置控件、存档或 release；后续可继续独立机器工作。
- 首次 `embedded_text_report.json` 因使用裸子串匹配节点标识而产生 forensic 假失败；已修正为 `scripts/validate/verify_embedded_localization_text.py` 的精确 `text = "..."` 字段检查，权威证据为 `embedded_text_report_v2.json`。
- 最新已由用户确认的可信中文化里程碑仍为 C5-L2；下一目标是继续定义并验证下一份 manifest-scoped 机器切片，不将 C5-L4 人工 checkpoint 当作阻塞项。

### 当前证据交接：C5-L3 角色创建/切换对话框切片（2026-08-14 08:22 +08:00）

- C5-L3 manifest：`mods/c5-l3-localization-character-class-dialogs/mod.json`，SHA-256 `1BC99F175965119422677E5255905438862E22042329664B3B4D80E7EBEBF99A`；依赖链由 resolver 固定为 `c5-l1-localization-menu-play-font -> c5-l2-localization-character-select -> c5-l3-localization-character-class-dialogs`，解析结果 SHA-256 `42DA949A1E24CEC01FC409BC3BBEE066720D0177FC4F4393C2CB2C635E5C1097`。
- C5-L3 从 `03_raw` 复制 pack，并从 `00_original/Mutagenic.exe` 新鲜嵌入；没有使用 C5-L2 EXE、脏根 `06_worktree` 或失败 worktree 作为生产输入。新增 4 个 DISPLAY_SAFE 单元：两个 `CharacterChanger.tscn` 与两个 `CharacterCreator.tscn` 的 `Cancel`/`Choose your Class`；累计 8 个文本单元，未修改脚本。
- 机器证据总索引：`10_logs/C5-L3-character-class-dialogs-20260814/build.json`。PCK SHA-256 `016FA3A3E39DB08DD43D894E65FEEA0106AEBF41CB8C43363E2291BC0F5F7AF7`；候选 EXE SHA-256 `B8564289CE2DEC95709F4230C558D7D56F22DA8E1C7C5D256C68331915EAB02A`；同目录 DLL SHA-256 `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`。
- S0 结构、字体 coverage/license、资源结构 token、声明 delta、PCK listing/checksum、PE/PCK/entry、完整嵌入复提取、embedded text 与 S1 boot 均为 `PASS`；pack 与 raw 的实际物理 changed paths 精确为：`Fonts/rsans.ttf`、`Scenes/Menu.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterChanger.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn`。
- C5-L3 人工阶段 checkpoint：`10_logs/C5-L3-character-class-dialogs-20260814/human_checkpoint.json`，状态 `HUMAN_REQUIRED`，`active_blocker=false`。它证明清单已按候选 SHA 绑定并保留记录点，不证明尚未观察的交互、视觉质量、动态职业文本、存档或 release；后续可继续独立机器工作。
- 最新已由用户确认的可信中文化里程碑仍为 C5-L2；下一目标是继续定义并验证下一份 manifest-scoped 机器切片，不将 C5-L3 人工 checkpoint 当作阻塞项。

### 当前证据交接：C5-L2 角色选择切片（2026-08-14 07:40 +08:00）

- 当前阶段仍为 `PHASE_6_INCREMENTAL_MOD_LOCALIZATION_INTEGRATION`。C5-L1 的已审核截图只证明主菜单显示切片，不作为 C5-L2 的人测证据。
- C5-L2 manifest：`mods/c5-l2-localization-character-select/mod.json`，SHA-256 `4FBD04B3DDBDDBCDE40BF6A788DD782D575FB59B28173410A2E4DA9187628157`；范围是 4 个 `DISPLAY_SAFE` 文本单元（含 C5-L1 的 `开始游戏` 控制）和声明的 `Fonts/rsans.ttf` 字体 overlay。
- C5-L2 由 `03_raw` 生成 pack，并从 `00_original/Mutagenic.exe` 新鲜嵌入；没有使用旧 modded EXE、脏根 `06_worktree` 或第一次失败的部分 worktree 作为生产输入。
- 机器证据：`10_logs/C5-L2-character-select-20260814/build.json`。PCK SHA-256 `24C371B0B1415B0FDDE6321D69BD275AAAA923C35622174977A5C99639557A32`；候选 EXE SHA-256 `4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3`；同目录 DLL SHA-256 `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`。
- S0 结构 Gate、字体 cmap/license 前置 Gate、资源结构 token Gate、声明 delta、PCK listing/checksum、PE/PCK/entry、完整嵌入复提取和 embedded text 均为 `PASS`；PCK 3744 条目，物理 changed paths 只有 `Fonts/rsans.ttf`、`Scenes/Menu.tscn`、`Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn`。
- S1 boot 为 `PASS`：`boot_probe.txt` 记录真实 `Mutagenic` 窗口、无 ALERT、无 fatal marker。日志中的 `Viewport`/`is_inside_tree`/`SelfList` 类错误已与 ORIGINAL 控制对照，记录为 baseline comparison，不作为 C5-L2 根因。
- 当前 Gate：`localization_c5_l2 = PASS`，对应 `core_smoke.json`、`human_visual_session_v2.json`、`human_visual_result_c5_l2_v1.json`、`human_visual_result_c5_l2_review_v2.json` 和 `HUMAN_CHECK_REQUEST.md`。用户报告精确候选 SHA `4675BE5D...FABDE3` 测试无误，记录中的 12 项检查均为 true，未提供截图；该记录证明声明的主菜单 -> 角色选择切片，不证明其他画面、完整本地化、存档或 release。
- 人工测试策略已更新：每个阶段保留 SHA 绑定的人测记录点；`HUMAN_REQUIRED` 不再作为独立项目阻塞项，机器可验证的后续阶段可继续。若人工检查失败，只降级受影响切片并回到可信基线，不在失败 EXE 上修补。

**最新视觉诊断**: 自动捕获矩阵 `capture_matrix_v11.json` 及其控制实验仍登记为 `INVALID`/非区分性证据，不能用于视觉 PASS；本次视觉 PASS 来自用户提供的真实菜单截图，并由 `human_visual_result_v17.json` 和 `human_visual_result_review_v27.json` 绑定到候选 SHA。

**捕获器对照实验**: `capture_control_experiment_v12.json` 用同一脚本和环境捕获已有 C2 人工视觉控制与 C5-L1 候选；三种输出逐字节相同，说明该捕获通道不能区分候选。该结果是 `INCONCLUSIVE_FOR_VISUAL_CONTENT`，不作为视觉证据，也不再重复此矩阵。

**历史捕获路径对照**: `capture_legacy_control_experiment_v13.json` 复测旧的 `GetWindowRect` 屏幕捕获路径；C2 与 C5-L1 均得到逐字节相同的 TraceMemo 白窗。两者窗口元数据均为可见、响应、`Engine`、前台 PID 匹配、客户区 `2048x1152`，但没有可信游戏像素，结论仍为 `INCONCLUSIVE_FOR_VISUAL_CONTENT`。

**人工启动前置检查**: `human_launch_precheck_v15.json` 证明精确 C5-L1 EXE 使用同目录 DLL 启动后产生响应中的 `Mutagenic` 窗口；随后用户截图完成了菜单文字/glyph/layout 的人工观察。

**人工视觉会话**: `human_visual_session_v16.json` 通过候选哈希/DLL 检查并启动前台 `Mutagenic` 窗口；用户提供的截图已记录为 `human_observation_v27.png`（SHA-256 `1D69F7F0C0D86A66D97AB7728430FAC353F37106F16F3330E6EB35E4DAAEDCB0`），人工清单为 `PASS`。

**人工会话快照**: `human_visual_session_snapshot_v18.json` 与 v20 是人工结果写入前的历史快照；最终结果以 `human_visual_result_v17.json` 及其 v27 审查记录为准。
**GPU 捕获对照 v23**: `capture_gfxcapture_control_experiment_v23.json` 使用 ffmpeg `gfxcapture` 直接 HWND + `hwdownload` 对 C2 与 C5-L1 采集；两帧均为相同纯黑 PNG（SHA `0A3FB351…EED7D0`），登记为 `INCONCLUSIVE_FOR_VISUAL_CONTENT`，不作为视觉证据，也不再重复该通道。
**Desktop Duplication v26**: `capture_ddagrab_control_experiment_v26.json` 尝试 `ddagrab` 对照，但 60 秒内没有生成帧、元数据或 stderr；登记为 `UNKNOWN`，不作为视觉证据且不再重复该挂起路径。
**ffmpeg 捕获对照**: `capture_ffmpeg_control_experiment_v19.json` 使用 SHA 锁定的 `ffmpeg 8.1.2`/`gdigrab` 对 C2 与 C5-L1 各采集三帧；六帧 SHA 均为 `13C8831E380AE1CA8B83F3624BD75BC4080A66C599C212E89CE7F5DBCA1A1D81`，都是 TraceMemo 白窗，登记为 `INCONCLUSIVE_FOR_VISUAL_CONTENT`，不得升级或替代用户视觉证据。

**C3 provenance 修复**: `C3-one-resource-help-label-20260814-retry` 的旧 patch report 使用根 `06_worktree`，不作为生产输入。`C3-one-resource-help-label-20260814-clean` 从 `03_raw` 新建，候选 EXE SHA-256 为 `08EE9F853E4AFA5DD988522C94EF082BBAFCA0339D6133A681E592786E75585F`；结构/PCK/EXE/启动 PASS，且旧截图所对应的 EXE 与 clean 候选逐字节相同，`visual_evidence_review.json` 绑定确认 Help Guides 右对齐，C3 恢复 `PASS`。

| 维度 | 原版 | 当前构建 |
|---|---|---|
| PCK 文件数 | 3744 | 3744 |
| `.gde` + `.gd.remap` | 524 对 | 524 对 |
| 纯文本 `.gd` | 1 | 1 |
| 启动窗口 | `Mutagenic` | `Mutagenic` |
| stderr | 255 字节 | 255 字节（同内容） |

---

## 本轮修复的根因

### 1. 嵌入式 PCK 尾部偏移字段为 0（P0，启动失败的直接原因）

Godot 3.x 自文件末尾反向定位嵌入 PCK：

```
1. 读末尾 4 字节  -> 必须是 GDPC
2. 读其前 8 字节  -> u64 ds
3. PCK 起点 = file_size - ds - 12，在该处再次校验 GDPC
```

GDRE `--pck-create` 产出的是 standalone PCK，该字段留为 `0`。直接嵌入后 Godot 在错误位置寻找 PCK，弹出
`Couldn't load project data at path "."`。

修复：`scripts/embed_pck.py` 写入 `ds = pck_size - 12`。

证据：原版 `ds=62745028`，`103290320 - 62745028 - 12 = 40545280` = PCK 起点。

### 2. PCK 内 file entry 偏移是 PCK 相对而非 EXE 绝对（P0，同上）

Godot 3.x 嵌入读取器**直接把存储偏移当 EXE 绝对地址使用**，不加 PCK base。GDRE 写的是 PCK 相对偏移。

修复：`embed_pck.py` 的 `adjust_pck_entry_offsets()` 在嵌入前对每个条目加 `PCK_OFFSET`。

证据（`scripts/probe_pck_offsets.py`）：

```
原版      stored_offset=55924896 -> 该绝对位置字节 = "RSRC"  OK
修复前    stored_offset=300928   -> 绝对位置非资源头，PCK相对位置才是 "RSRC"  BAD
修复后    stored_offset=40846208 -> 该绝对位置字节 = "RSRC"  OK
```

### 3. `build_pack.py` 无条件删除残留 `.gde`/`.remap`（丢弃 28 个脚本）

`addons/` 被 overlay 跳过（在 `SKIP_DIRS`），其 `.gde` 却在清理步骤被删除，导致这些脚本**既无 `.gd` 也无 `.gde`**，PCK 从 3744 缩到 3206。

修复：保留自洽的 `.gde`+`.remap` 对；不一致时 FAIL CLOSED 而非静默删除。

注：此项是真实缺陷，但**不是**启动失败的原因 —— Godot 3.x 能直接加载未加密 `.gd`。

### 4. `embed_pck.py` 硬编码路径 / 缺少 PE section 更新

- 无参数解析，`rebuild.py` 传的 3 个参数被忽略，始终嵌入旧的 `09_output/data.pck`
- 未更新 PE section table 中 `pck` section 的 `raw_size`

均已修复。

---

## 脚本编译 + 加密（已实现并验证）

`scripts/compile_encrypt_scripts.py`

```
.gd --(GDRE --compile)--> .gdc --(AES-256-ECB)--> .gde  + .gd.remap
```

GDEC 容器布局（Godot 3.x `FileAccessEncrypted`）：

```
0..4    "GDEC"
4..8    u32 mode = 1 (MODE_WRITE_AES256)
8..24   md5(plaintext)
24..32  u64 plaintext length
32..    AES-256-ECB 密文，零填充至 16 字节对齐
```

- 密钥：`manifests/script_key.txt`（64 hex / AES-256）
- 依赖：PyCryptodome 3.23.0（`02_tools/venv`）
- 产出：525 个 `.gde`，0 失败

**正确性证据**（非断言）：

- `scripts/verify_gde_against_original.py`：524 个有原版对照的脚本中 **456 个逐字节相同**
- 余下 68 处差异全部有解释（`scripts/classify_gde_mismatch.py`）：66 处源码在 `06_worktree` 被有意修改；2 处（`Constants`、`GameState`）因 `04_recovered` 被前序会话污染而被误判为缺陷
- `scripts/probe_pristine_roundtrip.py`：对这 2 个脚本用原版 `.gde` 反编译出的纯净源走完整管线，产出与原版**逐字节相同**（2880/2880、51440/51440）→ **管线无缺陷**

`build_pack.py` 现按脚本逐个保持原版形态：原版有 `.gde` 的 → 用加密产物；原版为纯文本的（1 个 `PassiveTree.gd`）→ 保持纯文本。因此 `08_pack` 为 3744 文件，与原版一致。

---

## 已知问题

### `04_recovered` 已被污染（违反 AGENTS.md §6）

`04_recovered/Globals/Constants.gd` 被前序会话就地修改，与 `06_worktree` 同 hash：

```diff
- var USE_STEAM = true          # 原版
+ var USE_STEAM = false
+ func _ready():
+     if Steam.isSteamRunning(): ...
```

`04_recovered` 应为纯净反编译源，当前**无法作为"未修改基线"使用**。需要纯净源时从
`03_raw/*.gde` 反编译获得（见 `probe_pristine_roundtrip.py`）。`Globals/GameState.gd` 同样受影响。

### `project.binary` 报 "not ECFG"

```
ERROR: Corrupted header in binary project.binary (not ECFG).
ERROR: Couldn't load file 'res://project.binary', error code 16.
```

**原版 EXE 产生完全相同的 stderr**，属该自定义构建的良性噪声，非本项目引入。

### `06_worktree/project.godot` 的改动不进 PCK

`build_pack.py` 的 `OVERLAY_EXTS` 不含 `.godot`，且 PCK 用的是 `project.binary`。之前为启用
`file_logging/enable_file_logging=true` 所做的编辑**未生效**。若确需生效，须重新生成 `project.binary`。

### Steam API 初始化失败（预期，非阻塞）

非 Steam 启动时 Steam API 无法验证，属预期行为。

---

## 验证能力与限制

**可自动验证**（`scripts/probe_boot.py`）：进程存活、窗口标题、模态对话框（`ALERT!`）、日志 boot marker、fatal marker。

关键教训：**进程存活不能作为成功判据** —— `ALERT!` 模态对话框同样会让进程保持存活。本轮早期多次"运行 15 秒通过"均为此误判。现以窗口标题 + 对话框检测为判据，并以原版 EXE 作对照组。

**无区分力的信号**（勿用作判据）：

- `user://` 写入：原版与本构建均只写日志，两者同为 `NO_SCRIPT_EVIDENCE`
- stdout：Windows GUI 构建下恒为空，`--verbose` 亦无额外输出
- GDScript `print()`：不进日志文件

**无法验证**：UI 中文显示、文字溢出/遮挡、真实游戏交互。

---

## Gate 状态

```
BASELINE_STRUCTURE   PASS   原版 EXE hash 已核对，00_original 未被修改
RECOVERY             PASS   3744 文件全部可枚举
TRANSLATION_SAFETY   N/A    尚未开始翻译
SCRIPT_BUILD         PASS   525/525 加密成功；456 逐字节对齐原版，余下均可解释
PACK_STRUCTURE       PASS   3744 文件、524 .gde+remap、1 纯文本，与原版一致
EXE_STRUCTURE        PASS   PE section、PCK 尾部 ds、条目绝对偏移均已校验
STATIC_VALIDATION    PASS   GDRE 可枚举嵌入 PCK 全部 3744 文件
RUNTIME_NONVISUAL    PASS   游戏窗口正常，无 ALERT，stderr 与原版同
VISUAL               UNVERIFIED
HUMAN_INTERACTION    UNVERIFIED
REPRODUCIBILITY      PASS   自 00_original 起全脚本自动化
```

---

## 环境

- Windows 10.0.19045
- Godot 3.5.3.stable.custom_build.9f743ad7f（游戏内嵌）
- GDRE Tools v2.6.4（运行于 Godot 4.8.dev）；字节码目标 `3.5.3.stable` → 实际 `a7aad78 (3.5.0-stable)`
- Python 3.11.15（`02_tools/venv`），PyCryptodome 3.23.0
- 原版 EXE SHA-256：`C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209`
- 原版 EXE 大小 103290320；PCK 起点 40545280；PCK 大小 62745040

---

## 构建命令

```powershell
# 1. 编译 + 加密脚本（约 10 分钟，525 个）
02_tools\venv\Scripts\python.exe scripts\compile_encrypt_scripts.py

# 2. 打包 + 嵌入
02_tools\venv\Scripts\python.exe scripts\rebuild.py --no-fonts --output 09_output\Mutagenic.exe

# 3. 启动验证
python scripts\probe_boot.py 09_output\Mutagenic.exe --seconds 15
```

辅助脚本：

| 脚本 | 用途 |
|---|---|
| `compile_encrypt_scripts.py --self-test` | 重建已有 `.gde` 并逐字节比对 |
| `verify_gde_against_original.py` | 全量 `.gde` 对照 `03_raw`，按目录汇总 |
| `classify_gde_mismatch.py` | 区分「源码被改」与「管线缺陷」 |
| `probe_pristine_roundtrip.py` | 纯净源往返，判定管线是否有缺陷 |
| `probe_pck_offsets.py` | 判定 PCK 偏移约定（绝对 vs 相对） |
| `check_tail.py` | 校验嵌入 PCK 尾部 `ds` 字段 |
| `audit_script_coverage.py` | 检查是否有脚本被丢弃 |
| `probe_boot.py` | 启动验证（唯一 runtime 判据） |

---

## 参考

- 项目总控规则：`AGENTS.md`
- Godot 运行日志：`%APPDATA%\Godot\app_userdata\Mutagenic\logs\`
- 前序残留物（未删除，供查阅）：`10_logs/prior_residue/`、`10_logs/cleaned_gdc_backup_*/`

---

## 下一步

1. **重建 `04_recovered`**：从 `03_raw/*.gde` 反编译，恢复纯净基线（P1，当前无干净基线）
2. **决定 Steam 改动去留**：`Constants.USE_STEAM` 与 `GameState._ready()` 的改动是否保留，需明确
3. **开始中文化**：按 AGENTS.md §7 建立带上下文的翻译单元，禁止全局英文替换
4. **CJK 字体**：当前 `--no-fonts`；`02_tools/fonts_merged` 需就绪后启用

人工验证（仅在需要时）：启动 `09_output/Mutagenic.exe`，确认主菜单可见、可进入游戏。当前为英文原版内容，无需判断中文显示。

---

## 2026-08-13 当前证据交接（以本节和 `10_logs/status.json` 为准）

- `00_original/Mutagenic.exe` 当前 SHA-256 仍为 `C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209`。
- 已生成协议要求的 `01_baseline/game_fingerprint.json`、`01_baseline/pe.json`、`01_baseline/pck_manifest.json`；原始 PCK 3744/3744 条目 MD5 有效。
- 已生成 `10_logs/environment.json` 和 `tools.lock.json`，记录 Python、GDRE、Git、uv 版本及工具哈希；脚本密钥未写入报告。
- `03_raw` 自校验通过：3744/3744 路径与 SHA-256 内容一致，证据为 `10_logs/raw_tree_selfcheck.json`。
- C0 代表性脚本零变化回环通过 6/6，证据为 `10_logs/C0-script-roundtrip-20260813.json`。这只证明分层样本，不证明全部脚本的语义运行正确性。
- 已从原始 EXE 重新恢复 524/524 脚本，证据为 `10_logs/recovery_full_20260813-2315/recovery_report.json`；正式 `04_recovered` 已切换为该干净恢复树。
- 旧污染 `04_recovered` 与其派生 `06_worktree` 已保存在 `10_logs/contaminated_baseline_20260813-2320/`，仅作取证，不得作为生产输入。
- 正式 `06_worktree` 已从干净 `04_recovered` 重新生成，manifest 为 `manifests/worktree_manifest.json`。

当前 Gate：`ENVIRONMENT/FINGERPRINT/RAW_EXTRACTION/RECOVERY/SCRIPT_CRYPTO_KNOWLEDGE/CLEAN_NOOP/C0 = PASS`；`C1 ONE-VALUE` 是下一个未完成 Gate。下一目标是从 `03_raw` 出发建立一个声明式、单值、可回滚的能力实验；不得修补历史 EXE 或进行全局文本替换。

### C1 ONE-VALUE 当前交接

已完成并保存：

- manifest：`mods/c1-one-value/mod.json`
- 单一逻辑变更：`Scenes/AreaSkillEffects/AreaSkillEffect.gd` 的 `radius` 默认值 `15.0 -> 16.0`
- preimage：`49E131C1E22AE40A3FAF5BE9C64D8794A46566E65AB50A57EC1D41A16164EC36`
- 声明式 patch/compile/pack/delta 证据：`10_logs/C1-one-value-20260813/patch_report.json`、`compile_report.json`、`delta_report.json`、`pack_v2_report.json`
- normalized PCK：3744/3744 条目 checksum 有效，证据 `pck_md5_normalization.json`
- EXE 结构与嵌入回抽：PASS，证据 `exe_structure_report.json`、`exe_normalized_vs_pack_report.json`
- 当前候选：`10_logs/C1-one-value-20260813/runtime_candidate/Mutagenic.exe`
- 候选 SHA-256：`3D28ECE53F5D29105A6D439836A3008270F868757AEC03AB0C70EA32A6ADE357`
- 当前 boot：PASS；证据 `boot_probe_with_dll.txt`，包含当前运行日志、真实窗口、无 ALERT/fatal。

C1 当前 Gate 为 `HUMAN_REQUIRED`，不是 PASS。机器尚不能证明默认 AreaSkillEffect 半径变化的视觉/交互效果。第一次缺少 `steam_api64.dll` 的启动结果和第一次 stale-log 误报均为失败/取证，不得复用。下一动作是用候选 EXE 与同目录 DLL 做一次短人工验证，确认是否看到/触发声明的半径变化；若确认，再更新 Gate 和继续 C2。

### C1 ONE-VALUE 有效闭合（2026-08-13 23:53 +08:00）

上一段描述的是已被语义审计否定的半径候选，保留作历史取证，不再代表当前 Gate。该候选的审计证据为 `10_logs/C1-one-value-20260813/semantic_review.json`：`AreaSkillEffect.radius` 会在 `DelayedSkill` 初始化及可玩技能实例化时被调用方值覆盖，因此不能证明声明的默认值能到达运行时效果。

独立重建的有效 C1 为菜单显示值实验：

- manifest：`mods/c1-one-value-menu-version/mod.json`
- 单一逻辑变更：`Globals/Constants.gd` 的 `GAME_VERSION`：`EA 0.6.2 -> EA 0.6.2 [C1-VALUE]`
- 从 `03_raw` 复制 pack 树，只覆盖 `Globals/Constants.gde` 与 `Globals/Constants.gd.remap`；`delta_report.json` 为 PASS
- PCK 3744/3744 条目 checksum 有效；PE/PCK/trailer/offset 结构 PASS；嵌入 EXE 完整复提取与 pack 树 3744/3744 路径和 SHA-256 一致
- 最终候选：`10_logs/C1-one-value-menu-20260813/runtime_candidate/Mutagenic.exe`
- 最终候选 SHA-256：`F48CF59FA81D6262D3FC47794DCEDF739D33C2E286FE4526F009194D1D019D00`
- 截图：`10_logs/C1-one-value-menu-20260813/menu_capture.png`
- 视觉结果：主菜单显示 `Build: EA 0.6.2 [C1-VALUE]`；报告为 `10_logs/C1-one-value-menu-20260813/menu_visual_report.json`

因此当前状态文件中的 `value_mod_c1 = PASS` 仅证明：一个声明式单值变更能以可解释的物理 delta 进入最终 PCK/EXE，并到达可观测的主菜单显示字段。它不证明核心 gameplay、存档、退出行为或全局视觉质量。

下一程序目标：C2 ONE-CODE。只从干净生成树构造一个 `Scenes/Menu.gd` 代码变更，使用明确的运行时标记 `[C2-CODE]`；不得复用任何 C1 生成目录作为生产输入。

### C2 ONE-CODE 已闭合（2026-08-14 00:06 +08:00）

- manifest：`mods/c2-one-code-menu-render/mod.json`
- 唯一代码变更：`Scenes/Menu.gd::render()` 将 `VersionLabel.text = Constants.GAME_VERSION` 改为追加 `[C2-CODE]`
- 编译/加密只产生 `Scenes/Menu.gde` 与 `Scenes/Menu.gd.remap` 的声明 delta；`10_logs/C2-one-code-menu-render-20260813/delta_report.json` 为 PASS
- 最终 PCK/EXE：结构、3744 条目 checksum、GDRE listing、完整复提取和原版 composition 均 PASS
- 最终候选：`10_logs/C2-one-code-menu-render-20260813/runtime_candidate/Mutagenic.exe`
- 最终候选 SHA-256：`AB5C3EE523DA4236BD8C6ED432A77C6DA3C3A341808E092F723A52C28118FE22`
- 运行时截图：`10_logs/C2-one-code-menu-render-20260813/menu_capture.png`
- 视觉结果：主菜单显示 `Build: EA 0.6.2 [C2-CODE]`；报告为 `10_logs/C2-one-code-menu-render-20260813/menu_visual_report.json`

因此 `status.json` 中 `code_mod_c2 = PASS` 仅证明：一条声明式代码变更经过编译、加密、打包、嵌入后在真实游戏窗口中执行。它不证明核心 gameplay、存档、退出行为或发布就绪。

下一程序目标：C3 ONE-RESOURCE。只从 `03_raw` 派生，修改 `Scenes/Menu.tscn` 一个用户可见属性，保持 NodePath、ExtResource/SubResource 和所有脚本逻辑不变。

### C3 ONE-RESOURCE 已闭合（2026-08-14 00:27 +08:00）

- manifest：`mods/c3-one-resource-help-label/mod.json`
- 唯一资源变更：`Scenes/Menu.tscn::HelpLabel.align` 从 `1`（居中）改为 `2`（右对齐）
- 第一次构建因 CRLF preimage 声明错误被 fail-closed 拒绝；取证保存在 `10_logs/C3-one-resource-help-label-20260814/`
- 修正后的 retry 从干净 `06_worktree` 生成，资源合同报告 `resource_contract_report.json` 为 PASS：除声明属性外内容相同，node declarations、NodePath、res:// 路径、ExtResource、SubResource、connection 集合均无差异
- `03_raw -> pack` 只有 `Scenes/Menu.tscn` 变化；PCK/EXE 结构、3744 条目 checksum、完整复提取、GDRE listing、原版 composition 均 PASS
- 最终候选：`10_logs/C3-one-resource-help-label-20260814-retry/runtime_candidate/Mutagenic.exe`
- 最终候选 SHA-256：`08EE9F853E4AFA5DD988522C94EF082BBAFCA0339D6133A681E592786E75585F`
- 视觉结果：主菜单 `Help Guides` 标签已右对齐；截图为 `10_logs/C3-one-resource-help-label-20260814-retry/menu_capture.png`

因此 `status.json` 中 `resource_mod_c3 = PASS` 仅证明一个结构化资源属性能安全进入最终 PCK/EXE 并影响目标 UI 属性，不证明核心 gameplay、存档、退出行为或发布就绪。

下一程序目标：C4 ONE-ASSET。只替换一个声明的菜单背景位图，保持路径、尺寸、格式及导入关系可验证。

### C4 ONE-ASSET 已闭合（2026-08-14 00:45 +08:00）

- manifest：`mods/c4-one-asset-menu-background/mod.json`
- 唯一资产变更：`.import/background_blurred.png-2b6b19973a497aee4145e7f6c132790d.stex` 替换为已有的 `background.png` 导入缓存；目标路径保持不变
- 资产合同报告 `10_logs/C4-one-asset-menu-background-20260814/asset_contract_report.json` 为 PASS：STEX、960x536、flags、WebP marker 均保持有效；嵌入后复提取合同也为 PASS
- `03_raw -> pack` 只有目标 `.stex` 变化；PCK/EXE 结构、3744 条目 checksum、完整复提取、GDRE listing、原版 composition 均 PASS
- 最终 PCK：`10_logs/C4-one-asset-menu-background-20260814/c4_menu_normalized.pck`，SHA-256 `F733ACDDC44D2DD6E9ABE93DC8A472BDFF7303A72AE869A9ADB422F94026DCA2`
- 最终候选：`10_logs/C4-one-asset-menu-background-20260814/runtime_candidate/Mutagenic.exe`
- 最终候选 SHA-256：`7F63BBCEDB64AF8BF474779FA28800FDF47964561FD247A3908E80803B32FDB2`
- 视觉结果：运行中的主菜单背景由模糊版本变为清晰版本；截图为 `10_logs/C4-one-asset-menu-background-20260814/menu_capture.png`，SHA-256 `2A1E02FFAD61EF4FBBF601D104D270B910C24DCBDEBF1EE5F2888B369B873C07`

因此 `status.json` 中 `asset_mod_c4 = PASS` 仅证明：一个已存在的同规格 Godot 导入缓存可以作为声明式资产 delta 进入最终 PCK/EXE，并在真实游戏窗口中产生目标视觉效果。它不证明从新的 PNG 源文件重新导入、完整视觉质量、核心 gameplay、存档、退出行为或发布就绪。

当前项目已进入 `PHASE_4_GAME_SCHEMA`；下一程序目标是从干净恢复/参考输入生成第一版机器可读 Game Schema，显式记录事实、推断与未知项。

### PHASE 4 GAME SCHEMA 已闭合（2026-08-14 01:11 +08:00）

- 生成脚本：`scripts/schema/discover_schema.py`
- Schema：`05_schema/game_schema.json`，SHA-256 `C4472A29A3696412A633B858CE8046B2D737BB2C210643336CA68144E9FBA7F1`
- 发现报告：`10_logs/schema_discovery-20260814.json`
- 独立校验：`scripts/schema/validate_schema.py`；报告 `10_logs/schema_validation-20260814.json` 为 PASS，16 项检查全部通过
- 初始覆盖：4 个职业、8 个专精、53 个技能、60 个技能支持、20 个地图配置、59 个世界地图节点、62 条边、143 个统计/技能字段、27 个 project 输入动作、356 个场景、2063 个场景节点、209 个连接
- 引用审计：1371 个唯一 `res://` 引用；123 个未直接解析项均已分类为 119 个编辑器源+导入 sidecar、2 个 extensionless/prefix match、1 个路径不一致 basename match、1 个动态模板；没有 `UNRESOLVED` 分类
- Schema 明确保留 UNKNOWN：运行时存档序列化、语义覆盖完整性、本地化字符串安全分类；这些未知项不得被解释为已验证

因此 `status.json` 中 `schema = PASS` 仅证明：Schema 在当前哈希锁定的干净恢复/参考输入上可确定性生成，并通过注册表、库存、引用分类、置信度和 UNKNOWN 项的一致性校验。它不证明运行时语义、存档兼容、本地化安全或发布就绪。

当前项目已进入 `PHASE_5_LOCALIZATION_SAFETY_ARCHITECTURE`；下一目标是建立带路径、字段上下文、占位符/token 和分类的翻译单元清单，先提取与审计，不直接应用翻译。

### PHASE 5 本地化安全架构已建立，C5-L0 已闭合（2026-08-14 01:34 +08:00）

- 提取脚本：`scripts/localization/extract_units.py`；翻译单元：`05_schema/localization_units.json`，SHA-256 `EFDF58F45776F7461332C62ED389F177B8EE69F48CC442D730C80D653171A11E`
- 提取报告：`10_logs/localization_extraction-20260814.json` 为 PASS；扫描 2535 个源文件、85280 个带引号字面量、10268 个唯一文本；分类为 DISPLAY_SAFE 711、AMBIGUOUS 52415、STRUCTURAL 27332、DO_NOT_TRANSLATE 4822
- 独立校验：`scripts/localization/validate_units.py`；报告 `10_logs/localization_validation-20260814.json` 为 PASS，12 项检查全部通过，包含源文件哈希、单元位置、去重、占位符/token 保全及 DISPLAY_SAFE 排除规则
- 应用脚本：`scripts/localization/apply_units.py`；它只接受 unit ID、目标 preimage 和 DISPLAY_SAFE 单元，不做全局文本替换
- C5-L0 manifest：`mods/c5-l0-localization-menu-play/mod.json`；从新生成工作树精确替换 `Scenes/Menu.tscn:69:9` 的 `Play` 为 `开始游戏`
- 正向证据：`10_logs/C5-L0-localization-menu-play-20260814/apply_report.json`、`resource_contract.json`、`delta_report.json` 均为 PASS；实际只有 `Scenes/Menu.tscn` 发生声明的变更
- 负向证据：故意提交 `Scenes/Menu.gd:3:22` 的 STRUCTURAL 音频路径，`negative_apply_report.json` 为预期 FAIL、0 次替换；`negative_integrity.json` 证明目标文件与基线 SHA `58373B0009BDE1B15E5FC7B665B6E7B173399A33E95993BF363E21E75A6F0CCC` 完全一致
- 完整实验/构建记录：`10_logs/C5-L0-localization-menu-play-20260814/experiment.json`、`build.json`

当前 `status.json` 中 `localization = IN_PROGRESS`，不是完整本地化 PASS。C5-L0 仅证明本地化安全架构、一个 DISPLAY_SAFE 单元的精确变换和 STRUCTURAL fail-closed 拒绝；尚未证明编译、PCK/EXE、启动、中文字体覆盖、视觉质量、核心 gameplay、存档或发布就绪。下一目标是从新生成工作树构建小 UI 本地化 slice，并完成编译、打包、结构、启动和视觉验证。

### C5-L0 最终构建闭环（2026-08-14 01:51 +08:00）

- 从 `03_raw` 派生独立 pack 树，`Scenes/Menu.tscn` 是唯一 declared delta；pack 3744/3744 文件，`pack_delta_report.json` 为 PASS
- PCK：`10_logs/C5-L0-localization-menu-play-20260814/c5_l0_menu_normalized.pck`，SHA-256 `D10D03271E1DB63C5C0BB236521BCBA9458774755489CB9A296E4CE53348C1D2`；MD5 normalization 3744/3744，拒绝项 0
- 最终 EXE：`10_logs/C5-L0-localization-menu-play-20260814/c5_l0_menu_normalized.exe`，SHA-256 `8319F148A6F0DF816F022870372C514ABEC0265FA2C9E09B2B2665CFF8864B9E`；来源为 `00_original/Mutagenic.exe`，没有复用旧 modded EXE
- `pck_listing.json`、`exe_structure_report.json`、`exe_vs_pack_report.json`、`embedded_delta_report.json` 均为 PASS：3744 路径、524 `.gde`、524 `.gd.remap`、1 plain `.gd`，嵌入复提取与 pack 树 SHA 完全一致
- `embedded_text_report.json` 为 PASS：最终嵌入/复提取的 `Scenes/Menu.tscn` 含 `开始游戏`，目标字段不再含 `text = \"Play\"`
- `boot_probe.txt` 为 PASS：真实 `Mutagenic` 窗口、无 ALERT、无 fatal project-load marker
- 视觉 Gate 不宣称 PASS：`visual_evidence_review.json` 登记为 `HUMAN_REQUIRED`。当前桌面环境的屏幕捕获落到了 TraceMemo，`PrintWindow` 为黑帧；这不否定结构/启动证据，但不能证明中文 glyph、布局或裁切

因此当前 `status.json` 中 `localization = HUMAN_REQUIRED`。下一步只需对上述 SHA 的候选做一次受控人工视觉检查；在此之前不得扩大翻译范围或宣称完整本地化通过。

### C5-L1 单一中文菜单字体能力实验已完成机器 Gate（2026-08-14 02:32 +08:00）

- Mod manifest：`mods/c5-l1-localization-menu-play-font/mod.json`，SHA-256 `B05D95616EDFF7344F840B39D8380CC11478BD2B65F4B81AC80105B16023FB90`
- 单一受控 delta：沿用 C5-L0 的 `Scenes/Menu.tscn:69:9`，`Play -> 开始游戏`；并将 `03_raw/Fonts/rsans.ttf` 的精确 preimage `120180C034232D7142F71F7F049465D7B37722241B769F9C1C812354F8E07E82` 替换为声明的 CJK 字体资产 `mods/c5-l1-localization-menu-play-font/assets/rsans.ttf`
- 字体资产 SHA-256 `B2D62DBAE45970DC7F2DCF098F4228703C2F598458EB4BFACF96B838624B10E2`；`font_coverage_rsans_report_v2.json` 中 `开始游戏` 四个 glyph 均存在、`fsType = 0`、license evidence 可追溯，coverage/license Gate 均为 PASS
- 从 `03_raw` 派生的 pack 树只包含两个声明 delta：`Scenes/Menu.tscn` 与 `Fonts/rsans.ttf`；证据为 `pack_from_mod_asset_report.json`、`pack_from_mod_asset_delta.json`、`pack_source_repro_report.json`
- 最终 PCK：`10_logs/C5-L1-localization-menu-play-font-20260814/c5_l1_menu_font_v3_normalized.pck`，SHA-256 `A51DC8277C5F2D18DA6EAA447E3334C0F576D937E730D9CF013F5DB4D090AA41`
- 最终 EXE：`10_logs/C5-L1-localization-menu-play-font-20260814/c5_l1_menu_font_v3_normalized.exe`，SHA-256 `1FFD924471C5C89B04DFF8E06BF5E227D0EB03F02B39D41FC1C1B38DFCAF3FA3`；来源为 `00_original/Mutagenic.exe`，未使用旧 modded EXE
- `pck_listing_v3.json`、`exe_structure_report_v3.json`、`exe_vs_pack_report_v3.json`、`embedded_delta_report_v3.json`、`composition_v3.txt`、`boot_probe_v3.txt` 均为 PASS；3744 条目完整 roundtrip，实际嵌入 delta 与声明一致，真实窗口启动且无 ALERT/fatal project-load marker
- 构建总记录：`10_logs/C5-L1-localization-menu-play-font-20260814/build.json`；实验记录：`experiment.json`
- 视觉 Gate 不宣称 PASS：`visual_evidence_review_c5_l1.json` 为 `HUMAN_REQUIRED`。foreground 与 GetWindowDC 截图都落到了同一 TraceMemo 画面，不能证明 glyph、字体 fallback、裁切或布局
- 后续 `capture_matrix_v11.json` 在单进程、目标窗口前台且可逆隐藏 TraceMemo 的条件下复测三种捕获路径；`screen`/`GetWindowDC` 仍为桌面，`PrintWindow` 为黑帧，三张图均为 `INVALID`，不能证明 glyph、字体 fallback、裁切或布局

因此当前 `status.json` 中 `localization = HUMAN_REQUIRED`。C5-L1 只证明单一中文 UI 单元与一个 CJK 字体资产可以经声明式流水线生成结构有效、可启动的候选；不证明视觉质量、核心 gameplay、存档、完整本地化或发布就绪。下一步只能对上述 SHA 的候选做一次受控人工视觉检查；通过前不得扩大翻译范围。
