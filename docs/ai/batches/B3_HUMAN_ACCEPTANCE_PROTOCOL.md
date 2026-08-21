# B3 Promotion S2 + HUMAN S5 联合人工验收协议

> **状态**：ACTIVE（等待人工执行 — 当前 governance_hold，见 releases/b3-s5-fix-3B6427B3.json）【已更新 2026-08-21】
> **绑定候选**：Promotion Candidate SHA256=`3B6427B3DBCF0B7DEE2CFC29276AB94F2ADB8F61C3188A0668D0925193489727` 【2026-08-21 起生效，旧值见 §8 History】
> **Build**：b3-s5-fix-20260820-3B6427B3（103,338,436B，12 mods / 57 patches，链根 `mods/b3-p2-x1-promotion-aggregate/mod.json` 含 b3-cp1-camera-zoom-setting 8 patches）【旧 Build 20260820-X0-3127D394 11/49 见 History】
> **可测文件**：`10_logs/b3-s5-fix-20260820/candidate/Mutagenic.exe`（+ 同目录 `steam_api64.dll`）【旧文件 10_logs/b3-p3-x0-promotion-20260820/candidate/Mutagenic.exe 保留但已 superseded】
> **权威来源**：`releases/b3-s5-fix-3B6427B3.json`（治理权威）、`docs/ai/audits/B3-P2-X1_PARITY_REPORT.json`（parity 32/32）、`status.json:promotion_3B6427B3` / `b3_s5_fix_promotion_candidate`、`docs/ai/audits/B3-P3-X1_PROMOTION_GATES.json`（历史 S0-S4 参考）、`docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json`（addendum 指向新候选）
> **创建**：2026-08-20（GPT 终审 B3-P3 PASS 后固化）；**更新**：2026-08-21 绑定至 3B6427B3（B3-S5-FIX）
> **验收范围决定（用户确认 2026-08-20）**：**保持现状，分开验收**——本候选（3B6427B3，含原 3127D394 全部 10 正式 gameplay MOD + p7-fix + b3-cp1 zoom）只含 B3 战斗手感 MOD（12 mods：feat-tce/feat-tce-context/k1-player-response/k2-hit-reaction/k4-audio-foundation/p7-fix-persistence/b2-x1-combat-event-spine/b2-x4-kill-feel/b2-x5-camera-impulse/b2-x6-combat-audio-layers/b3-cp1-camera-zoom-setting/b3-p2-x1-promotion-aggregate），**不含汉化**（汉化在独立 C5 线 `mods/localization`，zh_CN Core Playable v8.1 SHA 033A34F7… 单独验收）；不构建"汉化+战斗"组合候选。

---

## 1. 目的与范围

本协议把 **Promotion S2（真实战斗 smoke）** 与 **HUMAN S5（体验验收）** 合并为**同一次人工实机会话**完成，避免重复启动游戏。

- 机器已完成：S0 结构 PASS、S1 boot PASS、S3 persistence PASS、S4 parity 32/32 PASS（见 X1 门禁证据）。
- 机器无法完成：Promotion-native S2（promotion 候选无 harness 自动化入口，如实 BLOCKED）。
- 人工必须完成：Promotion S2 真实战斗 smoke + HUMAN S5 八项体验验收。

**禁止**：为本次验收引入任何 harness / diagnostic / test-only MOD；验收对象必须是冻结的 Promotion Candidate 本体。

### 1.1 当前 HUMAN S5 9/9 声称的证据状态（2026-08-21 更新，governance_hold 原因）

> **如实记录，不伪造 PASS** — 以下为 status.json 与 releases/b3-s5-fix-3B6427B3.json 的一致描述，保持 BLOCKED/待重跑。

