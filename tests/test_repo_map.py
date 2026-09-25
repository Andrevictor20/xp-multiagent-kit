import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestRepoMap(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create sample workspace structure
        src_dir = self.temp_path / "src"
        src_dir.mkdir()

        py_file = src_dir / "calculator.py"
        py_file.write_text(
            "class Calculator:\n"
            "    def add(self, a, b):\n"
            "        return a + b\n\n"
            "def calculate_total(items):\n"
            "    return sum(items)\n",
            encoding="utf-8",
        )

        ts_file = src_dir / "service.ts"
        ts_file.write_text(
            "export interface UserProfile {\n"
            "  id: string;\n"
            "}\n"
            "export class UserService {\n"
            "  getUser() {}\n"
            "}\n"
            "export function fetchAuth() {}\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_generate_repo_map_extracts_python_and_ts_symbols(self):
        from scripts.repo_map import generate_repo_map
        content = generate_repo_map(self.temp_path)
        self.assertIn("calculator.py", content)
        self.assertIn("Calculator", content)
        self.assertIn("calculate_total", content)
        self.assertIn("service.ts", content)
        self.assertIn("UserService", content)

    def test_repo_map_strictly_under_80_lines(self):
        from scripts.repo_map import generate_repo_map
        content = generate_repo_map(ROOT_DIR, max_lines=80)
        lines = content.strip().split("\n")
        self.assertLessEqual(len(lines), 80)

    def test_save_repo_map_persists_to_disk(self):
        from scripts.repo_map import save_repo_map
        target_file = self.temp_path / "REPO_MAP.md"
        saved_path = save_repo_map(self.temp_path, target_path=target_file)
        self.assertTrue(target_file.is_file())
        self.assertGreater(target_file.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
