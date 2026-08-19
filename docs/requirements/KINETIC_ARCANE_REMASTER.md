# Mutagenic — Kinetic Arcane Remaster

> **文档角色**：Mutagenic 现代化重制的体验层总纲（L2 Requirements）。
> **Authority**：低于 `AGENTS.md` 与 `status.json`；任何冲突以 L0/L1 为准。
> **关系**：`HD_UI_REMASTER.md` 继续作为 UI / Presentation 子系统规范。本文件扩展项目目标到 Player Response、Movement、Combat、Camera、Audio、Enemy Reaction 与 Build Density。
> **工程原则**：所有实际游戏修改仍必须通过声明式 MOD、精确 preimage 守卫、canonical pipeline、fresh embed 与分层验证完成；不得直接修改 `00_original/`、`03_raw/`、`04_recovered/`。

---

## 1. 总目标

Mutagenic 的目标不再只是“高清 UI”，而是：

> **让同一款 Mutagenic 在保持其构筑、信息结构和暗色 ARPG 身份的前提下，获得现代 PC 独立 ARPG 的响应速度、移动爽感、命中因果感、群怪释放感和视觉完成度。**

静态视觉语言继续使用：

**Dark Arcane Tactical**

动态战斗语言新增：

**Kinetic Arcane Combat**

两者必须同时成立：

- UI 冷静、精密、克制；
- 战斗快速、连续、猛烈但仍清晰；
- 不机械复制 Path of Exile 的 UI、美术或具体技能；
- 学习的是“速度 × 密度 × 构筑 × 连锁反馈 × 清晰度”的体验结构。

---

## 2. 最高设计优先级

以后所有体验层选择统一按以下顺序判断：

1. **Player Response**
2. **Gameplay Readability**
3. **Interaction Clarity**
4. **Impact**
5. **Visual Hierarchy**
6. **Consistency**
7. **Modern Appearance**
8. **Decoration**

也就是说：

> 按下去是否立刻响应 → 战斗是否读得懂 → 打中是否有感觉 → 最后才是是否漂亮。

---

## 3. 五个体验支柱

### 3.1 Instant Control

角色必须跟手。

重点不是单纯提高 `movement_speed`，而是缩短“输入 → 明确动作结果”的体感延迟。

需要审计：

- 移动输入到速度变化；
- 转向响应；
- 移动 → 攻击；
- 攻击 → 移动；
- 攻击/施法后摇；
- Dash 启动与结束；
- 鼠标目标获取；
- 技能取消窗口；
- 碰撞边缘滑动；
- 高攻速/高施法速度下的输入连续性。

第一轮优先修改“响应”，而不是大幅改平衡。

### 3.2 Kinetic Traversal

高速感由以下乘积产生：

**控制响应 × 世界参照 × 镜头 × 动画/FX × 实际速度**

因此禁止把“高速化”简化成全局移速翻倍。

优先尝试：

- 适度提高基础/成长移动能力；
- Dash 更直接；
- 高速时非常轻的运动反馈；
- 地面/环境提供稳定速度参照；
- 不让背景、网格或 HUD 抢夺注意力；
- 后期构筑允许移动能力显著突破初始尺度。

### 3.3 Impact Stack

一次命中不是一个粒子，而是一组同步因果反馈：

1. 技能本体到达/接触；
2. 命中点核心反馈；
3. 敌人状态变化；
4. 适量粒子/碎片/轨迹；
5. 声音 transient；
6. 必要时的镜头 impulse；
7. 致死时进入独立 Kill Feedback。

优先级：

**Enemy Reaction > Contact FX > Audio > Camera > Decoration**

预算不足时，宁可少粒子，也不能让敌人“像什么都没发生”。

### 3.4 Combat Readability

战斗越快，视觉纪律越严格。

必须明确区分：

- 玩家技能；
- 敌人攻击；
- 地面危险；
- 可交互物；
- 掉落物；
- 状态/稀有度；
- 装饰效果。

禁止通过满屏 Bloom、长拖尾、大面积白闪或无差别屏幕震动制造“爽感”。

### 3.5 Build Density

真正长期的 ARPG 爽感来自构筑逐步放大游戏尺度。

允许通过现有系统逐步放大：

- attack / cast speed；
- projectile count；
- projectile speed / range / lifetime；
- pierce / chain；
- AoE；
- on-hit / on-crit / on-kill trigger；
- movement / dash；
- kill-triggered secondary effects。

初期保持清楚；中后期允许形成明显的连锁反应和清屏能力。

---

## 4. Motion / Impact Design Tokens

UI 已有 Colors / Typography / Spacing / Radius / Border / Shadow / Animation Timing。

战斗必须建立对应的动态 Token，而不是每个技能自己散落随机数。

### 4.1 Motion Profiles

至少定义概念层级：

- `MOVE_NORMAL`
- `MOVE_FAST`
- `MOVE_BURST`
- `DASH_LIGHT`
- `DASH_HEAVY`

Profile 可统一约束：

- trail 强度；
- 残影是否允许；
- dust/streak 数量；
- camera lead；
- 音效层级。

