# B3-P2-X1 — Validation / Promotion Candidate Separation

> **任务**：B3-P2-X1（branch `agent/b3-p2-x1`）
> **目标**：正式区分 **Validation Candidate**（验证用）与 **Promotion Candidate**（可晋升用），
> 建立 gameplay parity contract，证明除测试入口外无正式 gameplay 差异。
> **依据**：GPT 评审结论（2026-08-20）——`mods/b2-x0-combat-harness-bridge` 把
> `Constants.ENABLE_TEST_ZONE = true` 写入 Candidate 供 S2 验证，但**不应默认随最终 baseline 晋升**。
> **合同**：`scripts/validate/semantic_validation_promotion_parity.py`（真实 resolve 差异断言，
> 机器可读报告 `docs/ai/audits/B3-P2-X1_PARITY_REPORT.json`）。

---

## 1. 两类 Candidate 定义

| Candidate | 构成 | 用途 |
|---|---|---|
| **Validation Candidate** | 正式 gameplay MOD（10 个）+ harness（k5 请求驱动场景）+ `ENABLE_TEST_ZONE=true` 桥（b2-x0-combat-harness-bridge）+ 聚合根；S2 bisect 时可再叠加 b3-p1-s2-diagnostic | S2/S4/S5 机器验证与 bisect 运行 |
| **Promotion Candidate** | 相同正式 gameplay MOD（10 个）− harness − ENABLE_TEST_ZONE − diagnostic − test-only route | 最终 baseline 的候选构成（`docs/ai/batches/B3_CANDIDATE_SPLIT.md` 本文件即其构成依据） |

**一句话原则**：*为自动测试开的后门（TestZone 入口、请求驱动 harness、存盘 marker 探针、KEY_END 物理键路由）属于验证面，永远不进晋升面。*

---

## 2. 两候选构成对照表

### 2.1 MOD 级构成

| 类别 | MOD id | patch_type | Validation | Promotion | 说明 |
|---|---|---|---|---|---|
| 正式 gameplay | `feat-tce` | CODE_PATCH | ✅ | ✅ | TCE 语义 |
| 正式 gameplay | `feat-tce-context` | CODE_PATCH | ✅ | ✅ | TCE 上下文 |
| 正式 gameplay | `k1-player-response` | CODE_PATCH | ✅ | ✅ | 玩家响应 |
| 正式 gameplay | `k2-hit-reaction` | CODE_PATCH | ✅ | ✅ | 受击反馈 |
| 正式 gameplay | `k4-audio-foundation` | CODE_PATCH | ✅ | ✅ | 音频基础 |
| 正式 gameplay | `p7-fix-persistence` | CODE_PATCH | ✅ | ✅ | USE_STEAM=false 本地持久化 |
| 正式 gameplay | `b2-x1-combat-event-spine` | CODE_PATCH | ✅ | ✅ | 战斗事件总线 |
| 正式 gameplay | `b2-x4-kill-feel` | CODE_PATCH | ✅ | ✅ | 击杀反馈 |
| 正式 gameplay | `b2-x5-camera-impulse` | CODE_PATCH | ✅ | ✅ | 相机动量 |
| 正式 gameplay | `b2-x6-combat-audio-layers` | CODE_PATCH | ✅ | ✅ | 战斗音频层 |
| **harness（验证专属）** | `k5-combat-harness` | CODE_PATCH | ✅ | ❌ | TestLevel.gd 请求驱动 harness |
| **harness bridge（验证专属）** | `b2-x0-combat-harness-bridge` | CODE_PATCH | ✅ | ❌ | `ENABLE_TEST_ZONE = true` |
| **diagnostic（验证专属）** | `b3-p1-s2-diagnostic` | CODE_PATCH | ✅(可选) | ❌ | do_save_game marker + KEY_END 路由 |
| 聚合根（元数据） | `b2-x0-aggregate` / `b2-i1-aggregate` | RESOLVED_MOD_CHAIN | ✅ | ❌ | B2 验证链根；依赖 harness bridge |
| **聚合根（元数据）** | `b3-p2-x1-promotion-aggregate` | RESOLVED_MOD_CHAIN | ❌ | ✅ | 本任务新增 Promotion 链根（无 patch 贡献） |

