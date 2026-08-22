# Mutagenic zh_CN 汉化术语表与词条句法规范（Glossary & Syntax v2）

> 用途：迁移或对照 `05_translation/` / `mods/c5-*` 时保持译名一致。  
> 不是任务入口，不启动新的汉化批次。当前主线：`AGENT.MD`（P1 Godot 4.7.1）。  
> 术语冲突以本表为准；与执行协议冲突以 `AGENT.MD` 为准。

> **版本**: v2.0（全量重构 · 权威版）
> **取代**: v0.1（Core Playable PoC）。本版为**唯一权威术语源**，覆盖全部 38+ 汉化切片（l1–l33）。任何切片与本文冲突，一律以本文为准。
> **原则**: 意义准确 > 玩家易理解 > **术语全站唯一** > 句法自然。语境优先，不机械直译；同一英文概念在**任意界面**只允许一个中文译名（专名豁免见 §1.6）。
> **生效范围**: 本文同时是 **STAT_NAMES / TAG_NAMES / craft_name / 帮助页 / ModHelp / 词条模板函数（StatsInfo.gd render_* 与 min_max / SkillTags.gd tags_to_string）** 的最终裁决。

---

## 0. 本版关键决策（速览）

| 域 | 裁决 | 一句话理由 |
|---|---|---|
| Crafting 体系根词 | **工艺** | 工艺之球(l27)/工艺制作(l31)/工艺选项(l30) 已成多数，统一为根词 |
| mod / modifier（物品修正） | **词缀** | ModHelp(l13)/工艺动作(l18)/词缀加工(l13) 全部已用"词缀"，帮助页"修饰"是落后残留 |
| stat（角色/物品属性值） | **属性** | EscapeMenu 面板、装备属性/物品属性(l14)、l28 均用"属性"，与"词缀"语义严格分离 |
| Item Modding（加工行为） | **加工** | 仅 CraftingBench 标题"物品与词缀加工"(l13) 保留 |
| Cold Damage（伤害类型） | **寒冷** | stat_name 寒冷伤害(l12)/SkillTags COLD=寒冷(l12) 是主源；帮助页"冰冷"改掉 |
| Toxic Damage | **毒素** | stat_name 毒素伤害(l12)/SkillTags TOXIC=毒素(l12) 是主源；帮助页"毒性"改掉 |
| Scramble | **洗练** | 与 Recombinate(重组) 语义必须分开；l30 帮助页"洗练"比 l18 按钮"重组"语义更准 |
| Recombinate | **重组** | "将存储词缀组合到物品" 正是"重组"；l18"再组合"改掉 |
| Freeze | **冻结** | 技能描述(l10)/帮助页(l31)/stat 冻结敌人(l12) 多数；状态图标 l17"冰冻"改掉 |
| Jolt | **电击** | 技能描述(l10)/帮助页(l31) 已用"电击"；l17"电震"改掉 |
| Electrocution | **触电** | 与 Jolt(电击) 撞名必须拆分；l31 已用"触电" |
| Vulnerable | **易伤** | 图标(l17)/stat(l12)/技能(l10) 多数；帮助页"脆弱"让位给 Brittle |
| Brittle | **脆弱** | 图标(l17) 权威；l10"易碎"改掉，与 Vulnerable(易伤) 彻底分离 |
| Hinder | **阻碍** | 图标(l17) 权威；l10"迟滞"改掉 |
| Hypothermia | **低温症** | 图标(l17) 权威；l10"失温"改掉 |
| Debilitate | **虚弱** | 图标(l17) 权威；l10"衰弱"改掉 |
| Increased | **提高** | 词条模板(l12/l33) 已部署"提高 N%"，全站统一 |
| Affix Effectiveness | **词缀效果** | l13 UI 已用；l31"词缀效率"改掉；**修复 l13 丢失的 % 号** |
| Damage Over Time | **持续伤害** | 全站已统一，维持 |

---

## 1. 权威术语总表（英文 → 唯一中文）

