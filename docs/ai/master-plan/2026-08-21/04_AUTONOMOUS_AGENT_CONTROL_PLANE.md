# 最小 AI 自治控制面

保留现有 `batchctl.py`，渐进升级，不先重写成大型调度平台。

P1/P2 只要求：

- Task DAG / claim / status / handoff。
- worktree 生命周期。
- heartbeat + stall detection。
- retry/backoff。
- 资源 lease：Godot editor/runtime/import/build、Blender 等重资源默认单并发。
- Coordinator integration queue。
- 重启后可从状态文件恢复任务。

状态优先 JSON；只有当任务规模证明 JSON 成为瓶颈时再引入 SQLite/数据库。

OpenCode/其他本地 Agent 通过命令行启动并输出结构化 handoff。MCP 是工具适配器，不是控制平面事实源。