# B3-P3-X2 — Promotion Evidence Package（Final Evidence Bundle）

> **任务**：B3-P3-X2（branch `agent/b3-p3-x2`，base_sha `8e28662` = `batch/b3-p3-anchor`）
> **目标**：整理 Promotion Evidence Package，使将来 baseline promotion 时**人工只需确认本 bundle 与真实产物一致**，无需重新整理证据。
> **机器可读版**：`docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json`（本文件为其人类可读说明，两文件共同构成 bundle）
> **上游**：B3-P2-X1 parity（32/32 PASS）已集成；B3-P3-X0（Promotion Build）与 B3-P3-X1（Promotion Gates）为并行 worker，**启动时尚未产出**——本 bundle 对它们引用 `PENDING_X0` / `PENDING_X1` + 预期路径，不编造内容。

---

## 0. Bundle 组成清单

| 文件 | 作用 |
|---|---|
| `docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json` | 机器可读证据包（本 bundle 主文件） |
| `docs/ai/batches/B3_PROMOTION_EVIDENCE_PACKAGE.md` | 人类可读说明（本文件） |

**证据引用原则**：candidate EXE 等大证据放 `<repo_root>/10_logs/`（不入库），bundle 只引用路径/hash；所有引用有真实来源（路径/id/hash）或明确 PENDING 标注。

---

## 1. Promotion Candidate（SHA + bytes）— 依赖 X0

| 字段 | 值 | 状态 |
|---|---|---|
| 证据文件 | `docs/ai/audits/B3-P3-X0_PROMOTION_BUILD.json` | **PENDING_X0**（并行产出中） |
| 链根 | `mods/b3-p2-x1-promotion-aggregate/mod.json`（v0.1.0） | READY |
| candidate EXE 路径 | `<repo_root>/10_logs/` 下 X0 产物（不入库） | 待填 |
| candidate SHA256 | — | 待填（X0 产出后回填） |
| candidate bytes | — | 待填 |
| Build ID | — | 待填 |
| 剥离清单 | 预期 = parity 报告 `validation_minus_promotion` 两 patch（k5 harness 驱动 + ENABLE_TEST_ZONE bridge） | 待填 |

> X0 产出后回填本节的 SHA/bytes/Build ID，并核验与 `B3-P3-X0_PROMOTION_BUILD.json` 一致。

---

## 2. MOD Chain（promotion-aggregate）— READY

**来源**：`docs/ai/audits/B3-P2-X1_PARITY_REPORT.json` `candidates.promotion`（真实 resolver 输出，PASS）

- **根**：`mods/b3-p2-x1-promotion-aggregate/mod.json`
- **11 mods / 49 patches**，resolution_order：

```
feat-tce → feat-tce-context → k1-player-response → k2-hit-reaction → k4-audio-foundation
→ p7-fix-persistence → b2-x1-combat-event-spine → b2-x4-kill-feel → b2-x5-camera-impulse
→ b2-x6-combat-audio-layers → b3-p2-x1-promotion-aggregate
```

- resolver stdout：`patch_count: 49, asset_overlay_count: 0, verdict: PASS`
- 构成依据文档：`docs/ai/batches/B3_CANDIDATE_SPLIT.md`

---

## 3. Parity Report — READY（32/32）

**来源**：`docs/ai/audits/B3-P2-X1_PARITY_REPORT.json`（head_sha `750865b3d142f5bac5e0a4bf62045fbca7c362e2`，branch `agent/b3-p2-x1`；契约脚本 `scripts/validate/semantic_validation_promotion_parity.py`）

- **checks 32/32 PASS，verdict PASS**
- `validation_minus_promotion` = 恰 2 patch（Promotion 唯一差异）：
  1. `Globals/Constants.gd::enable_test_zone`（b2-x0-combat-harness-bridge：ENABLE_TEST_ZONE=true 调试键）
  2. `Scenes/Levels/TestLevel/TestLevel.gd::combat_harness_integration`（k5-combat-harness：请求驱动 harness）