> 覆盖范围 = 受影响的切片 id / 文件。标注 `[全局]` 的禁止在任何切片改变。

### 1.1 工艺 / 制作系统（Crafting）

| 源文 | 中文 | 覆盖范围 |
|---|---|---|
| Crafting（体系） | 工艺 | [全局] |
| Crafting Help | 工艺帮助 | l14（现"制作帮助"改掉） |
| Crafting Options | 工艺选项 | l30 |
| Crafting Orbs | 工艺之球 | l27 |
| crafted（被动语态） | 工艺制作 | l31（"无法通过工艺制作"维持） |
| Item Crafting bench | 工艺工作台 | l27 教程、[全局] |
| Crafting Bench（互动物标题） | 物品与词缀加工 | l13 |
| Clear | 清除 | l18 craft_name |
| Store | 存入 | l18 / l30（l30"存储"改掉） |
| Restore | 恢复 | l18 / l30 |
| Scramble | 洗练 | l18（现"重组"改掉）/ l30 |
| Lucky Scramble | 幸运洗练 | l18（现"幸运重组"改掉）/ l30 |
| Godly Scramble | 神赐洗练 | l18（现"神赐重组"改掉）/ l30（"神圣洗练"改掉） |
| Scramble Prefixes | 洗练前缀 | l18（现"重组前缀"改掉） |
| Scramble Suffixes | 洗练后缀 | l18（现"重组后缀"改掉） |
| Add Random Mod | 添加随机词缀 | l18 |
| Remove Random Mod | 移除随机词缀 | l18 |
| Recombinate | 重组 | l18（现"再组合"改掉）/ l30 |
| Reroll Mod Values | 重掷词缀数值 | l18 / l30（现"重掷修饰数值"改掉） |
| Upgrade Random Mod | 升级随机词缀 | l18 / l30（现"升级随机修饰"改掉） |
| Permanently Lock Random Mod | 永久锁定随机词缀 | l18 |
| Unlock Random Mod | 解锁随机词缀 | l18 |
| Lock Mod | 锁定词缀 | l18 |
| Unlock Mod | 解锁词缀 | l18 |
| Orb of Experimentation | 实验之球 | l27 |
| Orb of Honing | 磨炼之球 | l27 |
| Orb of Enhancement | 强化之球 | l27 |
| Orb of Knowledge | 知识之球 | l27 |

### 1.2 词缀 / 物品系统（Mod / Affix）

| 源文 | 中文 | 覆盖范围 |
|---|---|---|
| mod / modifier（物品修正） | 词缀 | [全局]；l30/l31 帮助页所有"修饰"→"词缀" |
| Affix | 词缀 | [全局] |
| Prefix | 前缀 | l13 |
| Suffix | 后缀 | l13 |
| Implicit | 固有（词缀） | l13 / l31（"固有修饰"→"固有词缀"） |
| Drop Only Mod | 仅掉落词缀 | l13 / l31（"仅掉落修饰"→"仅掉落词缀"） |
| Mod Level | 词缀等级 | l13 / l31 / l30 |
| Maximum Mod Level | 词缀等级上限 | l31 |
| Available Affixes | 可用词缀 | l13 |
| Affix Effectiveness | 词缀效果 | l13（修复丢 %）/ l31（"词缀效率"改掉） |
| Item Modding（行为） | 加工 | l13 CraftingBench 标题 |
| Stat（角色/物品属性值） | 属性 | l14 / l28 / EscapeMenu / 帮助页"属性"章节 |
| Skill Stats | 技能属性 | l13 |
| Unique Mods | 独特词缀 | l31（"独特修饰"→"独特词缀"） |
| Mod Reference | 物品词缀参考 | l28（现"物品修饰参考"改掉） |
| Help Reference | 帮助参考 | l28 |
| Unique Item Reference | 独特物品参考 | l28 |
| Item Rarity / Rarity of Items Found | 物品掉落稀有度 | l16 |
| Quantity of Items Found | 物品掉落数量 | l16 |

