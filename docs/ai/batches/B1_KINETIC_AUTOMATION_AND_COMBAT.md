# B1 — Kinetic Automation & Combat Foundation

> **Batch ID**：`B1`
> **状态**：OPEN FOR CLAIM
> **Integration line**：`agent/kinetic-arcane-remaster-foundation`
> **Frozen base ref**：`batch/b1-anchor`
> **并行规模**：6 个 workstream（X0–X5）
> **目标**：在同一批内同时建立无人值守并发基础设施，并完成第一轮真实 Combat C0/实现/验证推进。

---

## 0. 用户最简操作

用户完成一次本地 clone/部署后，不需要手工创建 branch/worktree。

分别给 6 个执行 AI 发送一句：

- `认领 B1-X0，按仓库规则全自动执行到最远可验证状态。`
- `认领 B1-X1，按仓库规则全自动执行到最远可验证状态。`
- `认领 B1-X2，按仓库规则全自动执行到最远可验证状态。`
- `认领 B1-X3，按仓库规则全自动执行到最远可验证状态。`
- `认领 B1-X4，按仓库规则全自动执行到最远可验证状态。`
- `认领 B1-X5，按仓库规则全自动执行到最远可验证状态。`

执行 AI 必须自己读取本文件，不得要求用户再复制任务正文。

所有任务完成后，用户只需把 X0–X5 的 branch / final SHA / handoff 结果交给协调 AI。

---

## 1. 所有 Xi 的共同前置

每个执行 AI 都必须：

1. 读取 `AGENTS.md`；
2. 读取 `status.json`；
3. 读取 `docs/ai/AI_ENTRYPOINT.md`；
4. 读取 `docs/ai/PARALLEL_BATCH_WORKFLOW.md`；
5. 读取本文件；
6. Combat 任务继续读取：
   - `docs/requirements/KINETIC_ARCANE_REMASTER.md`
   - `docs/requirements/COMBAT_VERTICAL_SLICE.md`
7. 动态解析当前 clone 的 repo root，禁止假设盘符/用户名/父目录；
8. `git fetch` 后解析冻结基线 `batch/b1-anchor`，记录 exact `base_sha`；
9. 自动创建本任务独立 branch + worktree；不得让用户手工执行 worktree 命令；
10. 不修改主工作树已有用户改动；
11. 默认无人值守推进：普通失败自行诊断、修复、重试；
12. 任务结束 commit + push + 输出结构化 handoff。

如果本地尚不存在 `batch/b1-anchor` 的远端引用，应先 fetch；如果仍不存在，才视为真正基础设施阻塞。

---

# X0 — Portable Batch Automation

## Identity

- Task ID：`B1-X0`
- 推荐 branch：`agent/b1-x0-batch-automation`

## Goal

把“多 AI 并发”从文档规则变成可实际使用的一键基础设施，并完成仓库路径可移植性第一轮全扫。

用户价值：以后每批不需要手工建 worktree、算路径、整理交接或检查绝对路径。

## Primary scope

优先：

- `scripts/ai/**`
- 与脚本直接相关的测试目录
- 必要的 `.gitignore`
- 必要的 `docs/ai/` 使用说明

不要修改 gameplay MOD 或 recovered 资产。

## Required deliverables

至少实现一个 repo-relative 的批次 CLI（文件名/内部结构可按仓库实际情况调整），提供等价能力：

- batch/task root 自动解析；
- task claim：根据 batch/task 自动创建 branch + Git worktree；
- task status；
- task handoff 收集/模板；
- task cleanup（只清理已安全集成/明确允许的 worktree）；
- batch collect；
- integration preflight；
- repo-wide absolute-path scan；
- secret scan 包装或复用现有能力。

推荐 UX 目标：

```text
python scripts/ai/batchctl.py claim B1-X1
python scripts/ai/batchctl.py status B1
python scripts/ai/batchctl.py handoff B1-X1
python scripts/ai/batchctl.py collect B1
```

命令名称不是硬性要求；**一条命令完成一个人类意图**才是要求。

## Absolute-path audit

扫描生产相关：

- `.py`
- `.ps1`
- `.bat`
- `.cmd`
- `.json`
- `.yaml/.yml`
- `.toml`
- `.gd`
- `.tscn`
- `.tres`

分类输出：

