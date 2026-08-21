> **Authority**: L2 构建性能权威（AGENTS.md §6.1 渐进式披露的完整规范）。
> **必读时机**：凡任务涉及 `compile / pack / PCK / embed / normalize / verify / 构建耗时` 或改动 `scripts/build/*.py`，AI 必须先读本文件全文再执行编译行为，不得仅凭 AGENTS.md §6.1 摘要猜测实现细节。
> **渐进式披露**：AGENTS.md 仅保留全局硬规则与双模式默认行为，本文件承载 20 章完整执行方案、验收标准与集成顺序；工作时按需深入对应章节，不把全文回填 AGENTS.md。
> **双模式**：日常迭代 = `FAST DEV BUILD`（`--mode fast`，`NOT PROMOTION ELIGIBLE`），晋升/发布 = `CANONICAL RELEASE BUILD`（`--mode release`，fresh + 3744/3744 + S0-S4 全量）。
> **底线**：不可为提速削弱 RELEASE 验证链；`00_original/03_raw/04_recovered` 不可变；禁止 hardlink、旧 EXE 叠加、跳过 preimage、抽样冒充全量、硬编码绝对路径。

---

# Mutagenic 编译性能优化执行方案

你是 `Mutagenic-zhCN-HD` 项目的主控 Coordinator。

目标不是削弱验证流程，而是：

> **显著缩短日常开发 Build 时间，同时保持 Promotion / Release 的完整 fail-closed 验证链。**

项目仓库：

```text
https://github.com/zqs1223041447/Mutagenic-zhCN-HD
```

协调分支：

```text
agent/kinetic-arcane-remaster-foundation
```

---

# 0. 总原则

必须建立两条构建路径：

```text
FAST DEV BUILD
```

用于日常 Agent 开发和快速迭代。

以及：

```text
CANONICAL RELEASE BUILD
```

用于：

- 中央集成；
- Promotion Candidate；
- baseline；
- 正式 PR Gate；
- 最终证据。

**禁止为了提速削弱最终 Canonical Release 验证。**

不可违反：

```text
00_original/**
03_raw/**
04_recovered/**
```

不可修改。

禁止：

```text
hardlink 03_raw → 可写 pack tree
```

因为后续覆盖文件可能污染不可变 `03_raw`。

禁止：

- 在旧 modded EXE 上叠加；
- 跳过 preimage 校验；
- 关闭最终完整 S0；
- 用抽样结果冒充完整 Promotion Gate；
- 写死本机绝对路径。

---

# 1. 优化前先建立真实性能基线

这是第一优先级。

修改构建工具，使每个阶段记录：

```text
wall_time_ms
cpu_time_ms
input_count
output_count
bytes_read
bytes_written
cache_hits
cache_misses
gdre_invocations
workers
```

至少覆盖：

```text
resolve
apply
compile
pack_tree
pck_create
normalize_md5
embed
verify
roundtrip
```

输出统一：

```text
10_logs/<build-id>/timing.json
```

以及：

```text
10_logs/<build-id>/build.json
```

必须能够回答：

```text
整个 Build 最慢的三步是什么？
compile 占多少？
pack 占多少？
PCK create 占多少？
verify 占多少？
```

没有数据前不要继续猜瓶颈。

验收：

```text
同一个 Promotion modset 连续 Build 3 次
每一步均有 duration
```

---

# 2. P1：Persistent Compile Cache

这是最高 ROI 优化。

当前：

```text
scripts/build/compile_declared_scripts.py
```

已经支持：

```text
--cache
```

但需要正式升级成可靠持久缓存。

默认缓存目录：

```text
<repo_root>/.cache/gdre/
```

加入 `.gitignore`。

允许用户通过：

```text
MUTAGENIC_CACHE_ROOT
```

覆盖。

禁止硬编码宿主路径。

## Cache Key

不能只用：

```text
sha256(source)
```

推荐：

```text
cache_key = SHA256(
    relative_script_path
    + source_sha256
    + gdre_exe_sha256
    + bytecode_version
    + compile_tool_version
    + encryption_key_fingerprint
)
```

其中：

```text
encryption_key_fingerprint
```

只能记录：

```text
SHA256(key)
```

或其短 fingerprint。

禁止保存真实 key。

---

## Cache 验收

第一次：

