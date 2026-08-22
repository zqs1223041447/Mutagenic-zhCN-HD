#!/usr/bin/env python3
"""Mutagenic portable batch controller - one command, one intent.

Runs from ANY working directory inside a clone (main tree or a linked task
worktree); every path is derived from the repo at runtime - no host absolute
paths (AGENTS.md 9).

Commands:
  claim    B1-X1      claim a task: create branch + Git worktree (idempotent)
  status   B1         show task states for a batch (or one task)
  handoff  B1-X1      collect structured handoff report (writes YAML + prints)
  collect  B1         aggregate all handoffs of a batch
  preflight B1        integration preflight: base/diff/scans/immutable/conflicts
  cleanup  B1-X1      remove a task worktree (fail-closed on unknown/unmerged/dirty)
  scan-paths ...      repo-wide absolute-path scan (see abs_path_scan.py)
  scan-secrets ...    repo-wide secret scan, redacted (see secret_scan.py)

Fail-closed cleanup semantics (docs/ai/PARALLEL_BATCH_WORKFLOW.md 3/8):
  * unknown directory at the task path  -> always refused
  * uncommitted (dirty) worktree         -> refused unless --force
  * not provably merged into integration -> refused unless --allow-unmerged
  * worktree registered under another branch -> refused
Only cleanup of proven-merged, clean worktrees is automatic.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import abs_path_scan
import check_all
import secret_scan
from repo_util import (RepoError, claim_lock_path, default_branch, find_main_repo_root,
                       find_repo_root, find_worktree, git, is_merged, ref_exists, ref_sha,
                       split_task, task_dir, tracked_files, worktree_list, worktrees_root)

IMMUTABLE_PREFIXES = ("00_original/", "03_raw/", "04_recovered/")
INTEGRATION_BRANCH = "agent/kinetic-arcane-remaster-foundation"


def _anchor_ref(batch: str) -> str:
    return f"batch/{batch.lower()}-anchor"


def _short(sha7_or_full: str | None, n: int = 12) -> str:
    return (sha7_or_full or "?")[:n]


# ---------------------------------------------------------------- yaml mini
def _yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if not s or any(ch in s for ch in "\n") or s != s.strip() or s[0] in "#-?:,[]{}&*!|>'\"%@`" or ": " in s:
        return json.dumps(s, ensure_ascii=False)
    return s


def _yaml_dump(obj, indent: int = 0) -> str:
    pad = "  " * indent
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict) and v:
                out.append(f"{pad}{k}:")
                out.append(_yaml_dump(v, indent + 1))
            elif isinstance(v, list):
                if not v:
                    out.append(f"{pad}{k}: []")
                else:
                    out.append(f"{pad}{k}:")
                    for it in v:
                        if isinstance(it, dict):
                            out.append(f"{pad}  -")
                            out.append(_yaml_dump(it, indent + 3))
                        else:
                            out.append(f"{pad}  - {_yaml_scalar(it)}")
            else:
                out.append(f"{pad}{k}: {_yaml_scalar(v)}")
    elif isinstance(obj, list):
        for it in obj:
            out.append(f"{pad}- {_yaml_scalar(it)}")
    else:
        out.append(f"{pad}{_yaml_scalar(obj)}")
    return "\n".join(out)


def _yaml_load(text: str) -> dict:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        lines.append((len(raw) - len(raw.lstrip()), raw.strip()))

    def parse_block(start: int, indent: int) -> tuple[dict, int]:
        result: dict = {}
        i = start
        while i < len(lines):
            ind, content = lines[i]
            if ind < indent:
                break
            if ind > indent or content.startswith("- "):
                raise RepoError(f"bad yaml block indent at {content!r}")
            if ":" not in content or content.startswith(('"', "'")):
                i += 1
                continue
            key, _, val = content.partition(":")
            key = key.strip()
            if val.strip():
                result[key] = _yaml_parse(val.strip())
                i += 1
                continue
            if i + 1 < len(lines) and lines[i + 1][0] > indent:
                nind = lines[i + 1][0]
                if lines[i + 1][1].startswith("- "):
                    lst, ni = parse_list(i + 1, nind)
                    result[key] = lst
                    i = ni
                else:
                    d, ni = parse_block(i + 1, nind)
                    result[key] = d
                    i = ni
            else:
                result[key] = {}
                i += 1
        return result, i

    def parse_list(start: int, indent: int) -> tuple[list, int]:
        lst: list = []
        i = start
        while i < len(lines):
            ind, content = lines[i]
            if ind < indent:
                break
            if not content.startswith("- "):
                break
            rest = content[2:].strip()
            if ":" in rest and not rest.startswith(('"', "'")):
                k, _, v = rest.partition(":")
                key = k.strip()
                item: dict = {key: _yaml_parse(v.strip())}
                if i + 1 < len(lines) and lines[i + 1][0] > indent:
                    nind = lines[i + 1][0]
                    if lines[i + 1][1].startswith("- "):
                        item[key], i = parse_list(i + 1, nind)
                    else:
                        item[key], i = parse_block(i + 1, nind)
                else:
                    i += 1
                lst.append(item)
            else:
                lst.append(_yaml_parse(rest))
                i += 1
        return lst, i

    parsed, _ = parse_block(0, 0)
    return parsed


def _yaml_parse(s: str):
    if not s:
        return ""
    if s == "null":
        return None
    if s.startswith('"') and s.endswith('"'):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return s
    if s.startswith("[") and s.endswith("]"):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return s
    if s.isdigit():
        return int(s)
    if s.startswith("- ") or s == "-":
        return ""
    return s


# ---------------------------------------------------------------- helpers
def _task_state(tw_dir: Path) -> dict:
    entry = find_worktree(tw_dir)
    if entry is None:
        return {"worktree": str(tw_dir), "registered": False}
    state = {
        "worktree": str(tw_dir),
        "registered": True,
        "branch": entry.get("branch"),
        "head": entry.get("head", "?"),
        "detached": bool(entry.get("detached")),
    }
    if entry.get("branch"):
        try:
            r = git("status", "--porcelain", cwd=str(tw_dir))
            state["dirty_files"] = len([l for l in r.stdout.splitlines() if l])
        except RepoError:
            state["dirty_files"] = None
        try:
            up = git("rev-list", "--count", f"origin/{entry['branch']}..HEAD", cwd=str(tw_dir), check=False)
            state["ahead"] = int(up.stdout.strip() or 0)
        except RepoError:
            state["ahead"] = None
        try:
            dn = git("rev-list", "--count", f"HEAD..origin/{entry['branch']}", cwd=str(tw_dir), check=False)
            state["behind"] = int(dn.stdout.strip() or 0)
        except RepoError:
            state["behind"] = None
    return state


def _scan_changed(root: Path, changed: list[str]) -> dict:
    path_hits = abs_path_scan.scan_files(root, changed)
    secret_hits = secret_scan.scan_files(root, changed)
    return {
        "path_scan": abs_path_scan.summarize(path_hits),
        "path_failures": [h for h in path_hits if h["severity"] == "FAIL"],
        "secret_findings": secret_hits,
    }


# ---------------------------------------------------------------- claim lock
class ClaimLock:
    """O_EXCL lock in the git common dir: two concurrent `claim` runs for the
    same batch cannot both pass the check-then-create window (B2-X3: 并发
    claim 冲突). A stale lock (older than stale_seconds) is broken once so an
    unattended run cannot hang forever on a crashed predecessor."""

    def __init__(self, main, stale_seconds: int = 300):
        self.lock_path = claim_lock_path(main)
        self.stale_seconds = stale_seconds

    def __enter__(self):
        for attempt in range(2):
            try:
                fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w") as fh:
                    fh.write(f"{os.getpid()}\n{time.time()}\n")
                return self
            except FileExistsError:
                age = time.time() - self.lock_path.stat().st_mtime
                if attempt == 0 and age > self.stale_seconds:
                    try:
                        self.lock_path.unlink()
                    except OSError:
                        pass
                    continue
                raise RepoError(
                    f"claim: another claim is in progress (lock {self.lock_path}, age {int(age)}s); "
                    "retry later, or remove the lock file if it is stale")

    def __exit__(self, *exc):
        try:
            self.lock_path.unlink()
        except OSError:
            pass
        return False


# ---------------------------------------------------------------- claim
def cmd_claim(args) -> int:
    main = find_main_repo_root()
    base_dir = Path(args.worktrees_root) if args.worktrees_root else worktrees_root()
    batch, task = split_task(args.task)
    tw_dir = base_dir / batch / task
    branch = args.branch or default_branch(args.task, args.name)

    base = args.base
    if base is None:
        base = _anchor_ref(batch)
        if not ref_exists(base, main):
            head = ref_sha("HEAD", main)
            base = head or "HEAD"
    if not ref_exists(base, main):
        print(f"claim {args.task}: base ref {base!r} does not resolve", file=sys.stderr)
        return 2

    base_sha = ref_sha(base, main)
    if args.dry_run:
        plan = [f"git worktree add {tw_dir} {branch}"] if ref_exists(branch, main) \
            else [f"git worktree add -b {branch} {tw_dir} {base}"]
        print(f"claim {args.task} (DRY-RUN, nothing executed):")
        for p in plan:
            print(f"  git -C {main} {p}")
        print(f"  base_sha = {base_sha}")
        return 0

    with ClaimLock(main):
        registry = worktree_list(main)
        existing = find_worktree(tw_dir, main)
        if existing is not None:
            eb = existing.get("branch")
            if args.branch and eb and eb != args.branch:
                print(f"claim {args.task}: task dir already hosts branch {eb} (requested {args.branch})",
                      file=sys.stderr)
                return 2
            print(f"claim {args.task}: already claimed (idempotent)")
            print(f"  branch    : {eb or '[detached]'}")
            print(f"  worktree  : {existing['path']}")
            print(f"  head      : {_short(existing.get('head'))}")
            return 0
        if tw_dir.exists():
            print(f"claim {args.task}: directory exists but is NOT a registered git worktree - "
                  "refusing to touch unknown state (fail-closed)", file=sys.stderr)
            return 2

        other = [e for e in registry if e.get("branch") == branch and e["path"] != tw_dir]
        if other:
            print(f"claim {args.task}: branch {branch} already checked out at {other[0]['path']}",
                  file=sys.stderr)
            return 2

        tw_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            if ref_exists(branch, main):
                git("worktree", "add", str(tw_dir), branch, cwd=main)
            else:
                git("worktree", "add", "-b", branch, str(tw_dir), base, cwd=main)
        except RepoError as e:
            print(f"claim {args.task}: git worktree add failed: {e}", file=sys.stderr)
            print("  hint: 并发 claim 占用（branch/目录已被其他任务使用）或路径不可写；"
                  "先运行 'batchctl status <batch>' 检查后重试", file=sys.stderr)
            return 2
    head = ref_sha("HEAD", tw_dir)
    print(f"claim {args.task}: OK")
    print(f"  branch    : {branch}")
    print(f"  worktree  : {tw_dir}")
    print(f"  base_sha  : {base_sha}")
    print(f"  head      : {_short(head)}")
    return 0


# ---------------------------------------------------------------- status
def cmd_status(args) -> int:
    main = find_main_repo_root()
    base_dir = Path(args.worktrees_root) if args.worktrees_root else worktrees_root()
    target = args.target
    try:
        batch, task = split_task(target)
        dirs = [base_dir / batch / task]
        label = target
    except RepoError:
        batch = target
        dirs = sorted(p for p in (base_dir / batch).glob("*") if p.is_dir())
        label = f"batch {batch}"
    anchor = _anchor_ref(batch)
    anchor_sha = ref_sha(anchor, main)
    integration = INTEGRATION_BRANCH if ref_exists(INTEGRATION_BRANCH, main) else None

    rows = []
    for tw_dir in dirs:
        st = _task_state(tw_dir)
        row = {"task": tw_dir.name, **st}
        branch = st.get("branch")
        if branch:
            row["base_is_anchor"] = bool(anchor_sha and ref_exists(branch, main)
                                         and is_merged(anchor_sha, branch, main))
            if integration:
                row["merged_into_integration"] = is_merged(branch, integration, main)
        handoff = base_dir / batch / "handoffs" / f"{tw_dir.name}.yaml"
        row["handoff"] = handoff.exists()
        rows.append(row)

    if args.json:
        print(json.dumps({"batch": batch, "anchor": anchor_sha, "tasks": rows}, indent=1, ensure_ascii=False))
        return 0

    print(f"status {label}  (anchor {_anchor_ref(batch)}={_short(anchor_sha)})")
    if not rows:
        print("  no claimed task worktrees under", base_dir / batch)
        return 0
    for r in rows:
        head = _short(r.get("head"))
        dirty = r.get("dirty_files")
        dirty_s = "clean" if dirty == 0 else f"DIRTY({dirty})" if dirty else "?"
        ahead = r.get("ahead")
        behind = r.get("behind")
        track = f"ahead {ahead}/behind {behind}" if ahead is not None and behind is not None else "no upstream"
        merged = f"merged={r.get('merged_into_integration')}" if "merged_into_integration" in r else ""
        print(f"  {r['task']:8s} {r.get('branch') or '[detached]':44s} {head} "
              f"{dirty_s} {track} base_is_anchor={r.get('base_is_anchor')} {merged} handoff={'yes' if r.get('handoff') else 'no'}")
    return 0


# ---------------------------------------------------------------- handoff
def _build_handoff(state: dict, task: str) -> dict:
    batch, _ = split_task(task)
    branch = state.get("branch")
    anchor_sha = ref_sha(_anchor_ref(batch))
    head_sha = state.get("head")
    changed = []
    commits = []
    if branch:
        base = anchor_sha or ref_sha(f"origin/{branch}") or ref_sha("HEAD~1")
        if base:
            out = git("diff", "--name-status", base, head_sha, cwd=str(state["worktree"]), check=False)
            changed = [l for l in out.stdout.splitlines() if l]
            out = git("log", "--oneline", "--no-decorate", f"{base}..{head_sha}", cwd=str(state["worktree"]), check=False)
            commits = [l for l in out.stdout.splitlines() if l]
    dirty = []
    if branch:
        out = git("status", "--porcelain", cwd=str(state["worktree"]), check=False)
        dirty = [l for l in out.stdout.splitlines() if l]
    return {
        "task_id": task,
        "batch": batch,
        "branch": branch,
        "worktree": str(state["worktree"]),
        "base_sha": anchor_sha,
        "final_sha": head_sha,
        "commits_since_base": [c.split(" ", 1)[0] for c in commits],
        "changed_files": changed,
        "uncommitted": dirty,
        "ahead": state.get("ahead"),
        "behind": state.get("behind"),
    }


def cmd_handoff(args) -> int:
    root = find_repo_root()
    main = find_main_repo_root()
    base_dir = Path(args.worktrees_root) if args.worktrees_root else worktrees_root()
    batch, task = split_task(args.task)
    tw_dir = base_dir / batch / task
    state = _task_state(tw_dir)

    if args.template:
        report = {
            "task_id": args.task, "batch": batch, "branch": "agent/<batch>-<task>",
            "worktree": "<task worktree path>", "base_sha": "<anchor sha>",
            "final_sha": "<HEAD sha>", "commits_since_base": [], "changed_files": [],
            "uncommitted": [], "ahead": 0, "behind": 0,
            "verification_exit_code": 0,
            "scans": {"path_production_hardcode": 0, "secret_findings": 0},
            "verification": {"S0": "NOT_RUN", "S1": "NOT_RUN", "S2": "NOT_RUN",
                             "S4": "NOT_RUN", "S5": "NOT_RUN"},
            "not_run_or_blocked": [], "retries_and_fixes": [],
            "potential_conflict_paths": [], "remaining_risks": [],
            "push_status": "NOT_PUSHED",
        }
    else:
        report = _build_handoff(state, args.task)
        report["verification_exit_code"] = args.exit_code
        if args.summary:
            report["summary"] = args.summary
        if state.get("registered") and state.get("branch"):
            changed = [c.split("\t", 1)[-1] for c in report["changed_files"] if "\t" in c]
            changed += [c[3:] for c in report["uncommitted"] if len(c) > 3]
            changed = list(dict.fromkeys(changed))
            scans = _scan_changed(root, changed)
            report["scans"] = {
                "path_hits": scans["path_scan"],
                "path_production_hardcode": len(scans["path_failures"]),
                "secret_findings": len(scans["secret_findings"]),
            }
            report["verification"] = {"S0": "NOT_RUN", "S1": "NOT_RUN", "S2": "NOT_RUN",
                                      "S4": "NOT_RUN", "S5": "NOT_RUN"}
            report["not_run_or_blocked"] = ["S0-S5 runtime/build gates not run by batchctl (requires local 00_original + pipeline)"]
            report["retries_and_fixes"] = []
            report["potential_conflict_paths"] = sorted({
                f for f in changed
                if f.startswith(tuple(("scripts/", "mods/", "docs/ai/", "manifests/")))})
            upstream = f"origin/{report['branch']}" if report.get("branch") else None
            report["push_status"] = (f"ahead {report['ahead']}/behind {report['behind']} vs {upstream}"
                                     if upstream and report.get("ahead") is not None else "NO_UPSTREAM")
        else:
            report["scans"] = {}
            report["verification"] = {}
            report["not_run_or_blocked"] = [f"task worktree not found at {tw_dir}"]
            report["push_status"] = "NOT_CLAIMED"

    text = _yaml_dump(report)
    out_path = args.out or (base_dir / batch / "handoffs" / f"{task}.yaml")
    if args.dry_run:
        print(f"handoff {args.task} (DRY-RUN, report not written):")
        print(text)
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"--- handoff {args.task} written to {out_path}")
    return 0


# ---------------------------------------------------------------- collect
def _normalize_exit(code) -> int | None:
    if isinstance(code, bool):
        return None
    if isinstance(code, int):
        return code
    if isinstance(code, str) and code.strip().lstrip("-").isdigit():
        return int(code.strip())
    return None


def cmd_collect(args) -> int:
    base_dir = Path(args.worktrees_root) if args.worktrees_root else worktrees_root()
    handoffs_dir = base_dir / args.batch / "handoffs"
    gathered: list[dict] = []
    missing: list[str] = []
    incomplete: list[str] = []
    if handoffs_dir.is_dir():
        for f in sorted(handoffs_dir.glob("*.yaml")):
            try:
                data = _yaml_load(f.read_text(encoding="utf-8"))
                gathered.append(data)
                code = _normalize_exit(data.get("verification_exit_code"))
                if code is not None and code != 0:
                    incomplete.append(f"{f.stem}: declared verification exit_code {code} (non-zero)")
            except Exception as e:
                missing.append(f"{f.name}: unreadable ({e})")
    for e in worktree_list():
        rel = Path(e["path"]).resolve()
        if rel.parent.parent == base_dir.resolve() and rel.parent.name == args.batch:
            task = rel.name
            if not (handoffs_dir / f"{task}.yaml").exists():
                missing.append(f"{task}: claimed, no handoff")
    verdict = "FAIL" if (missing or incomplete) else "PASS"
    rc = 1 if (missing or incomplete) else 0
    if args.json:
        print(json.dumps({"batch": args.batch, "verdict": verdict, "handoffs": gathered,
                          "missing": missing, "incomplete": incomplete, "exit_code": rc},
                         indent=1, ensure_ascii=False))
        return rc
    print(f"collect {args.batch}: {len(gathered)} handoff(s) verdict={verdict}")
    for h in gathered:
        code = h.get("verification_exit_code", "?")
        print(f"  {str(h.get('task_id') or '?'):8s} {h.get('branch') or '?':44s} base={_short(h.get('base_sha'))} "
              f"head={_short(h.get('final_sha'))} files={len(h.get('changed_files') or [])} "
              f"push={h.get('push_status', '?')} verify_exit={code}")
    if missing:
        print("missing:")
        for m in missing:
            print(f"  - {m}")
    if incomplete:
        print("incomplete:")
        for m in incomplete:
            print(f"  - {m}")
    return rc


# ---------------------------------------------------------------- preflight
def cmd_preflight(args) -> int:
    main = find_main_repo_root()
    base_dir = Path(args.worktrees_root) if args.worktrees_root else worktrees_root()
    batch = args.batch
    anchor = _anchor_ref(batch)
    anchor_sha = ref_sha(anchor, main)
    if not anchor_sha:
        print(f"preflight {batch}: anchor {anchor} not found (run git fetch)", file=sys.stderr)
        return 2

    tasks = [d for d in sorted((base_dir / batch).glob("*")) if d.is_dir()]
    failures: list[str] = []
    warnings: list[str] = []
    conflict_map: dict[str, list[str]] = {}

    for tw_dir in tasks:
        task = tw_dir.name
        st = _task_state(tw_dir)
        branch = st.get("branch")
        if not st.get("registered") or not branch:
            warnings.append(f"{task}: not a registered claim or detached - skipped")
            continue
        if not is_merged(anchor_sha, branch, main):
            failures.append(f"{task}: branch base is NOT anchored on {anchor}")
        head_sha = st.get("head")
        out = git("diff", "--name-only", anchor_sha, head_sha, cwd=str(tw_dir), check=False)
        changed = [l for l in out.stdout.splitlines() if l]
        out = git("status", "--porcelain", cwd=str(tw_dir), check=False)
        dirty = [l for l in out.stdout.splitlines() if l]
        untracked = [l[3:] for l in dirty if l.startswith("?? ")]
        for f in changed:
            if f.startswith(IMMUTABLE_PREFIXES):
                failures.append(f"{task}: touches immutable {f}")
        for f in untracked:
            if f.startswith(("00_original/",)):
                failures.append(f"{task}: writes into 00_original ({f})")
        for f in changed + [l[3:] for l in dirty if len(l) > 3 and not l.startswith("?? ")]:
            conflict_map.setdefault(f, []).append(task)
        if st.get("dirty_files"):
            warnings.append(f"{task}: worktree dirty ({st['dirty_files']} files) - uncommitted work")
        scan = _scan_changed(main, changed)
        if scan["path_failures"]:
            failures.append(f"{task}: production hardcode in changed files:")
            for h in scan["path_failures"]:
                failures.append(f"    {h['file']}:{h['line']} value={h['matched']}")
        if scan["secret_findings"]:
            failures.append(f"{task}: secret findings in changed files (n={len(scan['secret_findings'])}, redacted)")
        warnings.append(f"{task}: path hits {scan['path_scan']}, changed files {len(changed)}")

    for f, ts in sorted(conflict_map.items()):
        if len(ts) > 1:
            warnings.append(f"conflict graph: {f} touched by {', '.join(ts)}")

    ok = not failures
    print(f"preflight {batch}: {'PASS' if ok else 'FAIL'}")
    for w in warnings:
        print(f"  [WARN] {w}")
    for f in failures:
        print(f"  [FAIL] {f}")
    print(f"anchor={anchor} sha={anchor_sha} tasks={len(tasks)} failures={len(failures)}")
    return 0 if ok else 1


# ---------------------------------------------------------------- cleanup
def cmd_cleanup(args) -> int:
    main = find_main_repo_root()
    base_dir = Path(args.worktrees_root) if args.worktrees_root else worktrees_root()
    batch, task = split_task(args.task)
    tw_dir = base_dir / batch / task

    entry = find_worktree(tw_dir, main)
    if entry is None:
        if tw_dir.exists():
            print(f"cleanup {args.task}: directory exists but is not a registered worktree - "
                  "unknown state, refused (fail-closed); review manually", file=sys.stderr)
            return 2
        print(f"cleanup {args.task}: nothing to do (no worktree at {tw_dir})")
        return 0
    branch = entry.get("branch")
    if not branch or entry.get("detached"):
        print(f"cleanup {args.task}: worktree is detached/unknown state - refused (fail-closed)", file=sys.stderr)
        return 2
    r = git("status", "--porcelain", cwd=str(tw_dir), check=False)
    dirty = [l for l in r.stdout.splitlines() if l]
    if dirty and not args.force:
        print(f"cleanup {args.task}: worktree is dirty ({len(dirty)} files) - refused; "
              "commit/merge elsewhere first, or pass --force to discard uncommitted data", file=sys.stderr)
        return 2
    integration = args.merged_into
    if integration and not ref_exists(integration, main):
        print(f"cleanup {args.task}: --merged-into ref {integration} not found", file=sys.stderr)
        return 2
    merged = False
    if integration:
        merged = is_merged(branch, integration, main)
    elif ref_exists(INTEGRATION_BRANCH, main):
        merged = is_merged(branch, INTEGRATION_BRANCH, main)
    if not merged and not args.allow_unmerged:
        print(f"cleanup {args.task}: branch {branch} is not provably merged into "
              f"{integration or INTEGRATION_BRANCH or '<integration line>'} - refused; "
              "verify central integration first, or pass --allow-unmerged", file=sys.stderr)
        return 2
    already_merged_ref = integration or (INTEGRATION_BRANCH if ref_exists(INTEGRATION_BRANCH, main) else None)

    plan = [f"git worktree remove {tw_dir}{' --force' if args.force else ''}"]
    if args.delete_branch:
        plan.append(f"git branch -{'D' if args.force else 'd'} {branch}")
    if args.dry_run:
        print(f"cleanup {args.task} (DRY-RUN, nothing executed):")
        for p in plan:
            print(f"  git -C {main} {p}")
        return 0
    git("worktree", "remove", *(("--force",) if args.force else ()), str(tw_dir), cwd=main)
    if args.delete_branch:
        git("branch", *("-D" if args.force else "-d"), branch, cwd=main)
    print(f"cleanup {args.task}: removed worktree {tw_dir}" +
          (f" (branch {branch} deleted)" if args.delete_branch else
           f" (branch {branch} kept)"))
    return 0


# ---------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("claim", help="claim a task: create branch + worktree")
    p.add_argument("task")
    p.add_argument("--name", help="short semantic name appended to branch (agent/<b>-<t>-<name>)")
    p.add_argument("--branch", help="explicit branch name (default agent/<batch>-<task>[-<name>])")
    p.add_argument("--base", help="base ref (default batch/<batch>-anchor, else main HEAD)")
    p.add_argument("--worktrees-root", help="override derived .worktrees root (testing/advanced)")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_claim)

    p = sub.add_parser("status", help="task status for a batch or one task")
    p.add_argument("target", help="batch id (B1) or task id (B1-X1)")
    p.add_argument("--worktrees-root")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("handoff", help="collect structured handoff report")
    p.add_argument("task")
    p.add_argument("--template", action="store_true", help="print empty template only")
    p.add_argument("--exit-code", type=int, default=0, help="declare verification exit code in report")
    p.add_argument("--summary", help="one-line summary recorded in the report")
    p.add_argument("--out", help="output file (default <worktrees_root>/<batch>/handoffs/<task>.yaml)")
    p.add_argument("--worktrees-root")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_handoff)

    p = sub.add_parser("collect", help="aggregate batch handoffs")
    p.add_argument("batch")
    p.add_argument("--worktrees-root")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_collect)

    p = sub.add_parser("preflight", help="integration preflight for a batch")
    p.add_argument("batch")
    p.add_argument("--worktrees-root")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_preflight)

    p = sub.add_parser("cleanup", help="remove a task worktree (fail-closed)")
    p.add_argument("task")
    p.add_argument("--worktrees-root")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--merged-into", help="integration ref that must contain the task branch")
    p.add_argument("--allow-unmerged", action="store_true", help="explicitly allow unmerged branch cleanup")
    p.add_argument("--force", action="store_true", help="explicitly allow discarding uncommitted changes")
    p.add_argument("--delete-branch", action="store_true")
    p.set_defaults(fn=cmd_cleanup)

    p = sub.add_parser("scan-paths", help="repo-wide absolute-path scan (see abs_path_scan.py)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--include-untracked", action="store_true")
    p.add_argument("--changed-in", metavar="REF")
    p.add_argument("--fail-on", default="FAIL", choices=("FAIL", "WARN", "INFO", "NEVER"))
    p.set_defaults(fn=lambda a: abs_path_scan.main(
        [*(["--json"] if a.json else ["--fail-on", a.fail_on]),
         *(["--include-untracked"] if a.include_untracked else []),
         *(["--changed-in", a.changed_in] if a.changed_in else [])]))

    p = sub.add_parser("scan-secrets", help="repo-wide redacted secret scan (see secret_scan.py)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--include-untracked", action="store_true")
    p.add_argument("--scan-ignored", action="store_true")
    p.add_argument("--changed-in", metavar="REF")
    p.set_defaults(fn=lambda a: secret_scan.main([
        *(["--json"] if a.json else []),
        *(["--include-untracked"] if a.include_untracked else []),
        *(["--scan-ignored"] if a.scan_ignored else []),
        *(["--changed-in", a.changed_in] if a.changed_in else []),
    ]))

    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except RepoError as e:
        print(f"batchctl: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())