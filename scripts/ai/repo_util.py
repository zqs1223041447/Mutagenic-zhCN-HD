#!/usr/bin/env python3
"""Repo-relative resolution helpers shared by scripts/ai tooling.

All production code in this repository must resolve paths from the repo root
at runtime; no host absolute paths are allowed (AGENTS.md 9). These helpers
pin two rules:

1. repo root == `git rev-parse --show-toplevel` (works from any cwd, including
   inside a linked Git worktree);
2. batch worktrees live at ``<main_repo_parent>/<main_repo_name>.worktrees/``
   (the runtime-derived convention from docs/ai/PARALLEL_BATCH_WORKFLOW.md,
   never a fixed host path).
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

TASK_ID_RE = re.compile(r"^[A-Za-z0-9]+-[A-Za-z0-9-]+$")


class RepoError(RuntimeError):
    pass


def git(*args: str, cwd: str | Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    cmd = ["git", *args]
    try:
        r = subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except OSError as e:
        raise RepoError(f"cannot run git: {e}") from e
    if check and r.returncode != 0:
        raise RepoError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r


def find_repo_root(start: str | Path | None = None) -> Path:
    start = Path(start or os.getcwd())
    try:
        r = git("rev-parse", "--show-toplevel", cwd=start)
        out = r.stdout.strip()
        if out:
            return Path(out).resolve()
    except RepoError:
        pass
    cur = start.resolve()
    while True:
        if (cur / "AGENTS.md").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RepoError(f"not inside a Mutagenic repo clone (no git toplevel or AGENTS.md marker): {start}")


def git_common_dir(root: str | Path) -> Path:
    """Absolute path of the git common dir (works from main tree or linked worktree)."""
    common = git("rev-parse", "--git-common-dir", cwd=root).stdout.strip()
    common_path = Path(common)
    if not common_path.is_absolute():
        common_path = (Path(root) / common_path).resolve()
    return common_path


def find_main_repo_root(start: str | Path | None = None) -> Path:
    root = find_repo_root(start)
    try:
        return git_common_dir(root).parent
    except RepoError:
        return root


def worktrees_root(start: str | Path | None = None) -> Path:
    main = find_main_repo_root(start)
    return main.parent / (main.name + ".worktrees")


def split_task(task_id: str) -> tuple[str, str]:
    if not TASK_ID_RE.match(task_id):
        raise RepoError(f"invalid task id {task_id!r}: expected <BATCH>-<TASK>, e.g. B1-X1")
    batch, task = task_id.split("-", 1)
    return batch, task


def default_branch(task_id: str, name: str | None = None) -> str:
    batch, task = split_task(task_id)
    branch = f"agent/{batch.lower()}-{task.lower()}"
    if name:
        branch += f"-{re.sub(r'[^A-Za-z0-9._-]', '-', name).strip('-')}"
    return branch


def task_dir(task_id: str, start: str | Path | None = None, worktrees_root_override: str | Path | None = None) -> Path:
    batch, task = split_task(task_id)
    base = Path(worktrees_root_override) if worktrees_root_override else worktrees_root(start)
    return base / batch / task


def ref_exists(ref: str, start: str | Path | None = None) -> bool:
    try:
        git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", cwd=start or os.getcwd())
        return True
    except RepoError:
        return False


def ref_sha(ref: str, start: str | Path | None = None) -> str | None:
    try:
        r = git("rev-parse", ref, cwd=start or os.getcwd())
        return r.stdout.strip()
    except RepoError:
        return None


def worktree_list(start: str | Path | None = None) -> list[dict]:
    r = git("worktree", "list", "--porcelain", cwd=start or os.getcwd())
    entries: list[dict] = []
    cur: dict | None = None
    for line in r.stdout.splitlines():
        if not line.strip():
            if cur is not None:
                entries.append(cur)
                cur = None
            continue
        if line.startswith("worktree "):
            cur = {"path": Path(line[len("worktree "):].strip())}
        elif cur is not None and line.startswith("HEAD "):
            cur["head"] = line[len("HEAD "):].strip()
        elif cur is not None and line.startswith("branch "):
            cur["branch"] = line[len("branch "):].strip().removeprefix("refs/heads/")
        elif cur is not None and line.startswith("detached"):
            cur["detached"] = True
        elif cur is not None and line.startswith("locked"):
            cur["locked"] = True
    if cur is not None:
        entries.append(cur)
    return entries


def find_worktree(path: Path, start: str | Path | None = None) -> dict | None:
    target = path.resolve()
    for e in worktree_list(start):
        if e["path"].resolve() == target:
            return e
    return None


def is_merged(branch: str, into_ref: str, start: str | Path | None = None) -> bool:
    try:
        git("merge-base", "--is-ancestor", branch, into_ref, cwd=start or os.getcwd())
        return True
    except RepoError:
        return False


def tracked_files(root: Path) -> list[str]:
    try:
        r = git("ls-files", cwd=root)
        return [ln for ln in r.stdout.splitlines() if ln]
    except RepoError:
        return _snapshot_files(root)


def _snapshot_files(root: Path) -> list[str]:
    """Fallback for non-git snapshots: list all files under root except .git."""
    out: list[str] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if ".git/" in rel or rel.startswith(".git/"):
            continue
        out.append(rel)
    return out


def claim_lock_path(root: str | Path) -> Path:
    """Path of the batchctl claim lock, inside the git common dir (shared by all worktrees)."""
    return git_common_dir(root) / "batchctl-claim.lock"