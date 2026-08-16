# AGENTS.md — Mutagenic Recovery / Mod SDK / Localization Engineering Protocol

> ⚠️ **HISTORICAL ARCHIVE (2026-08-16)**: 本文件已被重构为根目录精简版 `AGENTS.md`（唯一全局规范 L0，约 130 行全局硬规则）。
> 本文件保留作为详细历史参考（Phase 0-7 细节、C0-C4 能力定义、本地化分类等），**不再是权威规则源**。
> 冲突时以根目录 `AGENTS.md` 为准；细节性内容迁移至 `docs/governance/` 与 `docs/architecture/`。


> **Authority:** This file is the primary operating contract for every AI agent working in this repository.
>
> **Supersedes:** Any earlier `AGENTS.md`, ad-hoc TODO list, chat instruction, local workaround, or historical completion claim that conflicts with this document.
>
> **Primary idea:** This is a reproducible engineering program, not an interactive bug-fixing session. Agents must manage the project as a staged state machine with immutable inputs, declared deltas, evidence-backed Gates, reproducible builds, and explicit rollback boundaries.

---

# 1. Mission

Build a deterministic and auditable Mutagenic engineering pipeline that can start from a pristine Windows game executable and produce validated modded/localized builds without corrupting unrelated game behavior.

The long-term engineering target is:

```text
pristine game
  -> deterministic fingerprint
  -> exact raw extraction
  -> recover/reference source
  -> Game Schema
  -> declarative Mod definitions
  -> generated worktree
  -> path-preserving compile / resource transformation
  -> script encryption where required
  -> runtime pack tree based on pristine raw content
  -> deterministic PCK creation
  -> deterministic EXE embedding
  -> full structural re-validation
  -> automated runtime smoke tests
  -> targeted human validation only where machines cannot decide
  -> release artifact + evidence bundle
```

The SDK must ultimately support, without abandoning reproducibility:

- Chinese localization;
- data/value mods;
- script/code mods;
- skill/equipment/enemy/map changes;
- asset replacement;
- declarative mod manifests;
- multiple independently explainable modifications;
- regression testing and rollback.

The goal is **not** merely to make one EXE launch once.

---

# 2. Agent Role

The primary agent is an **engineering orchestrator**.

It is responsible for:

1. understanding the current project phase;
2. selecting the next project-level objective;
3. protecting trusted baselines;
4. defining an experiment or build before executing it;
5. limiting the number of variables changed at once;
6. collecting machine-verifiable evidence;
7. stopping when a Gate fails;
8. updating machine-readable state;
9. deciding when human input is genuinely necessary;
10. handing the project to a future agent without relying on chat memory.

The primary agent is **not** expected to spend the project continuously patching individual symptoms.

A local symptom such as:

- `Null` in a UI field;
- blank button text;
- a missing `NodePath`;
- one crash stack;
- one malformed translation;
- one Steam warning;

is evidence to classify inside the program. It is not automatically the next project objective.

Before acting on a symptom, ask:

```text
Which subsystem owns this failure?
Which Gate should have caught it?
Can it be reproduced from a trusted baseline?
What is the minimum controlled delta that distinguishes the hypotheses?
Will this investigation improve the reusable pipeline, or merely patch one contaminated build?
```

---

# 3. Source of Truth and Evidence Hierarchy

Use this authority order:

1. `00_original/` immutable binaries and hashes;
2. `03_raw/` immutable extracted runtime content;
3. saved machine evidence in `01_baseline/`, `manifests/`, and `10_logs/`;
4. reproducible results from current scripts and locked tools;
5. `10_logs/status.json` / `PROJECT_STATE.md` only when supported by evidence;
6. source-code analysis and controlled experiments;
7. historical failed builds and old reports;
8. prior chat conclusions.

Historical artifacts are useful for hypotheses but are never trusted automatically.

If a current measurement contradicts an old PASS, the old PASS is revoked immediately.

A human-observed functional failure overrides a machine PASS that claimed to cover the same function.

---

# 4. Evidence Vocabulary

For Gates use only:

```text
NOT_STARTED
IN_PROGRESS
PASS
FAIL
BLOCKED
HUMAN_REQUIRED
NOT_APPLICABLE
```

For technical conclusions use:

```text
FACT
INFERENCE_HIGH
INFERENCE_MEDIUM
INFERENCE_LOW
UNKNOWN
CONTRADICTED
```

For implementation/project items use:

```text
VERIFIED_DONE
LIKELY_DONE
PARTIAL
NOT_DONE
BLOCKED
UNKNOWN
CONTRADICTED
```

Never use `PASS`, `VERIFIED`, `DONE`, or equivalent language without saved evidence that states exactly what was tested.

Every PASS must also state what it **does not prove**.

Example:

```text
BOOT = PASS
proves: the real game window opened with no ALERT dialog
not_proven: character creation, gameplay, persistence, localization quality
```

---

# 5. Non-Negotiable Immutability Rules

## 5.1 `00_original` is sacred

Never write to, patch, rename, truncate, append to, delete, or replace anything in `00_original/`.

Every final EXE must originate from the pristine original, not from a previous modded EXE.

## 5.2 `03_raw` is immutable after verified extraction

Once extraction passes its checksum/path Gate, `03_raw/` becomes immutable.

It is the canonical runtime-content baseline.

Production pack trees must be derived from `03_raw`, not from old worktrees.

## 5.3 `04_recovered` is immutable after recovery

`04_recovered/` is a **reference/source-analysis tree**.

It is not automatically safe as a production runtime tree.

Recovered/decompiled source may contain normalization or decompiler artifacts. Therefore:

- do not batch-compile every recovered script merely because source exists;
- do not package `04_recovered` directly;
- only compile scripts explicitly declared as changed by a Mod or controlled capability test.

## 5.4 Generated directories are disposable

The following are generated and must be reproducible:

```text
06_worktree/
07_compiled/
08_pack/
09_output/
```

They must never become canonical source inputs for a future production build.

A new build starts from immutable inputs plus declarative changes.

## 5.5 Failed builds are forensic artifacts only

A failed or contaminated EXE may be preserved for:

- diffing;
- log comparison;
- crash reproduction;
- hypothesis generation.

It may never become the base of another production build.

---

# 6. Required Repository Layout

Maintain this logical structure:

```text
AGENTS.md
PROJECT_STATE.md
justfile
tools.lock.json

00_original/
01_baseline/
02_tools/
03_raw/
04_recovered/
05_schema/

mods/
  <mod-id>/
    mod.json
    patches/
    translations/
    assets/
    tests/

06_worktree/
07_compiled/
08_pack/
09_output/
10_logs/

scripts/
  baseline/
  recover/
  schema/
  patch/
  build/
  validate/
  test/
  release/

manifests/
test_saves/
docs/
.secrets/              # local only; never publish
```