### 2.2 resolve 结果（真实 resolver 输出，PASS）

| 根 manifest | 解析 MOD 数 | 解析 patch 数 |
|---|---|---|
| `mods/b2-i1-aggregate/mod.json`（Validation） | 14 | 51 |
| `mods/b3-p1-s2-diagnostic/mod.json`（Validation+Diagnostics） | 15 | 63 |
| `mods/b3-p2-x1-promotion-aggregate/mod.json`（Promotion） | 11 | 49 |

数字关系：49 = 51 − 2（k5 + bridge 两个 patch）；63 = 51 + 12（diagnostic 的 11 个 marker + 1 个 KEY_END 路由）。全部闭合成立。

---

## 3. 剥离清单（每个剥离项可追溯真实 patch）

> 引用的 unit_id / path 与 `mods/*/mod.json` 声明一致；`old_text_sha256` 为 old_text UTF-8 字节的 SHA-256
> （与 parity 报告 `validation_minus_promotion` 字段一致）。

### 3.1 Validation − Promotion（2 个 patch）

| # | declaring mod | unit_id | path | old_text_sha256 | 剥离理由 |
|---|---|---|---|---|---|
| 1 | `k5-combat-harness` | `Scenes/Levels/TestLevel/TestLevel.gd::combat_harness_integration` | `Scenes/Levels/TestLevel/TestLevel.gd` | 见 parity 报告 | harness 请求驱动：存在 `user://combat_harness/request.json` 时进入场景脚本驱动；不存在时回退原 `spawn_cluster_in_ladder` 行为 |
| 2 | `b2-x0-combat-harness-bridge` | `Globals/Constants.gd::enable_test_zone` | `Globals/Constants.gd` | 见 parity 报告 | 将 `const ENABLE_TEST_ZONE = false` 改为 `true`，放开 `goto_test_level` 调试键 |

### 3.2 Validation+Diagnostics − Promotion（追加 12 个 patch）

| # | declaring mod | unit_id（或 path 标识） | path | 剥离理由 |
|---|---|---|---|---|
| 3–13 | `b3-p1-s2-diagnostic` | `Globals/GameState.gd::s2_marker_helper`、`do_save_game::m01_enter` … `m11_onsave_done`（11 个） | `Globals/GameState.gd` | S2 存盘 bisect 磁盘 marker 探针（`user://s2_markers/`），纯观测性 |
| 14 | `b3-p1-s2-diagnostic` | （无 unit_id，path+old_text 定位） | `Scenes/Levels/Hideout/HideoutLevel.gd` | test-only route：`_input` 增加 `event.scancode == KEY_END` 分支，供 PostMessage 合成 End 键触达 `goto_test_level` |

### 3.3 断言（parity contract 强制执行）

1. `promotion − validation = ∅`（Promotion 的每个 patch 都在 Validation 中出现，无正式 gameplay 丢失）；
2. `validation − promotion` == 恰为 §3.1 两 patch（provenance 驱动：由 declaring mod 清单计算，非硬编码）；
3. `validation_diag − promotion` == 恰为 §3.1 + §3.2 共 14 patch；
4. shared 正式 patch（49 个）在三个 resolve 结果中 canonical 逐字节一致（含 preimage_sha256/expected_occurrences/placeholders/format_tokens）；
5. Promotion 解析 patch 中**不含**：`ENABLE_TEST_ZONE = true`、`user://s2_markers`/`_s2marker`、`KEY_END`、`_run_combat_harness`/`user://combat_harness`；
6. Promotion `resolution_order` 不含 `k5-combat-harness`/`b2-x0-combat-harness-bridge`/`b3-p1-s2-diagnostic` 及两个 B2 验证聚合根。

---

## 4. ENABLE_TEST_ZONE 影响面分析

### 4.1 原版（04_recovered，promotion 保持现状）

