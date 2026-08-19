# B1-X2 — Enemy Hit Reaction C0 远端预审计

> **Task**：B1-X2
> **基线**：`batch/b1-anchor` → `c864480d8908630d602c17f4949b96b65d19b275`
> **来源**：tracked `04_recovered/Scenes/Mobs/Mob.gd`、`04_recovered/Scenes/Stats.gd`、`04_recovered/Scenes/Mobs/Mob.tscn`
> **Mob.gd SHA-256**：`ba46348c8ba490644964a8b9bdabb58a8964199cd3464c468f77cc57babe9364`
> **状态**：REMOTE C0 + DECLARATIVE CANDIDATE READY；未做本地 build/runtime Gate。

## 1. 真实伤害/反馈边界

- Mob 的 `Stats` 节点通过 `health_changed` 连接到 `Mob._on_update_healthbar()`。
- `Stats.gd` 确实定义 `damage_taken(amounts, attacker_stats, was_crit)`，但 `on_take_damage()` 只有 `is_player` 时才 emit；Mob 没有现成 direct-hit/crit signal。
- `Mob._on_stats_changed()` 已使用 `Sprite.modulate` 表示 poison/bleed/burning/chilled/jolted/vulnerable/exposed/frozen 等状态。
- `Mob.tscn` 没有专用 hit Tween/Timer；Sprite 自带 outline material，elite/magic 也使用该 material。

## 2. 第一 Candidate 的取舍

为了不抢 X3 的 `Stats.gd` preimage，也不改变伤害语义，首版 `k2-hit-reaction` 不向 Stats 新增事件，而是在 Mob 已有 `health_changed` 回调中检测**生命值下降**。

这意味着首版不能区分 direct hit 与 DoT，也不能区分 crit/heavy；因此必须做统一节流，避免 DoT 每 tick 高频闪烁。

## 3. `k2-hit-reaction` v0.1

行为：

- 保存上一次 health；
- 当 health 下降且超出最小反馈间隔时，给 `Sprite.self_modulate` 一个 60ms 轻红/亮反馈；
- 最小触发间隔 160ms；
- `self_modulate` 与现有 `Sprite.modulate` 分层，避免覆盖状态颜色；
- 反馈到时自动恢复 `Color.white`；
- 不改 health、damage、collision、death、drop、TCE；
- DoT 与高攻速 direct hit 都被同一个节流器限制，不形成逐 tick 高频闪烁。

## 4. 为什么暂不做 Crit/Heavy 分层

当前 Mob 层没有收到 `was_crit`。为了在 X2 单独分支中保持低冲突，不应顺手修改 X3 所属 `Stats.gd`。

后续中央集成可基于 X3 的 TCE/context 或新增独立 combat event foundation，把 crit/heavy metadata 安全传到 Mob，再升级 Impact Profile。

## 5. 风险与验证

- health-loss feedback 也会响应 DoT，因此 160ms throttle 是首版安全预算，不代表最终 DoT 视觉语言。
- `Sprite.self_modulate` 需要在本地 Godot 3.5.3 compile/boot 验证。
- death 时对象可能在反馈结束前销毁，不影响伤害/死亡语义。
- 本地必须覆盖：单次 hit、快速连击、DoT、冻结/燃烧等状态色同时存在、elite/magic shader、死亡只结算一次。

## 6. 本地接手动作

resolve/apply → compile → pack → fresh embed → S0/S1/S2/S4 → TestLevel BEFORE/AFTER；S5 未人工接受前不写 gameplay PASS。
