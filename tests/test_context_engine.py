#!/usr/bin/env python3
"""
tests/test_context_engine.py
Suíte de testes para o Novo Motor de Memória e Contexto JIT do XP Multi-Agent Kit.
Valida:
1. Indexação expandida (details/, policies/, specs/, memory/).
2. Chunker contextualizado (cabeçalhos de contexto, breadcrumbs).
3. Busca híbrida FTS5 / BM25 com ponderação de títulos/identificadores.
4. Recuperação Just-In-Time (JIT) com limite estrito de tokens e formatação de prompt.
5. Associação de arquivos tocados com regras de políticas pertinentes.
"""

import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestContextEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        
        # Cria árvore simulada de governança e memória
        self.memory_dir = self.workspace / ".agents" / "memory"
        self.details_dir = self.memory_dir / "details"
        self.policies_dir = self.workspace / ".agents" / "policies"
        self.specs_dir = self.workspace / ".agents" / "specs"
        
        self.memory_dir.mkdir(parents=True)
        self.details_dir.mkdir(parents=True)
        self.policies_dir.mkdir(parents=True)
        self.specs_dir.mkdir(parents=True)

        # 1. Mock PROJECT_MEMORY.md
        (self.memory_dir / "PROJECT_MEMORY.md").write_text(
            "# 🧠 Project Memory\n\n"
            "## 1. Quick Summary\n"
            "- Sistema de memória híbrida e governança multiagente.\n\n"
            "## 3. Recent Changes\n"
            "| 2026-10-31 | `FEAT` | Motor de Memória JIT | scripts/memory_search.py | PASS |\n\n"
            "## 4. Procedural Memory\n"
            "- `[L-001]` **Regra de Ouro**: Minimize chamadas de ferramentas e mantenha o foco.\n",
            encoding="utf-8",
        )

        # 2. Mock details/6-gotchas... (Lessons)
        (self.details_dir / "6-gotchas-hurdles-learned-playbooks-procedural-memory.md").write_text(
            "## 6. Gotchas & Lessons Learned\n"
            "- **[L-012] O Maior Devorador de Tokens é o Histórico de Ferramentas:** Use sempre agy-sanitize.\n"
            "- **[L-014] Rotação de Sessão via Handoff:** Usar agy-handoff ao chegar a 25 turnos.\n"
            "- **[L-050] Concorrência em SQLite WAL:** Use timeout de 10s para conexões simultâneas.\n",
            encoding="utf-8",
        )

        # 3. Mock details/5-architectural-decisions... (Decisions)
        (self.details_dir / "5-architectural-decisions-domain-models-semantic-memory.md").write_text(
            "## 5. Architectural Decisions\n"
            "- **2026-09-30 - Pirâmide ATDD/BDD:** Separação entre Acceptance Criteria e testes de código.\n"
            "- **2026-10-15 - Zero-God-Files:** Proibido arquivos com mais de 500 linhas em produção.\n",
            encoding="utf-8",
        )

        # 4. Mock policies/code-quality.md (Policies)
        (self.policies_dir / "code-quality.md").write_text(
            "# Diretrizes de Qualidade de Código\n\n"
            "## 1. No God Files Rule\n"
            "Nunca crie arquivos com mais de 500 linhas de código no projeto.\n\n"
            "## 2. Zero Stubs e Workarounds\n"
            "Proibido deixar NotImplementedError, pass vazios ou @ts-ignore.\n",
            encoding="utf-8",
        )

        # 5. Mock policies/security.md (Security Policy)
        (self.policies_dir / "security.md").write_text(
            "# Diretrizes de Segurança\n\n"
            "## 1. Zero Secrets in Code\n"
            "Nunca commite chaves de API ou senhas em texto puro. Use variáveis de ambiente.\n"
            "## 2. Autenticação e JWT\n"
            "Tokens JWT devem expirar em 15 minutos e usar rotação de refresh token.\n",
            encoding="utf-8",
        )

        # 6. Mock specs/SPEC-001.md (Specs)
        (self.specs_dir / "SPEC-001-AUTH.md").write_text(
            "# SPEC-001: Módulo de Autenticação\n\n"
            "## Critérios de Aceitação\n"
            "- `AC-1`: Login deve retornar token JWT válido.\n"
            "- `AC-2`: Três tentativas com senha errada bloqueiam o usuário temporariamente.\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_expanded_indexing_covers_all_categories(self):
        """Verifica se indexa details/, policies/, specs/ e categoriza corretamente."""
        from scripts.memory_search import build_or_update_index, search_memory, get_db_path

        stats = build_or_update_index(self.workspace)
        self.assertGreaterEqual(stats["indexed_items"], 7)
        self.assertGreaterEqual(stats["reindexed_files"], 5)

        db_path = get_db_path(self.workspace)
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM memory_fts;")
        categories = {row[0] for row in cursor.fetchall()}
        conn.close()

        self.assertIn("lesson", categories)
        self.assertIn("decision", categories)
        self.assertIn("policy", categories)
        self.assertIn("spec", categories)

    def test_search_finds_unindexed_details_and_policies(self):
        """Verifica se busca por 'god files' encontra a regra em policies/."""
        from scripts.memory_search import build_or_update_index, search_memory

        build_or_update_index(self.workspace)
        results = search_memory(self.workspace, "god files")
        self.assertTrue(len(results) > 0)
        
        # O primeiro resultado deve ser a política ou a decisão de God Files
        top = results[0]
        self.assertTrue(
            "500 linhas" in top["content"] or "God Files" in top["title"] or "No God Files" in top["content"]
        )

    def test_contextual_breadcrumbs_prepended_to_chunks(self):
        """Verifica se breadcrumbs contextuais [Arquivo: ... | Seção: ...] são anexados."""
        from scripts.memory_search import build_or_update_index, search_memory

        build_or_update_index(self.workspace)
        results = search_memory(self.workspace, "Zero Secrets in Code")
        self.assertTrue(len(results) > 0)
        first = results[0]
        self.assertIn("security.md", first["content"])

    def test_jit_context_retriever_bounds_tokens(self):
        """Verifica se o context_retriever gera bloco JIT com limite estrito de tokens."""
        from scripts.context_retriever import get_jit_context, format_jit_prompt

        items = get_jit_context(self.workspace, query="autenticação JWT e senhas", max_items=3)
        self.assertTrue(len(items) > 0)
        self.assertLessEqual(len(items), 3)

        prompt_block = format_jit_prompt(items)
        self.assertIn("🧠 Contexto & Regras Relevantes (JIT Memory)", prompt_block)
        self.assertIn("JWT", prompt_block)
        # O bloco de prompt deve ser enxuto (< 400 palavras / ~500 tokens)
        self.assertLess(len(prompt_block.split()), 250)

    def test_jit_context_file_association(self):
        """Verifica se passar arquivos tocados traz regras pertinentes a esses arquivos."""
        from scripts.context_retriever import get_jit_context

        # Ao tocar em arquivos de autenticação, deve priorizar security.md ou SPEC-001
        items = get_jit_context(
            self.workspace,
            query="validar token",
            touched_files=["src/auth/jwt_handler.py"],
            max_items=3,
        )
        self.assertTrue(any("security" in item["source_file"] or "AUTH" in item["source_file"] for item in items))


if __name__ == "__main__":
    unittest.main()
