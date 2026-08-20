# B2-X2 Combat S5 Evidence — 使用说明

> **任务**：B2-X2（Combat S5 Evidence Automation）
> **权威层级**：L2 工具文档；低于 `AGENTS.md` / `status.json`。
> **范围**：把 Combat S5（Player Response / Enemy Hit Reaction / Kill Feel / Combat Camera / Combat Audio）的体验验证改造成“机器可重复准备 A/B evidence、人工只做最终体验判定”的流程。
> **只读边界**：不修改 `00_original/03_raw/04_recovered`；不修改 Player/Mob/GenericSkill/TestLevel 核心逻辑（X1/X2/X3/X4/X5 preimage 由各自分支持有）；B1-X5 的 `combat_harness.py / combat_scenarios.json / combat_telemetry_schema.json` 只读复用，不修改。
> **状态**：driver/aspect 目录/自测已落地，23/23 自测 PASS（证据：`docs/ai/audits/B2-X2_S5_EVIDENCE_SELFTEST_EVIDENCE.json`）；真实游戏内运行依赖 VM 环境与 X1/X5 集成，当前未执行，标 NOT RUN（见 §8）。

---

## 1. 一句话

> 一条命令准备一个 A/B 证据包（baseline + candidate），机器只产证据、绝不替人写体验结论：

```text
python scripts/validate/s5_evidence.py pair --aspect player_response --scenario movement_dash_smoke \
  --seed 2026082001 --baseline <baseline.exe> --candidate <candidate.exe> --launch "<vm-launch-command>"
```

产出 `package_manifest.json` + 两侧 `s5_request_*.json`（capture 请求）+ `checklist_*.json`（人工判定模板）；退出码 0 = 证据已备齐、等人工判定。

## 2. 交付文件

| 文件 | 角色 |
|---|---|
| `scripts/validate/s5_aspects.json` | S5 aspect 目录（Source of Truth）：5 个 aspect × scenario bindings（camera_start、capture_points、telemetry_fields、checklist 问题），contract 校验内建于自测 |
| `scripts/validate/s5_evidence.py` | 证据 driver（host 侧）：aspects/describe/plan/capture/pair/validate/checklist/selfcheck 命令，manifest/退出码契约 |
| `scripts/validate/s5_evidence_selftests.py` | 23 项自测（无游戏也可跑），产出 evidence JSON |
| `tests/s5_evidence/run_s5_selfchecks.py` | 自测入口包装（repo root 自动解析） |
| `tests/s5_evidence/fixtures/filled_checklist_sample.json` | 人工填写 checklist 的结构校验 fixture（合成数据，明确标注 TEST FIXTURE） |
| `docs/ai/audits/B2-X2_S5_EVIDENCE_SELFTEST_EVIDENCE.json` | 本批次自测证据（真实运行结果） |

只读复用（不修改）：`scripts/validate/combat_harness.py`（load_catalog/build_plan/validate_telemetry/load_telemetry_schema）、`combat_scenarios.json`、`combat_telemetry_schema.json`（B1-X5，telemetry 允许 `s5` 扩展键）。

## 3. 快速开始

```text
# 列出 5 个 S5 aspect
python scripts/validate/s5_evidence.py aspects

# 查看 aspect × scenario binding（camera_start / capture_points / checklist 问题）
python scripts/validate/s5_evidence.py describe --aspect player_response --scenario movement_dash_smoke

# 渲染 seed 化 capture plan（同 seed 字节级一致；spawn 复用 B1-X5 harness plan）
python scripts/validate/s5_evidence.py plan --aspect player_response --scenario movement_dash_smoke --seed 2026082001

# dry-run 骨架（不启动任何东西；退出码 3 = NOT_RUN，产物结构完整可审）
python scripts/validate/s5_evidence.py pair --aspect player_response --scenario movement_dash_smoke --seed 2026082001 --dry-run

# 机器准备完整 A/B 证据（真实运行：launcher 拉起游戏，capture 请求驱动截图，telemetry 回传）
python scripts/validate/s5_evidence.py pair --aspect player_response --scenario movement_dash_smoke --seed 2026082001 \
  --baseline <baseline.exe> --candidate <candidate.exe> --launch "<vm-launch-command>" \
  --build-id <YYYYMMDD-HHMMSS-hash> --modset <modset-hash>

# 只准备单侧证据
python scripts/validate/s5_evidence.py capture --aspect player_response --side baseline --scenario ... --seed ... --baseline <baseline.exe>

# 校验证据包结构（0 合法 / 2 结构违规）
python scripts/validate/s5_evidence.py validate --package <package_dir>

# 校验人工填写的 checklist（0 合法 / 2 结构违规；driver 永不写入 verdict）
python scripts/validate/s5_evidence.py checklist --package <package_dir> --filled <filled_checklist.json>

# 静态/结构自测（venv python，无游戏依赖）
python scripts/validate/s5_evidence.py selfcheck
python tests/s5_evidence/run_s5_selfchecks.py
```

