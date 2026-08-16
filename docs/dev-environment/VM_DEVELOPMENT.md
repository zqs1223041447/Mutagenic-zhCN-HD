# Mutageni VM 开发线 — 项目级规则文件

> **状态**：ACTIVE（2026-08-16 更新）
> **角色**：VM 开发线的权威规则。回答"最终目标、当前状态、下一步、每一步怎么做、如何验收、如何回滚"。
> **配套**：操作手册（`hyperv-mutageni-vm` skill，怎么做）+ 人类说明书（`docs/dev-environment/README.md`，你怎么办）。
> **权威**：冲突时以 `AGENTS.md` 为最高契约；本文件是 VM 线的操作化解读。

---

## 1. 最终目标

**用户通过隔离 VM 便捷地调试游戏功能、开发各种自定义 MOD。**

具体 = 一条可重复的闭环：
```
自然语言描述（如"骷髅射手移速+20%"）
  → AI 定位修改点（source-map/schema/04_recovered）
  → 生成声明式 MOD（nlmod.py）
  → 一键构建（build_mod.py）→ 候选 EXE
  → 部署到 VM → 启动（Mesa 软渲染）→ 语义/日志/视觉验证
  → 回滚或晋升
```

**Non-goals**：不追求 VM 内 GPU 性能基准；目标是 functional MOD 验证。视觉正确性最终以人眼为准。

---

## 2. 当前状态（2026-08-16 已核实）

### 2.1 环境事实（机器可核对）

| 项 | 值 | 证据 |
|---|---|---|
| VM | `Mutageni-Dev` Gen2, 4 vCPU, Mem Min=4GB/Startup=8GB/Max=16GB | `Get-VM` |
| VHDX | `G:\VMs\Mutageni-Dev\...\Mutageni-Dev.vhdx`（当前挂 checkpoint 链 → 实际 .avhdx） | Phase0 基线 |
| Guest | Win10 Enterprise Eval 19045（**90 天评估，注意到期**） | quser/registry |
| 网络 | Default Switch NAT，IP 会漂移（现 `172.24.251.128`）；**用 PowerShell Direct 不依赖 IP** | Phase0 |
| 账户 | `dev/REDACTED`（远程可用）；`ZZZ` 无密码（远程不可用，VMConnect 桌面用户） | skill |
| 工具链 | venv Python 3.11.15 + pycryptodome/fonttools/frida + GDRE 2.6.4 + VC++ redist | `02_tools/venv` |
| 项目 | VM `C:\dev\Mutageni`（04_recovered 5058/5058 PASS）；宿主 `G:\opencode-Mutageni` 只读参考 | phase33 |
| 渲染 | **Mesa LLVMpipe 软渲染已生效**：`opengl32.dll`+`libgallium_wgl.dll` 放游戏目录，Godot 日志 `Renderer: llvmpipe`，游戏在 VM 桌面正常显示 | A1 验证 |

### 2.2 能力状态

| 能力 | 状态 | 说明 |
|---|---|---|
| 远程执行/文件传输/checkpoint | ✅ | PS Direct + Copy-VMFile，见 skill |
| 游戏在 VM 内可视化运行 | ✅ | Mesa 软渲染（几 FPS，够开发验证 UI/文本/场景） |
| MOD 构建→候选 EXE | ✅ | NL2MOD 流水线（resolve/apply/compile/pack/embed 全 PASS） |
| MOD 应用到游戏+验证 | ✅ | 部署 VM 启动 + GDRE 语义确认（movement_speed 78.0 已验证） |
| GPU 硬件加速 | ⚠️ | 无直通；GPU-PV 是实验项（见 §5 Track A2） |

### 2.3 Checkpoint（恢复点）

| 名称 | 时间 | 内容 |
|---|---|---|
| `00-clean-os` | 08-15 | Windows 基础 |
| `01-dev-toolchain` | 08-15 | 工具链就绪 |
| `02-mutageni-baseline` | 08-15 | 项目迁移 + 5058 + smoke |
| （建议）`03-pre-mod` | 待建 | 每次有风险 MOD 构建前打点 |

---

## 3. 文件记录（VM 线素材清单）

| 位置 | 内容 |
|---|---|
| `docs/dev-environment/README.md` | 人类操作说明书（你） |
| `.opencode/skills/hyperv-mutageni-vm/SKILL.md` | AI 操作手册（怎么做） |
| `docs/ai/nl2mod-guide.md` | NL2MOD 框架使用指南（本文件的实现） |
| `docs/ai/source-map.md` / `scene-resource-map.md` | 修改点定位地图 |
| `05_schema/game_schema.json` | 实体/字段注册表 |
| `scripts/nlmod/nlmod.py` + `build_mod.py` | NL2MOD 生成器 + 流水线 |
| `mods/mm-monster-speed-skeleton-archer/` | NL2MOD 验证案例 |
| `G:\VMs\Mutageni-Dev\` | VM 配置 + phase1~52 历史脚本/日志（一次性搭建残留，仅审计用） |
| `G:\VMs\Mutageni-Dev\mesa\` | Mesa MinGW 包（软渲染 DLL 源） |
| VM `C:\dev\Mutageni\` | 实际开发工作区（只在此写） |

---

## 4. 开发设计（架构）

### 4.1 分层

```
宿主 AI（opencode）：规划/文档/决策/VM 生命周期管理/自然语言解析
   │  PowerShell Direct / Copy-VMFile / Copy-Item -FromSession
   ▼
