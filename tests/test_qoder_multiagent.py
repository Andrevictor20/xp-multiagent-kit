#!/usr/bin/env python3
"""
tests/test_qoder_multiagent.py
TDD Suite for Qoder Multi-Agent Engine Integration (Boss-Worker Pattern).
Covers:
- Qoder project provisioning (.qoder/rules/xp-governance.md, .qoder/mcp.json, .qoder/agents/*.md)
- QoderWorkerDriver headless command generation (qoder -p <prompt> -m <model> --yolo -o json -w <worktree>)
- Host-agnostic driver factory resolution for 'qoder'
- Orchestration integration with host='qoder'
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.host_adapters import HostAdapters, SUPPORTED_TARGETS
from scripts.multiagent_drivers import (
    BaseWorkerDriver,
    QoderWorkerDriver,
    get_worker_driver,
)
from scripts.antigravity_multiagent import (
    prepare_subagent_payload,
    validate_mission_manifest,
)


class TestQoderHostAdapter(unittest.TestCase):
    """Test Qoder configuration, MCP, and specialist agents provisioning in .qoder/agents/."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        self.kit_dir = Path(__file__).resolve().parent.parent
        self.adapter = HostAdapters(kit_dir=self.kit_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_qoder_is_in_supported_targets(self):
        self.assertIn("qoder", SUPPORTED_TARGETS)

    def test_install_qoder_provisions_governance_and_agents(self):
        actions = self.adapter.install_qoder_project(self.project_dir)
        self.assertTrue(len(actions) > 0)

        # 1. .qoder/rules/xp-governance.md deve existir
        gov_file = self.project_dir / ".qoder" / "rules" / "xp-governance.md"
        self.assertTrue(gov_file.is_file(), ".qoder/rules/xp-governance.md deve existir")
        gov_text = gov_file.read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", gov_text)

        # 2. .qoder/mcp.json deve existir
        mcp_file = self.project_dir / ".qoder" / "mcp.json"
        self.assertTrue(mcp_file.is_file(), ".qoder/mcp.json deve existir")
        mcp_data = json.loads(mcp_file.read_text(encoding="utf-8"))
        self.assertIn("mcpServers", mcp_data)
        self.assertIn("code-review-graph", mcp_data["mcpServers"])

        # 3. .qoder/agents/ deve conter os subagentes especialistas (6 nucleares)
        agents_dir = self.project_dir / ".qoder" / "agents"
        self.assertTrue(agents_dir.is_dir(), ".qoder/agents deve ser criado como diretório")

        for ag_name in ("builder", "orchestrator", "sentinel", "reviewer", "designer", "shipper"):
            ag_file = agents_dir / f"{ag_name}.md"
            self.assertTrue(ag_file.is_file(), f"Agente {ag_name}.md deve existir em .qoder/agents/")
            content = ag_file.read_text(encoding="utf-8")
            self.assertIn("---", content)
            self.assertIn("name:", content)


class TestQoderWorkerDriver(unittest.TestCase):
    """Test QoderWorkerDriver headless command (qoder -p ... -m ... --yolo -o json -w ...)."""

    def setUp(self):
        self.driver = QoderWorkerDriver()
        self.sample_task = {
            "task_id": "qoder-service-task",
            "subagent": "builder",
            "model": "gemini-3.8-flash",
            "effort": "low",
            "execution_group": 1,
            "allowed_paths": ["src/qoder/"],
            "objective": "Implementar QoderWorkerDriver e testes TDD",
            "verification_cmd": "python3 -m unittest tests/test_qoder_multiagent.py",
        }

    def test_build_worker_command_contains_required_flags(self):
        cmd = self.driver.build_worker_command(self.sample_task, shared_memory="SHARED_QODER_MEM")

        self.assertEqual(cmd[0], "qoder")
        self.assertIn("-p", cmd)
        idx_p = cmd.index("-p")
        prompt_arg = cmd[idx_p + 1]

        self.assertIn("-m", cmd)
        idx_m = cmd.index("-m")
        self.assertEqual(cmd[idx_m + 1], "gemini-2.5-flash")

        self.assertIn("--yolo", cmd)

        self.assertIn("-o", cmd)
        idx_o = cmd.index("-o")
        self.assertEqual(cmd[idx_o + 1], "json")

        self.assertIn("-w", cmd)
        idx_w = cmd.index("-w")
        self.assertEqual(cmd[idx_w + 1], "worker-qoder-service-task")

        # Prompt deve conter objetivo, subagente, escopo, verificação e referência a .qoder/agents/
        self.assertIn("QoderWorkerDriver e testes TDD", prompt_arg)
        self.assertIn("src/qoder/", prompt_arg)
        self.assertIn("tests/test_qoder_multiagent.py", prompt_arg)
        self.assertIn(".qoder/agents/", prompt_arg)
        self.assertIn("SHARED_QODER_MEM", prompt_arg)

    def test_model_resolution(self):
        pro_task = dict(self.sample_task, model="gemini-4-argon", effort="high")
        cmd = self.driver.build_worker_command(pro_task)
        idx_m = cmd.index("-m")
        self.assertEqual(cmd[idx_m + 1], "gemini-2.5-pro")

    def test_build_worker_payload_structure(self):
        payload = self.driver.build_worker_payload(self.sample_task, shared_memory="SHARED_MEM")
        self.assertEqual(payload["host"], "qoder")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "gemini-2.5-flash")
        self.assertIn("command", payload)
        self.assertIsInstance(payload["command"], list)
        self.assertIn("prompt", payload)


class TestQoderDriverFactory(unittest.TestCase):
    """Test get_worker_driver factory resolution for qoder."""

    def test_factory_returns_qoder_driver(self):
        d = get_worker_driver("qoder")
        self.assertIsInstance(d, QoderWorkerDriver)


class TestOrchestratorQoderIntegration(unittest.TestCase):
    """Test integration between manifest validation and Qoder driver."""

    def test_manifest_supports_qoder_host(self):
        manifest_data = {
            "mission_id": "feat-qoder-01",
            "feature_name": "Suporte Multiagente Qoder",
            "host": "qoder",
            "tasks": [
                {
                    "task_id": "task-qod-1",
                    "subagent": "builder",
                    "model": "flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/"],
                    "objective": "Qoder Build Task",
                    "verification_cmd": "exit 0",
                }
            ],
        }
        validated = validate_mission_manifest(manifest_data)
        self.assertEqual(validated.get("host"), "qoder")

    def test_prepare_subagent_payload_with_qoder_host(self):
        task = {
            "task_id": "task-qod-2",
            "subagent": "builder",
            "model": "flash",
            "effort": "medium",
            "execution_group": 1,
            "allowed_paths": ["src/"],
            "objective": "Build qoder service",
            "verification_cmd": "pytest",
        }
        payload = prepare_subagent_payload(task, shared_memory="", host="qoder")
        self.assertEqual(payload["host"], "qoder")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "gemini-2.5-flash")


if __name__ == "__main__":
    unittest.main()
