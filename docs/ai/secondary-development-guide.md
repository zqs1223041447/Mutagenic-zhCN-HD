# Mutagenic 二次开发指引(Secondary Development Guide)

> **文档角色**:源码参考工程的一部分。定义"如何在本仓库内安全地扩展/维护/二次开发"。
> **权威契约**:本文件是对 `AGENTS.md` 的操作化解读,不替代 `AGENTS.md`。冲突时以 `AGENTS.md` 为准。
> **适用范围**:G 盘分支仓库 `G:\opencode-Mutageni` 内的本地研究/扩展(用户已确认目标为 LOCAL_PLAY_ONLY)。

---

## 1. 仓库心智模型(先理解,再动手)

```
00_original/   原版 EXE(神圣不可变)
03_raw/        原版 PCK 提取的运行时内容(提取校验后不可变,3744 路径)
04_recovered/  反编译参考源码树(525 个 .gd,仅作阅读/分析,禁止直接作为生产输入)
05_schema/     Game Schema(机器可读的游戏概念模型)
mods/<id>/     声明式 Mod 定义(mod.json + patches + translations + assets)
06_worktree/   生成的工作树(可丢弃,可再生成)
07_compiled/   编译产物(可丢弃)
08_pack/       打包暂存(可丢弃)
09_output/     输出(可丢弃)
10_logs/       证据与状态(status.json 为权威机器状态)
```

**关键规则**:生产构建 = 从 `03_raw` 复制 + 只覆盖 Mod 声明的 delta + 嵌入 `00_original` 的新鲜 EXE 副本。**未触碰的脚本/资源必须与 `03_raw` 逐字节一致。**

---

## 2. 推荐的开发工作流

### 2.1 阅读与定位

1. 查 `docs/ai/source-map.md`(逐脚本职责)定位目标脚本
2. 查 `docs/ai/scene-resource-map.md`(场景/资源依赖)确认影响面
3. 查 `05_schema/game_schema.json` 确认该实体的标识符/数值注册位置
4. 读 `04_recovered/<path>.gd` 的完整源码

### 2.2 修改一个值 / 文本 / 代码(最小路径)

| 修改类型 | manifest 位置 | 参照范例 |
|---|---|---|
| 数据值 | `mods/<id>/patches/` VALUE_PATCH | `mods/c1-one-value-menu-version/` |
| 代码 | `mods/<id>/patches/` CODE_PATCH | `mods/c2-one-code-menu-render/`、`mods/p7-fix-persistence/` |
| 资源属性 | `mods/<id>/patches/` RESOURCE_PATCH | `mods/c3-one-resource-help-label/` |
| 资产 | `mods/<id>/assets/` ASSET_PATCH | `mods/c4-one-asset-menu-background/` |
| 本地化文本 | `mods/<id>/translations/` TEXT_PATCH | `mods/c5-l1-localization-menu-play-font/` 等 |

### 2.3 标准构建链(所有机器 Gate 自动执行)

```powershell
# 1. 声明 Mod(修改现有 manifest 或新建 mods/<id>/mod.json)
# 2. 应用补丁 -> 编译加密 -> 打包 -> 嵌入 -> 验证
02_tools\venv\Scripts\python.exe scripts\patch\apply_mod.py ...     # 按 manifest 应用
02_tools\venv\Scripts\python.exe scripts\compile_encrypt_scripts.py  # 只编译声明变更的脚本
02_tools\venv\Scripts\python.exe scripts\build\...                   # pack + embed
02_tools\venv\Scripts\python.exe scripts\validate\...                # 结构/文本/校验 Gates
# 3. 启动验证(真实窗口 + 无 ALERT)
python scripts\probe_boot.py <candidate> --seconds 15
```

> 具体命令参数以各脚本 `--help` 与既有证据目录(如 `10_logs/C2-one-code-menu-render-20260813/`)为准;不要凭记忆拼命令。

### 2.4 人工验证

需要 GUI 视觉/交互确认时,遵循 `AGENTS.md §19`:

- 提供:精确候选路径 + SHA-256 + 相邻 DLL + 测试清单 + 预期结果 + 证明什么/不证明什么
- 结果记录为 SHA 绑定的人工检查点(非阻塞,不阻碍机器工作)

---

## 3. 硬性禁止(违反即污染)

