#!/usr/bin/env python3
"""batchctl: claim/status/handoff/collect/preflight/cleanup lifecycle.

Proves:
  - claim dry-run has zero side effects
  - claim creates branch + worktree under derived (overrideable) root
  - duplicate claim is idempotent; conflicting claim fails clearly
  - status/handoff/collect/preflight work end-to-end on a scratch batch
  - cleanup fail-closed: unknown dir / dirty / unmerged are all refused
  - cleanup succeeds only with explicit --allow-unmerged (+ --force when dirty)
  - everything runs from a non-repo-root cwd
"""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import batchctl  # noqa: E402
import repo_util  # noqa: E402
from test_helpers import commit_all, make_repo, seed_repo, temp_area  # noqa: E402


class BatchCtlTest(unittest.TestCase):
    def setUp(self):
        self.area = temp_area()
        self.base = Path(self.area.name)
        self.repo = make_repo(self.base)
        self.head = seed_repo(self.repo)
        self.wt = self.base / "worktrees with spaces"
        self.orig_cwd = os.getcwd()
        os.chdir(str(self.repo / "scripts"))

    def tearDown(self):
        os.chdir(self.orig_cwd)
        for e in repo_util.worktree_list(self.repo):
            if e["path"] != self.repo.resolve():
                repo_util.git("worktree", "remove", "--force", str(e["path"]), cwd=self.repo)
        self.area.cleanup()

    def _claim(self, task="B1-Z1", *extra):
        return batchctl.main(["claim", task, "--worktrees-root", str(self.wt), *extra])

    def test_claim_dry_run_has_no_side_effects(self):
        rc = self._claim("B1-Z1", "--dry-run")
        self.assertEqual(rc, 0)
        self.assertFalse((self.wt / "B1" / "Z1").exists())
        self.assertFalse(repo_util.ref_exists("agent/b1-z1", self.repo))
        self.assertEqual([e["path"] for e in repo_util.worktree_list(self.repo)],
                         [self.repo.resolve()])

    def test_claim_creates_worktree_and_branch(self):
        rc = self._claim("B1-Z1")
        self.assertEqual(rc, 0)
        tw = self.wt / "B1" / "Z1"
        self.assertTrue((tw / "AGENTS.md").is_file())
        entries = [e for e in repo_util.worktree_list(self.repo) if e["path"] == tw.resolve()]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["branch"], "agent/b1-z1")
        self.assertEqual(repo_util.ref_sha("HEAD", tw), self.head)

    def test_duplicate_claim_idempotent(self):
        self.assertEqual(self._claim("B1-Z1"), 0)
        self.assertEqual(self._claim("B1-Z1"), 0)

    def test_claim_conflicting_branch_fails(self):
        self.assertEqual(self._claim("B1-Z1"), 0)
        rc = self._claim("B1-Z1", "--branch", "agent/other-branch")
        self.assertEqual(rc, 2)

    def test_claim_with_name_branch(self):
        self.assertEqual(self._claim("B1-Z2", "--name", "player-response"), 0)
        self.assertTrue(repo_util.ref_exists("agent/b1-z2-player-response", self.repo))

    def test_claim_from_any_cwd(self):
        nested = self.repo / "scripts" / "nested" / "dir"
        nested.mkdir(parents=True)
        os.chdir(str(nested))
        rc = self._claim("B1-Z3")
        self.assertEqual(rc, 0)
        self.assertTrue((self.wt / "B1" / "Z3" / "AGENTS.md").is_file())

    def test_unknown_leftover_dir_fail_closed(self):
        tw = self.wt / "B1" / "Z9"
        tw.mkdir(parents=True)
        (tw / "junk.txt").write_text("x", encoding="utf-8")
        rc = self._claim("B1-Z9")
        self.assertEqual(rc, 2)
        self.assertTrue((tw / "junk.txt").is_file(), "unknown dir must be left untouched")

    def test_lifecycle_status_handoff_collect_preflight(self):
        self.assertEqual(self._claim("B1-Z1"), 0)
        tw = self.wt / "B1" / "Z1"
        (tw / "feature.py").write_text("print('x')\n", encoding="utf-8")
        commit_all(tw, "feat: scratch change")
        repo_util.git("branch", "batch/b1-anchor", self.head, cwd=self.repo)

        rc = batchctl.main(["status", "B1", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 0)

        rc = batchctl.main(["handoff", "B1-Z1", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 0)
        handoff_file = self.wt / "B1" / "handoffs" / "Z1.yaml"
        self.assertTrue(handoff_file.is_file())
        data = batchctl._yaml_load(handoff_file.read_text(encoding="utf-8"))
        self.assertEqual(data["task_id"], "B1-Z1")
        self.assertEqual(data["branch"], "agent/b1-z1")
        self.assertIn("feature.py", "".join(data.get("changed_files", [])))

        rc = batchctl.main(["collect", "B1", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 0)

        rc = batchctl.main(["preflight", "B1", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 0)

    def test_preflight_fails_on_immutable_touch(self):
        self.assertEqual(self._claim("B1-Z1"), 0)
        tw = self.wt / "B1" / "Z1"
        repo_util.git("branch", "batch/b1-anchor", self.head, cwd=self.repo)
        (tw / "03_raw" / "evil.gd").parent.mkdir(parents=True)
        (tw / "03_raw" / "evil.gd").write_text("x\n", encoding="utf-8")
        commit_all(tw, "BAD: touches immutable 03_raw")
        rc = batchctl.main(["preflight", "B1", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 1)

    def test_cleanup_fail_closed_cases(self):
        self.assertEqual(self._claim("B1-Z1"), 0)
        tw = self.wt / "B1" / "Z1"

        rc = batchctl.main(["cleanup", "B1-Z1", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 2, "unmerged worktree must be refused")
        self.assertTrue(repo_util.find_worktree(tw, self.repo), "worktree must survive failed cleanup")

        (tw / "dirty.txt").write_text("uncommitted\n", encoding="utf-8")
        rc = batchctl.main(["cleanup", "B1-Z1", "--worktrees-root", str(self.wt), "--allow-unmerged"])
        self.assertEqual(rc, 2, "dirty worktree must be refused even when unmerged is allowed")
        self.assertTrue((tw / "dirty.txt").is_file(), "dirty file must survive")

        rc = batchctl.main(["cleanup", "B1-Z1", "--worktrees-root", str(self.wt),
                            "--allow-unmerged", "--force"])
        self.assertEqual(rc, 0, "explicit allow flags must permit cleanup")
        self.assertIsNone(repo_util.find_worktree(tw, self.repo))
        self.assertFalse(tw.exists())

    def test_cleanup_unknown_dir_refused(self):
        tw = self.wt / "B1" / "ZZ"
        tw.mkdir(parents=True)
        (tw / "data.txt").write_text("keep", encoding="utf-8")
        rc = batchctl.main(["cleanup", "B1-ZZ", "--worktrees-root", str(self.wt), "--force"])
        self.assertEqual(rc, 2)
        self.assertTrue((tw / "data.txt").is_file())

    def test_cleanup_nothing_to_do(self):
        rc = batchctl.main(["cleanup", "B1-ZZ", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 0)

    def test_cleanup_dry_run(self):
        self.assertEqual(self._claim("B1-Z1"), 0)
        repo_util.git("branch", "batch/b1-anchor", self.head, cwd=self.repo)
        repo_util.git("branch", "-f", "agent/kinetic-arcane-remaster-foundation", self.head, cwd=self.repo)
        rc = batchctl.main(["cleanup", "B1-Z1", "--worktrees-root", str(self.wt), "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertTrue(repo_util.find_worktree(self.wt / "B1" / "Z1", self.repo),
                        "dry-run must not remove the worktree")

    def test_cleanup_merged_allows_automatic(self):
        self.assertEqual(self._claim("B1-Z1"), 0)
        tw = self.wt / "B1" / "Z1"
        repo_util.git("branch", "batch/b1-anchor", self.head, cwd=self.repo)
        repo_util.git("branch", "-f", "agent/kinetic-arcane-remaster-foundation", self.head, cwd=self.repo)
        rc = batchctl.main(["cleanup", "B1-Z1", "--worktrees-root", str(self.wt)])
        self.assertEqual(rc, 0, "merged+clean worktree should clean automatically")
        self.assertIsNone(repo_util.find_worktree(tw, self.repo))

    def test_scan_subcommands(self):
        rc = batchctl.main(["scan-paths", "--fail-on", "FAIL"])
        self.assertEqual(rc, 0)
        rc = batchctl.main(["scan-secrets"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()