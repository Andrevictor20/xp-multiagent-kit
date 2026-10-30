#!/usr/bin/env python3
"""
tests/test_cursor_multiagent.py
TDD Suite for Cursor Multi-Agent Engine Integration (Boss-Worker Pattern).
Covers:
- Cursor project provisioning (.cursor/rules/30-multiagent-boss-worker.mdc)
- CursorWorkerDriver command generation (cursor agent <prompt> --model ... --worktree ... --output-format json)
- Host-agnostic driver factory resolution for 'cursor'
- Orchestration integration with host='cursor'
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.host_adapters import HostAdapters, SUPPORTED_TARGETS
from scripts.multiagent_drivers import (
    BaseWorkerDriver,
    CursorWorkerDriver,
    get_worker_driver,
)
from scripts.antigravity_multiagent import (
    prepare_subagent_payload,
    validate_mission_manifest,
)


class TestCursorHostAdapter(unittest.TestCase):
    """Test Cursor configuration and Boss-Worker rule (.cursor/rules/30-multiagent-boss-worker.mdc)."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        self.kit_dir = Path(__file__).resolve().parent.parent
        self.adapter = HostAdapters(kit_dir=self.kit_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cursor_is_in_supported_targets(self):
        self.assertIn("cursor", SUPPORTED_TARGETS)

    def test_install_cursor_provisions_boss_worker_rule(self):
        actions = self.adapter.install_cursor_project(self.project_dir)
        self.assertTrue(len(actions) > 0)

        rules_dir = self.project_dir / ".cursor" / "rules"
        self.assertTrue(rules_dir.is_dir(), ".cursor/rules deve ser um diretório")

        # 30-multiagent-boss-worker.mdc deve existir
        bw_rule = rules_dir / "30-multiagent-boss-worker.mdc"
        self.assertTrue(bw_rule.is_file(), "30-multiagent-boss-worker.mdc deve ser criado")

        content = bw_rule.read_text(encoding="utf-8")
        self.assertIn("---", content)
        self.assertIn("description:", content)
        self.assertIn("globs:", content)
        self.assertIn("alwaysApply:", content)
        self.assertIn("Boss-Worker", content)
        self.assertIn("allowed_paths", content)
        self.assertIn("TDD", content)
        self.assertIn("Português", content)

    def test_install_cursor_provisions_core_rules_and_mcp(self):
        self.adapter.install_cursor_project(self.project_dir)
        rules_dir = self.project_dir / ".cursor" / "rules"
        self.assertTrue((rules_dir / "00-xp-core.mdc").is_file())
        self.assertTrue((rules_dir / "10-frontend-design.mdc").is_file())
        self.assertTrue((rules_dir / "20-tdd-testing.mdc").is_file())

        mcp_path = self.project_dir / ".cursor" / "mcp.json"
        self.assertTrue(mcp_path.is_file())
        mcp_data = json.loads(mcp_path.read_text(encoding="utf-8"))
        self.assertIn("mcpServers", mcp_data)
        self.assertIn("code-review-graph", mcp_data["mcpServers"])


class TestCursorWorkerDriver(unittest.TestCase):
    """Test CursorWorkerDriver command, prompt formatting, and model resolution."""

    def setUp(self):
        self.driver = CursorWorkerDriver()
        self.sample_task = {
            "task_id": "cursor-auth-task",
            "subagent": "builder",
            "model": "gemini-3.8-flash",
            "effort": "low",
            "execution_group": 1,
            "allowed_paths": ["src/cursor/"],
            "objective": "Implementar CursorWorkerDriver e testes TDD",
            "verification_cmd": "python3 -m unittest tests/test_cursor_multiagent.py",
        }

    def test_build_worker_command_contains_required_flags(self):
        cmd = self.driver.build_worker_command(self.sample_task, shared_memory="SHARED_CURSOR_MEM")

        self.assertEqual(cmd[0], "cursor")
        self.assertEqual(cmd[1], "agent")

        self.assertIn("--model", cmd)
        idx_m = cmd.index("--model")
        self.assertEqual(cmd[idx_m + 1], "claude-3-5-haiku")

        self.assertIn("--worktree", cmd)
        idx_wt = cmd.index("--worktree")
        self.assertEqual(cmd[idx_wt + 1], "worker-cursor-auth-task")

        self.assertIn("--output-format", cmd)
        idx_fmt = cmd.index("--output-format")
        self.assertEqual(cmd[idx_fmt + 1], "json")

        prompt_arg = cmd[2]
        self.assertIn("CursorWorkerDriver e testes TDD", prompt_arg)
        self.assertIn("src/cursor/", prompt_arg)
        self.assertIn("tests/test_cursor_multiagent.py", prompt_arg)
        self.assertIn("30-multiagent-boss-worker.mdc", prompt_arg)
        self.assertIn("SHARED_CURSOR_MEM", prompt_arg)

    def test_model_resolution(self):
        pro_task = dict(self.sample_task, model="gemini-4-argon", effort="high")
        cmd = self.driver.build_worker_command(pro_task)
        idx_m = cmd.index("--model")
        self.assertEqual(cmd[idx_m + 1], "claude-3-5-sonnet")

    def test_build_worker_payload_structure(self):
        payload = self.driver.build_worker_payload(self.sample_task, shared_memory="SHARED_MEM")
        self.assertEqual(payload["host"], "cursor")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "claude-3-5-haiku")
        self.assertIn("command", payload)
        self.assertIsInstance(payload["command"], list)
        self.assertIn("prompt", payload)


class TestCursorDriverFactory(unittest.TestCase):
    """Test get_worker_driver factory resolution for cursor."""

    def test_factory_returns_cursor_driver(self):
        d = get_worker_driver("cursor")
        self.assertIsInstance(d, CursorWorkerDriver)


class TestOrchestratorCursorIntegration(unittest.TestCase):
    """Test integration between manifest validation and Cursor driver."""

    def test_manifest_supports_cursor_host(self):
        manifest_data = {
            "mission_id": "feat-cursor-01",
            "feature_name": "Suporte Multiagente Cursor",
            "host": "cursor",
            "tasks": [
                {
                    "task_id": "task-cur-1",
                    "subagent": "builder",
                    "model": "flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/"],
                    "objective": "Cursor Build Task",
                    "verification_cmd": "exit 0",
                }
            ],
        }
        validated = validate_mission_manifest(manifest_data)
        self.assertEqual(validated.get("host"), "cursor")

    def test_prepare_subagent_payload_with_cursor_host(self):
        task = {
            "task_id": "task-cur-2",
            "subagent": "builder",
            "model": "flash",
            "effort": "medium",
            "execution_group": 1,
            "allowed_paths": ["src/"],
            "objective": "Build cursor service",
            "verification_cmd": "pytest",
        }
        payload = prepare_subagent_payload(task, shared_memory="", host="cursor")
        self.assertEqual(payload["host"], "cursor")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "claude-3-5-haiku")


if __name__ == "__main__":
    unittest.main()