Existing layouts may be migrated gradually, but the architectural roles above must remain clear.

---

# 7. Project State Machine

The project proceeds through phases. Do not skip a phase because a later result looks visually promising.

```text
PHASE 0  Environment & Toolchain
PHASE 1  Original Fingerprint & Raw Recovery
PHASE 2  Clean NOOP / Packaging Baseline
PHASE 3  Capability Qualification
PHASE 4  Game Schema & Declarative Mod Layer
PHASE 5  Localization Safety Architecture
PHASE 6  Incremental Mod / Localization Integration
PHASE 7  Functional Regression & Persistence Tracks
PHASE 8  Release Validation
```

Each phase has explicit entry conditions, outputs, exit Gates, and stop conditions.

---

# 8. PHASE 0 — Environment and Toolchain

## Purpose

Make the build environment reproducible before touching game content.

## Required outputs

At minimum record:

- OS/version;
- PowerShell version;
- Python executable/version;
- `uv` if used;
- Git version;
- GDRE executable/version;
- Godot/GdTool/bytecode tooling where applicable;
- current project path;
- disk availability;
- SHA-256 for relevant executable tools;
- exact command/help output used to establish supported CLI syntax.

Store environment evidence under `10_logs/` and tool locks in `tools.lock.json`.

## Rules

- discover actual tool paths; never assume them;
- do not auto-update tools during a production build;
- install project-local tooling under `02_tools/` where practical;
- do not pollute global Python to make an old script work;
- use a project-local virtual environment or pinned environment;
- on Windows PowerShell, do not paste Bash-only heredoc syntax;
- complex logic belongs in scripts, not huge inline shell commands.

## Exit Gate

`ENVIRONMENT = PASS` only when the environment can inspect the original game and the toolchain is sufficiently pinned to reproduce results.

---

# 9. PHASE 1 — Original Fingerprint and Recovery

## Purpose

Create a trustworthy immutable base.

## Required products

```text
01_baseline/game_fingerprint.json
01_baseline/pe.json
01_baseline/pck_manifest.json
03_raw/
04_recovered/
manifests/raw_manifest.json
manifests/recovered_manifest.json
```

## Fingerprint must include

- original EXE SHA-256;
- size;
- PE architecture and sections;
- Godot version/build identification;
- PCK version;
- PCK start/size discovery evidence;
- file entry count;
- complete path inventory;
- `.gde` count;
- `.remap` count;
- `project.binary` presence;
- relevant script encryption/bytecode characteristics.

## Raw extraction rules

- validate every PCK entry that can be validated;
- checksum errors are production failures, not warnings to suppress;
- never use ignore-checksum flags just to turn a Gate green;
- preserve zero-byte files exactly;
- distinguish tool-generated sidecars from actual PCK paths.

## Script recovery rules

Determine and record:

- bytecode revision/version;
- script encryption format;
- verified decryption method;
- verified compile method;
- verified re-encryption method;
- exact path semantics of compiler output.

Secrets such as script keys must not be printed in reports, command histories, manifests, or shareable logs.

Store them only in a local secret mechanism such as `.secrets/` or an environment variable.

## Exit Gates

```text
ORIGINAL_FINGERPRINT = PASS
RAW_EXTRACTION = PASS
RECOVERY_REFERENCE = PASS or PARTIAL with exact limitations
SCRIPT_CRYPTO_KNOWLEDGE = PASS before production code mods
```

---

# 10. PHASE 2 — Clean NOOP and Packaging Baseline

## Purpose

Prove that the game can be rebuilt without any gameplay/content modification.

This is the most important control build in the project.

## NOOP definition

A CLEAN NOOP build must be derived from:

```text
00_original + 03_raw
```

and must contain no:

- translation changes;
- recovered-source recompilation;
- script patch;
- scene/resource patch;
- font replacement;
- Steam/save modification;
- gameplay modification.

Untouched runtime content must remain byte-identical to `03_raw`.

## Packaging contract

For this project, packaging is a standalone subsystem.

A packaging implementation is accepted only if it proves all of the following:

- PCK can be listed;
- PCK can be fully re-extracted;
- path set equals the intended source tree;
- actual file content hashes equal the intended source tree;
- `project.binary` is present;
- expected `.gde` and `.remap` files are present;
- embedded PCK boundaries are valid;
- PE `pck` section metadata is internally consistent;
- PCK trailer is valid;
- embedded entry offsets resolve to the intended bytes;
- real game window boots without an ALERT dialog.

A process merely remaining alive is **not** a boot PASS.

## Packaging stability rule

Once a packaging path passes CLEAN NOOP structural and runtime controls, freeze it as an infrastructure subsystem.

Do not repeatedly redesign PCK/PE embedding while debugging unrelated localization or gameplay regressions.

Alternative packers/embedding approaches must be tested as separate infrastructure experiments, never introduced silently during feature debugging.

## Exit Gate

`CLEAN_NOOP = PASS` requires both:

1. structural equivalence to the raw input; and
2. representative human/runtime behavior equivalent to the original for core gameplay flow.

Baseline behaviors shared by ORIGINAL and CLEAN NOOP are recorded separately and are **not mod regressions**.

---

# 11. PHASE 3 — Capability Qualification

## Purpose

Before a large localization or mod, prove that each transformation class works independently.

This phase is about **capabilities**, not specific game bugs.

Required capability milestones:

```text
C0  SCRIPT ZERO-CHANGE ROUNDTRIP
C1  ONE-VALUE MOD
C2  ONE-CODE MOD
C3  ONE-RESOURCE MOD
C4  ONE-ASSET MOD
```

## C0 — Script roundtrip capability

Prove that the script pipeline can handle representative script classes without semantic drift.

Use a stratified set, not every script and not only one trivial script. Include examples such as:

- global/autoload-style logic;
- UI script;
- gameplay script;
- level/scene script;
- one larger/complex script;
- one plugin/non-gameplay script if relevant.

For zero-change roundtrip:

```text
original .gde
  -> decrypt
  -> recover/decompile
  -> compile
  -> encrypt
  -> resulting .gde
```

Record whether the result is byte-identical.

Byte identity is strong evidence. Non-identity is not automatically failure, but it requires semantic/runtime validation before the pipeline is trusted.

Never infer that one trivial roundtrip proves all 524 scripts.

## C1 — ONE-VALUE

Change exactly one harmless data value through the intended declarative patch system.

Acceptance:

- exact input declared;
- exact output delta declared;
- final build contains only the intended logical change;
- structural Gates pass;
- runtime behavior matches expectation.

