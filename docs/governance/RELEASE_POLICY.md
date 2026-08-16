# 发布策略（RELEASE_POLICY）

> 定义 build/candidate/verified/accepted/baseline 状态机与发布记录格式。

## 状态机

```
BUILD → CANDIDATE → VERIFIED → ACCEPTED → BASELINE
```
- **CANDIDATE**：构建成功（fresh embed），未经完整验证。
- **VERIFIED**：通过 roundtrip + boot + semantic 机器验证。
- **ACCEPTED**：人工显式确认（SHA 绑定）。
- **BASELINE**：ACCEPTED 后由人工显式晋升为可信基线。**绝不自动晋升。**

## 每个 build 的唯一 Build ID

格式：`YYYYMMDD-HHMMSS-<hash8>`（如 `20260816-112430-4f93c1a`）。
构建 manifest（build/manifest.json）必须记录：
```
git_commit, game_fingerprint, schema_hash, toolchain_hash,
modset_hash, original_exe_hash, candidate_exe_hash,
encryption_key_id (只记 id), build_time, build_host
```

## Release 记录（releases/<id>.json）

```json
{
  "release_id": "zhCN-v8.1",
  "git_commit": "...",
  "game_fingerprint": "C7B5D5A5...",
  "modset_lock_hash": "...",
  "tools_lock_hash": "...",
  "candidate_exe_sha256": "...",
  "evidence_id": "...",
  "archive_locator": "G:\\Mutageni-Archive\\releases\\zhcn-v8.1\\",
  "status": "accepted"
}
```

## 发布包（handoff zip）

- 最终发布包 = 金标准 release artifact（如 `Mutagenic_zhCN_MOD_Handoff_20260816.zip`）。
- 记录 SHA256 + archive locator；**不进 Git**（.gitignore *.zip）。
- 至少保留主 archive + backup 两份副本。