```text
10 unique .gd
cache_hits=0
```

第二次完全不改：

```text
cache_hits=10
gdre_invocations=0
```

修改 1 个 `.gd`：

```text
cache_hits=9
cache_misses=1
gdre_invocations≈1
```

必须验证缓存产物和无缓存产物：

```text
.gde byte-identical
```

---

# 3. P1：GDRE Worker 本机自动调优

不要简单把：

```text
workers=4
```

改成：

```text
workers=8
```

慢电脑很可能因为：

```text
CPU contention
RAM pressure
SSD contention
```

反而更慢。

加入 benchmark：

```text
workers=1
workers=2
workers=4
workers=6
workers=8
```

对于同一批 compile workload 各跑至少 2 次。

选择：

```text
最低 median wall_time
```

结果写入：

```text
.cache/build_profile.json
```

例如：

```json
{
  "gdre_workers": 3
}
```

默认行为：

```text
CLI --workers
>
build_profile
>
safe default
```

用户明确指定 `--workers` 时必须优先。

---

# 4. P1：Build Queue

项目允许多 Agent 并行开发，但慢电脑禁止多个 Agent 同时启动大量重型编译。

默认：

```text
Coding Agents = 并行

Heavy Build Queue = 1

Runtime / VM Queue = 1
```

即：

```text
X1 coding ─┐
X2 coding ─┤
X3 coding ─┤
X4 coding ─┘
            ↓
        BUILD SLOT
            ↓
        VERIFY SLOT
```

主控必须实现：

```text
build semaphore
```

同一时刻默认只允许：

```text
1 个 heavy canonical build
```

可通过配置调整。

不能出现：

```text
4 Agent
×
4 GDRE workers
=
16 GDRE 同时抢机器
```

---

# 5. P1：Toolchain Attestation Cache

现在 pristine roundtrip 会重复证明相同工具链。

建立：

```text
toolchain_fingerprint
```

推荐：

```text
SHA256(
    gdre_tools.exe
    + compile_declared_scripts.py
    + compile_encrypt_scripts.py
    + BYTECODE
    + encryption_key_fingerprint
)
```

若该 fingerprint 已存在一次完整：

```text
roundtrip PASS
```

则日常 FAST DEV Build 可以写：

```text
TOOLCHAIN_ATTESTATION_REUSED
```

不用再次编译全部 pristine test scripts。

以下任一变化必须重新跑完整 roundtrip：

```text
GDRE exe changed
BYTECODE changed
compiler code changed
encryption implementation changed
script key changed
```

Promotion / Release Build 仍可根据治理要求重新 full-run。

---

# 6. P1：Immutable Base Hash Index

当前：

```text
build_declared_pack.py
```

最终会为整个 pack tree 的 3744 个文件重新计算 SHA256。

但：

```text
03_raw
```

是 immutable。

所以建立：

```text
.cache/base_index/
```

缓存：

```text
03_raw fingerprint
→
所有 base 文件：
path
size
sha256
```

未修改的 pack entry：

```text
直接复用 base index
```

只有：

```text
manifest changed files
generated .gde
generated .remap
asset overlays
```

重新 hash。

最终 report 仍必须包含完整：

```text
3744 entries
```

只是避免实际重新读取全部文件。

---

# 7. P2：Collision-Safe GDRE Batching

当前按照：

```text
rel.parent
```

分组。

10 个 GDScript 可能产生：

```text
8 GDRE processes
```

主要成本可能是 GDRE 冷启动。

目标：

```text
8 invocations
→
1~3 invocations
```

但不能简单把所有文件输出到同一个目录。

原因：

```text
Scenes/A/Stats.gd
Scenes/B/Stats.gd
```

都可能生成：

```text
Stats.gdc
```

导致覆盖。

---

## 正确方案

构建：

```text
collision graph
```

按：

```text
filename stem
```

检测冲突。

将没有 basename 冲突的文件组成一个 batch。

例如：

```text
Batch 1:
Player.gd
Mob.gd
GenericSkill.gd
Projectile.gd

Batch 2:
Stats.gd
...
```

每个 Batch：

```text
一次 GDRE invocation
```

产物生成后再移动回：

```text
out/<relative_parent>/
```

---

## 验收

对 B3 Promotion 10 `.gd`：

当前：

```text
8 invocations
```