- **声称**：`status.json:trusted_baselines.b3_s5_fix_promotion_candidate / promotion_3B6427B3` 与 `gate_scope.promotion_3B6427B3` 记录 HUMAN S5 9/9 PASS，来源 `10_logs/s5-human-feedback-20260820.md`（2026-08-21 用户复测“已确认无问题”，含 PLAY→World 加载已验证；三修复对应 b2-x5 blocked_kill_pulses、b2-x6 killer.is_player 守卫、b3-cp1 camera zoom 0.35-0.8）。
- **失步**：该 9/9 PASS 的**物理证据未归档** — `10_logs/s5-human-feedback-20260820.md` 与 `10_logs/b3-s5-fix-20260820/*`（verify_exe_3B6427B3.json / probe_boot_final.log / s3_out）均为 gitignored，**未随 releases 归档**（archive_locator `G:\Mutageni-Archive\releases\b3-s5-fix-3B6427B3\` 仅示例路径，需双副本物理化）；`releases/b3-s5-fix-3B6427B3.json` 因此标记 `human_s5: CLAIMED_9_9_NEEDS_REBIND`、`s0/s1: CLAIMED_PASS_NOT_VERIFIABLE`、`s3: BLOCKED_NEEDS_RERUN`。
- **待重绑**：需按本协议 §3-§4 **重新执行同一实机会话**（Promotion S2 smoke + HUMAN S5 八项/现九项对比），并将新的人工验收记录（SHA 绑定、截图/日志、checklist 签名）落盘至归档路径后，方可将 human_s5 从 CLAIMED 提升为 PASS，并更新 `docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json` addendum 与 status.json gate。
- **S3/S2 如实状态**：`s_gates.s2 = BLOCKED_EXPECTED`（promotion 无 harness 自动化入口，parity 实证，与 B3-P3 一致）、`s_gates.s3 = BLOCKED_NEEDS_RERUN`（isolated APPDATA 无 harness load trigger，预期 BLOCKED，需重跑 s3_persistence_gate.py）、`s0/s1 = CLAIMED_PASS_NOT_VERIFIABLE`（声称 3744/3744 与 20s 存活但未归档）、`s4 = PASS`（parity 32/32 已证，不依赖 10_logs）、`steam_cloud / s1 >20s 长稳` 仍为 not_proven（见 releases not_proven）。
- **禁止伪造**：本协议不因 status.json 曾写 PASS 而视为已验收；机器绝不代人工写 HUMAN_ACCEPTED，9/9 需重绑后才可作为 baseline 依据。

---

## 2. 前置条件（执行前确认）

- [ ] 候选文件 SHA256 与 `3B6427B3DBCF0B7DEE2CFC29276AB94F2ADB8F61C3188A0668D0925193489727` 一致（`Get-FileHash` 核验）。【旧值 3127D394… 见 §8 History，已 superseded】
- [ ] 使用隔离的 APPDATA（避免污染共享用户数据目录）。
- [ ] 已阅读 HUMAN S5 checklist（`docs/ai/batches/B3_PROMOTION_EVIDENCE_PACKAGE.md` 内 S5 节 + 本协议 §1.1 governance_hold 说明）。
- [ ] 准备一次性角色名（协议命名，如 `PROMO_S5_20260820`），用于持久化验证。
- [ ] 已知悉当前 HUMAN 9/9 声称来自 `10_logs/s5-human-feedback-20260820.md` 但未归档，需按 §1.1 重绑后才视为有效。

---

## 3. Promotion S2 — 真实战斗 smoke（同一会话内先做）

正常游戏路径，不附加任何调试手段：

1. **启动**：运行候选 EXE，确认窗口出现、无 ALERT 弹窗、无 script error。
2. **读档/建角**：创建协议命名角色（或读档既有角色）。
3. **进入真实战斗**：进入地图并遭遇敌人。
4. **操作**：移动 → Dash → 攻击，确认输入响应正常。
5. **敌人反馈**：敌人受击、受伤、死亡表现正常。
6. **玩家反馈**：玩家可正常受伤（生命变化可见）。
7. **持续运行**：战斗持续若干分钟，无 script error / crash。

**判定**：以上全部通过 → S2_PROMOTION = PASS；任一异常 → 记录现象（截图/日志/复现步骤）并判 FAIL，进入 §5 处理。

---

## 4. HUMAN S5 — 八项体验验收（同一会话内接着做）

按 `docs/ai/batches/B3_PROMOTION_EVIDENCE_PACKAGE.md` 的 S5 checklist 逐项执行并记录：

| # | 项 | 结果（PASS/FAIL/DEFERRED） | 备注 |
|---|---|---|---|
| 1 | 屏幕震动（用户已反馈：不要屏幕震动；当前设计一致） | PASS（已录） | 无需调 Camera |
| 2 | （按 bundle S5 checklist 逐项） | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |

**判定**：全部 PASS → HUMAN S5 = PASS；任一 FAIL → 记录现象，进入 §5。

---

## 5. 结果处理

### 5.1 全部 PASS

- S2_PROMOTION = PASS、HUMAN S5 = PASS；
- 更新 `docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json`（S5 状态 → PASS，绑定候选 SHA）；
- 提交最终 Promotion Review 给 GPT；用户显式批准后，才允许 baseline promotion。

### 5.2 任一 FAIL

- 记录失败项、现象、截图/日志；
- 若为 S5 体验问题（如震动、手感、密度）→ 按 `docs/ai/batches/B3_S5_INTAKE_MAP.md` 自动生成对应 Combat Polish 任务；
- 若为 S2 技术问题（crash/script error）→ 生成修复任务，重新走 canonical pipeline 出候选后重测；
- 修复/调参期间不启动新的 gameplay 开发批次（B3 Release Hold 保持）。

---

## 6. 验收后状态更新

验收完成后，主控负责：

1. 更新 `status.json` 的 `gate_scope.promotion_3B6427B3` / `gate_scope.b3_s5_fix_promotion_candidate`（S2/S5 重绑结果）；历史 `gate_scope.b3_p3_promotion_candidate` 保留但不再作为权威；
2. 更新 `docs/ai/batches/B3_STATUS.md`；
3. 更新 `docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json` addendum（不改写 3127D394 历史 11/49 事实，仅追加新候选记录）；
4. 更新 `releases/b3-s5-fix-3B6427B3.json` 将 `s_gates` 从 CLAIMED 提升为实证 PASS/FAIL，并将证据物理化至 `archive_locator` 双副本；
5. 提交 + push + CI 确认；
6. 按结果决定是否提交最终 Promotion Review（仅在 S0/S1/S3 归档且 HUMAN S5 重绑 PASS 后）。

---

## 7. 权威与禁止

- 本协议不降低 baseline promotion 条件（见 `releases/b3-s5-fix-3B6427B3.json` status=promotion_recorded_governance_hold 与 `docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json` 及 GPT 终审结论）。
- 机器绝不代人工通过 S5 / baseline promotion；本协议只定义人工如何执行与记录。
- 验收证据必须绑定当前候选 SHA `3B6427B3DBCF0B7DEE2CFC29276AB94F2ADB8F61C3188A0668D0925193489727`，禁止用其他候选（包括旧 3127D394…）的结果代替；旧候选见 §8 History。

---

## 8. History — 旧绑定保留（不作为当前权威）

> 为治理可追溯保留旧值，当前权威以头部 3B6427B3 为准。

- **旧绑定候选**：`3127D3948BCEEC66057F6D2359EB2E47C0FA77938F1153F41AA2C348E2FF7314`（Build 20260820-X0-3127D394，103,336,292B，11 mods / 49 patches，链根 `mods/b3-p2-x1-promotion-aggregate/mod.json` 未含 b3-cp1；状态见 `releases/b3-p3-3127D394.json` superseded/superseded_by 3B6427B3）
- **旧可测文件**：`10_logs/b3-p3-x0-promotion-20260820/candidate/Mutagenic.exe`（已保留但不再作为 Human Review Candidate）
- **旧权威来源**：`docs/ai/audits/B3-P3-X0_PROMOTION_BUILD.json` / `B3-P3-X1_PROMOTION_GATES.json`（S0/S1/S3/S4 历史 PASS 供参考，当前需按 §1.1 重绑）
- **变更原因**：b3-cp1 8 zoom patches + S5 3 修复（b2-x5 blocked_kill_pulses、b2-x6 killer 守卫、b3-cp1 zoom 0.35-0.8）使链从 11/49 增至 12/57， parity 新报告 `B3-P2-X1_PARITY_REPORT.json` head 095d57c（32/32 PASS）取代旧 parity；releases 中旧记录已标记 superseded。

---

## 9. 与 status.json / releases 的一致性声明

- 本协议头部绑定与 `releases/b3-s5-fix-3B6427B3.json` 的 `candidate_sha256` / `candidate_size` / `mods` / `patches` / `game_fingerprint` / `toolchain` 一致；
- s_gates 如实描述与该 releases 文件 `s_gates` / `not_proven` 一致（s0/s1 CLAIMED_PASS_NOT_VERIFIABLE、s2 BLOCKED_EXPECTED、s3 BLOCKED_NEEDS_RERUN、s4 PASS、human_s5 CLAIMED_9_9_NEEDS_REBIND）；
- 不伪造 S0/S1/S3 的 PASS 为已验证，不伪造 HUMAN 9/9 为已归档；
- `status.json` 中 `trusted_baselines.b3_s5_fix_promotion_candidate` / `promotion_3B6427B3` 的 PASS 为已晋升记录，但其 `s3_note` 与 `gate_scope` 明确 S3 BLOCKED 为预期，持久化靠 P7-FIX 闭环；本协议补充其 **governance_hold** 视角（10_logs 未物理归档前不视为 valid_baseline）。