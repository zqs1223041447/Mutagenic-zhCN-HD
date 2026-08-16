你现在负责 Mutageni 项目的**首个实际汉化 MOD 落地任务**。

本任务不是继续做源码研究报告，也不是继续扩大文档索引。

你的首要目标是：

**尽快交付一个用户可以实际启动、游玩、安装/卸载的中文版本，并建立后续全量汉化可以持续迭代的稳定工作流。**

---

# 一、项目现状

当前项目已有以下成果：

* `04_recovered`：可信恢复源码参考工程。
* 已有 5058 / 5058 文件与 clean manifest 哈希一致的纯净性验证。
* `docs/ai/source_index.json`

  * 525 个 `.gd` 文件索引。
* `docs/ai/source-map.md`

  * 525 个脚本的职责地图。
* `docs/ai/scene-resource-map.md`

  * 已整理场景、关卡、职业、专精、技能、输入、存档等 schema 信息。
* `docs/ai/secondary-development-guide.md`

  * 已包含本地化 / 技能 / 地图 / 存档等二次开发方向。
* P7-FIX 已存在 runtime candidate：

  * `10_logs/P7-fix-persistence-20260814/runtime_candidate/Mutagenic.exe`
* candidate 已完成此前机器和人工验证，但是否正式成为长期 baseline 仍需遵守项目当前状态定义。

在开始工作之前，必须先读取：

* `AGENTS.md`
* `PROJECT_STATE.md`
* `status.json`
* `docs/ai/secondary-development-guide.md`
* `docs/ai/source-map.md`
* `docs/ai/scene-resource-map.md`
* 与 localization / UI / Font / MOD loader / 构建有关的现有脚本和文档

已有项目事实优先于你的默认经验。

---

# 二、最高优先级

本阶段的用户需求只有一个最高优先事项：

## 尽快玩到汉化后的游戏。

因此：

不要为了追求一次性 100% 汉化而迟迟不交付可运行版本。

不要重新做一遍已经完成的源码地图。

不要重构整个游戏。

不要先建设庞大的通用 MOD SDK。

不要先做技能、装备、天赋、地图或人物模型修改。

除非汉化正常运行所必需，否则不要扩大任务范围。

优先采用：

**最小修改 + 最快闭环 + 可重复构建 + 可卸载恢复原版**

的方案。

---

# 三、硬性安全规则

## 1. 禁止访问 F: 盘

不得：

* 读取
* 枚举
* 扫描
* 搜索
* 索引
* 修改
* 写入

宿主机 `F:` 盘中的任何内容。

所有命令、脚本、搜索工具和自动发现逻辑均必须排除 F:。

---

## 2. 不得污染 recovered clean baseline

`04_recovered` 是参考源。

原则：

**只读参考，不原地修改。**

不得：

* 修改其 `.gd`
* 修改资源
* 修改 import 文件
* 自动格式化
* 修复代码
* 写缓存进去
* 生成 Godot `.godot` 缓存到 clean baseline

如需要用于开发：

复制到独立开发目录或使用现有 MOD 工作区。

---

## 3. 不得破坏现有生产构建管线

严格遵守：

`AGENTS.md`

以及已有构建契约。

不要为了汉化方便修改现有生产构建方式。

汉化优先走当前项目所定义的：

**声明式 MOD / Resource override / localization 扩展机制**

如果现有机制无法完成，再基于证据设计最小兼容方案。

不得未经验证直接侵入式修改 Runtime 核心代码。

---

# 四、第一步：确认游戏实际文字系统

不要凭文件名猜。

利用已有：

* source index
* source map
* schema
* recovered scripts
* resources

定位所有实际文本来源。

重点调查：

1. Godot Translation / `.translation` / `.csv` / `.po` 等正式本地化机制是否存在。
2. UI `.tscn` 中是否直接存在英文字符串。
3. `.tres` / `.res` / JSON / config 中是否存在：

   * skill name
   * description
   * class name
   * specialization
   * item text
   * talent text
4. GDScript 中是否存在硬编码 UI 文本。
5. 动态拼接文本的位置。
6. 数值占位符文本。
7. 富文本 / BBCode。
8. 字体资源和 fallback font。
9. 当前语言/locale 获取逻辑。
10. 是否已有 locale 切换接口。
11. 是否已有 MOD localization merge / override 机制。

