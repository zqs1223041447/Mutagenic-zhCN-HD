# Kinetic Arcane — 远期体验意图（P4+）

当前主线是 **P1 Godot 4.7.1 迁移**。本文件不是任务合同，不启动 3.5.3 Kinetic 批次，不禁止 Godot 4。

产品锁定见 `PRODUCT_CONTRACT.md` / `AGENT.MD`。下文只保留以后 P4 视觉/战斗呈现还用得上的意图。

---

静态视觉：**Dark Arcane Tactical**（冷静、精密、克制）。  
动态战斗：**Kinetic Arcane Combat**（跟手、可读、有冲击，但不做成 Survivor）。

体验选择顺序：

1. Player Response
2. Gameplay Readability
3. Interaction Clarity
4. Impact
5. Visual Hierarchy
6. Consistency
7. Modern Appearance
8. Decoration

支柱（以后做，不在 P1 扩 3.5.3 MOD）：

- **Instant Control**：缩短输入到动作结果的体感延迟（含 Dash），不要只加 `movement_speed`。
- **Kinetic Traversal**：速度感 = 控制响应 × 世界参照 × 镜头 × 动画/FX × 实际速度。
- **Impact Stack**：命中因果（敌人反应优先于装饰粒子）。
- **Combat Readability**：越快越要分清玩家技能 / 敌人攻击 / 地面危险。

Halls of Torment / PoE：只参考节奏与机制抽象，不复制受保护内容。迁移时必须保住主动技能、Dash、永久角色、Class+Specialization、Passive/Mutation Tree、Skill+Support。