## 4. Aspect 目录（S5 统一证据格式）

| aspect id | 意图 | wave | depends_on_event_spine | 首批场景 |
|---|---|---|---|---|
| `player_response` | 移动/Dash/攻击输入的即时反馈 | A | 否 | movement_dash_smoke、rapid_hit_10s |
| `enemy_hit_reaction` | 受击闪白/击退/硬直 | A | 否 | single_melee_hit、rapid_hit_10s |
| `kill_feel` | 击杀反馈（Wave B） | B | 是 | cluster_kill_20、single_ranged_pack |
| `camera` | 战斗相机行为 | B | 是 | cluster_kill_20、projectile_density |
| `audio` | 战斗音频反馈 | B | 是 | single_melee_hit、rapid_hit_10s、cluster_kill_20 |

每个 binding 声明：`camera_start`（两侧共享的相机起点）、`capture_points`（`id/at/kind/required/telemetry_fields`，required 点缺失 → 该侧 NOT_RUN）、`checklist`（`score_1_5 / yes_no / free_text / prefer_side` 四类问题，全部由人回答）。`depends_on_event_spine=true` 的 aspect 在 B2-X1 event spine 缺失时按 NOT_RUN 处理，永不 FAIL。

## 5. 证据包结构（统一格式）

`pair` 在 `<out-dir>/b2x2-<aspect>-<scenario>-<seed>/` 下产出（默认 out-dir `<repo_root>/10_logs/s5_evidence`，git-ignored）：

```text
b2x2-<aspect>-<scenario>-<seed>/
├── package_manifest.json      # 机器可读证据清单（确定性 core + volatile）
├── checklist_<aspect>_<scenario>_<seed>.json   # 人工判定模板（6 问，verdict=null）
├── baseline/
│   ├── s5_request_<aspect>_baseline_<scenario>_<seed>.json   # capture 请求（含 camera_start/spawn plan/telemetry 约定）
│   ├── captures/              # BEFORE 截图（<capture_point_id>_<n>.png；synthetic.marker 存在则整体标记 synthetic）
│   └── telemetry/telemetry_<scenario>_<seed>.json            # 游戏内 telemetry（B1-X5 合同 + s5 扩展）
└── candidate/                 # 同构
```

manifest 关键字段：`package_id / aspect / scenario(seed) / capture_plan(sha256) / spawn(plan_sha256) / camera.start / synthetic_captures / sides{baseline,candidate}{result,reasons,candidate(sha/build_id),telemetry(valid/issues/sha256),captures(status/assets),spine,camera_start_observed,request_rel} / event_spine{status} / human_gate{machine_status:"EVIDENCE_PREPARED",verdict:null} / dry_run / proves / not_proven / deterministic_core_sha256 / repo_head_sha / branch / volatile`。

- **确定性**：`deterministic_core_sha256` 只覆盖机器可重复字段（排除 repo_head_sha/branch/volatile/自身）；同输入两次运行 core 一致（自测锁定）。
- **A/B 对照**：同 aspect × 同 scenario × 同 seed × 同 camera_start × 同 spawn plan（plan sha 相同）→ 两侧证据可直接对照。
- **合成证据诚实标记**：capture 目录存在 `synthetic.marker` 时，全部 asset 标记 `synthetic:true` 且 manifest 记 `synthetic_captures:true`，不得伪装成真实截图。

## 6. 结果与退出码（契约）

