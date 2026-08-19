#!/usr/bin/env python3
"""Shared helpers for scripts/ai tests: temp git repos (names may contain
spaces to prove space-safe path handling)."""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

TEST_ROOT = Path(__file__).resolve().parents[3]
AI_DIR = TEST_ROOT / "scripts" / "ai"
FIXTURES = AI_DIR / "tests" / "fixtures"


def make_repo(base: Path, name: str = "repo with spaces") -> Path:
    root = base / name
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "B1-X0 test")
    _git(root, "config", "user.email", "b1-x0@invalid.local")
    return root


def commit_all(root: Path, msg: str = "seed") -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", msg)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def seed_repo(root: Path) -> str:
    (root / "AGENTS.md").write_text("# Mutagenic test repo\n", encoding="utf-8")
    (root / "status.json").write_text('{"project_phase":"TEST"}\n', encoding="utf-8")
    (root / "scripts").mkdir(exist_ok=True)
    (root / "scripts" / "bootstrap_deploy.py").write_text(
        "from pathlib import Path\nROOT = Path(__file__).resolve().parents[1]\n",
        encoding="utf-8")
    return commit_all(root)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def temp_area(name: str = "b1x0") -> tempfile.TemporaryDirectory:
    return tempfile.TemporaryDirectory(prefix=f"mutagenic-{name}-")


class CwdGuard:
    def __init__(self) -> None:
        self.original = os.getcwd()

    def restore(self) -> None:
        os.chdir(self.original)