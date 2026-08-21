# AGENTS.md — 兼容入口

部分 Agent、CLI 或 IDE 会自动寻找 `AGENTS.md`，因此保留本文件。

**唯一完整根执行协议是 `AGENT.MD`。**

本项目本地 Agent 角色：
- **gork**：主 AGENT（Coordinator），负责安排工作
- **AGY**：优先 Worker（gemini cli）
- **opencode**：备用 Worker（额度不足时切换）
- **gpt**：外部专家，疑难杂症时由 gork 调用会诊

开始工作前：

1. 读取 `AGENT.MD`
2. 读取 `state/product_state.json`
3. 按 `AGENT.MD` 的 GOAL 循环和权威顺序执行

本文件不得扩展成第二套治理规则。