## C2 — ONE-CODE

Change one controlled script behavior.

Prefer a machine-observable effect where possible.

Acceptance:

- only declared script output changes;
- compile path is preserved;
- encryption/remap contract is preserved;
- structural Gates pass;
- runtime effect proves the code actually executed.

## C3 — ONE-RESOURCE

Change one `.tscn`/`.tres` property without changing associated script logic.

Purpose: prove structured resource transformation independently from script transformation.

## C4 — ONE-ASSET

Replace one controlled image/font/audio asset while preserving import/remap consistency.

Visual confirmation may be HUMAN_REQUIRED, but structural resource validation remains mandatory.

## Exit Gate

`CAPABILITY_QUALIFICATION = PASS` only after the project can independently demonstrate data, code, resource, and asset changes.

Only then may broad localization or major Mods begin.

---

# 12. PHASE 4 — Game Schema and Declarative Mod Layer

## Purpose

Stop treating the game as an unstructured collection of strings and files.

Build a machine-readable schema of gameplay concepts and structural identifiers.

## Game Schema should identify, where discoverable

- player classes;
- skills;
- items/equipment;
- stats;
- modifiers/affixes;
- enemies;
- levels/maps;
- registries;
- resource references;
- state/enum values;
- save identifiers;
- input actions;
- groups/signals;
- important scene/node relationships.

Schema confidence must be explicit. Unknowns remain unknown.

## Declarative Mod principle

Production modifications must be represented as manifests, not remembered shell edits.

A Mod manifest should declare:

- mod ID/version;
- target pristine game fingerprint;
- dependencies/conflicts;
- modified logical entities;
- affected paths;
- patch type;
- expected preimage hash or other guard;
- source patch/translation/asset input;
- expected validation tests.

Suggested logical patch classes:

```text
VALUE_PATCH
TEXT_PATCH
CODE_PATCH
RESOURCE_PATCH
ASSET_PATCH
CONFIG_PATCH
```

## Worktree rule

`06_worktree/` is generated from immutable reference inputs plus manifests.

Agents must not make ad-hoc production edits directly in generated worktrees and then treat those edits as source of truth.

If an exploratory edit proves useful, convert it into a declarative patch before production integration.

---

# 13. Production Build Architecture

The production build model is **copy pristine runtime, overlay only declared deltas**.

Canonical model:

```text
03_raw
  -> copy to ephemeral 08_pack staging
  -> apply resource/asset deltas
  -> overlay only compiled/encrypted scripts that are intentionally changed
  -> verify delta manifest
  -> create PCK
  -> embed into pristine 00_original executable
  -> full re-extraction validation
```

This rule is fundamental:

> **Untouched scripts/resources stay byte-identical to `03_raw`.**

Do not recompile all recovered scripts simply because a compiler is available.

Do not rewrite all scenes because a translation tool touched one field.

The changed-file set must be explainable from Mod manifests.

---

# 14. Script Build Contract

For every intentionally modified script:

1. start from the verified recovered/reference source for the matching raw `.gde`;
2. apply a declared structured patch;
3. compile using the locked bytecode/toolchain;
4. preserve the full relative output path;
5. verify the compiler produced a **file**, not a same-named directory;
6. re-encrypt using the verified project method when required;
7. preserve/remap references correctly;
8. overlay only that declared runtime file into the pack tree;
9. record source and output hashes.

Never flatten compiled output paths.

Never accommodate a broken compiler-output layout downstream. Fix the generating stage.

Never rename an unencrypted `.gdc` to `.gde` and call encryption verified.

---

# 15. Scene / Resource Transformation Contract

Godot scenes and resources contain both user-visible content and structural data.

Never use unrestricted global text replacement across `.gd`, `.tscn`, `.tres`, project files, or JSON registries.

Treat the following as structural by default:

- node names;
- `NodePath`;
- `$Node/Path` expressions;
- `get_node()` arguments;
- `ExtResource` and `SubResource` relationships;
- `res://` paths;
- `user://` paths;
- signals;
- groups;
- InputMap actions;
- Audio Bus names;
- animation names;
- registry keys;
- dictionary keys used as IDs;
- enum/state strings;
- class IDs;
- save IDs;
- lookup keys;
- internal asset names.

A structural value may be changed only when the Mod explicitly intends to change program structure and the dependent references are understood.

Prefer structured parsers/patchers with exact field targeting.

Avoid reserializing untouched resources when possible.

---

# 16. PHASE 5 — Localization Safety Architecture

Localization is implemented as a Mod on top of the validated SDK architecture.

It is not a special permission to rewrite arbitrary strings.

## String classification

Every translation candidate must be classified as one of:

```text
DISPLAY_SAFE
STRUCTURAL
AMBIGUOUS
DO_NOT_TRANSLATE
```

`AMBIGUOUS` is not translated automatically.

## Extraction requirements

Translation units should include:

- exact source text;
- file path;
- field/context;
- occurrence count;
- semantic tags;
- placeholders/tokens;
- surrounding context where useful;
- classification/confidence.

## Translation application requirements

- apply only to `DISPLAY_SAFE` fields;
- preserve placeholders exactly;
- preserve formatting tokens;
- preserve numeric semantics;
- preserve resource paths and structural IDs;
- validate source preimage before replacement;
- produce a changed-unit manifest;
- reject unmatched or unexpectedly duplicated replacements.

## Glossary

Use a versioned glossary for recurring ARPG terminology.

Glossary consistency is necessary but does not override structural safety.

## Fonts

CJK font support is a separate asset capability, not mixed into script debugging.

Before production:

- verify glyph coverage;
- verify font license/distribution rights;
- verify relevant font resources/imports;
- perform targeted visual QA for clipping, fallback, and layout.

## Localization rollout

Do not jump from a clean baseline to full translation.

Recommended expansion:

```text
small UI slice
  -> menu/dialog slice
  -> gameplay display strings
  -> descriptions/data text
  -> broad localization
```

Each expansion is a manifest-defined delta with regression checks.

---

# 17. PHASE 6 — Incremental Integration

Once capabilities and Mod architecture pass, integrate features in controlled batches.

A batch is valid only if:

- scope is declared before build;
- changed-path set is predicted;
- final changed-path set is compared with prediction;
- build starts from immutable baseline inputs;
- no previous modded EXE is reused;
- structural validation passes before runtime testing;
- runtime regression scope is appropriate to the batch.

Prefer small semantically coherent batches, not arbitrary file counts.

Examples:

```text
character-selection localization
inventory localization
skill descriptions
one gameplay module
one asset family
```

If a batch fails, bisect the manifest or revert the batch. Do not patch the failed executable in place.

---

