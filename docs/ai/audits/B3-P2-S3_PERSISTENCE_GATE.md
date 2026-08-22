# B3-P2-X2 S3 Persistence Gate — 运行手册

> 任务：B3-P2-X2（S3 Persistence Regression Automation）
> 基线：`60f9232ca8d802de1016f3e3d46778bbc5b79a7d`（B3-P1 集成完成）
> 分支/worktree：`agent/b3-p2-x2` @ `<repo_root>.worktrees/B3/P2-X2`
> 候选：`10_logs/b2-i1-aggregate-20260820/candidate/Mutagenic.exe`
> 证据：`docs/ai/audits/B3-P2-S3_EVIDENCE.json`（入库）+ `10_logs/b3-p2-x2-s3-persistence-20260820/`（不入库）
> 审计级别：C0 静态 + 真实运行（本门禁对候选 EXE 显式执行 save→exit→reload）

---

## 1. 目标

以无人值守方式回答 S3 门禁问题：**游戏跨 退出 → 重新载入 边界后，自己写出的存档是否与退出前同态？**

S3 定义（AGENTS.md §6 验证分层）：状态持久化 —— 存档写入 → 进程退出 → 重新启动 → 重新载入，状态一致。

本任务把 B3-P1-X1 人工辅助的 S2 bisect 沉淀成可复跑的门禁，并真实跑通一次。

## 2. 门禁语义契约

门禁不比较种子和结果（种子是启动输入，游戏会归一化），而是比较**游戏自己写出的两个存档**：

```
seed 存档 ──(run1 启动)──▶ run1 加载 + 磁盘重写 ──(WM_CLOSE 退出)──▶ run1 退出态
                                                                           │
                                          语义指纹比较（0 差异 = S3 PASS）│
                                                                           ▼
     ──(run2 同 profile 冷启动)──▶ run2 加载 + 磁盘重写 ──(WM_CLOSE 退出)──▶ run2 退出态
```

失败即如实 FAIL / BLOCKED，不伪装 PASS。

## 3. 语义指纹（sane-state 判定）

对存档 JSON 做 canonicalize（key 递归排序）后 sha256。**剔除三项每档必变 volatile 字段**：

| 字段 | 为什么豁免 |
|---|---|
| `timestamp` | 每次 save 重算（GameState.do_save_game 写当前时间） |
| `checksum` | 每次 save 重算（内容校验和） |
| `stamp` | 每次 save 重算（防篡改戳） |

其余全部顶层字段参与指纹：`save_version / settings / shared_stash / keybind_overrides / characters / completed_achievements`。

关键判定点（全部命中才算 PASS）：

| 判定 | 含义 |
|---|---|
| `run1_exit_vs_run2_diffs == []` | run1 退出态存档 == run2 重载后存档（semantic_sha 相等） |
| `planted_marker_run2.ok` | 种子埋入的 character `default`（needs_starter=false）跨进程存活 |
| `rewritten_twice` | run1 与 run2 都发生了真实磁盘重写（不是读缓存） |
| `run2_load_marker` | run2 日志出现 `LOADED AND MERGED`（真的走了 load_game→merge） |
| `exit_stable` | 进程退出后磁碟快照 == settle 快照（防"仅内存假象"） |
| 无 fatal 标记 / 无 `No save file found` | 无加载失败 |

## 4. 工具

| 文件 | 作用 |
|---|---|
| `scripts/validate/s3_persistence_gate.py` | 门禁执行器（真实运行，退出码 0/1/2/3） |
| `scripts/validate/s3_persistence_selftests.py` | 离线自检 17/17（不启动游戏，快速回归） |
| `tests/s3_persistence/run_selfchecks.py` | 自检包装（repo 内任意目录可启动） |
| `scripts/validate/make_harness_seed_save.py` | 种子存档生成器（B3-X0 沉淀，复用） |

全脚本可移植：无仓库外绝对路径硬编码，candidate/apdata/seed/out 全部 CLI 注入（见 `--help`）。

## 5. 运行方法

### 5.1 离线自检（秒级回归，不启动游戏）

