# B3 — Control Plane Closure & Build Density Baseline

> **Batch ID**：`B3`
> **状态**：OPEN FOR CLAIM（B3-P0 四任务）
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **Planning/prep base**：`batch/b3-anchor` = `68bb1c184dfab3a96554fd3d7c52581ef6c6a266`（= B2-I1 集成 HEAD，本地=远端已核验）
> **来源**：GPT 评审（2026-08-20，会话 6a83bc24）——B2-I1 判定"有条件 PASS"，批准立即启动 B3-P0；Combat Polish 调参保持 WAITING_HUMAN_S5。
> **PR 策略**：PR #1 保持 Draft；B3-P0 元数据/证据修正并入 PR #1，B3 大规模 Gameplay 后续另开 PR。

## 0. 背景与 Gate

B2-I1 COMPLETE（S0/S1/S4 PASS，S2 BLOCKED 如实，S5 machine EVIDENCE_PREPARED）。GPT 评审指出 4 个需补强问题：

| 优先级 | 问题 | 归属 |
|---|---|---|
| P0 | S2 `save_loaded=false`、F10 已发送但 telemetry 未出现 —— 不得长期当"环境限制"搁置，应专项解决 | B3-X0 |
| P0 | `mods/b2-i1-aggregate/mod.json` 写了不存在的 `b2-x2-combat-timing` 并声称 15 mods（实际 resolution_order 14 mods）—— 元数据错误，B3 前必须修正 | B3-X2 |
| P0 | `check_all` 只注册到 Event Spine，未注册 Kill Feel / Camera / Combat Audio / S5 selftest —— 无人值守回归漏检风险 | B3-X1 |
| P1 | B2_STATUS 顶部 COMPLETE 但底部保留旧"启动 B2"指令；PR body 部分 branch/SHA 控制字符转义污染 | B3-X2 |

**Gate 规则**：四项 P0 均不得等待 HUMAN S5；Combat Polish 实际调参（B3-X4+）与 Density 数值实验依赖 H-S5 反馈 + S2 PASS，暂不启动。Baseline promotion 绝对禁止（需 S2 PASS + HUMAN S5 PASS + 元数据修正 + 最终 fresh rebuild 全验证）。

## 1. 执行原则

- 所有任务从 `batch/b3-anchor`（68bb1c1）同一 SHA 出发，独立 branch + worktree（batchctl claim，worktrees 位于 `<repo_parent>/Mutagenic-zhCN-HD.worktrees/B3/<task>`）。
- 禁止修改 `00_original/03_raw/04_recovered`；不触碰 B2 历史证据文件（只允许**新增** supplemental 证据，或经 X2 明确授权的元数据修正）。
- 每任务验收：显式 git add → 中文 commit → push 各自 branch → `git ls-remote` 核验；S0/S1/S2/S4/S5 状态如实上报。
- 完成后由协调 AI 中央集成（merge-tree 预检 → 依序合并 → aggregate 回归）。

## 2. B3-P0 任务合同

### B3-X0 — S2 Runtime Route Recovery

**目标**：定位 `save readiness → goto_test_level → TestLevel entered → harness request consumed → telemetry write` 的断点，增加可观测性，恢复真实 S2 telemetry 产出。

**范围**：
- 审计 `scripts/validate/launch_harness_game.py`、`scripts/validate/combat_harness.py`、`scripts/validate/combat_harness_selftests.py`、`scripts/validate/combat_telemetry_schema.json` 与 launcher 键盘序列路由；
- 若仅为 runner/tooling 缺陷：修复后**用原 B2-I1 Candidate（hash 不变，103,341,700 bytes）重新跑 S2**，新增 `docs/ai/audits/B2-I1_S2_SUPPLEMENT.json`（不修改原 B2-I1_AGGREGATE_EVIDENCE.json 的 BLOCKED 历史记录）；
- 若必须修改 gameplay/mod 才能让 harness 工作：不得倒填 B2 PASS，作为 B3 candidate 验证；
- 最后若确需 VM 才能继续：如实记录 BLOCKED + 明确断点结论与可观测性改进，交人工核查项。

**验收**：S2 从 BLOCKED 推进为（a）相同 Candidate 的 supplemental PASS 证据，或（b）带断点结论的明确 BLOCKED + 修复计划；不伪造 PASS；不改 B2 历史证据。

