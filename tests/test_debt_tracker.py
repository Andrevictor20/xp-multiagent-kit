#!/usr/bin/env python3
"""
Testes unitários para o rastreador de débito técnico auditável (agy-debt / debt_tracker.py).
Conformidade estrita com TDD e AC-4 / AC-5 da SPEC-001.
"""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

# O módulo scripts.debt_tracker será criado para satisfazer estes testes (fase RED -> GREEN)
from scripts.debt_tracker import (
    DebtItem,
    scan_debt_markers,
    parse_debt_line,
    format_debt_report,
    sync_memory_debt_section,
    main,
)


class TestDebtTrackerParsing(unittest.TestCase):
    """Testa a análise sintática de marcadores de débito no código."""

    def test_parse_valid_debt_with_trigger_hash(self):
        line = "  # debt: scan linear O(N), migrar para B-Tree se tabela > 50k registros\n"
        item = parse_debt_line("app.py", 42, line)
        self.assertIsNotNone(item)
        self.assertEqual(item.file_path, "app.py")
        self.assertEqual(item.line_number, 42)
        self.assertEqual(item.ceiling, "scan linear O(N)")
        self.assertEqual(item.trigger, "migrar para B-Tree se tabela > 50k registros")
        self.assertTrue(item.has_trigger)

    def test_parse_valid_debt_with_trigger_double_slash(self):
        line = "const x = 1; // debt: lock global em memória, migrar para Redis lock se RPS > 500"
        item = parse_debt_line("src/index.ts", 10, line)
        self.assertIsNotNone(item)
        self.assertEqual(item.ceiling, "lock global em memória")
        self.assertEqual(item.trigger, "migrar para Redis lock se RPS > 500")
        self.assertTrue(item.has_trigger)

    def test_parse_debt_without_trigger_flags_no_trigger(self):
        line = "/* debt: mock simples provisório */"
        item = parse_debt_line("tests/mock.c", 15, line)
        self.assertIsNotNone(item)
        self.assertEqual(item.ceiling, "mock simples provisório")
        self.assertIsNone(item.trigger)
        self.assertFalse(item.has_trigger)

    def test_parse_debt_html_comment(self):
        line = "<!-- debt: layout fixo 320px, adicionar flexbox quando tablet for solicitado -->"
        item = parse_debt_line("public/index.html", 5, line)
        self.assertIsNotNone(item)
        self.assertEqual(item.ceiling, "layout fixo 320px")
        self.assertEqual(item.trigger, "adicionar flexbox quando tablet for solicitado")
        self.assertTrue(item.has_trigger)

    def test_parse_line_without_debt_marker_returns_none(self):
        line = "const total = debt + interest; // calcula dívida do cliente"
        item = parse_debt_line("calc.js", 20, line)
        self.assertIsNone(item)


class TestDebtTrackerScanner(unittest.TestCase):
    """Testa a varredura recursiva de diretórios ignorando pastas de build/sistema."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scan_finds_debts_and_ignores_git_and_node_modules(self):
        # Arquivo válido com débito
        src_dir = os.path.join(self.test_dir, "src")
        os.makedirs(src_dir)
        with open(os.path.join(src_dir, "api.py"), "w", encoding="utf-8") as f:
            f.write("# debt: cache em dict simples, redis se > 1k usuarios\n")
            f.write("def get_data(): return {}\n")
            f.write("# debt: sem timeout aqui\n")

        # Arquivo dentro de node_modules (deve ser ignorado)
        nm_dir = os.path.join(self.test_dir, "node_modules", "pkg")
        os.makedirs(nm_dir)
        with open(os.path.join(nm_dir, "pkg.js"), "w", encoding="utf-8") as f:
            f.write("// debt: ignorar isto, trigger teste\n")

        # Arquivo dentro de .git (deve ser ignorado)
        git_dir = os.path.join(self.test_dir, ".git")
        os.makedirs(git_dir)
        with open(os.path.join(git_dir, "hook"), "w", encoding="utf-8") as f:
            f.write("# debt: ignorar git\n")

        items = scan_debt_markers(self.test_dir)
        self.assertEqual(len(items), 2)

        # Primeiro item tem gatilho
        self.assertTrue(items[0].has_trigger)
        self.assertEqual(items[0].ceiling, "cache em dict simples")

        # Segundo item não tem gatilho (risco de apodrecimento)
        self.assertFalse(items[1].has_trigger)
        self.assertEqual(items[1].ceiling, "sem timeout aqui")


class TestDebtTrackerFormattingAndCli(unittest.TestCase):
    """Testa a formatação de relatórios, exportação e códigos de retorno do CLI."""

    def setUp(self):
        self.items = [
            DebtItem(
                file_path="src/service.py",
                line_number=12,
                raw_comment="# debt: lock global, granular se concorrência > 100",
                ceiling="lock global",
                trigger="granular se concorrência > 100",
                has_trigger=True,
            ),
            DebtItem(
                file_path="src/legacy.py",
                line_number=88,
                raw_comment="# debt: fallback ingênuo sem retry",
                ceiling="fallback ingênuo sem retry",
                trigger=None,
                has_trigger=False,
            ),
        ]

    def test_format_report_includes_stats_and_rot_risk(self):
        report = format_debt_report(self.items)
        self.assertIn("src/service.py:12", report)
        self.assertIn("lock global", report)
        self.assertIn("src/legacy.py:88", report)
        self.assertIn("[NO-TRIGGER]", report)
        self.assertIn("Total de débitos: 2", report)
        self.assertIn("1 em risco de apodrecimento", report)

    def test_format_report_clean_when_empty(self):
        report = format_debt_report([])
        self.assertIn("Nenhum débito técnico encontrado. Ledger limpo.", report)

    def test_cli_fail_on_no_trigger_returns_code_1_when_trigger_missing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "code.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# debt: simplificação sem nenhum gatilho de upgrade\n")

            exit_code = main(["--dir", tmp_dir, "--fail-on-no-trigger"])
            self.assertEqual(exit_code, 1)

    def test_cli_fail_on_no_trigger_returns_code_0_when_all_have_triggers(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "code.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# debt: cache local, migrar para redis se N > 500\n")

            exit_code = main(["--dir", tmp_dir, "--fail-on-no-trigger"])
            self.assertEqual(exit_code, 0)

    def test_cli_json_output(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "code.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# debt: cache local, redis se N > 500\n")

            with patch("sys.stdout") as mock_stdout:
                # Usando StringIO simulado para capturar json
                import io

                fake_out = io.StringIO()
                with patch("sys.stdout", fake_out):
                    exit_code = main(["--dir", tmp_dir, "--json"])
                    self.assertEqual(exit_code, 0)
                    data = json.loads(fake_out.getvalue())
                    self.assertEqual(data["total_debts"], 1)
                    self.assertEqual(data["no_trigger_count"], 0)
                    self.assertEqual(len(data["items"]), 1)
                    self.assertEqual(data["items"][0]["ceiling"], "cache local")

    def test_sync_memory_debt_section(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            mem_path = os.path.join(tmp_dir, "PROJECT_MEMORY.md")
            with open(mem_path, "w", encoding="utf-8") as f:
                f.write("# Memory\n\n## 7. Technical Debts & Known Blockers\n\n- Nenhum bloqueio ativo.\n")

            items = [
                DebtItem("src/api.py", 10, "# debt: mock, real quando api pronta", "mock", "real quando api pronta", True)
            ]
            success = sync_memory_debt_section(mem_path, items)
            self.assertTrue(success)

            with open(mem_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("src/api.py:10", content)
                self.assertIn("mock", content)


if __name__ == "__main__":
    unittest.main()