# 18. PHASE 7 — Runtime Regression Strategy

Testing is layered. A later tier never replaces an earlier tier.

## Tier S0 — Structural

Must run for every build:

- PCK list;
- full PCK extraction when appropriate;
- path-set comparison;
- file-content hash comparison against intended pack tree;
- project settings presence;
- script/remap counts;
- PE/PCK/trailer/offset checks;
- declared-delta comparison.

Failure => build is invalid. Stop before runtime debugging.

## Tier S1 — Boot

Verify:

- actual game window title/presence;
- no ALERT modal;
- no fatal project-load failure;
- current build hash tied to the log/process.

`process alive` alone never passes this tier.

## Tier S2 — Core smoke

Representative flow should cover, where feasible:

- main menu;
- character/class selection;
- creation/selection dialog text;
- `Start Game`;
- transition into gameplay/hideout/level;
- basic interaction.

A build that boots but fails this tier is not functionally valid.

## Tier S3 — Persistence / Exit

Test separately:

- save creation/update;
- restart persistence;
- Quit behavior;
- Steam/local-save branch behavior where relevant.

Do not mix this tier into unrelated localization root-cause analysis.

If ORIGINAL and CLEAN NOOP share a behavior, classify it as a baseline/environment track until proven otherwise.

## Tier S4 — Mod-specific behavior

Test the exact intended semantic effect of each Mod/batch.

## Tier S5 — Visual localization

Human or visual automation may check:

- missing/blank text;
- untranslated strings;
- font glyphs;
- clipping/overflow;
- layout;
- image replacement.

Visual PASS cannot substitute for structural or gameplay PASS.

---

# 19. Human Testing Policy

Human interaction is a controlled evidence checkpoint, not a substitute for engineering evidence and not a blocking dependency for subsequent machine-verifiable work.

Ask for human testing only when:

- GUI semantics cannot be reliably automated;
- visual quality is the actual question;
- a short functional path is needed to distinguish machine-prepared candidates.

Before asking the human to test, provide:

- exact candidate path;
- SHA-256;
- adjacent runtime dependencies and their hashes where relevant;
- exact test checklist;
- expected outcomes;
- what the test will prove;
- what it will not prove;
- a recorder that preserves observer, timestamp, candidate hash, scope, and verdict.

Every phase evidence bundle must retain a human checkpoint record, even when the status is `NOT_APPLICABLE`, `HUMAN_REQUIRED`, `PASS`, or `FAIL`. The checkpoint is a historical/phase record. `HUMAN_REQUIRED` by itself is not an active project blocker and must not stop independent structural, build, validation, or documentation work. A human-dependent claim remains unclosed until its checkpoint is recorded, but unrelated machine Gates may proceed.

## Phase checkpoint record

For every phase that has a human-observable question, retain one machine-readable checkpoint in that phase's evidence bundle. The record must bind:

- phase and scope;
- candidate path and SHA-256, plus relevant adjacent dependency hashes;
- observer and timestamp;
- checklist and verdict;
- screenshot or other visual evidence hash when supplied;
- `proves`, `not_proven`, and review/state-change fields.

When a phase has no human-observable question, retain a `NOT_APPLICABLE` record with the reason. A pending, completed, or failed checkpoint is phase evidence only; it must not block unrelated machine-verifiable work. Only an explicitly declared release condition for the exact artifact may make a human verdict release-blocking.

When a human check is available, run it once for each materially distinct candidate or phase scope. Do not ask a human to retest a byte-identical candidate unless the environment, saved state, or test scope changed materially.

If a human check fails, downgrade only the affected feature/phase claim, preserve the candidate as forensic evidence, and return production integration to the newest trusted baseline. Do not repair the failed executable in place. A failed human checkpoint does not block unrelated program phases.

Batch human tests where practical instead of requesting interaction after every tiny internal step.

---

# 20. Experiment Discipline

Every nontrivial investigation must have an experiment definition before edits begin.

Minimum record:

```text
EXPERIMENT_ID
QUESTION
BASELINE
CONTROL
DELTA
EXPECTED_DISTINGUISHING_RESULT
INPUT_HASHES
OUTPUT_PATH
VALIDATION
RESULT
CONCLUSION
NEXT_DECISION
```

## Single-variable rule

When establishing causality, change one logical variable at a time.

A logical variable may occasionally require a tightly coupled file pair, but this must be explicitly justified.

Do not simultaneously change:

- packer;
- script source;
- scene;
- font;
- Steam logic;
- translation rules;

and then try to infer which solved the problem.

## Escalation rule

Use this order:

```text
control
  -> single delta
  -> paired dependency delta if necessary
  -> small coherent batch
  -> larger integration
```

## Stop rule

When an experiment has answered its stated question, stop and record the result.

Do not immediately transform a diagnostic experiment into an unreviewed production patch.

---

# 21. Failure Handling and Root-Cause Policy

A failure must first be assigned to a subsystem:

```text
ENVIRONMENT
BASELINE
RECOVERY
SCRIPT_PIPELINE
RESOURCE_PIPELINE
LOCALIZATION
PACKAGING
RUNTIME_GAMEPLAY
PERSISTENCE_STEAM
VISUAL_ASSET
UNKNOWN
```

Then build a root-cause tree rather than jumping to the first plausible log line.

For every hypothesis record:

```text
Finding
Evidence
Competing explanations
Confidence
Discriminating experiment
```

A log line immediately preceding a crash is `OBSERVED_BEFORE_CRASH`, not automatically `PROVEN_CRASH_CAUSE`.

Do not repeatedly announce “root cause found” without an isolated validation.

---

# 22. Rollback and Contamination Policy

Rollback is a normal engineering operation.

Rollback when:

- a Gate that previously passed is contradicted;
- generated worktree provenance is unclear;
- changed-file inventory is not explainable;
- production output contains undeclared changes;
- a build depends on a previous failed build;
- compiler/packer output paths are inconsistent;
- toolchain changed midstream;
- broad localization introduced structural changes.

Rollback target should be the newest **trusted immutable or Gate-passed baseline**, not the nearest convenient directory.

Never “repair forward” indefinitely from a contaminated build.

---

# 23. Build IDs, Artifact Provenance, and Logs

Every significant build or experiment gets a unique build ID.

Recommended form:

```text
YYYYMMDD-HHMM-<phase>-<short-id>
```

Never repeatedly overwrite generic files such as:

```text
data.pck
Mutagenic_modded.exe
godot.log
```

without binding them to a build ID.

Each build evidence directory should contain, as applicable:

```text
build.json
input_manifest.json
delta_manifest.json
toolchain.json
pck_validation.json
exe_validation.json
runtime.json
stdout.log
stderr.log
godot.log
crash/
report.md
```

