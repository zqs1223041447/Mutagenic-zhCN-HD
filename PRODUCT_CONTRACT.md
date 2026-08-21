# PRODUCT_CONTRACT.md — 产品北极星与锁定决议

## 1. Product North Star

核心循环：

```text
升级 → 杀怪 → 爆装备 → 构筑变强 → 进入更高风险/收益内容 → 继续杀怪
```

世界观、剧情和 IP 重要性**低于**玩法闭环、视觉一致性和 Build 深度。

## 2. USER_LOCKED（未经用户新指令不得改）

- Godot 4.7.1 stable 唯一活动 Product 引擎
- Godot 3.5.3 只读 Legacy
- 0 人工代码目标
- 主动 ARPG（不 Survivor 化）
- 永久角色
- Dash
- Class + Specialization
- Passive / Mutation Tree
- Active Skill + Support
- 不复制 Halls of Torment / Path of Exile 受保护内容
- 固定中央集成分支 `agent/kinetic-arcane-remaster-foundation`

## 3. 系统关系（已确认）

| 系统 | 说明 |
|------|------|
| Mutation Tree | 等价当前 Passive Tree 语义，不新增冗余第三棵大树 |
| Specialization | 独立于 Passive，承担职业定义级规则改变 |
| Skill | 继续 Active Skill + Support，不改成 PoE 装备插槽体系 |
| Equipment / Gene | 旧工程中 Gene 实际承担 Equipment 角色。Product 要把 Equipment 与 Gene 概念拆开 |
| Jewel | 后续可用的 itemized 插件层候选，具体实现属 ARCH_DEFAULT |

## 4. Item Philosophy

- Base Type 可以广泛掉落
- Item Level / 内容层控制 Affix tier、特殊池与权重
- Rare 偏通用数值天花板
- Legendary 偏规则改变与 Build Anchor
- Legendary 身份稳定、数值允许随机
- **不需要 Identification**
- Endgame 保留边际优化

## 5. Endgame 方向（高阶）

保留 Campaign World Map，并发展：

```text
Map Item → Craft → Consume → Instance → Boss / Drop → Next Map → Atlas
```

Atlas 支持奖励强化、目标农场和玩家塑造自己的终局路线。

**当前阶段（P1）不展开具体实现。** 只需保证迁移不丢失相关数据与契约。

## 6. 参考边界

### Halls of Torment
- 参考：暗黑复古视觉语言、怪潮密度、轮廓与危险信息可读性、战斗/击杀/死亡/VFX 节奏
- 不允许：复制资产、文本、角色、敌人设计；把游戏改成 Survivor 自动攻击

### Path of Exile / PoEDB
- 参考机制：Base Type / Affix、Skill / Support 深度、Craft、Monster Mods、Map Mods、Map Item、Atlas、Target Farming、Build 深度
- 流程必须是：External Reference → Mechanism Abstraction → Mutagenic Original Design → Schema → Implementation
- 不得复制受保护资产、文本、名称或数值表；不得默认批量抓取 PoEDB

## 7. ARCH_DEFAULT vs OPEN

- **ARCH_DEFAULT**：AI 可在有 Evidence 时修改，但必须记录 Decision（如 Runtime 服务边界、测试框架、pooling、Elite/Boss AI 等）
- **OPEN**：普通工程细节由 AI 决定（文件拆分、helper API、命名、临时实现方法等）

## 8. 不可退化清单（迁移时必须保护）

必须保留或恢复：主动技能、Dash、永久角色、Class+Specialization、Passive/Mutation Tree、Active Skill+Support、Equipment、Save/Load、Craft、Legendary/Rare、Campaign、Map Item/Map Mods、Atlas 基础、Combat Event / TCE 可演化基础。
