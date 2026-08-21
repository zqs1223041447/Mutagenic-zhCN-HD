# AGENTS.md — Mutagenic AI 开发总治理

> 本文件是仓库最高级 AI 工作规则。2026-08-21 用户已明确批准：未来产品开发统一迁移到 Godot 4.7.1，Godot 3.5.3 仅作为只读历史参考，不再维持双轨产品开发。

## 1. 权威顺序

发生冲突时按以下顺序执行：

1. `AGENTS.md`：治理、权限、禁止事项。
2. `state/product_state.json`：当前产品阶段、Gate、下一批任务。
3. `docs/ai/master-plan/2026-08-21/00_README.md`：产品与迁移总计划。
4. `status.json`：Legacy/B3 历史机器状态与证据索引；不再决定新产品路线。
5. `releases/*.json`、`docs/ai/audits/**`、`10_logs/**`：历史证据。

任何 Markdown 摘要不得反向覆盖机器状态或历史证据。

## 2. 唯一产品引擎

- **唯一活动产品引擎：Godot 4.7.1 stable。**
- Godot 3.5.3、GDRE/PCK v1、现有 declarative MOD 构建链从本决议起归类为 **Legacy Reference**。
- Legacy 允许：只读分析、行为/数值/资源参考、历史证据复验、必要的迁移对照。
- Legacy 禁止：新增产品功能、继续扩建玩法、继续投资长期 CI/Build/Release 能力。
- 新代码、新场景、新资源、新测试应进入 Godot 4.7.1 Product 结构；不得把 `04_recovered` 当作未来产品源码目录直接改写。
- 迁移策略是一次性主线迁移 + 垂直切片恢复可玩性，不维持两套活动 Gameplay。

## 3. 不可变与历史资产

- `00_original/`：版权/私有原版资产，不得提交，不得修改原件。
- `03_raw/`：提取来源快照，byte-preserving，只读。
- `04_recovered/`：恢复源码参考快照，byte-preserving，只读。
- 历史 B1/B2/B3、Localization、P7、release/evidence 记录不得因新路线而伪造、重写结论或删除。
- `3B6427B3...` 等旧候选/基线只表示 Legacy 事实，不构成 Godot 4 产品基线。

## 4. 0 人工代码政策

目标是 **0 人工代码操作**：

- AI 负责写代码、配置、测试、文档、资源流水线、构建、故障定位、修复、冲突解决、worktree、分支与集成。
- 人类只负责产品方向、凭据/私有资产、真正主观且无法机器化的偏好判断，以及公开发布授权。
- 普通测试失败、编译失败、冲突、格式问题、CI 红灯不得转嫁给用户手修。
- Public Release 默认仍需用户显式批准；开发基线可在未来单独建立自动晋升 Gate，但不得等同公开发布。

## 5. Git 与并行 Agent

固定中央集成分支：

`agent/kinetic-arcane-remaster-foundation`

规则：

- 主工作区保持一个主 clone；并行任务由 AI 创建/回收 worktree。
- Worker 使用 `agent/<batch>-<task>-<slug>` 分支，不直接推中央集成线。
- Coordinator 负责收集、审计、解决冲突、集成并推送中央分支。
- 禁止 `git add .`、`git add -A`、`git add --all`；只允许精确路径 staging。
- commit、PR、push 状态说明使用中文。
- 每次中央集成 push 必须同步：当前状态、已证明/未证明、风险、下一批本地 AI 开发计划。
- 不提交宿主机绝对路径；使用 repo-relative、环境变量或逻辑占位 `<repo_root>` / `<archive_root>`。

## 6. Product 目录与迁移边界

目标产品目录为 `product/`。在 P1 迁移建立前，不得假定目录已经存在。

建议边界：

- `product/project.godot`：Godot 4.7.1 产品工程。
- `product/src/`：产品运行时代码。
- `product/content/`：数据驱动内容。
- `product/assets/`：可发布产品资产。
- `product/tests/`：产品测试。
- `migration/`：一次性转换脚本、映射、迁移报告；迁移完成后可归档。

迁移不得直接覆盖 `03_raw/04_recovered`。

## 7. 产品目标不可被迁移简化掉

必须保留并继续深化：

- 主动技能、Dash、永久角色、Class + Specialization。
- Passive/Mutation Tree 的既有内容语义；Specialization 独立，不再新增重复第三棵大树。
- Active Skill + Support 架构，不改成 POE 装备插槽体系。
- Equipment 与 Gene 分离；Jewel 作为后续插件层候选。
- Rare 偏数值上限，Legendary 偏规则改变/Build Anchor。
- Campaign + Map Item + Map Mods + Atlas 双层终局。
- Halls of Torment 参考的是暗黑复古视觉、怪潮密度、战斗呈现与死亡/VFX 节奏，不改成 Survivor 自动攻击游戏。
- POE/PoEDB 只参考机制结构；禁止复制受保护资产、文本、名称和数值表。

## 8. 数据与合规

- 不默认批量抓取 pathofexile.com 或 PoEDB。
- 优先使用仓库已有 `data/poedb/` 快照、用户提供/授权的数据、官方公开 API/导出。
- 外部机制必须经过“参考事实 → 抽象机制 → Mutagenic 原创实现”。
- 不提交秘密、token、密钥、私有 EXE、未经许可二进制资产。

## 9. 工具策略

P0/P1 只引入能直接缩短迁移时间的工具：

- Godot 4.7.1 stable：必需。
- Python >=3.11、Git：必需。
- Godot MCP：在 Product 工程可以启动后接入，作为编辑/检查/运行适配器；CLI/测试仍是事实来源。
- Stagehand：第一可玩 Product baseline 形成后再接正式 runtime 回归。
- Blender 5.2 LTS：视觉资产规模化阶段再成为正式流水线；Blender MCP 仅可选。
- LimboAI、DuckDB/Parquet、复杂数据库状态中心：没有明确瓶颈前不引入。

## 10. Gate 驱动路线

产品路线只按 Gate 推进，不按日历强推：

`P0 仓库收口 → P1 Godot 4.7.1 迁移 → P2 最小 AI 自治闭环 → P3 原游戏功能回归 → P4 Halls 风格改造 → P5 POE-like Build/装备/怪物/地图 → P6 Atlas/Endgame → 持续内容扩张`

当前阶段与下一批任务只读 `state/product_state.json`。

## 11. 测试与失败处理

- 所有变更先跑最便宜的 schema/static/unit，再进入 headless/runtime/visual/perf。
- 迁移初期先建立事实清单与兼容性错误列表，不凭记忆盲改。
- AI 必须记录“已证明 / 未证明”；不能把 BLOCKED、NOT_RUN、推断写成 PASS。
- CI 红灯属于 AI 待修任务，除凭据/私有资产/主观产品决策外不得要求用户处理。

## 12. AI 启动入口

新会话固定读取：

1. `AGENTS.md`
2. `state/product_state.json`
3. `docs/ai/AI_ENTRYPOINT.md`
4. `docs/ai/master-plan/2026-08-21/00_README.md`
5. 当前任务对应文件

Fresh Clone 使用 `docs/dev-environment/QUICKSTART_FRESH_CLONE.md`，必须显式 clone 固定集成分支。