### B3-X1 — Verification Control Plane Closure

**目标**：`check_all` 统一注册全部语义契约 + S5 selftest；建立 repo-only GitHub CI（不依赖原版 EXE 的静态/语义测试）。

**范围**：
- `scripts/ai/check_all.py` + `scripts/ai/check_all_components.json`：Event Spine 改为 required，注册 Kill Feel 80/80、Camera 93/93、Combat Audio 120/120、audio selftest 14/14、S5 selfcheck 23/23；
- 新增 GitHub Actions workflow（`.github/workflows/`）：静态/语义契约测试（abs-path scan、secret scan、semantic contracts、selftests），不依赖 `00_original`/EXE/fresh embed；
- 控制面代码必须可移植（无宿主绝对路径），通过 abs-path scan + secret scan。

**验收**：本地 `check_all` 全组件 PASS 且覆盖全部已注册契约；CI workflow 语法正确（无法在线验证则提供 dry-run/act 或说明）；abs-path production_hardcode=0、secret findings=0。

### B3-X2 — Evidence / Status / PR Hygiene

**目标**：修正 B2 交付元数据与文档卫生，不触碰验证结论。

**范围**：
- `mods/b2-i1-aggregate/mod.json`：修正 `scope` 中不存在的 `b2-x2-combat-timing`、`proves` 中 15 mods → 与实际 resolution_order 一致的 14 mods（改动限文本字段，不得改动依赖解析语义）；
- `docs/ai/batches/B2_STATUS.md`：清理底部旧"启动 B2"指令块，顶部状态与正文一致；
- PR #1 body：清理 branch/SHA 控制字符转义污染（via gh API 或本地 gh；不改变 Draft 状态）；
- `status.json`：保持 `visual_ui_remaster=IN_PROGRESS` 不变，补 B2-I1 的**非 baseline** gate_scope/evidence 条目（不得写 trusted baseline、不得冒充 promotion）。

**验收**：mod.json 元数据与实际 resolution 一致；B2_STATUS 无残留旧指令；PR body 干净；status.json 仅新增非 baseline 条目；commit/push 核验；不触碰 03_raw/04_recovered。

### B3-X3 — Build Density Benchmark Scaffold

**目标**：只建立性能场景/指标/阈值框架，不提高正式游戏密度。

**范围**：
- 定义压力阶梯：5/20/50/100 同屏敌人；
- 指标：frame-time / FPS / event-rate / voice budget / camera budget（复用 B2 harness/telemetry 能力，禁止新总线）；
- 产出：`docs/ai/batches/B3_DENSITY_BENCHMARK.md`（场景矩阵、指标定义、阈值草案、执行方法）+ 可运行 scaffold（脚本/契约，能 offline 自测）；
- 明确"当前不修改任何 gameplay 密度数值"，仅基线框架。

**验收**：文档 + scaffold 自测通过；不触碰正式游戏密度；不要求 VM 即可验证框架本身（真实运行数据可留待后续）。

## 3. 不在此批做的事

- ❌ Combat Polish 实际调参（Kill/Camera/Audio 数值）→ WAITING_HUMAN_S5
- ❌ 真实增加战斗密度实验 → 依赖 S2 PASS + S5 稳定
- ❌ Baseline promotion / status.json trusted baseline 写入
- ❌ 修改 B2 历史证据文件（只允许新增 supplemental 证据）
- ❌ 修改 `00_original/03_raw/04_recovered`

## 4. 集成与后续

全部 B3-P0 完成后：协调 AI 中央集成 → 全契约回归 → push 协调线 → 更新 B3_STATUS 与 PR → 再次 GPT 评审；同时吸收用户 S5 八项反馈决定 B3 Combat Polish 与 Density 执行批次。

---

# B3-P1 — Diagnostics / Readiness Wave（GPT 评审 2026-08-20 批准）

> **Base**：`batch/b3-p1-anchor` = `de039a6`（B3-P0 集成 HEAD）
> **状态**：OPEN FOR CLAIM
> **背景**：GPT 评审 B3-P0 PASS；CI 仅为 `CI_CONFIGURED / LOCAL_PASS, GITHUB_RUN_NOT_PROVEN`；S2 冻结已缩到 do_save_game 附近，需宿主侧 bisect；S5 反馈需预建映射以快速响应。