最后形成一个**实际文本来源分类结果**。

但是：

不要因为调查而无限扩展。

只分析到足够实现首个中文版本即可。

---

# 五、第一阶段目标：核心可玩汉化 PoC

第一轮不要尝试翻译全部游戏。

必须先制作：

# `zh_CN Core Playable PoC`

至少覆盖实际运行中的以下内容。

## A. 主菜单

包括能实际看到的：

* 开始游戏
* 继续游戏
* 设置
* 退出
* 返回
* 确认
* 取消

具体以游戏实际 UI 为准，不得虚构不存在的文本。

---

## B. 基础游戏 UI

优先：

* 暂停
* 继续
* 生命
* 等级
* 经验
* 技能选择
* 升级相关 UI
* 常用按钮
* 战斗关键提示

---

## C. 职业 / 专精

项目目前已识别：

* 4 个职业
* 8 个专精

第一版至少应保证：

职业名称和玩家在选择/游玩过程中会直接看到的核心说明能够正常显示中文。

---

## D. 技能

项目目前已识别约 53 个技能。

PoC 不要求一次翻完 53 个。

优先选择：

* 玩家开局可能遇到的技能
* 最常见技能
* 一个带数值变量的技能
* 一个描述较长的技能

至少翻译 5～10 个技能，验证：

* 名称
* 描述
* 数值
* 换行
* 富文本
* 动态变量

均正常。

---

## E. 弹窗

至少选择一个实际游戏弹窗进行汉化。

用于验证：

UI 控件和动态文本路径不是只在主菜单有效。

---

# 六、中文字体是必须完成的功能，不是以后再做

必须实际验证中文字体渲染。

要求：

* 简体中文无方块。
* 常用中文标点正常。
* 英文、数字仍正常显示。
* 技能说明中的 `%`、`+`、`-`、小数等正常。
* UI 不出现明显文本裁切。
* 字号不因中文字体导致严重错位。
* 原有图标字体不能被错误覆盖。

如果原字体不包含 CJK：

优先研究 Godot 的 font fallback / DynamicFont / FontFile / Theme fallback 机制。

不要为了支持中文而把整个 UI Theme 粗暴替换成一个字体。

如果存在 icon font：

必须防止中文字体替换导致图标丢失。

---

# 七、第一阶段验收标准

PoC 只有满足下面所有条件才算成功。

## 安装前

原始游戏能够运行。

记录基线状态。

---

## 安装汉化 MOD 后

启动游戏。

必须实际确认：

1. 主菜单出现中文。
2. 中文字体正常。
3. 开始/继续游戏正常。
4. 至少一个游戏内 UI 显示中文。
5. 职业/专精中文至少部分生效。
6. 5～10 个目标技能名称与描述显示中文。
7. 一个动态/带数值描述正常。
8. 一个弹窗正常。
9. 游戏能够实际进入战斗。
10. 不因 localization 导致脚本错误。
11. 存档功能不被破坏。
12. 汉化不改变游戏核心玩法。

---

## 卸载汉化 MOD 后

必须验证：

* 游戏恢复原语言。
* 不残留永久性中文覆盖。
* 不需要重新恢复原游戏文件。
* 存档仍可使用。

我们的目标不是：

“把原游戏文件永久替换成中文版。”

而是：

**一个可安装、可升级、可卸载的汉化 MOD。**

---

# 八、PoC 成功后立即扩大汉化范围

只有第一阶段端到端 PASS 后，再进入第二阶段。

第二阶段目标：

# 核心游玩内容汉化

优先顺序如下：

1. 主菜单 / 设置 / 常规按钮
2. 战斗 UI
3. 全职业
4. 全专精
5. 全技能
6. 技能说明
7. 装备相关文本
8. 天赋相关文本
9. 怪物/状态相关文本
10. 游戏关键提示
11. 弹窗
12. 其他玩家高频文本
13. 剧情 / lore / 边缘文本

如果当前版本暂时没有某些系统，不得自己虚构内容。

---

# 九、建立汉化术语表

从第一版开始就建立一个轻量 glossary。

例如记录：

源文：

`Projectile`

中文：

`投射物`

源文：

`Cooldown`

中文：

`冷却时间`

源文：

`Area`

中文根据语境可能为：

`范围`

不要让不同技能里随机出现：

“子弹 / 弹丸 / 投射体 / 投射物”

