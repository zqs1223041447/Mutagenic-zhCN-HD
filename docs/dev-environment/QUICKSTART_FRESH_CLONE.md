# Fresh Clone 快速开始 — 最小闭环

> ![Portable Dev Closure](https://img.shields.io/badge/Portable%20Dev%20Closure-%E6%BF%80%E6%B4%BB%202026--08--21-0ea5e9?style=for-the-badge&labelColor=0f172a) &nbsp; ![Readiness](https://img.shields.io/badge/Readiness-DEV__ENV__READY-10b981?style=flat-square) &nbsp; `manifests/dev_environment_requirements.json`

> **适用对象**：全新机器 / 全新 clone / AI 新会话。**目标**：用最少命令验证环境是否就绪，不重复阅读 20 页手册。
> **原则**：仓库内路径全部从 `repo_root` 推导，无硬编码盘符；仓库外私资产通过环境变量注入，`.env` 永不入库。

---

## 30 秒跑通 — 复制即用

在任意目录执行（脚本自动 `git rev-parse` 定位仓库根，无需手动 `cd` 到特定盘符）：

```powershell
git clone https://github.com/zqs1223041447/Mutagenic-zhCN-HD
cd Mutagenic-zhCN-HD
python scripts/bootstrap/bootstrap_dev_env.py
python scripts/bootstrap/dev_doctor.py
# 看到 overall: DEV_ENV_READY 即就绪；看到 BLOCKED_BY_PRIVATE_ASSET 见下一节（预期行为，非报错）
```

| 步骤 | 作用 | 预期耗时 |
|---|---|---|
| `bootstrap_dev_env.py` | 预检仓库 + 创建 `.cache/` + 按优先级还原私资产 + 打印 readiness | < 10s |
| `dev_doctor.py` | 只读复检（等价 `bootstrap --check-only`），不写文件 | < 5s |

> **AI 用法**：两条命令可在任意子目录运行；`--json -` 可输出机器可读报告，`--verbose` 展开 provider 细节。

---

## 你会看到什么 — 两种正常结果

### 情况 A · 没有私资产（大多数全新机器，预期）

全新 clone 默认**没有**版权/密钥，`bootstrap` 会以 `exit 0` 结束，但报告：

```
overall: BLOCKED_BY_PRIVATE_ASSET
BLOCKED_BY_PRIVATE_ASSET: original_exe, script_key
```

| 资产 | 位置 | 状态 | 说明 |
|---|---|---|---|
| `original_exe` | `00_original/Mutagenic.exe` | `BLOCKED_BY_PRIVATE_ASSET` | 需自有正版 EXE，SHA `C7B5D5A5…2451209` / 103,290,320 B |
| `script_key` | `manifests/script_key.txt` | `BLOCKED_BY_PRIVATE_ASSET` | 64 hex AES 密钥，仅存指纹，不落明文 |
| `gdre` | `02_tools/gdre/gdre_tools.exe` | `WARN` | 可下载工具，未阻塞；可稍后补齐 |

> **这不是失败。** Fresh clone 的 `BLOCKED` 是设计行为——证明 fail-closed 生效。此时 `LEVEL_0_REPO_READY = PASS`（Git + `03_raw` 3744 + `04_recovered` 5058 已就绪），可直接做只读审计；构建/打包需进入情况 B。

### 情况 B · 已配置私资产

配置任一 provider 后重跑 `bootstrap`：

```powershell
# 方式 1 — 推荐：指向已导出的 DevKit 目录（一次性配置）
$env:MUTAGENIC_DEVKIT_ROOT = "D:\mutagenic_devkit"
python scripts/bootstrap/bootstrap_dev_env.py

# 方式 2 — 逐项指向
$env:MUTAGENIC_ORIGINAL_EXE   = "D:\assets\Mutagenic.exe"
$env:MUTAGENIC_SCRIPT_KEY_FILE = "D:\assets\script_key.txt"
python scripts/bootstrap/bootstrap_dev_env.py
```

| 环境 | 达成的 Readiness | 可做事项 |
|---|---|---|
| 仅修复 `original_exe` + `script_key` + `gdre` | `LEVEL_1_BUILD_READY` ✅ | `resolve → apply → compile → pack → fresh embed → candidate` 全链构建 |
| 再满足 `python ≥3.11` + `cache` 可写 | `LEVEL_2_RUNTIME_READY` ✅ | 本地启动 `probe_boot.py` / 存档验证 |
| 再通过 `abs_path_scan` + `secret_scan` | `LEVEL_3_FULL_VALIDATION_READY` ✅ | 提交前 Gate / 中央集成 / Promotion |

`dev_doctor.py` 此时应显示 `overall: DEV_ENV_READY`。

---

## Readiness Levels — 一览表

| Level | 含义 | 关键判定 | 典型用途 |
|---|---|---|---|
| `LEVEL_0_REPO_READY` | 仓库就绪 | `git` 正常 + `AGENTS.md` + `status.json` 可解析 + `03_raw`/`04_recovered` 存在 | 源码审计、preimage 核对、文档工作 |
| `LEVEL_1_BUILD_READY` | 构建就绪 | L0 + `original_exe` SHA/size 正确 + `script_key` 64hex + `gdre` 存在 + `python≥3.11` | 生成 candidate，全链路验证 S0 |
| `LEVEL_2_RUNTIME_READY` | 运行就绪 | L1 + `.cache` 可写 + `scripts/build` 存在 | 本地 boot / S1-S4 / 持久化实验 |
| `LEVEL_3_FULL_VALIDATION_READY` | 完整验证就绪 | L2 + `abs_path_scan PASS` + `secret_scan PASS` | PR Gate / 发布 / baseline 晋升 |

> 诊断细节：`python scripts/bootstrap/bootstrap_dev_env.py --json -` 或 `dev_doctor.py --json` 输出 `levels` + `reasons` 字段。

---

## 私资产 Provider 优先级

脚本按固定顺序尝试，命中即停，绝不猜测/联网下载版权资产。

**`original_exe` — `00_original/Mutagenic.exe`**

| 优先级 | Provider | 来源 |
|---|---|---|
| 1 | `existing_correct_sha` | 仓库内已存在且 SHA/size 正确 |
| 2 | `MUTAGENIC_DEVKIT_ROOT/00_original/Mutagenic.exe` | DevKit 目录（亦兼容扁平 `DevKit/Mutagenic.exe`） |
| 3 | `MUTAGENIC_ORIGINAL_EXE` | 直接指向自有正版文件 |
| 4 | `BLOCKED_BY_PRIVATE_ASSET` | 提示 `SHA C7B5D5… / 103290320` + 修复指引 |

**`script_key` — `manifests/script_key.txt`**

| 优先级 | Provider | 来源 |
|---|---|---|
| 1 | `existing` | 仓库内已存在且为 64 hex 合法 |
| 2 | `MUTAGENIC_SCRIPT_KEY` | 环境变量内联 64 hex（最不推荐，易泄露） |
| 3 | `MUTAGENIC_SCRIPT_KEY_FILE` | 指向含 64 hex 的文件 |
| 4 | `MUTAGENIC_DEVKIT_ROOT/manifests/script_key.txt` | DevKit 目录（兼容扁平 `DevKit/script_key.txt`） |
| 5 | `BLOCKED_BY_PRIVATE_ASSET` | 提示三种 Env 方式 |

`gdre` 为可下载工具：`existing` → `MUTAGENIC_TOOL_ROOT` → `MUTAGENIC_DEVKIT_ROOT` → `manual_download`，缺失仅 `WARN`。

---

## DevKit 导出与复用

在**已拥有私资产的源机器**上一次性导出：

```powershell
python scripts/bootstrap/export_private_devkit.py --out D:\mutagenic_devkit
# 产出：D:\mutagenic_devkit/00_original/Mutagenic.exe
#       D:\mutagenic_devkit/manifests/script_key.txt
#       D:\mutagenic_devkit/02_tools/gdre/gdre_tools.exe  (可选)
```

在**新机器**上复用：

```powershell
$env:MUTAGENIC_DEVKIT_ROOT = "D:\mutagenic_devkit"
python scripts/bootstrap/bootstrap_dev_env.py   # 自动还原到 00_original/ 与 manifests/
```

> DevKit 目录本身**永不入库**（已在 `.gitignore`：`.private_devkit/` `.devkit/` `*.devkit.zip`），仅作本地中转。

---

## `.env` 与 `.cache` 规则

| 项 | 规则 |
|---|---|
| `.env` | 永不入库（`.gitignore` 已屏蔽 `.env` / `.env.*`）。模板见 `.env.example`；本地通过 `MUTAGENIC_*` 环境变量或 `.env` 注入，禁止把真实 key/绝对路径写入任何 tracked 文件 |
| `.cache/` | 默认 `<repo_root>/.cache/`（含 `gdre/` `pack_stage/` `base_index/` `build_profile.json`），可经 `MUTAGENIC_CACHE_ROOT` 覆盖；已 `.gitignore`，可随时删除重建 |
| 密钥指纹 | 日志/报告仅记录 `sha256 fingerprint`，绝不打印 `script_key` 明文 |

---

## 下一步

- **已达 `DEV_ENV_READY`** → 按 `docs/ai/AI_ENTRYPOINT.md` 路由进入 Xi 任务（Kinetic / 本地化 / 并行批次）。
- **仍为 `BLOCKED`** → 完成 DevKit 配置后重跑本页 4 条命令即可。
- **需要更深手册** → 详见 `docs/dev-environment/README.md`（人类 VM 说明书）、`docs/dev-environment/VM_DEVELOPMENT.md`（VM 开发线）、`docs/build/COMPILE_PERFORMANCE_PLAN.md`（构建性能双模式）。

> 本页控制在 1–2 页打印范围；重复细节以链接收敛，不在此展开。
