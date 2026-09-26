#!/usr/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "agy-git-ops"


class TestAgyGitOps(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_dir = Path(self.temp_dir.name)
        # Initialize test git repo
        subprocess.run(["git", "init"], cwd=self.repo_dir, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Tester"], cwd=self.repo_dir, check=True)

        # Initial commit
        test_file = self.repo_dir / "README.md"
        test_file.write_text("# Test Repo\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=self.repo_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.repo_dir, check=True, stdout=subprocess.DEVNULL)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_help_command(self):
        res = subprocess.run([str(SCRIPT_PATH), "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Uso: agy-git-ops", res.stdout)
        self.assertIn("status", res.stdout)
        self.assertIn("diff", res.stdout)

    def test_status_command_clean(self):
        res = subprocess.run([str(SCRIPT_PATH), "status"], cwd=self.repo_dir, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), "")

    def test_status_command_dirty(self):
        new_file = self.repo_dir / "new_file.txt"
        new_file.write_text("Hello\n", encoding="utf-8")

        res = subprocess.run([str(SCRIPT_PATH), "status"], cwd=self.repo_dir, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("?? new_file.txt", res.stdout)

    def test_log_command(self):
        res = subprocess.run([str(SCRIPT_PATH), "log", "1"], cwd=self.repo_dir, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Initial commit", res.stdout)

    def test_diff_command(self):
        readme = self.repo_dir / "README.md"
        readme.write_text("# Test Repo Modified\n", encoding="utf-8")

        res = subprocess.run([str(SCRIPT_PATH), "diff"], cwd=self.repo_dir, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("README.md", res.stdout)
        self.assertIn("1 file changed", res.stdout)


if __name__ == "__main__":
    unittest.main()
