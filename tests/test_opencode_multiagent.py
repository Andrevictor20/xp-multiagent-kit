#!/usr/bin/env python3
"""
tests/test_opencode_multiagent.py
TDD Suite for OpenCode Multi-Agent Engine Integration (Boss-Worker Pattern).
Covers:
- OpenCode configuration generation (opencode.json with agents, subagent_depth, default_agent)
- OpenCodeWorkerDriver command generation (opencode run --agent ... --auto --format json)
- Host-agnostic driver factory (get_worker_driver)
- Orchestration integration with host='opencode'
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.host_adapters import HostAdapters
from scripts.multiagent_drivers import (
    AntigravityWorkerDriver,
    BaseWorkerDriver,
    OpenCodeWorkerDriver,
    get_worker_driver,
)
from scripts.antigravity_multiagent import (
    prepare_subagent_payload,
    validate_mission_manifest,
)


class TestOpenCodeHostAdapter(unittest.TestCase):
    """Test opencode.json generation with complete subagents block."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        self.kit_dir = Path(__file__).resolve().parent.parent
        self.adapter = HostAdapters(kit_dir=self.kit_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_install_opencode_provisions_agents_and_subagent_depth(self):
        self.adapter.install_opencode_project(self.project_dir)

        oc_json_path = self.project_dir / "opencode.json"
        self.assertTrue(oc_json_path.is_file(), "opencode.json deve existir")

        data = json.loads(oc_json_path.read_text(encoding="utf-8"))
        self.assertEqual(data.get("default_agent"), "orchestrator")
        self.assertEqual(data.get("subagent_depth"), 2)

        self.assertIn("agents", data)
        agents = data["agents"]

        # Deve conter pelo menos orchestrator e builder
        self.assertIn("orchestrator", agents)
        self.assertEqual(agents["orchestrator"]["mode"], "all")
        self.assertEqual(agents["orchestrator"]["prompt"], "{file:.opencode/agent/orchestrator.md}")

        self.assertIn("builder", agents)
        self.assertEqual(agents["builder"]["mode"], "subagent")
        self.assertEqual(agents["builder"]["prompt"], "{file:.opencode/agent/builder.md}")
        self.assertTrue(len(agents["builder"]["description"]) > 10)

        # Verifica outros agentes especialistas
        for ag_name in ("sentinel", "test-guardian", "refactor-warden", "navigator"):
            self.assertIn(ag_name, agents)
            self.assertEqual(agents[ag_name]["mode"], "subagent")


class TestOpenCodeWorkerDriver(unittest.TestCase):
    """Test OpenCodeWorkerDriver command and payload formatting."""

    def setUp(self):
        self.driver = OpenCodeWorkerDriver()
        self.sample_task = {
            "task_id": "auth-dto",
            "subagent": "builder",
            "model": "gemini-3.8-flash",
            "effort": "low",
            "execution_group": 1,
            "allowed_paths": ["src/dto/"],
            "objective": "Criar DTOs de autenticação com Pydantic",
            "verification_cmd": "pytest tests/test_dto.py",
        }

    def test_build_worker_command_contains_required_flags(self):
        cmd = self.driver.build_worker_command(self.sample_task, shared_memory="TOKEN_SPECS")

        self.assertEqual(cmd[0], "opencode")
        self.assertEqual(cmd[1], "run")

        self.assertIn("--agent", cmd)
        idx_agent = cmd.index("--agent")
        self.assertEqual(cmd[idx_agent + 1], "builder")

        self.assertIn("--auto", cmd)
        self.assertIn("--format", cmd)
        idx_fmt = cmd.index("--format")
        self.assertEqual(cmd[idx_fmt + 1], "json")

        self.assertIn("--model", cmd)

        # Último argumento deve ser o prompt contendo objetivo, allowed_paths e memória
        prompt_arg = cmd[-1]
        self.assertIn("Criar DTOs de autenticação", prompt_arg)
        self.assertIn("src/dto/", prompt_arg)
        self.assertIn("pytest tests/test_dto.py", prompt_arg)
        self.assertIn("TOKEN_SPECS", prompt_arg)

    def test_build_worker_payload_structure(self):
        payload = self.driver.build_worker_payload(self.sample_task, shared_memory="MEM_DATA")
        self.assertEqual(payload["host"], "opencode")
        self.assertEqual(payload["agent"], "builder")
        self.assertIn("command", payload)
        self.assertIsInstance(payload["command"], list)
        self.assertIn("prompt", payload)


class TestMultiAgentDriverFactory(unittest.TestCase):
    """Test get_worker_driver factory resolution."""

    def test_factory_returns_opencode_driver(self):
        d = get_worker_driver("opencode")
        self.assertIsInstance(d, OpenCodeWorkerDriver)

    def test_factory_returns_antigravity_driver(self):
        d = get_worker_driver("antigravity")
        self.assertIsInstance(d, AntigravityWorkerDriver)

    def test_factory_fallback_on_unknown(self):
        d = get_worker_driver("unknown-host")
        self.assertIsInstance(d, AntigravityWorkerDriver)


class TestOrchestratorOpenCodeIntegration(unittest.TestCase):
    """Test integration between manifest validation and host driver."""

    def test_manifest_supports_host_field(self):
        manifest_data = {
            "mission_id": "feat-opencode-01",
            "feature_name": "Suporte Multiagente OpenCode",
            "host": "opencode",
            "tasks": [
                {
                    "task_id": "task-01",
                    "subagent": "builder",
                    "model": "gemini-3.8-flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/"],
                    "objective": "Scaffold",
                    "verification_cmd": "python3 -c 'exit(0)'",
                }
            ],
        }
        validated = validate_mission_manifest(manifest_data)
        self.assertEqual(validated.get("host"), "opencode")

    def test_prepare_subagent_payload_with_opencode_host(self):
        task = {
            "task_id": "task-oc",
            "subagent": "builder",
            "model": "flash",
            "effort": "medium",
            "execution_group": 1,
            "allowed_paths": ["src/"],
            "objective": "Build service",
            "verification_cmd": "pytest",
        }
        payload = prepare_subagent_payload(task, shared_memory="", host="opencode")
        self.assertEqual(payload["host"], "opencode")
        self.assertEqual(payload["agent"], "builder")

    def test_cli_parser_accepts_host_flag(self):
        import argparse
        from scripts.antigravity_multiagent import main
        from unittest.mock import patch

        with patch("sys.argv", ["agy-orchestrate", "run", "--host", "opencode", "non_existent.json"]):
            ret = main()
            # Retorna 1 porque o manifesto não existe, mas comprova que o parser aceitou --host
            self.assertEqual(ret, 1)


if __name__ == "__main__":
    unittest.main()
