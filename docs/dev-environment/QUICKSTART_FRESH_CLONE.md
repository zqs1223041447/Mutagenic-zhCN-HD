# Fresh Clone — bootstrap / doctor

当前入口是 `AGENT.MD`，不是本页。本页只验证本机私资产和工具是否齐。

`LEVEL_3` 的 abs-path / secret 闭合 **不阻塞** Product 迁移。Godot 4.7.1 是 DOWNLOADABLE_TOOL：

```powershell
python scripts/bootstrap/fetch_godot.py
python scripts/bootstrap/product_toolchain.py --sanitize
python scripts/bootstrap/bootstrap_dev_env.py
python scripts/bootstrap/dev_doctor.py
```

可在仓库任意子目录运行。`--json -` 出机器可读报告。也可用 `scripts/bootstrap/bootstrap.ps1` / `doctor.ps1`。

---

## 两种正常结果

**没有私资产**（全新 clone 预期）：`overall: BLOCKED_BY_PRIVATE_ASSET`（`original_exe`, `script_key`）。这不是失败。此时仍可只读审计 `03_raw/` / `04_recovered/`。

**已配置私资产**：应到 `DEV_ENV_READY`。

| 资产 | 位置 | 说明 |
|---|---|---|
| `original_exe` | `00_original/Mutagenic.exe` | SHA `C7B5D5A5…2451209` / 103,290,320 B |
| `script_key` | `manifests/script_key.txt` | 64 hex，不入库 |
| `gdre` | `02_tools/gdre/gdre_tools.exe` | 可后补，缺失通常只 WARN |

```powershell
$env:MUTAGENIC_DEVKIT_ROOT = "D:\mutagenic_devkit"
python scripts/bootstrap/bootstrap_dev_env.py
```

或：`MUTAGENIC_ORIGINAL_EXE`、`MUTAGENIC_SCRIPT_KEY_FILE`。

源机器导出 DevKit：

```powershell
python scripts/bootstrap/export_private_devkit.py --out D:\mutagenic_devkit
```

DevKit 目录永不入库。

---

## Readiness

| Level | 含义 | 与 P1 的关系 |
|---|---|---|
| `LEVEL_0_REPO_READY` | Git + `03_raw` + `04_recovered` | 足够做源码扫描 / P1-X1 / P1-X3 |
| `LEVEL_1_BUILD_READY` | L0 + EXE + key + GDRE + Python | Legacy candidate 构建；**不等于** Godot 4 Product Ready |
| `LEVEL_2_RUNTIME_READY` | L1 + cache | Legacy boot / 持久化实验 |
| `LEVEL_3_FULL_VALIDATION_READY` | L2 + abs-path + secret | 与 P1 并行补齐，不挡 Product Seed |

判定以 doctor JSON 为准，不要把 `AGENTS.md` + `status.json` 可解析当成 L0 的定义。

`.env` 永不入库。日志只记密钥 fingerprint，不打明文。
