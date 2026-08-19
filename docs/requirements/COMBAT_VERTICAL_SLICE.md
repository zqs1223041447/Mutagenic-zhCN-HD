# Combat Vertical Slice — Kinetic Arcane Combat

> **状态**：FOUNDATION / IMPLEMENTATION SPEC
> **Authority**：L2 Requirements，低于 `AGENTS.md` 与 `status.json`。
> **上位设计**：`docs/requirements/KINETIC_ARCANE_REMASTER.md`
> **目标**：在全局铺开战斗修改之前，用一个很小但具有代表性的战斗切片证明“高速、清晰、有冲击力”的方向可行。

---

## 1. 为什么需要独立 Combat Slice

现有 Hub Vertical Slice 适合验证 UI、世界层级、标签、HUD、小地图和程序化高清化，但不能证明：

- 玩家是否跟手；
- 高速移动是否舒服；
- 命中是否有因果感；
- 群杀是否有释放感；
- Camera / Audio 是否在高频战斗中仍克制；
- 高 projectile / chain / trigger 密度下是否仍清晰。

因此 Combat Slice 是从“漂亮”进入“好玩”的独立 Gate。

若该 Slice 未达到要求，不允许把同类 VFX/Camera/Hit Feedback 批量复制到全游戏。

---

## 2. 已确认的源码入口

基于仓库机器索引，目前可以确认以下入口存在：

| 系统 | 路径 | 已知职责 | Slice 用途 |
|---|---|---|---|
| Player | `Scenes/Player/Player.gd` | `RigidBody2D`；移动、死亡、装备/技能联动 | 移动响应、Dash、控制状态 |
| Mob | `Scenes/Mobs/Mob.gd` | `RigidBody2D`；物理移动、受击、死亡掉落 | Enemy Reaction、Kill Feedback |
| Skill Core | `Scenes/Skills/GenericSkill.gd` | 技能伤害/属性/施放/支援 | cast pacing、Impact Profile 入口 |
| Projectile | `Scenes/Projectiles/Projectile.gd` | 投射物生命周期/距离/命中链路 | 速度感、contact feedback |
| Stats | `Scenes/Stats.gd` | 玩家/怪物事件与统计；已有 TCE patch 入口 | hit/crit/kill 事件语义 |
| Monster Registry | `Globals/MonsterStats/MonsterStats.gd` | 怪物 stats/attack pacing | pack 节奏实验 |
| Test Level | `Scenes/Levels/TestLevel/TestLevel.tscn` | 现有测试关卡 | 优先作为 Slice 容器候选 |
| Test Spawner | `Scenes/Levels/TestLevel/TestSpawner.tscn` | 测试刷怪 | 代表性 pack 组合 |
| Particles | `Scenes/Particles/*` | BloodExplosion / BombExplosion / ChainLightning 等 | 优先复用现有效果能力 |

仍需本机 recovered tree 精确确认：

- 实际 Camera2D 所属场景/脚本；
- 直接伤害最终进入 `Mob.gd` 的具体函数；
- death dissolve 与 drop 的精确顺序；
- 玩家 Dash 实现位置与当前时间参数；
- 技能输入到 `_cast/cast` 的精确调用链；
- SFX 播放器和 sample 选择入口；
- 哪些 hit path 是 projectile、melee、beam、DoT 共用，哪些必须分开。

**禁止根据路径索引猜 `old_text`。** 实际 CODE_PATCH 必须从本机不可变 `04_recovered` 精确读取 preimage 后生成。

---

## 3. 已有能力，应复用而不是重写

### 3.1 `feat-projectile-data-driven`

已有 per-skill：

- `projectile_lifetime`
- `projectile_max_range`

并保持默认行为零变化。

Combat Slice 应在其上继续做数据驱动调优，而不是再创建第二套 projectile range/lifetime 系统。

### 3.2 `feat-tce`

已有玩家侧：

- `on_hit`
- `on_crit`
- `on_kill`
- `on_take_damage`

以及：

- chance condition；
- status flag condition；
- cast_skill；
- apply_status_effect；
- gain_boon；
- recover/self-damage 等 effect。

后期 Build Density 应优先扩展 TCE 语义，而不是把特殊传奇/技能触发逻辑散落到几十个脚本。

### 3.3 现有粒子

已有 BloodExplosion / BombExplosion / ChainLightning 等脚本说明工程已经具备 Particles2D 战斗效果路径。

第一轮应优先：

- 复用；
- 调层级；
- 调生命周期；
- 调事件绑定；

而不是立即创建大量新 Shader。

---

## 4. Slice 场景构成

优先使用现有 Test Level；若本机发现它不适合稳定复现，再建立一个通过 MOD 声明加入的最小测试场景。

一次完整测试应至少能稳定遇到：

1. **Normal melee pack**：验证连续普通 hit；
2. **Normal ranged pack**：验证移动躲避与屏幕信息；
3. **Mixed pack**：近战 + 远程；
4. **Elite**：验证更高 Impact Profile；
5. **Fast projectile skill**；
6. **Heavy / high-damage skill**；
7. **Crit**；
8. **Group kill**；
9. **Dash / burst movement**；
10. **Chain/Pierce/Trigger 构筑样本**。