```powershell
python scripts/validate/s3_persistence_selftests.py
# 期望: 17/17 PASS, exit 0
```

### 5.2 全套回归（含本门禁注册）

```powershell
python scripts/ai/check_all.py
# 期望: 12/12 PASS（含 s3_persistence_selfcheck）
```

### 5.3 真实门禁运行（候选 → 证据）

对任意候选执行（路径来自本地配置/10_logs，不入库）：

```powershell
python scripts\validate\s3_persistence_gate.py `
  --candidate <候选 EXE> `
  --apdata    <隔离 APPDATA 目录（可自动创建）> `
  --seed-save <harness seed 存档> `
  --out       <证据输出目录> `
  --experiment-id <本次实验 ID>
```

先跑 `make_harness_seed_save.py --out <seed路径>` 生成种子，再运行门禁。

### 5.4 Promotion 候选重跑（软性强制）

`docs/ai/audits/B3-P2-S3_EVIDENCE.json` 的 not_proven 已声明：**晋升候选（promote 的对象）在晋升前必须重跑门禁并归档新证据**。这是 AGENTS.md §5.9（禁止自动晋升）与 §6（PASS 注明证明什么/不证明什么）的自然延伸——本批次的 PASS 属于当前候选，不自动转嫁到晋升后的新 EXE。

## 6. 首批真实运行结果（什么是 PASS）

- **候选**：Mutagenic.exe sha `4ad1de3844...`（b2-i1 aggregate, 103,341,700 B）
- **run1**：window@1.77s → load@9.77s（load_marker 触发）→ rewrite#1@9.77s（1431612b, 2170B）→ settled@21.8s → wm_close exit 0
- **run2**：window@1.77s → load@9.77s（LOADED AND MERGED 复现）→ rewrite#1@9.77s（5512e32b, 2170B）→ settled@21.78s → wm_close exit 0
- **比较**：semantic_sha 双轮均为 `a7ca81b86c...`，diff 路径 0 条；raw_sha 不同（volatile 三字段漂移，被语义指纹正确豁免）
- **markers**：character `default`（WARRIOR）存在，needs_starter=false，starter 弹窗未阻塞
- **status: PASS**

## 7. 现状与剩余风险

| 风险 | 状态 |
|---|---|
| 本地存档分支已验证；**Steam 云分支未验证**（USE_STEAM=false 本地分支） | not_proven，单独验证 |
| 游戏内 gameplay 产生的状态（局内 orbs/genes/stage）未注入输入 | 不属本门禁范围 |
| 视觉/UI 未验证 | 属 S5 |
| 每次 run 仅 1 次磁盘重写（加载期 rewrite），12s settle 内无 debounce 重写 | 满足"真实落盘"底线；加长 settle 可覆盖 debounce 路径 |
| make_harness_seed_save.py 打印的内存 sha 与落盘 CRLF sha 不一致 | 已按磁盘字节记录；下次维护修打印 |
| **promotion 候选需重跑本门禁** | 见 §5.4 |

## 8. 交接要点

- 交付文件（入库）：`scripts/validate/s3_persistence_gate.py`、`scripts/validate/s3_persistence_selftests.py`、`tests/s3_persistence/run_selfchecks.py`、`scripts/ai/check_all_components.json`（新增组件）、`docs/ai/audits/B3-P2-S3_EVIDENCE.json`、本手册
- 大证据（不入库，10_logs）：`b3-p2-x2-s3-persistence-20260820/`（evidence json + run1/run2 log tail + seed + 心跳）
- 失败重试记录：首跑两处运行时 bug（poll_log UnboundLocalError、心跳关闭文件 ValueError）已修复并重跑通过；种子 hash 打印差异为生成器报告偏差（CRLF），非门禁问题
- 潜在冲突路径：本任务仅新增工具脚本与检查注册，未触碰 `03_raw/04_recovered`，无 preimage 漂移面
- 推荐集成顺序：随 B3-P2 批次正常集成；promotion 后按 §5.4 重跑并替换 evidence 中的 candidate 字段