1. **禁止**修改 `00_original/`、`03_raw/`、已验证的 `04_recovered/`
2. **禁止**在历史 modded EXE 上再打补丁(每次从 `00_original` 新鲜嵌入)
3. **禁止**全局文本替换 `.gd/.tscn/.tres/.json`(必须用结构化 patcher,精确字段定位)
4. **禁止**批量重编译所有恢复脚本(只编译 manifest 声明的)
5. **禁止**直接编辑 `06_worktree/` 后把编辑当生产输入(探索性编辑必须转成声明式 patch)
6. **禁止**忽略 PCK checksum 失败;禁止把"进程存活"当成功
7. **禁止**泄露脚本加密密钥(在 `manifests/script_key.txt` 本地,不入报告/日志)
8. **禁止**读取 F 盘原工作树内容(本分支会话约束;仅可捕获 OS 进程表元数据作 UNBOUND 观察)

---

## 4. 常见扩展场景速查

### 4.1 新增/调整技能数值

1. 定位:`05_schema/game_schema.json` → `skills.entities`(53 技能)/ `stats`
2. 修改源:技能定义通常在 `Globals/` 或 `Scenes/Skills/`(见 source-map)
3. 声明:`mods/<id>/patches/` CODE_PATCH 或 VALUE_PATCH,preimage 哈希必须匹配
4. 验证:编译只产生声明脚本 delta + 结构 Gate + boot

### 4.2 新增职业

1. 修改 `Globals/PlayableClasses.gd`(4 职业 / 8 专精注册表)
2. 注意存档兼容:`GameState` 的 checksum/stamp 契约与存档迁移逻辑
3. 若涉及角色创建 UI,同步 `Scenes/Popups/Dialogs/CharacterSelect/CharacterCreator.tscn`

### 4.3 新增地图/关卡

1. 参照 `Scenes/Levels/BaseLevel.tscn` 创建新场景
2. 在 `05_schema` 的 levels.config 对应注册表(源码中)登记 id/display_name/layout
3. 世界地图节点需在 world_map 数据(59 节点)中接线

### 4.4 本地化更多界面

1. 字符串分类(DISPLAY_SAFE / STRUCTURAL / AMBIGUOUS / DO_NOT_TRANSLATE)——见 `AGENTS.md §16`
2. 只翻译 DISPLAY_SAFE;保留占位符/路径/结构 ID
3. 字体:确认 CJK 字形覆盖(`Fonts/rsans.ttf` 为现有中文字体 overlay)
4. 每次一个 manifest 切片 + 回归(参照 C5-L1→C5-L5 递增方式)

### 4.5 保存/持久化相关

- 本地存档:`user://_0_6_0.dat`(`Constants.USE_STEAM=false` 后走本地 File 分支)
- 修改 `Globals/GameState.gd` 时必须保持 `compute_checksum/compute_stamp/verify_stamp` 契约,否则旧存档失效
- 不要修改共享 APPDATA 中由外部活动写入的 `_0_6_0.dat`(UNBOUND 观察)

---

## 5. 状态与证据纪律

- 每个实验/构建:唯一 build ID(`YYYYMMDD-HHMM-<phase>-<short-id>`),独立证据目录
- 每次改动后更新 `10_logs/status.json`(机器权威状态)+ `PROJECT_STATE.md`(交接摘要)
- 每个 Gate 必须有证据文件;PASS 必须注明"证明什么 / 不证明什么"
- 变更集必须可解释:最终 changed-path 集合 == manifest 声明(多一个文件即视为污染,直到解释清楚)
- 失败:先分类子系统 → 根因树 → 单变量实验 → 回滚到最新可信基线(不"就地修复"失败 EXE)

---

## 6. 快速链接

| 资源 | 路径 |
|---|---|
| 操作契约 | `AGENTS.md`(仓库根,权威) |
| 项目状态 | `PROJECT_STATE.md` + `10_logs/status.json` |
| 源码索引(机器) | `docs/ai/source_index.json`(525 脚本元数据) |
| 源码地图(人工) | `docs/ai/source-map.md` |
| 场景/资源引用图 | `docs/ai/scene-resource-map.md` |
| Game Schema | `05_schema/game_schema.json` |
| 可信基线 | `10_logs/clean_noop/clean_noop.exe`;本地游玩候选 `10_logs/P7-fix-persistence-20260814/runtime_candidate/Mutagenic.exe` |
| 历史范例 | `mods/`(c1-c5、p7-fix-persistence)+ 对应 `10_logs/*/build.json` |