| 文件 | 位置 | 内容 | 影响 |
|---|---|---|---|
| `04_recovered/Globals/Constants.gd` | :102 | `const ENABLE_TEST_ZONE = false` | 唯一开关定义；promotion 保持 `false` |
| `04_recovered/Scenes/Levels/Hideout/HideoutLevel.gd` | :20 | `if event.is_action_pressed("goto_test_level") and Constants.ENABLE_TEST_ZONE:` | 唯一消费点（keybind `goto_test_level`）。`ENABLE_TEST_ZONE=false` 时整键分支恒不触发，恢复正常玩家无法因按键进入 TestLevel |

### 4.2 影响面结论

- `ENABLE_TEST_ZONE` 在整个 04_recovered 中**仅出现 2 处**（1 定义 + 1 守卫），parity 契约断言该计数与 pristine 值不变；
- `goto_test_level` 键位本身是项目自带的 debug 键（`project.godot`），原版即为 false 关闭；
- Validation 只把**这一个开关置 true** 以便自动化 S2 路由到 TestLevel——不改变任何 gameplay 数值/路径，TEST_ZONE 门内的行为是原版自带；
- **Promotion 剥离后即恢复原版 false** → 玩家不可经该键进入 TestLevel → 测试后门不会成为正式 baseline 的一部分；
- 不剥离的代价（GPT 评审风险）：任何"原始用户"在 Hideout 按 End/goto_test_level 键即被送进测试关卡，属于无意暴露的调试入口，晋升风险不可接受。

---

## 5. Parity Contract（`scripts/validate/semantic_validation_promotion_parity.py`）

- **真实 resolve**：用 `scripts/patch/resolve_mod_chain.py` 对三个根 manifest 各跑一次 resolver（非自实现解析），解析产物写入临时目录，报告记录每条 resolver 的真实 stdout；
- **patch 身份**：与 resolver 一致——有 `unit_id` 按 `unit_id`，否则按 `(path, old_text)`（保证两个相同 old_text、不同 unit_id 的补丁不被误合并，本链实际命中 feat-tce-context 的 `func trigger_on_hit():`/`func trigger_on_crit():` 成对补丁）；
- **差集检查**：集合差 + provenance 白名单双向匹配，杜绝静默丢弃正式 patch 或误留测试 patch；
- **禁用面扫描**：对 promotion 全部补丁的 old/new 文本做 token 扫描；
- **pristine 影响面**：04_recovered 的 Constants.gd / HideoutLevel.gd 断言 `ENABLE_TEST_ZONE = false`、2 处出现、无 KEY_END 变体；
- **abs/secret**：新文件不含宿主绝对路径；docs 遵循仓库 `docs_example` 语义。
- 退出码：0=PASS（并写机器报告），1=FAIL，`--selftest` 独立自检（比较/差集/禁用扫描/abs 助手 15/15）。

### 运行方式

```
python scripts/validate/semantic_validation_promotion_parity.py            # 真实 parity（写报告）
python scripts/validate/semantic_validation_promotion_parity.py --selftest # 内存自检
```

报告：`docs/ai/audits/B3-P2-X1_PARITY_REPORT.json`（machine-readable，可被后续 gate 复用：字段
`candidates.*.resolution_order` / `parity.validation_minus_promotion` / `forbidden.promotion_hits` /
`enable_test_zone_impact`）。

---

## 6. 集成须知

- 本任务只做划分/文档/校验工具，**未修改任何正式 gameplay MOD 的数值或语义**；
- **新文件**：`mods/b3-p2-x1-promotion-aggregate/mod.json`（Promotion 链根，纯元数据，无 patch 贡献）；
- 修改文件：`scripts/ai/check_all_components.json`（注册 parity contract 为 required；若 B3-P2-X0/X2 已并行改动该文件，冲突由协调 AI 合并，保留本条目可降级为说明即可）；
- **不触碰**：`00_original/`、`03_raw/`、`04_recovered/`、任何既有 MOD 声明、任何 gameplay 数值。
- Promotion Candidate 尚未构建/embed/运行验证——`docs/ai/audits/B3-P2-X1_PARITY_REPORT.json` 的
  `not_proven` 明示：promotion 的 S0–S5 证据需在最终晋升流程的 fresh rebuild 阶段补齐。