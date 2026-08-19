# B1-X0 — Portability / Batch Automation C0 远端预审计

> **Task**：B1-X0
> **基线**：`batch/b1-anchor` → `c864480d8908630d602c17f4949b96b65d19b275`
> **状态**：REMOTE C0 COMPLETE；batchctl/scanner 实现待执行 Agent。

## 1. 已确认的正向基础

最新主线的 `scripts/bootstrap_deploy.py` 已采用：

- `ROOT = Path(__file__).resolve().parents[1]`；
- `ROOT / "00_original/..."`、`ROOT / "03_raw"`、`ROOT / "04_recovered"` 等 repo-relative 默认；
- CLI `Path` 参数可覆盖外部位置。

这符合当前 clone-root 治理，不应被 X0 重写成另一套路径框架。

## 2. Scanner 必须正确分类的绝对路径

### A. Production hardcode — 应阻断

Git 中生产 `.py/.ps1/.bat/.cmd/.json/.yaml/.yml/.toml/.gd/.tscn/.tres` 如果把某台机器的盘符、用户名、UNC 当作运行默认值或逻辑依赖，应 FAIL。

### B. Historical provenance metadata — 保留/允许但报告

`manifests/recovered_clean_manifest.json` 顶层 `source` 当前保存历史恢复来源，例如旧机器上的 `F:\...` 路径。

这属于 provenance 证据，不是运行路径。Scanner 不得为了“零绝对路径”破坏历史证据；应分类为 `provenance_metadata`，默认 WARN/INFO，不作为 production hardcode。

同理，历史 evidence/manifest 中记录当时运行机绝对路径，如果该字段明确是 evidence 而不是运行配置，应保留。

### C. Docs/example — 允许但报告

`docs/DEPLOYMENT.md` 包含类似：

`Copy-Item "C:\path\to\Mutagenic.exe" ...`

这是显式示例占位符，不是代码默认值。Scanner 应分类 `docs_example`，不能误判为 production FAIL。

### D. Local ignored config/log — 不入 Git 或不作为 Source of Truth

用户机器真实 `MUTAGENIC_*_ROOT`、VM 路径、archive 路径、工具路径允许存在于本地忽略配置/日志中，但不得反向写回生产脚本默认值。

## 3. Batch controller 已知反例

旧 Kinetic forensic 快照中的 `scripts/batch-monitor/batch_monitor.ps1` 曾把多个执行 Agent 全部用同一个主 `RepoRoot` 作为 `--dir` 启动。

该实现没有迁入新基线。

X0 新实现必须：

1. `claim B1-Xn` 自动定位/创建 task branch；
2. 自动创建独立 Git worktree；
3. 返回/记录 task worktree 路径；
4. 启动 Agent 时 `--dir` 指向**对应 task worktree**；
5. 不让两个任务共享可写 working tree；
6. cleanup 对未合并、未知或有脏改动的 worktree fail-closed。

## 4. 推荐 scanner 结果模型

每条命中至少输出：

- file
- line / json path（能力允许）
- matched value（敏感值需脱敏）
- classification：`production_hardcode | provenance_metadata | local_config | test_fixture | docs_example | false_positive`
- severity：`FAIL | WARN | INFO`
- remediation

CI/Preflight 默认只因 `production_hardcode` FAIL。

## 5. 人类 UX

目标仍是一条命令一个意图：

- `batchctl claim B1-X1`
- `batchctl status B1`
- `batchctl handoff B1-X1`
- `batchctl collect B1`
- `batchctl preflight B1`

用户不应手工输入 worktree 绝对路径。

## 6. 接手后的第一验收

X0 Agent 首先对当前 repo 跑 scanner：

- bootstrap_deploy.py 的 repo-relative 路径不应 FAIL；
- recovered manifest 的历史 `source` 不应被自动删除/改写；
- docs 中 `C:\path\to` 示例不应 FAIL；
- 构造一个 production hardcode fixture 必须 FAIL；
- secret scanner 不能打印 secret 正文。
