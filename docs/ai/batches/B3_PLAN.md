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
