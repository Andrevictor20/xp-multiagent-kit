import unittest
from unittest.mock import MagicMock, patch
import os
import subprocess
from scripts.git_worktree_manager import (
    create_worktree,
    remove_worktree,
    list_worktrees,
    sanitize_branch_name,
)

class TestGitWorktreeManager(unittest.TestCase):
    def test_sanitize_branch_name(self):
        self.assertEqual(sanitize_branch_name("feat/my new task!"), "feat-my-new-task")
        self.assertEqual(sanitize_branch_name("bugfix #123"), "bugfix-123")
        self.assertEqual(sanitize_branch_name("task_456"), "task_456")

    @patch("os.makedirs")
    @patch("subprocess.run")
    def test_create_worktree_success(self, mock_run, mock_makedirs):
        mock_run.return_value = MagicMock(returncode=0, stdout="Preparing worktree", stderr="")
        path, branch = create_worktree("auth-refactor", base_branch="main", base_dir="/fake/repo")
        
        expected_branch = "task/auth-refactor"
        expected_path = os.path.join("/fake/repo", ".agents", "worktrees", "auth-refactor")
        
        self.assertEqual(branch, expected_branch)
        self.assertEqual(path, expected_path)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("git", args)
        self.assertIn("worktree", args)
        self.assertIn("add", args)
        self.assertIn("-b", args)
        self.assertIn(expected_branch, args)

    @patch("os.makedirs")
    @patch("subprocess.run")
    def test_create_worktree_failure_raises(self, mock_run, mock_makedirs):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="fatal: branch already exists")
        with self.assertRaises(RuntimeError):
            create_worktree("existing-task", base_dir="/fake/repo")

    @patch("subprocess.run")
    def test_remove_worktree(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        success = remove_worktree("auth-refactor", force=True, delete_branch=True, base_dir="/fake/repo")
        
        self.assertTrue(success)
        self.assertGreaterEqual(mock_run.call_count, 1)

    @patch("subprocess.run")
    def test_list_worktrees(self, mock_run):
        mock_output = (
            "/fake/repo                  abc1234 [main]\n"
            "/fake/repo/.agents/worktrees/task-1 def5678 [task/task-1]\n"
        )
        mock_run.return_value = MagicMock(returncode=0, stdout=mock_output, stderr="")
        worktrees = list_worktrees(base_dir="/fake/repo")
        
        self.assertEqual(len(worktrees), 1)
        self.assertEqual(worktrees[0]["task"], "task-1")
        self.assertEqual(worktrees[0]["branch"], "task/task-1")

if __name__ == "__main__":
    unittest.main()