- production hardcode；
- local-only/config；
- test fixture；
- docs/example；
- false positive。

能安全迁移的 production hardcode 在本任务内修复；范围过大或需要环境事实的登记 portability debt，并建立阻断新增的静态检查。

## Verification

至少：

- 从非 repo-root cwd 调用仍能解析正确 repo；
- 含空格路径场景；
- Windows 路径语义；
- dry-run 不破坏工作树；
- 重复 claim 幂等/清楚失败；
- cleanup 不删除未合并或未知工作树；
- absolute-path scanner 有正/负测试；
- secret scan 不打印 secret 内容。

## Stop condition

除会删除未知用户数据/需要外部凭据外，不因普通实现问题等待用户。

---

# X1 — Player Response Candidate

## Identity

- Task ID：`B1-X1`
- 推荐 branch：`agent/b1-x1-player-response`

## Goal

完成 Player Response 的真实 C0 链路审计，并落地至少一个高价值、低耦合的 `k1-player-response` Candidate。

## Primary scope

只读审计重点：

- `Scenes/Player/Player.gd`
- input/dash 相关场景与脚本
- move ↔ attack/cast 交互入口

可写 Source of Truth 优先：

- `mods/k1-player-response/**` 或仓库实际约定位置
- 本任务专属测试/证据 manifest

不要实现 Enemy Hit Reaction、Camera、Audio。

## Required execution

1. C0：输入 → movement → dash → cast/attack transition 调用链；
2. 记录目标文件 SHA-256、真实 preimage、当前 timing/value、事件频率与既有 MOD 冲突；
3. 识别体感延迟最高价值点；
4. 选择至少一个最小且可 A/B 的响应改动；
5. 创建独立 declarative MOD；
6. canonical build；
7. S0/S1/S2/S4；
8. 若自动 capture 条件具备，做 BEFORE/AFTER；否则准备可重复 S5 evidence 并标 NOT HUMAN-ACCEPTED；
9. 失败自行修复重试。

## Acceptance

- 改的是响应而非粗暴全局速度放大；
- 不改变存档格式；
- Dash/连续施法不产生重复触发或吞输入；
- 无运行时验证时不得声称“手感 PASS”。

---

# X2 — Enemy Hit Reaction Candidate

## Identity

- Task ID：`B1-X2`
- 推荐 branch：`agent/b1-x2-hit-reaction`

## Goal

完成 Mob 伤害链 C0，并实现至少一个不改变伤害结果的 `k2-hit-reaction` Candidate。

## Primary scope

只读重点：

- `Scenes/Mobs/Mob.gd`
- direct hit / DoT / crit / death 入口
- 与 hit/kill 事件相关的必要调用链

可写 Source of Truth：

- `mods/k2-hit-reaction/**`
- 本任务专属测试/证据 manifest

不要修改 Player controller、Camera、Audio。

## Required execution

1. 追踪 projectile/melee/skill → damage → Mob 汇合点；
2. 明确 direct hit 与 DoT 是否共享入口；
3. 明确 crit/heavy 信息是否到达 Mob；
4. 记录真实 preimage/SHA/event frequency；
5. 实现 direct-hit 短时明确反馈；
6. DoT 必须节流/差异化，禁止每 tick 白闪；
7. 不改变碰撞、伤害、死亡次数；
8. canonical build + S0/S1/S2/S4；
9. 能自动 capture 则输出 BEFORE/AFTER。

## Acceptance

- 敌人状态成为第一命中反馈载体；
- 高频 hit 不形成持续闪烁；
- death 仍只结算一次；
- 不靠 Camera shake 冒充 hit reaction。

---

# X3 — Skill / Projectile / TCE Combat Pipeline

## Identity

- Task ID：`B1-X3`
- 推荐 branch：`agent/b1-x3-combat-pipeline`

## Goal

把技能施放、投射物、hit/crit/kill/TCE 的真实运行链路建立成后续 Impact/Build Density 可依赖的基础事实，并在安全时落地独立基础能力。

## Primary scope

- `Scenes/Skills/GenericSkill.gd`
- `Scenes/Projectiles/Projectile.gd`
- `Scenes/Stats.gd`
- `feat-tce`
- `feat-projectile-data-driven`

不要修改 Player/Mob 核心反馈逻辑，避免与 X1/X2 争同一 preimage。

