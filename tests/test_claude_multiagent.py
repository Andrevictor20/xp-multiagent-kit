#!/usr/bin/env python3
"""
tests/test_claude_multiagent.py
TDD Suite for Claude Code / Claude Desktop Multi-Agent Engine Integration (Boss-Worker Pattern).
Covers:
- Claude project provisioning (CLAUDE.md, .mcp.json, .claude/agents/*.md)
- ClaudeWorkerDriver command generation (claude -p ... --model ... --effort ... --permission-mode bypassPermissions --worktree ... --output-format json)
- Host-agnostic driver factory resolution for 'claude'
- Orchestration integration with host='claude'
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.host_adapters import HostAdapters, SUPPORTED_TARGETS
from scripts.multiagent_drivers import (
    BaseWorkerDriver,
    ClaudeWorkerDriver,
    get_worker_driver,
)
from scripts.antigravity_multiagent import (
    prepare_subagent_payload,
    validate_mission_manifest,
)


class TestClaudeHostAdapter(unittest.TestCase):
    """Test CLAUDE.md, .mcp.json and .claude/agents/*.md provisioning."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        self.kit_dir = Path(__file__).resolve().parent.parent
        self.adapter = HostAdapters(kit_dir=self.kit_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_claude_is_in_supported_targets(self):
        self.assertIn("claude", SUPPORTED_TARGETS)

    def test_install_claude_provisions_governance_and_agents(self):
        actions = self.adapter.install_claude_project(self.project_dir)
        self.assertTrue(len(actions) > 0)

        # 1. CLAUDE.md deve existir na raiz do projeto
        claude_md = self.project_dir / "CLAUDE.md"
        self.assertTrue(claude_md.is_file(), "CLAUDE.md deve ser criado na raiz")
        content = claude_md.read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", content)
        self.assertIn("Português", content)
        self.assertIn("TDD", content)

        # 2. .mcp.json deve existir na raiz do projeto
        mcp_json = self.project_dir / ".mcp.json"
        self.assertTrue(mcp_json.is_file(), ".mcp.json deve ser criado na raiz")
        mcp_data = json.loads(mcp_json.read_text(encoding="utf-8"))
        self.assertIn("mcpServers", mcp_data)
        self.assertIn("code-review-graph", mcp_data["mcpServers"])
        self.assertIn("open-design", mcp_data["mcpServers"])

        # 3. .claude/agents/ deve conter os 11 agentes especialistas
        agents_dir = self.project_dir / ".claude" / "agents"
        self.assertTrue(agents_dir.is_dir(), ".claude/agents/ deve ser um diretório")

        for ag_name in ("builder", "orchestrator", "sentinel", "test-guardian", "navigator"):
            ag_file = agents_dir / f"{ag_name}.md"
            self.assertTrue(ag_file.is_file(), f"Agente {ag_name}.md deve existir em .claude/agents/")
            ag_text = ag_file.read_text(encoding="utf-8")
            self.assertIn("---", ag_text)
            self.assertIn("name:", ag_text)
            self.assertIn("description:", ag_text)


class TestClaudeWorkerDriver(unittest.TestCase):
    """Test ClaudeWorkerDriver command and payload formatting."""

    def setUp(self):
        self.driver = ClaudeWorkerDriver()
        self.sample_task = {
            "task_id": "auth-service-task",
            "subagent": "builder",
            "model": "gemini-3.8-flash",
            "effort": "low",
            "execution_group": 1,
            "allowed_paths": ["src/auth/"],
            "objective": "Implementar AuthService em TDD",
            "verification_cmd": "pytest tests/test_auth.py",
        }

    def test_build_worker_command_contains_required_flags(self):
        cmd = self.driver.build_worker_command(self.sample_task, shared_memory="SHARED_CONTRACTS")

        self.assertEqual(cmd[0], "claude")
        self.assertIn("-p", cmd)

        self.assertIn("--model", cmd)
        idx_m = cmd.index("--model")
        # Flash deve mapear para haiku
        self.assertEqual(cmd[idx_m + 1], "haiku")

        self.assertIn("--effort", cmd)
        idx_eff = cmd.index("--effort")
        self.assertEqual(cmd[idx_eff + 1], "low")

        self.assertIn("--permission-mode", cmd)
        idx_perm = cmd.index("--permission-mode")
        self.assertEqual(cmd[idx_perm + 1], "bypassPermissions")

        self.assertIn("--worktree", cmd)
        idx_wt = cmd.index("--worktree")
        self.assertEqual(cmd[idx_wt + 1], "worker-auth-service-task")

        self.assertIn("--output-format", cmd)
        idx_fmt = cmd.index("--output-format")
        self.assertEqual(cmd[idx_fmt + 1], "json")

        # Prompt deve conter objetivo, allowed_paths e memória
        idx_p = cmd.index("-p")
        prompt_arg = cmd[idx_p + 1]
        self.assertIn("Implementar AuthService em TDD", prompt_arg)
        self.assertIn("src/auth/", prompt_arg)
        self.assertIn("pytest tests/test_auth.py", prompt_arg)
        self.assertIn("SHARED_CONTRACTS", prompt_arg)

    def test_model_resolution(self):
        # Pro / Argon deve mapear para sonnet
        pro_task = dict(self.sample_task, model="gemini-4-argon", effort="high")
        cmd = self.driver.build_worker_command(pro_task)
        idx_m = cmd.index("--model")
        self.assertEqual(cmd[idx_m + 1], "sonnet")
        idx_eff = cmd.index("--effort")
        self.assertEqual(cmd[idx_eff + 1], "high")

    def test_build_worker_payload_structure(self):
        payload = self.driver.build_worker_payload(self.sample_task, shared_memory="MEM")
        self.assertEqual(payload["host"], "claude")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "haiku")
        self.assertEqual(payload["effort"], "low")
        self.assertIn("command", payload)
        self.assertIsInstance(payload["command"], list)


class TestClaudeDriverFactory(unittest.TestCase):
    """Test get_worker_driver factory resolution for claude."""

    def test_factory_returns_claude_driver(self):
        d = get_worker_driver("claude")
        self.assertIsInstance(d, ClaudeWorkerDriver)


class TestOrchestratorClaudeIntegration(unittest.TestCase):
    """Test integration between manifest validation and Claude driver."""

    def test_manifest_supports_claude_host(self):
        manifest_data = {
            "mission_id": "feat-claude-01",
            "feature_name": "Suporte Multiagente Claude",
            "host": "claude",
            "tasks": [
                {
                    "task_id": "task-01",
                    "subagent": "builder",
                    "model": "flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/"],
                    "objective": "Build",
                    "verification_cmd": "exit 0",
                }
            ],
        }
        validated = validate_mission_manifest(manifest_data)
        self.assertEqual(validated.get("host"), "claude")

    def test_prepare_subagent_payload_with_claude_host(self):
        task = {
            "task_id": "task-c1",
            "subagent": "builder",
            "model": "flash",
            "effort": "medium",
            "execution_group": 1,
            "allowed_paths": ["src/"],
            "objective": "Build service",
            "verification_cmd": "pytest",
        }
        payload = prepare_subagent_payload(task, shared_memory="", host="claude")
        self.assertEqual(payload["host"], "claude")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "haiku")


if __name__ == "__main__":
    unittest.main()