### 1.3 伤害 / 数值

| 源文 | 中文 | 覆盖范围 |
|---|---|---|
| Physical Damage | 物理伤害 | l12 / l31 |
| Lightning Damage | 闪电伤害 | l12 / l31 |
| Cold Damage | 寒冷伤害 | [全局]；l31/l30"冰冷伤害"改掉 |
| Fire Damage | 火焰伤害 | l12 / l31 |
| Toxic Damage | 毒素伤害 | [全局]；l31"毒性伤害"改掉 |
| Damage over Time (DoT) | 持续伤害 | [全局] |
| Increased / Reduced | 提高 / 减少 | [全局]；l31"增加/减少"→"提高/减少" |
| More / Less | 更多 / 更少 | [全局] |
| Added（固定值） | 额外 | [全局]（词条模板已用） |
| Skill Damage Effectiveness | 技能伤害效用 | l12（"效用"避免与"词缀效率"混淆） |
| Added Damage Effectiveness | 附加伤害效用 | l12 |
| Critical Strike Chance | 暴击几率 | l12 / l31（"暴击率"→统一"暴击几率"） |
| Ailment Damage | 异常伤害 | l31 |
| Ailment Chance | 异常几率 | l12 / l31 |
| Damage Conversion | 伤害转化 | l31 |

### 1.4 状态 / 异常 / 诅咒

> 铁律：状态图标名(l17) / 帮助页(l31) / 技能描述(l10) **必须同源**。

| 源文 | 中文 | 覆盖范围 |
|---|---|---|
| Ailment（状态类别） | 异常状态 / 异常 | l31 |
| Bleed | 流血 | l17 / l31 |
| Rupture | 撕裂 | l31 |
| Burn | 燃烧 | l17 / l31 |
| Char | 焦灼 | l31 |
| Chill | 冰缓 | l31（现"寒冷"与伤害类型撞名，改掉） |
| Freeze | 冻结 | l17（现"冰冻"改掉）/ l31 / l10 |
| Jolt | 电击 | l17（现"电震"改掉）/ l31 / l10 |
| Electrocution | 触电 | l17（现"电击"改掉）/ l31 |
| Poison | 中毒 | l31 |
| Infection | 感染 | l31 |
| Vulnerable | 易伤 | l17 / l12 / l10 / l31（现"脆弱"改掉） |
| Exposed | 暴露 | l31 |
| Brittle（诅咒） | 脆弱 | l17 / l10（现"易碎"改掉） |
| Hinder（诅咒） | 阻碍 | l17 / l10（现"迟滞"改掉） |
| Hypothermia（诅咒） | 低温症 | l17 / l10（现"失温"改掉） |
| Debilitate（诅咒） | 虚弱 | l17 / l10（现"衰弱"改掉） |
| 诅咒系技能名 | {状态名}诅咒 | l10（衰弱诅咒→虚弱诅咒 / 迟滞诅咒→阻碍诅咒 / 易碎诅咒→脆弱诅咒 / 失温诅咒→低温症诅咒） |

### 1.5 技能标签（SkillTags，24 个）

| 源文 | 中文 | 备注 |
|---|---|---|
| Projectile | 投射物 | |
| Area | 范围 | |
| Curse | 诅咒 | |
| Buff | 增益 | |
| Castable | 可施放 | |
| Chain | 连锁 | |
| Passive | 被动 | |
| Duration | 持续时间 | |
| Triggerable | 可触发 | |
| Hit | 命中 | |
| Bomb | 炸弹 | |
| Fire | 火焰 | |
| Cold | 寒冷 | |
| Lightning | 闪电 | |
| Physical | 物理 | |
| Toxic | 毒素 | |
| Damaging | 伤害性 | |
| Utility | 实用 | |
| Elemental | 元素 | |
| Damage Over Time | 持续伤害 | |
| Aura | 光环 | |
| Melee | 近战 | |
| Attack | 攻击 | |
| Spell | 法术 | |

