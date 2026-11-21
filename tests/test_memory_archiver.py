#!/usr/bin/env python3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.memory_archiver import (
    parse_episodic_entries,
    archive_memory,
    check_memory_budget,
    spill_sections_to_details,
    split_top_level_sections,
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


class TestMemoryByteBudget(unittest.TestCase):
    """A3: o teto de bytes governa a rotação, não apenas a contagem de entregas."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.memory_file = self.temp_path / "PROJECT_MEMORY.md"
        self.history_file = self.temp_path / "archive" / "HISTORY.md"
        self.details_file = self.temp_path / "details" / "EPISODES.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _sample(self, entry_count: int) -> str:
        header = (
            "# Memória\n\n"
            "## 3. Recent Changes & Activity Log (Episodic)\n\n"
        )
        entries = [
            f"| 2026-09-{i:02d} | `FEAT` | Entrega {i} " + ("x" * 120) + " | `src/m.py` | `PASS` |"
            for i in range(1, entry_count + 1)
        ]
        return header + "\n".join(entries) + "\n\n## 4. Lições\n- ok\n"

    def test_rotates_when_under_entry_count_but_over_byte_budget(self):
        self.memory_file.write_text(self._sample(4), encoding="utf-8")
        original_size = self.memory_file.stat().st_size

        retained, archived = archive_memory(
            self.memory_file,
            history_path=self.history_file,
            max_entries=10,
            max_bytes=original_size // 2,
            details_path=self.details_file,
        )

        self.assertGreater(archived, 0)
        self.assertLess(retained, 4)
        self.assertLessEqual(
            self.memory_file.stat().st_size, original_size // 2 + 200
        )
        self.assertTrue(self.details_file.is_file())
        self.assertIn("Entrega 4", self.details_file.read_text(encoding="utf-8"))

    def test_never_drops_the_most_recent_entry(self):
        self.memory_file.write_text(self._sample(3), encoding="utf-8")
        retained, archived = archive_memory(
            self.memory_file,
            history_path=self.history_file,
            max_entries=10,
            max_bytes=1,
        )
        self.assertEqual(retained, 1)
        self.assertEqual(archived, 2)
        self.assertIn("Entrega 1", self.memory_file.read_text(encoding="utf-8"))

    def test_byte_budget_disabled_preserves_entry_count_behaviour(self):
        self.memory_file.write_text(self._sample(3), encoding="utf-8")
        retained, archived = archive_memory(
            self.memory_file,
            history_path=self.history_file,
            max_entries=10,
            max_bytes=None,
        )
        self.assertEqual((retained, archived), (3, 0))


class TestSectionSpill(unittest.TestCase):
    """A3: quando o volume está nas seções semânticas, elas vão para details/."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.memory_file = self.root / "PROJECT_MEMORY.md"
        self.details = self.root / "details"
        self.memory_file.write_text(
            "# Memória\n\n"
            "## 1. Quick Summary\n- essencial\n\n"
            "## 3. Recent Changes\n| 2026-09-01 | entrega |\n\n"
            "## 4. Active Backlog\n- pendência crítica\n\n"
            "## 5. Architectural Decisions\n" + ("decisão longa " * 300) + "\n\n"
            "## 6. Procedural Lessons\n" + ("lição longa " * 300) + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_splits_sections_by_level_two_header(self):
        blocks = split_top_level_sections(self.memory_file.read_text(encoding="utf-8"))
        headers = [header for header, _ in blocks if header]
        self.assertEqual(len(headers), 5)
        self.assertIn("## 5. Architectural Decisions", headers)

    def test_spills_largest_unprotected_sections_until_budget(self):
        new_size, moved = spill_sections_to_details(
            self.memory_file, max_bytes=2000, details_dir=self.details
        )
        self.assertLessEqual(new_size, 2000)
        self.assertEqual(len(moved), 2)
        content = self.memory_file.read_text(encoding="utf-8")
        self.assertIn("## 1. Quick Summary", content)
        self.assertNotIn("decisão longa", content)
        self.assertNotIn("lição longa", content)
        self.assertIn("details/", content)
        self.assertTrue((self.details / moved[0]).is_file())

    def test_protected_sections_are_never_spilled(self):
        spill_sections_to_details(self.memory_file, max_bytes=10, details_dir=self.details)
        content = self.memory_file.read_text(encoding="utf-8")
        self.assertIn("essencial", content)
        self.assertIn("## 3. Recent Changes", content)
        self.assertIn("pendência crítica", content)

    def test_spill_dry_run_does_not_write(self):
        before = self.memory_file.read_text(encoding="utf-8")
        _, moved = spill_sections_to_details(
            self.memory_file, max_bytes=2000, details_dir=self.details, dry_run=True
        )
        self.assertTrue(moved)
        self.assertEqual(self.memory_file.read_text(encoding="utf-8"), before)
        self.assertFalse(self.details.exists())


class TestOrphanLogRotation(unittest.TestCase):
    """Memória que perdeu o cabeçalho `## 3.` não pode escapar da rotação."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.memory_file = self.root / "PROJECT_MEMORY.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _orphan_memory(self, rows: int) -> str:
        log = "\n".join(
            f"| 2026-10-{i:02d} | `FEAT/{i}` | Entrega {i} " + ("detalhe " * 40) + " |"
            for i in range(1, rows + 1)
        )
        return (
            "# Memória do Projeto\n\n"
            "> **Última Atualização:** 2026-10-31\n\n"
            "---\n\n" + log + "\n\n---\n\n"
            "## 4. Active Backlog\n- handoff crítico\n"
        )

    def test_orphan_log_is_rotated_and_gains_section_header(self):
        self.memory_file.write_text(self._orphan_memory(40), encoding="utf-8")
        original = self.memory_file.stat().st_size

        retained, archived = archive_memory(
            self.memory_file,
            history_path=self.root / "archive" / "HISTORY.md",
            max_entries=8,
            max_bytes=None,
        )

        self.assertEqual(retained, 8)
        self.assertEqual(archived, 32)
        content = self.memory_file.read_text(encoding="utf-8")
        self.assertIn("## 3. PROGRESSO", content)
        self.assertIn("handoff crítico", content)
        self.assertIn("Entrega 8 ", content)
        self.assertNotIn("Entrega 9 ", content)
        self.assertIn(
            "Entrega 40",
            (self.root / "archive" / "HISTORY.md").read_text(encoding="utf-8"),
        )
        self.assertLess(self.memory_file.stat().st_size, original)

    def test_orphan_log_respects_byte_budget(self):
        self.memory_file.write_text(self._orphan_memory(40), encoding="utf-8")
        archive_memory(
            self.memory_file,
            history_path=self.root / "archive" / "HISTORY.md",
            max_entries=8,
            max_bytes=2500,
        )
        self.assertLessEqual(self.memory_file.stat().st_size, 2700)
        self.assertIn("handoff crítico", self.memory_file.read_text(encoding="utf-8"))

    def test_orphan_entries_are_parseable_after_rotation(self):
        self.memory_file.write_text(self._orphan_memory(20), encoding="utf-8")
        archive_memory(
            self.memory_file,
            history_path=self.root / "archive" / "HISTORY.md",
            max_entries=5,
            max_bytes=None,
        )
        entries = parse_episodic_entries(self.memory_file.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 5)

    def test_file_without_entries_is_left_untouched(self):
        content = "# Memória\n\n## 1. Resumo\n- ok\n\n## 4. Backlog\n- item\n"
        self.memory_file.write_text(content, encoding="utf-8")
        retained, archived = archive_memory(
            self.memory_file,
            history_path=self.root / "archive" / "HISTORY.md",
            max_bytes=3000,
        )
        self.assertEqual((retained, archived), (0, 0))
        self.assertEqual(self.memory_file.read_text(encoding="utf-8"), content)


class TestArchiverExitCode(unittest.TestCase):
    """O CLI não pode declarar sucesso quando o teto de bytes não foi atingido."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.memory_file = self.root / "PROJECT_MEMORY.md"
        self.script = Path(__file__).resolve().parent.parent / "scripts" / "memory_archiver.py"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run(self):
        return subprocess.run(
            [sys.executable, str(self.script), "--file", str(self.memory_file)],
            capture_output=True,
            text=True,
        )

    def test_exits_three_when_protected_sections_exceed_budget(self):
        self.memory_file.write_text(
            "# Memória\n\n## 1. Resumo\n- essencial\n\n"
            "## 3. PROGRESSO\n| 2026-10-01 | entrega |\n\n"
            "## 4. Backlog\n" + ("pendência crítica " * 400) + "\n",
            encoding="utf-8",
        )
        proc = self._run()
        self.assertEqual(proc.returncode, 3)
        self.assertIn("Teto não atingido", proc.stderr)

    def test_exits_zero_when_within_budget(self):
        self.memory_file.write_text(
            "# Memória\n\n## 1. Resumo\n- essencial\n\n"
            "## 3. PROGRESSO\n| 2026-10-01 | entrega |\n",
            encoding="utf-8",
        )
        proc = self._run()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("dentro do orçamento", proc.stdout)


class TestMemoryBudgetWarning(unittest.TestCase):
    """O gate precisa sinalizar memória acima do orçamento sem bloquear."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.mem_dir = self.root / ".agents" / "memory"
        self.mem_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_no_warning_when_absent(self):
        self.assertEqual(check_memory_budget(self.root), "")

    def test_no_warning_when_within_budget(self):
        (self.mem_dir / "PROJECT_MEMORY.md").write_text("# ok\n", encoding="utf-8")
        self.assertEqual(check_memory_budget(self.root), "")

    def test_warns_when_over_budget(self):
        (self.mem_dir / "PROJECT_MEMORY.md").write_text("x" * 9000, encoding="utf-8")
        warning = check_memory_budget(self.root)
        self.assertIn("over_budget", warning)
        self.assertIn("xp memory", warning)


if __name__ == "__main__":
    unittest.main()
