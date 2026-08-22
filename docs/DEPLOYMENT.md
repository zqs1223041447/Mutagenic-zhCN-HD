# 仓库布局与私资产

当前主线是 **Godot 4.7.1 Product**（`product/` 尚未建立）。本页只说明 clone 后磁盘上有什么、哪些不能进 Git。启动协议是 `AGENT.MD`，不是本文件。

环境检查：`docs/dev-environment/QUICKSTART_FRESH_CLONE.md`。

---

## 目录（以本 clone 磁盘为准）

| 路径 | 内容 | Git |
|---|---|---|
| `00_original/` | 自备原版 `Mutagenic.exe` | 不入库 |
| `02_tools/gdre/` | GDRE | 不入库 |
| `03_raw/` | 提取物 3744 路径，不可变 | 入库，byte-preserving |
| `04_recovered/` | 3.5.3 恢复源码，不可变 | 入库，byte-preserving |
| `05_translation/` | 汉化切片数据 | 入库 |
| `mods/` | Legacy 声明式 MOD | 入库 |
| `scripts/` | 旧管线 + bootstrap | 入库 |
| `docs/` | 对照/证据/工具说明 | 入库 |
| `state/product_state.json` | 当前机器状态 | 入库 |
| `status.json` / `releases/` | Legacy 批次证据 | 入库 |
| `10_logs/` | 运行证据 | 不入库 |
| `.cache/` | 本地缓存 | 不入库 |

本 clone **没有** `01_baseline/`、`05_schema/`、`06_worktree/`–`09_output/`、`product/`、`migration/`。

`.gitattributes` 对 `03_raw/**`、`04_recovered/**` 强制 `-text -eol`，避免 checkout 破坏 preimage。

---

## 原版 EXE

放到 `00_original/Mutagenic.exe`。指纹：

`C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209`（103,290,320 字节）

脚本加密密钥只存在 `manifests/script_key.txt`（gitignore），禁止写入报告或 tracked 文件。

私资产注入：`MUTAGENIC_DEVKIT_ROOT` / `MUTAGENIC_ORIGINAL_EXE` / `MUTAGENIC_SCRIPT_KEY_FILE`。见 QUICKSTART。

---

## 不要用本页去做的事

- 不要按旧「canonical pipeline」给 3.5.3 加新玩法。
- 不要编辑 `04_recovered` 当生产输入。
- 不要把 `status.json` 当 Product Gate。