- `identical_shared_preimage_and_semantics = true`；`forbidden.promotion_hits = {}`（Promotion 零禁用面：无 ENABLE_TEST_ZONE=true / marker writer / KEY_END / request-driven harness）
- ENABLE_TEST_ZONE 影响面：pristine `false` → promotion 保持 `false`（2 处出现不变，HideoutLevel gate inactive）

---

## 4. S0–S4 Gates — 依赖 X1

| 字段 | 值 | 状态 |
|---|---|---|
| 证据文件 | `docs/ai/audits/B3-P3-X1_PROMOTION_GATES.json` | **PENDING_X1**（并行产出中） |
| 任务合同 | `docs/ai/batches/B3_PLAN.md` B3-P3-X1 节 | READY |

X1 须在 Promotion Candidate 上执行（合同定义）：

| Gate | 内容 | 复用工具 |
|---|---|---|
| S0 结构 | roundtrip / PCK checksum / delta 精确 | verify_exe_structure、roundtrip |
| S1 boot | 真实窗口/进程 + 无 ALERT + 无 fatal | probe_boot 或等价 |
| S2 core smoke | 启动→主流程→存档路径→基础战斗；**不依赖 TestLevel harness**；无 harness 可用时如实 BLOCKED | — |
| S3 persistence | save→exit→reload 同态（promotion 候选重跑） | `scripts/validate/s3_persistence_gate.py`（B3-P2-S3_PERSISTENCE_GATE.md §5.4） |
| S4 semantic | 既有 semantic contracts 在 Promotion 链根通过 | check_all 组件（13/13，含 parity 32/32、s3 17/17） |

---

## 5. CI Run 汇总 — READY（真实 id + success）

**Workflow**：`ci-static-semantic`（workflow_id `338323634`，active）
**查询命令**：`gh run list --repo zqs1223041447/Mutagenic-zhCN-HD --workflow ci-static-semantic.yml --limit 3`

| run_id | event | head_sha | conclusion | 说明 |
|---|---|---|---|---|
| **32355579771** | push | `173bdcf7…b2a514`（B3-P3 规划 commit，协调线最新） | **success** | **最终协调线 push run** |
| 32355584355 | pull_request | 同 173bdcf | success | 同期 PR sync |
| 32355295494 | pull_request | — | success | 更早 PR sync |
| 32354862043 | push | `359d1f5a…0d8627`（B3-P2 集成 HEAD） | success | 历史实证（commit 8e28662 信息 + gh run view 核验） |

---

## 6. 未验证项清单（promotion 前必须逐项消解或显式接受）

| # | 未验证项 | 来源 | 依赖 |
|---|---|---|---|
| 1 | Steam 云存档分支（USE_STEAM=false 仅验证本地分支） | `B3-P2-S3_EVIDENCE.json` not_proven 第 2 条 | 非 X0/X1 |
| 2 | perf 帧统计占位（frames=0/fps_min=0 由游戏侧填充） | `B3-P2-S2_TELEMETRY.json` residual_risks 第 1 条 | 非 X0/X1 |
| 3 | all_killed / scene_exit 出口未独立触发（代码路径由编译+结构验证覆盖） | `B3-P2-S2_TELEMETRY.json` residual_risks 第 3 条 | 非 X0/X1 |
| 4 | HUMAN S5 第 2–8 项 DEFERRED_BY_USER | `10_logs/s5-human-feedback-20260820.md`（不入库）+ `B3_STATUS.md` | 人工 |
| 5 | **Promotion Candidate 的 S0–S5 门禁未执行** | B3_PLAN.md B3-P3 合同 | **X0 + X1** |
| 6 | S3 门禁须对 Promotion Candidate 重跑（现行 PASS 针对 b2-i1 候选 sha4ad1de38） | `B3-P2-S3_EVIDENCE.json` not_proven 第 5 条 | **X1** |
| 7 | S2 Promotion 冒烟不依赖 harness；无 harness 时如实 BLOCKED | B3_PLAN.md B3-P3-X1 合同 | **X1** |
| 8 | Boss 击杀无 S5 场景绑定（机器 capture 不可得，靠实机反馈） | `B3_S5_INTAKE_MAP.md` §7.2 | 人工 |