> 覆盖：l12（SkillTags.gd TagNames）。技能描述中"使用 X 标签技能"均引用本表。

### 1.6 专名豁免规则（区域 / 怪物 / 技能 / 天赋名）

以下属于**专有名词**，保留既有译名，**不**参与伤害类型术语统一，也不要求与新术语同源：

- 区域：寒霜洞窟（l16）、区域名含"寒霜/寒冰"者
- 怪物：寒冰魔像（l16）、骷髅电击者（l16）
- 技能/天赋名：冰霜弹（l8/l10）、寒冰碎片迸发、寒冰亲和、寒冰静电、寒冰研习、严寒、严寒光环、寒冰开局（l10/l16）
- 前缀/后缀词（ItemNameGenerator.gd，l18）：冰封、寒冷、剧毒、微光等——保持原译

> 判断规则：**能指代具体实体（某区域/某怪/某技能）** 的名为专名；**作为通用伤害类型/状态/词缀** 出现时一律用 §1.3/§1.4 的标准词。

### 1.7 品质（Normal / Magic / Rare / Unique）

**评估结论**：当前恢复源码与已翻译切片中，**未发现** normal/magic/rare 品质档位的 UI 展示文案（GeneInfo.gd 中 quality 指"词缀效果"数值，l13 已处理）。**暂不新增翻译条目**；若后续切片暴露品质档位，按此预留：
`Normal=普通`、`Magic=魔法`、`Rare=稀有`、`Unique=独特`（独特物品已在 l19/l27 使用，维持）。

---

## 2. 词条句法模式库（Syntax Pattern Library）

> 目标：解决"寒冷伤害的攻击技能提高 12%"式直译生硬 + 词条缺作用对象 + 数值格式不一。
> 总纲：**作用域前置，动宾后置，数值收尾**。
> 通用形式：`{作用域}的{stat}{修饰词}{数值}`（作用域为空时省略"的"）。

### 2.1 三大语法完整模式

| 语法 | 模板字符串 | 示例 | 说明 |
|---|---|---|---|
| **FLAT（额外，固定值）** | `{作用域}的{stat}额外 +{N}` / `额外 -{N}` | "攻击和法术技能的火焰伤害额外 +5"、"攻击技能的火焰伤害额外 -3" | 正数必带 `+`，负数带 `-`，零不渲染该行；作用于基础伤害 |
| **PERCENT（提高/减少，加算）** | `{作用域}的{stat}提高 {N}%` / `减少 {N}%` | "攻击技能的寒冷伤害提高 12%" | N 恒为正整数，正负由"提高/减少"表达，**不出现 `-` 号** |
| **MORE（更多/更少，乘算）** | `{作用域}的{stat}更多 {N}%` / `更少 {N}%` | "投射物技能的伤害更多 20%" | 同上；帮助页标注"乘算" |

- 非伤害类 FLAT（生命/护甲/抗性/几率等，无修饰词）：`{作用域}的{stat} +{N}`（% 型如 `+{N}%`）。
- 例：`最大生命值 +50`、`火焰抗性 +15%`、`攻击技能的暴击几率 +5%`。

### 2.2 无 tag（全局）默认处理

**规则：无 tags 的 mod → 省略作用域，不显示"所有技能的"。**
- 理由：①无 tag 词缀作用于角色全局，含技能与非技能属性，加"所有技能"对"最大生命值"类属性语义错误；②大多数无 tag 词条是角色属性（非技能作用域），加前缀属噪音。
- 全局伤害词条示例：`火焰伤害额外 +5`、`寒冷伤害提高 12%`。
- **消歧手段**：在帮助页（§3 说明文末尾）固定一句——"未标注技能类型的加成对所有伤害/所有技能生效。" 由帮助页统一负责全局语义，词条本身不重复。
- 实现：`render_tag_mods` 在 `tags==null || len(tags)==0` 时返回 `""`。

### 2.3 多 tag 拼接

**规则**：标签用中文顿号 `、` 连接；恰好两个标签用 `和`；三个及以上用 `、`（末尾 `和`）。随后接 `技能`。