这种术语漂移。

术语表需要重点覆盖：

* Character
* Class
* Specialization
* Skill
* Talent
* Equipment
* Projectile
* Area
* Damage
* Critical
* Cooldown
* Duration
* Radius
* Speed
* Attack Speed
* Movement Speed
* Pierce
* Bounce
* Return
* Homing
* Range
* Buff
* Debuff
* Elite
* Boss

具体最终译法以游戏语境决定。

不要机械直译。

---

# 十、翻译风格

目标是：

**自然、简洁、像正式游戏汉化。**

优先：

意义准确

>

玩家容易理解

>

术语一致

>

逐字对应英文

不要做明显机器翻译风格。

例如技能说明应优先表达玩家实际会得到什么效果，而不是机械保留英语语序。

如果遇到原文本语义不确定：

先结合代码行为、技能参数或调用上下文判断。

不要仅凭英文单句猜。

如果仍无法确认：

标记：

`TRANSLATION_UNCERTAIN`

并保留证据。

不要无声猜测。

---

# 十一、动态变量保护

翻译时必须保护：

* `{xxx}`
* `%s`
* `%d`
* `%0.1f`
* format string
* BBCode
* Godot placeholder
* localization key
* resource path
* skill ID
* internal name

不要把程序变量翻译掉。

例如：

`Deals {damage}% damage`

可以翻译文本，但必须保留实际 placeholder 契约。

翻译完成后建立自动检查：

确保原文和译文 placeholder 集合一致。

任何 placeholder 丢失都必须视为构建失败。

---

# 十二、不要翻译内部标识符

不得为了汉化修改：

* class name
* script path
* signal name
* method name
* resource ID
* GUID / UID
* skill internal ID
* scene node path
* save key
* JSON key
* schema field
* asset path

只修改玩家可见文本。

特别注意：

`display_name`

可以翻译。

但：

`skill_id`

不可以翻译。

---

# 十三、存档兼容性

必须检查汉化方案是否可能影响：

* save ID
* skill ID
* class ID
* resource path
* dictionary key
* enum
* serialized property

汉化不得让英文显示名称变成存档的唯一标识。

如果发现原游戏错误地使用可见名称作为逻辑 ID：

先记录风险。

不要直接大规模重构。

选择最小、安全的兼容方案。

---

# 十四、MOD 目录结构

如果项目已有 MOD 目录规范：

严格遵守现有规范。

如果尚未固定，在不违反现有架构的情况下，将汉化保持为独立 MOD，例如逻辑上类似：

`mods/zh_CN/`

其内部可以包含：

* localization
* fonts
* resources
* manifest
* build files

但不要为了追求这个目录示例而破坏项目现有约定。

项目已有约定优先。

---

# 十五、构建可重复性

最终不能依赖：

“某个 AI 手工改了几个文件所以现在能跑。”

至少建立一个确定性的汉化构建过程。

目标是做到：

源翻译数据

↓

验证 placeholder

↓

生成/转换 Godot localization 资源

↓

打包中文 MOD

↓

输出构建产物

不要把大量翻译直接散落修改在 recovered `.gd` 里。

---

# 十六、机器检查

尽量增加低成本自动检查：

## 必须检查：

1. localization key 是否重复。
2. key 是否缺失。
3. placeholder 是否变化。
4. 空译文。
5. 非预期修改 internal ID。
6. 资源路径是否合法。
7. 中文文件编码正确。
8. 构建输出是否确定。
9. clean baseline 是否保持不变。

如果已有测试/验证框架，优先加入已有框架。

不要新造一整套庞大测试基础设施。

---

# 十七、翻译覆盖率

PoC 成功后建立可以机器计算的覆盖率。

至少记录：

* 总可翻译字符串数量
* 已翻译数量
* 未翻译数量
* uncertain 数量
* 当前覆盖率

最好能够按模块显示：

* UI
* Skills
* Classes
* Specializations
* Equipment
* Talents
* Misc

但是：

覆盖率工具不得阻塞第一版可玩汉化交付。

---

# 十八、证据要求

每次关键验证必须留下可复验信息。

至少保留：

* 使用的 Runtime hash
* 汉化 MOD build hash
* 使用的翻译源版本
* 构建日志
* placeholder 检查
* localization 检查
* clean baseline hash 检查
* 运行验证结果
* 安装测试
* 卸载测试

