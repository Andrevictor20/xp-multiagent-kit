import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestAgyDaemon(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.pid_file = self.workspace / "daemon.pid"
        self.log_file = self.workspace / "daemon.log"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_daemon_status_stopped(self):
        from scripts.agy_daemon import get_daemon_status

        status = get_daemon_status(self.pid_file)
        self.assertFalse(status["running"])

    def test_daemon_pid_lifecycle(self):
        from scripts.agy_daemon import write_pid_file, read_pid, remove_pid_file

        write_pid_file(self.pid_file, 12345)
        self.assertTrue(self.pid_file.is_file())
        self.assertEqual(read_pid(self.pid_file, check_alive=False), 12345)

        removed = remove_pid_file(self.pid_file)
        self.assertTrue(removed)
        self.assertIsNone(read_pid(self.pid_file))

    def test_run_maintenance_cycle(self):
        from scripts.agy_daemon import run_maintenance_cycle

        # Setup mock memory file
        mem_dir = self.workspace / ".agents" / "memory"
        mem_dir.mkdir(parents=True)
        mem_file = mem_dir / "PROJECT_MEMORY.md"
        mem_file.write_text("# Project Memory\n\n## 1. Summary\nOk\n", encoding="utf-8")

        result = run_maintenance_cycle(self.workspace, log_file=self.log_file)
        self.assertIn("memory", result)
        self.assertIn("worktree", result)
        self.assertIn("quota", result)
        self.assertTrue(self.log_file.is_file())

    def test_sync_live_quota_task(self):
        from scripts.agy_daemon import sync_live_quota_task
        res = sync_live_quota_task(self.workspace, log_file=self.log_file)
        self.assertIsInstance(res, str)



if __name__ == "__main__":
    unittest.main()