`build.json` should include:

- build ID;
- timestamp;
- original EXE hash;
- raw manifest hash;
- tool lock hash;
- Mod manifest hashes;
- pack tree manifest hash;
- PCK hash;
- final EXE hash;
- validation Gate results.

Logs must be associated with the correct build SHA, PID, and run time.

Never use an old log as evidence for a new EXE.

---

# 24. Machine-Readable Project State

Maintain at minimum:

```text
10_logs/status.json
PROJECT_STATE.md
```

`status.json` is authoritative for machine resumption.

Suggested shape:

```json
{
  "updated_at": "ISO-8601",
  "project_phase": "CAPABILITY_QUALIFICATION",
  "original_sha256": "...",
  "trusted_baselines": {
    "original": {"status": "PASS", "sha256": "..."},
    "raw": {"status": "PASS", "manifest": "..."},
    "clean_noop": {"status": "PASS", "sha256": "..."}
  },
  "gates": {
    "environment": "PASS",
    "fingerprint": "PASS",
    "raw_extraction": "PASS",
    "recovery": "PASS",
    "clean_noop": "PASS",
    "script_capability": "IN_PROGRESS",
    "value_mod": "NOT_STARTED",
    "code_mod": "NOT_STARTED",
    "resource_mod": "NOT_STARTED",
    "asset_mod": "NOT_STARTED",
    "schema": "NOT_STARTED",
    "localization": "NOT_STARTED",
    "release": "NOT_STARTED"
  },
  "known_baseline_behaviors": [],
  "active_blockers": [],
  "next_program_objective": "...",
  "last_evidence_bundle": "..."
}
```

Do not store secrets in state files.

A future agent must be able to resume from filesystem state and evidence without reconstructing the project from chat history.

---

# 25. Tool and Script Engineering Rules

- Prefer reusable scripts over copy-pasted command fragments.
- Scripts must fail loudly on unexpected input.
- Validate input fingerprints before destructive/generated operations.
- Use nonzero exit codes for failed Gates.
- Avoid “best effort” production builds.
- Never silently skip failed files.
- Do not normalize or rewrite files outside the declared scope.
- Preserve relative paths end-to-end.
- Tests should produce machine-readable results when possible.
- When a workaround becomes required for production, encode it explicitly and test it; do not leave it as tribal knowledge.

For third-party tool behavior, inspect the actual installed tool help/version rather than relying on remembered CLI syntax.

For format semantics, prefer matching-version upstream source/documentation over guesswork.

---

# 26. Subagent Policy

Subagents may be used for bounded parallel work such as:

- schema discovery;
- translation batches;
- static code classification;
- documentation analysis;
- independent hypothesis review.

Every subagent task must specify:

- exact read inputs;
- exact allowed write outputs;
- forbidden files/actions;
- validation requirements;
- completion format.

Subagent claims are not automatically trusted.

The primary agent must verify produced artifacts, counts, hashes, and syntax before accepting them.

Do not accept “task completed” when the expected artifact is missing or malformed.

---

# 27. Security and Privacy

Never expose the script-encryption key in:

- `AGENTS.md`;
- `PROJECT_STATE.md`;
- ordinary logs;
- build manifests;
- shell command history where avoidable;
- screenshots;
- shared reports;
- public repositories.

Use `.secrets/` or environment-based secret injection.

Do not publish local user paths, share URLs, crash dumps, or save data unless explicitly required and sanitized.

Crash dumps and user saves may contain sensitive local data. Keep them local by default.

---

# 28. Prohibited Patterns

The following are explicitly prohibited in production workflow:

1. patching a previously modded EXE to create a new release;
2. modifying `00_original`, `03_raw`, or verified `04_recovered`;
3. using historical generated trees as new canonical inputs;
4. global text replacement over GDScript/scenes/resources;
5. translating English-looking identifiers without semantic classification;
6. recompiling every recovered script by default;
7. flattening compile output paths;
8. accepting a directory where a compiled script file was expected;
9. ignoring PCK checksum failures;
10. treating process survival as gameplay success;
11. treating absence of stderr as functional success;
12. using stale logs for a new build;
13. changing multiple subsystems during a causal experiment;
14. continuing feature work after a structural Gate failure;
15. changing tool versions in the middle of a production build;
16. hiding known failures behind `PASS` labels;
17. asking the human to repeatedly test identical binaries;
18. conflating baseline game behavior with a Mod regression;
19. fixing a generated artifact instead of fixing the generating stage;
20. declaring the project complete because a game window appeared.

---

# 29. Decision Rules for Common Situations

## If a modified build crashes but CLEAN NOOP does not

Do not revisit PCK packaging unless structural evidence fails.

Investigate the declared modification layers from the clean baseline.

## If ORIGINAL and CLEAN NOOP share a behavior

Classify it as baseline/environment behavior, not a Mod regression.

Create a separate track if changing that behavior is in scope.

## If a single machine Gate fails

Stop downstream validation and fix/investigate that Gate first.

## If changed-file count is larger than predicted

The build is contaminated until explained.

## If the agent cannot prove provenance of a generated directory

Regenerate it from immutable inputs.

## If a full localization build breaks gameplay

Do not repair the broken EXE in place.

Return to CLEAN NOOP / last trusted integration milestone and reintroduce manifest-defined batches.

## If a tool emits different serialization for semantically equivalent content

Record the distinction. Decide acceptance based on the consuming runtime and explicit validation, not on superficial byte differences alone.

## If human test contradicts an automated claim

Downgrade the relevant Gate and improve the automated test so the same false positive cannot recur.

---

# 30. Current Project Snapshot — Resume Guidance

> This section describes the currently established project state as of 2026-08-14. `10_logs/status.json` should be updated as work progresses. If later evidence conflicts with this section, current evidence wins and this section must be revised.

## Current evidence override (2026-08-14)

The authoritative current state is `10_logs/status.json` and the latest evidence bundle, not the historical milestone text below:

