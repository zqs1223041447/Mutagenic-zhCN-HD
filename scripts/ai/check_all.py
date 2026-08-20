#!/usr/bin/env python3
"""Unified machine preflight/check entry (B2-X3).

Runs every repository-level verification gate the batch control plane
depends on, in one command with stable exit codes:

  EXIT 0  PASS      - every registered component that ran passed
  EXIT 1  FAIL      - at least one component failed
  EXIT 2  USAGE     - invalid arguments / unreadable registry / not a repo
  EXIT 3  NOT_RUN   - all components that ran passed, but at least one
                      registered component was NOT RUN (e.g. a contract
                      that is integrated by a later task)

Components are declared in ``scripts/ai/check_all_components.json``
(repo-relative). A later task integrates a new contract simply by adding
its entry file; the registry already carries the hook (e.g. the B2-X1
combat event spine contract, NOT RUN until X1 lands).

Report contract (``--json`` / ``--out``): see _report_shape in
``scripts/ai/tests/test_check_all.py``.

Usage (from any repo path):
    python scripts/ai/check_all.py [--json] [--out <path>] [--registry <path>]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from repo_util import RepoError, find_repo_root, git, ref_sha

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_NOT_RUN = 3

DEFAULT_REGISTRY = "scripts/ai/check_all_components.json"
STDOUT_TAIL_CHARS = 8000


def load_registry(root: Path, registry_path: str | Path | None = None) -> dict:
    path = (Path(registry_path) if registry_path else root / DEFAULT_REGISTRY)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        raise RepoError(f"check-all registry not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("components"), list):
        raise RepoError(f"check-all registry {path} is missing a components list")
    for comp in data["components"]:
        if not isinstance(comp, dict) or "id" not in comp or "kind" not in comp or "relpath" not in comp:
            raise RepoError(f"check-all registry {path}: malformed component entry {comp!r}")
    return {"path": path, "schema_version": data.get("schema_version", 1), "components": data["components"]}


def _entry_exists(root: Path, comp: dict) -> bool:
    p = root / comp["relpath"]
    return p.exists()


def _run_unit(root: Path, comp: dict, timeout_s: int) -> subprocess.CompletedProcess:
    rel = comp["relpath"]
    top = comp.get("top_level", rel)
    return subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(root / rel), "-t", str(root / top)],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout_s,
    )


def _run_python(root: Path, comp: dict, timeout_s: int) -> subprocess.CompletedProcess:
    args = [sys.executable, str(root / comp["relpath"]), *(comp.get("args") or [])]
    return subprocess.run(args, cwd=str(root), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout_s)


def run_component(root: Path, comp: dict, timeout_s: int) -> dict:
    entry = comp.get("relpath", "")
    result = {
        "id": comp["id"], "kind": comp["kind"], "relpath": entry,
        "required": bool(comp.get("required", True)),
        "description": comp.get("description", ""),
    }
    if not _entry_exists(root, comp):
        if comp.get("required", True):
            result.update({"status": "FAIL", "exit_code": None,
                           "detail": "required component entry missing - control plane incomplete"})
        else:
            result.update({"status": "NOT_RUN", "exit_code": None, "detail": "entry not present yet"})
        return result
    started = time.monotonic()
    try:
        if comp["kind"] == "unittest":
            proc = _run_unit(root, comp, timeout_s)
        elif comp["kind"] == "python":
            proc = _run_python(root, comp, timeout_s)
        else:
            raise RepoError(f"unknown component kind {comp['kind']!r}")
    except subprocess.TimeoutExpired:
        result.update({"status": "FAIL", "exit_code": None,
                       "detail": f"timeout after {timeout_s}s"})
        return result
    except RepoError as e:
        result.update({"status": "FAIL", "exit_code": None, "detail": str(e)})
        return result
    result["duration_ms"] = int((time.monotonic() - started) * 1000)
    result["exit_code"] = proc.returncode
    tail = (proc.stdout or "") + (("\n--- stderr ---\n" + proc.stderr) if proc.stderr else "")
    tail = tail.strip()[-STDOUT_TAIL_CHARS:]
    if tail:
        result["output_tail"] = tail
    if proc.returncode == 0:
        result.update({"status": "PASS", "detail": f"exit {proc.returncode}"})
    else:
        result.update({"status": "FAIL", "detail": f"exit {proc.returncode}"})
    return result


def _branch_and_head(root: Path) -> tuple[str, str]:
    head = ref_sha("HEAD", root) or "unknown"
    try:
        branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=root).stdout.strip()
    except RepoError:
        branch = "unknown"
    return branch, head


def run_check_all(root: Path, registry_path: str | Path | None = None, out: str | Path | None = None,
                  json_out: bool = False) -> int:
    registry = load_registry(root, registry_path)
    timeout_default = 600
    components = [run_component(root, comp, int(comp.get("timeout_s", timeout_default)))
                  for comp in registry["components"]]
    passed = sum(1 for c in components if c["status"] == "PASS")
    failed = sum(1 for c in components if c["status"] == "FAIL")
    not_run = [c for c in components if c["status"] == "NOT_RUN"]
    total = len(components)
    if failed:
        result, exit_code = "FAIL", EXIT_FAIL
    elif not_run:
        result, exit_code = "NOT_RUN", EXIT_NOT_RUN
    else:
        result, exit_code = "PASS", EXIT_PASS

    branch, head = _branch_and_head(root)
    report = {
        "check_all": "B2-X3",
        "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "repo_root": str(root),
        "branch": branch,
        "head_sha": head,
        "registry": str(registry["path"]),
        "schema_version": registry["schema_version"],
        "components": components,
        "summary": {"total": total, "passed": passed, "failed": failed, "not_run": len(not_run)},
        "not_run_ids": [c["id"] for c in not_run],
        "result": result,
        "exit_code": exit_code,
        "proves": "all registered machine gates that could run are PASS: batchctl 单测、绝对路径扫描、"
                  "secret 扫描、combat harness 自测、semantic combat pipeline 契约（按注册表现状）",
        "not_proven": "未注册/未落盘的契约（如 B2-X1 event spine），游戏内运行态、候选构建与人工验收"
                      "由对应任务各自负责",
    }
    if json_out:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        for c in components:
            mark = {"PASS": "PASS", "FAIL": "FAIL", "NOT_RUN": "SKIP"}[c["status"]]
            extra = c["detail"] or ""
            duration = f" ({c['duration_ms']}ms)" if "duration_ms" in c else ""
            print(f"[{mark}] {c['id']}: {extra}{duration}")
            if c.get("output_tail"):
                print("      tail: " + c["output_tail"].replace("\n", "\n      ")[:400])
        print(f"check-all: {result}  ({passed}/{total} passed, {len(not_run)} not run)  exit={exit_code}")
        print(f"  repo_root={root}")
        print(f"  branch={branch} head={head}")
        if not_run:
            print("  not run: " + ", ".join(c["id"] for c in not_run))
    if out:
        out_path = Path(out)
        if not out_path.is_absolute():
            out_path = root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"check-all report written to {out_path}")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON report")
    ap.add_argument("--out", type=Path, default=None, help="write JSON report to a file")
    ap.add_argument("--registry", type=Path, default=None, help="component registry (default scripts/ai/check_all_components.json)")
    args = ap.parse_args(argv)
    try:
        root = find_repo_root()
    except RepoError as e:
        print(f"check-all: {e}", file=sys.stderr)
        return EXIT_USAGE
    try:
        return run_check_all(root, args.registry, args.out, args.json)
    except RepoError as e:
        print(f"check-all: {e}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())