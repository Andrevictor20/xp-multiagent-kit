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

    def test_run_command_unittest_is_sanitized(self):
        cmd = "python3 -m unittest discover tests/"
        decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        self.assertIn("agy-sanitize", overwrite.get("CommandLine", ""))

    def test_run_command_with_env_vars_is_sanitized(self):
        cmd = "CI=1 pytest tests/ -v"
        decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        self.assertIn("agy-sanitize", overwrite.get("CommandLine", ""))

    def test_run_command_chained_commands_are_sanitized(self):
        cmd = "cd /tmp && pytest"
        decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        self.assertIn("agy-sanitize", overwrite.get("CommandLine", ""))

    def test_run_command_pipeline_without_limiter_is_sanitized(self):
        cmd = "cat log.txt | grep ERROR"
        decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        self.assertIn("agy-sanitize", overwrite.get("CommandLine", ""))

    def test_run_command_linters_and_tools_are_sanitized(self):
        cmds = ["mypy src/", "flake8 .", "ruff check", "eslint .", "npm run lint", "cargo clippy"]
        for cmd in cmds:
            decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
            self.assertEqual(decision, "allow")
            self.assertIsNotNone(overwrite, f"Expected sanitization for: {cmd}")
            self.assertIn("agy-sanitize", overwrite.get("CommandLine", ""))

    def test_run_command_preserves_exit_code_pipefail(self):
        cmd = "pytest tests/"
        decision, reason, overwrite = optimize_run_command({"CommandLine": cmd})
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        new_cmd = overwrite.get("CommandLine", "")
        self.assertIn("pipefail", new_cmd)

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


    def test_loop_detection_allows_first_and_second_call_then_blocks_third(self):
        from scripts.hooks.smart_tool_optimizer import check_tool_loop, reset_tool_loop_history
        history_file = self.temp_path / "tool_history.json"
        reset_tool_loop_history(history_file)

        tool = "view_file"
        args = {"AbsolutePath": "/some/file.py", "StartLine": 1, "EndLine": 40}

        # 1st call: OK
        is_loop, msg = check_tool_loop(tool, args, history_file=history_file, max_repeats=3)
        self.assertFalse(is_loop)

        # 2nd call: OK
        is_loop, msg = check_tool_loop(tool, args, history_file=history_file, max_repeats=3)
        self.assertFalse(is_loop)

        # 3rd call: BLOCKED
        is_loop, msg = check_tool_loop(tool, args, history_file=history_file, max_repeats=3)
        self.assertTrue(is_loop)
        self.assertIn("Loop", msg)

    def test_loop_detection_resets_on_different_args(self):
        from scripts.hooks.smart_tool_optimizer import check_tool_loop, reset_tool_loop_history
        history_file = self.temp_path / "tool_history.json"
        reset_tool_loop_history(history_file)

        tool = "view_file"
        # 2 calls with args1
        check_tool_loop(tool, {"StartLine": 1}, history_file=history_file, max_repeats=3)
        check_tool_loop(tool, {"StartLine": 1}, history_file=history_file, max_repeats=3)

        # Call with different args: should NOT trigger loop
        is_loop, _ = check_tool_loop(tool, {"StartLine": 41}, history_file=history_file, max_repeats=3)
        self.assertFalse(is_loop)

    def test_optimize_list_dir_blocks_workspace_root_direct_scan(self):
        from scripts.hooks.smart_tool_optimizer import optimize_list_dir
        ws_root = str(ROOT_DIR)
        decision, reason, overwrite = optimize_list_dir({"DirectoryPath": ws_root}, workspace_root=ws_root)
        self.assertEqual(decision, "deny")
        self.assertIn("REPO_MAP.md", reason)

    def test_optimize_list_dir_allows_subdirectories(self):
        from scripts.hooks.smart_tool_optimizer import optimize_list_dir
        ws_root = str(ROOT_DIR)
        sub_dir = str(ROOT_DIR / "scripts")
        decision, reason, overwrite = optimize_list_dir({"DirectoryPath": sub_dir}, workspace_root=ws_root)
        self.assertEqual(decision, "allow")

    def test_optimize_grep_search_injects_noise_filters_when_includes_empty(self):
        from scripts.hooks.smart_tool_optimizer import optimize_grep_search
        args = {"SearchPath": str(ROOT_DIR), "Query": "test"}
        decision, reason, overwrite = optimize_grep_search(args)
        self.assertEqual(decision, "allow")
        self.assertIsNotNone(overwrite)
        includes = overwrite.get("Includes", [])
        self.assertTrue(any("node_modules" in inc for inc in includes))
        self.assertTrue(any(".git" in inc for inc in includes))

    def test_optimize_grep_search_preserves_custom_includes(self):
        from scripts.hooks.smart_tool_optimizer import optimize_grep_search
        args = {"SearchPath": str(ROOT_DIR), "Query": "test", "Includes": ["*.py"]}
        decision, reason, overwrite = optimize_grep_search(args)
        self.assertEqual(decision, "allow")
        self.assertIsNone(overwrite)

    def test_optimize_write_to_file_allows_new_file(self):
        from scripts.hooks.smart_tool_optimizer import optimize_write_to_file
        new_file = self.temp_path / "non_existent.txt"
        args = {"TargetFile": str(new_file), "CodeContent": "hello world"}
        decision, reason, overwrite = optimize_write_to_file(args)
        self.assertEqual(decision, "allow")
        self.assertIsNone(overwrite)

    def test_optimize_write_to_file_allows_small_file(self):
        from scripts.hooks.smart_tool_optimizer import optimize_write_to_file
        args = {"TargetFile": str(self.small_file), "CodeContent": "new content"}
        decision, reason, overwrite = optimize_write_to_file(args)
        self.assertEqual(decision, "allow")

    def test_optimize_write_to_file_blocks_large_existing_file(self):
        from scripts.hooks.smart_tool_optimizer import optimize_write_to_file
        args = {"TargetFile": str(self.large_file), "CodeContent": "new content"}
        decision, reason, overwrite = optimize_write_to_file(args)
        self.assertEqual(decision, "deny")
        self.assertIn("replace_file_content", reason)
        self.assertIn("100 linhas", reason)

    def test_optimize_write_to_file_allows_artifacts(self):
        from scripts.hooks.smart_tool_optimizer import optimize_write_to_file
        args = {
            "TargetFile": str(self.large_file),
            "CodeContent": "new content",
            "ArtifactMetadata": {"Summary": "summary", "UserFacing": True, "RequestFeedback": False},
        }
        decision, reason, overwrite = optimize_write_to_file(args)
        self.assertEqual(decision, "allow")


if __name__ == "__main__":
    unittest.main()

