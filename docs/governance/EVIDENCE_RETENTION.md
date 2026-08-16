# 证据保留策略（EVIDENCE_RETENTION）

> 依据 AGENTS.md §7。定义证据分级、保留期限、归档流程。

## 分级

| 级别 | 含义 | 保留 | 位置 |
|---|---|---|---|
| **E0 Provenance** | 原版指纹、提取 manifest、恢复 manifest | 永久 | 活动区 `manifests/provenance/` |
| **E1 Accepted Release** | accepted build 的 roundtrip/boot/semantic/acceptance | 永久 | `releases/<id>/evidence/` + archive |
| **E2 Development** | 中间 build、P7 实验、历史验证 | 归档 | `G:\Mutageni-Archive\evidence\` |
| **E3 Ephemeral** | 临时 smoke、失败中间产物、重复 candidate | TTL 清理 | 产生后归档索引，可删 |

## 归档流程（E2/E3 → Archive）

1. 产生完整 manifest（记录 path/size/sha256/classification）。
2. 写入 archive index（`G:\Mutageni-Archive\index.json` 或 `manifests/evidence-index/`）。
3. 移动到 `G:\Mutageni-Archive\evidence\<category>\`。
4. 活动工作区保留索引指针，删除实体。

## 活动工作区保持规则

- `10_logs/` 只保留：`README.md`、`evidence-index.json`、`current/`（当前 build 证据）。
- 历史 C5/P7/nl2mod 证据 → 归档。
- 任何归档操作前先确认目标已在 manifest + index 中。

## 禁止

- 不可逆删除 E0/E1 证据。
- 在无 manifest/index 的情况下移动或删除证据。
- 把归档证据当作活动构建输入。
