import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestMemorySearch(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.memory_dir = self.workspace / ".agents" / "memory"
        self.memory_dir.mkdir(parents=True)

        # Mock PROJECT_MEMORY.md
        self.proj_memory = self.memory_dir / "PROJECT_MEMORY.md"
        self.proj_memory.write_text(
            "# Project Memory\n\n"
            "## 3. Recent Changes\n"
            "| 2026-09-26 | `FEAT` | Implementação do motor agy-git-ops e context compactor | scripts/agy-git-ops | PASS |\n"
            "| 2026-09-25 | `FIX`  | Correção de recursao infinita no agy CLI | scripts/agy_effort_router.py | PASS |\n\n"
            "## 4. Procedural Memory & Lessons Learned\n"
            "- `[L-001]` **Regra de Ouro**: Use sempre o menor número de agentes e etapas.\n"
            "- `[L-015]` **Recursão no CLI**: Validar magic bytes ELF para evitar chamadas cíclicas.\n"
            "- `[L-020]` **Compressão de Tokens**: Nunca despejar logs brutos de CI/CD.\n",
            encoding="utf-8",
        )

        # Mock archive/HISTORY.md
        archive_dir = self.memory_dir / "archive"
        archive_dir.mkdir()
        self.history = archive_dir / "HISTORY.md"
        self.history.write_text(
            "# History Archive\n\n"
            "| 2026-09-20 | `FEAT` | Implementação do Smart Quota Failover | scripts/failover.py | PASS |\n"
            "| 2026-09-18 | `FEAT` | Setup inicial de TDD e Fast Bootstrap | scripts/bootstrap.py | PASS |\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_index_and_search_lessons(self):
        from scripts.memory_search import build_or_update_index, search_memory, get_db_path

        db_path = get_db_path(self.workspace)
        stats = build_or_update_index(self.workspace)
        self.assertTrue(db_path.is_file())
        self.assertGreater(stats["indexed_items"], 0)

        # Search for "recursao"
        results = search_memory(self.workspace, "recursao")
        self.assertTrue(len(results) > 0)
        first = results[0]
        self.assertIn("L-015", first["content"])

    def test_search_history(self):
        from scripts.memory_search import build_or_update_index, search_memory

        build_or_update_index(self.workspace)
        results = search_memory(self.workspace, "Smart Quota Failover")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["category"], "history")

    def test_incremental_indexing_skips_unchanged_files(self):
        from scripts.memory_search import build_or_update_index

        stats1 = build_or_update_index(self.workspace)
        self.assertGreater(stats1["indexed_items"], 0)

        # Second call without modifying files should be 0 items reindexed
        stats2 = build_or_update_index(self.workspace)
        self.assertEqual(stats2["reindexed_files"], 0)

    def test_format_results_compact(self):
        from scripts.memory_search import build_or_update_index, search_memory, format_search_results

        build_or_update_index(self.workspace)
        results = search_memory(self.workspace, "Regra de Ouro")
        formatted = format_search_results(results, query="Regra de Ouro")
        self.assertIn("L-001", formatted)
        self.assertLess(len(formatted.split("\n")), 20)


if __name__ == "__main__":
    unittest.main()