- Current phase: `PHASE_6_INCREMENTAL_MOD_LOCALIZATION_INTEGRATION`, with the separate Phase 7 persistence track `IN_PROGRESS`, after C5-L1 and C5-L2 were closed from immutable inputs; C5-L3, C5-L4, and C5-L5 have machine PASS evidence and retained nonblocking human checkpoints.
- C5-L2 is the newest reviewed manifest-scoped localization milestone: its machine structural/boot evidence and its SHA-guarded character-selection core/visual checkpoint are `PASS` for candidate SHA `4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3`.
- C5-L3 is the previous machine candidate: its dependency chain, exact DISPLAY_SAFE patch application, resource contract, declared delta, font coverage/license, PCK/EXE structure, embedded text, extraction comparison, and exact-candidate boot checks are `PASS`; candidate SHA is `B8564289CE2DEC95709F4230C558D7D56F22DA8E1C7C5D256C68331915EAB02A`.
- C5-L3 human evidence is retained at `10_logs/C5-L3-character-class-dialogs-20260814/human_checkpoint.json` with status `HUMAN_REQUIRED` and `active_blocker=false`. This is a phase record point, not a standing dependency; independent machine work may continue without waiting for it.
- C5-L4 is the newest machine candidate: its dependency chain, exact Settings `DISPLAY_SAFE` patch application, resource contract, six-path declared delta, font coverage/license, PCK/EXE structure, embedded text, extraction comparison, and exact-candidate boot checks are `PASS`; candidate SHA is `8563851B812A2E1AA8C86DCA0ADB3A89CD060983249BD2446C727DAA7A475397`.
- C5-L4 human evidence is retained at `10_logs/C5-L4-settings-dialog-20260814/human_checkpoint.json` with status `HUMAN_REQUIRED` and `active_blocker=false`. This is a phase record point, not a standing dependency; independent machine work may continue without waiting for it.
- C5-L5 is the newest machine candidate: its dependency chain, exact Keybinds `DISPLAY_SAFE` patch application, resource contract, seven-path declared delta, font coverage/license, PCK/EXE structure, embedded text, extraction comparison, and exact-candidate boot checks are `PASS`; candidate SHA is `F1DAE1C7EAB8784DA44C14C06717C38E53709A1D95A49F185CE0D300A7C8E90E`.
- C5-L5 human evidence is retained at `10_logs/C5-L5-keybinds-dialog-20260814/human_checkpoint.json` with status `HUMAN_REQUIRED`, `result=PARTIAL`, and `active_blocker=false`. The SHA-bound screenshot proves the visible `键盘设置` title, `完成` button, displayed action labels, glyphs, and layout; input-action behavior and completion return path remain unproven. This is a phase record point, not a standing dependency; independent machine work may continue without waiting for it.
- The C5-L5 screenshot's all-`Unassigned` values are tracked separately by `10_logs/C5-L5-keybinds-dialog-20260814/keybind_defaults_audit.json` (`PASS`, technical conclusion `INFERENCE_HIGH`): default InputMap keys exist, but fresh `keybind_overrides` is empty, the initial path does not call `load_keybinds`, and `Show Inventory` is outside `configurable_actions`. This is a baseline initialization/configuration hypothesis, not a proven C5-L5 translation regression; do not patch it into the localization candidate without a separate CODE_PATCH scope.
- The C5-L5 resource boundary audit is `PASS` at `10_logs/C5-L5-keybinds-dialog-20260814/keybind_resource_boundary_audit.json`: exactly two Keybinds text lines changed; action labels/names, `project.binary`, scripts, and remaps remain byte-identical to raw. The `Unassigned` observation is outside the declared localization delta boundary.
- The exact requested main-menu scope is separately PASS at `10_logs/C5-L1-localization-menu-play-font-20260814/requested_scope_audit.json`: only `Play -> 开始游戏` changes in the visible menu, other visible labels remain English, and later C5-L2 through C5-L5 batches are broader independent experiments rather than proof required for that exact scope.
- Human review queue is recorded at `10_logs/human_review_queue_20260814.md`. C5-L3 v3 now has a SHA-bound partial human checkpoint recording the user-reported Quit failure and missing prior character; C5-L4 remains queued. The exact C5-L5 candidate (`F1DAE1C7EAB8784DA44C14C06717C38E53709A1D95A49F185CE0D300A7C8E90E`, PID `17532`) was launched with a responding `Mutagenic` window, and the supplied screenshot is recorded as a SHA-bound partial visual result. The queue is phase evidence only and has no active blocker.
- `ENVIRONMENT`, `FINGERPRINT`, `RAW_EXTRACTION`, `RECOVERY`, `SCRIPT_CRYPTO_KNOWLEDGE`, `CLEAN_NOOP`, `C0`, `C1`, `C2`, `C3`, `C4`, and `SCHEMA` have current saved evidence; C3 clean structural/boot Gates and its SHA-bound Help Guides alignment visual effect are `PASS`.
- The previous C5-L1 candidate was `10_logs/C5-L1-localization-menu-play-font-20260814/c5_l1_menu_font_v3_normalized.exe`, SHA-256 `1FFD924471C5C89B04DFF8E06BF5E227D0EB03F02B39D41FC1C1B38DFCAF3FA3`; its reviewed main-menu slice remains a prior trusted checkpoint.
- The current C5-L2 candidate is `10_logs/C5-L2-character-select-20260814/c5_l2_character_select_normalized.exe`, SHA-256 `4675BE5DA3FE9F32F8C0F9DD4B8AFFA32DB09E8D6962BF74D03C1D94B5FABDE3`, and requires the adjacent `steam_api64.dll` for the controlled launch.
- C5-L2 machine structure/PCK/EXE/boot checks and the user-observed character-selection core/visual checkpoint are `PASS` for the declared main-menu-to-character-selection slice.
- `capture_matrix_v11.json` proves only that three capture methods were attempted against the foreground target window; its pixels were invalid visual evidence.
- The current program objective is to retain C5-L2 as the newest user-accepted trusted checkpoint, retain C5-L3/C5-L4/C5-L5 machine evidence and nonblocking human checkpoints, and complete the explicitly authorized controlled Phase 7 ORIGINAL/CLEAN NOOP/C5-L2 persistence comparison. Do not perform any additional Steam/cloud or save mutation outside the named one-time disposable character and the recorded protocol; do not translate additional visible labels without explicit scope and provenance.
- The v15 launch precheck passed for the exact candidate/DLL and a responding `Mutagenic` window; v16 is the direct-observation session, and `human_visual_result_v17.json` plus `human_visual_result_review_v27.json` record a user `PASS` for the complete visual checklist against candidate SHA `1FFD924471C5C89B04DFF8E06BF5E227D0EB03F02B39D41FC1C1B38DFCAF3FA3`.
- The screenshot `human_observation_v27.png` has SHA-256 `1D69F7F0C0D86A66D97AB7728430FAC353F37106F16F3330E6EB35E4DAAEDCB0`; it shows only `开始游戏` in Chinese and the other visible menu labels in English, with normal glyphs/fallback/clipping/layout. It proves only this displayed menu slice.
- The v18 and v20 read-only session snapshots predate the v17 result and remain historical session evidence; they do not override the reviewed user result.
- The v23 direct-HWND `gfxcapture` GPU control experiment produced byte-identical solid-black frames for C2 and C5-L1; it is `INCONCLUSIVE_FOR_VISUAL_CONTENT` and must not be reused as visual evidence.
- The v26 `ddagrab` Desktop Duplication attempt timed out without producing a frame or metadata; it is `UNKNOWN`, not visual evidence, and must not be repeated.
- There is no active human blocker. C5-L1 and C5-L2 completed checks plus the C5-L3/C5-L4/C5-L5 checkpoints are retained as SHA-bound phase evidence; the latest C5-L5 screenshot is recorded in `human_checkpoint.json` with SHA `BAEA6CC7AFB58D97F62A40AE1B5E84E58E77CDD19688B26D6AC49766D4273AB8` and proves only the visible Keybinds subset. The earlier English Keybinds image remains unbound and is not a C5-L5 failure. Automated capture defects and the failed C5-L4 substring validator remain forensic and must not be reused as visual evidence or text evidence. Future phases must retain the same checkpoint record without waiting on it to perform independent machine work.
- Phase 7 persistence preparation and the explicit authorization are recorded at `10_logs/P7-persistence-track-20260814/`: input integrity, SHA-guarded control preflight, and the static GameState/Constants contract are `PASS`; `authorization_granted_original_v2.json` records the second explicit `AllowDisposableTestSave` authorization for the SHA-locked ORIGINAL candidate. The v2 stage and relaunch records bind EXE SHA `C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209`, DLL SHA `DCFAA13AA419A0641917205957DBE15AA472E7CF09A28CF8D3CF429598E67799`, and the fixed disposable name `P7_ORIGINAL_20260814`. The user reports that the role was created without using Quit, but after exact-path relaunch the SHA-bound screenshot shows an empty character list, English ORIGINAL labels, and `Quit` unusable; save debounce and save provenance were not confirmed, so persistence is `NOT_ESTABLISHED`, not a proven root cause. The verified ephemeral PID was cleaned up. The read-only post-ORIGINAL-v2 preflight is also `PASS`: all three control EXE/DLL hashes, immutable input counts, no active process, and no matching local save file were verified without Steam reads or save mutation. A CLEAN NOOP non-mutating v2 window is currently open under `session_launch_no_save_v2.json` for English baseline/Quit only; no character creation or save mutation is allowed. CLEAN NOOP/C5-L2 runtime save comparison still requires candidate-scoped authorization. The read-only `quit_static_hypothesis_v1.json` records an `INFERENCE_HIGH` Steam async-save callback hypothesis, not a proven root cause. Human checkpoints are required evidence records but are nonblocking project policy; do not promote the runtime Gate from window launch alone. Never modify `00_original` or `03_raw`; every candidate uses a fresh ephemeral stage.
- The read-only Quit static review v2 is `10_logs/P7-persistence-track-20260814/quit_static_hypothesis_v2.json` with technical conclusion `INFERENCE_HIGH`: it identifies the `save_game()` debounce -> Steam `fileWriteAsync` -> `_on_save()` -> quit-notification chain, but does not prove a runtime root cause; the exact ORIGINAL/CLEAN NOOP comparison remains the discriminator.
- CLEAN NOOP v3 has a SHA-bound human checkpoint at `10_logs/P7-persistence-track-20260814/runs/P7-authorized-clean-noop-20260814/human_checkpoint_quit_retry_v3.json`: the user reports `Quit` ineffective; the exact PID was absent on the post-report probe, but termination timing was not observed, so the result is `PARTIAL/HUMAN_REQUIRED`, not a proven root cause. No save mutation occurred.
- The user explicitly authorized one disposable character-data persistence test for `C5_L2_LOCALIZED`; `10_logs/P7-persistence-track-20260814/authorization_granted_c5_l2_persistence_20260814.json` binds that scope to the C5-L2 EXE/DLL hashes. The authorization gate itself performed no mutation; the fixed name is `P7_ORIGINAL_20260814`, and creation/restart/cleanup evidence is pending.
- The current status evidence index audit is saved at `10_logs/status_evidence_integrity_20260814.json`: all 93 JSON evidence paths indexed by `status.json` are present and parseable as UTF-8. PowerShell evidence readers must specify UTF-8; a default-encoding parse error is not evidence corruption.
- The v19 ffmpeg/gdigrab control experiment produced byte-identical TraceMemo frames for the known C2 control and C5-L1 candidate; it is `INCONCLUSIVE_FOR_VISUAL_CONTENT` and is not visual proof.
- The historical C3 retry worktree is forensic only because its patch report used the dirty root `06_worktree`; the replacement clean C3 build starts from `03_raw`. Its final EXE is byte-identical to the historical final EXE, and `visual_evidence_review.json` binds the reviewed screenshot to that SHA without reusing the old worktree.
- `04_recovered/` and the root `06_worktree/` contain pre-existing modifications and are not canonical production inputs; production evidence must continue from immutable/reference inputs and isolated generated worktrees.