VM（guest）：构建执行/脚本运行/游戏启动（Mesa 软渲染）
   │
   ▼
视觉验证：VM 桌面（VMConnect，用户或计划任务拉起）+ 宿主（最终游玩）
```

### 4.2 Source of Truth

- **代码真相**：宿主 `G:\opencode-Mutageni`（含 `04_recovered` 纯净源码 + mods + scripts）是**不可变源**。
- **工作区**：VM `C:\dev\Mutageni` 是**执行副本**（可重建，不做唯一真相）。
- 防漂移：修改一律在宿主声明 MOD → 构建产物部署 VM；VM 内不手工编辑源码。

### 4.3 数据流

```
意图(natural language) → mods/<id>/mod.json (宿主)
→ build_mod.py → normalized.pck (宿主 10_logs)
→ embed → 候选 EXE → Copy-VMFile 部署 VM
→ 计划任务(zzz 交互) 启动 → godot.log / GDRE 语义确认
```

### 4.4 Decision Log（已定决策，勿重新研究）

| ID | 决策 | 理由 |
|---|---|---|
| D001 | DDA 直通**排除** | 需 Server 宿主 + 独占 GPU，与"宿主+VM 同时工作"冲突 |
| D002 | **Mesa LLVMpipe 软渲染为第一 unblock 路径** | 已验证：Godot GLES2 在 VM 内正常显示；几 FPS 够功能验证 |
| D003 | GPU-PV（Easy-GPU-PV）为**实验项** | 微软官方 Win10 Pro 不支持；OpenGL 可能不工作；设止损线 |
| D004 | 远程通道**首选 PowerShell Direct** | 不依赖 NAT IP 漂移/guest WinRM 状态 |
| D005 | VM 内 GUI 启动用**计划任务 /ru zzz /it** | 远程会话无法拉起可见窗口；zzz 在 console 交互会话 |

---

## 5. 分阶段路线图（下一步）

### 阶段 A（已完成）：VM 可视化 + 远程通道
- ✅ Mesa 软渲染：游戏在 VM 桌面正常显示（llvmpipe）
- ✅ NL2MOD 端到端：自然语言 → 候选 EXE → 应用验证（movement_speed 65→78）

### 阶段 B（当前/下一步）：
1. **NL2MOD 意图模板库**：把常见修改沉淀为 intent 模板（数值比例、技能、怪物、投射物）
2. **一键全链**：build_mod.py 补 embed + GDRE 语义确认（当前停在 normalized.pck）
3. **自动部署+视觉验证**：集成 VM 部署 + 交互会话启动 + 截图（zzz 会话截图）
4. **回滚自动化**：每次 MOD 构建前自动 `Checkpoint-VM 03-pre-mod`

### 阶段 C（可选实验）：GPU-PV
- 止损线：能枚举 partitionable GPU → guest 驱动加载 → 最小 OpenGL context；任一失败即停止
- 若 Win10 GPU-PV 失败：不无限投入，软渲染已够开发验证

### 阶段 D（环境寿命，重要）
- Guest 是 **90 天 Enterprise Eval**（到期需处理：重装/换密钥/换 Win11）
- Win10 22H2 已停止常规支持 → 中长期评估宿主/guest 迁 Win11 匹配 build

---

## 6. 每步验收标准（DoD）

| 步骤 | 通过标准 |
|---|---|
| 自然语言→intent | old_text 在 04_recovered 中唯一（count==expected），new_text 数值正确 |
| mod.json 生成 | nlmod.py exit 0，preimage_sha256 == 目标文件整文件哈希 |
| 一键构建 | resolve/apply/compile/pack/pck-create/normalize 全 PASS，输出 normalized.pck |
| embed | 候选 EXE 含 GDPC 魔数，size ~103MB |
| 语义确认 | **GDRE 从最终 EXE 恢复目标 .gde，新值已嵌入**（权威，不靠 UI） |
| VM 部署启动 | 进程存活 responding，无 ALERT/GLAD 错误，日志含 llvmpipe |
| 视觉确认 | 用户（或 zzz 会话截图）确认 UI/文本/效果符合预期 |

---

## 7. 硬规则（关键安全不变量，SKILL 中同样可见）

1. **禁止访问宿主 F: 盘**（唯一历史例外已删除的 QEMU 目录，不再涉及）
2. **`00_original` / `03_raw` / `04_recovered` 不可变**（只读输入；worktree 是副本）
3. **不覆盖已存在 manifest/构建输出**（脚本 fail-closed）
4. **每次从 00_original 新鲜嵌入**（不在历史 modded EXE 上叠加）
5. **候选不自动晋升 baseline**（需用户批准）
6. **破坏性 VM 操作前必须有 rollback path**（Checkpoint 03-pre-mod 或 VM export）
7. **密钥 `manifests/script_key.txt` 不入报告/日志**

---

## 8. 下一步（单一、明确）

**当前唯一下一步**：扩充 NL2MOD 意图模板库（阶段 B1）——选 2-3 个常见 MOD 类型（如"技能伤害比例调整""怪物血量修改""投射物数量修改"）各做一个端到端验证案例，沉淀为可复用的 intent 模板，使框架覆盖最常见的"改数值"需求。

完成后：把 embed+语义确认并入 build_mod.py（B2），再做自动部署+截图（B3）。