### 4.2 Impact Profiles

至少定义：

- `HIT_LIGHT`
- `HIT_MEDIUM`
- `HIT_HEAVY`
- `HIT_CRIT`
- `KILL_NORMAL`
- `KILL_ELITE`
- `BOSS_IMPACT`
- `BOSS_KILL`

Profile 统一描述：

- hit flash 时间；
- enemy recoil / squash 范围；
- contact FX 强度；
- 粒子数量上限；
- camera impulse；
- audio transient / low-frequency layer；
- death burst 等级。

实现可以先是常量/函数，不强求一开始创建复杂资源系统；但语义必须统一。

---

## 5. Hit Stop 规则

高速 ARPG 禁止把传统动作游戏式 Hit Stop 应用于每次普通命中。

原因：当攻击频率提高到 5–20 hit/s 时，全局时间停顿会转化为粘滞和卡顿感。

规则：

- 普通命中：默认无全局 hit stop；
- 快速多段：禁止逐 hit 停顿；
- Heavy / Crit / Elite kill：允许极短、受控的特殊时间反馈，但必须通过实机验证；
- Boss 强攻击/死亡：可使用更明显的时间层反馈；
- 若 Godot 3.x 实现全局 time scale 造成副作用，优先不用，而不是为了“打击感”强行引入。

---

## 6. Enemy Reaction

敌人必须成为命中反馈的第一载体。

优先尝试不破坏逻辑的短时反馈：

- 40–100ms 的颜色/亮度压缩；
- 短时轮廓强化；
- 极轻方向性 recoil；
- 局部 squash/stretch（仅适合的 Sprite/Node）；
- 稀有/精英使用更克制但更明确的反馈；
- DoT 不应像 direct hit 一样频繁闪烁。

任何反馈不得改变实际碰撞/伤害结果，除非对应 MOD 明确声明玩法变化。

---

## 7. Kill Feel

Hit Feel 与 Kill Feel 分开设计。

普通怪死亡：

- 快；
- 短；
- 清楚；
- 不阻塞下一次移动/攻击。

Elite Death：

- 明显高一级；
- 可增加更强 contact/death burst 与声音层；
- 仍避免遮住地面危险。

Boss Death：

- 是最高等级 release event；
- 可以独立设计节奏、声音和镜头；
- 不复用“普通怪粒子放大 5 倍”的粗暴方案。

On-kill、chain、explosion 等构筑效果应把 Kill Feel 转化为连续因果链，而不是无来源的屏幕烟花。

---

## 8. Camera System

Camera 必须进入正式设计系统。

目标：高速时稳定，重击时有力。

默认规则：

- 普通移动：稳定；
- 高速移动：可测试非常轻的 movement lead；
- Dash：短促 velocity impulse，可选；
- 普通 hit：默认不 shake；
- Heavy hit：很小 impulse；
- Crit / Elite kill：比 Heavy 高一级；
- Boss heavy / kill：允许更完整反馈。

所有 camera feedback 必须聚合并设最大振幅/频率上限。

禁止多个 AoE 命中事件逐个叠加造成“持续地震”。

如果现有工程没有集中 Camera 管理器，第一轮先复用实际 Camera2D 所属节点做最小实现；只有验证成功后才考虑抽象公共管理器。

---

## 9. Audio Impact

声音是打击感的一部分，不是最后补丁。

核心攻击应按实际资产能力考虑：

- attack / cast；
- travel；
- impact；
- enemy reaction；
- kill。

原则：

- Heavy 不是把 Light 单纯调大音量；
- Crit 应有独立可识别瞬态；
- 高频重复技能应有轻微 pitch / volume variation；
- 多怪同帧死亡必须限制声音叠加，避免削波和噪声墙；
- 现有 `.sample` 优先复用，新增音频必须走 ASSET_PATCH/asset overlay 与许可/来源记录。

---

## 10. UI 与高速战斗的关系

沿用 `HD_UI_REMASTER.md` 的 Dark Arcane Tactical 方向，并新增：

> **战斗越激烈，HUD 越安静。**

Combat 中必须一眼读取：

- Health / 核心资源；
- 技能状态/关键冷却；
- 高危状态；
- Boss/Elite 关键状态。

等级、职业、菜单入口、次要统计在战斗中降到第二视觉平面。

Hub 可以承载更多信息密度。

---

## 11. 对旧 UI-only 玩法禁令的解释更新

`HD_UI_REMASTER.md` 为保证纯视觉阶段安全，曾禁止修改玩法逻辑、碰撞、移动速度和伤害逻辑。

在本总重制范围内，该限制调整为：

- **UI/Presentation MOD** 仍不得顺手改玩法；
- **Gameplay/Combat MOD** 可以修改移动、攻击节奏、技能行为、怪物密度、碰撞体验或伤害相关参数，但必须独立声明、可回滚、可验证；
- 每个 gameplay change 必须说明目标、风险、预期体感和 balance 影响；
- 不允许把视觉、平衡、存档、核心机制十几项混成一个不可审查大补丁；
- 每一批独立 Candidate；
- 未完成实机战斗验证的 gameplay MOD 不得声称“手感已验证”。

