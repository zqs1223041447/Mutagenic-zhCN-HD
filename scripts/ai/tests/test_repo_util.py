#!/usr/bin/env python3
"""repo_util: repo root resolution from arbitrary cwd, spaces in paths,
Windows path semantics, worktrees-root derivation."""
from __future__ import annotations

import os
import sys
import unittest

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import repo_util  # noqa: E402
from test_helpers import CwdGuard, commit_all, make_repo, seed_repo, temp_area  # noqa: E402


class RepoUtilTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.area = temp_area()
        cls.base = Path(cls.area.name)
        cls.repo = make_repo(cls.base)
        cls.head = seed_repo(cls.repo)
        cls.guard = CwdGuard()

    @classmethod
    def tearDownClass(cls):
        cls.guard.restore()
        cls.area.cleanup()

    def test_root_from_nested_cwd(self):
        nested = self.repo / "scripts" / "deep" / "deeper"
        nested.mkdir(parents=True)
        root = repo_util.find_repo_root(nested)
        self.assertEqual(root, self.repo.resolve())

    def test_root_from_fake_repo_with_spaces(self):
        self.assertIn(" ", str(self.repo))
        os.chdir(str(self.repo))
        self.assertEqual(repo_util.find_repo_root(), self.repo.resolve())

    def test_main_root_and_worktrees_root(self):
        main = repo_util.find_main_repo_root(self.repo)
        self.assertEqual(main, self.repo.resolve())
        wt = repo_util.worktrees_root(self.repo)
        self.assertEqual(wt, self.repo.parent / (self.repo.name + ".worktrees"))

    def test_main_root_from_linked_worktree(self):
        real = Path(__file__).resolve()
        in_real = False
        while real != real.parent:
            if (real / "AGENTS.md").exists():
                in_real = True
                break
            real = real.parent
        if not in_real:
            self.skipTest("not running inside a real Mutagenic clone")
            return
        main = repo_util.find_main_repo_root()
        self.assertTrue((main / "AGENTS.md").is_file(), "main root must carry the AGENTS.md marker")
        wt = repo_util.worktrees_root()
        self.assertTrue(wt.name.endswith(".worktrees"), "worktrees root must follow the derived layout")
        self.assertTrue((main / "status.json").is_file() or (main / "scripts").is_dir(),
                        "main root must be a real Mutagenic clone")

    def test_task_parsing_and_defaults(self):
        self.assertEqual(repo_util.split_task("B1-X1"), ("B1", "X1"))
        self.assertEqual(repo_util.default_branch("B1-X1"), "agent/b1-x1")
        self.assertEqual(repo_util.default_branch("B1-X1", "player-response"), "agent/b1-x1-player-response")
        with self.assertRaises(repo_util.RepoError):
            repo_util.split_task("nonsense")

    def test_task_dir_derivation(self):
        with temp_area() as a:
            override = Path(a)
            td = repo_util.task_dir("B1-X1", self.repo, override)
            self.assertEqual(td, override / "B1" / "X1")

    def test_git_markers(self):
        self.assertTrue(repo_util.ref_exists("HEAD", self.repo))
        self.assertEqual(repo_util.ref_sha("HEAD", self.repo), self.head)

    def test_tracked_files(self):
        files = repo_util.tracked_files(self.repo)
        self.assertIn("AGENTS.md", files)
        self.assertIn("scripts/bootstrap_deploy.py", files)


if __name__ == "__main__":
    unittest.main()