Boss 不作为第一轮完成的必要条件；Boss feedback 在普通/Elite 层级成立后再上。

---

## 5. Batch C0 — Experience Audit

这是实际代码修改前的必做步骤。

在本机 recovered tree 输出精确表：

| Element | Script / Scene | Function / Node | Current Timing/Value | Event Frequency | Risk | Upgrade |
|---|---|---|---:|---:|---|---|
| Move | | | | | | |
| Turn | | | | | | |
| Dash | | | | | | |
| Attack/Cast Start | | | | | | |
| Attack/Cast Recovery | | | | | | |
| Projectile Hit | | | | | | |
| Melee Hit | | | | | | |
| Crit | | | | | | |
| Mob Direct Hit | | | | | | |
| Mob DoT | | | | | | |
| Mob Death | | | | | | |
| Elite Death | | | | | | |
| Camera | | | | | | |
| SFX | | | | | | |

额外记录：

- 每个目标文件 SHA-256；
- exact old_text anchor；
- 是否已有 MOD 修改同 unit_id；
- 是否需要依赖 `feat-tce` / `feat-projectile-data-driven`；
- 是否能通过现有 S4/S5 验证。

C0 不改变运行时行为。

---

## 6. Batch C1 — Responsiveness Pass

### 目标

让角色“更快响应”，而不是先把所有速度数值放大。

### 审计与实验顺序

1. movement input response；
2. turn response；
3. Dash startup / recovery；
4. move → attack/cast；
5. attack/cast → move；
6. repeat cast / repeat attack；
7. 高 attack/cast speed 下输入是否丢失。

### 规则

- 第一个 Candidate 只允许少量参数变化；
- 单项优先做 A/B；
- 不猜“正确数字”，从现值和实际帧率测量；
- 初始 tuning 可围绕 10–20% 体感变化试验，但这不是硬编码目标；
- 若游戏原本已无明显 recovery 锁，不额外引入复杂 cancel state machine；
- 不因手感调整改变存档格式。

### 通过条件

玩家能明显感觉控制更直接，同时：

- 不出现滑动失控；
- 不穿过碰撞；
- Dash 不吞输入；
- 高速施法不出现重复触发 bug；
- HUD/鼠标操作不受影响。

---

## 7. Batch C2 — Impact Stack

### 7.1 Enemy Hit Reaction

先做最便宜、最高价值反馈：

- direct hit 短时受击 flash；
- 可选极轻 recoil；
- heavy/crit 提高一级；
- DoT 必须节流或使用不同反馈，禁止每 tick 白闪。

优先在 `Mob.gd` 的统一受击入口实现；如果不同伤害路径不共用入口，再按事实拆分。

### 7.2 Contact FX

命中点效果只承担“接触瞬间”。

普通 hit：

- 极短；
- 小；
- 不遮挡目标。

Heavy/Crit：

- 更亮/更快；
- 可多一层 radial/shard；
- 仍限制生命周期。

### 7.3 Projectile Feel

高速 projectile 的爽感优先来自：

- 更清晰的 flight core；
- 合理 projectile speed；
- 短 trail；
- 命中消失/穿透的清晰因果；
- range/lifetime 与屏幕空间匹配。

不要让 trail 长到无法判断当前 projectile 位置。

---

## 8. Batch C3 — Kill Feel

### `KILL_NORMAL`

- 快速 dissolve/burst；
- drop 时序明确；
- 不阻塞玩家；
- 同帧大量死亡时可批量节流粒子/声音。

### `KILL_ELITE`

- 比 normal 更明显；
- 更强声音瞬态；
- 可触发极小 camera impulse；
- 不使用巨大白屏。

### Cluster Kill

重点验证 5–20 个敌人短时间死亡时：

- 画面不会变成噪声墙；
- FPS 不明显跌落；
- 声音不会削波；
- 掉落仍可读；
- On-kill trigger 的因果来源可理解。

---

## 9. Batch C4 — Camera Feedback

必须先定位实际 Camera2D。

实现原则：

- 普通 hit：0；
- heavy：小；
- crit：小到中；
- elite kill：中；
- boss：后续独立设计。

推荐事件采用“impulse + decay”，并设置：

- max amplitude；
- max frequency；
- aggregation window；
- cooldown/merge rule。

高 AoE 一帧命中 N 个目标时，Camera 只能收到一次聚合事件，而不是 N 次相加。

若现有 Camera 架构不适合安全注入，Combat Slice 可以先不做 Camera；禁止为了 shake 大重构节点树。

---

## 10. Batch C5 — Audio Impact

先盘点现有 `.sample` 与播放入口。

每个核心样本类型需要确认：

- 是否可复用；
- 是否有 simultaneous voice 上限；
- 是否支持 pitch variation；
- 是否会在 cluster kill 时叠加失控。

第一轮优先：

- 普通 impact；
- heavy impact；
- crit cue；
- kill cue。

如果现有资产不足，将缺口放入 **HD / Audio Asset Replacement List**，不要用一个 sample 加大音量假装完成全部层级。

---

