#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from scripts.session_compactor import get_git_summary, update_project_memory


class TestSessionCompactor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_git_summary(self):
        status, diff = get_git_summary()
        self.assertIsInstance(status, str)
        self.assertIsInstance(diff, str)

    def test_update_project_memory_nonexistent_file(self):
        dummy_file = self.base_dir / "DOES_NOT_EXIST.md"
        result = update_project_memory("Teste", dummy_file)
        self.assertFalse(result)

    def test_update_project_memory_success(self):
        memory_file = self.base_dir / "PROJECT_MEMORY.md"
        initial_content = (
            "# Memória do Projeto\n\n"
            "## 1. Contexto Geral\n"
            "Info do projeto.\n\n"
            "## 2. Working Memory (Sessão Atual)\n"
            "Conteúdo inicial.\n"
        )
        memory_file.write_text(initial_content, encoding="utf-8")

        result = update_project_memory("Otimizações de tokens aplicadas.", memory_file)
        self.assertTrue(result)

        updated_text = memory_file.read_text(encoding="utf-8")
        self.assertIn("Checkpoint de Sessão", updated_text)
        self.assertIn("Otimizações de tokens aplicadas.", updated_text)


if __name__ == "__main__":
    unittest.main()