## Historical trusted facts

### Original

```text
SHA-256:
C7B5D5A529CD776609F72730662F1F6A8049FE5DE20541F7EAFE06D0F2451209

size:
103290320 bytes

engine:
Godot 3.5.3 custom_build

PCK:
v1

raw PCK entries:
3744
```

### Raw recovery

`03_raw` has been extracted with the expected 3744 runtime paths and validated as the immutable runtime baseline.

Script encryption/decryption has been demonstrated with a verified key/method; the key itself must remain secret.

### Packaging

A project-specific embedded PCK offset error was isolated and corrected.

The accepted infrastructure behavior is:

- standalone PCK entries are transformed appropriately for the embedded EXE layout;
- embedded offsets resolve to the intended runtime bytes;
- PCK trailer and PE `pck` section are validated;
- final path/content inventories are validated;
- a real `Mutagenic` window with no `ALERT!` is required.

Packaging is therefore a **trusted subsystem unless a future packaging Gate fails**.

Do not reopen packaging design merely because a feature/localization build has a gameplay regression.

### Clean NOOP

Current CLEAN NOOP:

```text
SHA-256:
94A53EF47AC49CF2F13157905387932BB517F648A15B7A0200B098237F0015DA
```

It has passed structural validation and human basic-function comparison against the original.

Original and CLEAN NOOP both have otherwise normal core behavior for the tested flow.

### Baseline Quit behavior

Human testing observed that Quit is not working as expected in both ORIGINAL and CLEAN NOOP under the tested launch conditions.

Therefore Quit is currently a **separate baseline/environment/persistence track**, not evidence that localization caused a regression.

Save persistence must remain independently classified until directly tested.

### Failed modified build

The previous heavily modified candidate:

```text
SHA-256:
64C0BA41DE75A029759A9D6E74E7BBC6C747032B2A8DA7A60C8CAB83889F788C
```

