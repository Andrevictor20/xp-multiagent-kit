import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestAgyDashboard(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        mem_dir = self.workspace / ".agents" / "memory"
        mem_dir.mkdir(parents=True)
        (mem_dir / "PROJECT_MEMORY.md").write_text("# Test Memory\n", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_collect_dashboard_data(self):
        from scripts.agy_dashboard import collect_dashboard_data

        data = collect_dashboard_data(self.workspace)
        self.assertIn("health", data)
        self.assertIn("quotas", data)
        self.assertIn("memory", data)
        self.assertIn("daemon", data)
        self.assertIn("session", data)

    def test_render_dashboard_text(self):
        from scripts.agy_dashboard import collect_dashboard_data, render_dashboard

        data = collect_dashboard_data(self.workspace)
        rendered = render_dashboard(data, width=80)
        self.assertIn("Antigravity", rendered)
        self.assertIn("COTAS", rendered)
        self.assertIn("Memória", rendered)


if __name__ == "__main__":
    unittest.main()
