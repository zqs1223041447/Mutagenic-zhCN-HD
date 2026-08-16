# NL2MOD：自然语言驱动 MOD 修改框架

> 状态：**已实现 + 端到端验证**（2026-08-16）
> 一句话：用自然语言描述"我要改什么"，AI 定位修改点 → 生成声明式 MOD → 一键构建 → 应用到游戏并验证。

---

## 1. 这是什么

让用户用自然语言（如"把骷髅射手的移速提高 20%"）驱动 MOD 修改的完整框架。它**复用项目成熟的声明式 MOD 管线**（38 个现有 mod.json + resolve/apply/compile/pack/embed），在其上补齐两个确定性层：

```
用户自然语言
   │  (Layer 1: AI 用源码地图/schema 定位真实修改点)
   ▼
结构化 intent.json (文件路径 + 字段 + 旧值 + 新值)
   │  (Layer 2: scripts/nlmod/nlmod.py —— 确定性生成器)
   ▼
preimage 守卫的 mod.json (可被现有构建链消费)
   │  (Layer 3: scripts/nlmod/build_mod.py —— 一键流水线)
   ▼
候选 EXE（嵌入 PCK）→ 部署到 VM → 运行/语义验证
```

**关键设计**：
- **AI 是翻译器**（Layer 1）：把自然语言映射到具体文件/字段。由 AI 读 `docs/ai/source-map.md` + `05_schema/game_schema.json` + `04_recovered/*.gd` 定位。
- **脚本是执行器**（Layer 2/3）：`nlmod.py` 校验 intent 的 old_text 在真实源码中唯一存在、计算整文件 preimage；`build_mod.py` 串起全部构建步骤并 fail-closed。
- **可回滚**：每个 MOD 是独立 manifest + SHA 绑定候选，随时可回到 02-baseline。

---

## 2. 快速上手（30 秒）

### 2.1 表达意图（Layer 1 产物：intent.json）

```json
{
  "id": "mm-monster-speed-skeleton-archer",
  "scope": "Skeleton Archer movement_speed 65.0 -> 78.0 (+20%)",
  "patch_type": "CODE_PATCH",
  "patches": [
    {
      "path": "Globals/MonsterStats/MonsterStats.gd",
      "classification": "CODE_PATCH",
      "old_text": "\t...\"name\": \"Skeleton Archer\", ...\"movement_speed\": 65.0, ",
      "new_text": "\t...\"name\": \"Skeleton Archer\", ...\"movement_speed\": 78.0, ",
      "expected_occurrences": 1
    }
  ]
}
```

> **重要**：`old_text` 必须从 `04_recovered/<path>` **精确复制**（含制表符缩进），且在该文件中唯一（用 `expected_occurrences` 或带上下文锚点保证）。AI 定位字段的正确姿势见 §4。

### 2.2 生成 mod.json（Layer 2）

```powershell
02_tools\venv\Scripts\python.exe scripts\nlmod\nlmod.py `
  --intent mods\<id>\intent.json --out mods\<id>\mod.json
```
校验失败会拒绝（old_text 不唯一 / 文件不存在 / old==new）。

### 2.3 一键构建（Layer 3）

```powershell
02_tools\venv\Scripts\python.exe scripts\nlmod\build_mod.py --mod-id <id>
```
自动执行：`setup worktree(04_recovered) → resolve → apply → compile → pack → GDRE pck-create → normalize → 输出 normalized.pck`。输出在 `10_logs\nl2mod-<id>-<timestamp>\`。

### 2.4 嵌入 + 部署 + 验证

```powershell
# embed 到新鲜 00_original 副本
02_tools\venv\Scripts\python.exe scripts\embed_pck.py 00_original\Mutagenic.exe `
  <out>\<id>_normalized.pck -o <out>\Mutagenic_<id>.exe

# 语义确认（权威）：GDRE 从最终 EXE 恢复目标 .gde，验证新值已嵌入
02_tools\gdre\gdre_tools.exe --headless "--recover=<exe>" "--output=<dir>" `
  "--include=res://Globals/MonsterStats/MonsterStats.gde" "--key=<script_key>"