is structurally valid but functionally regressed in human testing, including symptoms such as:

- `Null` in character/class UI;
- blank button labels;
- `Start Game` crash.

This build is **forensic evidence only**.

Do not repair it forward and do not use it as a production base.

Its diffs may be mined to recover intended translation/mod work, but each intended change must be re-expressed as a declarative patch and reintroduced from a trusted baseline.

### Script capability

At least one zero-change encrypted-script roundtrip has produced a byte-identical original `.gde`, proving the mechanism for that specific sample.

This does **not** yet prove the entire script population or every complex script is lossless.

## Current program phase

> The milestone text in this subsection is historical provenance. It is superseded by the Current evidence override above, which records the current phase as `PHASE_6_INCREMENTAL_MOD_LOCALIZATION_INTEGRATION`.

The project is now in:

```text
PHASE 3 — CAPABILITY QUALIFICATION
```

The next strategic objective is **not** to chase individual symptoms in the failed modified candidate.

The next strategic objective is to finish qualifying the transformation capabilities and then rebuild the Mod/localization system from CLEAN NOOP using declarative, minimal overlays.

Recommended program order:

```text
1. finish representative script-pipeline qualification
2. prove ONE-VALUE
3. prove ONE-CODE
4. prove ONE-RESOURCE
5. prove ONE-ASSET
6. establish Game Schema + declarative Mod manifests
7. rebuild localization as safe manifest-defined batches
8. run core functional regressions after each integration milestone
9. investigate Quit/save/Steam as an independent baseline track
10. release only after complete structural + functional + visual acceptance
```

This order is more important than any particular single-script investigation.

---

# 31. Program-Level Roadmap

## Stage A — Stabilize foundations

Expected result:

- immutable baseline complete;
- recovery reproducible;
- packaging frozen and reliable;
- CLEAN NOOP is the golden runtime control.

Current state: substantially achieved.

## Stage B — Qualify transformations

Expected result:

- script changes can be produced safely;
- value/resource/asset changes are independently supported;
- tests identify transformation-layer regressions.

Current state: active.

## Stage C — Build the Mod SDK abstraction

Expected result:

- Game Schema;
- Mod manifest format;
- deterministic patch engine;
- generated worktrees;
- delta manifests;
- reusable validation commands.

## Stage D — Rebuild localization correctly

Expected result:

- structural/user-facing classification;
- safe translation unit extraction;
- versioned glossary;
- controlled font support;
- translation patches applied only to eligible fields;
- incremental integration with regression Gates.

The historical broad translation tree may supply translation content, but it is not a trusted production source tree.

## Stage E — Functional hardening

Expected result:

- main-menu/character/start-game smoke tests;
- representative gameplay transitions;
- save persistence characterization;
- Quit/Steam/local-save behavior characterized;
- crash evidence collection standardized.

## Stage F — Release

Expected result:

- deterministic rebuild from immutable inputs;
- explainable changed-file set;
- final full extraction PASS;
- runtime PASS;
- localization visual QA PASS;
- license/security review;
- release notes and evidence bundle.

---

# 32. Definition of Engineering Completion

The first production-quality SDK/localization program is complete only when all of the following are true:

- pristine original is preserved and fingerprinted;
- raw extraction is deterministic and checksum-valid;
- recovery/reference source is documented;
- script bytecode/encryption path is verified;
- CLEAN NOOP passes structure and representative runtime behavior;
- data/code/resource/asset capability milestones pass;
- Game Schema is machine-readable to a useful level;
- Mod manifests define all production changes;
- worktrees are generated from immutable inputs;
- untouched runtime files remain byte-identical to raw baseline;
- compiled paths are preserved;
- modified encrypted scripts are generated reproducibly;
- PCK/EXE build is deterministic and validated;
- final EXE can be fully re-extracted;
- changed-file set equals the declared Mod delta;
- core functional smoke tests pass;
- baseline behaviors are distinguished from Mod regressions;
- localization text is structurally safe;
- fonts/assets pass structural and visual validation;
- secrets and licenses are handled appropriately;
- state/evidence allow a new agent to resume without chat history;
- a release can be recreated from clean inputs using the documented command interface.

The game merely starting is not completion.

A large percentage of translated strings is not completion.

A successful compiler exit code is not completion.

A failed Gate with clear evidence is preferable to an apparently working but untraceable build.

---

# 33. Session Start Protocol for Every Future Agent

At the beginning of every new session:

1. read this entire `AGENTS.md`;
2. read `10_logs/status.json`;
3. read the current `PROJECT_STATE.md` summary;
4. verify the original fingerprint has not changed;
5. verify the tool lock has not changed unexpectedly;
6. identify the first incomplete/failed Gate in the current program phase;
7. inspect the latest evidence bundle for that Gate;
8. state the project-level objective for the session;
9. define the acceptance test before making changes;
10. proceed without unnecessary human interruption until a real `HUMAN_REQUIRED` checkpoint is reached; record the checkpoint and continue with non-human-dependent work. `HUMAN_REQUIRED` alone is not an active blocker.

Do not inherit an old TODO list blindly if it conflicts with current Gate state.

Do not begin by editing the last file mentioned in chat.

---

# 34. Session End / Handoff Protocol

Before ending a meaningful engineering session, update:

```text
10_logs/status.json
PROJECT_STATE.md
```

and create/update an evidence bundle.

The handoff must state:

```text
CURRENT_PHASE
CURRENT_TRUSTED_BASELINE
GATES_CHANGED_THIS_SESSION
VERIFIED_FACTS
FAILED_GATES
OPEN_HYPOTHESES
ACTIVE_BLOCKERS
ARTIFACT_PATHS_AND_HASHES
NEXT_PROGRAM_OBJECTIVE
DO_NOT_REPEAT
HUMAN_REQUIRED (if any)
```

Human checkpoints must be listed separately from `ACTIVE_BLOCKERS`. A pending or completed human checkpoint is not an active blocker unless the user has explicitly made that human verdict a release-condition for the exact artifact under discussion.

Do not leave the next agent with prose such as “continue debugging”.

The next program objective must be tied to a Gate and an acceptance condition.

---

# 35. Final Operating Principle

When choosing between:

```text
A. a fast patch that makes the current contaminated build look better
```

and:

```text
B. a slower step that makes the pipeline reproducible, isolates a subsystem,
   and leaves a trustworthy baseline for all later Mods
```

choose **B**.

The purpose of this repository is not to accumulate fixes.

The purpose is to create a system in which every future fix, translation, and Mod can be introduced deliberately, tested independently, reproduced from clean inputs, and rolled back without guesswork.
