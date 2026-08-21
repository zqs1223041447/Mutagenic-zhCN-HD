# 当前状态与已批准决议

## 远端起点

治理切换前固定集成分支 HEAD：`641d944e8aa175d3de89183ca554e81a2cff1a51`。

当时已确认：PR #1 仍是 Draft/Mergeable，但正文停留在旧 B3-P3/3127D394；最新 CI 因两个 release manifest 的宿主绝对 `archive_locator` 失败；Fresh Clone 没有显式 checkout 固定集成分支。

## 已批准决议

- 取消 Godot 3.5.3 / Godot 4.7.1 双活开发。
- Godot 4.7.1 成为唯一 Product 主线。
- Legacy B3 成果作为迁移参考而不是未来开发平台。
- 复杂 State DB、Stagehand 全面接管、Blender MCP、LimboAI、数据湖等全部后置到出现明确需求。
- Roadmap 改为 Gate 驱动。

## 不被裁掉的能力

现有 53 Skills、60 Supports、326 Passive、88 Keystone、149 Stats、24 Skill Tags、4 Classes/8 Specializations 等是迁移保持对象，不因换引擎重新设计清零。

`status.json` 和历史 release/evidence 继续保存 Legacy 事实。