# 部署到 VM + 交互会话启动 + 日志验证（见 hyperv-mutageni-vm skill）
```

---

## 3. 已验证案例（端到端证据）

| 项 | 值 |
|---|---|
| 自然语言 | "把骷髅射手的移速提高 20%" |
| intent | `mods/mm-monster-speed-skeleton-archer/intent.json` |
| mod.json | `mods/mm-monster-speed-skeleton-archer/mod.json`（preimage `208c4145...`） |
| 构建链 | resolve/apply(1 file)/compile(1 script)/pack(3744)/pck-create/normalize **全 PASS** |
| 候选 EXE | `10_logs\nl2mod-mm-monster-speed-skeleton-archer-20260816-105641\Mutagenic_zhCN_mmspeed.exe` SHA `75F076FB...` |
| VM 启动 | 部署 VM + Mesa 软渲染 + zzz 交互会话，进程存活 responding |
| **语义确认** | **GDRE 恢复最终 EXE 的 MonsterStats.gde → `movement_speed: 78.0` ✓** |

---

## 4. AI 如何定位修改点（Layer 1 操作化）

1. **查职责**：`docs/ai/source-map.md` → 找到管目标实体的脚本（如怪物属性 → `Globals/MonsterStats/MonsterStats.gd`）
2. **查数据**：`05_schema/game_schema.json` → 确认实体标识符（如 `SKELETON_ARCHER`、字段 `movement_speed`）
3. **读源码**：`04_recovered/<path>.gd` → 读实际字段定义、缩进、相邻行
4. **构造 old_text**：从源码**精确复制**含目标行的文本块（建议含唯一性锚点，如相邻字段）
5. **验证唯一性**：写 intent 前先用 Python `text.count(old_text)` 确认 == expected_occurrences
6. **估算新值**：如"移速+20%" → 65.0 × 1.2 = 78.0；注意浮点保留格式一致（`78.0` 而非 `78`）

**常见修改类型速查**（沿用 secondary-development-guide §2.2）：

| 类型 | patch path | 参照 |
|---|---|---|
| 数值/代码 | `04_recovered` 对应 `.gd` | MonsterStats.gd、Genes.gd、技能脚本 |
| 资源属性 | `.tscn/.tres` 文本字段 | c3-resource-help-label |
| 资产替换 | `assets/` ASSET_PATCH | c4-asset-menu-background |
| 本地化文本 | `.tscn/.gd` 显示串 | c5-l* 系列 |

---

## 5. 硬规则（必须遵守）

1. **不修改** `00_original/`、`03_raw/`、`04_recovered/`（只读输入；worktree 是副本）
2. **不覆盖**已存在的 `mods/<id>/mod.json`（nlmod.py 拒绝）或构建 out 目录
3. **old_text 必须精确匹配**源码（含缩进），否则生成器/apply 拒绝 —— 这是防误改的守卫
4. **每次从 00_original 新鲜嵌入**（build_mod.py 的 embed 步骤独立于构建链，按 §2.4 执行）
5. **MOD 改变的是编译前 .gd 源码**：patch 路径用 `.gd`（源码），构建链自动产出 `.gde` + `.gd.remap`
6. **候选不自动晋升 baseline**：需用户批准（沿用 AGENTS.md）
7. **密钥** `manifests/script_key.txt` 本地使用，不写入报告/日志/代码

---

## 6. 扩展路径（下一步）

- **意图模板库**：把常见修改（数值比例调整、技能伤害、怪物属性、投射物行为）沉淀为 intent 模板，AI 直接套用减少错误
- **一键全链**：`build_mod.py` 增加 embed + GDRE 语义确认步骤（当前停在 normalized.pck，embed 由调用方执行）
- **自动部署**：集成 VM 部署 + 交互会话启动 + 截图验证（基于 hyperv-mutageni-vm skill）
- **回滚自动化**：checkpoint 03-pre-mod + 每次 MOD 构建前自动打点

---

## 7. 相关文件

| 文件 | 作用 |
|---|---|
| `scripts/nlmod/nlmod.py` | Layer 2：intent → mod.json（preimage 守卫） |
| `scripts/nlmod/build_mod.py` | Layer 3：mod.json → normalized.pck（一键流水线） |
| `mods/mm-monster-speed-skeleton-archer/` | 验证案例（intent.json + mod.json） |
| `docs/ai/source-map.md` / `scene-resource-map.md` | 定位修改点的地图 |
| `05_schema/game_schema.json` | 实体/字段注册表 |
| `docs/ai/secondary-development-guide.md` | 构建链权威描述 |