| tags | 作用域串 | 完整词条 |
|---|---|---|
| [ATTACK] | 攻击技能 | 攻击技能的寒冷伤害提高 12% |
| [ATTACK, SPELL] | 攻击和法术技能 | 攻击和法术技能的火焰伤害额外 +5 |
| [ATTACK, SPELL, PROJECTILE] | 攻击、法术和投射物技能 | 攻击、法术和投射物技能的伤害更多 20% |

> 实现点：`SkillTags.gd` 的 `tags_to_string()` / `render_tag_list()` 当前用英文 `", "` 连接，必须改为上述中文规则（影响技能详情页标签行 + 词条作用域）。

### 2.4 数值范围 min_max

**规则**：`(5 to 8)` → `(5 至 8)`。保留圆括号，`to` 译为 `至`。
- 例：`攻击技能的寒冷伤害提高 (5 至 8)%`、`词缀等级 3：(12% 至 18%)`。
- 实现点：`StatsInfo.gd` `min_max(mn, mx)` 的 `" to "` → `" 至 "`。

### 2.5 百分比与 + 号规范

| 语境 | 格式 | 示例 |
|---|---|---|
| PERCENT 提高/减少 | `{N}%`（N 正整数，无 +/- 号） | 提高 12% |
| MORE 更多/更少 | `{N}%`（同上） | 更多 20% |
| FLAT 额外（正） | `+{N}`（必带 +） | 额外 +5 |
| FLAT 额外（负） | `-{N}`（带 -） | 额外 -3 |
| FLAT 百分比属性（正/负） | `+{N}%` / `-{N}%` | 火焰抗性 +15% |
| 非百分比 FLAT | `+{N}` / `-{N}` | 最大生命值 +50 |

### 2.6 GDScript 拼接顺序与需改函数清单

**拼接顺序**：`作用域(render_tag_mods) + "的"(可选) + stat_name[stat] + 修饰词 + 数值`

需修改（新一轮 CODE_PATCH，建议并入现有 l12/l33 所在 StatsInfo.gd 补丁）：

| 函数 | 现状（l12/l33 已 patch） | 改为 |
|---|---|---|
| `render_tag_mods` (StatsInfo.gd:1092) | `"的" + tags_to_string + "技能"` | `tags_to_string(tags) + "技能"`（无 tag 返回 `""`） |
| `render_passive_stat_line` (932) | `stat + tag_postfix + "提高 N%"` | `tag_postfix + ("的" if tag_postfix else "") + stat + verb + value` |
| `render_item_stat_line` (988) | 同上 | 同上 |
| `render_range_into_rtl` (1028) | 同上 | 同上，数值位用 `min_max(min,max)` |
| `render_stat_name` (914) | stat-first | 作用域前置，verb（额外/提高/更多）后置 |
| `render_formatted_number` (969) | FLAT 正数已带 + | 维持 |
| `min_max` (1098) | `"(5 to 8)"` | `"(5 至 8)"` |
| `SkillTags.tags_to_string` / `render_tag_list` (66/70) | `join(", ")` | 中文顿号/和规则 |

> 拼接伪码：
> ```
> scope = render_tag_mods(tags)          # "" 或 "攻击、法术技能"
> line  = (scope + "的" if scope else "") + stat_name[stat]
> line += "提高 "  # 或 减少/更多/更少/额外
> line += value    # "12%" / "+5" / "(5 至 8)"
> ```

---

## 3. 伤害加成机制标准说明文（帮助页模板，l31 Help.tscn 复用）