| 退出码 | 含义 | 触发 |
|---|---|---|
| 0 | EVIDENCE_PREPARED | 两侧 result=OK（telemetry 有效、required 截图齐、无 NOT_RUN reason） |
| 2 | EVIDENCE_FAIL | 任一侧 telemetry_invalid（schema 违规/场景或 seed 不符）或包结构违规（validate/checklist 命令） |
| 3 | NOT_RUN | 任一侧有非致命缺证 reason：dry_run_mode / vm_not_launched / telemetry_missing / captures_NOT_RUN|PARTIAL / required_event_spine_missing（**缺证据 ≠ 失败**） |
| 1 | SELFTEST_FAIL | `selfcheck` 内部断言失败 |
| 4 | USAGE | 未知 aspect/scenario、无 binding、缺/不存在 candidate、非法 --side、非包目录等参数错误 |

每侧 `reasons` 逐条记录未满足项；`event_spine.status` 独立记录（PRESENT / NOT_RUN），缺失时**永不 FAIL**（B2-X1 未集成期间的契约行为）。

## 7. 人工 Gate（机器永不代答）

- 机器产出：证据 + 模板。`human_gate.machine_status` 固定 `"EVIDENCE_PREPARED"`，`verdict` 为 `null`；
- 人填写 `checklist_*.json`（改 6 问答案为分数/选择/文本），`checklist --filled` 只做结构校验（0/2），**不写入、不推断 verdict**；
- 仓库任何自动化路径都不会生成 `HUMAN_ACCEPTED`（自测 `human_gate_never_auto_accepted` 扫描全部生成物锁定）；
- baseline 晋升仍走 AGENTS.md §5.9 的人工显式批准，与证据包解耦。

## 8. 与 X0/X1 的兼容（NOT RUN 语义）

- **X0（aggregate candidate）**：`--build-id` / `--modset` 显式传入即绑定到两侧 evidence；未集成时缺省记 `unbound`，不影响打包；
- **X1（event spine）**：telemetry 携带 `s5.event_spine` → `PRESENT`；不携带 → `NOT_RUN`；`--require-event-spine` 时缺 spine 的侧直接 NOT_RUN（退出码 3），等 X1 合入后自然升级为可判定；
- 本批次自测在无 VM/无候选/无 X1 环境下全部可跑（dry-run + synthetic fixture），退出码契约稳定。

## 9. 与 sibling 边界

- X0（scripts/ai/）、X1（event spine 注入方）、X2（Mob hit reaction）、X3/X4（Skill/Camera/Audio）：X2-S5 不修改这些文件、不抢 preimage；只新增 `scripts/validate/s5_*` 与 `tests/s5_evidence/`；
- 潜在冲突路径：`scripts/validate/` 目录新增文件（与 B1-X5/X0 无重叠文件）；`combat_harness.py / combat_scenarios.json / combat_telemetry_schema.json` 只读引用（若 X5 未来改 telemetry 合同，X2 的 `validate_side_telemetry` 会跟随 schema 自动校验）。

## 10. 证明什么 / 不证明什么

**已证明（本机自测，证据：`docs/ai/audits/B2-X2_S5_EVIDENCE_SELFTEST_EVIDENCE.json`）**：
- 5 个 aspect 目录可解析、契约字段完整，全部 scenario binding 在 B1-X5 catalog 中可解析；
- capture plan 同 seed 字节级一致、异 seed 必不同；spawn 与 camera_start 两侧共享（A/B 可对照前提）；
- dry-run 骨架 → 退出码 3 + NOT_RUN manifest + 模板齐全；缺 VM launcher → 3；缺 candidate → 4；telemetry 缺失/无效 → 3/2 区分稳定；
- `--require-event-spine` 缺 spine → 3（NOT_RUN，永不 FAIL）；synthetic captures 完整 → 0（EVIDENCE_PREPARED）且诚实标记；
- manifest 确定性 core 同输入一致、异 seed 不同；telemetry 带 `s5` 扩展仍通过 B1-X5 schema 校验；
- 机器产物永不出现 HUMAN_ACCEPTED；checklist 模板/填写结构校验 0/2 正确；validate/checklist 包结构 0/2 正确；
- 任意 cwd 可启动；X2 文件无宿主绝对路径、无 secret 样 token。

**尚未证明（NOT RUN / 需运行环境与集成）**：
- 真实游戏内截图、真实 telemetry（本机无 VM/Godot 运行环境；需接入 B1-X5 run 流程 + 运行环境就绪后的实际 pair 运行）；
- X1 event spine 合入后的 PRESENT 路径（当前按 NOT_RUN 契约运行）；
- 任何 Combat 手感结论本身（最终体验判定属人工 Gate，机器只准备证据）。