---

## 7. HUMAN S5 Checklist — 状态 WAITING

- **绑定**：Promotion Candidate SHA（`PENDING_X0`，回填自 `B3-P3-X0_PROMOTION_BUILD.json` 的 candidate_exe_sha256）
- **gate 语义**：唯一 HUMAN_ACCEPTED 录入路径 = `scripts/validate/s5_evidence.py`；机器只写 `EVIDENCE_PREPARED`/`verdict=null`，selfcheck 内建 `human_gate_never_auto_accepted` 断言
- **引用**：8 项来自 `docs/ai/batches/B3_S5_INTAKE_MAP.md` §1 总表

| # | 验收项 | 用户反馈 | 状态 |
|---|---|---|---|
| 1 | 普通 hit 无震 / 有 hit 音效 | **不要屏幕震动**（其他暂无感觉） | PENDING_FULL_TEST（**与契约一致**：direct_hit 无 camera impulse，camera 契约 7a） |
| 2 | 小怪击杀 shatter+脉冲+blood_explosion | 暂不测试（后续有实际进展再测） | DEFERRED_BY_USER |
| 3 | 5–20 快速击杀集群抑制 | 同上 | DEFERRED_BY_USER |
| 4 | 精英击杀 shatter×1.25 | 同上 | DEFERRED_BY_USER |
| 5 | Boss 击杀 shatter+poof×1.6 | 同上 | DEFERRED_BY_USER |
| 6 | 重击 heavy 脉冲 + ice_crack | 同上 | DEFERRED_BY_USER |
| 7 | DoT 全抑制 | 同上 | DEFERRED_BY_USER |
| 8 | 全程无报错崩溃 | 同上 | DEFERRED_BY_USER |

> 反馈原始记录：`10_logs/s5-human-feedback-20260820.md`（不入库）。若人工验收 Validation Candidate 也可沿用，前提是 parity 证明唯一差异为 TestLevel/harness 调试入口（B3_PLAN.md Promotion 条件）。

---

## 8. Promotion Review 人工确认清单（将来 promotion 时逐项打勾）

1. [ ] Promotion Candidate SHA/bytes 与 `B3-P3-X0_PROMOTION_BUILD.json` 一致（X0 产出后回填本 bundle）
2. [ ] 候选 EXE 实测 = bundle 记录 hash（人工或工具复核）
3. [ ] MOD chain = 11 mods/49 patches（§2 与 parity 报告一致）
4. [ ] parity 32/32 报告在集成分支上仍 PASS（集成后重跑 `semantic_validation_promotion_parity.py`）
5. [ ] S0–S4 各门禁 PASS/BLOCKED 结果与 `B3-P3-X1_PROMOTION_GATES.json` 一致（X1 产出后回填）
6. [ ] CI run（32355579771 等）全 success 且覆盖最终集成分支 HEAD
7. [ ] 未验证项清单（§6）逐项接受或消解
8. [ ] HUMAN S5 八项全部人工验收并录入（含第 1 项 PENDING_FULL_TEST 补全）
9. [ ] 用户显式批准 promotion（AGENTS.md：候选 EXE 自动晋升 baseline 必须人工显式批准）

---

## 9. 本 bundle 不做什么（边界）

- ❌ 不构建 Promotion Candidate（属 X0）、不执行门禁（属 X1）——本 bundle 只聚合与引用
- ❌ 不写 HUMAN_ACCEPTED、不改 `s5_evidence.py` 流程
- ❌ 不触碰 `00_original/03_raw/04_recovered`；不修改 B2/B3-P2 历史证据文件
- ❌ 不引入宿主绝对路径（所有引用均为 repo-relative 或 `<repo_root>/…` 逻辑路径）