目标：

```text
≤3
```

并且新旧编译结果：

```text
所有 .gde byte-identical
所有 .remap byte-identical
```

任何不一致立即 fallback 到旧目录分组方式。

---

# 8. P2：Persistent Mutable Pack Staging

当前：

```text
shutil.copytree(03_raw, out)
```

每次复制完整：

```text
3744 files
```

不要使用 hardlink。

改成：

```text
persistent mutable staging
```

例如：

```text
.cache/pack_stage/
```

首次：

```text
03_raw
→ full physical copy
→ pack_stage
```

以后：

保存：

```text
previous_changed_paths
```

新 Build：

```text
touched =
previous_changed_paths
∪
current_changed_paths
```

对于 touched：

```text
如果原始文件存在：
从 03_raw 恢复

如果是上次生成的新文件：
删除
```

然后只应用当前：

```text
.gde
.remap
resource patches
asset overlays
```

---

## 必须存在 clean fallback

提供：

```text
--clean-pack-stage
```

或：

```text
--fresh
```

强制：

```text
删除 staging
→ 从 03_raw 完整重建
```

Canonical Release 默认允许选择：

```text
fresh
```

确保最终证据链不依赖历史 staging。

---

# 9. FAST DEV 与 RELEASE 双模式

正式加入：

```text
--mode fast
```

和：

```text
--mode release
```

---

## FAST DEV

允许：

```text
persistent compile cache
toolchain attestation reuse
base hash index reuse
persistent pack staging
collision-safe batching
quick structural checks
```

目标：

```text
日常改 1~2 个 .gd 时尽可能秒级/几十秒级
```

FAST DEV 结果必须明确：

```text
NOT PROMOTION ELIGIBLE
```

---

## RELEASE

必须：

```text
fresh resolve
fresh apply
compile with validated cache or clean compile
fresh pack tree
full PCK creation
full normalize
fresh embed from 00_original
3744/3744 verify
required roundtrip/attestation
S0/S1/S2/S3/S4
```

Promotion Candidate 必须使用：

```text
--mode release
```

---

# 10. normalize_pck_md5 不要直接增量化

当前 normalize 是 fail-closed：

```text
扫描所有 PCK entries
重新计算 MD5
只允许已知 zero-byte defect
```

这个 Gate 安全价值很高。

不要直接改成：

```text
只检查 changed entries
```

FAST DEV 可以未来增加：

```text
quick normalize
```

但：

```text
Release / Promotion
```

必须继续：

```text
full normalize
```

---

# 11. verify_exe_structure 同样保留完整 Release Gate

日常 FAST DEV 可以减少重复验证。

但：

```text
Promotion Candidate
```

必须：

```text
3744/3744
bad_entries=[]
```

不可降低。

---

# 12. 实验项：GDRE --pck-patch

P1/P2 完成后，如果仍然慢，再创建实验任务。

研究：

```text
GDRE --pck-patch
```

以及：

```text
--patch-file
```

是否可以直接：

```text
00_original/Mutagenic.exe
+
49 changed resources
↓
Candidate
```

从而绕过：

```text
full pack tree copy
full pck-create
separate embed
```

---

## 只能实验，不立即进入 canonical

生成两个 Candidate：

```text
A = 当前 canonical pipeline
B = pck-patch pipeline
```

必须比较：

```text
extract entry count
entry paths
entry bytes
PCK structure
S0
S1
S3
S4
```

如果：

```text
A/B semantic + structural equivalence PASS
```

才能考虑作为：

```text
FAST BUILDER
```

之后再决定是否升级成 canonical。

---

# 13. 旧编译链防误用

当前旧：

```text
scripts/compile_encrypt_scripts.py
```

存在：

```text
rglob("*.gd")
```

全量扫描路径。

加入明确保护：

```text
LEGACY_FULL_COMPILE
```

或者需要显式参数：

```text
--allow-full-recompile
```

否则普通 AI 不允许调用。

文档标明：

```text
canonical gameplay mod build
必须使用 compile_declared_scripts.py
```

防止误操作重新编译数千脚本。

---

# 14. 编译性能报告

每次 FAST Build 打印：

```text
Build mode: FAST

resolve:        0.3s
apply:          0.8s
compile:        4.1s
cache:          9/10
GDRE calls:     1
pack staging:   0.5s
pck:            3.2s
verify quick:   0.8s

TOTAL:          9.7s
```

