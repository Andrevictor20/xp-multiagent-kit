#!/usr/bin/env python3
"""tests/test_kit_constants.py — Testes para a fonte única de constantes."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.kit_constants import (
    AGENTS_MD_MAX_BYTES,
    CHARS_PER_TOKEN,
    CONTIGUOUS_READ_TTL_SECONDS,
    LOOP_HISTORY_SIZE,
    LOOP_MAX_REPEATS,
    LOOP_STATE_FILE,
    MAX_TASK_STATUS_POLLS,
    MEMORY_INDEX_MAX_BYTES,
    MEMORY_INDEX_MAX_TOKENS,
    MIN_TURNS_FOR_RESEND_ALERT,
    POST_EDIT_REREAD_TTL_SECONDS,
    PREFLIGHT_CONTEXT_PCT,
    PREFLIGHT_QUOTA_PCT,
    RESEND_SHARE_ALERT_PCT,
    SECTION_READ_MAX_LINES,
    SKILL_BODY_MAX_BYTES,
    SKILL_INDEX_LINE_MAX_CHARS,
    TOOL_OUTPUT_MAX_CHARS,
    TOOL_OUTPUT_MAX_LINES,
    TURN_BUDGET,
    WHOLE_FILE_READ_MAX_LINES,
    WRITE_TO_FILE_MAX_LINES,
    kit_root,
    needs_posix_wrapper,
    posix_wrapper,
    runtime_dir,
    user_shell,
)


class TestKitConstants(unittest.TestCase):
    """Verifica invariantes das constantes do kit."""

    def test_whole_file_read_exceeds_section_read(self):
        """O teto de leitura inteira deve ser maior que a janela de seção."""
        self.assertGreater(WHOLE_FILE_READ_MAX_LINES, SECTION_READ_MAX_LINES)

    def test_whole_file_read_is_800(self):
        """Valor canônico documentado em AGENTS.md e token-economy.md."""
        self.assertEqual(WHOLE_FILE_READ_MAX_LINES, 800)

    def test_section_read_is_400(self):
        self.assertEqual(SECTION_READ_MAX_LINES, 400)

    def test_turn_budget_l0_leq_l1_leq_l2(self):
        """Orçamento de turnos cresce com o risco."""
        self.assertLess(TURN_BUDGET["L0"], TURN_BUDGET["L1"])
        self.assertLess(TURN_BUDGET["L1"], TURN_BUDGET["L2"])

    def test_turn_budget_l3_is_none(self):
        """L3 não tem teto, mas exige checkpoint."""
        self.assertIsNone(TURN_BUDGET["L3"])

    def test_memory_index_max_bytes_positive(self):
        self.assertGreater(MEMORY_INDEX_MAX_BYTES, 0)

    def test_agents_md_max_bytes_positive(self):
        self.assertGreater(AGENTS_MD_MAX_BYTES, 0)

    def test_chars_per_token_is_4(self):
        self.assertEqual(CHARS_PER_TOKEN, 4)

    def test_preflight_thresholds_in_range(self):
        self.assertGreater(PREFLIGHT_CONTEXT_PCT, 0)
        self.assertLessEqual(PREFLIGHT_CONTEXT_PCT, 100)
        self.assertGreater(PREFLIGHT_QUOTA_PCT, 0)
        self.assertLessEqual(PREFLIGHT_QUOTA_PCT, 100)

    def test_kit_root_returns_valid_path(self):
        root = kit_root()
        self.assertTrue(root.exists(), f"kit_root() = {root} does not exist")
        # Deve conter o diretório scripts/ ou .agents/
        self.assertTrue(
            (root / "scripts").exists() or (root / ".agents").exists(),
            f"kit_root() = {root} does not look like a kit directory",
        )

    def test_runtime_dir_creates_dir(self):
        rd = runtime_dir()
        self.assertTrue(rd.is_dir())

    def test_user_shell_returns_string(self):
        shell = user_shell()
        self.assertIsInstance(shell, str)
        self.assertGreater(len(shell), 0)

    def test_posix_wrapper_returns_path(self):
        wrapper = posix_wrapper()
        self.assertIn("/", wrapper)

    def test_needs_posix_wrapper_returns_bool(self):
        result = needs_posix_wrapper()
        self.assertIsInstance(result, bool)

    def test_max_task_status_polls_is_one(self):
        """Bloqueia polling contínuo de status de background tasks."""
        self.assertEqual(MAX_TASK_STATUS_POLLS, 1)

    def test_post_edit_reread_ttl_is_positive(self):
        """TTL de releitura pós-edição deve ser janela positiva."""
        self.assertGreater(POST_EDIT_REREAD_TTL_SECONDS, 0.0)


if __name__ == "__main__":
    unittest.main()
