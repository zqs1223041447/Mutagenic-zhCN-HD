# AGENTS.md — Mutagenic 工程治理协议（唯一全局规范）

> **Authority**: 本文件是仓库的**唯一全局规范**（L0）。所有 AI 开始工作前必须读它。
> **Scope**: 只写全局硬规则。Hyper-V/VM 操作、NL2MOD 实现、汉化切片详情、GDRE 手册等全部下放到对应子文档，不在此重复。
> **Supersedes**: `AGENTS1.md`（旧版，已重构为本文件）。冲突以本文件为准。

---

## 1. Mission

从原版游戏 EXE 出发，经确定性管线产出可验证的汉化/MOD 构建，保持可复现、可回滚、证据可追溯。

```
pristine game → fingerprint → raw extraction → recovered source → schema
  → declarative MOD → resolve/apply/compile/pack → fresh embed
  → candidate → roundtrip/boot/semantic verify → evidence
  → human-only promote → baseline
```

**VM 定位**：VM 是部署/运行/观察/语义验证的执行环境，**不是**构建系统。canonical build 由宿主固定管线生成。
**NL2MOD 定位**：NL2MOD 是“自然语言 → 声明式 MOD”的前端，**不得**复制第二套构建逻辑。

---

## 2. 资产分类（判断一切文件该不该进 Git / 能不能删）

| 类别 | 含义 | 进 Git | 可删除性 |
|---|---|---|---|
| Source of Truth | 规则、脚本、MOD 声明、人工数据 | ✅ | 只能经 Git 变更 |
| Immutable Provenance | 原版（`00_original`） | ❌ 版权资产永不入库 | 永不删除 |
| Recovered Provenance | 提取物（`03_raw`）、恢复源码（`04_recovered`） | ✅，必须 byte-preserving | 永不删除/修改 |
| Generated | worktree/compiled/pack/candidate | ❌ | 可重新生成，可清理 |
| Evidence | manifest/验证报告/日志/截图 | manifest✅ 大证据❌ | 按等级归档 |
| Local Environment | venv/GDRE/密钥/VM/node_modules | ❌ | 可重建 |

`03_raw/**` 与 `04_recovered/**` 虽然进入 Git，但仍属于**不可变恢复来源**，必须由 `.gitattributes` 以 byte-preserving 方式存储，禁止行尾规范化破坏 preimage SHA。

---

## 3. 非协商不可变规则