如果能够自动化截图或日志验证可以使用。

不允许只写：

“测试通过。”

必须说明：

测试了什么。

使用了什么版本。

实际观察到什么。

---

# 十九、禁止做的事情

本阶段禁止：

* 重新逆向整个游戏
* 重建 source map
* 大规模重构 recovered source
* 开发 Combat Modifier Framework
* 开发新技能
* 修改怪物数值
* 开发天赋系统
* 开发装备系统
* 修改地图
* 修改人物模型
* 为了“以后可能用到”安装大量工具
* 在汉化闭环未成功前追求全文本 100% 翻译

当前唯一业务优先级：

**用户尽快玩到稳定中文版本。**

---

# 二十、工作策略

按以下顺序执行：

### Phase 1

定位 localization 实际机制。

### Phase 2

确认中文字体方案。

### Phase 3

制作 5～10 条真实文本的最小 PoC。

### Phase 4

实际启动游戏验证。

### Phase 5

验证卸载恢复。

### Phase 6

扩大到“核心可玩汉化”。

### Phase 7

继续向全量汉化推进。

每个阶段如果已经获得足够证据：

直接进入下一阶段。

不要为了追求研究完整度停留。

---

# 二十一、遇到阻碍时

如果发现游戏没有正式 localization 系统：

不要停止任务。

继续寻找最小可维护方案，例如：

* UI text override
* Resource override
* 数据层 display text override
* MOD 注入的 translation table

但必须优先选择：

**集中式翻译映射**

而不是：

把几百个源码文件逐个硬改成中文。

如果遇到无法通过资源层解决的硬编码字符串：

可以建立最小的 runtime translation lookup，但范围只覆盖真正需要的硬编码文本。

不要借机重构整个 UI。

---

# 二十二、用户可玩版本的定义

你需要主动区分：

## 开发版本

用于测试单条字符串和功能。

## Core Chinese Build

第一版给用户实际玩的汉化版。

即使只有 60%～80% 的高频内容完成，只要：

主流程中文覆盖足够；

字体正常；

没有严重未翻译干扰；

安装/卸载安全；

运行稳定；

就可以先交付 Core Chinese Build。

剩余低频文本继续迭代。

不要为了追求统计意义上的 100%，长期不给用户可玩的版本。

---

# 二十三、最终交付

完成后必须明确告诉用户：

## 1. 汉化现在到了什么程度

例如：

* PoC
* Core Playable
* Near Complete
* Complete

不要只说：

“汉化完成。”

---

## 2. 已覆盖什么

给出实际模块。

---

## 3. 尚未覆盖什么

明确列出主要缺口。

---

## 4. 如何安装

给出最简单步骤。

---

## 5. 如何卸载

必须提供。

---

## 6. 汉化 MOD 文件在哪里

给出明确产物路径。

---

## 7. 使用哪个 Runtime

提供：

路径

*

SHA-256。

---

## 8. clean baseline 是否保持不变

给出验证结果。

---

## 9. 是否影响存档

给出实际测试结果，而不是推测。

---

## 10. 下一步

如果 Core Chinese Build 已经可以正常游玩：

默认下一阶段继续补齐汉化。

但不要自行转入技能 MOD 开发。

技能与 Combat Modifier 将作为之后单独任务执行。

---

# 二十四、最终成功标准

本任务最重要的成功标准不是：

“找到了所有字符串。”

也不是：

“写了一份完整汉化研究报告。”

而是用户最终能够做到：

原版游戏

↓

安装中文 MOD

↓

启动游戏

↓

实际看到中文菜单、职业、技能和战斗 UI

↓

正常游玩

↓

正常保存

↓

退出游戏

↓

卸载汉化

↓

游戏恢复原版

且：

`04_recovered` clean baseline 未被污染。

---

现在开始执行。

优先利用现有项目已经完成的 source map、schema 和 secondary development guide。

**不要重复已经完成的研究工作。**

在没有必要阻塞的问题时，自主推进，不要频繁要求用户确认。

遇到非关键翻译歧义时使用最佳判断并记录。

只有涉及：

* 破坏性操作
* 修改宿主系统
* 改变可信 baseline
* 无法回滚的游戏文件修改

时才停下并明确说明风险。

最终以一个**可以实际安装和游玩的中文版本**作为本阶段核心交付成果。