Release：

```text
Build mode: RELEASE

resolve:
apply:
compile:
pack:
pck:
normalize:
embed:
verify:

TOTAL:
```

同时输出相对上次：

```text
previous_total
current_total
improvement_percent
```

---

# 15. 性能验收标准

至少使用以下场景 benchmark。

### Case A — Cold Build

删除：

```text
.cache
```

然后 Promotion modset Build。

记录：

```text
TOTAL
compile
pack
pck
```

---

### Case B — No Change Rebuild

不改任何源码再次构建。

目标：

```text
compile cache hit = 100%
gdre_invocations = 0
```

---

### Case C — One Script Changed

只改变一个测试 `.gd`。

目标：

```text
cache hit = N-1
GDRE invocations <=1
```

---

### Case D — Promotion Release Build

完整：

```text
--mode release
```

必须保持：

```text
S0 PASS
结构完整
最终结果与优化前语义等价
```

---

# 16. 最终性能目标

不要提前承诺具体百分比。

以真实 benchmark 为准。

建议目标：

```text
No-change build：
GDRE invocation → 0
```

```text
单脚本迭代：
GDRE invocation → 1
```

```text
B3 Promotion 10 scripts：
Cold build GDRE invocation
8 → ≤3
```

```text
Pack filesystem writes：
3744 → touched files only
```

同时：

```text
Release Gate 质量不得下降
```

---

# 17. 多 Agent 拆分方式

如果支持多 Agent，建议并行拆成：

```text
BUILD-X0
Timing + benchmark framework

BUILD-X1
Persistent compile cache + cache key

BUILD-X2
Worker autotune + Build Queue

BUILD-X3
Toolchain attestation + base hash index
```

以上四项可以并行。

第一波集成 PASS 后，再启动：

```text
BUILD-X4
Collision-safe GDRE batching

BUILD-X5
Persistent mutable pack staging

BUILD-X6
FAST/RELEASE build modes
```

最后：

```text
BUILD-X7
pck-patch experimental prototype
```

X7 不进入 canonical，除非 equivalence gate PASS。

---

# 18. 集成顺序

推荐：

```text
X0 timing
↓
X1 cache
+
X2 worker/build queue
+
X3 attestation/index
↓
I1 benchmark
↓
X4 batching
+
X5 staging
↓
I2 benchmark
↓
X6 FAST/RELEASE
↓
Release regression
↓
X7 experimental pck-patch
```

每一步都必须给：

```text
before duration
after duration
speedup
functional diff
check_all
abs_path_scan
secret_scan
```

---

# 19. 停止条件

如果某优化：

```text
速度提升 < 5%
```

且显著增加复杂度：

不进入 canonical。

如果：

```text
任何 .gde 不一致
任何 PCK entry 不一致
任何 immutable source 被改变
任何 S0/S1/S3/S4 回归
```

立即 rollback。

---

# 20. 最终交付

完成后必须输出：

```yaml
baseline:
  cold_build_ms:
  warm_build_ms:
  one_script_build_ms:

optimized:
  cold_build_ms:
  warm_build_ms:
  one_script_build_ms:

compile:
  old_gdre_invocations:
  new_gdre_invocations:
  cache_hit_rate:

pack:
  old_files_copied:
  new_files_written:

release_validation:
  check_all:
  S0:
  S1:
  S3:
  S4:

risks:
rollback:
recommended_default_mode:
```

并更新仓库 AI 指南，使后续 Agent 默认：

```text
开发 = FAST
中央集成 / Promotion = RELEASE
```

---

# 最重要的实施顺序

严格按照：

```text
1. Timing
2. Persistent Compile Cache
3. Worker Autotune
4. Build Queue
5. Toolchain Attestation
6. Base Hash Index
7. Collision-safe GDRE Batching
8. Persistent Pack Staging
9. FAST / RELEASE 双模式
10. pck-patch 实验
```

不要一开始同时重写整个 Pipeline。

每一步：

```text
实现
→ benchmark
→ correctness regression
→ commit
→ push
→ 再进行下一项
```

目标：

> **让 AI 日常迭代尽可能快，但 Promotion Candidate 永远保持完整、可重复、可审计。**