1. **`00_original` 神圣不可变**：原版 EXE 只能读取；每次构建从它**新鲜嵌入**，绝不在历史 modded EXE 上叠加。
2. **`03_raw` 提取校验后不可变**：3744 路径，`manifests/raw_manifest.json` 绑定；已入 Git 但禁止编辑/重建。
3. **`04_recovered` 恢复后不可变**：5058 文件，`manifests/recovered_clean_manifest.json` 绑定；已入 Git但只读参考，禁止修改。
4. **Generated 目录**（06_worktree/07_compiled/08_pack/build/*）可随时重建，不算资产。
5. **失败构建是 forensic artifact**：保留证据但不作为生产输入。

---

## 4. 状态权威（Truth Matrix）

| 问题 | 唯一答案来源 |
|---|---|
| 哪些行为禁止？ | **AGENTS.md**（本文件） |
| 当前版本/状态？ | **`status.json`**（唯一机器权威源） |
| 人类可读当前状态？ | `PROJECT_STATE.md`（**从 status.json 生成**，不人工维护） |
| 原版指纹/提取/恢复清单？ | `manifests/provenance/*` |
| 哪些 MOD 构成版本？ | `modset.lock.json`（待建） |
| 如何构建？ | canonical pipeline（scripts/pipeline + docs/architecture/PIPELINE.md） |
| 如何跑游戏/验证？ | VM workflow（docs/dev-environment + Hyper-V skill） |
| 哪个版本是 baseline？ | release registry（status.json + releases/*.json） |
| 如何做构建性能优化？ | `docs/build/COMPILE_PERFORMANCE_PLAN.md`（L2 构建性能权威，AGENTS.md §6.1 仅入口） |
| 历史大文件在哪？ | 本地配置的 archive root；仓库不得硬编码宿主绝对路径 |

> 规则：一个问题的答案只有一个权威源。任何文档与 status.json 冲突时，以 status.json 为准。

---

## 5. 硬性禁止（违反即污染）

1. **禁止仓库代码、MOD、manifest 和自动化脚本硬编码宿主绝对路径**（包括盘符路径、UNC、固定用户目录）。仓库内部资源必须从 repo root 推导；仓库外资源必须来自本地配置、环境变量、CLI 参数或可靠的工具发现。
2. **宿主路径安全策略不得因为可移植化而放宽**：未经显式本地配置/白名单的外部路径必须 fail-closed。历史机器上的特定工具盘符只能作为本地配置值，不能成为仓库常量。
3. **禁止修改** `00_original/`、`03_raw/`、`04_recovered/`。
4. **禁止**全局文本替换 `.gd/.tscn/.tres/.json`（必须结构化 patcher，精确字段定位 + preimage 守卫）。
5. **禁止**批量重编译所有恢复脚本（只编译 manifest 声明的）。
6. **禁止**把 `06_worktree/` 手工编辑当生产输入（探索性编辑必须转声明式 patch）。
7. **禁止**忽略 PCK checksum 失败；**禁止**把“进程存活”当成功。
8. **禁止**泄露脚本加密密钥（`manifests/script_key.txt` 本地，不入库/日志/报告）。
9. **禁止**把候选 EXE 自动晋升 baseline（必须人工显式批准）。

---

## 6. 构建与验证最低要求

- **声明式 MOD**：所有改动必须是 `mods/<id>/mod.json`（CODE_PATCH/VALUE_PATCH/RESOURCE_PATCH/ASSET_PATCH/TEXT_PATCH），带 preimage_sha256 + expected_occurrences。
- **canonical pipeline**（唯一构建路径）：resolve → apply → compile → pack → **fresh embed**（从 00_original）→ candidate。
- **每个 build 有唯一 Build ID**（`YYYYMMDD-HHMMSS-<hash>`），产出 manifest 记录：git_commit/game_fingerprint/schema_hash/toolchain_hash/modset_hash/original_exe_hash/candidate_exe_hash/**encryption_key_id**（只记 id 不记 key）/build_time/host。
- **验证分层**：
  - S0 结构（roundtrip 3744/3744、delta 精确、PCK checksum）
  - S1 boot（真实窗口/进程 + 无 ALERT + 无 fatal）
  - S2 core smoke / S3 persistence / S4 mod-specific / S5 visual（按需）
  - **语义确认**：GDRE 从最终 EXE 恢复目标 .gde，确认新值已嵌入（权威，不靠 UI）。
- 每个 Gate 必须有证据文件（verified_at/command/artifact）；PASS 注明“证明什么/不证明什么”。

### 6.1 构建性能双模式（渐进式披露入口）

> **渐进式披露**：本节仅声明全局硬规则与默认行为，完整 20 章执行方案、验收标准与实施顺序见 `docs/build/COMPILE_PERFORMANCE_PLAN.md`（L2 构建性能权威）。凡任务涉及 `compile / pack / PCK / embed / verify / 构建耗时`，AI 必须先读该文件再执行，不得仅凭本节摘要猜测细节。

- **双路径**：`FAST DEV BUILD`（日常迭代，默认）vs `CANONICAL RELEASE BUILD`（中央集成/Promotion/baseline/PR Gate/最终证据，必选）。
- **默认行为**：开发期默认 `--mode fast`；Promotion Candidate / baseline 必须 `--mode release`。`FAST` 产物标注 `NOT PROMOTION ELIGIBLE`，不得晋升 baseline。
- **加速前提**：`FAST` 允许持久编译缓存、toolchain attestation 复用、base hash index 复用、persistent pack staging、collision-safe batching 与 quick checks；`RELEASE` 必须 fresh resolve/apply、validated 编译、fresh pack、full PCK+normalize、fresh embed、3744/3744 verify 与全量 roundtrip/S0~S4。
- **不可为提速削弱验证**：`normalize_pck_md5` 与 `verify_exe_structure` 的 RELEASE 全量 Gate 不得增量化；`00_original/03_raw/04_recovered` 仍不可变；禁止 hardlink `03_raw` 到可写 pack、禁止在旧 modded EXE 上叠加、禁止跳过 preimage、禁止抽样冒充完整 Gate、禁止硬编码宿主绝对路径。
- **缓存与可移植性**：默认缓存 `<repo_root>/.cache/`（含 `gdre/`、`pack_stage/`、`base_index/`、`build_profile.json`），已 `.gitignore`；可经 `MUTAGENIC_CACHE_ROOT` 覆盖；cache key 必须包含 `相对路径+源码SHA+GDRE SHA+bytecode版本+编译工具版本+key指纹(SHA)`，禁止落盘真实 key。
- **并发纪律**：Coding 可并行，Heavy Build / Verify 默认各 1 槽（build semaphore），禁止 `N Agent × M GDRE workers` 抢占；CLI `--workers` > `build_profile.json` > 安全默认值。
- **执行顺序**：严格 `Timing → Cache → Worker/Queue → Attestation/Index → Batching/Staging → FAST/RELEASE → pck-patch 实验`，每步 `实现→benchmark→回归→commit→push` 后再下一步；单步提速 <5% 且显著增复杂则不入 canonical，任何 `.gde/PCK` 不一致或 S0/S1/S3/S4 回归立即 rollback。
- **报告**：`FAST`/`RELEASE` 均须打印分阶段耗时与 cache/GDRE 统计，并落盘 `10_logs/<build-id>/timing.json` + `build.json`；Release 回归需 `check_all/abs_path_scan/secret_scan` 全过。

---

## 7. 证据保留策略

- **E0 Provenance**（指纹/提取/恢复 manifest）：永久保留。
- **E1 Accepted Release Evidence**（accepted build 的 roundtrip/boot/semantic/acceptance）：永久保留。
- **E2 Development Evidence**（中间 build/P7 实验/历史验证）：归档到本地配置的 `<archive_root>/evidence/`，不留在活动工作区；`archive_root` 不能写死在仓库代码中。
- **E3 Ephemeral**（NL2MOD 临时 smoke/失败中间产物/重复 candidate）：允许 TTL 清理（保留 manifest + 索引后）。

> 规则：不得不可逆丢失具有 provenance 或 accepted-release 价值的证据。E2/E3 在产生完整 manifest + SHA256 + archive index 后可移出活动工作区。

---

## 8. Git 规则

- **仓库包含**：规则、脚本、MOD 声明、manifest、人工数据、schema contracts、**Recovered Provenance**（`03_raw/04_recovered`，byte-preserving）。**不含**：原版游戏二进制（`00_original`/EXE/DLL/PCK）、venv、node_modules、10_logs、build 产物、archive。
- `.gitignore` 与 `.gitattributes` 必须共同保证：`00_original` 和生成物不入库；`03_raw/04_recovered` 入库但字节不被转换。
- 提交前跑 secret scan（key/credential/.env 检测）。
- **分支策略：trunk-based**。长期只有 `main`；工作分支按任务 `mod/xxx`、`feat/xxx`、`fix/xxx` 或批次任务 `agent/<batch>-<task>`，合完即删。
- **里程碑用 git tag**（`zhcn-v8.1`、`pipeline-v1`、`nl2mod-v1`），不用长期分支。
- 初始/大批量提交分次进行，禁止 `git add .` 一锅端。
- **AI Git 发布通道适配**：当 AI 运行环境已经提供对本仓库具有写权限且已完成认证的 GitHub Connector / GitHub API 工具时，该通道本身视为已完成 GitHub 身份认证；**不要求额外执行本地 `gh --version` 或 `gh auth status`，也不得仅因运行环境缺少 `gh` CLI 阻断提交、推送或 PR 更新**。只有实际选择本地 `gh` CLI 作为发布通道时，才需要检查 `gh` 可用性与认证状态。
- 上述 Connector/API 豁免**只豁免本地 `gh` 前置检查**，不豁免提交范围确认、目标分支确认、diff/文件审查、secret scan、不可变资产保护、PR Draft 策略与验证要求。
- 本项目由 AI 产生的 commit message、push/PR 说明与开发交接默认使用中文；命令、代码标识符与上游固定字段按原格式保留。

---

## 9. 路径与可移植性

### 9.1 Repo root 是唯一工程定位基准

- 用户可以把仓库 clone 到任意本地目录；**仓库不得假设盘符、用户名、父目录或 clone 位置**。
- 所有仓库内部路径必须从 `repo_root` 推导。首选 `git rev-parse --show-toplevel`；不能调用 git 时可从当前脚本文件位置向上定位仓库标记文件。
- 文档和任务描述使用 `<repo_root>/...`、`<archive_root>/...`、`<task_root>/...` 等逻辑路径，不把某台开发机的绝对路径复制成规范。

### 9.2 仓库外资源必须显式注入

- 工具链、归档目录、VM 部署目录、`00_original` 等仓库外路径，必须通过以下一种方式获得：本地忽略配置、环境变量、CLI 参数、PATH/注册工具发现。
- 推荐环境变量命名统一使用 `MUTAGENIC_*_ROOT`；具体变量由对应 workflow/脚本定义，不在多个脚本中发明不同名称。
- 本地绝对路径可以存在于**不入 Git 的本地配置/日志**中，但不得进入可移植的 Source of Truth。

### 9.3 禁止路径拼接脆弱性

- Python 使用 `pathlib.Path`；PowerShell 使用 `Join-Path` / `Resolve-Path`；不得手工字符串拼接盘符和反斜杠。
- 路径比较前必须规范化；涉及安全边界时必须解析 real path 后验证仍位于允许 root 内。
- 自动化脚本必须可从 repo 内任意工作目录启动，不能依赖调用者先 `cd` 到某个固定目录。

### 9.4 静态检查

- 自动化必须提供 repo-wide absolute-path scan，对 `.py/.ps1/.bat/.cmd/.json/.yaml/.yml/.toml/.gd/.tscn/.tres` 中新增的宿主绝对路径进行阻断或显式白名单审查。
- 测试夹具、错误消息、文档示例如果必须出现绝对路径，必须放在明确的 test/example 范围，不能被生产代码读取为默认值。
- 行尾：`.md/.json/.yaml/.py/.gd` 用 LF，`.ps1/.bat/.cmd` 用 CRLF；`03_raw/**`、`04_recovered/**` 例外遵循 byte-preserving `.gitattributes` 规则。

---

## 10. AI 工作入口

新任务开始固定读取：
1. `AGENTS.md`（本文件）
2. `status.json`
3. `docs/ai/AI_ENTRYPOINT.md`（任务路由）
4. 任务对应 workflow 文档（docs/workflows/）

任务路由（详情见 AI_ENTRYPOINT）：
- 汉化请求 → `mods/localization` → canonical build
- 自定义 MOD → 手工 mod.json 或 NL2MOD → canonical build
- 自然语言需求/疑问（非明确命令）→ **按需**加载 `nl2mod-requirement-analysis` skill
- Kinetic Arcane / 战斗手感 / Player Response / Hit Reaction / Kill Feel / Combat Camera/Audio / Build Density → `docs/requirements/KINETIC_ARCANE_REMASTER.md` + `docs/requirements/COMBAT_VERTICAL_SLICE.md`
- 并行批次 / X1、X2… 多 Agent 认领 → `docs/ai/PARALLEL_BATCH_WORKFLOW.md`
- Runtime bug → canonical candidate → VM verification
- 管线 bug → scripts/pipeline；VM/工具链 bug → scripts/vm
- 构建/编译/打包耗时优化或 FAST/RELEASE 迭代 → `docs/build/COMPILE_PERFORMANCE_PLAN.md`（必读后再动 `scripts/build/*.py`）

---

## 11. AI 自动化铁律

1. 远程 VM 命令必须显式提供对应凭据/非交互认证；忘传凭据导致的 guest 服务风险必须 fail-closed。
2. 回滚/删除类命令一律显式非交互确认策略，避免无人值守流程挂死；同时必须受允许 root/任务范围保护。
3. 脚本内禁用交互式 shell/session；长任务输出重定向到日志防缓冲阻塞。
4. 等待就绪用轮询（状态 + 心跳 + 实际命令探测），不裸 sleep。
5. 关键步骤必须 fail-fast + try/catch/异常捕获 + 失败日志落盘。
6. 普通构建失败、测试失败、可恢复依赖问题或局部实现选择**不得自动升级成人工阻塞**；AI 应在任务授权范围内自行诊断、修复、重试并推进到最远可验证状态。

---

## 12. 批次并行与最少人工操作

1. **默认目标是无人值守的大批次进展**：对于可以并行的研发工作，由协调 AI 拆成 `X1/X2/X3...` 独立 workstream；执行 AI 一次认领后应覆盖审计 → 实现 → 构建 → 验证 → 修复 → commit/push → 交接，而不是每发现一个函数就等待用户确认。
2. **用户只需要 clone 一次仓库**。并行 Agent 禁止各自重新 clone；应使用 Git worktree 或等价隔离机制，并从当前 `repo_root` 自动推导任务目录。
3. **并行 Agent 不能共享同一个可写 working tree**。每个任务必须有独立 branch + 独立 task worktree；任务 worktree 的实际绝对路径由自动化生成，用户不需要手工输入。
4. 推荐逻辑布局为 `<repo_parent>/<repo_name>.worktrees/<batch>/<task>`；这是运行时推导规则，不是固定宿主路径。完成集成后自动清理已合并 task worktree。
5. **中央集成**：执行 Agent 不自行把多个 sibling task 合成最终线。所有 Xi 完成后，由协调 AI 统一检查 base SHA、diff、preimage 漂移、依赖、冲突和验证结果，再决定 merge/rebase/cherry-pick 顺序并运行 aggregate regression。
6. **人工操作最小化**：任务包必须可直接交给 AI 认领；默认不要求用户手工建分支、计算路径、复制文件、逐项执行测试或手工整理报告。
7. **允许真正人工阻塞的 Gate**：baseline promotion；不可逆资产操作；无法通过证据自动判断的最终 S5 体验验收；需要用户凭据/外部实体授权且工具无法安全取得；无法自动消解且会改变产品意图的冲突。
8. 每个 Xi 最终交接至少包含：task_id、branch、base_sha、final_sha、修改文件、MOD/工具产物、Build ID、S0/S1/S2/S4/S5 状态、失败重试记录、潜在冲突路径、剩余风险、推荐集成顺序。

---

*权威层级：AGENTS.md（L0）> status.json（L1 机器状态）> 子文档（L2，含 `docs/build/COMPILE_PERFORMANCE_PLAN.md` 构建性能权威）。SKILL.md 是执行适配层，不是政策制定者；不得复制一套新规则。*