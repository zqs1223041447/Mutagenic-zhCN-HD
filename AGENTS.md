# AGENTS.md — Mutagenic 工程治理协议（唯一全局规范）

> **Authority**: 本文件是仓库的**唯一全局规范**（L0）。所有 AI 开始工作前必须读它。
> **Scope**: 只写全局硬规则。Hyper-V/VM 操作、NL2MOD 实现、汉化切片详情、GDRE 手册等全部下放到对应子文档，不在此重复。
> **Supersedes**: `AGENTS1.md`（旧版，已重构为本文件）。冲突以本文件为准。

---

## 1. Mission

从原版游戏 EXE 出发，经确定性管线产出可验证的汉化/MOD 构建，保持可复现、可回滚、证据可追溯。

```
pristine game → fingerprint → raw extraction → recovered source → schema
  → declarative MOD → resolve/apply/compile/pack → fresh embed
  → candidate → roundtrip/boot/semantic verify → evidence
  → human-only promote → baseline
```

**VM 定位**：VM 是部署/运行/观察/语义验证的执行环境，**不是**构建系统。canonical build 由宿主固定管线生成。
**NL2MOD 定位**：NL2MOD 是"自然语言 → 声明式 MOD"的前端，**不得**复制第二套构建逻辑。

---

## 2. 资产分类（判断一切文件该不该进 Git / 能不能删）

| 类别 | 含义 | 进 Git | 可删除性 |
|---|---|---|---|
| Source of Truth | 规则、脚本、MOD 声明、人工数据 | ✅ | 只能经 Git 变更 |
| Immutable Provenance | 原版、提取物、恢复源码 | ❌ | 永不删除 |
| Generated | worktree/compiled/pack/candidate | ❌ | 可重新生成，可清理 |
| Evidence | manifest/验证报告/日志/截图 | manifest✅ 大证据❌ | 按等级归档 |
| Local Environment | venv/GDRE/密钥/VM/node_modules | ❌ | 可重建 |

---

## 3. 非协商不可变规则

