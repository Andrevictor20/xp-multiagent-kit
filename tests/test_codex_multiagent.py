#!/usr/bin/env python3
"""
tests/test_codex_multiagent.py
TDD Suite for OpenAI Codex CLI Multi-Agent Engine Integration (Boss-Worker Pattern).
Covers:
- Codex project provisioning (.codex/rules/default.rules, .codex/config.toml, instructions.md, mcp.json)
- CodexWorkerDriver command generation (codex exec ... -m ... -c model_reasoning_effort=... --sandbox workspace-write --approve-for-me --worktree)
- Host-agnostic driver factory resolution for 'codex'
- Orchestration integration with host='codex'
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.host_adapters import HostAdapters
from scripts.multiagent_drivers import (
    BaseWorkerDriver,
    CodexWorkerDriver,
    get_worker_driver,
)
from scripts.antigravity_multiagent import (
    prepare_subagent_payload,
    validate_mission_manifest,
)


class TestCodexHostAdapter(unittest.TestCase):
    """Test Codex configuration generation (.codex/rules/default.rules, config.toml, instructions.md)."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        self.kit_dir = Path(__file__).resolve().parent.parent
        self.adapter = HostAdapters(kit_dir=self.kit_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_install_codex_provisions_governance_and_sandbox_rules(self):
        actions = self.adapter.install_codex_project(self.project_dir)
        self.assertTrue(len(actions) > 0)

        codex_dir = self.project_dir / ".codex"
        self.assertTrue(codex_dir.is_dir(), ".codex deve ser criado")

        # 1. instructions.md e rules/xp-governance.md
        inst_md = codex_dir / "instructions.md"
        self.assertTrue(inst_md.is_file(), "instructions.md deve existir")

        gov_md = codex_dir / "rules" / "xp-governance.md"
        self.assertTrue(gov_md.is_file(), "rules/xp-governance.md deve existir")

        # 2. .codex/rules/default.rules (Starlark execution policy para aprovação de testes)
        default_rules = codex_dir / "rules" / "default.rules"
        self.assertTrue(default_rules.is_file(), "rules/default.rules deve existir")
        rules_content = default_rules.read_text(encoding="utf-8")
        self.assertIn("prefix_rule", rules_content)
        self.assertIn("pytest", rules_content)
        self.assertIn("unittest", rules_content)

        # 3. .codex/config.toml (Configuração de MCPs e modelo padrão)
        cfg_toml = codex_dir / "config.toml"
        self.assertTrue(cfg_toml.is_file(), "config.toml deve existir")
        cfg_content = cfg_toml.read_text(encoding="utf-8")
        self.assertIn("[mcp_servers", cfg_content)
        self.assertIn("code_review_graph", cfg_content)


class TestCodexWorkerDriver(unittest.TestCase):
    """Test CodexWorkerDriver command and payload formatting."""

    def setUp(self):
        self.driver = CodexWorkerDriver()
        self.sample_task = {
            "task_id": "auth-tokens",
            "subagent": "builder",
            "model": "gemini-3.8-flash",
            "effort": "low",
            "execution_group": 1,
            "allowed_paths": ["src/auth/"],
            "objective": "Implementar gerador de JWT e rotação de refresh token",
            "verification_cmd": "pytest tests/test_tokens.py",
        }

    def test_build_worker_command_contains_required_flags(self):
        cmd = self.driver.build_worker_command(self.sample_task, shared_memory="CODEX_MEM")

        self.assertEqual(cmd[0], "codex")
        self.assertEqual(cmd[1], "exec")

        self.assertIn("-m", cmd)
        idx_m = cmd.index("-m")
        # Flash deve mapear para gpt-5.6-luna
        self.assertEqual(cmd[idx_m + 1], "gpt-5.6-luna")

        self.assertIn("-c", cmd)
        idx_c = cmd.index("-c")
        self.assertIn("model_reasoning_effort", cmd[idx_c + 1])
        self.assertIn("low", cmd[idx_c + 1])

        self.assertIn("--sandbox", cmd)
        idx_sb = cmd.index("--sandbox")
        self.assertEqual(cmd[idx_sb + 1], "workspace-write")

        self.assertIn("--approve-for-me", cmd)
        self.assertIn("--worktree", cmd)
        self.assertIn("--ephemeral", cmd)

        self.assertIn("-o", cmd)
        idx_o = cmd.index("-o")
        self.assertTrue(cmd[idx_o + 1].endswith(".md"))

        prompt_arg = cmd[2]
        self.assertIn("gerador de JWT", prompt_arg)
        self.assertIn("src/auth/", prompt_arg)
        self.assertIn("pytest tests/test_tokens.py", prompt_arg)
        self.assertIn("CODEX_MEM", prompt_arg)

    def test_model_resolution(self):
        # Argon / Pro / High deve mapear para gpt-5.6-terra
        pro_task = dict(self.sample_task, model="gemini-4-argon", effort="high")
        cmd = self.driver.build_worker_command(pro_task)
        idx_m = cmd.index("-m")
        self.assertEqual(cmd[idx_m + 1], "gpt-5.6-terra")
        idx_c = cmd.index("-c")
        self.assertIn('model_reasoning_effort="high"', cmd[idx_c + 1])

    def test_build_worker_payload_structure(self):
        payload = self.driver.build_worker_payload(self.sample_task, shared_memory="MEM")
        self.assertEqual(payload["host"], "codex")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "gpt-5.6-luna")
        self.assertEqual(payload["effort"], "low")
        self.assertIn("command", payload)
        self.assertIsInstance(payload["command"], list)


class TestCodexDriverFactory(unittest.TestCase):
    """Test get_worker_driver factory resolution for codex."""

    def test_factory_returns_codex_driver(self):
        d = get_worker_driver("codex")
        self.assertIsInstance(d, CodexWorkerDriver)


class TestOrchestratorCodexIntegration(unittest.TestCase):
    """Test integration between manifest validation and Codex driver."""

    def test_manifest_supports_codex_host(self):
        manifest_data = {
            "mission_id": "feat-codex-01",
            "feature_name": "Suporte Multiagente Codex",
            "host": "codex",
            "tasks": [
                {
                    "task_id": "task-cx",
                    "subagent": "builder",
                    "model": "flash",
                    "effort": "low",
                    "execution_group": 1,
                    "allowed_paths": ["src/"],
                    "objective": "Codex Task",
                    "verification_cmd": "exit 0",
                }
            ],
        }
        validated = validate_mission_manifest(manifest_data)
        self.assertEqual(validated.get("host"), "codex")

    def test_prepare_subagent_payload_with_codex_host(self):
        task = {
            "task_id": "task-cx1",
            "subagent": "builder",
            "model": "flash",
            "effort": "medium",
            "execution_group": 1,
            "allowed_paths": ["src/"],
            "objective": "Build service",
            "verification_cmd": "pytest",
        }
        payload = prepare_subagent_payload(task, shared_memory="", host="codex")
        self.assertEqual(payload["host"], "codex")
        self.assertEqual(payload["agent"], "builder")
        self.assertEqual(payload["model"], "gpt-5.6-luna")


if __name__ == "__main__":
    unittest.main()
