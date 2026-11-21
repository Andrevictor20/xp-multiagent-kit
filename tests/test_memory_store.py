#!/usr/bin/env python3
"""tests/test_memory_store.py — TDD para Memória Multi-Repositório (user: + repo: + session:)
e auto-consolidação determinística inspirada no Google ADK.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestScopedMultiRepoMemory(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.user_dir = self.root / "user_memory"
        self.repo_a = self.root / "repo_a"
        self.repo_b = self.root / "repo_b"
        for repo, title in ((self.repo_a, "Repo Alpha"), (self.repo_b, "Repo Beta")):
            mem_dir = repo / ".agents" / "memory"
            mem_dir.mkdir(parents=True)
            (mem_dir / "PROJECT_MEMORY.md").write_text(
                f"# Project Memory — {title}\n\n"
                "## 1. FATOS\n"
                f"- Stack do {title}: Python 3.11\n\n"
                "## 2. DECISÕES\n"
                f"- **Banco {title}:** Usar PostgreSQL com índices parciais.\n\n"
                "## 3. PROGRESSO\n"
                "- **2026-11-20**: Setup inicial concluído.\n\n"
                "## 4. LIÇÕES & REGRAS 'NEVER'\n"
                "- `never` usar sleep arbitrário em testes de integração.\n\n"
                "## 5. TENTATIVAS QUE FALHARAM (DEAD-ENDS)\n"
                f"- [{title}] Regex gulosa causou backtracking catastrófico no parser.\n",
                encoding="utf-8",
            )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_indexes_dead_ends_and_never_rules_in_fts5(self) -> None:
        from scripts.memory_search import search_memory

        dead = search_memory(self.repo_a, "backtracking catastrófico", scope="repo", user_dir=self.user_dir)
        self.assertTrue(dead, "Dead-Ends da seção 5 devem ser indexados no FTS5")
        self.assertEqual(dead[0]["category"], "dead_end")
        self.assertEqual(dead[0]["scope"], "repo")

        never = search_memory(self.repo_a, "sleep arbitrário", scope="repo", user_dir=self.user_dir)
        self.assertTrue(never, "Regras 'never' da seção 4 devem ser indexadas no FTS5")
        self.assertEqual(never[0]["category"], "never")

    def test_user_scope_shared_across_repos_while_repo_stays_isolated(self) -> None:
        from scripts.memory_store import promote_memory
        from scripts.memory_search import search_memory

        res = promote_memory(
            "Sempre configurar WAL mode e busy_timeout=5000 no SQLite em Linux.",
            scope="user",
            category="lesson",
            user_dir=self.user_dir,
        )
        self.assertTrue(res["added"])
        self.assertEqual(res["scope"], "user")

        # Repo B deve enxergar a lição promovida no escopo user:
        hits_b = search_memory(self.repo_b, "busy_timeout SQLite", scope="all", user_dir=self.user_dir)
        self.assertTrue(hits_b, "Repo B deve recuperar memória do escopo user:")
        self.assertEqual(hits_b[0]["scope"], "user")

        # Repo B NÃO deve vazar dados específicos do Repo A
        leak = search_memory(self.repo_b, "Alpha", scope="all", user_dir=self.user_dir)
        self.assertEqual(leak, [], "Memória do Repo A não pode vazar para o Repo B")

    def test_promote_memory_deduplicates_identical_entries(self) -> None:
        from scripts.memory_store import promote_memory

        first = promote_memory("Nunca usar eval em input externo.", scope="user", category="never", user_dir=self.user_dir)
        second = promote_memory("Nunca usar eval em input externo.", scope="user", category="never", user_dir=self.user_dir)
        self.assertTrue(first["added"])
        self.assertFalse(second["added"])
        self.assertTrue(second["duplicate"])

    def test_consolidate_session_promotes_dead_ends_and_never_rules(self) -> None:
        from scripts.memory_store import consolidate_session_memory
        from scripts.xp_contract import add_never, init_contract, record_dead_end

        rt_dir = self.repo_a / ".agents" / "runtime"
        with patch.dict(os.environ, {"KIT_RUNTIME_DIR": str(rt_dir)}):
            init_contract(risk="L2", goal="Testar consolidação")
            record_dead_end("sig_timeout_db", "Conexão síncrona travou o pool sob carga")
            add_never("nunca abrir transação antes de chamada HTTP externa")

            summary = consolidate_session_memory(workspace=self.repo_a, user_dir=self.user_dir)
            self.assertGreaterEqual(summary["dead_ends_added"], 1)
            self.assertGreaterEqual(summary["never_added"], 1)

            mem_txt = (self.repo_a / ".agents" / "memory" / "PROJECT_MEMORY.md").read_text(encoding="utf-8")
            self.assertIn("sig_timeout_db", mem_txt)
            self.assertIn("chamada HTTP externa", mem_txt)

            # Segunda consolidação deve ser idempotente (0 duplicatas)
            summary2 = consolidate_session_memory(workspace=self.repo_a, user_dir=self.user_dir)
            self.assertEqual(summary2["dead_ends_added"], 0)
            self.assertEqual(summary2["never_added"], 0)

    def test_jit_context_retriever_combines_repo_and_user_scopes(self) -> None:
        from scripts.context_retriever import format_jit_prompt, get_jit_context
        from scripts.memory_store import promote_memory

        promote_memory(
            "Em Docker multi-stage sempre rodar com usuário non-root uid 10001.",
            scope="user",
            category="dead_end",
            user_dir=self.user_dir,
        )
        items = get_jit_context(
            self.repo_b,
            query="Docker non-root",
            max_items=4,
            token_budget=300,
            scope="all",
            user_dir=self.user_dir,
        )
        self.assertTrue(any(i.get("scope") == "user" for i in items))
        rendered = format_jit_prompt(items)
        self.assertIn("USER", rendered)

    def test_xp_cli_memory_promote_and_consolidate(self) -> None:
        env = dict(os.environ)
        env["XP_USER_MEMORY_DIR"] = str(self.user_dir)
        res = subprocess.run(
            [sys.executable, str(ROOT_DIR / "scripts" / "xp"), "memory", "promote",
             "--scope", "user", "--category", "lesson", "Usar pathlib em vez de os.path.join"],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr + res.stdout)
        self.assertTrue((self.user_dir / "USER_MEMORY.md").is_file())


if __name__ == "__main__":
    unittest.main()