1. **`00_original` 神圣不可变**：原版 EXE 只能读取；每次构建从它**新鲜嵌入**，绝不在历史 modded EXE 上叠加。
2. **`03_raw` 提取校验后不可变**：3744 路径，`manifests/raw_manifest.json` 绑定。
3. **`04_recovered` 恢复后不可变**：5058 文件，`manifests/recovered_clean_manifest.json` 绑定；只读参考，禁止重建/修改。
4. **Generated 目录**（06_worktree/07_compiled/08_pack/build/*）可随时重建，不算资产。
5. **失败构建是 forensic artifact**：保留证据但不作为生产输入。

---

## 4. 状态权威（Truth Matrix）

| 问题 | 唯一答案来源 |
|---|---|
| 哪些行为禁止？ | **AGENTS.md**（本文件） |
| 当前版本/状态？ | **`status.json`**（唯一机器权威源） |
| 人类可读当前状态？ | `PROJECT_STATE.md`（**从 status.json 生成**，不人工维护） |
| 原版指纹/提取/恢复清单？ | `manifests/provenance/*` |
| 哪些 MOD 构成版本？ | `modset.lock.json`（待建） |
| 如何构建？ | canonical pipeline（scripts/pipeline + docs/architecture/PIPELINE.md） |
| 如何跑游戏/验证？ | VM workflow（docs/dev-environment + Hyper-V skill） |
| 哪个版本是 baseline？ | release registry（status.json + releases/*.json） |

> 规则：一个问题的答案只有一个权威源。任何文档与 status.json 冲突时，以 status.json 为准。

---

## 5. 硬性禁止（违反即污染）

1. **禁止访问宿主 F: 盘**（永久；代码层所有路径解析对 `F:` hard-fail）。
2. **禁止修改** `00_original/`、`03_raw/`、`04_recovered/`。
3. **禁止**全局文本替换 `.gd/.tscn/.tres/.json`（必须结构化 patcher，精确字段定位 + preimage 守卫）。
4. **禁止**批量重编译所有恢复脚本（只编译 manifest 声明的）。
5. **禁止**把 `06_worktree/` 手工编辑当生产输入（探索性编辑必须转声明式 patch）。
6. **禁止**忽略 PCK checksum 失败；**禁止**把"进程存活"当成功。
7. **禁止**泄露脚本加密密钥（`manifests/script_key.txt` 本地，不入库/日志/报告）。
8. **禁止**把候选 EXE 自动晋升 baseline（必须人工显式批准）。

---

## 6. 构建与验证最低要求

- **声明式 MOD**：所有改动必须是 `mods/<id>/mod.json`（CODE_PATCH/VALUE_PATCH/RESOURCE_PATCH/ASSET_PATCH/TEXT_PATCH），带 preimage_sha256 + expected_occurrences。
- **canonical pipeline**（唯一构建路径）：resolve → apply → compile → pack → **fresh embed**（从 00_original）→ candidate。
- **每个 build 有唯一 Build ID**（`YYYYMMDD-HHMMSS-<hash>`），产出 manifest 记录：git_commit/game_fingerprint/schema_hash/toolchain_hash/modset_hash/original_exe_hash/candidate_exe_hash/**encryption_key_id**（只记 id 不记 key）/build_time/host。
- **验证分层**：
  - S0 结构（roundtrip 3744/3744、delta 精确、PCK checksum）
  - S1 boot（真实窗口/进程 + 无 ALERT + 无 fatal）
  - S2 core smoke / S3 persistence / S4 mod-specific / S5 visual（按需）
  - **语义确认**：GDRE 从最终 EXE 恢复目标 .gde，确认新值已嵌入（权威，不靠 UI）。
- 每个 Gate 必须有证据文件（verified_at/command/artifact）；PASS 注明"证明什么/不证明什么"。

---

## 7. 证据保留策略

- **E0 Provenance**（指纹/提取/恢复 manifest）：永久保留。
- **E1 Accepted Release Evidence**（accepted build 的 roundtrip/boot/semantic/acceptance）：永久保留。
- **E2 Development Evidence**（中间 build/P7 实验/历史验证）：归档到 cold archive（`G:\Mutageni-Archive\evidence\`），不留在活动工作区。
- **E3 Ephemeral**（NL2MOD 临时 smoke/失败中间产物/重复 candidate）：允许 TTL 清理（保留 manifest + 索引后）。

> 规则：不得不可逆丢失具有 provenance 或 accepted-release 价值的证据。E2/E3 在产生完整 manifest + SHA256 + archive index 后可移出活动工作区。

---

## 8. Git 规则

- **仓库只含**：规则、脚本、MOD 声明、manifest、人工数据、schema contracts。**不含**：游戏二进制（00_original/03_raw/04_recovered/EXE/DLL/PCK）、venv、node_modules、10_logs、build 产物、archive。
- `.gitignore` 必须覆盖上述排除项；提交前跑 secret scan（key/credential/.env 检测）。
- **分支策略：trunk-based**。长期只有 `main`；工作分支按任务 `mod/xxx`、`feat/xxx`、`fix/xxx`，合完即删。
- **里程碑用 git tag**（`zhcn-v8.1`、`pipeline-v1`、`nl2mod-v1`），不用长期分支。
- 初始提交分次进行（governance → pipeline → mods → vm → nl2mod → release），禁止 `git add .` 一锅端。

---

## 9. 路径与可移植性

- 所有脚本路径**相对 repo root**（用 `git rev-parse --show-toplevel` 或脚本位置定位），**禁止硬编码 `G:\`**。
- F: 禁令在代码层实现（路径解析 hard-fail），并有静态扫描检查。
- 行尾：`.md/.json/.yaml/.py/.gd` 用 LF，`.ps1/.bat/.cmd` 用 CRLF（`.gitattributes` 约束）。

---

## 10. AI 工作入口

新任务开始固定读取：
1. `AGENTS.md`（本文件）
2. `status.json`
3. `docs/ai/AI_ENTRYPOINT.md`（任务路由）
4. 任务对应 workflow 文档（docs/workflows/）

任务路由（详情见 AI_ENTRYPOINT）：
- 汉化请求 → `mods/localization` → canonical build
- 自定义 MOD → 手工 mod.json 或 NL2MOD → canonical build
- Runtime bug → canonical candidate → VM verification
- 管线 bug → scripts/pipeline；VM/工具链 bug → scripts/vm

---

## 11. AI 自动化铁律

1. 远程 VM 命令**永远显式 -Credential**（dev 账户）；`New-PSSession -VMName` 忘传凭证会触发 guest 服务崩溃。
2. 回滚/删除类命令**一律 -Confirm:$false**，否则确认框挂死自动化。
3. 脚本内禁用 `Enter-PSSession`（交互式挂死）；长任务输出重定向到文件防缓冲阻塞。
4. 等待就绪用轮询（State=Running + Heartbeat OK + 实际命令探测），不裸 sleep。
5. 关键步骤 `-ErrorAction Stop` + try/catch + 失败日志落盘。

---

*权威层级：AGENTS.md（L0）> status.json（L1 机器状态）> 子文档（L2）。SKILL.md 是执行适配层，不是政策制定者；不得复制一套新规则。*