## 执行原则

- 三个任务并行，独立 branch + worktree（batchctl claim）；
- **禁止**实际 Combat Polish 调参（WAITING_HUMAN_S5）；**禁止**提高正式 Density（WAITING_S2_AND_S5）；**禁止** baseline promotion；
- **禁止**倒填 B2 历史 S2 PASS；不修改正式 gameplay（X1 只做 diagnostic tooling/MOD）；
- X1 的 diagnostic MOD 必须走声明式 mod.json（apply_mod 硬约束：old_text 必须存在于原始 04_recovered 内容，preimage=整文件 SHA）；不改正式 B2 evidence。

## 任务合同

### B3-P1-X0 — CI Bring-up

查明 `ci-static-semantic` 在 de039a6 无远端 workflow run / combined status 为空的原因（候选：workflow 文件只存在于非默认分支、`on: push` 对非默认分支不触发、Draft PR 不触发等），修复触发/权限/配置问题并取得**真实 GitHub Actions PASS**。不得用本地 PASS 冒充云端 PASS。验收：远端 workflow run 存在且 PASS（或明确证明当前仓库配置下不可达 + 修复方案），PR required gate 准备状态说明。

### B3-P1-X1 — S2 Save Bisect

不改变正式 gameplay；围绕 `GameState.do_save_game()`（compute_checksum → compute_stamp → JSON.print → File.open/store/close → _on_save）以**声明式 diagnostic MOD** 写磁盘级 marker（before/after 每子步骤）；三组 control：① 当前 generated seed save、② 历史已验证正常真实 save、③ 无 save/fresh profile。目标：把冻结缩到具体调用子步骤；无法继续时才生成 VM/hang-dump handoff。复用 B3-X0 的 launch_harness_game.py v2 可观测性。验收：bisect 结论（冻结子步骤定位）+ 三组 control 结果 + diagnostic MOD/工具提交；不得倒填 B2 历史 S2 PASS。

### B3-P1-X2 — S5 Feedback Intake

不修改 gameplay；建立当前 8 项 S5 人工验收 checklist → Kill Feel / Camera Impulse / Combat Audio 各 tunable 参数（含允许调整范围）→ 对应 semantic contract → 需要重跑的 regression/Gate 的映射文档。用户反馈返回后即可自动生成 Combat Polish 调参任务。验收：`docs/ai/batches/B3_S5_INTAKE_MAP.md`（或等价文档）+ 映射校验（每个 checklist 项可追溯到具体 tunable/contract）。

## B3-P1 集成

三任务完成后：merge-tree 预检 → 依序合并 → check_all 全量 → push → 更新 B3_STATUS/PR → GPT 评审；继续等待/吸收 HUMAN S5 反馈。

## Promotion 条件（GPT 强化，含新增 S3）

S0 + S1 + S2 + S3 + S4 PASS + HUMAN S5 PASS + GitHub CI PASS + final fresh rebuild + 用户显式批准。顺序：修通 S2 → HUMAN S5 → 必要 Combat Polish → fresh aggregate rebuild → S0/S1/S2/S3/S4 → 受调参影响项重新 HUMAN S5 → CI PASS → 用户显式 promotion。PR #1 在此之前保持 Draft。

---

# B3-P2 — S2/S3/发行候选边界收口（GPT 评审 2026-08-20 批准）

> **Base**：`batch/b3-p2-anchor` = `60f9232`（B3-P1 集成 HEAD）
> **状态**：OPEN FOR CLAIM
> **背景**：GPT 评审 B3-P1 PASS（CI GITHUB_RUN_PASS 采纳）。S2 已证 save 路径无冻结、TestLevel 路由到达、harness spawns=started，剩余问题=玩家 3–5s 死亡而 telemetry 需 ~20s 完成——已从"环境未知"转为"确定性测试 harness 生命周期问题"，无需 VM。promotion 前必须处理 b2-x0-combat-harness-bridge 写入 ENABLE_TEST_ZONE=true 的风险（不应默认随 baseline 晋升）。

## 执行原则

