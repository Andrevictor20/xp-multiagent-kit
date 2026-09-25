import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path so we can import the module
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.hooks.smart_tool_optimizer import (
    optimize_tool_call,
    optimize_view_file,
    optimize_run_command,
    MAX_VIEW_LINES,
)


class TestSmartToolOptimizer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a large file (100 lines)
        self.large_file = self.temp_path / "large_file.txt"
        self.large_file.write_text("\n".join(f"Line {i}" for i in range(1, 101)) + "\n", encoding="utf-8")

        # Create a small file (15 lines)
        self.small_file = self.temp_path / "small_file.txt"
        self.small_file.write_text("\n".join(f"Line {i}" for i in range(1, 16)) + "\n", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_view_file_unbounded_large_file_is_clamped(self):
        args = {"AbsolutePath": str(self.large_file)}
        decision, reason, overwrite = optimize_view_file(args)
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        self.assertEqual(overwrite.get("StartLine"), 1)
        self.assertEqual(overwrite.get("EndLine"), MAX_VIEW_LINES)
        self.assertIn("clamped", reason.lower())

    def test_view_file_small_file_is_unmodified(self):
        args = {"AbsolutePath": str(self.small_file)}
        decision, reason, overwrite = optimize_view_file(args)
        self.assertEqual(decision, "allow")
        self.assertIsNone(overwrite)

    def test_view_file_range_exceeding_max_lines_is_clamped(self):
        args = {
            "AbsolutePath": str(self.large_file),
            "StartLine": 10,
            "EndLine": 90,
        }
        decision, reason, overwrite = optimize_view_file(args)
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        self.assertEqual(overwrite.get("StartLine"), 10)
        self.assertEqual(overwrite.get("EndLine"), 10 + MAX_VIEW_LINES)

    def test_view_file_range_within_max_lines_is_preserved(self):
        args = {
            "AbsolutePath": str(self.large_file),
            "StartLine": 10,
            "EndLine": 35,
        }
        decision, reason, overwrite = optimize_view_file(args)
        self.assertEqual(decision, "allow")
        self.assertIsNone(overwrite)

    def test_run_command_verbose_test_runner_is_sanitized(self):
        cmd = "pytest tests/ -v"
        decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        new_cmd = overwrite.get("CommandLine", "")
        self.assertTrue("agy-sanitize" in new_cmd or "head" in new_cmd)

    def test_run_command_verbose_git_log_is_sanitized(self):
        cmd = "git log"
        decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        new_cmd = overwrite.get("CommandLine", "")
        self.assertTrue("agy-sanitize" in new_cmd or "head" in new_cmd or "-n" in new_cmd)

    def test_run_command_already_piped_or_limited_is_preserved(self):
        cmds = [
            "pytest tests/ -v | head -n 30",
            "git log -n 5 --oneline",
            "npm test | agy-sanitize",
            "find . -maxdepth 2 -name '*.py' | head -n 10",
        ]
        for cmd in cmds:
            decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
            self.assertEqual(decision, "allow", f"Failed for cmd: {cmd}")
            self.assertIsNone(overwrite, f"Expected no overwrite for: {cmd}")

    def test_run_command_safe_short_commands_are_preserved(self):
        cmds = [
            "git status",
            "git branch",
            "pwd",
            "which python3",
            "mkdir -p src/foo",
            "ls -la",
            "echo 'hello world'",
        ]
        for cmd in cmds:
            decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
            self.assertEqual(decision, "allow")
            self.assertIsNone(overwrite, f"Expected no overwrite for: {cmd}")

    def test_run_command_redirect_to_file_is_preserved(self):
        cmds = [
            "pytest tests/ > /tmp/output.log 2>&1",
            "npm test >> test.log",
        ]
        for cmd in cmds:
            decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
            self.assertEqual(decision, "allow")
            self.assertIsNone(overwrite)

    def test_empty_or_invalid_payload_safe_fallback(self):
        res = optimize_tool_call({})
        self.assertEqual(res.get("decision"), "allow")
        self.assertNotIn("overwrite", res)

    def test_hook_cli_subprocess_contract(self):
        script_path = ROOT_DIR / "scripts" / "hooks" / "smart-tool-optimizer.py"
        payload = {
            "toolCall": {
                "name": "view_file",
                "args": {
                    "AbsolutePath": str(self.large_file),
                },
            },
            "stepIdx": 42,
        }
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(payload),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        output_data = json.loads(proc.stdout)
        self.assertEqual(output_data.get("decision"), "allow")
        self.assertIn("overwrite", output_data)
        self.assertEqual(output_data["overwrite"].get("EndLine"), MAX_VIEW_LINES)


if __name__ == "__main__":
    unittest.main()
