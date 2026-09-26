#!/usr/bin/env python3
import importlib.util
import tempfile
import unittest
from pathlib import Path

# Load module with hyphen in name
MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "hooks" / "tool-size-guard.py"
spec = importlib.util.spec_from_file_location("tool_size_guard", str(MODULE_PATH))
tool_size_guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool_size_guard)
process_tool_payload = tool_size_guard.process_tool_payload


class TestToolSizeGuard(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.scratch_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_process_payload_normal_size_no_flood(self):
        data = {
            "tool_name": "run_command",
            "output": "Normal command output with few lines\nline 2\nline 3\n",
        }
        res = process_tool_payload(data, scratch_dir=self.scratch_dir)

        self.assertFalse(res["is_flooding"])
        self.assertEqual(res["tool_name"], "run_command")
        self.assertFalse((self.scratch_dir / "tool_warnings.log").exists())

    def test_process_payload_exceeding_chars_triggers_flood_warning(self):
        huge_text = "X" * 3000
        data = {
            "tool_name": "run_command",
            "output": huge_text,
        }
        res = process_tool_payload(data, scratch_dir=self.scratch_dir)

        self.assertTrue(res["is_flooding"])
        self.assertEqual(res["char_count"], 3000)

        log_file = self.scratch_dir / "tool_warnings.log"
        self.assertTrue(log_file.exists())
        log_content = log_file.read_text(encoding="utf-8")
        self.assertIn("TOOL FLOOD WARNING", log_content)
        self.assertIn("3000 chars", log_content)

    def test_process_payload_exceeding_lines_triggers_flood_warning(self):
        many_lines = "\n".join(f"line {i}" for i in range(60))
        data = {
            "tool_name": "view_file",
            "content": many_lines,
        }
        res = process_tool_payload(data, scratch_dir=self.scratch_dir)

        self.assertTrue(res["is_flooding"])
        self.assertEqual(res["line_count"], 60)

        log_file = self.scratch_dir / "tool_warnings.log"
        self.assertTrue(log_file.exists())
        log_content = log_file.read_text(encoding="utf-8")
        self.assertIn("view_file", log_content)
        self.assertIn("60 linhas", log_content)


if __name__ == "__main__":
    unittest.main()
