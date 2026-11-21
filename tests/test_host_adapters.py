#!/usr/bin/env python3
"""tests/test_host_adapters.py — Regressão do contexto base do OpenCode.

O `instructions` do opencode é inlinado inteiro a cada sessão. Código-fonte de
hook (12,5 KB) não é regra de conduta e não deve entrar nesse bloco.
"""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.host_adapters import HostAdapters


class TestOpenCodeInstructions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.kit_dir = self.root / "kit"
        (self.kit_dir / ".agents").mkdir(parents=True)
        (self.kit_dir / "AGENTS.md").write_text("# Kit\n", encoding="utf-8")
        self.project = self.root / "project"
        self.project.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _install(self):
        adapter = HostAdapters(self.kit_dir, home_dir=self.root / "home")
        adapter.install_opencode_project(self.project)
        return json.loads((self.project / "opencode.json").read_text(encoding="utf-8"))

    def test_instructions_contain_only_governance_files(self):
        data = self._install()
        self.assertEqual(
            data["instructions"],
            [
                "AGENTS.md",
                ".agents/memory/PROJECT_MEMORY.md",
                ".agents/policies/*.md",
            ],
        )

    def test_instructions_never_reference_source_code(self):
        data = self._install()
        self.assertFalse(
            [entry for entry in data["instructions"] if entry.endswith(".py")]
        )

    def test_default_agent_and_subagent_depth_preserved(self):
        data = self._install()
        self.assertEqual(data["default_agent"], "orchestrator")
        self.assertEqual(data["subagent_depth"], 2)


if __name__ == "__main__":
    unittest.main()