- 三任务并行，独立 branch + worktree（batchctl claim）；
- **禁止**修改正常 gameplay 数值（Combat Polish WAITING_HUMAN_S5）；**禁止**真实 Density 提升（WAITING_S2_PASS_AND_S5_STABLE）；**禁止** baseline promotion；
- 验证 Candidate 允许 harness/ENABLE_TEST_ZONE；Promotion Candidate 必须剥离 diagnostic/test-only route/ENABLE_TEST_ZONE=true；
- 不修改 `00_original/03_raw/04_recovered`；apply_mod 硬约束（old_text 存在于原始 04_recovered 内容，preimage=整文件 SHA）；
- X0 必须真实跑出 telemetry 才能写 S2 PASS，不得伪造。

## 任务合同

### B3-P2-X0 — S2 Telemetry Closure

完善 combat harness telemetry 生命周期：scenario 启动即创建 telemetry/session 文件；周期 checkpoint（固定间隔 flush）；player death / scene exit / timeout 均 flush 并记录 `exit_reason` + partial telemetry；新增仅在 harness/TestLevel 下生效的确定性 nonlethal `runtime_smoke_safe` 场景（test-only：enemy_damage_scale=0 或 player_invulnerable=true，普通游戏绝不受影响），使 S2 稳定跑到 final telemetry。证明链：boot → load → hideout → TestLevel → spawn → main loop → harness runtime → telemetry → clean completion。**不修改正常 gameplay 数值**（test-only 豁免必须限定在该 harness 场景显式开启时）。验收：真实跑 S2 取得 final telemetry 后写 PASS（或如实记录 BLOCKED+原因）；telemetry 含 exit_reason/checkpoint 证据。

### B3-P2-X1 — Validation/Promotion Candidate Separation

正式区分双 modset：
- **Validation Candidate** = 正式 gameplay mods + harness + `ENABLE_TEST_ZONE=true`（b2-x0-combat-harness-bridge 现状）；
- **Promotion Candidate** = 相同正式 gameplay mods − diagnostic mods − test-only route − `ENABLE_TEST_ZONE=true`；
建立 gameplay parity contract：证明两者除调试入口外行为/正式 MOD 完全一致（如 resolve 链对比、非 harness patch 集一致、patch 集差集仅限 harness 相关）。产出：modset 定义（mods/ 或 docs 中的 manifest/文档）+ parity contract 脚本/文档。验收：parity 检查 PASS（真实命令输出），文档化两候选构成差异；不触碰正式 gameplay 数值。

### B3-P2-X2 — S3 Persistence Regression Automation

把 isolated APPDATA `save → exit → reload → same-state` 验证做成无人值守 S3 gate 与 evidence：save 后记录状态指纹（存档 sha/关键字段），退出重载后比较一致；工具化脚本 + evidence 文档；可先在当前可用 Candidate 验证工具，最终 promotion Candidate 必须重跑。验收：S3 工具 selftest PASS + 当前 Candidate 上真实 save/reload 验证记录（PASS 或如实 BLOCKED）；evidence 结构对齐既有证据文档。

## B3-P2 集成

三任务完成后：merge-tree 预检 → 依序合并 → 确认最终 HEAD GitHub Actions run success（gh run list 实证）→ check_all 全量 → abs-path/secret → push 核验 → 更新 B3_STATUS（移除旧 B3-P0 启动指令）→ 更新 PR #1 正文到当前状态 → GPT 评审；继续等待 HUMAN S5 反馈。

## Promotion 条件（GPT 再强化，含调试入口剥离）

GitHub CI PASS + Promotion Candidate fresh rebuild + S0/S1/S2/S3/S4 PASS + HUMAN S5 PASS + Validation↔Promotion parity PASS + 无 diagnostic/test-only MOD + 用户显式批准。HUMAN S5 绑定最终 Promotion Candidate SHA；若人工验收的是 Validation Candidate 也可沿用，前提是 parity contract 证明唯一差异为 TestLevel/harness 调试入口。

---

# B3-P3 — Promotion Candidate Validation Wave（GPT 评审 2026-08-20 批准）

> **Base**：`batch/b3-p3-anchor` = `8e28662`（B3-P2 集成 HEAD）
> **状态**：OPEN FOR CLAIM
> **背景**：GPT 评审 B3-P2 PASS（S2 telemetry 闭环、parity 32/32、S3 gate、CI 全绿采纳）。工程已从"开发功能"进入"把开发 Candidate 变成可被信任的发行 Candidate"阶段：生成 Promotion Candidate → 全量验证 → 证据打包，之后进入最终 Promotion Review。