```bbcode
[center]伤害加成机制[/center]

词缀中的伤害加成分为三类，它们的计算方式不同：

[color=#d38b1a]提高[/color]与[color=#d38b1a]减少[/color]（Increased / Reduced）为加算：
同类效果彼此相加后再作用于基础值。例如"攻击技能的寒冷伤害提高 12%"与"寒冷伤害减少 8%"合并后，寒冷伤害整体提高 4%。

[color=#d38b1a]更多[/color]与[color=#d38b1a]更少[/color]（More / Less）为乘算：
每个效果独立相乘，叠加越多收益越大。例如两个"更多 20%"会相乘为 1.2 × 1.2 = 1.44 倍。

[color=#d38b1a]额外[/color]（Added）为固定值：
直接加到基础伤害上，如"火焰伤害额外 +5"直接增加 5 点火焰伤害。

每种伤害类型的最终伤害计算如下：
[color=#d38b1a]最终伤害 = 基础伤害 × (1 + 提高总和 − 减少总和) × 更多之积 × 更少之积[/color]

[color=#b3b3b3]未标注技能类型的加成对所有伤害与所有技能生效。[/color]
```

> 说明：本段替换 l31 现有"增加 vs 更多"章节（"增加"→"提高"，并补"额外"类别与无作用域说明）。

---

## 4. 术语变更对照表（旧译 → 新译，按切片）

| 切片 | 旧译 | 新译 | 位置 |
|---|---|---|---|
| l14 | 制作帮助 | 工艺帮助 | CraftingHelp.tscn 标题 |
| l17 | 冰冻 | 冻结 | Freeze.tscn |
| l17 | 电震 | 电击 | Jolt.tscn |
| l17 | 电击 | 触电 | Electrocution.tscn |
| l17 | （Brittle=脆弱 / Vulnerable=易伤 维持） | — | Curses/Generic |
| l18 | 重组 / 幸运重组 / 神赐重组 | 洗练 / 幸运洗练 / 神赐洗练 | Genes.gd craft_name SCRAMBLE 系 |
| l18 | 再组合 | 重组 | Genes.gd craft_name RECOMBINATE |
| l18 | 重组前缀 / 重组后缀 | 洗练前缀 / 洗练后缀 | Genes.gd craft_name |
| l18 | （存入 / 恢复 / 重掷词缀数值 等已合规） | — | Genes.gd craft_name |
| l27 | "You can use the various 工艺之球 in the Item Crafting bench…" | 全中文"你可以在藏身处的工艺工作台使用各种工艺之球……" | OrbTip |
| l27 | "Your 装备配置 is your chosen set of Items…" | 全中文"你的装备配置是你为角色选择的一套物品……" | LoadoutScreenTip |
| l27 | "In Mutagenic, you can have up to 6 Active 技能…" | 全中文"在 Mutagenic 中，你最多可以同时拥有 6 个主动技能……" | WeaponIntro |
| l27 | "Please select a skill from the \"" | 全中文（接技能名）"请从 \"" | NoWeaponWarning |
| l28 | 物品修饰参考 | 物品词缀参考 | Menu.tscn Mod Reference |
| l30 | 存储 | 存入 | CraftingHelp |
| l30 | 神圣洗练 | 神赐洗练 | CraftingHelp |
| l30 | 重掷修饰数值 / 升级随机修饰 | 重掷词缀数值 / 升级随机词缀 | CraftingHelp |
| l30 | 修饰属性（全篇"修饰"） | 词缀 | CraftingHelp 全篇 |
| l30 | 冰冷伤害 / 毒性伤害 | 寒冷伤害 / 毒素伤害 | CraftingHelp |
| l31 | 修饰（全篇） | 词缀 | Help.tscn Mechanics |
| l31 | 词缀效率 | 词缀效果 | Help.tscn Affix Effectiveness |
| l31 | 冰冷伤害 / 毒性伤害 | 寒冷伤害 / 毒素伤害 | Help.tscn Damage Types |
| l31 | 增加 / 减少 | 提高 / 减少 | Help.tscn 加算章节 |
| l31 | 脆弱（Vulnerable） | 易伤 | Help.tscn Ailments |
| l31 | 寒冷（Chill） | 冰缓 | Help.tscn Ailments（与伤害类型"寒冷"分离） |
| l10 | 易碎诅咒 / 使其易碎 | 脆弱诅咒 / 使其脆弱 | 技能树（Brittle 系） |
| l10 | 迟滞诅咒 / 使其迟滞 | 阻碍诅咒 / 使其阻碍 | 技能树（Hinder 系） |
| l10 | 失温诅咒 / 使其失温 | 低温症诅咒 / 使其低温症 | 技能树（Hypothermia 系） |
| l10 | 衰弱诅咒 / 使其衰弱 | 虚弱诅咒 / 使其虚弱 | 技能树（Debilitate 系） |
| l13 | `"+" + str(quality) + "词缀效果"`（丢 %） | `"+" + str(quality) + "% 词缀效果"` | GeneInfo.gd / GeneEditor 两处 |