这不是放宽 `AGENTS.md`，只是把项目从 UI Remaster 扩展为完整 Experience Remaster。

---

## 12. 新阶段顺序

### PHASE K0 — EXPERIENCE AUDIT

在 Visual Audit 之外审计：

- Player controller；
- movement / dash；
- attack / cast execution；
- projectile；
- enemy hit/death；
- Camera2D；
- Audio；
- particles / VFX；
- TCE triggers；
- monster density / spawn pacing。

输出精确 Script / Function / Resource / Risk / Recommended Upgrade。

### PHASE K1 — HD CLEANUP + RESPONSIVENESS

继续现有 `v1-hd-cleanup` 路线，并增加低风险响应实验。

不做大规模 balance 重构。

### PHASE K2A — HUB VERTICAL SLICE

继续 `PHASE2_DESIGN_SPEC.md` 的 Hub 样板。

验证 Dark Arcane Tactical。

### PHASE K2B — COMBAT VERTICAL SLICE

新增核心阶段。

在一个小型代表性战斗场景验证：

- normal pack；
- ranged enemy；
- elite；
- fast skill；
- heavy skill；
- crit；
- group kill；
- dash / burst movement。

如果 Combat Slice 不成功，禁止把 VFX 全局铺开。

### PHASE K3 — KINETIC COMBAT PASS

建立 Impact Profiles、Enemy Reaction、Kill Feel、Camera、Audio、技能轨迹与命中层级。

### PHASE K4 — UNIFIED DESIGN SYSTEM

统一：

- UI Tokens；
- Motion Tokens；
- Impact Tokens；
- Camera Tokens；
- Audio 层级规则；
- VFX budget。

### PHASE K5 — GAMEPLAY SPEED & BUILD DENSITY

在 Vertical Slice 已证明方向正确后，才系统调整：

- movement；
- attack/cast pacing；
- cancel windows；
- projectile behavior；
- monster packs；
- AoE / chain / pierce；
- TCE trigger density；
- build growth curve。

### PHASE K6 — GLOBAL ROLLOUT + ASSET PASS

扩展到所有关卡、技能、怪物和 UI，并处理仍无法通过程序反馈掩盖的低分辨率 Sprite。

---

## 13. 性能预算

Godot 3.5.3 custom build / GLES3 2D 下：

- 禁止每个 hit 创建昂贵 Shader；
- 禁止大范围实时 Blur；
- 禁止全屏多 Pass 作为基础画质；
- 粒子必须有单帧/同屏预算；
- 高频事件应聚合，而不是每 hit 独立创建重对象；
- camera/audio 同样需要事件节流；
- 优先复用现有 Particles2D、Tween、CanvasItem 和 Sprite 能力。

目标是高帧率下仍有冲击力。

---

## 14. 工程落地规则

所有实际实现：

1. 先从本机只读 `04_recovered` 定位精确源码；
2. 生成独立 `mods/<id>/mod.json`；
3. 每个 patch 必须有精确 `preimage_sha256` 与 `expected_occurrences`；
4. resolve → apply → compile → pack → fresh embed；
5. S0/S1 必跑；
6. 玩法改动至少增加对应 S4 semantic/runtime check；
7. 视觉/打击感至少需要 S5 人工或可重复 capture；
8. Candidate 不自动晋升 baseline。

GitHub 仓库未提交 recovered 明文源码时，禁止根据索引猜 `old_text` 制作假 CODE_PATCH。

---

## 15. 验收问题

每轮 Combat Candidate 必须回答：

### Response

输入是否更快得到明确结果？高速攻击/移动是否仍可控？

### Readability

高密度战斗中，玩家技能、敌方危险、掉落和 HUD 是否仍分层？

### Impact

普通 hit、heavy、crit 是否有明显层级，而不是所有反馈同样大？

### Enemy Reaction

玩家是否能仅看敌人状态变化就感知命中？

### Kill Feel

单杀、群杀、Elite、Boss 是否有不同释放等级？

### Movement

速度感是否来自完整运动系统，而不是单纯坐标变快？

### Camera

是否增强重击而没有造成高速战斗眩晕/抖动？

### Audio

高速重复是否仍清楚，不形成单一样本机关枪或声音墙？

### Performance

高密度 pack + 多 projectile + chain/trigger 时是否仍保持目标帧率？

### Determinism

所有变化是否仍能从 pristine 基线由声明式 MOD 完整重现？

---

## 16. 最终体验目标

Hub：

> 冷静、幽暗、精密、克制。

Combat：

> 角色响应直接，移动快速，技能接触清楚，敌人明确受击，群体死亡产生连续因果，构筑成长逐渐突破初始尺度，但关键危险始终可读。

最终玩家应觉得：

> **“这是同一个 Mutagenic，但现在真的像一款完成度很高、节奏现代的 ARPG。”**

而不是：

> “这个 MOD 加了很多特效。”
