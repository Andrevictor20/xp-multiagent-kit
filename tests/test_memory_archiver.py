#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from scripts.memory_archiver import (
    parse_episodic_entries,
    archive_memory,
    DEFAULT_MAX_EPISODIC_ENTRIES,
)


class TestMemoryArchiver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.memory_file = self.temp_path / "PROJECT_MEMORY.md"
        self.history_file = self.temp_path / "archive" / "HISTORY.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _generate_sample_memory(self, entry_count: int) -> str:
        header = (
            "# 🧠 Project Memory & Context Snapshot\n\n"
            "> **Última Atualização:** 2026-09-26 12:00\n"
            "> **Status Geral:** STABLE\n\n"
            "---\n\n"
            "## 1. Quick Project Summary (Semantic)\n"
            "- Sumário de teste do projeto.\n\n"
            "---\n\n"
            "## 2. Current Health & System Status\n"
            "- Status operacional.\n\n"
            "---\n\n"
            "## 3. Recent Changes & Activity Log (Episodic - Sliding Window: 5-10 Entregas)\n\n"
        )
        entries = []
        for i in range(1, entry_count + 1):
            entries.append(
                f"| 2026-09-{i:02d} | `FEAT` | Descrição da funcionalidade número {i} com detalhes | `src/mod_{i}.py` | `PASS` |"
            )
        
        footer = (
            "\n\n---\n\n"
            "## 4. Architectural Decisions & Procedural Lessons\n"
            "- Lições aprendidas de teste.\n"
        )
        return header + "\n".join(entries) + footer

    def test_parse_episodic_entries(self):
        content = self._generate_sample_memory(5)
        entries = parse_episodic_entries(content)
        self.assertEqual(len(entries), 5)
        self.assertIn("funcionalidade número 1", entries[0])
        self.assertIn("funcionalidade número 5", entries[4])

    def test_no_archive_when_under_limit(self):
        content = self._generate_sample_memory(5)
        self.memory_file.write_text(content, encoding="utf-8")

        retained, archived = archive_memory(
            self.memory_file,
            self.history_file,
            max_entries=8,
        )

        self.assertEqual(retained, 5)
        self.assertEqual(archived, 0)
        self.assertFalse(self.history_file.exists())
        self.assertEqual(self.memory_file.read_text(encoding="utf-8"), content)

    def test_archive_when_exceeding_limit(self):
        content = self._generate_sample_memory(14)
        self.memory_file.write_text(content, encoding="utf-8")

        retained, archived = archive_memory(
            self.memory_file,
            self.history_file,
            max_entries=8,
        )

        self.assertEqual(retained, 8)
        self.assertEqual(archived, 6)

        # Verifica PROJECT_MEMORY.md podado
        new_memory_content = self.memory_file.read_text(encoding="utf-8")
        new_entries = parse_episodic_entries(new_memory_content)
        self.assertEqual(len(new_entries), 8)
        self.assertIn("funcionalidade número 1", new_entries[0])
        self.assertIn("funcionalidade número 8", new_entries[7])
        self.assertIn("## 1. Quick Project Summary", new_memory_content)
        self.assertIn("## 4. Architectural Decisions", new_memory_content)

        # Verifica HISTORY.md com as entradas antigas
        self.assertTrue(self.history_file.exists())
        history_content = self.history_file.read_text(encoding="utf-8")
        self.assertIn("funcionalidade número 9", history_content)
        self.assertIn("funcionalidade número 14", history_content)
        self.assertNotIn("funcionalidade número 1 com", history_content)

    def test_idempotent_rotation(self):
        content = self._generate_sample_memory(12)
        self.memory_file.write_text(content, encoding="utf-8")

        # Primeira rotação: 12 -> 8 (4 arquivadas)
        archive_memory(self.memory_file, self.history_file, max_entries=8)
        
        # Segunda rotação sem novas adições
        retained, archived = archive_memory(self.memory_file, self.history_file, max_entries=8)
        self.assertEqual(retained, 8)
        self.assertEqual(archived, 0)

    def test_archive_subsection_blocks(self):
        header = "# Project Memory\n\n## 3. Working Memory\n\n"
        blocks = [f"### 3.{i}. Subseção número {i}\nDetalhes do passo {i}\n" for i in range(12, 0, -1)]
        footer = "\n## 4. Lessons\n- Lição\n"
        content = header + "\n".join(blocks) + footer
        self.memory_file.write_text(content, encoding="utf-8")

        retained, archived = archive_memory(self.memory_file, self.history_file, max_entries=8)
        self.assertEqual(retained, 8)
        self.assertEqual(archived, 4)

        new_content = self.memory_file.read_text(encoding="utf-8")
        self.assertIn("### 3.12", new_content)
        self.assertIn("### 3.5", new_content)
        self.assertNotIn("### 3.4", new_content)

        history_content = self.history_file.read_text(encoding="utf-8")
        self.assertIn("### 3.4", history_content)
        self.assertIn("### 3.1", history_content)


if __name__ == "__main__":
    unittest.main()