---

## 5. 待用户拍板的决策点（≤5）

1. **Cold 元素命名**：统一「寒冷」（推荐，stat_name/SkillTags 主源，l12 已部署） vs 改「冰冷」（更文雅但与 l12 全量冲突）。→ 默认按「寒冷」执行。
2. **mod 统一「词缀」**：帮助页 l30/l31 全部「修饰」改「词缀」（推荐）；「属性」保留给角色属性。→ 默认执行。
3. **无 tag 全局词条**：省略作用域 + 帮助页说明（推荐） vs 强制显示「所有技能的」。→ 默认省略。
4. **Scramble/Recombinate 工艺命名**：洗练 / 重组（推荐，语义清晰） vs 维持 l18 现状（重组 / 再组合）。→ 默认洗练/重组。
5. **Freeze=冻结**（推荐，多数同源） vs **冰冻**（l17 现状，更口语）。→ 默认冻结。

> 除上述 5 项外，其余冲突（Jolt/Electrocution、Vulnerable/Brittle、Hinder/Hypothermia/Debilitate、提高、词缀效果、chill=冰缓 等）均已在 §0/§1 直接定案。

---

## 6. 影响面清单（预计需修改的切片 / 文件）

| 类别 | 文件 | 变更类型 |
|---|---|---|
| 代码层句法 | `Globals/StatsInfo.gd`（render_tag_mods / render_passive_stat_line / render_item_stat_line / render_range_into_rtl / render_stat_name / min_max） | CODE_PATCH（作用域前置 + 至） |
| 代码层标签 | `Globals/SkillTags.gd`（tags_to_string / render_tag_list） | CODE_PATCH（中文顿号/和） |
| 状态图标 | `Scenes/StatusEffects/**`（Freeze/Jolt/Electrocution.tscn） | TEXT_PATCH（l17 重打） |
| 工艺动作 | `Globals/Genes.gd`（craft_name） | TEXT_PATCH（l18 重打） |
| 帮助页 | `Scenes/Popups/Dialogs/Help/Help.tscn` | TEXT_PATCH（l31 重打） |
| 工艺帮助 | `Scenes/Popups/Dialogs/HelpTip/CraftingHelp/CraftingHelp.tscn` | TEXT_PATCH（l30/l14 重打） |
| 教程 | `Scenes/Popups/Dialogs/HelpTip/{OrbTip,LoadoutScreenTip,WeaponIntro,NoWeaponWarning}.tscn` | TEXT_PATCH（l27 补全中文） |
| 技能树诅咒 | `Globals/Skills.gd`（或 l10 对应源）诅咒描述 | TEXT_PATCH（l10 重打） |
| 品质标签 | `Scenes/Tooltips/GeneTooltip/GeneInfo.gd` + GeneEditor | TEXT_PATCH（l13 补 %） |
| 主菜单 | `Scenes/Menu.tscn` | TEXT_PATCH（l28 物品词缀参考） |

> 执行顺序建议：先 StatsInfo/SkillTags 代码层 → 帮助页（l31/l30）→ 状态图标（l17）→ 工艺动作（l18）→ 技能树诅咒（l10）→ 教程（l27）→ 补漏（l13/l14/l28）。每次产出 Build ID + 语义验证（GDRE 从最终 EXE 恢复确认新值已嵌入）。
