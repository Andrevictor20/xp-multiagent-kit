#!/usr/bin/env python3
"""
tests/test_mission_scenarios.py
Acceptance tests for SPEC-007 (XP Multi-Agent Kit v4 Honesty & Corrections).
Scenarios S1 through S15 executed in isolated environments or repository audits.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent


class TestMissionScenarios(unittest.TestCase):
    """Scenarios S1 through S15 as defined in SPEC-007."""

    def test_s15_repository_delivered_budget_tests(self):
        """
        S15: Repositório entregue -> testes de orçamento.
        AGENTS.md + memória <= 8.000 B; memória <= 3.000 B.
        """
        from scripts.kit_constants import BASE_CONTEXT_MAX_BYTES, MEMORY_INDEX_MAX_BYTES

        agents_md = KIT_ROOT / "AGENTS.md"
        memory_md = KIT_ROOT / ".agents" / "memory" / "PROJECT_MEMORY.md"

        self.assertTrue(agents_md.is_file(), "AGENTS.md must exist")
        self.assertTrue(memory_md.is_file(), "PROJECT_MEMORY.md must exist")

        agents_bytes = len(agents_md.read_text(encoding="utf-8").encode("utf-8"))
        memory_bytes = len(memory_md.read_text(encoding="utf-8").encode("utf-8"))

        self.assertLessEqual(
            memory_bytes,
            MEMORY_INDEX_MAX_BYTES,
            f"PROJECT_MEMORY.md ({memory_bytes} B) must be <= {MEMORY_INDEX_MAX_BYTES} B",
        )
        self.assertLessEqual(
            agents_bytes + memory_bytes,
            BASE_CONTEXT_MAX_BYTES,
            f"AGENTS.md + memory ({agents_bytes + memory_bytes} B) must be <= {BASE_CONTEXT_MAX_BYTES} B",
        )


if __name__ == "__main__":
    unittest.main()
