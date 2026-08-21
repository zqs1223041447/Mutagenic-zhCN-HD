# GitHub / Worktree 工作流

固定集成分支：`agent/kinetic-arcane-remaster-foundation`。

主 clone 唯一；Worker worktree 位于仓库外 `<WORKSPACE_ROOT>/worktrees/`，由 AI 管理。

Worker 分支：`agent/<batch>-<task>-<slug>`。

流程：Coordinator 分配 → Worker claim → 实现/测试 → handoff → Coordinator 审计 → merge-tree/冲突处理 → 集成测试 → 中央 push → PR/状态/下一批同步。

禁止：

- Worker 直接更新中央分支。
- `git add .` / `git add -A` / `git add --all`。
- tracked 文件写入真实宿主绝对路径。
- 在同一 worktree 混入未确认的无关改动。

中央 push 的中文说明必须包括：现状、完成项、证据、风险/未证明、下一批本地 AI 计划、远端 SHA 核验。