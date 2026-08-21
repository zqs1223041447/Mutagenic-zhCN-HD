# Gameplay 架构保持与深化

职责分层：

- Character Level：基础成长。
- Class：起始战斗底盘。
- Passive/Mutation Tree：广域路线与桥接。
- Specialization：职业定义级规则改变，独立于 Passive。
- Active Skill：动作身份。
- Support：技能局部行为变换。
- Equipment：装备承载。
- Gene/Jewel：插件层，具体形态可迭代但不再与 Equipment 混为同一概念。
- Craft：演化有价值掉落。
- Map/Atlas：风险、收益、目标农场。

运行时优先抽象：StatEngine、ModifierEngine、TagEngine、CombatEvent、TCE v2、deterministic RNG、damage trace。

TCE 继续利用现有 trigger/condition/effect 基础，但必须加递归/事件预算保护，不能把所有机制硬塞进一个万能系统。