## Required execution

至少回答并留证：

- cast startup/recovery 的实际调用链；
- attack/cast speed 如何作用；
- projectile speed/range/lifetime 如何流转；
- pierce/chain 的处理位置；
- on_hit/on_crit/on_kill 的 dispatch 语义和重复触发风险；
- 高频 projectile/trigger 的主要对象/事件成本；
- Impact Profile 最合适的事件层挂点。

如果存在完全独立、低风险且可验证的基础改进，可以创建 foundation MOD/测试；否则不要为“必须有代码”而制造无价值 patch。

## Verification

静态/结构 + 可运行 semantic check；任何 foundation 修改都必须 canonical build + 对应 S0/S1/S2/S4。

---

# X4 — Camera & Combat Audio Foundation

## Identity

- Task ID：`B1-X4`
- 推荐 branch：`agent/b1-x4-camera-audio`

## Goal

定位真实 Camera2D 与战斗音频架构，并尽可能落地不依赖 X1/X2 的 foundation 能力，为下一批 impact 分层做好准备。

## Primary scope

- Camera2D owner/scene/script
- AudioStreamPlayer / sample / SFX 调用
- 现有 shake/impulse/audio manager（若有）

禁止为了第一轮 camera shake 大改 Player/Mob；若只有通过修改 X1/X2 所属核心文件才能接入，则先提交事实审计和独立基础设施，不抢 preimage。

## Required execution

至少确认：

- Camera owner 与 update 路径；
- 是否已有 impulse/shake；
- Audio 播放器结构；
- impact/kill/cast 样本入口；
- pitch/volume variation 能力；
- simultaneous voice/cluster kill 风险；
- 最小聚合窗口/振幅/voice budget 设计入口。

若可独立实现：建立 camera impulse aggregator 或 audio event limiter foundation，并运行对应验证；普通 hit 仍默认不震屏。

---

# X5 — Combat Test Harness & Automation

## Identity

- Task ID：`B1-X5`
- 推荐 branch：`agent/b1-x5-combat-harness`

## Goal

把现有 Test Level 发展为可重复、尽可能无人值守的 Combat Vertical Slice 验证环境，为本批 X1/X2 及后续所有战斗 Candidate 提供自动回归能力。

## Primary scope

- `Scenes/Levels/TestLevel/*`
- TestSpawner/测试资源
- 与 combat smoke/capture 直接相关的测试脚本/工具

避免修改 Player/Mob/GenericSkill 核心逻辑；通过测试场景、fixture、driver 或独立 MOD 接入。

## Required scenarios

尽量自动复现并记录：

- movement；
- dash；
- normal melee pack；
- ranged pack；
- direct hit；
- crit/heavy sample；
- kill；
- 5–20 敌人 cluster kill；
- fast projectile；
- projectile density；
- chain/pierce/trigger sample（能力允许时）。

## Required telemetry/evidence

能自动化的尽量包括：

- boot/fatal；
- damage/kill count；
- duplicate death；
- trigger count；
- frame/FPS/frame pacing；
- camera event count；
- audio event count；
- screenshot/capture；
- Candidate hash；
- scenario seed/config。

## Acceptance

同一 scenario 可重复；测试失败有明确退出码/报告；不依赖手工点十几个菜单才能开始；不得为了测试方便修改 immutable recovered source。

---

## 2. 并行冲突预期

预期低冲突边界：

- X0：`scripts/ai`/自动化
- X1：Player response MOD
- X2：Mob hit reaction MOD
- X3：Skill/Projectile/Stats/TCE
- X4：Camera/Audio
- X5：TestLevel/harness

执行 AI 若发现必须修改 sibling 主要范围：

1. 先寻找独立挂点；
2. 无法避免时只记录 integration requirement；
3. 不静默抢占 sibling 的核心 preimage；
4. 在 handoff 标记 `potential_conflict_paths`。

---

## 3. B1 中央集成入口

X0–X5 全部交接后，进入 `B1-I1`，由协调 AI执行：

- collect；
- scope/secret/absolute-path review；
- conflict graph；
- preimage drift review；
- dependency ordering；
- integration；
- aggregate candidate；
- aggregate S0/S1/S2/S4 + 必要 S5；
- 更新 Draft PR；
- 发布 B2。

执行 Xi 不自行执行 B1-I1。