## 执行原则

- 三任务并行，独立 branch + worktree（batchctl claim）；
- **禁止** baseline promotion；**禁止** Combat Polish 数值调整（WAITING_HUMAN_S5，2–8 项 DEFERRED_BY_USER，提前调参会污染人工验收基线）；**禁止** Build Density 正式实验；
- Promotion Candidate = 正式 Kinetic Arcane gameplay mods（K1/K2/Event Spine/Kill Feel/Camera/Audio）− 全部 diagnostic/test-only MOD（k5 harness runtime、ENABLE_TEST_ZONE bridge、marker writer、KEY_END debug route、b3-p1-s2-diagnostic）；
- 复用 B3-P2-X1 已建链根 `mods/b3-p2-x1-promotion-aggregate`（11 mods/49 patches，parity 32/32 已证）为构建输入；
- 不修改 `00_original/03_raw/04_recovered`；apply_mod 硬约束；候选产物放 10_logs/ 不入库；
- 所有 Gate 必须 evidence 化（PASS 注明证明什么/不证明什么），禁止伪造。

## 任务合同

### B3-P3-X0 — Promotion Candidate Build

用 `mods/b3-p2-x1-promotion-aggregate/mod.json` 作为链根，走 canonical pipeline：resolve → apply → compile（manifest 声明脚本）→ pack → **fresh embed（从 00_original）** → Promotion Candidate EXE。输出：resolved chain（mods/patches 清单）、candidate SHA256 + bytes、removed diagnostic 清单（对照 Validation 差集：k5 harness + b2-x0 bridge + b3-p1-s2-diagnostic）、Build ID、toolchain/manifest 记录。验证产物结构（verify_exe_structure / normalize_pck_md5 等既有工具），确认无 harness/test-only 痕迹（复用/引用 parity 脚本或等价断言：Promotion Candidate 不含 ENABLE_TEST_ZONE=true、无 marker writer、无 KEY_END route）。验收：candidate 产出 + 结构验证 PASS + removed 清单可追溯。

### B3-P3-X1 — Promotion Candidate Gates

在 B3-P3-X0 产出的 Promotion Candidate 上执行 S0/S1/S2/S3/S4 全量验证：
- **S0** 结构：roundtrip/PCK checksum/delta 精确（复用既有工具，如 verify_exe_structure / roundtrip）；
- **S1** boot：真实窗口/进程 + 无 ALERT + 无 fatal（probe_boot 或等价）；
- **S2** Promotion 版核心冒烟：游戏启动 → 主流程 → 存档路径 → 基础战斗路径；**不依赖 TestLevel debug harness**（不要用 harness 当正式运行证明；正式路径无 harness 可用时如实记录 BLOCKED+原因，不伪造）；
- **S3** persistence：复用 B3-P2-X2 的 `s3_persistence_gate.py` 在 Promotion Candidate 上重跑（手册 B3-P2-S3_PERSISTENCE_GATE.md §5.4）；
- **S4** mod-specific 语义：既有 semantic contracts 在 Promotion 链根上通过（check_all 组件内或等价验证）；
- 全部结果 evidence 化（S0–S4 各自 PASS/BLOCKED + proves/not_proven）。验收：S0–S4 全 evidence 化，真实运行记录。

### B3-P3-X2 — Final Evidence Bundle

整理 Promotion Evidence Package：Candidate SHA + MOD chain + parity report（引用 B3-P2-X1）+ S0–S4 gates（引用 X0/X1 产出）+ CI run（引用 push run id）+ 未验证项清单 + HUMAN S5 checklist（绑定 Promotion Candidate SHA，状态 WAITING）。结构对齐既有证据文档（manifest/evidence JSON + 人类可读说明）。目标：将来 baseline promotion 时只需人工确认，不用重新整理证据。验收：bundle 完整、可追溯、引用真实产物路径/hash。

## B3-P3 集成

三任务完成后：merge-tree 预检 → 依序合并 → check_all 全量 → CI run 确认 → push 核验 → 更新 B3_STATUS/PR → GPT 评审（最终 Promotion Review）。HUMAN S5 继续等待（Promotion Candidate 产出后供用户验收）。