## 11. Batch C6 — Build Density Sample

只有 C1–C5 基础手感成立后再做。

建议用现有机制构造一个可重复样本：

- 适量 projectile count；
- 更长但合理的 projectile range；
- pierce 或 chain；
- `on_hit` / `on_crit` / `on_kill` 中至少一种 TCE；
- 一次 cluster kill。

目的不是先做一个超强 Build，而是验证：

> 当构筑密度提高时，新的 Impact/Camera/Audio/Enemy Reaction 系统是否仍然清楚且性能稳定。

---

## 12. 不要在第一轮做的事

1. 全局移速翻倍；
2. 所有怪统一提速；
3. 每 hit Hit Stop；
4. 每 hit Camera Shake；
5. 全屏 Bloom；
6. 给所有技能加长拖尾；
7. 每个 Mob 一个昂贵 Shader；
8. 一次性重做所有 53 个技能；
9. 一次性重做所有怪；
10. 在 `04_recovered` 手工编辑后直接打包；
11. 为了“现代化”升级 Godot 4；
12. 把未知 Camera/Audio 路径写成猜测性的 CODE_PATCH。

---

## 13. MOD 拆分建议

实际落地时建议拆成独立可回滚 MOD，例如：

- `k1-player-response`
- `k2-hit-reaction`
- `k3-kill-feedback`
- `k4-camera-impact`
- `k5-audio-impact`
- `k6-combat-density-sample`
- `k2b-combat-slice-aggregate`

名称可在本机实现时调整，但必须保持职责单一。

Aggregate 只声明依赖，不复制不同语义补丁。

如果某个基础能力应被全局复用，应单独成为基础 MOD，而不是埋在某个技能专属 manifest。

---

## 14. 验证矩阵

### S0 — Structural

- dependency resolve PASS；
- exact preimage PASS；
- declared delta 精确；
- compile PASS；
- PCK checksum PASS；
- roundtrip 3744/3744（或当前 status.json 权威基线）。

### S1 — Boot

- 真窗口启动；
- 无 fatal / ALERT；
- 目标场景可进入。

### S2 — Core Smoke

- 移动；
- Dash；
- 攻击/施法；
- projectile；
- kill；
- drop；
- UI 打开/关闭。

### S4 — Combat-Specific Semantic

至少记录：

- 修改参数最终 EXE 语义恢复确认；
- hit path 仍结算正确；
- direct hit / DoT 区分正确；
- crit 只触发一次对应反馈；
- death 只结算一次；
- TCE 未发生重复分发；
- camera/audio 聚合没有修改伤害语义。

### S5 — Experience / Visual

同场景 BEFORE / AFTER：

- normal hit；
- heavy/crit；
- dash；
- 5+ enemies cluster kill；
- high projectile density。

人工回答：

- 是否明显更跟手？
- 是否更有命中感？
- 是否仍能读懂危险？
- 是否过度闪烁/震动？
- 是否出现视觉噪声？
- 是否感觉只是“特效变多”而不是“战斗变好”？

---

## 15. 性能检查

Combat Slice 至少覆盖：

- 单目标连续攻击；
- 10+ 敌人；
- 多 projectile；
- chain/pierce；
- cluster kill；
- 多 trigger。

重点观察：

- Particles2D instance 数；
- 同帧 Audio voice；
- Camera event 数；
- 高频 Tween / Timer；
- shader/material 实例化；
- frame pacing。

效果系统必须能在高攻速下自然降级，而不是线性增加开销。

---

## 16. GitHub-only 环境当前能证明与不能证明的事

GitHub 仓库提交了：

- 源码索引；
- scene/resource map；
- MOD manifests；
- deterministic patch/build scripts；
- requirements；
- status/evidence metadata。

但按治理规则没有提交 `04_recovered` 明文源码和原游戏二进制。

因此 GitHub-only 审查可以证明：

- 系统边界；
- 文件/函数存在性（来自机器索引）；
- 已有 MOD 的声明；
- patch/build 规则；
- 可复用基础能力。

不能证明：

- `Player.gd` 当前具体代码块内容；
- Camera2D 精确 owner；
- 运行时体感；
- Candidate boot；
- 实际 FPS；
- BEFORE/AFTER 战斗观感。

这些必须在拥有 immutable recovered tree、工具链和 VM 的本机按 canonical workflow 完成。

---

## 17. 下一次本机执行的最小动作

进入具备完整工程资产的宿主后：

1. 读取 `AGENTS.md` / `status.json` / AI entrypoint；
2. 只读扫描 `Player.gd`、`Mob.gd`、`GenericSkill.gd`、`Projectile.gd`、Camera、Audio；
3. 生成 C0 Experience Audit；
4. 只选择 **一个** Player Response 改动与 **一个** Enemy Hit Reaction 改动；
5. 分成两个 declarative MOD；
6. build Candidate；
7. S0/S1/S2/S4；
8. 同场景 S5 A/B；
9. 若明显改善且无副作用，再继续 Camera/Audio/Kill；
10. 最后才进入 Build Density sample。

这个顺序的目的，是让每一次“更爽”都有明确因果和可回滚证据。
