# B3 Promotion S2 + HUMAN S5 联合人工验收协议

> **状态**：ACTIVE（等待人工执行）
> **绑定候选**：Promotion Candidate SHA256=`3127D3948BCEEC66057F6D2359EB2E47C0FA77938F1153F41AA2C348E2FF7314`
> **Build**：20260820-X0-3127D394（103,336,292B，11 mods / 49 patches，链根 `mods/b3-p2-x1-promotion-aggregate/mod.json`）
> **可测文件**：`10_logs/b3-p3-x0-promotion-20260820/candidate/Mutagenic.exe`（+ 同目录 `steam_api64.dll`）
> **权威来源**：`docs/ai/audits/B3-P3-X0_PROMOTION_BUILD.json`、`docs/ai/audits/B3-P3-X1_PROMOTION_GATES.json`、`docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json`
> **创建**：2026-08-20（GPT 终审 B3-P3 PASS 后固化）

---

## 1. 目的与范围

本协议把 **Promotion S2（真实战斗 smoke）** 与 **HUMAN S5（体验验收）** 合并为**同一次人工实机会话**完成，避免重复启动游戏。

- 机器已完成：S0 结构 PASS、S1 boot PASS、S3 persistence PASS、S4 parity 32/32 PASS（见 X1 门禁证据）。
- 机器无法完成：Promotion-native S2（promotion 候选无 harness 自动化入口，如实 BLOCKED）。
- 人工必须完成：Promotion S2 真实战斗 smoke + HUMAN S5 八项体验验收。

**禁止**：为本次验收引入任何 harness / diagnostic / test-only MOD；验收对象必须是冻结的 Promotion Candidate 本体。

---

## 2. 前置条件（执行前确认）

- [ ] 候选文件 SHA256 与 `3127D3948BCEEC66057F6D2359EB2E47C0FA77938F1153F41AA2C348E2FF7314` 一致（`Get-FileHash` 核验）。
- [ ] 使用隔离的 APPDATA（避免污染共享用户数据目录）。
- [ ] 已阅读 HUMAN S5 checklist（`docs/ai/batches/B3_PROMOTION_EVIDENCE_PACKAGE.md` 内 S5 节）。
- [ ] 准备一次性角色名（协议命名，如 `PROMO_S5_20260820`），用于持久化验证。

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

1. 更新 `status.json` 的 `gate_scope.b3_p3_promotion_candidate`（S2/S5 结果）；
2. 更新 `docs/ai/batches/B3_STATUS.md`；
3. 更新 `docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json`；
4. 提交 + push + CI 确认；
5. 按结果决定是否提交最终 Promotion Review。

---

## 7. 权威与禁止

- 本协议不降低 baseline promotion 条件（见 `docs/ai/audits/B3_PROMOTION_EVIDENCE_PACKAGE.json` 与 GPT 终审结论）。
- 机器绝不代人工通过 S5 / baseline promotion；本协议只定义人工如何执行与记录。
- 验收证据必须绑定候选 SHA `3127D394…`，禁止用其他候选的结果代替。