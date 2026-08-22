#!/usr/bin/env python3
"""Minimal Product-lane environment doctor for Mutagenic Godot 4.7.1."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

EXPECTED_INTEGRATION = "agent/kinetic-arcane-remaster-foundation"
EXPECTED_GODOT = "4.7.1"


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=10, check=False)
        return p.returncode, (p.stdout or p.stderr).strip()
    except Exception as exc:
        return 127, f"{type(exc).__name__}: {exc}"


def find_repo() -> Path | None:
    code, out = run(["git", "rev-parse", "--show-toplevel"])
    if code != 0 or not out:
        return None
    return Path(out).resolve()


def godot_candidate() -> str | None:
    explicit = os.environ.get("MUTAGENIC_GODOT4")
    if explicit:
        return explicit
    for name in ("godot4", "godot", "Godot"):
        hit = shutil.which(name)
        if hit:
            return hit
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = find_repo()
    result: dict[str, object] = {
        "expected_integration_branch": EXPECTED_INTEGRATION,
        "expected_godot": EXPECTED_GODOT,
        "python": sys.version.split()[0],
    }
    if repo is None:
        result.update(status="NOT_A_GIT_REPO", ready=False)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "status: NOT_A_GIT_REPO")
        return 2

    result["repo_root"] = str(repo)
    _, branch = run(["git", "branch", "--show-current"], cwd=repo)
    result["branch"] = branch
    branch_ok = branch == EXPECTED_INTEGRATION or branch.startswith("agent/")
    result["branch_ok"] = branch_ok

    py_ok = sys.version_info >= (3, 11)
    result["python_ok"] = py_ok

    candidate = godot_candidate()
    result["godot_executable"] = candidate
    godot_ok = False
    godot_version = None
    if candidate:
        code, out = run([candidate, "--version"], cwd=repo)
        godot_version = out
        godot_ok = code == 0 and EXPECTED_GODOT in out
    result["godot_version"] = godot_version
    result["godot_ok"] = godot_ok

    repo_ready = branch_ok and py_ok
    if repo_ready and godot_ok:
        status = "PRODUCT_DEV_READY"
    elif repo_ready:
        status = "PRODUCT_REPO_READY_TOOLCHAIN_BLOCKED"
    else:
        status = "PRODUCT_REPO_NOT_READY"
    result["status"] = status
    result["ready"] = status == "PRODUCT_DEV_READY"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {status}")
        print(f"repo: {repo}")
        print(f"branch: {branch}")
        print(f"python: {result['python']} ({'OK' if py_ok else 'NEED >=3.11'})")
        print(f"godot: {godot_version or 'NOT FOUND'}")
        if not godot_ok:
            print("hint: set MUTAGENIC_GODOT4 to the Godot 4.7.1 executable")

    return 0 if repo_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
